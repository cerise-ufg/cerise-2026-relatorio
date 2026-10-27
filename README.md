# Relatório Técnico-Científico CERISE 2026

Relatório técnico-científico do plano de trabalho individual **"Pesquisa, Desenvolvimento e Inovação em Gêmeos
Digitais, Tecnologias Imersivas, Robótica e Navegação Autônoma no escopo do CERISE/EMC/UFG"**, referente a 2026,
com todo o material usado na sua elaboração: texto-fonte em Markdown, gerador do `.docx` no modelo oficial do
CERISE, seções por área de trabalho, figuras (originais e derivadas, com os scripts que as produziram), anexos
(artigos, pôster, certificados e fotos) e versões intermediárias de revisão.

- **Bolsista:** Eduardo Martins de Carvalho Caixeta (CERISE/EMC/UFG)
- **Coordenadores:** Prof. Dr. Alisson Assis Cardoso (Navegação Autônoma e Gêmeos Digitais) e
  Prof. Dr. Carlos Galvão Pinheiro Junior (Realidade Aumentada)
- **Versão do relatório:** 26/10/2026 — 77 páginas, 47 figuras, 33 tabelas e 62 referências

O relatório cobre as 14 atividades numeradas do plano de trabalho 2026, os itens 1, 3 e 4 do Objetivo 5
(detecção e contagem de pessoas com drones, módulos de comunicação e adequação dos drones), os algoritmos de
colaboração entre drones do segundo eixo, a produção científica do período (artigos no MEDER 2026 e no CBA 2026,
pôster no CBA 2026) e a participação no CERISE Summit 2026.

## Arquivos principais

| Arquivo | Conteúdo |
|---|---|
| [`Relatorio_CERISE_2026_Eduardo_Caixeta.pdf`](Relatorio_CERISE_2026_Eduardo_Caixeta.pdf) | Versão final em PDF (77 páginas) |
| [`Relatorio_CERISE_2026_Eduardo_Caixeta.docx`](Relatorio_CERISE_2026_Eduardo_Caixeta.docx) | Versão final em Word, gerada a partir do Markdown |
| [`RELATORIO_CERISE_2026.md`](RELATORIO_CERISE_2026.md) | Texto-fonte completo do relatório (formato do gerador) |
| [`capa.json`](capa.json) | Dados da capa (título do plano, grupos, coordenadores, versão, bolsista) |
| [`partes_fixas.md`](partes_fixas.md) | Rascunho das partes fixas (introdução e objetivos) |
| [`roteiro/Roteiro_CERISE_2026_Eduardo_Caixeta.pdf`](roteiro/Roteiro_CERISE_2026_Eduardo_Caixeta.pdf) | Roteiro de Implementação CERISE 2026 (69 páginas): como reproduzir cada frente, com requisitos, comandos, resultados esperados e problemas comuns (também em `.docx` e no texto-fonte `ROTEIRO_CERISE_2026.md`) |

## Estrutura de pastas

