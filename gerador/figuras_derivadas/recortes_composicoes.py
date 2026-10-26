"""Recortes e composições de figuras das frentes usadas no relatório (sem alterar os dados).

Gera em figuras/: a4_viewer_renders.png, fig_formato_quadro_recorte.png, amostras_perturbacoes_2x4.png,
curvas_treino_2x2.png e a12i_piores_quadros_grade.png.

Entradas: figuras/frentes/ (cópia das evidências das frentes) ou a pasta indicada em CERISE_FRENTES.
"""
import os

from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
F = os.environ.get('CERISE_FRENTES', os.path.join(RAIZ, 'figuras', 'frentes')).replace('\\', '/').rstrip('/') + '/'
OUT = os.environ.get('CERISE_FIGURAS', os.path.join(RAIZ, 'figuras')).replace('\\', '/').rstrip('/') + '/'
WHITE = (255, 255, 255)


def compose(rows, gap=20, bg=WHITE):
    rw = [sum(im.width for im in r) + gap * (len(r) - 1) for r in rows]
    rh = [max(im.height for im in r) for r in rows]
    W = max(rw); H = sum(rh) + gap * (len(rows) - 1)
    canvas = Image.new('RGB', (W, H), bg)
    y = 0
    for r, w, h in zip(rows, rw, rh):
        x = (W - w) // 2
        for im in r:
            canvas.paste(im, (x, y + (h - im.height) // 2))
            x += im.width + gap
        y += h + gap
    return canvas


# 1) a4_viewer: só as quatro vistas renderizadas, em linha
im = Image.open(F + 'REALIDADE AUMENTADA/GERACAO_3D/evidencias/a4_viewer_model_viewer.png').convert('RGB')
boxes = [(16, 16, 417, 416), (664, 16, 1065, 416), (16, 443, 417, 843), (664, 443, 1065, 843)]
compose([[im.crop(b) for b in boxes]], gap=12, bg=(252, 252, 250)).save(OUT + 'a4_viewer_renders.png')

# 2) formato do quadro sem a tabela de tempo no ar
im = Image.open(F + 'NAVEGACAO AUTONOMA/LORA/evidencias/fig_formato_quadro.png').convert('RGB')
im.crop((130, 30, 1795, 795)).save(OUT + 'fig_formato_quadro_recorte.png')

# 3) perturbações em 2 linhas de 4
im = Image.open(F + 'ROBOTICA/POSE_SERVO6DOF/evidencias/amostras_perturbacoes.png').convert('RGB')
compose([[im.crop((0, 0, 1050, 315))], [im.crop((1050, 0, 2100, 315))]], gap=6).save(OUT + 'amostras_perturbacoes_2x4.png')

# 4) curvas de treino em 2x2 (sem o título interno)
im = Image.open(F + 'ROBOTICA/POSE_SERVO6DOF/evidencias/curvas_treino.png').convert('RGB')
cuts = [0, 514, 1008, 1473, 1950]
p = [im.crop((cuts[i], 45, cuts[i + 1], 450)) for i in range(4)]
compose([[p[0], p[1]], [p[2], p[3]]], gap=10).save(OUT + 'curvas_treino_2x2.png')

# 5) piores quadros em 3 + 2 (sem o título interno)
im = Image.open(F + 'ROBOTICA/SERVO6DOF_GEMEO/evidencias/a12i_piores_quadros.png').convert('RGB')
cuts = [0, 504, 995, 1486, 1977, 2475]
p = [im.crop((cuts[i], 70, cuts[i + 1], 640)) for i in range(5)]
compose([[p[0], p[1], p[2]], [p[3], p[4]]], gap=10).save(OUT + 'a12i_piores_quadros_grade.png')
for n in ('a4_viewer_renders', 'fig_formato_quadro_recorte', 'amostras_perturbacoes_2x4', 'curvas_treino_2x2', 'a12i_piores_quadros_grade'):
    print(n, Image.open(OUT + n + '.png').size)
