## Análise comparativa e seleção do modelo de geração 3D

Esta etapa corresponde à Atividade 1 do Objetivo 1 do plano de trabalho, que prevê a análise comparativa de redes neurais de geração de objetos 3D com textura. O aplicativo CERISE-AR de 2025 enviava as fotografias capturadas a um servidor que apenas simulava a reconstrução: aguardava 67 s e devolvia sempre o mesmo arquivo GLB. O objetivo da atividade foi levantar os modelos abertos de imagem para 3D texturizado e compará-los experimentalmente na infraestrutura do laboratório, a fim de selecionar a rede a ser integrada ao aplicativo.

### Metodologia

Os experimentos foram executados na estação NVIDIA DGX Spark (GB10) do laboratório, com GPU de arquitetura Blackwell (sm_121), CPU aarch64 de 20 núcleos e 128 GB de memória unificada. Foi usado um contêiner derivado de `nvcr.io/nvidia/pytorch:26.05-py3` (PyTorch 2.12, CUDA 13.2), com as extensões CUDA dos modelos compiladas para sm_121 e o alocador do PyTorch limitado a 24 GB, teto definido para esta frente. A estação é de produção e foi compartilhada durante todas as medições, com a geração de um conjunto de dados de outra frente, treinamentos e serviços de inferência (vLLM). Por isso, os tempos absolutos devem ser lidos como limites superiores, dependentes da ocupação da máquina.

O conjunto de avaliação reuniu 13 objetos do Google Scanned Objects [@gso] (licença CC-BY 4.0), que fornecem a malha escaneada de referência. Cada malha foi normalizada e renderizada com nvdiffrast [@nvdiffrast] numa vista de entrada de 1024×1024 px com fundo transparente (azimute 30°, elevação 15°) e em três vistas de referência não observadas pelos modelos (azimutes 120°, 210° e 300°). Na geometria, foram calculados a distância de Chamfer e o F-score a τ = 0,05 e 0,1, após normalização pela caixa envolvente e alinhamento por ICP com escala uniforme [@umeyama], iniciado em 12 guinadas e duas convenções de eixo. Na aparência, foi usada a similaridade de cosseno CLIP ViT-L/14 [@clip], calculada entre a entrada e o render do resultado na mesma vista (CLIP entrada) e entre os renders do resultado e da referência nas três vistas novas (CLIP vistas novas). No desempenho, foram medidos a mediana do tempo por objeto em carga quente (modelos residentes e primeira geração descartada) e o pico de memória do alocador. Um autoteste do alinhamento, que aplica rotação, escala e translação arbitrárias à própria malha de referência, indicou piso de erro com Chamfer médio de 0,0042 e F-score@0,05 mínimo de 0,976. A saída desse autoteste permanece na estação de trabalho e não foi copiada para o repositório.

### Levantamento da literatura

A tabela a seguir resume os modelos considerados e o resultado da tentativa de instalação no GB10, que combina CPU aarch64, arquitetura sm_121 e CUDA 13.

Tabela: Modelos abertos de geração 3D texturizada a partir de imagem e situação da instalação no GB10
| Modelo (organização, ano) | Licença | Saída | Situação no GB10 |
|---|---|---|---|
| Hunyuan3D-2.0 [@hunyuan3d2] (Tencent, 2025) | Tencent Hunyuan 3D 2.0 Community | malha e textura UV RGB | instalado e medido |
| Hunyuan3D-2mini Turbo (Tencent, 2025) | idem | malha e textura UV RGB | instalado e medido |
| Hunyuan3D-2 Turbo e FlashVDM [@flashvdm] (Tencent, 2025) | idem | malha e textura UV RGB | instalado e medido |
| Hunyuan3D-2.1 [@hunyuan3d21] (Tencent, 2025) | Tencent Hunyuan 3D 2.1 Community | malha e materiais PBR | instalado com adaptações e medido |
| TRELLIS [@trellis] (Microsoft, 2024) | MIT | gaussianas, campos de radiância ou malha | bloqueado: dependências sem versão aarch64 |
| TRELLIS.2 (Microsoft, 2025) | MIT | malha O-Voxel e PBR | bloqueado: componente de acesso restrito |
| TripoSR [@triposr] (Stability AI e Tripo AI, 2024) | MIT | malha com cor por vértice | instalado e medido |
| Stable Fast 3D [@sf3d] (Stability AI, 2024) | Stability AI Community | malha com UV, textura e material | bloqueado: pesos de acesso restrito |
| SPAR3D [@spar3d] (Stability AI, 2025) | Stability AI Community | nuvem de pontos e malha texturizada | bloqueado: pesos de acesso restrito |
| InstantMesh [@instantmesh] (TencentARC, 2024) | Apache-2.0 | malha com cor por vértice ou textura | instalado e medido |

