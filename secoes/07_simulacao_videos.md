## Validação da contagem em vídeos reais de drone

A etapa anterior mediu o detector YOLO11s ajustado em imagens estáticas. A missão de contagem no Campus Samambaia, porém, produz vídeo, e nele a mesma pessoa aparece em dezenas de quadros. Por isso, esta atividade mediu em vídeo aéreo real, com gabarito de identidades: o erro da contagem por quadro; o erro da contagem de pessoas distintas obtida pelos identificadores (IDs) de um rastreador multiobjeto; as métricas padronizadas de rastreamento da classe pessoa; e a vazão do pipeline na estação NVIDIA DGX Spark (GB10).

### Dados e metodologia

Foram usadas as partições val (7 sequências, 2.846 quadros) e test-dev (17 sequências, 6.635 quadros, gabarito público) do VisDrone2019-MOT [@zhu2022visdrone], obtidas dos links oficiais e conferidas por SHA-256. A classe pessoa reúne `pedestrian` e `people`, e as regiões marcadas como ignoradas são excluídas, como no protocolo do conjunto. O test-dev contém 1.012 pessoas distintas em cenas majoritariamente oblíquas e urbanas, com resoluções de 680×382 a 3840×2160 e de 1 a 109 pessoas por quadro.

Foram avaliados quatro detectores em FP32: o YOLO11s ajustado no VisDrone-DET, a 960 e a 1280 px, e o YOLO11s com pesos COCO nas mesmas resoluções, como referência [@jocher2024yolo11]. As detecções foram calculadas uma vez e guardadas em cache, com confiança mínima de 0,01. Sobre elas rodaram, sem modificação de código, os rastreadores do Ultralytics: ByteTrack [@zhang2022bytetrack] e BoT-SORT [@aharon2022botsort], este com compensação de movimento de câmera (GMC, fluxo óptico esparso) e sem reidentificação por aparência.

Todas as escolhas foram feitas apenas no val e aplicadas sem alteração ao test-dev:

- a grade de limiares do rastreador (1.904 execuções), pelo maior HOTA;
- o limiar da contagem por quadro, pelo menor erro absoluto médio (MAE);
- o comprimento mínimo de trilha L da contagem de IDs, pelo menor erro relativo.

Para o detector ajustado a 960 px com BoT-SORT, a configuração escolhida foi `track_high_thresh` = `new_track_thresh` = 0,40, `track_low_thresh` = 0,05 e `track_buffer` de 30 quadros. As métricas HOTA [@luiten2021hota], MOTA [@bernardin2008clear] e IDF1 [@ristani2016idf1] foram reimplementadas seguindo o TrackEval [@luiten2020trackeval]. A implementação foi conferida com casos sintéticos e com o py-motmetrics em 72 pares sequência × combinação: o IDF1 coincidiu e a diferença máxima de MOTA foi de 0,0026.

### Resultados

Tabela: Rastreamento e contagem de pessoas no VisDrone2019-MOT test-dev (16 sequências com pessoas; 1.012 pessoas distintas), com as configurações escolhidas no val; IDs brutos = trilhas com L = 1
| Combinação | HOTA | IDF1 | MOTA | Trocas de ID | MAE por quadro (trilhas) | IDs brutos | IDs com ≥ L quadros |
|---|---|---|---|---|---|---|---|
| Ajustado 960 + ByteTrack | 0,286 | 0,339 | 0,095 | 1.639 | 8,46 | 2.684 | 500 (L = 60) |
| Ajustado 960 + BoT-SORT | 0,328 | 0,399 | 0,092 | 974 | 7,46 | 2.095 | 584 (L = 60) |
| Ajustado 960 + BoT-SORT sem GMC | 0,289 | 0,343 | 0,094 | 1.589 | — | 2.639 | — |
| COCO 1280 + BoT-SORT | 0,328 | 0,406 | 0,214 | 444 | 11,14 | 1.173 | 599 (L = 30) |

As duas melhores combinações empataram em HOTA (0,328), por caminhos opostos. O detector ajustado recupera mais pessoas pequenas (revocação de detecção de 0,358 contra 0,278), mas tem menor precisão (0,458 contra 0,574), o que derruba o MOTA. O BoT-SORT superou o ByteTrack em todas as combinações (+0,035 a +0,042 de HOTA). A ablação atribui essa vantagem à GMC: sem ela, o HOTA do ajustado cai de 0,328 para 0,289 e as trocas de ID sobem de 974 para 1.589. Na contagem por quadro, com média de 20,8 pessoas anotadas por quadro, as trilhas do ajustado com BoT-SORT tiveram MAE de 7,46 e viés de −4,52. Todos os estimadores subcontam, sobretudo em multidões.

