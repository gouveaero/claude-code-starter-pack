# SFX paramétricos com `earshot` (complemento ao banco e ao ElevenLabs)

Repositório: https://github.com/Leonxlnx/earshot (MIT, v0.4.0 testada em 23/10/2026). **Não é o pacote "earshot" do PyPI**: instale do git. Sons **sintéticos gerados por código** (252 receitas), 24-bit, sem rede, sem créditos, determinísticos.

## Veredito (medido, não ouvido)
**Complementar, não substituto.**
- Usar para o que o banco não cobre com precisão: duração exata, apex/pico em segundo definido, nota (pitch) definida, nível definido, variação por seed, sem custo de créditos e com licença limpa (MIT). Ordem de preferência para um som que falta: (1) banco local → (2) **earshot** → (3) ElevenLabs (só se precisar de textura real: foley, voz/humano, aplauso, ambiente, impacto fotográfico).
- O banco continua melhor para o que é gravado: foley, humano, aplauso, ambiente, cartoon, drums. O earshot só faz UI/movimento sintético (whoosh, riser, hit, sting, pop, ding, glitch, boom, plucks).
- Limites declarados pelo próprio projeto (docs/LIMITS.md): não julga gosto; a busca "listening" pode sobreajustar seus modelos; o teste cego da v1 deu 8/15 (cara ou coroa, 1 ouvinte). Nada aqui prova que "soa melhor": prove escutando o 1º vídeo.

## Instalar (uma vez; ~30 s, sem torch)
```bash
python3 scripts/sfx_earshot.py setup      # clona em ~/.cache/earshot/repo, venv, pip numpy scipy soundfile soxr, pip install --no-deps .
```
Só o núcleo `sfx` é usado. `describe/match/critique/forge search` exigem torch + ~1,1 GB de modelos CLAP/AST: **não instale**.

## Usar
```bash
python3 scripts/sfx_earshot.py buscar whoosh                       # ids disponíveis (cat/receita)
python3 scripts/sfx_earshot.py render whoosh_fast/crisp --dur 0.6 --apex 0.3 -o PROJETO/assets/sfx/whoosh_corte.wav
python3 scripts/sfx_earshot.py render pro_notify/ding_2045 --pitch E5 -o PROJETO/assets/sfx/ding_ok.wav
python3 scripts/sfx_earshot.py pack PROJETO/assets/sfx/earshot      # pacote padrão (17 sons) + INDEX.json
python3 scripts/sfx_earshot.py check arquivo.wav                    # auditoria sem modelo
```
- Salve em `PROJETO/assets/sfx/<nome>.wav`: tem prioridade sobre o banco. Referencie por `data-sfx="nome"`.
- Som que vai servir de novo: copie para `assets/sfx/<NN_categoria>/gen_earshot_<nome>.wav` e registre no `manifest.json` (`source.kind: "earshot"`, `source.id`, `hit_ms` = instante do pico) e em `index/<pasta>.md`. O pacote padrão já está lá (17 itens `gen_earshot_*`).
- O helper aplica trava de **true peak ≤ −1 dBTP**: o earshot garante pico de amostra −1 dBFS, mas `pro_glitch/standard` chegou a +0,2 dBTP.
- Mixagem por `nivel` em LUFS continua igual (`pos.py`); a faixa do earshot não é normalizada em loudness (momentâneo máx. típico −10 a −20 LUFS no arquivo, o `nivel` do gatilho define o resultado).

## O que cada botão controla de fato (testes de 23/10/2026)
| botão | resultado medido |
|---|---|
| `--dur` | comprimento do arquivo **exato** em todas as receitas testadas (0,5–3 s). O pico acompanha o `dur` em `riser/tension`, `pro_riser/roll` (pico ≈ 97–99 % do comprimento) e `glitch/burst` (pico ≈ 35–47 %); em `riser/build` o pico fica em 41–81 % (não no fim); em `sub_drop`, `logo_sting` e `downlifter` o golpe é fixo no início (~0,06–0,15 s) e `dur` só alonga a cauda |
| `--apex` (só família whoosh/swipe/swish) | pico de energia no tempo pedido: erro típico ≤ 10 ms (0,1→0,095…0,6→0,595); piores casos 0,32→0,34 e 0,6→0,65 em `whoosh_big/thump` |
| `--pitch` (receitas afinadas: ding, notify, pluck, sub_drop) | dentro de ±5 cents; **recusa** nota fora da faixa da receita (ex.: C5 em `pro_notify/ding_2045`, faixa 600–3200 Hz). `pop/0` **não** é afinado (erro de 200–350 cents) |
| `--seed` | variação pequena do mesmo timbre (diferença média por banda ~0,7–2,9 dB entre seeds): serve para não repetir cliques idênticos, **não** para mudar caráter. O caráter vem do **id** |
| `--peak/--weight` | nível de pico de amostra exato (padrão −1 dBFS; 6 dB por dobro) |
| determinismo | mesma seed → mesmo hash do áudio |
| tempo | ~2 s por render em processo; ~3,3 s pelo CLI (partida a frio); 5–14 s quando `dur/apex` fazem re-sorteio |

## Alinhamento
Pico (golpe) ≠ início do arquivo em riser/hit/whoosh (pré-swell): use o instante do pico como `hit_ms`. Exemplos medidos: `riser/build` pico a 1,20 s de 1,76 s; `pro_impact/short` 0,18 s; `whoosh_fast/crisp --dur 0.6 --apex 0.3` 0,285 s; `pop`/`ding` ≈ 0–40 ms.

## O que NÃO foi verificado
Qualidade subjetiva (ninguém ouviu), encaixe no mix com voz real, comparação cega com o banco, e os modelos de escuta (`describe/match/critique`).
