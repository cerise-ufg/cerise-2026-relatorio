"""Verificações de consistência do Markdown do relatório antes de gerar o .docx.

Confere títulos (no máximo nível 3), figuras (arquivo existente, largura entre 8 e 16 cm, legenda sem "Figura"),
tabelas com legenda, citações [n] na ordem da primeira ocorrência e todas presentes na lista de referências,
chaves [@...] remanescentes, padrões de texto a evitar e números de 4 ou mais dígitos sem separador de milhar.

Uso: python verificar_relatorio.py [RELATORIO.md] [--repo]
  --repo  resolve os caminhos absolutos E:/CERISE/... das figuras para as cópias deste repositório.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_relatorio import MAPA_REPO, RAIZ_REPO, resolver_caminho  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('md', nargs='?', default=os.path.join(RAIZ_REPO, 'RELATORIO_CERISE_2026.md'))
ap.add_argument('--repo', action='store_true')
a = ap.parse_args()
P = a.md
mapas = [(antigo, os.path.join(RAIZ_REPO, novo)) for antigo, novo in MAPA_REPO] if a.repo else []
base = os.path.dirname(os.path.abspath(P))

t = open(P, encoding='utf-8').read()
lines = t.splitlines()
corpo, refs = t.split('# Referências bibliográficas')
# headings
for ln in lines:
    if ln.startswith('#'):
        lvl = len(ln) - len(ln.lstrip('#'))
        if lvl == 1:
            print('H1', ln)
        if lvl > 3:
            print('NIVEL>3', ln)
print('H2:', sum(1 for l in lines if l.startswith('## ')), 'H3:', sum(1 for l in lines if l.startswith('### ')))
# figuras
nf = 0
for ln in lines:
    m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)(\{w=([\d.]+)\})?\s*$', ln.strip())
    if m:
        nf += 1
        w = float(m.group(4)) if m.group(4) else None
        caminho = resolver_caminho(m.group(2), mapas, base)
        if not os.path.exists(caminho) or 'Figura' in m.group(1) or w is None or not 8 <= w <= 16:
            print('FIG PROBLEMA', m.group(2), w)
    elif ln.strip().startswith('!['):
        print('FIG NAO RECONHECIDA', ln[:100])
print('figuras', nf)
# tabelas
nt = 0
for i, ln in enumerate(lines):
    if ln.startswith('Tabela:'):
        if i + 1 < len(lines) and lines[i + 1].startswith('|'):
            nt += 1
        else:
            print('TABELA SEM PIPE', ln)
    if ln.startswith('|') and (i == 0 or not (lines[i - 1].startswith('|') or lines[i - 1].startswith('Tabela:'))):
        print('TABELA SEM LEGENDA', ln[:80])
print('tabelas', nt)
# corpo: paragrafos iniciados por [n]
for ln in corpo.splitlines():
    if re.match(r'^\[\d+\]', ln.strip()):
        print('CORPO COMECA COM [n]', ln[:80])
print('cit seguida de ( :', re.findall(r'\[\d+\]\(', corpo))
print('[@ restantes:', re.findall(r'\[@[^\]]+\]', t))
cits = set(int(x) for x in re.findall(r'\[(\d+)\]', corpo))
refn = [int(x) for x in re.findall(r'(?m)^\[(\d+)\]', refs)]
print('refs listadas', len(refn), 'citadas', len(cits), 'faltando', sorted(set(refn) - cits), sorted(cits - set(refn)))
# primeira citação em ordem
seq = []
for x in re.findall(r'\[(\d+)\]', corpo):
    x = int(x)
    if x not in seq:
        seq.append(x)
print('ordem ok', seq == sorted(seq))
for pat in ['frente LoRa', 'CERISE-AR', '172.16', 'Objetivo 3 do plano', '(Objetivo 2)', 'seção própria', 'NaN', '1e-', ' %%']:
    for m in re.finditer(re.escape(pat), t):
        print('PADRAO', pat, repr(t[max(0, m.start() - 50):m.end() + 30]))
# numeros com 4+ digitos sem separador
for m in re.finditer(r'(?<![\d.,×xX/@:#-])\d{4,}(?![\d.,×]?\d)', corpo):
    ctx = corpo[max(0, m.start() - 20):m.end() + 12].replace('\n', ' ')
    v = m.group(0)
    if v in ('2024', '2025', '2026', '2017', '2016', '2015', '1997', '2021', '2022', '2020', '2019', '2012', '2014', '2004', '2000', '1991', '1970', '1955', '1973', '1980', '2018'):
        continue
    print('NUM', repr(ctx))
