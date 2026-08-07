# Design System — Carrossel Pro (1080×1350)

Versão Pro. Substitui o design-system 5.5. Três mudanças de fundo em relação ao original:

1. **A cor é SEMPRE da marca do projeto** (cliente, produto, marca pessoal…), derivada no briefing — nunca uma paleta fixa. Skill generalista, como a original.
2. **O texto preenche o canvas.** Nada de metade da tela vazia. Cada slide ocupa uma porção generosa com tipo grande + um elemento estrutural (numeral gigante, palavra-display, imagem). Espaço morto é bug.
3. **Imagens de fundo são padrão** (geradas por IA, buscadas em stock/web ou fornecidas pelo usuário) — ver [image-direction.md](image-direction.md). E **sem marca d'água**: a brand bar é só `@handle` + ano.

Princípios de UI seguem [impeccable-baked.md](impeccable-baked.md) (OKLCH, tinted neutrals, sem side-stripe, sem em-dash em chrome, teste anti-AI-slop). Leia os dois antes de renderizar.

---

## 1. Tokens de tipografia (escala modular 1.25, canvas fixo → px fixo)

```css
:root{
  --t-cap: 19px;    /* eyebrow, brand bar, labels (ALL-CAPS) */
  --t-meta: 24px;   /* progresso, página, footnote */
  --t-body: 36px;   /* corpo */
  --t-lead: 46px;   /* frase-líder — DEGRAU INTERMEDIÁRIO (preenche o vão corpo→headline) */
  --t-h3: 58px;     /* headline interna leve */
  --t-h2: 74px;     /* headline interna forte */
  --t-h1: 94px;     /* headline de capa */
  --t-display: 118px; /* capa curta / palavra-display / big stat */
  --t-num: 300px;   /* numeral estrutural gigante (preenche slides esparsos) */
}
```

**Tracking (corrige a queixa "letras muito espaçadas"):**
- Headline (display/h1/h2/h3, ALL-CAPS condensada): `letter-spacing: -0.02em`. **Nunca** o `3px` em tag pequena (≈0.23em) do original.
- Eyebrow/tag/brand-bar (ALL-CAPS pequena): `letter-spacing: 0.08em–0.10em` (faixa impeccable 0.05–0.12em).
- Corpo (sentence case): `letter-spacing: 0` (remover o `-0.2px`).

**Line-height:** headline `0.95–0.99`; lead `1.28`; corpo `1.5`. **Light-on-dark (texto claro em fundo escuro): compensar em 3 eixos** — line-height +0.05 (corpo `1.55`), `letter-spacing: 0.01em`, peso +1 passo (400→500). Sem isso o texto some no escuro.

**Render:** `text-wrap: balance` em headline, `text-wrap: pretty` no corpo. Corpo com `max-width: 28–34ch` (medida confortável).

**Fontes:** SEMPRE `@font-face` base64 (gerar com `scripts/fonts_to_base64.py`), nunca `<link>` Google Fonts. Headline = fonte da marca (Space Grotesk, Barlow Condensed, etc.); corpo = a de leitura da marca (Inter, Plus Jakarta, etc.).

---

## 2. Paleta derivada da MARCA (generalista, OKLCH, anti-slop)

A cor vem do briefing (1–2 hex da marca, ou "não sei" → derivar do nicho). Recipe:

1. Converter o hex primário da marca → OKLCH, ler o hue **H**.
2. Derivar variantes mantendo H, variando L e **baixando chroma ao clarear** (alto chroma perto do branco fica berrante):
```css
:root{
  --P:   <hex primário da marca>;                 /* accent principal */
  --PL:  oklch(from var(--P) calc(l + 0.14) calc(c - 0.04) h);  /* claro (texto em fundo escuro) */
  --PD:  oklch(from var(--P) calc(l - 0.16) c h);               /* escuro (texto em fundo claro) */
  --A2:  <2º hex da marca, se houver>;            /* accent secundário (opcional) */
  /* Neutros TINTADOS na direção de H (nunca #000/#fff) */
  --DB:  oklch(0.15 0.02 H);   /* fundo escuro (dark mode 12–18%) */
  --DB2: oklch(0.20 0.02 H);   /* painel escuro */
  --LB:  oklch(0.96 0.008 H);  /* fundo claro tintado */
  --LR:  oklch(0.90 0.01 H);   /* borda clara */
  --ink: oklch(0.18 0.02 H);   /* texto escuro */
  --ink2:oklch(0.40 0.02 H);   /* texto escuro secundário */
}
```
(Se preferir compatibilidade máxima, calcule os hex equivalentes e escreva-os direto — `oklch(from ...)` relativo funciona no Chromium do Playwright, mas hex fixo é à prova de falha.)

