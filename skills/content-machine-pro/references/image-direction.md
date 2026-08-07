# Direção de Imagem — fundos do carrossel (gerar vs buscar)

Como a skill obtém e aplica imagens de fundo. A skill **decide sozinha, deliberadamente**, slide a slide, quando vale gerar uma imagem única com IA e quando vale buscar uma real na web. Livre pra fazer isso a qualquer momento.

> **Provedores são opcionais.** Higgsfield e Magnific abaixo são só os caminhos *preferidos* quando existem. O contrato real do pipeline é: **a skill consegue uma URL de imagem → `fetch_image.py` faz o pixel**. Qualquer fonte que produza uma URL serve. Se nenhum MCP de imagem estiver instalado, pule para **"Sem MCP de imagem"** no fim deste arquivo — a skill continua entregando o carrossel completo.

## Heurística: gerar (IA) vs buscar (web/stock)

| Situação | Fonte | Por quê |
|---|---|---|
| Conceito abstrato, metáfora visual, cena única, "algo que não existe em foto" | **Gerar** (IA) | Imagem única, contextual, coesa com a marca |
| Assunto real concreto (pessoa pública, produto, lugar, marca, objeto) | **Buscar** (stock / web) | Mais rápido, real, sem crédito |
| Coesão visual entre vários slides | **Gerar** (mesma direção de arte) ou aplicar **duotone** em todas | Uniformiza fontes diferentes |
| Slide de dado / gradient / CTA | **Sem imagem** | Limpo (impeccable: "ou nada"; não é todo slide que leva foto) |

Teto padrão **~4 imagens** por carrossel (custo + carga cognitiva). Capa SEMPRE tem imagem.

## Fluxo Higgsfield (provedor de IA preferido — **se instalado**)

Saldo: `mcp__higgsfield__balance`. Modelo: `recraft-v4-1` é ótimo (suporta **`aspect_ratio: "4:5"` nativo = 1080×1350, sem crop**, e aceita `colors` da marca). Alternativas via `mcp__higgsfield__models_explore` (`action:recommend`).

```
generate_image({ params:{
  model:"recraft-v4-1", prompt:"<prompt>", aspect_ratio:"4:5",
  model_type:"standard", colors:["<hex marca>","<hex accent>","<hex fundo>"], count:1 }})
  → { results:[{ id }] }              # async
job_status({ jobId:id, sync:true })   # poll; ~10-20s; repetir honrando poll_after_seconds
  → results.rawUrl                    # URL final
```
Depois: `python3 scripts/fetch_image.py --source url --url "<rawUrl>" --out <slide>.jpg --crop smart --measure-luma --emit-base64`. Se o modelo não fizer 4:5, gere o mais próximo e o `--crop smart` ajusta. `get_cost:true` no generate_image pré-calcula o custo sem gastar.

## Fluxo web/stock (imagem real)

- **Magnific stock:** `mcp__magnific__stock_search({query, content_type:"photo", per_page:10})` → escolher item → `mcp__magnific__stock_download({id})` → `{download_url}` → `fetch_image.py --source url --url <download_url>`.
- **Magnific IA (alternativa ao Higgsfield, 4:5 nativo):** `images_generate({prompt, aspectRatio:"4:5"})` → `creations_wait({identifiers, timeoutSeconds:25})` → `creations_get` → `url` → `fetch_image.py`.
- **Unsplash (fallback, precisa `UNSPLASH_ACCESS_KEY`):** `fetch_image.py --source unsplash --query "..."`.
- **URL direta / arquivo do usuário:** `fetch_image.py --source url --url <...>` ou ler o arquivo e base64.

## Prompts de geração (template)

Sempre incluir negative space embaixo (pro texto) e proibir texto/logo:

> `<assunto concreto do slide>, <mood do nicho>, editorial photography, cinematic lighting, muted <família de cor da marca> tones, deep dark negative space in the lower third for text overlay, no text, no letters, no logos, no watermark, no people unless essential, ultra detailed, 4:5 vertical`

