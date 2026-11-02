#!/usr/bin/env python3
"""Gerador paramétrico de SFX com o repositório `earshot` (MIT, sintético, sem rede, sem créditos).

Uso:
  sfx_earshot.py setup                       # clona + venv + instala (só numpy/scipy/soundfile/soxr)
  sfx_earshot.py buscar whoosh [--max 30]    # lista ids do banco do earshot
  sfx_earshot.py render ID -o PROJETO/assets/sfx/nome.wav [--dur S] [--apex S] [--pitch E5] [--peak -1] [--weight 1] [--seed N]
  sfx_earshot.py pack DIR                    # gera o pacote padrão de vídeo (whoosh x3, riser, hit, logo sting, pop, ding, glitch, boom)
  sfx_earshot.py check ARQUIVO.wav ...       # auditoria sem modelo (cliques, clipping, DC, cauda, true peak)

Depois de renderizar, o arquivo passa por uma trava de true peak (<= -1,0 dBTP): o earshot garante
o pico de AMOSTRA em -1 dBFS, mas alguns sons (ex.: glitch) passam de 0 dBTP ao reconstruir.
Salve em PROJETO/assets/sfx/: a skill dá prioridade a essa pasta sobre o banco.
Variáveis: EARSHOT_HOME (default ~/.cache/earshot), EARSHOT_BIN (caminho do executável).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HOME = Path(os.environ.get('EARSHOT_HOME', Path.home() / '.cache' / 'earshot'))
REPO = 'https://github.com/Leonxlnx/earshot'   # NÃO existe "earshot" no PyPI com este conteúdo: instale do git
PACK = {   # nome: (id, flags)  — pacote padrão de vídeo
    'whoosh_rapido': ('whoosh_fast/crisp', ['--dur', '0.6', '--apex', '0.3']),
    'whoosh_grande': ('whoosh_big/thump', []),
    'whoosh_swipe': ('swipe/cloth', ['--dur', '0.5']),
    'riser_build': ('riser/build', []),
    'riser_escuro': ('riser/dark', []),
    'hit_corte': ('cut_hit/sub', []),
    'hit_impacto': ('pro_impact/short', []),
    'logo_sting': ('logo_sting/soft_bloom', []),
    'logo_sting_zap': ('pro_logo_sting/zap_bloom', []),
    'pop_ui': ('ui_pop/soft', []),
    'pop_pro': ('pro_pop/boop', []),
    'ding_sucesso': ('notify/mid_tine', []),
    'ding_pro': ('pro_notify/ding_2045', []),
    'glitch_burst': ('glitch/burst', []),
    'glitch_pro': ('pro_glitch/standard', []),
    'boom_sub': ('sub_drop/808', []),
    'boom_impacto': ('impact/deep', []),
}

def binpath():
    b = os.environ.get('EARSHOT_BIN')
    for c in [b, str(HOME / 'repo/.venv/bin/earshot'), '/workspace/earshot/.venv/bin/earshot', shutil.which('earshot')]:
        if c and Path(c).exists():
            return c
    sys.exit('earshot não instalado: rode `sfx_earshot.py setup`')

def run(cmd, **k):
    return subprocess.run(cmd, check=True, **k)

def setup():
    HOME.mkdir(parents=True, exist_ok=True)
    repo = HOME / 'repo'
    if not repo.exists():
        run(['git', 'clone', '--depth', '1', REPO, str(repo)])
    venv = repo / '.venv'
    if not venv.exists():
        run([sys.executable, '-m', 'venv', str(venv)])
    pip = str(venv / 'bin/pip')
    # o núcleo de SFX só precisa disto; torch/CLAP (≈1,1 GB) só servem para describe/match/critique/forge-search
    run([pip, 'install', '-q', 'numpy', 'scipy', 'soundfile', 'soxr'])
    run([pip, 'install', '-q', '--no-deps', str(repo)])
    print('ok:', venv / 'bin/earshot')

def truepeak(path):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    m = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    return float(m[-1]) if m else None

def limitar_tp(path, alvo=-1.0):
    """Reduz o ganho (sem limiter, preserva a forma) até o true peak ficar <= alvo."""
    tp = truepeak(path)
    if tp is None or tp <= alvo:
        return tp
    g = alvo - tp - 0.05
    tmp = Path(str(path) + '.tmp.wav')
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(path), '-af', f'volume={g}dB', '-c:a', 'pcm_s24le', str(tmp)])
    tmp.replace(path)
    return truepeak(path)

def render(sid, out, dur=None, apex=None, pitch=None, peak=None, weight=None, seed=None):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [binpath(), 'sfx', 'render', sid, '-o', str(out)]
    for f, v in [('--dur', dur), ('--apex', apex), ('--pitch', pitch), ('--peak', peak), ('--weight', weight), ('--seed', seed)]:
        if v is not None:
            cmd += [f, str(v)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-800:])
    tp = limitar_tp(out)
    info = {'id': sid, 'file': str(out), 'dur_s': dur, 'apex_s': apex, 'pitch': pitch, 'true_peak_dbtp': tp, 'seed': seed}
    print(json.dumps(info, ensure_ascii=False))
    return info

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('setup')
    b = sp.add_parser('buscar'); b.add_argument('termo', nargs='?', default=''); b.add_argument('--max', type=int, default=40)
    r = sp.add_parser('render'); r.add_argument('id'); r.add_argument('-o', '--out', required=True)
    for f in ('dur', 'apex', 'peak', 'weight'):
        r.add_argument('--' + f, type=float)
    r.add_argument('--pitch'); r.add_argument('--seed', type=int)
    p = sp.add_parser('pack'); p.add_argument('dir')
    c = sp.add_parser('check'); c.add_argument('arquivos', nargs='+')
    a = ap.parse_args()
    if a.cmd == 'setup':
        setup()
    elif a.cmd == 'buscar':
        out = subprocess.run([binpath(), 'sfx', 'list'], capture_output=True, text=True).stdout.splitlines()
        hit = [l for l in out if a.termo.lower() in l.lower()]
        print('\n'.join(hit[:a.max])); print(f'({len(hit)} de {len(out)} linhas)')
    elif a.cmd == 'render':
        render(a.id, a.out, a.dur, a.apex, a.pitch, a.peak, a.weight, a.seed)
    elif a.cmd == 'pack':
        d = Path(a.dir); idx = {}
        for nome, (sid, fl) in PACK.items():
            kw = {fl[i][2:]: fl[i + 1] for i in range(0, len(fl), 2)}
            idx[nome] = render(sid, d / f'{nome}.wav', **{k: float(v) for k, v in kw.items()})
        (d / 'INDEX.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1))
    elif a.cmd == 'check':
        for f in a.arquivos:
            subprocess.run([binpath(), 'sfx', 'check', f])
            print(f, 'true peak', truepeak(f), 'dBTP')

if __name__ == '__main__':
    main()