3. **Estratégia de cor (impeccable, eixo de comprometimento):** capa/gradient = **Committed** (a cor da marca carrega 30–60%); slides internos = **Restrained** (neutro tintado + accent ≤10%). Aplicar 60-30-10 por slide.
4. **Guard anti-AI-slop:** se H cair em ciano ~195–230 OU violeta ~280–300 sobre quase-preto (o reflexo "ferramenta de IA"), desloque o hue ou compense com um **accent secundário quente** (uma dupla azul+dourado, por exemplo, é exatamente essa correção). Rode o teste de reflexo de categoria do impeccable: "dá pra adivinhar a paleta só pelo nicho?" Se sim, retrabalhe.
5. **Accent secundário:** quando a marca tem 2 cores (ex.: azul+dourado), use a 2ª como pop em CTA, numeral, fios e underline — dá identidade e quebra o monocromático. Quando só tem 1, derive um neutro-quente ou use o próprio accent com parcimônia.

> Cores são exemplos por projeto, **nunca hardcoded**: uma marca pode ser `#3c83f6`+`#f59f0a`; a próxima terá outro H. A tabela de nicho do `principios-design.md` dá pontos de partida quando o usuário não sabe a cor.

---

## 3. Estilos visuais (a skill EXPLORA contextos — não há look único)

Um **core** comum (tokens, paleta, chrome, contrato de imagem) + **presets de estilo** que mudam a personalidade. Escolher pelo briefing (estilo + nicho + marca) ou propor; dá pra misturar. O default recomendado é **Editorial** (testado, preenche o canvas, premium).

| Estilo | Personalidade | Marcas de estilo |
|---|---|---|
| **Editorial** (flagship) | Revista premium, dramático | Kicker com tick, fio fino no topo, **numeral estrutural gigante** preenchendo slides esparsos, imagens **duotone** tintadas na marca, headline pesada |
| **Clean** | SaaS moderno, claro/escuro alternado, leve | Sem numeral; respiro maior; accent só em palavra-chave; imagens full-bleed naturais |
| **Bold** | Impacto máximo | Headline `--t-display`, fundo majoritariamente escuro, numeral opacity baixa, accent forte |
| **Minimal** | Tipográfico, muito ar | Maioria clara, 1–2 escuros, imagens raras (image-in-card), tipo grande, zero ornamento |

Cada preset é um conjunto de overrides de CSS sobre o core. Mantêm SEMPRE: cor da marca, fill-the-canvas, sem watermark, sem side-stripe, contrato de legibilidade.

---

## 4. Layout — PREENCHER O CANVAS (a diretriz central)

O problema do original: `justify-content:flex-end` jogava tudo embaixo e deixava o topo vazio. O problema oposto (ancorar no topo) deixa o rodapé vazio. **Solução: cada slide ocupa uma porção generosa da tela; o que sobraria vira elemento estrutural, nunca vazio.**

```css
.content{ position:absolute; inset:160px 64px 130px; display:grid; z-index:10; }
```

**Alvo de preenchimento:** o conteúdo (texto + elementos) ocupa **55–75% da altura útil**. Regras por densidade:

- **Slide com bastante texto** → tipo grande (headline `--t-h2/--t-h1` + lead `--t-lead` + corpo) preenche naturalmente. `align-content:start` ou `space-between`.
- **Slide esparso (pouca copy)** → **NÃO deixe vazio.** Preencha com um destes: (a) **numeral estrutural gigante** (`--t-num`, outline ou opacity baixa, atrás/ao lado do texto — estilo Editorial), (b) **palavra-display** (uma palavra-chave em `--t-display`), (c) **imagem de fundo**, (d) tipo ainda maior.
  - **Slide SEM imagem (light/CTA):** centralize o bloco verticalmente (`justify-content:center`) e posicione o numeral grande abrangendo a altura (`top:50%; transform:translateY(-50%)`, font-size ~440–460px). Equilibra e evita o "vazio numa borda só" (testado: ancorar só no topo ou só na base deixa metade morta).
  - **Slide COM imagem full-bleed:** o texto ancora no rodapé, dentro do scrim escuro (`justify-content:flex-end`) — a imagem preenche o resto.
