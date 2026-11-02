# Novo vídeo bruto → MP4 legendado (pipeline básico)

Receita mínima para um talking-head novo (telefone, pausas, qualquer FPS/resolução) até um MP4 **1080×1920 / 30 fps** com legendas brancas no estilo da skill. Sem overlays de evidência.

## Pré-requisitos (já no box)

```sh
cd /workspace/skills/editar-videos-com-fontes
source .venv/bin/activate
export PYTHONPATH=scripts
```

- FFmpeg no PATH
- `faster-whisper` no venv (modelo `medium` int8, pré-baixado)
- HyperFrames 0.8.33 via npx (Node ≥ 22)

## 1. Pasta de revisão nova

```sh
REV=/workspace/video-tests/meu-video-$(date +%Y%m%d-%H%M)
mkdir -p "$REV"/{raw,masters,captions,build}
cp /caminho/do/bruto.mp4 "$REV/raw/take.mp4"
```

## 2. Normalizar master (crop 9:16 + 1080×1920/30 + áudio 48 kHz stereo)

Ajuste o filtro `crop` se o bruto não for 9:16. Exemplo centrado:

```sh
# Descubra duração e resolução
ffprobe -v error -show_entries stream=width,height,r_frame_rate -show_entries format=duration -of json "$REV/raw/take.mp4"

# Crop central 9:16 → scale → fps 30; loudnorm; AAC
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$REV/raw/take.mp4")
ffmpeg -y -i "$REV/raw/take.mp4" \
  -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,setsar=1" \
  -af "aresample=48000,highpass=f=65,loudnorm=I=-16:TP=-1.5:LRA=9" \
  -c:v libx264 -preset fast -crf 18 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -t "$DUR" \
  -movflags +faststart \
  "$REV/masters/principal.mp4"

FRAMES=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 "$REV/masters/principal.mp4")
echo "frames=$FRAMES"
```

Se o bruto já for 9:16, troque o `-vf` por `scale=1080:1920:flags=lanczos,fps=30,format=yuv420p,setsar=1` (sem crop).  
**Cortes de respiração / silêncio:** ainda manuais — use `scripts/inspect_audio.py` e edite o master (ou use `cuts` no JSON). Esta receita não remove pausas automaticamente.

## 3. Transcrever (português, word timestamps, VAD)

```sh
python3 scripts/transcribe_local.py \
  "$REV/masters/principal.mp4" \
  -o "$REV/captions/principal.whisper.json" \
  --model medium --compute-type int8 --language pt
```

## 4. `project.json` mínimo (sem evidências)

Salve como `$REV/project.json` (substitua `FRAMES`):

```json
{
  "schema_version": 2,
  "output": "build",
  "components": {
    "principal": {
      "frames": FRAMES,
      "master": "masters/principal.mp4",
      "captions": "captions/principal.json",
      "shift_y": 0,
      "close": false,
      "evidence": []
    }
  },
  "assets": {},
  "variants": [
    {
      "id": "principal",
      "title": "Principal",
      "components": ["principal"]
    }
  ]
}
```

Notas:
- `frames` = número exato de quadros do master a 30 fps.
- `shift_y` entre -500 e 0 (sobe o apresentador). Meça no celular; 0 é seguro no primeiro teste.
- O arquivo `captions/principal.json` **ainda não existe** — o import cria.

## 5. Importar legendas a partir do Whisper JSON

```sh
python3 scripts/import_words.py "$REV/project.json" principal "$REV/captions/principal.whisper.json"
# → cria captions/principal.json (+ .import.json). Revise nomes próprios e números.
```

## 6. Validar → render → verify

```sh
python3 scripts/video_pipeline.py validate "$REV/project.json"
python3 scripts/video_pipeline.py render "$REV/project.json"
python3 scripts/video_pipeline.py verify "$REV/project.json"
```

Entrega:
- `$REV/build/versions/principal.mp4`
- `$REV/build/versions/principal.srt`
- `$REV/build/versions/principal.captions.json`

## 7. (Opcional) extrair frame de checagem

```sh
ffmpeg -y -ss 1.5 -i "$REV/build/versions/principal.mp4" -frames:v 1 "$REV/frame.png"
```

## Atalho: bruto já é master 1080×1920/30

Pule o passo 2, copie o arquivo para `masters/principal.mp4`, conte os frames e siga do passo 3.
