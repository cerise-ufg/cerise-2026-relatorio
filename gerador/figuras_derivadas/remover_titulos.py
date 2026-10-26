"""Remove o título interno (faixa superior) de gráficos das frentes, já que o relatório usa legenda própria.

Gera em figuras/ os arquivos *_sem_titulo.png. O número associado a cada figura é a altura, em pixels,
da faixa removida no topo.

Entradas: figuras/frentes/ (cópia das evidências das frentes) ou a pasta indicada em CERISE_FRENTES.
"""
import os

from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
F = os.environ.get('CERISE_FRENTES', os.path.join(RAIZ, 'figuras', 'frentes')).replace('\\', '/').rstrip('/') + '/'
OUT = os.environ.get('CERISE_FIGURAS', os.path.join(RAIZ, 'figuras')).replace('\\', '/').rstrip('/') + '/'

crops = {
 'REALIDADE AUMENTADA/GERACAO_3D/evidencias/a1_qualidade_vs_tempo.png': 42,
 'REALIDADE AUMENTADA/GERACAO_3D/evidencias/a3i_tempo_por_etapa.png': 54,
 'ROBOTICA/SERVO6DOF_GEMEO/evidencias/a7_cobertura_correlacao.png': 78,
 'ROBOTICA/SERVO6DOF_GEMEO/evidencias/a7_real_vs_comandado.png': 43,
 'NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/06_colaboracao_linha_do_tempo.png': 40,
 'NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/04_benchmark_makespan.png': 40,
 'ROBOTICA/SERVO6DOF_GEMEO/evidencias/a11_espaco_trabalho.png': 74,
}
for p, y in crops.items():
    im = Image.open(F + p)
    name = p.split('/')[-1].replace('.png', '_sem_titulo.png')
    im.crop((0, y, im.width, im.height)).save(OUT + name)
    print(name)