```
.
├── RELATORIO_CERISE_2026.md            texto-fonte final
├── Relatorio_CERISE_2026_Eduardo_Caixeta.docx / .pdf
├── capa.json, partes_fixas.md
├── roteiro/                            Roteiro de Implementação: texto-fonte, .docx, .pdf, capa
│                                       (capa_roteiro.json) e um capítulo por frente (secoes/)
├── secoes/                             seções condensadas de cada área (01 a 07), com citações [@chave]
│                                       e bloco de referências, no formato de entrada do integrar_secao.py
├── gerador/
│   ├── build_relatorio.py              Markdown -> .docx no modelo oficial do CERISE
│   ├── modelo_cerise.docx              modelo oficial (capa, cabeçalho com logos, estilos)
│   ├── integrar_secao.py               insere uma seção no relatório e renumera as referências
│   ├── verificar_relatorio.py          verificações de consistência do Markdown
│   ├── figuras_derivadas/              scripts que geraram as figuras derivadas de figuras/
│   └── montagem_inicial/               montagem da primeira versão integrada (montar.py + partes)
├── figuras/                            figuras derivadas usadas no relatório (recortes, composições,
│   │                                   gráficos e diagramas redesenhados)
│   ├── producao_eventos/               artigos, pôster, certificados e fotos do CERISE Summit 2026
│   └── frentes/                        cópia das figuras das áreas de trabalho citadas no relatório
│                                       (mesma estrutura de pastas do espelho local E:/CERISE/FRENTES)
├── anexos/                             artigos MEDER 2026 e CBA 2026, pôster CBA 2026, certificados
│                                       do CERISE Summit 2026 e fotos do evento
├── revisao/                            versões intermediárias (antes das edições finais e antes da
│                                       seção de simulação 3D), com o .docx/.pdf de revisão
└── tools/term2png.py                   renderiza saídas de terminal como imagem (prints das evidências)
```

## Como reproduzir

### Requisitos

- Python 3.11 com `python-docx` (testado com 1.2.0) e `Pillow` — para gerar o `.docx`;
- LibreOffice (o PDF final foi exportado pelo LibreOffice Writer 26.2) — para gerar o `.pdf`;
- `matplotlib` e `PyMuPDF` — apenas para refazer as figuras derivadas.

### Gerar o `.docx` e o `.pdf`

As figuras do `RELATORIO_CERISE_2026.md` estão referenciadas pelos caminhos absolutos do ambiente em que o
relatório foi escrito (`E:/CERISE/RELATORIOS/2026/...` e `E:/CERISE/FRENTES/...`). O gerador aceita a opção
`--repo`, que resolve esses caminhos para as cópias deste repositório (a raiz e `figuras/frentes/`), sem alterar
o texto-fonte:

```bash
python gerador/build_relatorio.py gerador/modelo_cerise.docx RELATORIO_CERISE_2026.md Relatorio.docx capa.json --repo
soffice --headless --convert-to pdf --outdir . Relatorio.docx
```

Sem opções, o comportamento original é mantido (caminho usado como está escrito). Para outra organização de
pastas, use `--mapa ANTIGO=NOVO` (pode ser repetido), por exemplo
`--mapa "E:/CERISE/FRENTES=figuras/frentes"`; caminhos relativos em `NOVO` são resolvidos a partir da pasta do
Markdown. Outra alternativa é substituir os prefixos `E:/CERISE/...` no Markdown por caminhos relativos.

Conferência feita na montagem deste repositório: a geração com `--repo` produziu 47 figuras e 33 tabelas, e as
51 imagens embutidas no `.docx` (47 figuras e 4 imagens do modelo) são idênticas, byte a byte, às do `.docx` final.

### Verificar o Markdown

```bash
python gerador/verificar_relatorio.py --repo
```

Confere títulos, figuras (arquivo existente e largura entre 8 e 16 cm), tabelas com legenda, ordem e
completude das citações e números sem separador de milhar.

### Inserir uma nova seção

```bash
python gerador/integrar_secao.py RELATORIO_CERISE_2026.md secoes/NN_secao.md "## Título antes do qual inserir" --mapa chave=52
```

A seção usa citações `[@chave]` e termina com um bloco `<!-- REFERENCIAS ... -->`; as citações do relatório
são renumeradas na ordem da primeira ocorrência. A seção 07 (vídeos reais e simulação 3D) foi inserida assim.

### Refazer as figuras derivadas

Os scripts de `gerador/figuras_derivadas/` leem as figuras originais de `figuras/frentes/` (ou da pasta
indicada em `CERISE_FRENTES`) e gravam em `figuras/` (ou em `CERISE_FIGURAS`). Todos foram executados na
montagem deste repositório e reproduziram, byte a byte, as figuras derivadas versionadas.

