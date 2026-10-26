"""Diagrama da arquitetura do servidor de geração 3D de 2026, em formato vertical para o relatório.

Gera figuras/srv_arquitetura_2026_vertical.png (matplotlib).
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.environ.get('CERISE_FIGURAS', os.path.join(RAIZ, 'figuras')).replace('\\', '/').rstrip('/') + '/'

FS = 9
fig = plt.figure(figsize=(5.9, 5.9 * 0.94), dpi=220)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 94); ax.axis('off')


def box(x, y, w, h, title, body='', fc='#EAF1F8', ec='#5B7A99', ls='-', fs=FS):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.5', fc=fc, ec=ec, lw=1, ls=ls))
    if body:
        ax.text(x + w / 2, y + h - 1.8, title, ha='center', va='top', fontsize=fs, fontweight='bold')
        ax.text(x + w / 2, y + h - 5.6, body, ha='center', va='top', fontsize=fs - 0.5, linespacing=1.2)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha='center', va='center', fontsize=fs, linespacing=1.2)


def arrow(x0, y0, x1, y1, label='', dx=2.5, ha='left', style='-|>'):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=10, lw=1, color='#444444'))
    if label:
        ax.text((x0 + x1) / 2 + dx, (y0 + y1) / 2, label, ha=ha, va='center', fontsize=FS - 1, color='#333333', linespacing=1.1)


box(2, 84, 30, 8.5, 'Aplicativo CERISE AR\n2026 (Android e iOS)')
box(35, 84, 30, 8.5, 'Aplicativo Android\nde 2025 (rota legada)')
box(68, 84, 30, 8.5, 'Testes no Windows\ne no emulador')
box(8, 70.5, 84, 7.5, 'Acesso apenas pela rede interna, por túnel SSH local;\nexposição pública pendente de decisão', fc='#FFF8E6', ec='#B8860B', ls='--')
arrow(17, 83.4, 30, 78.7); arrow(50, 83.4, 50, 78.7); arrow(83, 83.4, 70, 78.7)
ax.add_patch(FancyBboxPatch((1, 1), 98, 65.5, boxstyle='round,pad=0.4,rounding_size=2', fc='none', ec='#2A9D8F', lw=1.2))
ax.text(50, 3.0, 'Estação NVIDIA DGX Spark (GB10), compartilhada com os serviços de IA em produção',
        ha='center', va='center', fontsize=FS - 1, color='#1F6F66')
box(12, 46, 76, 16.5, 'API assíncrona (FastAPI)',
    'validação e normalização da foto; resposta 202 em milissegundos\nlimites de fila (429), por cliente e de taxa\ncache por hash SHA-256 e coalescência de pedidos iguais\nretenção máxima de 7 dias; rota legada de 2025', fc='#E8F6F3', ec='#5E8C85')
arrow(50, 69.8, 50, 63.2, 'HTTP /api/v1')
box(3, 26.5, 44, 13, 'Fila persistente (SQLite, WAL)',
    'jobs, estado e progresso; reserva atômica\nFIFO com prioridade por preset\ne envelhecimento', fc='#F3F3F3', ec='#777777')
box(53, 26.5, 44, 13, 'Volume de arquivos',
    'foto de entrada (apagada após\na geração), GLB e miniatura', fc='#F3F3F3', ec='#777777')
arrow(30, 45.4, 25, 40.2, 'registra o job', dx=-2.5, ha='right')
arrow(70, 45.4, 75, 40.2, 'grava a foto, lê o GLB')
box(12, 7, 76, 13.5, 'Processo de GPU (sem rede)',
    'Hunyuan3D-2 Turbo carregado uma única vez\n1 job por vez (produção) ou 2 slots com travas por componente\ntempo limite, retomada após reinício e guarda de memória', fc='#E8F6F3', ec='#5E8C85')
arrow(25, 25.9, 30, 21.2, 'reserva o job,\natualiza o estado', dx=-3.5, ha='right', style='<|-|>')
arrow(75, 25.9, 70, 21.2, 'lê a foto,\ngrava o GLB', dx=3.5, style='<|-|>')
fig.savefig(OUT + 'srv_arquitetura_2026_vertical.png', dpi=220, facecolor='white')
print('ok')