Os bloqueios são concretos. O TRELLIS depende de `spconv` e `cumm`, que não têm distribuição para linux-aarch64 no PyPI: nenhum dos 10 arquivos de cada distribuição consultada é aarch64 (`resultados/trellis_bloqueio_pypi.txt`). O TRELLIS.2 usa extensões CUDA próprias e o codificador DINOv3, distribuído em repositório de acesso restrito. Os pesos do Stable Fast 3D e do SPAR3D também exigem login no Hugging Face e aceite da licença pelo bolsista, etapa ainda pendente.

### Benchmark prático

Foram instalados e medidos seis modelos ou variantes. Executar o Hunyuan3D-2.1 em aarch64 exigiu duas adaptações: o GLB com materiais PBR passou a ser escrito com trimesh, porque o Blender (`bpy`) não tem pacote para essa plataforma, e o rasterizador da versão 2.1 foi compilado à parte. Pelo custo de cerca de 4 min por objeto, o Hunyuan3D-2.0 na configuração padrão e o 2.1 foram medidos em subconjuntos de 4 e 2 objetos, respectivamente.

Tabela: Benchmark no GB10 em carga quente (n = objetos avaliados; tempo mediano por objeto)
| Modelo | n | Tempo (s) | Pico GPU (GB) | Chamfer ↓ / F@0,05 ↑ | CLIP entrada / vistas novas ↑ |
|---|---|---|---|---|---|
| TripoSR | 13 | 0,9 | 4,2 | 0,042 / 0,904 | 0,849 / 0,809 |
| InstantMesh | 13 | 16,5 | 23,2 | 0,046 / 0,893 | 0,844 / 0,836 |
| Hunyuan3D-2mini-Turbo | 13 | 65,8 | 13,6 | 0,035 / 0,930 | 0,893 / 0,859 |
| **Hunyuan3D-2-Turbo** | 13 | 68,8 | 14,6 | **0,032 / 0,951** | 0,907 / 0,854 |
| Hunyuan3D-2.0 (padrão) | 4 | 229,5 | 14,5 | 0,039 / 0,918 | **0,933 / 0,884** |
| Hunyuan3D-2.1 (PBR) | 2 | 242,9 | 13,8 | 0,032 / 0,949 | 0,883 / 0,878 |

![Qualidade em função do tempo mediano por objeto (escala logarítmica) no benchmark com objetos do Google Scanned Objects: à esquerda, F-score@0,1 da geometria; à direita, similaridade CLIP entre a entrada e o render do resultado](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a1_qualidade_vs_tempo.png){w=16}

![Comparação qualitativa numa vista não observada pelos modelos (azimute 210°): entrada, referência escaneada e resultado de cada modelo alinhado à referência; "não medido" indica objeto fora do subconjunto daquele modelo](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a1_grade_vista_nova.png){w=16}

![Tempo médio por objeto decomposto por etapa para cada modelo avaliado](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a1_tempo_por_etapa.png){w=15}

![Saída do terminal do benchmark do Hunyuan3D-2 Turbo no contêiner da estação DGX Spark: carga do modelo, aquecimento e, por objeto, tempo total, faces, pico de memória e etapas mais longas](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/term_a1_hy2_turbo.png){w=16}

### Discussão e seleção