| Script | Figuras geradas |
|---|---|
| `remover_titulos.py` | `*_sem_titulo.png` (gráficos sem o título interno, já que o relatório usa legenda própria) |
| `recortes_composicoes.py` | `a4_viewer_renders.png`, `fig_formato_quadro_recorte.png`, `amostras_perturbacoes_2x4.png`, `curvas_treino_2x2.png`, `a12i_piores_quadros_grade.png` |
| `a1_qualidade_vs_tempo_pt.py` | `a1_qualidade_vs_tempo_pt.png` (a partir de `resultados/a1_tabela.csv` da geração 3D) |
| `srv_arquitetura_vertical.py` | `srv_arquitetura_2026_vertical.png` |
| `figuras_eventos.py` | `producao_eventos/fig_summit2026_mosaico.jpg`, `fig_certificados_summit2026.png`, `fig_artigos_primeira_pagina.png`, `fig_banner_cba2026.jpg` |
| `fotos_summit.py` | `producao_eventos/summit2026_foto1..7.jpg` (orientação EXIF corrigida; requer as fotos originais) |

### Montagem inicial

`gerador/montagem_inicial/montar.py` monta a primeira versão integrada do relatório a partir de
`head.md`, `tail.md`, `anexos.md` e das seções 01 a 06 de `secoes/`. A saída coincide com
`revisao/backup_pre_edicao/RELATORIO_CERISE_2026.md`; o texto final passou depois por revisões e pela inserção
da seção 07.

## Resultados principais

Resumo transcrito da seção "Resultados obtidos" do relatório:

1. **Seleção do modelo de geração 3D:** Hunyuan3D-2 Turbo, com a melhor geometria medida (distância de Chamfer de 0,032 e F-score@0,05 de 0,951).
2. **Otimização do modelo integrado:** redução de cerca de 38 % no tempo de geração e três *presets* com tempos medianos de 23,9 s, 30,4 s e 82,1 s.
3. **Validação dos objetos 3D:** 58 de 58 testes automatizados aprovados e 7 de 7 arquivos GLB carregados nos visualizadores.
4. **Servidor de geração 3D:** taxa de erro reduzida de 90,9 % para zero e latência p95 até 22 % menor com 16 clientes simultâneos.
5. **Aplicativo CERISE AR:** fluxo da foto ao modelo texturizado validado no emulador contra o servidor real, em 13,5 s a 31,5 s sem fila.
6. **Play Store:** pacote 1.1.0 pronto e verificado, com publicação pendente.
7. **Dataset do braço robótico:** 5.000 poses e 30.000 imagens, verificadas integralmente e documentadas.
8. **Modelo de pose de 2025 no novo dataset:** ADD@60 mm de 68,0 % com transferência de aprendizado, contra 32,8 % da linha de base inicializada no ImageNet.
9. **Precisão e robustez do modelo de pose:** robustez a brilho e contraste, sensibilidade a ruído, desfoque e compressão e latência de 162,5 ms por imagem.
10. **Modelo digital do braço:** cinemática validada contra o ROS 2 e IoU de silhueta de 0,950 e 0,938 nas duas câmeras, sem calibração de massas e inércias.
11. **Gêmeo digital do braço:** erro médio de 5,41° nas juntas 1 a 4 e latência mediana de 99,6 ms, em simulação.
12. **Comunicação LoRa:** software do protótipo verificado sem hardware (51 testes automatizados e 1.130 execuções de simulação) e projeto do módulo dos drones, com ensaio físico e fabricação pendentes.
13. **Segmentação da área entre drones:** menor *makespan* em 31 de 40 casos com o DARP com refinamento por tempo.
14. **Colaboração e realocação dinâmica:** cobertura de pelo menos 99,7 % após o abandono de um drone, com aumento médio de 23,1 % no *makespan*.
15. **Detecção de pessoas em imagens aéreas:** mAP50 de pessoa de 0,528 (validação) e 0,316 (test-dev) após ajuste fino.
16. **Contagem em vídeos reais de drone:** HOTA de 0,328 e MAE de 7,46 pessoas por quadro no VisDrone2019-MOT test-dev.
17. **Simulação 3D no Isaac Sim:** quatro drones e 80 pessoas animadas, AP50 de 0,702 por quadro e contagem única global com erro de −1,3 % a 40 m e −4,1 % a 30 m na configuração calibrada.
18. **Produção científica:** dois artigos publicados (MEDER 2026 e CBA 2026) e um pôster no CBA 2026, sobre a estimação de pose com profundidade monocular (acurácia de 75,4 % com limiar de 60 mm no conjunto real DREAM, com cerca de 70 % menos dados sintéticos de treino).
19. **CERISE Summit 2026:** participação como expositor de projetos e protótipos e como monitor do evento.

