# Impeccable — regras destiladas pro carrossel (offline)

Destilado do skill `impeccable` (~/.claude/skills/impeccable) pras decisões de UI do carrossel, pra rodar **sem depender do skill em runtime**. Opcionalmente, depois de renderizar, dá pra rodar `/impeccable audit` e `/impeccable polish` sobre o HTML pra um passe extra — mas estas regras já cobrem o caminho padrão.

## Tipografia
- Escala modular, **poucos tamanhos com muito contraste** (ratio 1.25). Evitar 5 tamanhos quase iguais (hierarquia "lamacenta").
- Hierarquia por **2–3 dimensões** (tamanho ≥3:1 + peso + cor/posição/espaço). Tamanho sozinho é fraco.
- **ALL-CAPS** (eyebrow, label): tracking **0.05–0.12em**. Capitais no default ficam apertadas; sem isso parecem "espremidas" — e o exagero oposto (3px em fonte pequena) parece "espaçada demais". Fique na faixa.
- Headline grande condensada: tracking **negativo** (`-0.02em`).
- **Light-on-dark** (texto claro no escuro): compensar nos 3 eixos — line-height +0.05, letter-spacing +0.01em, peso +1 passo. Senão o texto "some".
- `text-wrap: balance` em headline; `pretty` no corpo. Medida do corpo 28–34ch.

## Cor (OKLCH)
- Usar **OKLCH**, não HSL. Reduzir chroma perto de branco/preto.
- **Nunca `#000`/`#fff`.** Neutros **tintados** na direção do hue da marca (chroma 0.005–0.015).
- O hue vem da **marca**, não de default. **Não** puxar azul (~250) nem laranja (~60) por reflexo — são os defaults de "design de IA".
- **60-30-10**: 60% neutro, 30% texto/secundário, 10% accent. Accent funciona porque é raro.
- Dark mode: superfície oklch 12–18%, peso do corpo −1 passo, accent levemente dessaturado.
- Alpha demais = cheiro de paleta incompleta. Definir scrims/overlays explícitos (exceção: estados interativos).

## Layout
- **Espaço é material.** Variar ritmo: agrupar próximo (8–24px), separar generoso (40–96px). Padding igual em tudo = monotonia.
- **Squint test:** desfoque os olhos — primário/secundário/agrupamentos têm que aparecer.
- Esquerda + assimetria > tudo centralizado.
- Hierarquia com o **mínimo de dimensões** necessárias (às vezes só espaço + peso).
- Sem **card-grid idêntico** repetido. Cards só quando são a melhor opção; nunca card dentro de card.
- z-index semântico; sombras sutis ("se dá pra ver claramente, está forte demais").

## Carga cognitiva
- **≤ 4 elementos/ideias distintas por slide.** Mais que isso, cortar ou dividir. (No carrossel: eyebrow + headline + corpo + 1 elemento já fecha o orçamento.)

## Bans absolutos (match-and-refuse — reescrever)
- **Side-stripe borders** (`border-left/right` colorido >1px em card/lista/callout). Usar borda completa, tint de fundo, número-líder/ícone, ou nada.
- **Gradient text** (`background-clip:text`). Cor sólida; ênfase por peso/tamanho.
- **Glassmorphism decorativo** por default. Raro e proposital, ou nada.
- **Hero-metric template** (número gigante + label + stats + gradiente). Clichê SaaS.
- **Em dash (—)** em chrome/labels de UI. (No corpo editorial PT-BR é permitido — ver manual-de-qualidade.)

## Teste anti-AI-slop (rodar antes de exportar)
- **1ª ordem:** dá pra adivinhar tema+paleta só pela categoria? ("IA → azul/ciano no preto"). Se sim, retrabalhar paleta/cena.
- **2ª ordem:** dá pra adivinhar a família estética por categoria+anti-referência? Retrabalhar até nenhum dos dois ser óbvio.

## Checklist pré-export (carrossel)
- [ ] **Sem watermark** "Powered by Content Machine" — brand bar só `@handle` + ano.
- [ ] **Sem side-stripe** em nenhum card/lista.
- [ ] Cor **derivada da marca** (não azul/laranja por reflexo); passa no teste anti-slop.
- [ ] Tracking certo (ALL-CAPS 0.08em; headline −0.02em; corpo 0).
- [ ] Degrau `--t-lead` presente onde há salto corpo→headline.
- [ ] **Canvas preenchido** (55–75% da altura útil) — nenhum slide com metade vazia.
- [ ] Texto sobre imagem com scrim AA ≥ 4.5:1 (usar `--measure-luma`).
- [ ] ≤4 ideias por slide. Squint test passa.
- [ ] Acentos PT-BR renderizam (fontes base64 latin + latin-ext).
