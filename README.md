# Claude Code Starter Pack

Um kit de início para o [Claude Code](https://claude.com/claude-code): instala num comando os **plugins essenciais oficiais** + um **subconjunto curado de skills próprias** de conteúdo e design.

A ideia é sair do zero para um Claude Code produtivo — com a meta-skill de **criação de skills** no centro, porque uma vez que você consegue criar skills, destrava todo o resto.

## Instalação

```bash
git clone https://github.com/<owner>/claude-code-starter-pack.git
cd claude-code-starter-pack
./install.sh
```

Depois **reinicie o Claude Code** para carregar tudo.

O `install.sh` é idempotente — pode rodar de novo sem duplicar nada.

## O que vem no pack

### Camada 1 — Essenciais (plugins oficiais Anthropic)

Instalados via marketplace `anthropics/claude-plugins-official`, sempre na versão mais recente. **Não são vendorizados** neste repo — o instalador os baixa do marketplace.

| Plugin | Para quê |
|---|---|
| **skill-creator** | Criar, editar, testar e otimizar skills. A meta-skill — o coração do pack. |
| **superpowers** | Workflow de engenharia: `brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `verification-before-completion`, `using-git-worktrees` e mais. |
| **frontend-design** | Design de interface de alto padrão. |

> O `superpowers` inclui a `writing-skills` (como estruturar uma skill) — companheira direta da `skill-creator`.

### Camada 2 — Skills curadas (próprias, vendorizadas)

Copiadas para `~/.claude/skills/`, onde carregam automaticamente. Selecionadas por serem **gerais e úteis no dia a dia** (não amarradas a um cliente específico):

| Skill | Para quê |
|---|---|
| **carousel-generator** | Carrosséis (Instagram/LinkedIn/Stories) como HTML editável → exporta JPG/PNG. |
| **canva-presentation** | Apresentações Canva a partir de markdown, com playbook de animação. |
| **slidev-presentation** | Decks Slidev cinematográficos (código, diagramas, animações) com deploy. |
| **clone-website** | Engenharia reversa e clone de sites seção por seção. |
| **impeccable** | Design/review/polish de interfaces frontend. |

## Por que os essenciais não estão neste repo

`skill-creator`, `superpowers` e `frontend-design` são plugins **oficiais da Anthropic**. Copiá-los para cá significaria republicar conteúdo de terceiros e ficar desatualizado em relação ao marketplace. O instalador os puxa direto da fonte — sempre atuais.

## Estrutura

```
claude-code-starter-pack/
├── install.sh          # marketplace + plugins oficiais + skills curadas
├── README.md
├── LICENSE
└── skills/             # skills próprias vendorizadas (Camada 2)
    ├── carousel-generator/
    ├── canva-presentation/
    ├── slidev-presentation/
    ├── clone-website/
    └── impeccable/
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