![HOTA, IDF1 e MOTA, MAE da contagem por quadro e erro da contagem de pessoas únicas no VisDrone2019-MOT test-dev para as oito combinações detector × rastreador](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/validacao_videos/evidencias/v02_metricas_agregadas.png){w=14}

O resultado central para a missão é que contar IDs do rastreador não é contar pessoas. Com o ajustado e o BoT-SORT, os 2.095 IDs brutos (+107 % em relação às 1.012 pessoas) decompõem-se em:

- 861 IDs falsos, isto é, trilhas curtas sobre falsos positivos;
- 1.234 IDs associados a 816 pessoas, o que corresponde a 418 IDs extras por troca ou fragmentação.

Outras 196 pessoas nunca foram rastreadas. O filtro por comprimento mínimo troca inflação por subcontagem: com L = 60, o total cai para 584 (−42 %). O melhor resultado sem vazamento, do COCO a 960 px com L = 10, ainda tem 29 % de erro relativo médio por sequência.

![Pessoas únicas por sequência do test-dev (gabarito, IDs brutos e IDs com ≥ L quadros) e decomposição dos IDs brutos em IDs falsos, IDs extras por troca ou fragmentação e pessoas nunca rastreadas](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/validacao_videos/evidencias/v03_contagem_unica.png){w=14}

A escala da pessoa na imagem, que funciona como indicador da altitude, foi o fator mais associado ao desempenho, com correlação de Spearman ρ = 0,62 (p = 0,011) entre a altura mediana e o HOTA. A revocação do ajustado foi de 12 % abaixo de 20 px de altura, 30 % entre 20 e 40 px, 56 % entre 40 e 80 px e 66 % acima de 80 px; para o COCO, os valores foram 2 %, 15 %, 43 % e 75 %. O ajuste no VisDrone compensa justamente a faixa de pessoas pequenas de uma missão em nádir a 40 m. Quanto à vazão, o pipeline com BoT-SORT rodou a 23,0 quadros/s em 4K e a 68,9 quadros/s em 1344×756, com no máximo 0,33 GB de GPU.

![Revocação por faixa de altura da pessoa e natureza dos falsos positivos do rastreador no test-dev (ajustado 960 × COCO 1280, com BoT-SORT)](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/validacao_videos/evidencias/v14_analise_erros.png){w=14}

Três decisões foram levadas para a simulação: usar o detector ajustado com BoT-SORT e GMC; tratar as trilhas apenas como agregadoras de uma mesma passagem; e fazer a contagem única pela posição projetada no solo, não pelos IDs. Como limitações, o VisDrone2019-MOT é oblíquo, urbano e filmado a baixa altura, ao passo que a missão da UFG é em nádir sobre um campus. Além disso, o val tem só 7 sequências e o TrackEval original não foi executado.

