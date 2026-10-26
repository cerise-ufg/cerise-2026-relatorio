"""Gráfico da Atividade 1 (qualidade em função do tempo mediano por objeto) com rótulos em português.

Lê a tabela de resultados medidos da frente de geração 3D (resultados/a1_tabela.csv, copiada em
figuras/frentes/REALIDADE AUMENTADA/GERACAO_3D/resultados/) e gera figuras/a1_qualidade_vs_tempo_pt.png.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
F = os.environ.get('CERISE_FRENTES', os.path.join(RAIZ, 'figuras', 'frentes')).replace('\\', '/').rstrip('/') + '/'
OUT = os.environ.get('CERISE_FIGURAS', os.path.join(RAIZ, 'figuras')).replace('\\', '/').rstrip('/') + '/'

rows = list(csv.DictReader(open(F + 'REALIDADE AUMENTADA/GERACAO_3D/resultados/a1_tabela.csv', encoding='utf-8')))
nome = {'TripoSR': 'TripoSR', 'InstantMesh': 'InstantMesh', 'Hunyuan3D-2mini-Turbo': '2mini-Turbo',
        'Hunyuan3D-2-Turbo': '2-Turbo', 'Hunyuan3D-2.0 (padrão)': '2.0 (padrão)', 'Hunyuan3D-2.1 (PBR)': '2.1 (PBR)'}
cores = {'TripoSR': '#1f77b4', 'InstantMesh': '#d62728', 'Hunyuan3D-2mini-Turbo': '#2ca02c', 'Hunyuan3D-2-Turbo': '#9467bd',
         'Hunyuan3D-2.0 (padrão)': '#ff7f0e', 'Hunyuan3D-2.1 (PBR)': '#8c564b'}
# deslocamentos dos rótulos (pontos) para evitar sobreposição
off_f = {'TripoSR': (6, -10), 'InstantMesh': (6, 4), 'Hunyuan3D-2mini-Turbo': (-8, -12), 'Hunyuan3D-2-Turbo': (-10, 6),
         'Hunyuan3D-2.0 (padrão)': (-20, -12), 'Hunyuan3D-2.1 (PBR)': (-30, 6)}
off_c = {'TripoSR': (6, 4), 'InstantMesh': (6, -10), 'Hunyuan3D-2mini-Turbo': (-40, 5), 'Hunyuan3D-2-Turbo': (-34, 4),
         'Hunyuan3D-2.0 (padrão)': (-34, 4), 'Hunyuan3D-2.1 (PBR)': (-26, -11)}
virg = lambda d: FuncFormatter(lambda v, _: (f'{v:.{d}f}').replace('.', ','))
plt.rcParams.update({'font.size': 8, 'font.family': 'DejaVu Sans'})
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.5), dpi=220)
for ax, col, off, ylab, d in ((axs[0], 'f01', off_f, 'F-score@0,1 (geometria)', 3), (axs[1], 'clip_in', off_c, 'CLIP entrada (aparência)', 2)):
    for r in rows:
        x, y = float(r['t_median']), float(r[col])
        ax.scatter(x, y, s=28, color=cores[r['label']], zorder=3)
        lab = nome[r['label']] + (f" (n={r['n']})" if r['n'] != '13' else '')
        ax.annotate(lab, (x, y), xytext=off[r['label']], textcoords='offset points', fontsize=7)
    ax.set_xscale('log'); ax.set_xlim(0.5, 600)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'.replace('.', ',')))
    ax.yaxis.set_major_formatter(virg(d))
    ax.set_xlabel('tempo mediano por objeto (s, escala log)'); ax.set_ylabel(ylab)
    ax.grid(alpha=0.3); ax.spines[['top', 'right']].set_visible(False)
axs[0].set_ylim(0.958, 0.998); axs[1].set_ylim(0.835, 0.94)
fig.tight_layout()
fig.savefig(OUT + 'a1_qualidade_vs_tempo_pt.png', facecolor='white')
for r in rows: print(r['label'], r['n'], round(float(r['t_median']), 1), round(float(r['f01']), 3), round(float(r['clip_in']), 3))
