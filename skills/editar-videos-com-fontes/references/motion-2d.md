# Motion 2D sobre vídeo falado (receita genérica)

Receita para pegar um bruto falando para a câmera e entregar **rosto + animações 2D sincronizadas com as palavras**, com cortes de pausas/resets, 1× e 1,25×, legenda queimada e QA por quadros. Não depende de tema, marca, pessoa ou projeto: troque só o conteúdo das cenas.

Quando usar: o pedido é "animações/motion explicando a fala" em vídeo gravado (não geração de apresentador). Para o motor HTML+GSAP, o estilo e as primitivas de cena, use a skill `animacao-explicativa` (`references/cenas_html.md`, `movimento.md`). Esta receita só cobre a **costura** com o vídeo editado.

## Regras fixas (a menos que o pedido diga outra coisa)
- **Voz original**: a animação é só vídeo; o áudio sai do master do rosto (`-c:a copy`). Nunca regravar nem sintetizar.
- **Rosto na abertura e no CTA.** O gancho (primeiros segundos) e a chamada final ficam com o rosto, sem animação por cima.
- **Alternar rosto ↔ animação** no corpo: animação de ~2,5–8 s por ideia; **nunca mais de ~3 s seguidos só de rosto** nem mais de ~8 s seguidos de animação. Sem sobreposição entre janelas.
- **Velocidades: 1,0× e 1,25×.** Nunca 1,3× por padrão (só se pedirem explicitamente). Um único retime a partir do master 1×; nunca acelerar um master já acelerado.
- **Fundo escuro, composição centralizada, nada sobreposto, nada cortado.** Palco seguro 1080×1920: margens de ≥250 px no topo e na base (legenda mora embaixo, título em cima); palco central ~960×1150.
- **Legenda queimada sincronizada com a fala editada** (palavras do ASR do áudio *depois* dos cortes), branca com contorno escuro, ≤2 linhas, sem caixa; SRT com a mesma lista de cues.
- Uma pasta nova por revisão; versões anteriores ficam (renomeie, não apague).

## Ordem de trabalho
1. **Bruto → mapa de cortes.** ASR com tempo por palavra (faster-whisper, `scripts/transcribe_local.py`) → lista `keep=[[ini,fim],…]` removendo pausas longas, falsos começos e "resets" (repetições da mesma frase: fique com a última boa tomada). Margem pequena antes da primeira consoante; confira respiração (`scripts/inspect_audio.py`). Registre origem/entrada/saída/motivo de cada corte. Fade de ~8 ms nas emendas.
2. **Master do corpo (1×, sem animação)** = bruto cortado e concatenado, 1080×1920/30. **Reexecute o ASR sobre este áudio** e corrija nomes próprios: esse JSON é o relógio único de legenda, cenas e SFX.
3. **Janelas de animação.** Sobre o texto do master, marque uma janela `(id, a, b)` por ideia que ganha imagem (número, comparação, lista, fluxo, mapa, contagem). `a`/`b` ficam em fronteiras de palavra (±0,05 s). Os vãos entre janelas são rosto. Guarde em `windows.json` (formato em `scripts/motion2d_composite.py`) e rode `--check`: ele acusa rosto sozinho >3 s, animação >8 s ou <1,2 s e sobreposição.
4. **Cenas 2D** (uma por janela) com o motor HTML+GSAP da skill `animacao-explicativa`:
   - Para cada janela gere o áudio do trecho e o JSON de palavras **relativo ao início da janela** (`palavra, inicio, fim`) e passe como narração da cena. Assim `c.q('palavra')` ancora o movimento *na sílaba falada*.
   - Escreva cada cena em `src/cNN.html` (bloco `<style>` + marcação + `<script>` com a linha do tempo). Um gerador (`gen_scenes`) concatena CSS/JS compartilhados, **prefixa todos os `id` e seletores com o número da cena** (evita colisão entre cenas no mesmo documento) e embrulha em `kit.cena('cena_NN', c => {…})`. Cena sem arquivo vira palco vazio (o composite não deve depender dela).
   - CSS/JS compartilhados: palco central (flex, centralizado), cartão/ícone/pílula/rótulos, 3–4 tamanhos de título, cores de destaque fixas (azul/vermelho/âmbar/verde sobre fundo escuro), ícones por `data-icone`, utilitários de efeito (tremor, contador numérico, escalonamento irregular).
   - Movimento: tudo entra se movendo (nunca só fade), entrada ~0,3–0,4 s, no máximo 1 overshoot por vídeo, uma ideia por vez, texto grande (≥ ~40 px em 1080 de largura). Mapas/gráficos: gere os dados (pontos, caminhos) em script e embuta como JS, não como imagem.
