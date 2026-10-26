## Segmentação da área de atuação entre drones

Esta etapa corresponde à Atividade 13 do Objetivo 5 do plano de trabalho, que prevê o desenvolvimento de um software funcional de segmentação da área de atuação entre os drones disponíveis. O problema tratado consiste em dividir uma área poligonal georreferenciada entre uma frota possivelmente heterogênea, de modo que as aeronaves concluam a varredura em tempos próximos, e em gerar, para cada drone, uma missão de cobertura executável por um piloto automático. A validação foi exclusivamente algorítmica e em planta (2D), com um modelo cinemático simplificado e com o polígono real de uma área do Campus Samambaia; não foram realizadas simulações 3D de voo (SITL com Gazebo ou Isaac) nem voos reais nesta etapa.

### Metodologia e implementação

Foi desenvolvido o pacote Python `cerise_drones`, que recebe o polígono da área em GeoJSON, zonas proibidas com margem de segurança (10 m nos experimentos) e a descrição da frota (velocidade, autonomia, reserva de bateria de 20 %, campo de visão da câmera, altitude de 40 m e base). O planejamento é feito em coordenadas UTM, e o espaçamento `s` entre linhas de varredura corresponde a 80 % da largura da pegada da câmera em nádir (sobreposição lateral de 20 % e frontal de 70 %). Foram definidos três tipos de multirrotor com parâmetros representativos, sem correspondência com modelos comerciais: A (10 m/s, 20 min, 70° × 55°), B (6 m/s, 30 min, 70° × 55°) e C (14 m/s, 25 min, 82° × 52°).

Foram comparados quatro métodos de partição:

- **faixas ponderadas**: faixas paralelas à direção de varredura, com área proporcional ao peso de cada drone;
- **k-means + Voronoi**: células de Voronoi dos centroides de um k-means sobre pontos da área livre, atribuídas aos drones pelo método húngaro [@kuhn1955]; trata-se da linha de base clássica, sem ponderação;
- **DARP em grade** [@kapoutsis2017darp]: atribuição das células de uma grade por distância geodésica a sementes, com balanceamento iterativo até erro de área inferior a 1 % do alvo; além da pesagem multiplicativa original, foi implementada uma pesagem aditiva que gera regiões conexas por construção, com retificação das fronteiras pelo algoritmo de Douglas–Peucker [@douglas1973];
- **DARP + refinamento por tempo**, proposto neste trabalho: sementes nos centros de um k-means ponderado, pesos iniciais proporcionais à taxa de cobertura `v·s` e quatro iterações de reajuste `w ← w·(T̄/T)^0,8`, em que `T` é o tempo de missão estimado de cada drone, mantendo-se a solução de menor makespan (maior tempo de missão da frota).

Cada subárea recebe uma rota em boustrophedon [@choset2000] com a orientação de menor tempo estimado (subida, percurso, 4 s por curva e descida) e trânsito por grafo de visibilidade em torno das zonas proibidas. Uma checagem de bateria a cada 25 m insere retorno à base, troca de bateria (5 min) e retomada quando a autonomia útil não permite prosseguir. Para cada drone são exportados um plano `.plan` do QGroundControl (PX4, com waypoints, disparo da câmera por distância, retorno à base e geocerca), arquivos KML e GeoJSON e um mapa interativo. Os planos foram aprovados por um validador estrutural do formato, mas ainda não foram abertos no QGroundControl nem executados em SITL.

O benchmark utilizou o campo aberto do Campus Samambaia (polígono côncavo de 34,23 ha e 49 vértices, obtido do OpenStreetMap [@osm]) e três cenários sintéticos: convexo (96 ha), côncavo em L com uma zona proibida (43 ha) e côncavo em U com duas zonas proibidas (50 ha). Com N = 2 a 6 drones e frotas homogênea (somente tipo A) e heterogênea (tipos A, B e C alternados), foram realizadas 160 execuções, além de 70 execuções de ablação. A suíte de 16 testes automatizados (partições, balanceamento, cobertura, trocas de bateria, validade dos `.plan`, protocolo LoRa e georreferenciamento) foi aprovada integralmente.

### Resultados

