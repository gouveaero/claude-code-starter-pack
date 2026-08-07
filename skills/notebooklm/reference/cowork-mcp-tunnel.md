# Addendum — NotebookLM no Cowork (MCP Server + Cloudflare Tunnel)

> **Contexto:** isto NÃO faz parte da skill oficial `teng-lin/notebooklm-py`. É um addendum opcional, útil apenas se você quiser usar o NotebookLM dentro do **Cowork** (o sandbox em nuvem da Anthropic), que não enxerga o CLI local da sua máquina. No uso normal de Claude Code local, ignore este arquivo — o CLI roda direto.

---

## Adding NotebookLM to Cowork (MCP Server + Cloudflare Tunnel)

> **Credit:** This approach was contributed by Daniel at [skool.com/navaigate](https://www.skool.com/navaigate). It supersedes the older cookie-inlining method, which broke whenever Google rotated tokens.

When the user asks to "add this to Cowork", "use this in Cowork", or "make this work in Cowork":

### Why the MCP Approach

Cowork runs on Anthropic's servers. It can't see your local files. It can't run your CLI tools. The old approach of inlining auth cookies into a skill file failed repeatedly because:
- Tokens expire and force a full regeneration cycle
- Google's auth flow can change without warning
- You have to re-upload the skill every time

The MCP pattern solves this cleanly: the CLI stays on your Mac (full filesystem access, full auth), you wrap it in an MCP server, Cloudflare Tunnel gives it a public HTTPS URL, and Cowork connects to that URL like any other MCP server. The agent doesn't know or care where the tool runs — it just works.

### Architecture

```
Claude Code / Cowork
        ↓ MCP Protocol (SSE)
Cloudflare Tunnel (HTTPS)
        ↓
Your Mac → localhost:8484
        ↓
MCP Server (Python + FastMCP)
        ↓
NotebookLM CLI → Google NotebookLM
```

### Prerequisite Check

```bash
# Make sure the local CLI is installed and authenticated first
cat ~/.notebooklm/storage_state.json > /dev/null 2>&1 && notebooklm auth check
```

If either check fails, run the **Step 0: Local Setup** above before continuing.

You'll also need a domain on Cloudflare (for the tunnel hostname). If the user doesn't have one yet, they'll need to set that up first at cloudflare.com.

### Step 1: Build the MCP Server

Create the project and set up a Python 3.12 virtual environment:

```bash
mkdir -p ~/notebooklm-mcp && cd ~/notebooklm-mcp
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]" uvicorn
```

Create `~/notebooklm-mcp/server.py`. Every CLI command becomes a decorated Python function — here's the pattern (extend with as many tools as you want exposed):

```python
import sys, subprocess
from mcp.server.fastmcp import FastMCP

NOTEBOOKLM = "/Users/YOUR_USERNAME/bin/notebooklm"  # adjust to your symlink path
mcp = FastMCP("notebooklm", host="0.0.0.0", port=8484)

def run_cli(*args, timeout=120):
    result = subprocess.run(
        [NOTEBOOKLM, *args],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip() or "(no output)"

@mcp.tool()
def notebooklm_list() -> str:
    """List all NotebookLM notebooks."""
    return run_cli("list")

@mcp.tool()
def notebooklm_use(notebook_id: str) -> str:
    """Set the active notebook context."""
    return run_cli("use", notebook_id)

@mcp.tool()
def notebooklm_ask(question: str) -> str:
    """Ask the current notebook a question (RAG query)."""
    return run_cli("ask", question, timeout=120)

@mcp.tool()
def notebooklm_source_add(url_or_path: str) -> str:
    """Add a URL, YouTube link, or local file as a source to the current notebook."""
    return run_cli("source", "add", url_or_path, timeout=180)

@mcp.tool()
def notebooklm_generate_audio(instructions: str = "") -> str:
    """Generate a podcast-style audio overview."""
    args = ["generate", "audio"]
    if instructions:
        args.append(instructions)
    return run_cli(*args, timeout=600)

# Follow this pattern for every command you want to expose —
# create, source list, generate video/report/quiz/flashcards, download, etc.
# See the Quick Reference table in ../SKILL.md for the full command surface.

if __name__ == "__main__":
    if "--sse" in sys.argv:
        import uvicorn
        app = mcp.sse_app()
        uvicorn.run(app, host="0.0.0.0", port=8484)
    else:
        mcp.run(transport="stdio")
```

The entry point supports two transport modes:
- **SSE mode** (`--sse`) — for Cowork via the tunnel. Runs an HTTP server on port 8484.
- **Stdio mode** (default) — for local Claude Code. Direct pipe, no network overhead.

Smoke test it:
```bash
source ~/notebooklm-mcp/.venv/bin/activate
python -c "from server import run_cli; print(run_cli('auth', 'check'))"
```

### Step 2: Set Up the Cloudflare Tunnel

Cowork runs on Anthropic's servers. `localhost` means nothing to it. You need a public HTTPS URL pointing at your Mac. Cloudflare Tunnel does this without opening any ports on your router.

```bash
brew install cloudflared
cloudflared tunnel login
cloudflared tunnel create notebooklm-mcp
cloudflared tunnel route dns notebooklm-mcp mcp-notebooklm.yourdomain.com
```

Create `~/.cloudflared/config-notebooklm-mcp.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: ~/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: mcp-notebooklm.yourdomain.com
    service: http://localhost:8484
  - service: http_status:404
```

Test it end-to-end:
```bash
# Terminal 1: start the server
cd ~/notebooklm-mcp && source .venv/bin/activate
python server.py --sse

# Terminal 2: start the tunnel
cloudflared tunnel --config ~/.cloudflared/config-notebooklm-mcp.yml run notebooklm-mcp

# Terminal 3: verify
curl -s https://mcp-notebooklm.yourdomain.com/sse | head -3
```

You should see `event: endpoint` with a session ID. That means it's working.

### Step 3: Auto-Start on Boot (macOS Launch Agents)

You don't want to manually start two processes every time you turn on your Mac. Create two Launch Agents:

**MCP Server** — `~/Library/LaunchAgents/dev.navaigate.notebooklm-mcp.plist`
Points to `.venv/bin/python server.py --sse`. Set `RunAtLoad` and `KeepAlive` to `true`.

**Tunnel** — `~/Library/LaunchAgents/dev.navaigate.notebooklm-tunnel.plist`
Points to `cloudflared tunnel run` with the config file. Same flags.

Load them once — they persist across reboots, and macOS restarts either process automatically if it crashes:

```bash
launchctl load ~/Library/LaunchAgents/dev.navaigate.notebooklm-mcp.plist
launchctl load ~/Library/LaunchAgents/dev.navaigate.notebooklm-tunnel.plist
```

### Step 4: Connect to Cowork

1. Open Cowork and click the **+** icon
2. Go to **Connectors → Add connection → Add custom connector**
3. Enter: `https://mcp-notebooklm.yourdomain.com/sse`
4. Click **Add**

The NotebookLM tools appear immediately. Prompt naturally:

> "List my NotebookLM notebooks"
> "Switch to my AI Brain notebook and tell me the last 3 entries"
> "Ask my AI Brain: what were the key decisions from last week?"
> "Generate a podcast from my current notebook"

### Step 5: Local Claude Code Setup (Stdio Transport)

For terminal sessions you don't need the tunnel — add the MCP server to `~/.claude/settings.json` using stdio transport:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "/Users/YOUR_USERNAME/notebooklm-mcp/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/notebooklm-mcp/server.py"]
    }
  }
}
```

Same server, different transport. The tools work identically — local sessions just skip the network hop.

### MCP Troubleshooting

| Symptom | Fix |
|---|---|
| Auth expired | Run `notebooklm login` (or the custom login script in Step 0) locally. The MCP server picks up new tokens automatically — no restart needed. |
| Server not responding | `lsof -i :8484` to check the port, `tail ~/notebooklm-mcp/mcp-server.log` for errors, then `launchctl kickstart -k gui/$(id -u)/dev.navaigate.notebooklm-mcp`. |
| Tunnel down | `cloudflared tunnel info notebooklm-mcp`. `KeepAlive` usually restarts it automatically. |
| Cowork says "can't reach server" | Verify with `curl -s https://mcp-notebooklm.yourdomain.com/sse \| head -3`. If that works, remove and re-add the connector in Cowork. |

### Why This Pattern Generalizes

Local MCP server + Cloudflare Tunnel isn't just for NotebookLM. Any CLI tool, any local service, any API that needs local credentials can be wrapped as an MCP server and made available to Cowork the same way. Once you've done it once, you can do it for anything.

### Resources

- NotebookLM CLI Skill for Claude Code: [github.com/skyremote/claude-code-notebooklm-skills](https://github.com/skyremote/claude-code-notebooklm-skills)
- notebooklm-py (CLI tool): [github.com/teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py)
- MCP Python SDK: [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- Cloudflare Tunnel docs: [developers.cloudflare.com/cloudflare-one/connections/connect-networks](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks)