O Hunyuan3D-2-Turbo obteve a melhor geometria no conjunto completo (Chamfer 0,032; F-score@0,05 de 0,951 e F-score@0,1 de 0,992). O Hunyuan3D-2.1 alcançou valores equivalentes nos dois objetos em que foi medido. O TripoSR foi duas ordens de grandeza mais rápido (0,9 s), mas apresentou geometria inferior e aparência limitada à cor por vértice, com as faces ocultas escuras e borradas. O InstantMesh também produz apenas cor por vértice e atingiu 23,2 GB de pico, no limite do teto da frente. Seu F-score@0,05 médio caiu para 0,766 no subconjunto que inclui a águia e a tartaruga, contra 0,913 apenas no ônibus e na caneca. Segundo as métricas por objeto mantidas na estação, essa queda se concentra na águia, cujas asas finas colapsam.

Na aparência, o Hunyuan3D-2.0 com o módulo de textura completo obteve os maiores valores de CLIP (0,933 na entrada e 0,884 nas vistas novas), à custa de 229,5 s por objeto. O CLIP do Hunyuan3D-2.1 ficou subestimado, porque o renderizador da avaliação usa apenas o albedo e não aplica sombreamento PBR, o que escurece o resultado. A comparação de tempos entre modelos é apenas indicativa: os modelos turbo foram medidos com média de carga da CPU próxima de 39, enquanto o 2.0 e o 2.1 rodaram com carga entre 3 e 4. A mesma configuração Turbo levou 28,7 s por objeto (mediana) na série sequencial de otimização, executada em outro horário, com a máquina parcialmente livre. A decomposição por etapa mostra que, nos modelos turbo, a rede de forma (difusão e decodificação) consome em média de 10,8 a 11,7 s, e o restante do tempo cabe à limpeza da malha com pymeshlab e à textura, que se tornaram os alvos da otimização. Já no 2.0 e no 2.1 predominam os 50 passos de difusão (45 a 74 s) e a decodificação volumétrica sem FlashVDM (77 a 81 s).

Foi selecionado o **Hunyuan3D-2 Turbo** (forma destilada com FlashVDM, textura Paint-v2-0-Turbo e remoção de iluminação), pelos seguintes motivos: melhor geometria medida no conjunto completo; textura UV real, requisito para boa aparência em realidade aumentada; pico de memória de cerca de 14,5 GB, compatível com o teto da frente e com a coexistência com os serviços de produção; e licença que permite o uso no Brasil, embora exclua a União Europeia, o Reino Unido e a Coreia do Sul e exija licença própria para uso comercial acima de 1 milhão de usuários mensais. O TripoSR (MIT) fica documentado como alternativa de licença permissiva, e o Hunyuan3D-2.1 (PBR), como evolução futura quando houver GPU dedicada.