A tabela a seguir resume a partição do campo aberto do Campus Samambaia entre quatro drones heterogêneos (dois do tipo A, um B e um C).

Tabela: Partição do campo aberto do Campus Samambaia (34,2 ha) entre 4 drones heterogêneos pelos quatro métodos
| Método | Makespan (min) | CV do tempo | Distância (km) | Curvas | Cobertura (%) |
|---|---|---|---|---|---|
| Faixas ponderadas | 8,63 | 0,120 | 13,36 | 56 | 100,0 |
| k-means + Voronoi | 10,63 | 0,385 | 10,65 | 70 | 100,0 |
| DARP (sementes nas bases) | 8,18 | 0,152 | 11,66 | 77 | 100,0 |
| DARP + refinamento | 6,57 | 0,002 | 11,37 | 73 | 100,0 |

No plano final (DARP + refinamento), o drone do tipo C recebeu 13,46 ha, os dois do tipo A receberam 7,07 ha e 9,20 ha e o do tipo B, 4,50 ha. Os quatro concluem a missão entre 6,54 e 6,57 min, com uso de 22 % a 33 % da bateria, e a sobreposição entre drones foi de 7,0 % das células rasterizadas. As figuras a seguir mostram a partição pelos quatro métodos e o plano final sobre imagem de satélite.

![Partição do campo aberto do Campus Samambaia entre 4 drones heterogêneos pelos quatro métodos, com as rotas em boustrophedon (linhas cheias: câmera ligada; pontilhadas: trânsito e curvas) e as bases indicadas por triângulos](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/01_ufg_comparacao_metodos.png){w=16}

![Mapa interativo do plano final (DARP + refinamento) sobre imagem de satélite, com subárea, rota e base de cada drone; legenda com área e tempo de missão por drone](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/03_ufg_mapa_folium.png){w=14}

Tabela: Médias do benchmark sobre os 4 cenários e N = 2 a 6 (20 casos por linha; vitórias = casos com o menor makespan)
| Frota | Método | Makespan médio (min) | Makespan / melhor do caso | CV do tempo | Vitórias |
|---|---|---|---|---|---|
| Homogênea | Faixas | 11,66 | 1,153 | 0,097 | 2 |
| Homogênea | k-means | 11,47 | 1,100 | 0,117 | 2 |
| Homogênea | DARP | 11,37 | 1,107 | 0,055 | 1 |
| Homogênea | DARP + ref. | 10,64 | 1,008 | 0,023 | 15 |
| Heterogênea | Faixas | 12,68 | 1,189 | 0,123 | 3 |
| Heterogênea | k-means | 15,90 | 1,504 | 0,308 | 0 |
| Heterogênea | DARP | 12,04 | 1,119 | 0,075 | 1 |
| Heterogênea | DARP + ref. | 10,96 | 1,007 | 0,028 | 16 |

O DARP com refinamento por tempo obteve o menor makespan em 31 dos 40 casos, ficou em média a 0,7–0,8 % do melhor resultado de cada caso e reduziu o coeficiente de variação (CV) dos tempos de missão para 0,023–0,028, contra 0,055–0,308 dos demais métodos. Com frota heterogênea, o k-means/Voronoi, por não ser ponderado, ficou em média 50 % acima do melhor makespan. As faixas ponderadas fizeram menos curvas (49 a 50 em média, contra 71 a 78 dos demais métodos), mas perderam em trânsito nos polígonos côncavos. A cobertura rasterizada ficou entre 99,65 % e 100 % nas 160 execuções. As medianas de tempo de execução foram de 0,4 a 1,2 s para os métodos de passo único e de 5,8 a 7,1 s para o DARP + refinamento, que executa cinco partições completas; o máximo observado (29,7 s) inclui interferência de outras tarefas no notebook compartilhado.

A ablação (cenários UFG e U, frota heterogênea, N = 2 a 6) mostrou que a pesagem multiplicativa original não convergiu no polígono real da UFG (erro máximo de área de 24,9 %, contra 0,6 % a 1,2 % da pesagem aditiva); que sementes em centros de k-means reduziram o makespan médio em relação a sementes nas bases (8,61 contra 8,67 min na UFG; 11,44 contra 12,38 min no U); e que o refinamento por tempo foi o fator de maior ganho (8,13 min na UFG e 9,89 min no U, com CV de 0,011 e 0,041).

