"""Copia as fotos do CERISE Summit 2026 com nomes simples, corrigindo a orientação EXIF.

Uso: python fotos_summit.py PASTA_COM_AS_FOTOS_ORIGINAIS

As fotos originais (JPEG, em ordem alfabética de nome) não estão no repositório; as versões já corrigidas
estão em figuras/producao_eventos/summit2026_foto1..7.jpg e em anexos/fotos_cerise_summit_2026/.
"""
import glob
import os
import sys

from PIL import Image, ImageOps

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
src = sys.argv[1]
dst = os.path.join(os.environ.get('CERISE_FIGURAS', os.path.join(RAIZ, 'figuras')), 'producao_eventos')
os.makedirs(dst, exist_ok=True)

fotos = sorted(glob.glob(os.path.join(src, '*.jpeg')) + glob.glob(os.path.join(src, '*.jpg')))
for i, f in enumerate(fotos, 1):
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    out = os.path.join(dst, f'summit2026_foto{i}.jpg')
    im.save(out, quality=90)
    print(out, im.size)
