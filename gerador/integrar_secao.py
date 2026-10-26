#!/usr/bin/env python3
"""Insere uma seção condensada (secoes/NN_*.md, formato do gerador) no relatório e renumera as referências.

- A seção usa citações [@chave] e termina com um bloco <!-- REFERENCIAS ... --> ("[@chave]: referência").
- Chaves que já existem na lista do relatório são mapeadas por --mapa chave=n (n = número atual no relatório).
- As demais entram no fim da lista; depois todas as citações [n] são renumeradas na ordem da primeira citação
  no corpo e a lista de referências é reordenada.

Uso: python integrar_secao.py RELATORIO.md SECAO.md "## Título antes do qual inserir" --mapa chave=52 chave2=47
"""
import argparse
import re

REF_HEAD = '# Referências bibliográficas'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('relatorio')
    ap.add_argument('secao')
    ap.add_argument('antes_de')
    ap.add_argument('--mapa', nargs='*', default=[])
    a = ap.parse_args()

    doc = open(a.relatorio, encoding='utf-8').read()
    sec = open(a.secao, encoding='utf-8').read()

    m = re.search(r'<!--\s*REFERENCIAS(.*?)-->', sec, re.S)
    refs_sec = {}
    if m:
        for ln in m.group(1).splitlines():
            mm = re.match(r'\s*\[@([^\]]+)\]:\s*(.+)$', ln)
            if mm:
                refs_sec[mm.group(1).strip()] = mm.group(2).strip()
        sec = sec[:m.start()].rstrip() + '\n'

    i_ref = doc.index(REF_HEAD)
    body, refs_part = doc[:i_ref], doc[i_ref + len(REF_HEAD):]
    lista = {}
    for mm in re.finditer(r'^\[(\d+)\]\s+(.+?)\s*$', refs_part, re.M):
        lista[int(mm.group(1))] = mm.group(2)

    mapa = {}
    for kv in a.mapa:
        k, v = kv.split('=')
        mapa[k] = int(v)
    prox = max(lista) + 1
    for k in re.findall(r'\[@([^\]]+)\]', sec):
        if k not in mapa:
            if k not in refs_sec:
                raise SystemExit(f'chave sem referência: {k}')
            mapa[k] = prox
            lista[prox] = refs_sec[k]
            prox += 1
    sec = re.sub(r'\[@([^\]]+)\]', lambda mm: f'[{mapa[mm.group(1)]}]', sec)

    if a.antes_de not in body:
        raise SystemExit(f'âncora não encontrada: {a.antes_de}')
    body = body.replace(a.antes_de, sec.rstrip() + '\n\n' + a.antes_de, 1)

    # renumera na ordem da primeira citação no corpo
    cit = re.compile(r'\[(\d{1,3})\](?!\()')
    ordem = []
    for mm in cit.finditer(body):
        n = int(mm.group(1))
        if n in lista and n not in ordem:
            ordem.append(n)
    nao_citadas = [n for n in sorted(lista) if n not in ordem]
    if nao_citadas:
        print('AVISO: referências não citadas (mantidas no fim):', nao_citadas)
    ordem += nao_citadas
    novo = {old: i + 1 for i, old in enumerate(ordem)}
    body = cit.sub(lambda mm: f'[{novo[int(mm.group(1))]}]' if int(mm.group(1)) in novo else mm.group(0), body)
    nova_lista = '\n\n'.join(f'[{novo[old]}] {lista[old]}' for old in ordem)
    doc = body + REF_HEAD + '\n\n' + nova_lista + '\n'
    open(a.relatorio, 'w', encoding='utf-8').write(doc)
    print(f'OK: {len(lista)} referências; novas: {[k for k in mapa if mapa[k] >= max(lista) - len(refs_sec)]}')
    mudou = {o: n for o, n in novo.items() if o != n}
    print('renumeradas:', len(mudou))


if __name__ == '__main__':
    main()
