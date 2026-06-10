#!/usr/bin/env bash
#
# Claude Code Starter Pack — instalador
#
# Faz três coisas:
#   1. Registra o marketplace oficial da Anthropic (idempotente)
#   2. Instala os plugins essenciais (skill-creator, superpowers, frontend-design)
#   3. Copia o subconjunto curado de skills próprias para ~/.claude/skills/
#
# Uso:  ./install.sh
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

bold() { printf '\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
info() { printf '  \033[34m→\033[0m %s\n' "$1"; }

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
  claude plugin marketplace add "${MARKETPLACE}"
  ok "marketplace '${MARKETPLACE_NAME}' adicionado"
fi

# --- 2. plugins oficiais --------------------------------------------------
bold "2/3  Plugins essenciais"
for p in "${PLUGINS[@]}"; do
  if claude plugin list 2>/dev/null | grep -q "^${p}\b\|${p}@"; then
    ok "${p} já instalado"
  else
    info "instalando ${p}…"
    claude plugin install "${p}@${MARKETPLACE_NAME}"
    ok "${p} instalado"
  fi
done

# --- 3. skills próprias curadas ------------------------------------------
bold "3/3  Skills curadas"
mkdir -p "${SKILLS_DIR}"
for dir in "${SELF_DIR}"/skills/*/; do
  name="$(basename "${dir}")"
  dest="${SKILLS_DIR}/${name}"
  if [ -d "${dest}" ]; then
    ok "${name} já existe em ~/.claude/skills (pulado)"
  else
    cp -R "${dir}" "${dest}"
    ok "${name} copiada"
  fi
done

echo
bold "Pronto. Reinicie o Claude Code para carregar tudo."
echo "  Plugins:  /plugin  (gerenciar)"
echo "  Skills:   já carregam automaticamente de ~/.claude/skills/"
