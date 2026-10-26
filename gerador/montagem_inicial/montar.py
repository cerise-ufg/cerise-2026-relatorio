"""Montagem inicial do RELATORIO_CERISE_2026.md a partir das partes fixas (head.md, tail.md, anexos.md) e das
seções condensadas de cada frente (secoes/01..06).

Registro da primeira versão integrada do relatório. O texto final (RELATORIO_CERISE_2026.md, na raiz do
repositório) passou depois por revisões manuais e pela inserção da seção 07 com gerador/integrar_secao.py;
por isso a saída deste script não coincide com a versão final.

Uso: python montar.py [SAIDA.md]   (padrão: RELATORIO_CERISE_2026.montagem_inicial.md nesta pasta)
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
SCR = AQUI + os.sep
SEC = os.path.join(AQUI, '..', '..', 'secoes') + os.sep
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'RELATORIO_CERISE_2026.montagem_inicial.md')


def rd(p):
    return open(p, encoding='utf-8').read()


def rep(txt, old, new, count=1):
    n = txt.count(old)
    if n != count:
        raise SystemExit(f'ERRO: esperado {count} ocorrencia(s), achado {n}: {old[:90]!r}')
    return txt.replace(old, new)


REFS = {}


def tira_refs(txt):
    def coleta(m):
        for ln in m.group(1).splitlines():
            mm = re.match(r'^\s*\[@([^\]]+)\]:\s*(.+)$', ln)
            if mm:
                k = mm.group(1).strip()
                if k == 'yang2024dav2':
                    k = 'depthanythingv2'
                REFS.setdefault(k, mm.group(2).strip())
        return ''
    return re.sub(r'<!--\s*REFERENCIAS(.*?)-->', coleta, txt, flags=re.S).rstrip() + '\n'


# ---------- 01 geração 3D ----------
s01 = rd(SEC + '01_geracao3d.md')
s01 = rep(s01, 'O aplicativo CERISE-AR de 2025 enviava as fotografias capturadas a um servidor que apenas simulava a reconstrução: aguardava 67 s e devolvia sempre o mesmo arquivo GLB.',
          'O aplicativo CERISE AR de 2025 enviava as fotografias capturadas a um servidor que apenas simulava a reconstrução e devolvia sempre o mesmo arquivo GLB, conforme detalhado na análise do servidor apresentada adiante.')
s01 = rep(s01, 'A integração com o servidor e com o aplicativo é tratada nas seções próprias.',
          'A integração com o servidor e com o aplicativo é tratada nas subseções próprias.')
s01 = rep(s01, 'de 2,60 MB para 0,44 MB no rápido.',
          'de 2,60 MB para 0,44 MB no rápido, usado pela rota legada do servidor.')
s01 = rep(s01, 'foi validado da mesma forma no teste ponta a ponta do servidor, apresentado na seção correspondente.',
          'foi validado da mesma forma no teste ponta a ponta do servidor, apresentado na subseção correspondente.')
s01 = rep(s01, 'etapa que depende da integração tratada em seção própria.',
          'etapa que depende da integração com o aplicativo, tratada adiante.')
s01 = tira_refs(s01)

# ---------- 02 servidor e app ----------
s02 = rd(SEC + '02_servidor_app.md')
s02 = rep(s02, 'O servidor executa o modelo de geração 3D selecionado e otimizado na frente de modelos generativos (Hunyuan3D-2 Turbo [@hunyuan3d2]) e está hospedado na estação NVIDIA DGX Spark (GB10) do CERISE, compartilhada com os serviços de IA em produção.',
          'O servidor executa o modelo de geração 3D selecionado e otimizado nas subseções anteriores (Hunyuan3D-2 Turbo [@hunyuan3d2]) e está hospedado na mesma estação DGX Spark, compartilhada com os serviços de IA em produção.')
s02 = rep(s02, 'Esse teste revelou que a textura era gravada em PNG; corrigido o pós-processamento, o GLB caiu de 2,97 MB para 0,72 MB (−76 %) no *preset* padrão e de 2,60 MB para 0,44 MB (−83 %) na rota legada, sem alteração mensurável no tempo de geração.',
          'Esse teste revelou que a textura era gravada em PNG, defeito descrito na errata da subseção de otimização do modelo; corrigido o pós-processamento, o GLB caiu de 2,97 MB para 0,72 MB (−76 %) no *preset* padrão e de 2,60 MB para 0,44 MB (−83 %) na rota legada, que usa o *preset* rápido, sem alteração mensurável no tempo de geração.')
s02 = tira_refs(s02)

# ---------- 03 dataset, modelo digital, gêmeo ----------
s03 = rd(SEC + '03_dataset_gemeo.md')
s03 = rep(s03, 'Código e evidências: [cerise-2026-servo6dof-gemeo-digital](https://github.com/EduardoCaixeta/cerise-2026-servo6dof-gemeo-digital) (repositório privado).',
          'Código e evidências: [repositório cerise-2026-servo6dof-gemeo-digital (privado)](https://github.com/EduardoCaixeta/cerise-2026-servo6dof-gemeo-digital)', count=3)
s03 = rep(s03, 'uma amostra de 8 poses (4,2 MB) está versionada no repositório. O *split* determinístico por identificador (`id` mod 10) define 4.000 poses de treino, 500 de validação e 500 de teste.',
          'uma amostra de 8 poses (4,2 MB) está versionada no repositório. O datasheet recomenda um *split* determinístico por identificador (`id` mod 10), com 4.000 poses de treino, 500 de validação e 500 de teste; as avaliações das subseções seguintes adotaram, nas mesmas proporções, a divisão aleatória por pose definida na etapa de estimação de pose.')
s03 = rep(s03, 'Todos os resultados desta seção e das seções seguintes referem-se à versão do dataset com o braço em cinza',
          'Todos os resultados desta subseção e das subseções seguintes sobre o braço robótico referem-se à versão do dataset com o braço em cinza')
s03 = s03.replace('[@yang2024dav2]', '[@depthanythingv2]')
s03 = tira_refs(s03)
partes03 = re.split(r'(?m)^(?=## )', s03)
partes03 = [p for p in partes03 if p.strip()]
assert len(partes03) == 3, len(partes03)
a7, a11, a12 = partes03
assert a7.startswith('## Geração e documentação') and a11.startswith('## Modelo digital') and a12.startswith('## Gêmeo digital')

# ---------- 04 pose ----------
s04 = rd(SEC + '04_pose.md')
s04 = rep(s04, 'Esse conjunto foi produzido em simulação (Gazebo/ROS 2) com o braço servo6dof, de cinco juntas rotacionais e garra, observado por duas câmeras fixas (frontal e diagonal), e reúne 5.000 poses com imagens RGB 1280×720 e os ângulos reais das juntas.',
          'Esse conjunto, descrito na subseção anterior, reúne 5.000 poses do braço servo6dof, de cinco juntas rotacionais e garra, observado em simulação por duas câmeras fixas (frontal e diagonal), com imagens RGB 1280×720 e os ângulos reais das juntas.')
s04 = rep(s04, 'A divisão treino/validação/teste foi feita por pose, na proporção 80/10/10',
          'A divisão treino/validação/teste foi feita por pose, de forma aleatória (semente 2026), na proporção 80/10/10')
s04 = rep(s04, 'com taxa 1e-4 decaindo 0,9 por época', 'com taxa de aprendizado de 1×10⁻⁴, multiplicada por 0,9 a cada época')
s04 = rep(s04, 'Os valores de RoboPose e HPRE reproduzem os do relatório de 2025;',
          'Os valores de RoboPose e HPRE foram transcritos do relatório de 2025 e não puderam ser reconferidos em arquivo de resultados nesta etapa;')
s04 = tira_refs(s04)

# ---------- 05 LoRa ----------
s05 = rd(SEC + '05_lora.md')
s05 = rep(s05, 'Esta etapa corresponde à Atividade 10 do Objetivo 3 do plano de trabalho, que prevê',
          'Esta etapa corresponde à Atividade 10 do plano de trabalho, que prevê')
s05 = rep(s05, 'Três tipos propostos por aquela frente (`AREA_POLY`, `TASK_BID` e `TASK_AWARD`) foram incorporados como extensão aditiva, sem mudança de versão.',
          'Três tipos propostos por aquela frente (`AREA_POLY`, `TASK_BID` e `TASK_AWARD`) foram incorporados como extensão aditiva, sem mudança de versão, e um teste automatizado confirma a compatibilidade byte a byte com os quadros de exemplo daquela frente.')
s05 = tira_refs(s05)

# ---------- 06 drones ----------
s06 = rd(SEC + '06_drones.md')
s06 = rep(s06, 'Esta etapa trata dos algoritmos de colaboração entre drones previstos no plano de trabalho (Objetivo 2) e complementa a Atividade 13 do Objetivo 5.',
          'Esta etapa trata dos algoritmos de colaboração entre drones previstos no plano de trabalho e complementa a Atividade 13 do Objetivo 5.')
s06 = rep(s06, 'As mensagens foram alinhadas à biblioteca `cerise_proto` v1, implementada na frente de comunicação LoRa deste plano.',
          'As mensagens foram alinhadas à biblioteca `cerise_proto` v1 do protótipo LoRa apresentado anteriormente.')
s06 = rep(s06, '8 (TASK_BID) e 9 (TASK_AWARD), ainda não incorporada ao firmware da frente LoRa.',
          '8 (TASK_BID) e 9 (TASK_AWARD), incorporada à biblioteca do protótipo LoRa, mas ainda não exercitada com rádios.')
s06 = rep(s06, 'Em SF9, configuração padrão do firmware da frente LoRa, todos os quadros ficam abaixo do limite de 400 ms de ocupação adotado naquela frente;',
          'Em SF9, configuração padrão do firmware do protótipo LoRa, todos os quadros ficam abaixo do limite de 400 ms de ocupação adotado no protótipo;')
s06 = rep(s06, 'A extensão AREA_POLY, TASK_BID e TASK_AWARD ainda precisa ser incorporada ao `cerise_proto`, e a realocação não foi testada de ponta a ponta com os módulos de rádio nem em voo; a política híbrida não foi implementada.',
          'A realocação não foi testada de ponta a ponta com os módulos de rádio nem em voo, e a política híbrida não foi implementada.')
s06 = rep(s06, 'Além do módulo LoRa descrito na seção da frente de comunicação, foram levantados',
          'Além do módulo LoRa descrito anteriormente, foram levantados')
s06 = rep(s06, 'O conjunto de treino tem 6471 imagens e 106 396 pessoas; o de validação, 548 imagens e 13 969 pessoas; e o test-dev, 1610 imagens e 27 382 pessoas.',
          'O conjunto de treino tem 6.471 imagens e 106.396 pessoas; o de validação, 548 imagens e 13.969 pessoas; e o test-dev, 1.610 imagens e 27.382 pessoas.')
s06 = rep(s06, 'avaliadas com até 1000 detecções por imagem', 'avaliadas com até 1.000 detecções por imagem')
s06 = tira_refs(s06)

# separador de milhar com espaço (05 e 06) -> ponto
milhar = re.compile(r'(?<![\d,.])(\d{1,3}) (\d{3})(?![\d,])')
for nome in ('s05', 's06'):
    t = globals()[nome]
    for m in milhar.finditer(t):
        print('milhar', nome, repr(t[max(0, m.start() - 25):m.end() + 10]))
    globals()[nome] = milhar.sub(r'\1.\2', t)

corpo = '\n'.join(x.strip() + '\n' for x in (s01, s02, a7, s04, a11, a12, s05, s06))
doc = rd(SCR + 'head.md').rstrip() + '\n\n' + corpo + '\n' + rd(SCR + 'tail.md').rstrip() + '\n'

# porcentagem e unidades com espaço inseparável (evita quebrar "30,4 | s" no fim da linha)
doc = re.sub(r'(\d)%', r'\1 %', doc)
UNID = r'(%|s|ms|mm|cm|m|km|MB|GB|GiB|KiB|MiB|KB|B|px|ha|min|h|W|V|dB|dBm|dBi|MHz|kHz|Hz|bps|m³|cm³|g|kg|p\.p\.)'
doc = re.sub(r'(\d) ' + UNID + r'(?=[\s,.;:)|/]|$)', '\\1\u00a0\\2', doc)

# citações -> [n] na ordem da primeira citação
ordem = []
for m in re.finditer(r'\[@([A-Za-z0-9_:-]+)\]', doc):
    k = m.group(1)
    if k not in ordem:
        ordem.append(k)
REFS.update({
    'azuma1997': 'AZUMA, R. T. A survey of augmented reality. Presence: Teleoperators and Virtual Environments, v. 6, n. 4, 1997.',
    'billinghurst2015': 'BILLINGHURST, M.; CLARK, A.; LEE, G. A survey of augmented reality. Foundations and Trends in Human-Computer Interaction, v. 8, n. 2-3, 2015.',
    'chen2017': 'CHEN, P.; LIU, X.; CHENG, W.; HUANG, R. A review of using augmented reality in education from 2011 to 2016. In: Innovations in Smart Learning. Singapore: Springer, 2017.',
    'barsom2016': 'BARSOM, E. Z.; GRAAFLAND, M.; SCHIJVEN, M. P. Systematic review on the effectiveness of augmented reality applications in medical training. Surgical Endoscopy, v. 30, n. 10, 2016.',
})
faltam = [k for k in ordem if k not in REFS]
if faltam:
    raise SystemExit(f'ERRO: citações sem referência: {faltam}')
nao_citadas = [k for k in REFS if k not in ordem]
print('referencias definidas e nao citadas (descartadas):', nao_citadas)
num = {k: i + 1 for i, k in enumerate(ordem)}
doc = re.sub(r'\[@([A-Za-z0-9_:-]+)\]', lambda m: f'[{num[m.group(1)]}]', doc)
doc = re.sub(r'\[(\d+)\] \[(\d+)\]', r'[\1], [\2]', doc)


def linkifica(ref):
    return re.sub(r'(https?://[^\s)\]]+?)(\.?)(?=\s|$)', lambda m: f'[{m.group(1)}]({m.group(1)}){m.group(2)}', ref)


refs_md = '# Referências bibliográficas\n\n' + '\n\n'.join(f'[{num[k]}] {linkifica(REFS[k])}' for k in ordem) + '\n'
doc = doc.rstrip() + '\n\n' + refs_md + '\n' + rd(SCR + 'anexos.md').rstrip() + '\n'
open(OUT, 'w', encoding='utf-8', newline='\n').write(doc)
print('OK', OUT, 'refs', len(ordem), 'chars', len(doc))