Código e evidências: [repositório cerise-2026-drones-segmentacao (privado)](https://github.com/EduardoCaixeta/cerise-2026-drones-segmentacao)

## Simulação 3D de drones contando pessoas

Para fechar o ciclo entre a partição da área, o detector e a validação em vídeo, foi construída uma simulação fotorrealista no NVIDIA Isaac Sim 5.1 [@nvidia2025isaacsim], executada sem tela (headless) no DGX Spark. A cena reproduz um recorte de 11,27 ha da área aberta da UFG, com terreno, caminhos, 14 edifícios esquemáticos e 78 árvores gerados a partir do polígono do OpenStreetMap. Quatro drones percorrem as rotas DARP + refinamento [@kapoutsis2017darp] da frota heterogênea, em nádir a 40 m (1280×960, campo de visão horizontal de 70°). Na cena caminham **80 pessoas animadas**: caminhantes, grupos andando ou parados e pessoas que cruzam as fronteiras entre subáreas.

As pessoas usam os personagens e o comportamento do `omni.anim.people`, e seguem os comandos do plano sobre uma navmesh. O Replicator grava, a 5 fps, por câmera: RGB, caixas 2D de gabarito e a pose; o gabarito de posição é a posição real de cada personagem. A licença foi aceita pelo bolsista, sem telemetria, e os ativos oficiais (0,55 GB) foram espelhados localmente. Nada foi exposto à rede externa.

Os testes de fumaça revelaram duas falhas de API, ambas corrigidas:

- o esqueleto `biped_demo` ausente impedia o grafo de animação;
- o volume da navmesh ficava restrito a ±4,5 m da origem, o que fazia as pessoas andarem em linha reta.

Depois das correções, as caixas do Replicator coincidiram com a projeção do gabarito pela pose, com erro mediano de 2,8 px. O voo a 40 m (866 instantes × 5 câmeras, incluindo a visão geral) levou 21,0 min, ou 1,46 s por instante. Ele ocupou ~18 a 21 GB de memória unificada e manteve sempre mais de 24 GB livres no Spark. Foi feito também um voo a 30 m (1.001 instantes). O maior lado mediano das caixas de gabarito foi de 21 px a 40 m e de 31 px a 30 m.

![Cena renderizada no Isaac Sim: visão geral com os quatro drones e câmera do D4 em nádir a 40 m com as caixas de gabarito do Replicator](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/simulacao/evidencias/sim_09_cena_render.png){w=14}

A contagem usa o YOLO11s ajustado (FP32, 1280 px) e projeta cada trilha no solo com a pose da câmera. Em seguida, aplica a posse da subárea, com faixa de fronteira de 6 m, e a deduplicação espaço-temporal pela posição. O detector localiza bem as pessoas simuladas: AP de 0,702 a IoU 0,5 a 40 m e de 0,652 a 30 m. As pontuações, porém, ficaram baixas no domínio simulado: no limiar 0,40 a precisão é de 0,998 e a revocação, de 0,230. O detector roda a 82 a 89 FPS, ou 56 a 60 FPS com leitura e GMC.

Tabela: Contagem única global na simulação contra as pessoas distintas vistas no gabarito (79 a 40 m; 73 a 30 m)
| Voo | Rastreador + deduplicação no solo | Contagem | Erro | Corretos | Duplicatas | Perdidas |
|---|---|---|---|---|---|---|
| 40 m | BoT-SORT recomendado pelos vídeos reais (pré-registrado) | 34 | −57,0 % | 30 | 4 | 49 |
| 40 m | Rastreador próprio no solo (pré-registrado) | 88 | +11,4 % | 68 | 20 | 11 |
| 40 m | BoT-SORT sem `fuse_score`, limiar 0,15 (escolhido neste voo) | 78 | −1,3 % | 65 | 13 | 14 |
| 30 m | BoT-SORT recomendado | 29 | −60,3 % | 29 | 0 | 44 |
| 30 m | Rastreador próprio no solo | 94 | +28,8 % | 61 | 33 | 12 |
| 30 m | BoT-SORT sem `fuse_score`, limiar 0,15 (teste) | 70 | −4,1 % | 54 | 16 | 19 |

Os resultados se resumem em três pontos:

- **Deduplicação.** A soma ingênua das detecções dá 1.306 para 79 pessoas, o que confirma que a deduplicação no solo é indispensável. Nenhuma configuração produziu clusters falsos.
- **Transferência da configuração dos vídeos reais.** A configuração recomendada subconta 57 % a 60 % porque o `fuse_score` padrão multiplica a IoU pela pontuação da detecção: com pontuações baixas, as trilhas novas não se confirmam. Sem GMC, nada é rastreado, pois a imagem se desloca de 28 a 71 px por quadro.
- **Configuração calibrada.** Escolhida a posteriori no voo a 40 m, ela errou −4,1 % no voo a 30 m. Esse total próximo do correto, contudo, vem da compensação entre 16 duplicatas e 19 perdidas.

As duplicatas vêm sobretudo do mesmo drone, por pessoas andando que são revistas na faixa seguinte da varredura. A posse e a faixa de fronteira limitaram as duplicatas entre drones a 2 ou 3 por voo.

![Recortes das câmeras dos drones a 40 m com acertos, pessoas perdidas e falsos positivos; verde = gabarito do Replicator, vermelho = trilha](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/simulacao/evidencias/sim_10_deteccoes_vs_gabarito.png){w=14}

![Mapa da contagem única no voo a 40 m: subáreas de posse, rotas, clusters corretos, duplicatas e pessoas não contadas](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/simulacao/evidencias/sim_11_mapa_posse_dedup.png){w=14}

![Sensibilidade da contagem única ao limiar do BoT-SORT (com e sem fuse_score) e à confiança mínima do rastreador no solo, a 40 m e a 30 m](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/DRONES_SEGMENTACAO/simulacao/evidencias/sim_15_sensibilidade_rastreador.png){w=14}

Um vídeo H.264 de 57,7 s acompanha a seção. Ele mostra a visão geral com os drones em voo e as pessoas caminhando, além das câmeras dos drones com caixas, contagem atual e contagem acumulada.

O cenário completo (34,2 ha, 120 pessoas) não foi renderizado. A assadura da navmesh de 1.330 × 998 m consumiu mais de 34 GB em ~22 s e provocou um OOM do sistema, apesar de o vigia de memória ter interrompido o contêiner. O OOM reiniciou o worker do servidor 3D, que voltou sozinho; os serviços de produção não foram afetados. Os scripts passaram a impor limite de memória ao contêiner e um vigia mais rápido.

Ficam como limitações o terreno procedural, a atitude ideal dos drones (sem vento, borrão ou erro de pose), a velocidade fixa de caminhada, a diferença de domínio das pontuações do detector, apenas dois voos e a altitude confundida com o plano de voo. O plano B com Gazebo e PX4 SITL não foi necessário. Os próximos passos são:

- calibrar ou ajustar o detector com imagens sintéticas;
- repetir o cenário completo com a navmesh por subárea;
- validar em voo real no campus.

Código e evidências: [repositório cerise-2026-drones-segmentacao (privado)](https://github.com/EduardoCaixeta/cerise-2026-drones-segmentacao)

<!-- REFERENCIAS
[@zhu2022visdrone]: ZHU, P. et al. Detection and tracking meet drones challenge. IEEE Transactions on Pattern Analysis and Machine Intelligence, v. 44, n. 11, p. 7380-7399, 2022.
[@jocher2024yolo11]: JOCHER, G.; QIU, J. Ultralytics YOLO11. Versão 11.0.0, 2024. Disponível em: https://github.com/ultralytics/ultralytics.
[@zhang2022bytetrack]: ZHANG, Y. et al. ByteTrack: multi-object tracking by associating every detection box. In: EUROPEAN CONFERENCE ON COMPUTER VISION (ECCV), 17., 2022, Tel Aviv. Proceedings [...]. Cham: Springer, 2022. p. 1-21. (Lecture Notes in Computer Science, v. 13682).
[@aharon2022botsort]: AHARON, N.; ORFAIG, R.; BOBROVSKY, B.-Z. BoT-SORT: robust associations multi-pedestrian tracking. arXiv:2206.14651, 2022. Disponível em: https://arxiv.org/abs/2206.14651.
[@luiten2021hota]: LUITEN, J. et al. HOTA: a higher order metric for evaluating multi-object tracking. International Journal of Computer Vision, v. 129, n. 2, p. 548-578, 2021.
[@luiten2020trackeval]: LUITEN, J.; HOFFHUES, A. TrackEval. 2020. Disponível em: https://github.com/JonathonLuiten/TrackEval. Acesso em: 26 out. 2026.
[@bernardin2008clear]: BERNARDIN, K.; STIEFELHAGEN, R. Evaluating multiple object tracking performance: the CLEAR MOT metrics. EURASIP Journal on Image and Video Processing, v. 2008, art. 246309, 2008.
[@ristani2016idf1]: RISTANI, E. et al. Performance measures and a data set for multi-target, multi-camera tracking. In: EUROPEAN CONFERENCE ON COMPUTER VISION (ECCV) WORKSHOPS, 2016, Amsterdam. Proceedings [...]. Cham: Springer, 2016. p. 17-35.
[@nvidia2025isaacsim]: NVIDIA CORPORATION. NVIDIA Isaac Sim. Versão 5.1.0. Santa Clara: NVIDIA, 2025. Plataforma de simulação robótica baseada no Omniverse, com as extensões omni.anim.people e omni.replicator. Disponível em: https://developer.nvidia.com/isaac/sim. Acesso em: 26 out. 2026.
[@kapoutsis2017darp]: KAPOUTSIS, A. C.; CHATZICHRISTOFIS, S. A.; KOSMATOPOULOS, E. B. DARP: divide areas algorithm for optimal multi-robot coverage path planning. Journal of Intelligent & Robotic Systems, v. 86, n. 3-4, p. 663-680, 2017.
-->
