#!/usr/bin/env python3
"""QA de quadros a cada N s (padrão 0,5 s) de um vídeo, em folhas de contato rotuladas.

Uso: qa_contact_sheet.py video.mp4 saida_dir [--step 0.5] [--cols 6] [--per-sheet 36] [--from 0 --to 20]
Gera saida_dir/sheet_XX.png com o tempo (s) sob cada quadro. Olhe CADA folha: texto cortado,
sobreposição, rosto coberto, legenda colidindo com a animação, quadro preto/vazio, emenda.
Requer ffmpeg e Pillow (use o .venv da skill).
"""
import argparse, subprocess, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--step', type=float, default=0.5); ap.add_argument('--cols', type=int, default=6)
ap.add_argument('--per-sheet', type=int, default=36); ap.add_argument('--tw', type=int, default=240)
ap.add_argument('--from', dest='t0', type=float, default=0.0); ap.add_argument('--to', dest='t1', type=float, default=None)
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
tmp = Path(tempfile.mkdtemp())
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.video], capture_output=True, text=True).stdout)
t1 = min(a.t1 or dur, dur)
ts = []; t = a.t0
while t < t1 - 1e-6: ts.append(round(t, 3)); t += a.step
for i, t in enumerate(ts):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', a.video, '-frames:v', '1', '-vf', f'scale={a.tw}:-2', str(tmp / f'f{i:05d}.png')], check=True)
try: fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except Exception: fnt = ImageFont.load_default()
fr = sorted(tmp.glob('f*.png')); im0 = Image.open(fr[0]); tw, th = im0.size
for s in range(0, len(fr), a.per_sheet):
    chunk = fr[s:s + a.per_sheet]; rows = (len(chunk) + a.cols - 1) // a.cols
    sh = Image.new('RGB', (a.cols * (tw + 6) + 6, rows * (th + 22) + 6), (30, 30, 34)); d = ImageDraw.Draw(sh)
    for k, f in enumerate(chunk):
        r, c = divmod(k, a.cols); x = 6 + c * (tw + 6); y = 6 + r * (th + 22)
        sh.paste(Image.open(f).convert('RGB'), (x, y)); d.text((x + 3, y + th + 3), f'{ts[s + k]:.1f}s', fill=(225, 225, 225), font=fnt)
    p = out / f'sheet_{s // a.per_sheet:02d}.png'; sh.save(p); print(p)
shutil.rmtree(tmp)