- **Squint test** (impeccable): desfoque os olhos — primário, secundário e agrupamentos têm que aparecer. Hierarquia por 2–3 dimensões (tamanho ≥3:1 + peso + cor/posição).
- **Ritmo (impeccable):** agrupar próximo (16–24px entre irmãos), separar generoso (40–64px entre blocos). Escala **4pt**: `8/16/24/32/40/64`. Variar — padding igual em tudo é monotonia.
- **Assimetria:** alinhar à esquerda, evitar tudo centralizado. CTA pode quebrar o padrão.

**Numeral estrutural (preenche + dá ritmo editorial):**
```css
.bignum{ position:absolute; font-family:var(--FH); font-weight:700; font-size:var(--t-num);
  line-height:.8; z-index:1; color:transparent; -webkit-text-stroke:2px color-mix(in oklch, var(--A2, var(--P)) 30%, transparent); }
/* variante preenchida sutil: color: color-mix(in oklch, var(--P) 6%, transparent); */
```

---

## 5. Imagens de fundo (padrão — ver image-direction.md pro pipeline)

Tratamentos (cada um com contrato de legibilidade). Imagens entram como base64 (`scripts/fetch_image.py --emit-base64`) ou `file://` no preview.

```css
.imgbg{ position:absolute; inset:0; background-size:cover; background-position:center; z-index:0; }
/* DUOTONE tintado na marca — faz fotos de fontes variadas (IA, stock, web) lerem como UMA marca */
.imgbg.duo{ filter:grayscale(.92) contrast(1.08) brightness(.82); }
.duotone{ position:absolute; inset:0; z-index:1; background: var(--P); mix-blend-mode:color; opacity:.55; }
/* SCRIM — sempre neutro/escuro, NUNCA colorido */
.scrim{ position:absolute; inset:0; z-index:2; }
.sc-cover{ background:linear-gradient(to bottom, rgba(0,0,0,.28) 0%, rgba(0,0,0,.08) 28%, rgba(0,0,0,.5) 60%, rgba(0,0,0,.9) 84%, rgba(0,0,0,.99) 100%); }
.sc-dark{ background:linear-gradient(to bottom, rgba(0,0,0,.55) 0%, rgba(0,0,0,.42) 32%, rgba(0,0,0,.8) 72%, rgba(0,0,0,.96) 100%); }
```

**Contrato de legibilidade (não-negociável):**
- Texto sobre imagem exige scrim que garanta **AA ≥ 4.5:1** no pixel mais claro sob o texto. Use `fetch_image.py --measure-luma` → `SCRIM_SUGGEST` pra dimensionar a opacidade do scrim de forma determinística (faixa 0.72–0.99).
- Scrim **sempre neutro/escuro**, nunca da cor da marca (nada de overlay azul/roxo).
- Accent (cor da marca) **nunca** como preenchimento de texto sobre foto — ênfase por peso.

**Tratamentos:** (a) **full-bleed + scrim** (capa + 2–3 internos), (b) **duotone** (coesão de marca, estilo Editorial), (c) **image-in-card** (mídia com borda completa, sem stripe), (d) **sólido/sem imagem** (slides de dado/CTA — impeccable: "ou nada"; não é todo slide que leva foto).

**Distribuição (9 slides, teto ~4 imagens):** capa SEMPRE; depois slides escuros contextuais; **dados (5), gradient (8) e CTA (9) ficam limpos** (sem foto). A skill decide IA-gerada vs web/stock por slide (ver image-direction.md).

---

## 6. Componentes — SEM side-stripe (ban do impeccable)

O original usava `border-left` colorido (`.dark-card`, `.light-card`, `.light-pex`, `.sig-row`). Proibido. Substituir por:

