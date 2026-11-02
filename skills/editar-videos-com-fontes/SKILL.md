---
name: editar-videos-com-fontes
description: >-
  Use this when editing Gabriel's talking-to-camera vertical videos
  (TikTok/Reels, 1080x1920) with natural cuts, alternative hooks, burned-in
  captions, real sources/evidence images, big images, animated demos and sound
  effects; not for generating a presenter or only analyzing a video.
---
## Instalação neste computador

O repositório original (https://github.com/gouveaero/editar-videos-com-fontes) está instalado em `/workspace/skills/editar-videos-com-fontes`. Todos os links relativos abaixo (`scripts/…`, `references/…`, `assets/…`) apontam para essa pasta. Se ela não existir, baixe o tarball de `https://codeload.github.com/gouveaero/editar-videos-com-fontes/tar.gz/HEAD` e extraia lá.

Requisitos: Node 22+, ffmpeg, Chrome, venv com Pillow em `.venv`, HyperFrames 0.8.33 via `npx`. Nesta máquina (pouca RAM livre) o render usa `--workers 1 --low-memory-mode --no-browser-gpu` sem `--gpu` (patch local em `scripts/video_pipeline.py`).

```bash
cd /workspace/skills/editar-videos-com-fontes
source .venv/bin/activate
export PYTHONPATH=scripts
python3 scripts/regression.py --output /workspace/video-tests/benchmark/qa   # teste de regressão
python3 scripts/video_pipeline.py validate|render|verify /caminho/project.json
python3 scripts/editorial_pipeline.py render /caminho/project.json
python3 scripts/import_words.py project.json <componente> whisper.json      # importar legendas do ASR
```

A skill não transcreve sozinha: gere JSON com tempos por palavra via ASR local (faster-whisper) e importe com `import_words.py`.

---

# Editar vídeos com fontes

Entregue fala íntegra, ritmo natural e elementos visuais legíveis no celular. Esta skill inclui a direção visual e os recursos executáveis necessários; não depende de outra skill de design. A referência e as instruções do vídeo atual prevalecem sobre padrões anteriores.

## Escolha o caminho mínimo

- **Edição com acabamento visual:** use [editorial_pipeline.py](scripts/editorial_pipeline.py), que estende o motor estável com enquadramento por tomada, imagens únicas, títulos, conexões, gráficos, demonstrações e sons. Leia [contrato básico](references/projeto.md) e [contrato editorial](references/editorial.md).
- **Montagem simples ou reprodução antiga:** [video_pipeline.py](scripts/video_pipeline.py) mantém o perfil original sem zoom. Os projetos anteriores continuam compatíveis.
- **Só entrega ou melhoria da skill:** preserve os vídeos aprovados. Não renderize de novo por carregar esta skill.
- **Revisão pontual:** altere a menor unidade necessária. Um defeito no corpo compartilhado deve ser corrigido em todas as variantes que o usam; um defeito exclusivo de um gancho não deve modificar os outros.

Antes de editar, localize brutos, roteiro, transcrições, fontes, referência e última versão aprovada. Use uma nova pasta de revisão; mantenha as anteriores. Não imponha sete ganchos, duração fixa, uma profissão, a paleta ou exemplos de um projeto antigo.

## Fala, respiração e relógio único

Transcreva o **áudio realmente editado**, com tempos por palavra, e preserve o JSON original. Não invente falas ou sintetize uma abertura ausente. Registre origem, entrada, saída, número de quadros e motivo dos cortes.

Na junção gancho → corpo, confira o final da última palavra, a inspiração e o início real da primeira consoante. **Uma pausa curta ainda pode conter uma respiração audível.** O tempo de palavra do ASR e um limiar de silêncio são pistas, não o ponto de corte definitivo. Use [inspect_audio.py](scripts/inspect_audio.py) para gerar trecho de escuta, forma de onda e espectrograma. Confirme a frase depois do corte; não alegue audição integral quando só houve análise técnica. Veja [cortes e som](references/audio-e-tempo.md).

Corte logo antes da fala com pequena margem que preserve a consoante inicial; não copie os 16 quadros usados em outra gravação. Um fade curto evita clique, mas não substitui retirar a inspiração. Preserve pausas expressivas e as ressalvas do argumento.

Mantenha **um relógio por componente final** para fala, legendas, imagens, estados das demonstrações, música e SFX. Para cortar o início ou mudar a velocidade, use [retime_project.py](scripts/retime_project.py): ele cria outra revisão e aplica o mesmo mapa a todas essas posições. Tempos relativos dos estados também mudam. Não misture tempos de bruto, 1× e saída final. Velocidade padrão 1×; 1,1× somente quando solicitado, com pitch preservado; **1,25×** quando pedido ou na entrega dupla 1× + 1,25× de motion 2D (nunca 1,3× por padrão). Nunca acelere duas vezes um master já acelerado.

## Direção visual incorporada

Leia [direção visual](references/direcao-visual.md) quando compuser ou revisar elementos. Use o rosto como presença principal e o material de apoio para tornar uma ideia concreta.

- Meça o enquadramento de **cada tomada**, inclusive início, meio, fim e movimento mais próximo. Aproximar o rosto e remover teto indesejado é permitido. Configure escala/origem; confira cabelo, barba e fundo depois do zoom. Igualar a sensação de proximidade pode exigir escalas diferentes em brutos diferentes.
- Mostre primeiro o apresentador iniciando a ideia; introduza a imagem na palavra pertinente. Evite um flash do rosto seguido imediatamente por uma tela cheia após o gancho.
- Para obras e fotos de destaque, prefira **uma imagem grande por vez**, proporcional. Não duplique miniatura e detalhe nem encaixe duas imagens ilegíveis para preencher espaço. Capturas de publicações podem usar um recorte focado sobre a câmera ou tela inteira conforme a legibilidade.
- Títulos de ênfase ficam no espaço livre acima do rosto quando ele existe. Se o zoom ocupou esse espaço, reposicione; nunca deixe o texto atravessar cabelo, olhos ou barba. Confira novamente as legendas depois de reenquadrar.
- Hierarquia clara, tipografia local, poucos níveis de texto, espaço generoso e contraste. Uma mudança de estado deve explicar uma ação. Evite cartões decorativos repetidos, rótulos minúsculos e movimento sem função.

Os recursos em `assets/editorial/` incluem CSS, Newsreader, Source Sans 3, licenças e modelos funcionais de navegação, pêndulo e cronologia com documentos. São pontos de partida configuráveis, não conteúdo para inserir automaticamente. Teste ações e dados; identifique dados fictícios como **Exemplo ilustrativo**. Animação HTML criada localmente não deve ser chamada de captura real de um site. Não prometa funcionamento de um botão só porque ele foi desenhado.

## Fontes reais e legendas

Escolha a passagem que sustenta exatamente a fala e registre alegação/relação, URL e crédito. Preserve qualificações, hipótese e resposta pertinente. Capture a publicação real; não redesenhe uma manchete ou parágrafo como se fosse original. [prepare_evidence.py](scripts/prepare_evidence.py) e [manifesto de evidências](references/evidencias.md) preservam fonte, recorte e marcação. Se o navegador estiver indisponível, use um documento oficial real quando adequado e identifique-o corretamente.

Legenda branca, contorno escuro, até duas linhas, sem caixa, distante da barba. Destaque pontual, não a frase inteira. Use a lista de cues tanto no MP4 quanto no SRT. Saída de referência: 1080×1920/30; margens de texto de 250 px no topo e base. Veja [perfil de Gabriel](references/perfil-gabriel.md) para distinguir preferências de valores específicos de um vídeo.

## Motion 2D sobre a fala (animações sincronizadas ao vídeo gravado)

Quando o pedido é "animações/motion explicando o que eu falo", siga [motion 2D](references/motion-2d.md): cortes de pausas e resets a partir do ASR, master 1× do corpo, janelas de animação por ideia ancoradas na palavra falada, rosto na abertura e no CTA, alternância rosto ↔ animação (rosto ≤ ~3 s seguidos, animação ~2,5–8 s), legenda queimada sincronizada, entrega em 1× e 1,25× e QA de quadros a cada 0,5 s. As cenas usam o motor HTML+GSAP da skill `animacao-explicativa`. Scripts: [motion2d_composite.py](scripts/motion2d_composite.py) (`windows.json`, `--check` valida janelas e limites, compõe as janelas sobre o rosto mantendo o áudio original) e [qa_contact_sheet.py](scripts/qa_contact_sheet.py) (folhas de contato a cada N s com tempo rotulado). Testados só em vídeo sintético; confira a primeira entrega real.

## Som e verificação

Use efeitos correspondentes às ações: clique na seleção, chave no controle, transição discreta na troca, confirmação no resultado. Não sonorize cada palavra. Escolha sons locais autorizados, registre origem/licença conhecida, recorte o ataque e mantenha-os abaixo da voz. O motor gera faixas separadas e permite reduzir a música em intervalos relevantes; veja [cortes e som](references/audio-e-tempo.md). Música e SFX são opcionais; não adicione ruído para preencher silêncio. Ordem para um som que falta: banco local da skill `animacao-explicativa` (`assets/sfx`, 17 itens `gen_earshot_*` incluídos) → **earshot** com [sfx_earshot.py](scripts/sfx_earshot.py) (gera sem créditos e sem perguntar: duração/apex/nota exatos, true peak ≤ −1 dBTP; ver [sfx_earshot.md](references/sfx_earshot.md)) → ElevenLabs só para textura real (foley, humano, aplauso, ambiente). O earshot é complementar e foi avaliado só por medições, não por audição.

Faça uma primeira revisão visual em lote, corrija os problemas encontrados e confirme os quadros afetados. Antes do lote final, confira uma versão principal, **todas as emendas diferentes** e os estados das demonstrações. Um corpo igual permite reaproveitar a revisão do corpo, não presumir que todos os ganchos estão bons.

Mudança no motor/estilo exige [testes e limites](references/validacao.md): invariantes, regressão antiga e checks editoriais quando afetados. Verifique decodificação completa, quadros, A/V, áudio, SRT e equivalência do corpo. Cache inclui código, fontes, mídia, enquadramento e eventos; não reaproveite um render só pelo nome.

[package_project.py](scripts/package_project.py) cria galeria e ZIP com MP4, SRT, legenda de publicação, fontes e composições. Projetos editoriais incluem motor, fontes locais, demonstrações, documentos e sons para reconstrução independente. Inspecione o pacote extraído; preserve também o plano e a revisão efetivamente feita. O registro editorial é documentação do trabalho, não um pedido de aprovação. Não publique em redes como consequência da entrega.
