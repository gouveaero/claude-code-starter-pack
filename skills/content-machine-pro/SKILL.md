---
name: content-machine-pro
description: >-
  Versão PRO da máquina de carrosséis virais BrandsDecoded — carrosséis de Instagram com IMAGENS DE
  FUNDO (geradas por IA, buscadas em stock ou fornecidas por você), UI nível impeccable (tipografia/
  proporção/cor corrigidas), paleta derivada da MARCA do projeto e SEM marca d'água. Use quando o
  usuário quiser um carrossel viral "caprichado/premium", com imagens de fundo, ou citar "carrossel
  pro", "content machine pro", "carrossel com imagem de fundo", "carrossel com IA", "deixa mais
  bonito/profissional", ou pedir um carrossel pra uma marca específica (qualquer cliente, produto ou
  projeto pessoal) com visual forte. Mesmo pipeline editorial da content-machine (briefing → 10 headlines calibradas →
  espinha → validação → texto → imagens → HTML 1080×1350 → PNG), mas com design system novo (estilos
  Editorial/Clean/Bold/Minimal, cor da marca, texto preenchendo o canvas) e geração/busca de imagens.
  Prefira esta à `content-machine` original (fundo sólido, com watermark) sempre que quiser imagens de
  fundo e acabamento premium. NÃO use pra deck/palestra (slidev) nem pra capa única de notícia (newsroom-pro).
---

# Content Machine PRO — Carrossel viral com imagens de fundo (BrandsDecoded)

Fork "pro" da máquina de carrosséis. Mesmo cérebro editorial — briefing → 10 headlines calibradas →
espinha narrativa → validação editorial → texto aprovado → imagens → HTML 1080×1350 → PNGs — com três
upgrades grandes:

1. **Imagens de fundo de verdade** (não fundo sólido): geradas por IA, buscadas em stock/web ou fornecidas por você, com tratamento duotone e scrim pra legibilidade.
2. **UI nível impeccable**: tipografia/proporção/cor corrigidas, **texto preenche o canvas**, múltiplos estilos visuais, **cor sempre derivada da marca** do projeto.
3. **Sem white-label**: a brand bar é só `@handle` + ano (nada de "Powered by Content Machine").

Continua generalista: serve qualquer marca/nicho. Bastidor invisível — o usuário vê só o resultado de cada etapa.

## Antes de responder: leia a spec + o design

- **[references/system-prompt.md](references/system-prompt.md)** — o cérebro editorial (verbatim). Fluxo de etapas, engine de headlines, regras de copy. **Leia primeiro.**
- **[references/design-system.md](references/design-system.md)** — o NOVO sistema visual (substitui o Bloco 6 do system-prompt). Tokens, paleta por marca, estilos, fill-the-canvas, imagens, chrome sem watermark.
- **[references/impeccable-baked.md](references/impeccable-baked.md)** — regras de UI + checklist pré-export.

**Onde conflitar, o design-system.md e o impeccable-baked.md vencem o Bloco 6 do system-prompt.** Em particular: **ignore a linha "Powered by Content Machine"** da brand bar; **não use side-stripe borders**; cores/tracking/zonas são os do design-system.

## Ambiente: Claude Code (não Claude.ai)

Igual à content-machine original: `present_files` → gravar arquivo no disco + `open` no navegador; pasta de saída `content-machine-pro-out/<slug>/` no cwd (ou perguntar se for repo de cliente); ignorar paths de sandbox; fontes via `scripts/fonts_to_base64.py` (base64, nunca `<link>`); export via `scripts/export_png.py`. **Imagens agora vêm de 3 fontes** (ver Etapa 3.9 + image-direction.md), não só upload do usuário.

## Pipeline (visão geral — detalhe na spec)

Igual ao original até o texto aprovado, com uma etapa de imagem reforçada:

1. **Entrada** (saudação + 2 intenções) → **Briefing** (7 perguntas; cor = da marca, ou "não sei" → nicho; estilo visual = Editorial/Clean/Bold/Minimal).
2. **Headlines** (10, formatos rígidos) → **Espinha** → **Validação editorial** → **Aprovação de texto** ("aprovado").
3. **Etapa 3.9 — Imagens de fundo (NOVA).** Pra cada slide, a skill **decide deliberadamente** gerar (IA) vs buscar (stock/web) vs deixar limpo, conforme a heurística de **[references/image-direction.md](references/image-direction.md)**. Capa sempre tem imagem; dados/gradient/CTA ficam limpos; teto ~4 imagens. Obtém a URL → normaliza com `scripts/fetch_image.py` → base64 no HTML. Ciente de saldo, sem narrar o processo. **Sem MCP de imagem instalado a skill continua funcionando** — ver "Sem MCP de imagem" em image-direction.md.
4. **Render HTML** (design-system.md: estilo escolhido, cor da marca, canvas preenchido, scrim AA) → **Export PNG** ("exportar") → **Legenda**.

## Quando ler cada reference

- **system-prompt.md** — sempre primeiro (fluxo + copy + headlines).
- **design-system.md** + **impeccable-baked.md** — ao montar o HTML (Etapa 5) e no checklist pré-export.
- **image-direction.md** — na Etapa 3.9 (gerar/buscar imagens; prompts; distribuição).
- **banco-de-headlines.md** — Etapa 2 (headlines + capa).
- **filtro-editorial.md** + **manual-de-qualidade.md** (seção "Refinamentos Pro") — validação editorial (3.5) e títulos internos.
- **principios-design.md** — princípios + tabela de paleta por nicho ("não sei" a cor).
- **referencias.md** + **boas-praticas.md** — exemplos, pautas, customização, checklist.

## Scripts bundled

- `python3 scripts/fonts_to_base64.py "Fonte Headline:700" "Fonte Body:400,600,700" > fonts.css` — `@font-face` base64 (latin + latin-ext).
- `python3 scripts/fetch_image.py --source url --url "<url>" --out <slide>.jpg --crop smart --measure-luma --emit-base64` — baixa/normaliza pra 1080×1350, mede luma do rodapé (dimensiona o scrim) e emite data-URI. Aceita **qualquer URL** e também `--source unsplash --query "..."` (precisa `UNSPLASH_ACCESS_KEY`), então funciona com ou sem MCP — ver image-direction.md.
- `python3 scripts/export_png.py content-machine-pro-out/<slug>/carousel.html` — screenshota cada `.slide` em 1080×1350.
- Deps: Playwright + Chromium (`pip install playwright && python -m playwright install chromium`), Pillow (fallback `sips`/`magick`). `python3` = 3.9.

## Polimento opcional via impeccable

As regras já estão bakeadas (impeccable-baked.md). Pra um passe extra sobre o HTML gerado, dá pra invocar o skill `impeccable`: `/impeccable audit <html>` (contraste/a11y), `typeset`/`layout`/`colorize` (alvo específico) ou `polish` (geral). Off por default — oferecer como "quer um polimento de UI no impeccable?" depois do 1º render.

## Mandamento

Bastidor invisível. Cor da marca, não a sua. Canvas preenchido, sem espaço morto. Sem watermark, sem side-stripe. O sistema é invisível; o carrossel é tudo.