```css
/* Card: borda completa 1px + tint de fundo (sem stripe) */
.card{ border:1px solid color-mix(in oklch, var(--P) 22%, transparent);
  background: color-mix(in oklch, var(--P) 6%, transparent); border-radius:18px; padding:40px 44px; }
/* Lista de padrões: NÚMERO-LÍDER como âncora (não stripe) */
.plist .item{ display:grid; grid-template-columns:auto 1fr; gap:24px; align-items:baseline; }
.plist .n{ font-family:var(--FH); font-weight:700; font-size:var(--t-h3); color:var(--P); line-height:1; }
/* Quote: glifo de aspas grande, não barra lateral */
.quote{ position:relative; padding-left:0; }
.quote::before{ content:'\201C'; font-family:var(--FH); font-size:140px; color:color-mix(in oklch,var(--P) 30%,transparent); line-height:.7; }
/* Tabela de dados: header com fill colorido (é preenchimento, permitido) */
.tbl th{ background:var(--P); color:#fff; }
```
Underline editorial (ênfase): `box-shadow: inset 0 -0.12em 0 var(--A2, var(--P));` (não border-bottom solto).

---

## 7. Chrome — brand bar SEM watermark, accent bar, progresso

```css
/* Accent bar topo (fina, gradiente da marca) */
.accent{ position:absolute; top:0; left:0; right:0; height:5px; z-index:30;
  background:linear-gradient(90deg, var(--P), var(--A2, var(--PL))); }
/* BRAND BAR — só handle + ano. NUNCA "Powered by Content Machine". */
.brandbar{ position:absolute; top:5px; left:0; right:0; padding:40px 64px 0; display:flex; justify-content:space-between;
  z-index:20; font-size:var(--t-cap); font-weight:600; letter-spacing:0.08em; text-transform:uppercase; }
.on-dark .brandbar{ color:rgba(255,255,255,.5); } .on-light .brandbar{ color: color-mix(in oklch, var(--ink) 45%, transparent); }
/* Progresso/página */
.pagenum{ position:absolute; bottom:0; left:0; right:0; padding:0 64px 46px; display:flex; align-items:center; gap:20px;
  z-index:20; font-size:var(--t-meta); font-weight:600; font-family:var(--FH); }
.pagenum .bar{ flex:1; height:2px; border-radius:2px; }
.pagenum .bar i{ display:block; height:100%; border-radius:2px; background:var(--P); }
```
`brandbar` esquerda = `@handle`; direita = `ano ®`. (Estilo Editorial pode trocar por rail com `MARCA — Nº NN` + seção.) **Sem swipe arrow** (o swipe é nativo do Instagram).

> **Override explícito:** o `system-prompt.md` (verbatim) ainda manda escrever "Powered by Content Machine" na brand bar — **ignore essa linha**. A brand bar é a definida aqui (sem white-label). Onde o `Bloco 6` do system-prompt conflitar, as cores/tracking/zonas deste arquivo prevalecem.

---

## 8. Sequência por nº de slides (treatment-aware)

Mantém a alternância clara/escura pro ritmo (não 100% escuro — cansa), com imagens nos pontos certos:

```
9 slides (padrão):
 1 Capa     full-bleed + scrim       (imagem SEMPRE)
 2 Hook     dark + imagem/duotone    (imagem)
 3 Contexto light, numeral/limpo
 4 Mecanismo dark + imagem           (imagem)
 5 Prova    light, dados — LIMPO (sem foto)
 6 Expansão dark + numeral ou imagem
 7 Aplicação light, image-in-card OU limpo
 8 Direção  GRADIENT da marca (sem foto)
 9 CTA      light/dark — LIMPO (sem foto)
```
5/7/12 slides: condensar/expandir mantendo capa(img) → alternância → gradient (penúltimo) → CTA limpo. Últimos 3 slides sempre preparam o CTA.

---

## 9. Render + export

- Slides 1080×1350 nativos empilhados (`flex-direction:column; gap`), CSS inline no `<style>`, fontes base64, imagens base64.
- Preview: abrir o HTML (`open`); export: `scripts/export_png.py <html>` (screenshota cada `.slide`).
- Antes de exportar: rodar o checklist do [impeccable-baked.md](impeccable-baked.md) (squint test, contraste AA, sem side-stripe, sem watermark, canvas preenchido) — ou, opcionalmente, `/impeccable audit` + `polish` sobre o HTML.
