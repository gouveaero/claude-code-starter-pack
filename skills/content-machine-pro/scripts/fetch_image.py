#!/usr/bin/env python3
"""
Fetch an image (from any URL, or Unsplash search) and normalize it to an exact
1080x1350 (4:5) JPEG for use as a carousel/cover background. Optionally emits a
base64 data-URI for inline embedding, and/or measures the luminance of the text
band so the caller can size the dark scrim deterministically.

This script does the deterministic pixel work ONLY. AI generation and stock
search happen in the agent turn via MCP (Higgsfield / Magnific): the agent obtains
the final image URL, then passes it here with `--url`. So in practice:
  - Higgsfield / Magnific (AI) / Magnific stock  → agent gets URL → `--url <url>`
  - Unsplash                                     → `--source unsplash --query "..."` (needs UNSPLASH_ACCESS_KEY)
  - any direct link                              → `--url <url>`

Usage:
  python3 fetch_image.py --url "https://..." --out bg.jpg [--emit-base64] [--measure-luma] [--crop smart|center]
  python3 fetch_image.py --source unsplash --query "data center servers" --out bg.jpg [...]

Notes:
  - Python 3.9 compatible (from __future__ import annotations).
  - Uses Pillow if available (preferred); falls back to the `sips` CLI (macOS) for resize.
  - `--measure-luma` prints `LUMA_BAND=<0-255>` (avg luminance of the bottom 38% band)
    plus a suggested scrim: `SCRIM_SUGGEST=<0.72-0.99>`. Brighter band -> stronger scrim.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request

W, H = 1080, 1350           # target 4:5 canvas
TEXT_BAND = 0.38            # bottom fraction where headline/body usually sits
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 carousel-fetch"


def _get(url: str, headers: dict | None = None, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def unsplash_url(query: str) -> str:
    """Resolve an Unsplash photo URL for a query. Requires UNSPLASH_ACCESS_KEY."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        sys.exit("error: --source unsplash needs UNSPLASH_ACCESS_KEY in env. "
                 "Prefer Magnific stock (agent-side) and pass the result with --url.")
    api = ("https://api.unsplash.com/search/photos?per_page=5&orientation=portrait&query="
           + urllib.parse.quote(query))
    data = json.loads(_get(api, headers={"Authorization": "Client-ID " + key, "User-Agent": UA}))
    results = data.get("results") or []
    if not results:
        sys.exit("error: no Unsplash results for query: " + query)
    # full > regular; pick the first (most relevant) result.
    urls = results[0]["urls"]
    return urls.get("full") or urls.get("regular")


def normalize_pillow(raw: bytes, out: str, crop: str) -> None:
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(raw)).convert("RGB")
    iw, ih = im.size
    scale = max(W / iw, H / ih)            # cover
    nw, nh = round(iw * scale), round(ih * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - W) // 2
    if crop == "smart":
        # subjects usually sit in the upper portion; bias the crop to keep the top.
        top = int((nh - H) * 0.30)
    else:
        top = (nh - H) // 2
    top = max(0, min(top, nh - H))
    im = im.crop((left, top, left + W, top + H))
    im.save(out, "JPEG", quality=88, optimize=True)


def normalize_sips(raw: bytes, out: str) -> None:
    import subprocess
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".img", delete=False)
    tmp.write(raw)
    tmp.close()
    # sips cover-crops with -z then -c (pad/crop). Use -c to crop to exact size after scaling.
    subprocess.run(["sips", "-s", "format", "jpeg", "-z", str(H), str(int(H * W / H)),
                    tmp.name, "--out", out], check=True, capture_output=True)
    subprocess.run(["sips", "-c", str(H), str(W), out], check=True, capture_output=True)
    os.unlink(tmp.name)


def measure_luma(out: str) -> None:
    try:
        from PIL import Image
    except Exception:
        return
    im = Image.open(out).convert("L")
    band = im.crop((0, int(H * (1 - TEXT_BAND)), W, H))
    px = list(band.getdata())
    avg = sum(px) / len(px)
    # brighter band -> need a stronger scrim to keep white text at >=4.5:1
    scrim = 0.72 + (avg / 255.0) * 0.27
    scrim = max(0.72, min(0.99, scrim))
    print("LUMA_BAND=%.0f" % avg)
    print("SCRIM_SUGGEST=%.2f" % scrim)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["url", "unsplash"], default="url")
    ap.add_argument("--url")
    ap.add_argument("--query")
    ap.add_argument("--out", required=True)
    ap.add_argument("--emit-base64", action="store_true")
    ap.add_argument("--measure-luma", action="store_true")
    ap.add_argument("--crop", choices=["smart", "center"], default="center")
    a = ap.parse_args()

    if a.source == "unsplash":
        if not a.query:
            return _err("--source unsplash requires --query")
        url = unsplash_url(a.query)
    else:
        if not a.url:
            return _err("--source url requires --url")
        url = a.url

    raw = _get(url)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    try:
        normalize_pillow(raw, a.out, a.crop)
    except ImportError:
        normalize_sips(raw, a.out)

    print("saved %dx%d -> %s" % (W, H, a.out))
    if a.measure_luma:
        measure_luma(a.out)
    if a.emit_base64:
        b = base64.b64encode(open(a.out, "rb").read()).decode("ascii")
        print("data:image/jpeg;base64," + b)
    return 0


def _err(msg: str) -> int:
    print("error: " + msg, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
