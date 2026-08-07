#!/usr/bin/env bash
#
# Claude Code Starter Pack — instalador
#
# Faz três coisas:
#   1. Registra o marketplace oficial da Anthropic (idempotente)
#   2. Instala os plugins essenciais (skill-creator, superpowers, frontend-design)
#   3. Copia o subconjunto curado de skills próprias para ~/.claude/skills/
#
# Uso:
#   ./install.sh            # instala o que falta; NÃO toca no que já existe
#   ./install.sh --force    # atualiza também o que já existe (faz backup antes)
#   ./install.sh --dry-run  # só mostra o que faria
#
set -euo pipefail

MARKETPLACE="anthropics/claude-plugins-official"
MARKETPLACE_NAME="claude-plugins-official"
PLUGINS=(
  "skill-creator"     # cria, edita e testa skills — a meta-skill
  "superpowers"       # workflow de engenharia: brainstorming, plans, TDD, debugging, code-review
  "frontend-design"   # design de interface de alto padrão
)
SKILLS_DIR="${HOME}/.claude/skills"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${HOME}/.claude/skills-backup-$(date +%Y%m%d-%H%M%S)"

FORCE=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --force|-f)   FORCE=1 ;;
    --dry-run|-n) DRY_RUN=1 ;;
    --help|-h)
      sed -n '3,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "✗ opção desconhecida: $arg (use --help)" >&2; exit 1 ;;
  esac
done

bold() { printf '\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
info() { printf '  \033[34m→\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }

run() { if [ "$DRY_RUN" = 1 ]; then echo "      [dry-run] $*"; else "$@"; fi; }

[ "$DRY_RUN" = 1 ] && bold "MODO DRY-RUN — nada será alterado"

# --- pré-requisito --------------------------------------------------------
if ! command -v claude >/dev/null 2>&1; then
  echo "✗ CLI 'claude' não encontrado. Instale o Claude Code primeiro:" >&2
  echo "  https://docs.claude.com/claude-code" >&2
  exit 1
fi

# --- 1. marketplace -------------------------------------------------------
bold "1/3  Marketplace oficial"
if claude plugin marketplace list 2>/dev/null | grep -q "${MARKETPLACE_NAME}"; then
  ok "marketplace '${MARKETPLACE_NAME}' já registrado"
else
  run claude plugin marketplace add "${MARKETPLACE}"
  ok "marketplace '${MARKETPLACE_NAME}' adicionado"
fi

# --- 2. plugins oficiais --------------------------------------------------
bold "2/3  Plugins essenciais"
for p in "${PLUGINS[@]}"; do
  if claude plugin list 2>/dev/null | grep -q "^${p}\b\|${p}@"; then
    ok "${p} já instalado"
  else
    info "instalando ${p}…"
    run claude plugin install "${p}@${MARKETPLACE_NAME}"
    ok "${p} instalado"
  fi
done

# --- 3. skills próprias curadas ------------------------------------------
bold "3/3  Skills curadas"
run mkdir -p "${SKILLS_DIR}"

outdated=0
for dir in "${SELF_DIR}"/skills/*/; do
  name="$(basename "${dir}")"
  dest="${SKILLS_DIR}/${name}"

  if [ ! -d "${dest}" ]; then
    run cp -R "${dir}" "${dest}"
    ok "${name} instalada"
    continue
  fi

  # já existe: só mexe com --force, e só se o conteúdo mudou
  if diff -rq "${dir}" "${dest}" >/dev/null 2>&1; then
    ok "${name} já atualizada"
  elif [ "$FORCE" = 1 ]; then
    run mkdir -p "${BACKUP_DIR}"
    run cp -R "${dest}" "${BACKUP_DIR}/${name}"
    run rm -rf "${dest}"
    run cp -R "${dir}" "${dest}"
    ok "${name} ATUALIZADA (backup em ${BACKUP_DIR}/${name})"
  else
    warn "${name} está desatualizada — rode com --force para atualizar"
    outdated=$((outdated + 1))
  fi
done

echo
if [ "$outdated" -gt 0 ]; then
  bold "${outdated} skill(s) desatualizada(s). Para atualizar:"
  echo "  ./install.sh --force        # move a versão atual para ~/.claude/skills-backup-<data>/"
  echo
fi
bold "Pronto. Reinicie o Claude Code para carregar tudo."
echo "  Plugins:  /plugin  (gerenciar)"
echo "  Skills:   já carregam automaticamente de ~/.claude/skills/"
