# Claude Code Starter Pack

Um kit de início para o [Claude Code](https://claude.com/claude-code): instala num comando os **plugins essenciais oficiais** + um **subconjunto curado de skills próprias** de conteúdo, escrita e design.

A ideia é sair do zero para um Claude Code produtivo — com a meta-skill de **criação de skills** no centro, porque uma vez que você consegue criar skills, destrava todo o resto.

## Instalação

```bash
git clone https://github.com/gouveaero/claude-code-starter-pack.git
cd claude-code-starter-pack
./install.sh
```

Depois **reinicie o Claude Code** para carregar tudo.

### Atualizando

O `install.sh` é idempotente e **nunca sobrescreve** uma skill existente sem você pedir. Se o pack tiver uma versão mais nova de algo que você já tem, ele avisa e para por aí:

```bash
./install.sh --dry-run   # mostra o que mudaria, sem tocar em nada
./install.sh --force     # atualiza as desatualizadas
```

Com `--force`, a versão que estava em `~/.claude/skills/` é movida para `~/.claude/skills-backup-<data>/` antes da substituição — se você tinha customizações locais, elas continuam recuperáveis.

## O que vem no pack

### Camada 1 — Essenciais (plugins oficiais Anthropic)

Instalados via marketplace `anthropics/claude-plugins-official`, sempre na versão mais recente. **Não são vendorizados** neste repo — o instalador os baixa do marketplace.

| Plugin | Para quê |
|---|---|
| **skill-creator** | Criar, editar, testar e otimizar skills. A meta-skill — o coração do pack. |
| **superpowers** | Workflow de engenharia: `brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `verification-before-completion`, `using-git-worktrees`, **`writing-skills`** e mais. |
| **frontend-design** | Design de interface de alto padrão. |

> A **`writing-skills`** (como estruturar uma skill — companheira direta da `skill-creator`) vem **dentro** do `superpowers`. Instalar o plugin já a traz; não precisa instalar à parte.

### Camada 2 — Skills curadas (vendorizadas)

Copiadas para `~/.claude/skills/`, onde carregam automaticamente. Selecionadas por serem **gerais e úteis no dia a dia** — nenhuma amarrada a um cliente, marca ou credencial específica.

**Decisão e pensamento**

| Skill | Para quê |
|---|---|
| **llm-council** | Pressiona uma decisão de alto risco por 5 conselheiros independentes + revisão anônima entre pares + veredito de um presidente. Adaptada do LLM Council do Karpathy. ([repo próprio](https://github.com/gouveaero/llm-council)) |

**Escrita** — a suíte que filtra texto que "soa como IA"

| Skill | Para quê |
|---|---|
| **anti-ai-writing** | O filtro final de qualquer texto. Pega prosa fluente-mas-oca, formatação excessiva e o cheiro de LLM. |
| **viral-hooks** | Escreve e audita as primeiras linhas — hook de reel, slide 1 de carrossel, intro de vídeo. |
| **storytelling** | Conteúdo narrativo / talking-head: roteiro de reel, história, "yap". |
| **voice-dna** | Faz o texto bater com a voz real de uma pessoa ou marca, a partir de amostras. |
| **dumbify** | Conteúdo que precisa ser fácil de seguir — explicador, carrossel de ensino, how-to. |

**Criação**

| Skill | Para quê |
|---|---|
| **content-machine-pro** | Carrosséis de Instagram/LinkedIn com imagens de fundo, paleta derivada da marca e sem marca d'água. Pipeline editorial completo: briefing → headlines → espinha → texto → imagens → HTML 1080×1350 → PNG. |
| **canva-presentation** | Apresentações Canva a partir de markdown, com playbook de animação. |
| **video-editor-remotion** | Pipeline de vídeo 100% Remotion — renderiza o MP4 final sem editor externo. |
| **notebooklm** | API completa do Google NotebookLM — cria notebooks, fontes, podcasts e demais artefatos via API, incluindo o que não existe na UI web. |

**Frontend**

| Skill | Para quê |
|---|---|
| **impeccable** | Design, review e polish de interfaces frontend. Sub-comandos: `shape`, `audit`, `critique`, `polish`, `typeset`, `layout`, `colorize`, `harden`, `live` e mais. |
| **clone-website** | Engenharia reversa e clone de sites seção por seção. |

### Dependências opcionais

Quase tudo roda sem configuração extra. As exceções, todas com degradação graciosa:

- **content-machine-pro** — usa MCP de imagem (Higgsfield/Magnific) se existir. Sem nenhum, cai para imagens suas → Unsplash (`UNSPLASH_ACCESS_KEY`) → URL direta → modo Minimal (numeral + gradiente da marca). Entrega o carrossel de qualquer jeito. Para o export PNG: Playwright + Chromium.
- **video-editor-remotion** — Node + Remotion. Bancos de SFX/PNG locais são opcionais e configuráveis (`SFX_ROOT`).
- **notebooklm** — CLI `notebooklm-py` (Python 3.10+). O uso via Cowork é um addendum opcional.

## Por que os essenciais não estão neste repo

`skill-creator`, `superpowers` e `frontend-design` são plugins **oficiais da Anthropic**. Copiá-los para cá significaria republicar conteúdo de terceiros e ficar desatualizado em relação ao marketplace. O instalador os puxa direto da fonte — sempre atuais.

## Estrutura

```
claude-code-starter-pack/
├── install.sh          # marketplace + plugins oficiais + skills curadas
├── README.md
├── LICENSE
└── skills/             # skills vendorizadas (Camada 2)
    ├── llm-council/
    ├── anti-ai-writing/
    ├── viral-hooks/
    ├── storytelling/
    ├── voice-dna/
    ├── dumbify/
    ├── content-machine-pro/
    ├── canva-presentation/
    ├── video-editor-remotion/
    ├── notebooklm/
    ├── impeccable/
    └── clone-website/
```

## Instalação manual (sem o script)

```bash
# 1. marketplace
claude plugin marketplace add anthropics/claude-plugins-official

# 2. plugins essenciais
claude plugin install skill-creator@claude-plugins-official
claude plugin install superpowers@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official

# 3. skills curadas
cp -R skills/* ~/.claude/skills/
```

## Licença

MIT — veja [LICENSE](LICENSE).

A `impeccable` é Apache 2.0, derivada da skill `frontend-design` da Anthropic. A `notebooklm` embrulha o CLI de terceiros [`notebooklm-py`](https://github.com/teng-lin/notebooklm-py).