![Makespan em função do número de drones para os quatro métodos, por cenário (colunas) e tipo de frota (linhas)](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/04_benchmark_makespan.png){w=16}

![Saída de terminal da suíte de testes do pacote cerise_drones, com os 16 testes aprovados](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/10_terminal_pytest.png){w=11}

### Discussão e limitações

Os resultados indicam que, em frotas heterogêneas, a ponderação pela capacidade de cobertura e, sobretudo, o ajuste dos pesos pelo tempo estimado de missão são determinantes para o balanceamento. As principais limitações são: (i) os tempos de missão derivam de um modelo cinemático simples (velocidade constante, penalidade fixa por curva, energia proporcional ao tempo e ausência de vento), não calibrado com voos; (ii) a validação foi feita apenas em planta, sem SITL nem voo real; e (iii) o k-means/Voronoi foi usado sem ponderação, e uma versão ponderada (diagrama de potência) reduziria a diferença em frotas heterogêneas.

Código e evidências: [repositório cerise-2026-drones-segmentacao (privado)](https://github.com/EduardoCaixeta/cerise-2026-drones-segmentacao)

## Colaboração entre drones e realocação dinâmica

Esta etapa trata dos algoritmos de colaboração entre drones previstos no plano de trabalho (Objetivo 2) e complementa a Atividade 13 do Objetivo 5. O objetivo foi tratar o abandono da missão por um drone, seja por falha, seja por retorno antecipado devido a bateria baixa, redistribuindo a área ainda não varrida entre os sobreviventes, e quantificar o custo de comunicação dessa coordenação no enlace LoRa desenvolvido no projeto. Toda a avaliação foi feita por simulação 2D, com o mesmo modelo cinemático da etapa de segmentação.

### Metodologia e implementação

O cenário de referência é o plano final da UFG com quatro drones heterogêneos (DARP + refinamento), cujo makespan sem falha é de 394 s (6,57 min). A falha é detectada pela ausência de mensagens HEARTBEAT, com atraso de 3 s. Foram comparadas três estratégias:

- **sem realocação**: a parte não varrida da subárea do drone perdido é abandonada;
- **repartição**: a área ainda não coberta por nenhum drone é repartida entre os sobreviventes a partir de suas posições atuais; cada componente conexa recebe um subconjunto de drones, escolhido por enumeração das alocações, e passa pelo DARP com refinamento pelo instante de conclusão, considerando a bateria já consumida; as novas subáreas são difundidas por mensagens AREA_ASSIGN e AREA_POLY;
- **leilão**: a área órfã é dividida em tarefas (células de 2s × 2s) distribuídas por leilão sequencial de item único com objetivo minimax [@koenig2006ssi], por meio de mensagens TASK_BID e TASK_AWARD; as tarefas ganhas são varridas após a própria subárea.

Foram simuladas 12 falhas: cada um dos quatro drones abandonando a missão a 25 %, 50 % e 75 % do seu voo.

As mensagens foram alinhadas à biblioteca `cerise_proto` v1, implementada na frente de comunicação LoRa deste plano. O módulo `cerise_drones.protocolo` codifica e decodifica os mesmos quadros byte a byte (cabeçalho de 8 B, payload de até 32 B e CRC-16/CCITT-FALSE, cujo valor de verificação 0x29B1 é conferido nos testes). Como o AREA_ASSIGN v1 descreve apenas um retângulo envolvente, insuficiente para as subáreas poligonais do DARP, foi proposta uma extensão com os tipos 7 (AREA_POLY, vértices em deslocamentos inteiros de metros, até 7 por quadro, com fragmentação), 8 (TASK_BID) e 9 (TASK_AWARD), ainda não incorporada ao firmware da frente LoRa. Os tempos no ar foram calculados pela formulação da Semtech [@semtech_an1200] (BW 125 kHz, CR 4/5, preâmbulo de 8 símbolos).

### Resultados

Tabela: Efeito do abandono de um drone no plano da UFG com 4 drones heterogêneos: área perdida sem realocação, aumento do makespan por estratégia e custo LoRa sem ACKs (4 falhas por instante)
| Instante da falha | Perda sem realocação (%) | Makespan, repartição (%) | Makespan, leilão (%) | Quadros LoRa (rep./leilão) | No ar em SF9, s (rep./leilão) |
|---|---|---|---|---|---|
| 25 % do voo | 16,7 | +33,3 | +49,2 | 20,0 / 59,8 | 5,5 / 10,5 |
| 50 % do voo | 9,5 | +18,3 | +32,2 | 15,0 / 38,5 | 4,0 / 6,8 |
| 75 % do voo | 1,4 | +17,8 | +12,2 | 8,0 / 12,8 | 2,0 / 2,3 |
| Média (12 casos) | 9,2 (máx. 26,4) | +23,1 | +31,2 | 14,3 / 37,0 | 3,8 / 6,5 |

Sem realocação, o makespan não se altera, mas em média 9,2 % da área permanece descoberta, chegando a 26,4 % quando o drone rápido do tipo C abandona a missão a 25 % do voo. As duas estratégias colaborativas recuperaram pelo menos 99,7 % de cobertura em todos os casos. A repartição teve menor aumento de makespan em 9 dos 12 casos; o leilão foi melhor em três casos, dois deles com falha a 75 % do voo, quando a área órfã é pequena e os sobreviventes não abandonam as próprias rotas, e um terceiro praticamente empatado (+75,8 % nas duas estratégias). Uma política híbrida que escolhesse a melhor das duas teria aumento médio de 20,6 %. O replanejamento levou em média 1,95 s na repartição e 0,08 s no leilão.

![Linha do tempo da realocação por repartição quando o drone D3 abandona a missão a 50 % do voo: áreas já cobertas coloridas por drone e novas subáreas tracejadas; makespan de 6,6 para 8,7 min, com 100 % de cobertura](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/06_colaboracao_linha_do_tempo.png){w=16}

![Estado final das três estratégias para a falha de D3 a 50 % do voo: sem realocação (82,8 % de cobertura), repartição (+32,2 % de makespan, 14 quadros LoRa) e leilão (+51,6 %, 58 quadros)](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/07_colaboracao_estrategias.png){w=16}

Tabela: Tamanho e tempo no ar das mensagens de coordenação (BW 125 kHz, CR 4/5)
| Mensagem | Quadro (B) | SF7 (ms) | SF9 (ms) | SF10 (ms) | Origem |
|---|---|---|---|---|---|
| HEARTBEAT | 18 | 51,5 | 185,3 | 329,7 | cerise_proto v1 |
| POS | 24 | 61,7 | 205,8 | 370,7 | cerise_proto v1 |
| AREA_ASSIGN | 32 | 71,9 | 246,8 | 452,6 | cerise_proto v1 |
| COVERAGE_DONE | 17 | 51,5 | 164,9 | 329,7 | cerise_proto v1 |
| COUNT_REPORT | 23 | 61,7 | 205,8 | 370,7 | cerise_proto v1 |
| ACK | 16 | 51,5 | 164,9 | 329,7 | cerise_proto v1 |
| AREA_POLY (7 vértices) | 42 | 87,3 | 287,7 | 534,5 | extensão proposta |
| TASK_BID | 14 | 46,3 | 164,9 | 288,8 | extensão proposta |
| TASK_AWARD | 13 | 46,3 | 164,9 | 288,8 | extensão proposta |

Em SF9, configuração padrão do firmware da frente LoRa, todos os quadros ficam abaixo do limite de 400 ms de ocupação adotado naquela frente; em SF10, AREA_ASSIGN e AREA_POLY o ultrapassam. Em média, uma repartição custou 14,3 quadros (537 B e 3,8 s no ar em SF9) e um leilão, 37,0 quadros (608 B e 6,5 s), sem contar confirmações, conforme ilustrado abaixo.

![Tempo no ar de cada mensagem em SF7, SF9 e SF10, com o limite de 400 ms, e custo médio de comunicação das estratégias de realocação em SF9 nas 12 falhas simuladas](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/08_lora_mensagens.png){w=16}

### Discussão e limitações

A repartição é mais vantajosa quando a falha ocorre cedo e a área órfã é grande, pois redistribui o trabalho de forma equilibrada e exige menos mensagens; o leilão é competitivo para áreas órfãs pequenas, o que sugere uma política híbrida. A simulação assume detecção da falha em 3 s e canal sem perdas, e o custo LoRa foi contado sem ACKs nem retransmissões. A extensão AREA_POLY, TASK_BID e TASK_AWARD ainda precisa ser incorporada ao `cerise_proto`, e a realocação não foi testada de ponta a ponta com os módulos de rádio nem em voo; a política híbrida não foi implementada.

Código e evidências: [repositório cerise-2026-drones-segmentacao (privado)](https://github.com/EduardoCaixeta/cerise-2026-drones-segmentacao)

## Detecção e contagem de pessoas em imagens aéreas

Esta etapa corresponde ao item 1 do Objetivo 5 do plano de trabalho, que trata do planejamento e da adequação de um projeto com drones para detecção e contagem de pessoas. Foram validados os pipelines de detecção e de contagem em imagens aéreas reais do conjunto público VisDrone2019-DET [@zhu2022visdrone], desenvolvido o método de agregação das contagens entre drones e levantados os requisitos de adequação das aeronaves. Não foram coletadas imagens próprias do Campus Samambaia, e a construção e a instalação do hardware embarcado permanecem pendentes.

### Dados, ambiente e treinamento

As categorias *pedestrian* e *people* do VisDrone2019-DET foram unidas em uma única classe *pessoa*. O conjunto de treino tem 6471 imagens e 106 396 pessoas; o de validação, 548 imagens e 13 969 pessoas; e o test-dev, 1610 imagens e 27 382 pessoas. As imagens de treino foram reduzidas para 960 px no lado maior, enquanto as de validação e de test-dev foram mantidas na resolução original.

O treinamento e a avaliação foram executados na estação NVIDIA DGX Spark (GB10), em um contêiner derivado da imagem NGC PyTorch 26.05 com a biblioteca Ultralytics 8.4.189 [@jocher2024yolo11], com GPU compartilhada com outros processos. O uso de memória de GPU foi limitado a 7,5 GB, e o pico medido foi de 6,5 GB. No GB10, o *autocast* em FP16 produziu valores NaN e caixas espúrias, razão pela qual treino e inferência foram realizados em FP32. O ajuste fino partiu do YOLO11s com pesos COCO, com imagens de 960 px, lote 4, otimizador AdamW (taxa de aprendizado 0,002) e limite de tempo de 0,8 h, que resultou em 5 épocas em 48,7 min. A figura a seguir mostra as perdas e o mAP de pessoa na validação ao longo das épocas.

![Curvas do ajuste fino do YOLO11s a 960 px no GB10: perdas de caixa e de classe por época e mAP50 e mAP50-95 de pessoa no conjunto de validação](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/13_deteccao_treino.png){w=15}

### Resultados de detecção e contagem

Tabela: Classe pessoa no VisDrone2019-DET (validador Ultralytics, FP32, conf 0,001, IoU 0,7)
| Modelo | Resolução (px) | Conjunto | mAP50 | mAP50-95 | Revocação |
|---|---|---|---|---|---|
| YOLO11n COCO | 960 | val | 0,274 | 0,111 | 0,285 |
| YOLO11m COCO | 960 | val | 0,433 | 0,194 | 0,401 |
| YOLO11s COCO | 1280 | val | 0,443 | 0,201 | 0,417 |
| YOLO11s COCO | 960 | val | 0,384 | 0,163 | 0,363 |
| YOLO11s ajustado | 960 | val | 0,528 | 0,220 | 0,473 |
| YOLO11s COCO | 960 | test-dev | 0,183 | 0,077 | 0,192 |
| YOLO11s ajustado | 960 | test-dev | 0,316 | 0,121 | 0,312 |

As linhas do YOLO11s a 960 px foram avaliadas com até 1000 detecções por imagem; as demais, com o padrão de 300 (nessa condição, o YOLO11s COCO a 960 px obtém mAP50 de 0,372 no val). O ajuste fino elevou o mAP50 de pessoa de 0,384 para 0,528 no val (+37 %) e de 0,183 para 0,316 no test-dev (+73 %), superando o YOLO11m COCO a 960 px e o YOLO11s COCO a 1280 px.

Para a contagem, considera-se o número de detecções com confiança acima de um limiar escolhido no val (mínimo erro absoluto médio, MAE) e aplicado ao test-dev. Detecções com centro nas regiões ignoradas da anotação do VisDrone foram descartadas, e o erro percentual absoluto médio (MAPE) foi calculado apenas sobre as imagens com pelo menos uma pessoa.

Tabela: Erro de contagem de pessoas por imagem, com limiar escolhido no val e aplicado ao test-dev
| Modelo | Limiar | MAE val | MAPE val (%) | MAE test-dev | MAPE test-dev (%) |
|---|---|---|---|---|---|
| YOLO11s COCO | 0,05 | 9,91 | 44,8 | 11,44 | 81,7 |
| YOLO11s ajustado | 0,175 | 6,91 | 31,3 | 8,76 | 61,2 |

O modelo ajustado reduziu o MAE em cerca de 30 % no val e 23 % no test-dev. O viés é de subcontagem nos dois conjuntos: o erro do total de pessoas foi de −13,8 % no val e −42,8 % no test-dev, que concentra pessoas muito pequenas e imagens noturnas. Para o modelo COCO, o mínimo do MAE ocorreu no limite inferior da grade de limiares (0,05).

![Métricas de detecção e contagem: mAP de pessoa no val para os modelos COCO (com o limite padrão de 300 detecções) e o ajustado; MAE da contagem em função do limiar (val e test-dev); e pessoas detectadas versus anotadas por imagem no test-dev](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/14_deteccao_metricas.png){w=16}

![Exemplos do VisDrone val com as detecções do modelo ajustado (limiar 0,175) e as contagens real e detectada por imagem](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/15_deteccao_exemplos.png){w=15}

Com lote 1, FP32 e 150 imagens pré-carregadas, o YOLO11s ajustado atingiu 25,5 imagens/s de ponta a ponta a 960 px (39,2 ms por imagem, dos quais 18,2 ms de inferência) e 31,0 imagens/s a 640 px; a 960 px, o YOLO11n atingiu 28,8 imagens/s e o YOLO11m, 12,9. CPU e GPU estavam compartilhadas com outros processos. Nos planos exportados para a UFG, um drone do tipo A dispara uma foto a cada 12,5 m a 10 m/s (0,8 foto/s), e a soma para os quatro drones é de cerca de 3,3 fotos/s; a vazão medida é cerca de 8 vezes superior, o que permite processar as imagens de vários drones em uma única estação de solo.

![Saída de terminal da avaliação no DGX Spark: mAP dos modelos, erro de contagem e vazão em imagens por segundo](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/evidencias/16_terminal_avaliacao_spark.png){w=15}

### Agregação das contagens entre drones

Como as subáreas são disjuntas, a contagem total é a soma das contagens de cada subárea, desde que cada pessoa seja contada uma única vez. O método implementado (`cerise_drones.agregacao`) georreferencia cada detecção pela posição, altitude e rumo do drone no instante da foto (câmera em nádir e terreno plano); atribui a detecção apenas ao drone dono da subárea em que o ponto cai (regra de posse); agrupa detecções a menos de um raio `r` para eliminar repetições causadas pela sobreposição entre fotos; e, em uma faixa de fronteira de largura `max(3 m, 2r)`, faz o agrupamento entre drones, que trocariam as detecções de borda por mensagens COUNT_REPORT.

A lógica foi validada apenas por simulação, com 348 pessoas sintéticas estáticas (300 distribuídas uniformemente e 6 grupos de 8 sobre as fronteiras) no plano da UFG, com 619 fotos e ruído de georreferenciamento σ. Com detector ideal, σ = 0,8 m e r = 3 m, a soma ingênua superestimou a contagem em 300,5 %, a deduplicação sem regra de posse em 6,8 ± 3,4 %, e o método proposto errou −1,1 ± 1,8 %. A regra de posse deslocou a estimativa para baixo em 7 a 20 pontos percentuais em todas as configurações simuladas, o que reduz o erro quando há sobrecontagem, mas acentua a subcontagem quando o raio é grande em relação a σ (com σ = 0,3 m e r = 2 m, de +4,0 % para −6,8 %). Com a revocação e a precisão medidas (0,473 e 0,638) e falsos positivos independentes entre fotos, hipótese pessimista, o erro foi de +102,7 %, dominado pelos falsos positivos.

### Requisitos para a adequação dos drones

A adequação física dos drones não foi executada por depender de hardware. Além do módulo LoRa descrito na seção da frente de comunicação, foram levantados como requisitos: câmera em nádir com pelo menos 12 MP (resolução no solo inferior a 1,5 cm/pixel a 40 m) e disparo por distância; processamento das imagens na estação de solo após o pouso, cenário validado nesta etapa, ou em computador embarcado, o que exige revisar massa e autonomia; e GNSS com correção RTK ou PPK, pois um erro de georreferenciamento menor permite raios de deduplicação de 1 a 2 m.

### Discussão e limitações

O ajuste fino foi curto (5 épocas) e o VisDrone contém majoritariamente imagens oblíquas de cenas urbanas, distintas das imagens em nádir a 40 m previstas para o campus; o mAP50 de 0,316 e a subcontagem de 42,8 % no test-dev indicam limites de generalização. O FP16 não pôde ser usado no GB10 com a versão de PyTorch empregada. A agregação foi validada apenas com pessoas sintéticas e estáticas, e o resultado com o detector medido indica a necessidade de confirmação multivista ou de calibração da contagem antes do uso operacional. Os próximos passos incluem coletar e anotar imagens próprias do campus e treinar por mais épocas.

Código e evidências: [repositório cerise-2026-drones-segmentacao (privado)](https://github.com/EduardoCaixeta/cerise-2026-drones-segmentacao)

<!-- REFERENCIAS
[@kapoutsis2017darp]: KAPOUTSIS, A. C.; CHATZICHRISTOFIS, S. A.; KOSMATOPOULOS, E. B. DARP: divide areas algorithm for optimal multi-robot coverage path planning. Journal of Intelligent & Robotic Systems, v. 86, n. 3-4, p. 663-680, 2017.
[@choset2000]: CHOSET, H. Coverage of known spaces: the boustrophedon cellular decomposition. Autonomous Robots, v. 9, n. 3, p. 247-253, 2000.
[@kuhn1955]: KUHN, H. W. The Hungarian method for the assignment problem. Naval Research Logistics Quarterly, v. 2, n. 1-2, p. 83-97, 1955.
[@douglas1973]: DOUGLAS, D. H.; PEUCKER, T. K. Algorithms for the reduction of the number of points required to represent a digitized line or its caricature. Cartographica, v. 10, n. 2, p. 112-122, 1973.
[@osm]: OPENSTREETMAP CONTRIBUTORS. OpenStreetMap. Dados disponibilizados sob a licença Open Database License (ODbL). Disponível em: https://www.openstreetmap.org. Acesso em: 26 out. 2026.
[@koenig2006ssi]: KOENIG, S. et al. The power of sequential single-item auctions for agent coordination. In: NATIONAL CONFERENCE ON ARTIFICIAL INTELLIGENCE (AAAI-06), 21., 2006, Boston. Proceedings [...]. Menlo Park: AAAI Press, 2006. p. 1625-1629.
[@semtech_an1200]: SEMTECH CORPORATION. AN1200.13: LoRa Modem Designer's Guide. Camarillo: Semtech, 2013.
[@zhu2022visdrone]: ZHU, P. et al. Detection and tracking meet drones challenge. IEEE Transactions on Pattern Analysis and Machine Intelligence, v. 44, n. 11, p. 7380-7399, 2022.
[@jocher2024yolo11]: JOCHER, G.; QIU, J. Ultralytics YOLO11. Versão 11.0.0, 2024. Disponível em: https://github.com/ultralytics/ultralytics.
-->
