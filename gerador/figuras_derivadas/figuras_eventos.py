"""Monta as figuras de produção científica e do CERISE Summit 2026 para o relatório:
- mosaico de 6 fotos do Summit com rótulos (a)-(f);
- certificados lado a lado;
- primeira página dos dois artigos lado a lado;
- banner (pôster) do CBA 2026 reduzido.

Entradas: anexos/ (PDFs dos artigos, do pôster e dos certificados) e figuras/producao_eventos/summit2026_foto*.jpg.
Saída: figuras/producao_eventos/. Depende de Pillow e PyMuPDF (fitz) e da fonte Arial Negrito do Windows.
"""
import os

import fitz
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ent = os.path.join(RAIZ, 'anexos')
dst = os.path.join(os.environ.get('CERISE_FIGURAS', os.path.join(RAIZ, 'figuras')), 'producao_eventos')
PDF = {'cert_expositor': 'Certificado_Expositor_CERISE_SUMMIT_2026.pdf',
       'cert_monitor_summit2026': 'Certificado_Monitor_CERISE_SUMMIT_2026.pdf',
       'artigo_meder2026': 'Artigo_MEDER_2026.pdf', 'artigo_cba2026': 'Artigo_CBA_2026.pdf',
       'poster_cba2026': 'Poster_CBA_2026.pdf'}
font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 34)


def label(im, txt):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 64, 50], fill=(255, 255, 255))
    d.text((10, 6), txt, fill=(0, 0, 0), font=font)
    return im


def grid(images, cols, cell_w, gap=12, bg=(255, 255, 255)):
    cells = []
    for im in images:
        im = im.copy()
        im.thumbnail((cell_w, 10_000))
        cells.append(im)
    rows = (len(cells) + cols - 1) // cols
    row_h = [max(c.height for c in cells[r * cols:(r + 1) * cols]) for r in range(rows)]
    W = cols * cell_w + (cols - 1) * gap
    H = sum(row_h) + (rows - 1) * gap
    out = Image.new('RGB', (W, H), bg)
    y = 0
    for r in range(rows):
        x = 0
        for c in cells[r * cols:(r + 1) * cols]:
            out.paste(c, (x + (cell_w - c.width) // 2, y))
            x += cell_w + gap
        y += row_h[r] + gap
    return out


# 1) mosaico do Summit: fotos 1, 3, 4, 5, 7 e a foto do grupo (6)
sel = [1, 3, 4, 5, 7, 6]
fotos = [Image.open(os.path.join(dst, f'summit2026_foto{i}.jpg')).convert('RGB') for i in sel]
fotos = [label(f.resize((800, int(800 * f.height / f.width))), f'({chr(97 + k)})') for k, f in enumerate(fotos)]
m = grid(fotos, 3, 800)
m.save(os.path.join(dst, 'fig_summit2026_mosaico.jpg'), quality=88)
print('mosaico', m.size)


def render(nome, width_px):
    d = fitz.open(os.path.join(ent, PDF[nome]))
    r = d[0].rect
    z = width_px / r.width
    pix = d[0].get_pixmap(matrix=fitz.Matrix(z, z))
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


# 2) certificados lado a lado
c1 = render('cert_expositor', 1400)
c2 = render('cert_monitor_summit2026', 1400)
for im in (c1, c2):
    ImageDraw.Draw(im).rectangle([0, 0, im.width - 1, im.height - 1], outline=(150, 150, 150), width=3)
cert = grid([label(c1, '(a)'), label(c2, '(b)')], 2, 1400, gap=30)
cert.save(os.path.join(dst, 'fig_certificados_summit2026.png'))
print('certificados', cert.size)

# 3) primeira página dos artigos lado a lado
a1 = render('artigo_meder2026', 1100)
a2 = render('artigo_cba2026', 1100)
for im in (a1, a2):
    ImageDraw.Draw(im).rectangle([0, 0, im.width - 1, im.height - 1], outline=(150, 150, 150), width=3)
art = grid([label(a1, '(a)'), label(a2, '(b)')], 2, 1100, gap=30)
art.save(os.path.join(dst, 'fig_artigos_primeira_pagina.png'))
print('artigos', art.size)

# 4) banner
p = render('poster_cba2026', 1300)
p.save(os.path.join(dst, 'fig_banner_cba2026.jpg'), quality=90)
print('banner', p.size)