Código e evidências: [repositório cerise-2026-gen3d (privado)](https://github.com/cerise-ufg/cerise-2026-gen3d)

## Otimização do modelo integrado e desempenho

Esta etapa corresponde à Atividade 3 do Objetivo 1 do plano de trabalho (aplicativo otimizado e relatório de desempenho), na parte relativa à otimização do modelo de geração. A integração com o servidor e com o aplicativo é tratada nas seções próprias. O objetivo foi reduzir o tempo de geração do Hunyuan3D-2 Turbo sem perda mensurável de qualidade, definir configurações (*presets*) para o aplicativo e empacotar o pipeline para uso pelo servidor.

### Variantes avaliadas

Partiu-se da configuração base: 5 passos de difusão, FlashVDM, octree 384, limpeza e decimação para 40 mil faces com pymeshlab, textura de 2048 px e precisão fp16. Cada fator foi alterado isoladamente: pós-processamento rápido da malha (descarte de componentes com menos de 1% da área do maior e decimação quádrica com `fast-simplification`), octree 256, 20 mil e 10 mil faces, textura de 1024 px, 10 passos de difusão, módulo de textura completo (não destilado), forma em bf16 e FlashVDM desligado. Foram medidas duas séries. Na série intercalada, com 4 objetos, os modelos foram carregados uma única vez e todas as variantes de parâmetros foram executadas em sequência para cada objeto, o que as submete às mesmas condições de ocupação. Na série sequencial, com 7 objetos, cada variante foi executada numa rodada própria, o que permitiu incluir as variantes que exigem outros pesos, com tempos mais sensíveis à ocupação da máquina.

Tabela: Série intercalada (4 objetos; razão = mediana, por objeto, do tempo da variante dividido pelo tempo da base)
| Variante | Tempo mediano (s) | Razão vs. base | Pós-proc. da malha (s) | F@0,05 ↑ | CLIP entrada / vistas novas ↑ |
|---|---|---|---|---|---|
| base | 63,9 | 1,00 | 33,1 | 0,949 | 0,917 / 0,837 |
| **pós-processamento rápido** | **37,5** | **0,62** | **6,2** | 0,950 | 0,908 / 0,833 |
| **octree 256** | **41,0** | **0,64** | 13,1 | 0,951 | 0,914 / 0,844 |
| 20 mil faces | 63,8 | 0,99 | 33,3 | 0,948 | 0,915 / 0,843 |
| 10 mil faces | 63,6 | 0,98 | 33,6 | 0,949 | 0,914 / 0,845 |
| textura 1024 px | 63,0 | 0,99 | 33,0 | 0,949 | 0,912 / 0,843 |
| 10 passos de difusão | 67,1 | 1,10 | 32,9 | 0,948 | 0,913 / 0,864 |

![Tempo médio por objeto e por etapa de cada variante do Hunyuan3D-2 Turbo na série intercalada (4 objetos)](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a3i_tempo_por_etapa.png){w=15}

![Qualidade de cada variante na série sequencial (7 objetos): F-score@0,05, Chamfer e CLIP de entrada; a linha tracejada indica a configuração base](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a3_qualidade_variantes.png){w=16}

Os principais resultados foram os seguintes:

- **FlashVDM** mostrou-se indispensável: sem ele, a etapa de forma passou de 3,5 s para 115,7 s (cerca de 33 vezes, medido em 3 objetos), sem ganho de geometria (F-score@0,05 de 0,933 contra 0,940).
- O **pós-processamento rápido** trouxe a maior economia: o tempo da limpeza caiu de 33,1 s para 6,2 s e o total foi reduzido em cerca de 38% (razão mediana de 0,62 na série intercalada e de 0,55 na sequencial), com geometria inalterada e CLIP de entrada 0,009 menor.
- A **octree 256** reduziu o total em cerca de 36% sem perda mensurável de qualidade.
- O orçamento de faces e a textura de 1024 px praticamente não alteraram o tempo, mas reduziram o GLB bruto (3,7 MB para 2,8 MB com 10 mil faces e para 1,9 MB com textura de 1024 px, ambos com textura PNG).
- **10 passos** custaram 10% a mais de tempo, sem ganho geométrico, e elevaram o CLIP das vistas novas em 0,027.
- O **módulo de textura completo** elevou o tempo da textura de 12,0 s para 51,7 s na série sequencial, mas foi a única variante que melhorou claramente as partes ocultas (CLIP vistas novas de 0,846 para 0,893).
- A **forma em bf16** teve qualidade equivalente após uma correção de tipo no *marching cubes* e não trouxe ganho de tempo, de modo que o fp16 foi mantido. A compilação com `torch.compile` não foi avaliada.

### Presets e pipeline empacotado

Com base nesses resultados, foram definidos três presets sobre um único modelo de forma (Turbo com FlashVDM e 5 passos) e com o pós-processamento rápido, o que permite manter os modelos carregados no servidor. O preset **rápido** usa octree 256, 10 mil faces e textura de 1024 px com o Paint Turbo. O **padrão** usa octree 384, 20 mil faces e textura gerada em 2048 px e entregue em 1024 px, também com o Paint Turbo. O **alto** usa octree 384, 40 mil faces, textura de 2048 px e o módulo de textura completo. Os presets foram medidos de ponta a ponta com o pipeline empacotado (remoção de fundo, geração, pós-processamento para o celular e miniatura) nos 13 objetos do GSO e em 6 fotografias reais, com os serviços de produção ativos na mesma máquina.

Tabela: Presets medidos no pipeline empacotado (19 entradas; GLB com textura PNG, anterior à correção descrita adiante)
| Preset | Tempo mediano GSO (s) | Tempo mediano fotos reais (s) | Faixa (s) | Pico GPU (GB) | GLB mediano (MB) |
|---|---|---|---|---|---|
| rápido | 23,9 | 24,0 | 21,9–27,3 | 14,5 | 1,65 |
| padrão | 30,4 | 29,8 | 26,8–76,6 | 14,5 | 2,01 |
| alto | 82,1 | 56,7 | 53,5–104,5 | 14,5 | 6,14 |

A geometria foi a mesma nos três presets (F-score@0,05 de 0,951 nos 13 objetos do GSO). O CLIP de entrada foi de 0,890, 0,894 e 0,922 e o CLIP das vistas novas, de 0,840, 0,851 e 0,876, nos presets rápido, padrão e alto. A carga a frio do pipeline levou 115 s, com 11,4 GB alocados, e o aquecimento, 79 s. No preset alto, esses tempos foram de 107 s e 118 s. Esses valores justificam manter os modelos residentes no servidor. A dispersão dos tempos (até 76,6 s no padrão) e a diferença do preset alto entre GSO e fotos reais refletem a variação de ocupação da GPU durante as rodadas.

![Tempo médio por objeto e por etapa dos três presets no pipeline empacotado; no preset alto predomina a difusão multivista do módulo de textura completo](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/presets_tempo_por_etapa.png){w=15}

O pós-processamento para o celular (`pipeline/postprocess.py`) assenta o objeto em y = 0 e o centraliza em x e z, corrigindo o script de ajuste de 2025, que deslocava o eixo Z pelo centro do eixo Y. Em seguida, escala a maior dimensão para 0,30 m, reduz a textura com glTF-Transform e valida o arquivo com o Khronos glTF-Validator. Por requisito do aplicativo, cujo `<model-viewer>` funciona sem conexão e cujo ViroReact não tem decodificadores, o GLB entregue não usa Draco, meshopt nem KTX2. O pipeline foi empacotado na classe `Gen3DPipeline`, que carrega os modelos uma única vez e oferece o método `generate(imagem, saída, preset)`, e na imagem Docker `cerise26_gen3d:latest` (38 GB), conforme ilustrado abaixo.

![Construção da imagem Docker cerise26_gen3d:latest na estação DGX Spark e teste rápido dentro dela: PyTorch com CUDA no GB10, módulo do pipeline, presets, Node 22 e glTF-Transform](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/term_docker_imagem.png){w=16}

### Errata da textura e limitações

O teste ponta a ponta do servidor, realizado em 26/10/2026, revelou que a recodificação da textura em JPEG não ocorreu nas rodadas desta seção. O pós-processamento chamava `gltf-transform jpeg` sem a opção `--formats`, e, na versão 4.5 da ferramenta, o padrão recomprime apenas texturas que já são JPEG. Assim, a textura PNG gerada pelo modelo passava intacta. Os tamanhos de GLB da tabela de presets estão, portanto, superestimados, e a comparação feita com essas rodadas, segundo a qual a compressão geométrica economizaria apenas cerca de 21%, não é mais válida. As conclusões de tempo e de geometria não se alteram.

A correção (`--formats "*"`) foi aplicada no motor do servidor e em `pipeline/postprocess.py` no repositório. Com ela, a mesma fotografia de teste passou de 2,97 MB para 0,72 MB no preset padrão e de 2,60 MB para 0,44 MB no rápido. No GLB corrigido, a textura JPEG ocupa 0,23 MB dos 0,72 MB, de modo que a geometria passa a responder pela maior parte do arquivo. Ainda falta reconstruir a imagem Docker com a correção e refazer a rodada de presets para obter as medianas definitivas. Todos os tempos foram medidos com a máquina compartilhada, e recomenda-se repeti-los numa janela ociosa da GPU.

Código e evidências: [repositório cerise-2026-gen3d (privado)](https://github.com/cerise-ufg/cerise-2026-gen3d)

## Validação dos objetos 3D gerados

Esta etapa corresponde à Atividade 4 do Objetivo 1 do plano de trabalho, que prevê o relatório de validação e os resultados experimentais. As métricas quantitativas de geometria e de aparência foram apresentadas nas subseções anteriores. Aqui, o pipeline selecionado e otimizado foi validado de três formas: testes funcionais automatizados sobre a mesma classe usada pelo servidor, carregamento dos arquivos nos visualizadores empregados pelo aplicativo e análise qualitativa, incluindo os casos de falha.

### Testes funcionais automatizados

A suíte `validation/test_pipeline.py` (pytest) gera modelos a partir de três entradas em cada preset: duas imagens RGBA do GSO (águia e caneca) e uma fotografia real com fundo (bule), que força a etapa de remoção de fundo. A suíte verifica, para cada GLB final, os critérios resumidos na tabela a seguir e inclui ainda dois testes sem GPU, do assentamento e escala e da redução de textura.

Tabela: Verificações automatizadas do pipeline empacotado (9 GLBs: 3 entradas em 3 presets)
| Verificação | Critério | Resultado |
|---|---|---|
| Validade do arquivo | Khronos glTF-Validator sem erros | aprovado |
| Material | material PBR com `baseColorTexture` | aprovado |
| Compatibilidade com o app | sem Draco, meshopt ou KTX2; textura JPEG ou PNG | aprovado |
| Orçamento de faces | até 10 mil, 20 mil e 40 mil faces conforme o preset | aprovado |
| Escala e posição | maior dimensão de 0,30 m, base em y = 0, centrado em x e z | aprovado |
| Tempo e tamanho | até 60, 90 e 180 s; até 3, 4 e 10 MB | aprovado |
| Total | rápido e padrão: 38 testes em 189,7 s; alto: 20 testes em 135,2 s | 58 de 58 aprovados |

![Saída do terminal da suíte pytest do pipeline no contêiner da estação DGX Spark: 38 testes aprovados nos presets rápido e padrão e 20 no preset alto](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/term_a4_pytest.png){w=13}

A suíte aceitava textura JPEG ou PNG e teve os limites de tamanho calibrados com a rodada de presets. Por isso, não detectou o defeito de recodificação da textura descrito na subseção anterior: os GLBs do teste tinham textura PNG. Recomenda-se exigir textura JPEG e recalibrar os limites de tamanho após a nova rodada de presets.

### Carregamento nos visualizadores

Sete GLBs finais (cinco do preset padrão, um do rápido e um do alto, com objetos do GSO e fotografias reais) foram abertos em Chromium sem interface (Playwright, com WebGL por software) numa página com o `<model-viewer>` e, em paralelo, com o `GLTFLoader` do three.js. Os sete carregaram nos dois visualizadores, sem erros no console e sem extensões glTF, com uma malha, um material com mapa de cor, a contagem de triângulos do preset, maior dimensão de 0,30 m e base em y = 0 (`resultados/viewer/viewer_report.json`). Esses arquivos são anteriores à correção da textura. O GLB corrigido, com textura JPEG, foi validado da mesma forma no teste ponta a ponta do servidor, apresentado na seção correspondente.

![GLBs finais carregados no model-viewer e no three.js em Chromium sem interface, com as estatísticas lidas pelo GLTFLoader: ônibus e pato no preset padrão, caneca no rápido e robô no alto](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a4_viewer_model_viewer.png){w=15}

### Análise qualitativa e casos de falha

As figuras a seguir mostram, no preset padrão, a entrada, os renders frontal e de três quartos e um detalhe da textura para oito objetos do GSO e para as seis fotografias reais. Essas fotografias, com licença CC0, foram obtidas no Wikimedia Commons: quatro peças do acervo aberto do Metropolitan Museum (bule de prata e estatuetas de burro, galo e gato), um bule fotografado no Victoria and Albert Museum e um pato de borracha sobre fundo complexo. Nas vistas observadas, a textura reproduz detalhes finos, como o rosto e o boné do motorista do ônibus, os cadarços e o logotipo do tênis e o padrão da caneca. A geometria preserva estruturas finas, como as pernas do cavalo e as asas da águia. Nas fotografias reais, a remoção de fundo funcionou inclusive sobre a grade metálica atrás do pato, e o pipeline produziu formas plausíveis para estatuetas cerâmicas antigas, bem diferentes dos objetos domésticos do GSO.

![Grade qualitativa do preset padrão em oito objetos do Google Scanned Objects: entrada, render frontal, render de três quartos e detalhe da textura](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a4_grade_gso_padrao.png){w=12}

![Grade qualitativa do preset padrão nas seis fotografias reais com licença CC0: entrada com fundo, render frontal, render de três quartos e detalhe da textura](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/a4_grade_fotos_reais.png){w=12}

Foram identificados os seguintes casos de falha e limitações:

- **Partes ocultas**: as faces não visíveis na foto são inferidas pelo modelo e tendem a sair mais lisas e acinzentadas, como nas costas das asas da águia. Regiões escuras ou finas podem sair pretas ou com lacunas, como nas costas do robô. O módulo de textura completo do preset alto atenua o problema (CLIP vistas novas de 0,876, contra 0,851 no padrão).
- **Materiais metálicos ou especulares**: no bule de prata, os reflexos ficam incorporados ao albedo e o aspecto metálico se perde, porque o Hunyuan3D-2 não gera materiais PBR. O Hunyuan3D-2.1 trataria esse caso com mapas de metal e rugosidade.
- **Objetos compostos**: os dados seguros pelo pato saem como peças parcialmente destacadas, e a limpeza de componentes pequenos pode remover partes legítimas com menos de 1% da área.
- **Estruturas finas nos concorrentes**: o InstantMesh colapsou as asas da águia, o que responde pela maior parte da queda do seu F-score@0,05 no subconjunto que a inclui; no TripoSR, as faces ocultas saem escuras e borradas.
- **Limitações da avaliação**: o CLIP mede semelhança visual, e não exatidão métrica; o renderizador sem sombreamento PBR subestima o Hunyuan3D-2.1; e não houve ainda teste com fotografias capturadas pelo próprio aplicativo no celular, etapa que depende da integração tratada em seção própria.

Código e evidências: [repositório cerise-2026-gen3d (privado)](https://github.com/cerise-ufg/cerise-2026-gen3d)

<!-- REFERENCIAS
[@gso]: DOWNS, L. et al. Google Scanned Objects: a high-quality dataset of 3D scanned household items. In: IEEE INTERNATIONAL CONFERENCE ON ROBOTICS AND AUTOMATION (ICRA), 2022, Filadélfia. Proceedings [...]. IEEE, 2022. arXiv:2204.11918.
[@nvdiffrast]: LAINE, S. et al. Modular primitives for high-performance differentiable rendering. ACM Transactions on Graphics, v. 39, n. 6, 2020.
[@umeyama]: UMEYAMA, S. Least-squares estimation of transformation parameters between two point patterns. IEEE Transactions on Pattern Analysis and Machine Intelligence, v. 13, n. 4, p. 376-380, 1991.
[@clip]: RADFORD, A. et al. Learning transferable visual models from natural language supervision. In: INTERNATIONAL CONFERENCE ON MACHINE LEARNING (ICML), 38., 2021. Proceedings [...]. PMLR, 2021. arXiv:2103.00020.
[@hunyuan3d2]: ZHAO, Z. et al. Hunyuan3D 2.0: scaling diffusion models for high resolution textured 3D assets generation. arXiv:2501.12202, 2025.
[@flashvdm]: LAI, Z. et al. Unleashing vecset diffusion model for fast shape generation. arXiv:2503.16302, 2025.
[@hunyuan3d21]: HUNYUAN3D TEAM. Hunyuan3D 2.1: from images to high-fidelity 3D assets with production-ready PBR material. arXiv:2506.15442, 2025.
[@trellis]: XIANG, J. et al. Structured 3D latents for scalable and versatile 3D generation. arXiv:2412.01506, 2024.
[@triposr]: TOCHILKIN, D. et al. TripoSR: fast 3D object reconstruction from a single image. arXiv:2403.02151, 2024.
[@sf3d]: BOSS, M. et al. SF3D: stable fast 3D mesh reconstruction with UV-unwrapping and illumination disentanglement. arXiv:2408.00653, 2024.
[@spar3d]: HUANG, Z. et al. SPAR3D: stable point-aware reconstruction of 3D objects from single images. arXiv:2501.04689, 2025.
[@instantmesh]: XU, J. et al. InstantMesh: efficient 3D mesh generation from a single image with sparse-view large reconstruction models. arXiv:2404.07191, 2024.
-->
