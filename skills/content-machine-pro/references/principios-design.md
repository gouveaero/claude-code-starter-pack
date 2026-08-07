# Princípios de Design — Carrossel Pro

Realinhado à versão Pro. Os detalhes de CSS/tokens estão em [design-system.md](design-system.md); as regras de UI em [impeccable-baked.md](impeccable-baked.md). Aqui ficam os princípios e a tabela de paleta por nicho.

## Filosofia Pro (o que mudou)

1. **Generalista, dirigido pela marca.** Cada projeto (cliente, produto, marca pessoal…) tem sua cor, sua fonte, seu tom. Nada hardcoded. A cor vem da marca; o estilo, do contexto.
2. **Preencher o canvas.** O slide ocupa 55–75% da altura útil. Texto grande + um elemento estrutural (numeral, palavra-display, imagem). Espaço morto é defeito.
3. **Explorar contextos e estilos.** Editorial, Clean, Bold, Minimal (design-system §3). Escolher pelo briefing ou propor; misturar quando fizer sentido. Não há look único.
4. **Imagem de fundo é regra, não exceção.** Gerada por IA (Higgsfield) ou buscada (web/stock) — image-direction.md.
5. **Sem white-label.** A peça é do cliente; brand bar = `@handle` + ano.

## Hierarquia (resumo)

- 2–3 dimensões simultâneas (tamanho ≥3:1 + peso + cor/posição/espaço).
- Eyebrow → Headline → Lead (degrau intermediário) → Corpo. O Lead (`--t-lead` 46px) existe pra matar o salto corpo→headline.
- ≤4 ideias por slide. Squint test antes de exportar.

## Tom visual por estilo (quando propor)

- **Editorial:** dramático, premium, numeral gigante, duotone, kicker+fio. Bom pra tese/análise, marca de autoridade.
- **Clean:** claro/escuro alternado, leve, direto. Bom pra educativo, SaaS, B2B.
- **Bold:** impacto, headline gigante, escuro. Bom pra provocação, lançamento.
- **Minimal:** tipográfico, muito ar, tipo grande. Bom pra marca sóbria, premium discreto.

## Paleta por nicho (ponto de partida quando o usuário diz "não sei")

Pontos de partida — sempre tintar neutros na direção do hue e rodar o guard anti-slop (design-system §2). NUNCA tratar como fixo; a cor real da marca vence.

| Nicho | Primária | Accent 2 | Fonte headline sugerida |
|---|---|---|---|
| Marketing/Negócios | #E8421A | #1B2A4A | Barlow Condensed |
| IA / Tech / SaaS | #3C83F6 | #F59F0A | Space Grotesk |
| Imobiliário | #1B2A4A | #C9A84C | Montserrat |
| Fitness/Saúde | #E94560 | #1A1A2E | Inter |
| Gastronomia | #C0392B | #D4A574 | Playfair Display |
| Moda/Beleza | #1C1C1C | #C4956A | Cormorant Garamond |
| Educação | #1B3A4B | #34B3A0 | Source Sans Pro |
| Advocacia/Jurídico | #1A2A4A | #B8860B | EB Garamond |
| Finanças/Contábil | #143B2E | #C9A84C | Roboto Slab |
| Saúde/Medicina | #0E6B6B | #4AC0B0 | DM Sans |
| Pet/Veterinária | #2D6A4F | #E17055 | Quicksand |

Se o nicho não estiver na tabela, derivar da cor informada ou propor 2 opções e deixar o usuário escolher.

## Copy (resumo — detalhe nos arquivos verbatim)

- Anti-AI-slop e os 7 parâmetros editoriais ficam em `filtro-editorial.md` e `manual-de-qualidade.md` (mantidos da versão original; ver a seção **Refinamentos Pro** no final do manual).
- Títulos internos: ancorados e concretos (substantivo do slide), nunca slogan genérico.
- Em-dash (—) é permitido no **corpo editorial** PT-BR; o ban do impeccable vale só pro **chrome/labels de UI**.