Das 14 atividades numeradas do plano, 10 foram concluídas e 4 ficaram parciais; os itens 3 e 4 do Objetivo 5
ficaram pendentes por falta de hardware. A tabela completa da situação das atividades, com as ressalvas, está na
seção "Comparação com o plano de trabalho" do relatório.

## Repositórios das áreas de trabalho

O código, os resultados medidos (JSON/CSV), os registros de execução e as evidências citadas no relatório estão
nos repositórios de cada área:

| Repositório | Conteúdo |
|---|---|
| `cerise-2026-gen3d` | Análise comparativa, otimização e validação da geração 3D; servidor de geração 3D |
| `cerise-ar` | Aplicativo CERISE AR 1.1.0: integração com o servidor e pacote da Play Store |
| `cerise-2026-servo6dof-gemeo-digital` | Dataset do braço (datasheet e amostra), modelo digital e gêmeo digital |
| `cerise-2026-pose-servo6dof` | Porte, treino e avaliação do modelo de estimação de pose |
| `cerise-2026-lora-prototipo` | Protocolo, firmware, testes, simulação e projeto do módulo LoRa |
| `cerise-2026-drones-segmentacao` | Segmentação de áreas, colaboração entre drones e detecção e contagem de pessoas |

Os links do relatório apontam para os repositórios da organização ([`github.com/cerise-ufg`](https://github.com/cerise-ufg)). Cada repositório de código traz, no arquivo `ROTEIRO.md`, a parte do roteiro de implementação da sua frente; o documento completo está em [`roteiro/`](roteiro/).

## Artefatos em Releases

O PDF e o `.docx` finais também são publicados como arquivos do Release, para download direto. A lista, com
tamanhos e SHA-256, está em [`RELEASES.md`](RELEASES.md). Nenhum arquivo deste repositório passa de 50 MB.

## O que não está aqui e por quê

- **`gerador/teste/`**: teste do gerador com texto fictício (um `.md` de exemplo e as páginas renderizadas),
  sem relação com o conteúdo do relatório.
- **Arquivos de cache do Python (`__pycache__/`)**: regeneráveis.
- **Fotos originais do CERISE Summit 2026** (JPEG recebidos): as mesmas fotos, com a orientação corrigida,
  estão em `anexos/fotos_cerise_summit_2026/` e em `figuras/producao_eventos/`.
- **Notas internas de organização do trabalho e registros de execução das etapas**: não fazem parte do relatório.
- **Código, dados e pesos das áreas de trabalho**: ficam nos repositórios listados acima (e nos respectivos
  Releases); aqui estão apenas as figuras citadas no relatório e a tabela usada em uma figura derivada.
- **Segredos**: nenhum arquivo deste repositório contém chaves, tokens ou senhas.

## Licença

Nenhum arquivo de licença foi adicionado, por decisão do autor. Os artigos e o pôster em `anexos/` seguem as
condições das respectivas publicações, e o `gerador/modelo_cerise.docx` é o modelo oficial de relatório do CERISE.

## Autor

Eduardo Martins de Carvalho Caixeta — CERISE/EMC/UFG.
