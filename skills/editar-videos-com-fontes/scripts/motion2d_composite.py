#!/usr/bin/env python3
"""Compõe animações 2D (um render único, já na ordem das cenas) sobre o master com o rosto.

windows.json:
{
  "face": "masters/corpo_face_only.mp4",     # áudio original, rosto, sem animação (relógio único do corpo)
  "anim": "anim/build/final/render.mp4",     # render das cenas, uma atrás da outra
  "out":  "masters/corpo_anim.mp4",
  "fps": 30, "crf": 14,
  "limits": {"max_face_gap": 3.0, "max_anim": 8.0, "min_anim": 1.2},
  "scenes": [ {"id": "cena_01", "a": 0.00, "b": 4.50, "anim_start": 0.00}, ... ]
}
a/b = tempo no master do corpo (s). anim_start = onde a cena começa dentro do render de animação
(campo `inicio` do linha.json da skill animacao-explicativa). A duração é b-a.

Uso:  motion2d_composite.py windows.json --check     # só valida (sem renderizar)
      motion2d_composite.py windows.json             # valida e renderiza
O áudio sai do master (-c:a copy): a animação nunca troca a voz.
"""
import json, subprocess, sys
from pathlib import Path

def check(cfg, dur_face=None):
    L = cfg.get('limits', {}); mf = L.get('max_face_gap', 3.0); ma = L.get('max_anim', 8.0); mi = L.get('min_anim', 1.2)
    S = cfg['scenes']; bad = []; prev = 0.0
    for s in S:
        d = s['b'] - s['a']
        if s['a'] < prev - 1e-6: bad.append(f"{s['id']}: sobrepõe a anterior ({s['a']:.2f} < {prev:.2f})")
        if d > ma: bad.append(f"{s['id']}: animação longa demais ({d:.2f}s > {ma}s)")
        if d < mi: bad.append(f"{s['id']}: animação curta demais ({d:.2f}s < {mi}s)")
        if s['a'] - prev > mf: bad.append(f"rosto sozinho por {s['a']-prev:.2f}s antes de {s['id']} (limite {mf}s)")
        prev = s['b']
    if dur_face and dur_face - prev > mf + 3.0:
        bad.append(f"final do corpo sem animação por {dur_face-prev:.2f}s (ok se for o CTA com rosto)")
    return bad

def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__ + '\nUso: motion2d_composite.py windows.json [--check]'); return
    cfg = json.load(open(sys.argv[1])); base = Path(sys.argv[1]).parent
    f = str(base / cfg['face']); r = str(base / cfg['anim']); out = str(base / cfg['out'])
    bad = check(cfg, probe(f))
    for b in bad: print('AVISO:', b)
    if '--check' in sys.argv: sys.exit(1 if bad else 0)
    inp = ['-i', f]; fc = []; last = '0:v'
    for i, s in enumerate(cfg['scenes']):
        a, b, st = s['a'], s['b'], s.get('anim_start', 0.0); d = b - a
        inp += ['-i', r]
        fc.append(f"[{i+1}:v]trim=start={st:.3f}:end={st+d:.3f},setpts=PTS-STARTPTS+{a:.3f}/TB[s{i}]")
        fc.append(f"[{last}][s{i}]overlay=enable='between(t,{a:.3f},{b:.3f})':eof_action=pass[o{i}]"); last = f'o{i}'
    cmd = ['ffmpeg', '-y', '-v', 'error'] + inp + ['-filter_complex', ';'.join(fc), '-map', f'[{last}]', '-map', '0:a',
           '-c:v', 'libx264', '-crf', str(cfg.get('crf', 14)), '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(cfg.get('fps', 30)), '-c:a', 'copy', out]
    subprocess.run(cmd, check=True); print('ok', out, round(probe(out), 3), 's')

if __name__ == '__main__':
    main()