5. **Render das animações** em um único `render.mp4` com as cenas em sequência (HyperFrames). Rode `lint` antes e QA de quadros (abaixo) por cena **antes** de compor.
6. **Composite** com `scripts/motion2d_composite.py windows.json`: para cada janela, `trim` do render (`anim_start` = início da cena no render) deslocado para `a`, `overlay` com `enable=between(t,a,b)`; áudio copiado do master. Saída em CRF 14 como master intermediário.
7. **Som.** Áudio da voz intacto; SFX em faixa separada, cada um ancorado numa palavra/evento (whoosh na entrada/saída de janela, pop em elemento que aparece, golpe em número, ding em confirmação). Use o fluxo de SFX da skill (banco local → `sfx_earshot.py` para o que faltar → ElevenLabs só se nada servir). Densidade conforme a skill; silêncio também é recurso.
8. **Legendas e ganchos.** Importe o ASR corrigido (`scripts/import_words.py`), destaques pontuais, renderize cada variante (gancho + corpo com animação). A animação não pode colidir com a legenda: palco acima da zona de legenda.
9. **Velocidade.** Entregue **1× e 1,25×** a partir do master 1×, uma só passada: `python scripts/retime_project.py project.json --speed 1.25 --output NOVA_REVISAO --reason "versão 1,25×"` (`atempo`, pitch preservado; aplica o mesmo mapa a fala, legenda, cenas e SFX). Se o projeto ainda não é um `project.json` do motor da skill, acelere o **MP4 final** do 1× uma vez com ffmpeg (`setpts=PTS/1.25` no vídeo, `atempo=1.25` no áudio) e regenere só a legenda dividindo todos os tempos por 1,25. Tempos de uma lista de momentos "em 1×" dividem por 1,25 na versão rápida.
10. **QA** (obrigatório antes de entregar):
    - Por cena, antes do composite: snapshots a cada **0,5 s** em folha de contato (5–6 colunas, tempo rotulado) — `qa.py`-style com `hyperframes snapshot --at …`.
    - No vídeo final de **cada variante e cada velocidade**: `scripts/qa_contact_sheet.py video.mp4 qa/ --step 0.5`. Olhe todas as folhas: texto cortado, sobreposição, rosto coberto, legenda colidindo, quadro vazio, emenda de corte, janela começando fora da palavra.
    - Todas as emendas diferentes de gancho→corpo; início e fim de cada animação; CTA com rosto.
    - Decodificação completa, durações A/V, SRT idêntico às cues, 1,25× ≈ 1× ÷ 1,25 (±1 quadro), áudio sem clique nas emendas. Não alegue "ouvi" se só houve análise técnica.
11. **Entrega.** MP4 por variante×velocidade, SRT, e uma tabela `momentos` (tempo 1×, cena, frase) para o usuário saber onde cada animação cai. Versões antigas: renomear com prefixo "pode apagar -", nunca apagar sozinho. Não publicar.

## Armadilhas já vistas
- Cache de render por nome: invalide quando mudar cena, fonte, fps ou ASR.
- Ids repetidos entre cenas no mesmo HTML quebram animações → namespace por cena.
- Mudar o corte depois de gerar cenas desloca TODAS as janelas: refaça ASR → janelas → áudio por cena → composite.
- Animação 3D/"bonita" que não explica a frase é pior que rosto. Se o feedback for "ruim", reescreva a cena 2D, não adicione efeito.
- Memória baixa: `--workers 1 --low-memory-mode --no-browser-gpu`.