- Passar `colors` da marca pro Recraft reforça coesão cromática.
- Para coesão entre slides: manter a mesma direção de arte (mesma luz, mesma paleta) nos prompts.
- Para **busca**: derivar 2–4 queries curtas dos substantivos do slide (sem o sufixo de estilo).

## Distribuição pelos 9 slides

```
1 Capa      imagem SEMPRE (gerar conceito-mãe ou foto de impacto) — full-bleed + scrim
2 Hook      imagem (duotone) ou sólido
3 Contexto  geralmente sólido + numeral
4 Mecanismo imagem contextual (gerar)
5 Prova     SEM imagem (dados limpos)
6 Expansão  imagem (web/stock se concreto) ou numeral
7 Aplicação image-in-card (web/stock) ou sólido
8 Direção   SEM imagem (gradient da marca)
9 CTA       SEM imagem (limpo)
```
Capa primeiro; preencher os escuros contextuais; nunca os de dado/gradient/CTA. Tratar tudo com duotone tintado na marca (estilo Editorial) pra uniformizar fontes diferentes — ver `design-system.md §5`.

## Segurança de crédito
- A skill é livre pra gerar, mas **ciente do saldo**: checar `balance` na 1ª geração da sessão e respeitar o teto (~4). Se o saldo estiver baixo, avisar e cair pra web/stock.
- Nunca disparar dezenas de gerações. Lote enxuto, reaproveitar a imagem-mãe da capa quando fizer sentido.

## Sem MCP de imagem

Higgsfield e Magnific são **opcionais**. Se nenhum dos dois estiver disponível na sessão, **não pare e não peça pro usuário instalar MCP** — desça a escada abaixo, na ordem, e entregue o carrossel do mesmo jeito. Trate isso como caminho normal, não como erro.

| # | Fonte | Como |
|---|---|---|
| 1 | **Imagens do próprio usuário** | Pergunte uma vez, no briefing, se ele tem fotos da marca/produto. Arquivo local → `fetch_image.py --source url --url "file:///caminho/foto.jpg"` (ou leia e converta em base64). Sempre a melhor opção quando existe. |
| 2 | **Unsplash** | `fetch_image.py --source unsplash --query "<2-4 substantivos do slide>"`. Precisa de `UNSPLASH_ACCESS_KEY` no ambiente (chave gratuita em unsplash.com/developers). Cobre praticamente todo assunto concreto. |
| 3 | **URL direta** | Qualquer imagem aberta que a sessão consiga achar (WebSearch/WebFetch, banco de stock livre, página do produto) → `fetch_image.py --source url --url "<url>"`. Respeite a licença: só o que for livre pra uso. |
| 4 | **Zero imagem — modo Minimal** | Último degrau. Não é falha: é uma decisão de design. Ver abaixo. |

**Modo Minimal (fallback final).** Sem nenhuma imagem, mude o *estilo* em vez de entregar slides pobres: use `Minimal` ou `Bold` do design-system, e compense a ausência de foto com o que já é forte na skill —

- **numeral gigante** e hierarquia tipográfica extrema (o texto vira o visual);
- **gradientes da cor da marca** + campos de cor sólidos alternando slide a slide;
- **grafismos CSS**: fios, réguas, blocos, grid sutil, aspas grandes;
- ritmo de layout variando entre slides pra ninguém achar que é template.

O duotone e o scrim (design-system.md §5) só se aplicam quando há foto — sem imagem, o contraste vem direto do par cor-de-marca/fundo, e o checklist AA do `impeccable-baked.md` continua valendo igual.

**Avise uma linha, sem drama.** Ex.: "Sem provedor de imagem por aqui — vou no estilo Minimal, com numeral e gradiente da marca. Se quiser foto, me manda as suas ou configura uma `UNSPLASH_ACCESS_KEY`." Depois siga o pipeline normalmente.
