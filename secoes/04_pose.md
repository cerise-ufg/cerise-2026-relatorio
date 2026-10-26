## Aplicação do modelo de estimação de pose de 2025 ao novo dataset

Esta etapa corresponde à Atividade 8 do Objetivo 3, que previa obter resultados quantitativos da execução do modelo de detecção de pose do ano anterior sobre o novo conjunto de dados da Atividade 7. Esse conjunto foi produzido em simulação (Gazebo/ROS 2) com o braço servo6dof, de cinco juntas rotacionais e garra, observado por duas câmeras fixas (frontal e diagonal), e reúne 5.000 poses com imagens RGB 1280×720 e os ângulos reais das juntas. O modelo de 2025 estima a pose do braço a partir de uma única imagem RGB, sem acesso aos estados das juntas, e segue a arquitetura HPE (*Real-time Holistic Robot Pose Estimation with Unknown States*) [@hpe], acrescida de um ramo de profundidade monocular baseado no Depth Anything V2 [@depthanythingv2]. No relatório de dezembro de 2025, esse modelo atingiu 75,4% de acurácia ADD com limiar de 60 mm no robô Panda, no conjunto real DREAM com câmera RealSense [@dream].

### Metodologia e implementação

O experimento final de 2025 foi identificado nos registros de treino (`MyNet/experiments/panda/realsense_full`): os 75,4% correspondem ao registro da época 355, com AUC-ADD de 0,547. Como o script de 2025 guardava apenas o melhor AUC e o último estado, os pesos dessa época não existem; a transferência partiu do estado final salvo do mesmo treino (`checkpoint.pk`, 111,2 milhões de parâmetros). A arquitetura combina uma rede de profundidade da raiz (DepthNet, HRNet-W32 [@hrnet]) fundida com a profundidade relativa do Depth Anything V2, um ramo integral com mapas de calor 3D (ResNet-50 [@resnet]), a regressão iterativa dos ângulos e da rotação da raiz e uma cinemática direta diferenciável.

O código, escrito para o Google Colab, foi portado para um contêiner derivado da imagem PyTorch da NVIDIA na estação NVIDIA DGX Spark (GB10, aarch64), sem reimplementação e com compatibilidade de pesos. Foram corrigidos dois defeitos do código de 2025: (i) a profundidade da raiz era calculada depois da camada integral, de modo que os keypoints desse ramo não a incluíam, o que explica as métricas zeradas do ramo integral nos registros de 2025; (ii) o laço de treino chamava `optimizer.step()` duas vezes por iteração. A adaptação ao servo6dof envolveu:

- cinemática direta diferenciável da cadeia do servo6dof, obtida do URDF gerado por `xacro`, no lugar da cinemática do Panda;
- 7 keypoints (base, origens das cinco juntas e centro da garra), o mesmo número do Panda, o que permitiu reaproveitar a camada final dos mapas de calor; cinco juntas estimadas (a abertura da garra não é estimada);
- faixa de profundidade dos mapas de calor 3D ampliada de 1,3 m para 3,0 m, pois o braço tem cerca de 2,0 m de alcance, aproximadamente 2,4 vezes o do Panda.

A geometria das câmeras, lida do mundo da simulação, foi verificada projetando sobre as imagens os keypoints calculados por cinemática direta com os ângulos reais, conforme ilustrado abaixo: numa amostra de 300 poses, 99,9% (frontal) e 99,6% (diagonal) dos keypoints dentro do quadro recaem sobre a máscara de segmentação do robô.

![Verificação da geometria: keypoints e esqueleto obtidos por cinemática direta do URDF com os ângulos reais, projetados com as poses e intrínsecos das câmeras sobre imagens do dataset; em magenta, a máscara de segmentação do robô](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/verificacao_geometria_overlay.png){w=12}

A divisão treino/validação/teste foi feita por pose, na proporção 80/10/10 (4.000/500/500 poses, ou 8.000/1.000/1.000 imagens), mantendo as duas câmeras de uma pose no mesmo subconjunto. Em vez do recorte pela caixa dos keypoints verdadeiros do protocolo DREAM de 2025, adotou-se um recorte fixo por câmera, calculado só com o treino e redimensionado para 256×256, de modo que teste e inferência não dependem do gabarito.

Foram aplicadas as etapas da metodologia de 2025 compatíveis com dados sintéticos rotulados. Na etapa 1, a DepthNet foi treinada por 5 épocas sobre as 3.151 poses de treino já disponíveis naquele momento (subconjunto do split final), atingindo, com os pesos de 2025, erro de profundidade da raiz de 71 mm na validação. Na etapa 2, o modelo completo foi treinado com taxa 1e-4 decaindo 0,9 por época, lote 32 e as augmentations fotométricas de 2025. A etapa 3 de 2025, autossupervisionada com imagens reais, não se aplica, pois ainda não há imagens reais do braço. Foram comparadas duas inicializações: a **transferência**, em que 98,1% dos parâmetros (109,1 M de 111,2 M) vieram do modelo de 2025 e apenas as camadas do regressor que dependem do número de juntas (8 para 5) foram reinicializadas; e um **baseline** com backbones pré-treinados no ImageNet. A transferência recebeu 20 épocas (cerca de 62 min); o baseline, re-executado isoladamente depois que uma tentativa em paralelo foi abortada por falta de memória na estação (compartilhada com serviços em produção), parou pelo limite de tempo após 12 épocas (cerca de 52 min).

A figura a seguir mostra as curvas por época. Com os pesos de 2025, o erro 3D na validação caiu de 262 mm (época 1) para 54,1 mm (época 20). Na época 12, a transferência tinha erro 3D de validação de 65,0 mm contra 83,7 mm do baseline e acurácia@60 mm de 59,1% contra 34,9%, com MAE das juntas semelhante (13,1° contra 12,8°).

![Etapa 2: perda total de treino e métricas de validação por época (erro 3D, MAE das juntas e PCK a 10 px) para a transferência dos pesos de 2025 e para o baseline ImageNet](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/curvas_treino.png){w=16}

![Saída de terminal do treino da etapa 2 (transferência) na estação NVIDIA DGX Spark, com a fração de parâmetros carregados do modelo de 2025 e as métricas de validação por época](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/print_treino_transfer.png){w=14}

### Resultados no conjunto de teste

A tabela a seguir resume as métricas no teste (500 poses × 2 câmeras), não usado no treino nem na escolha do checkpoint, feita pela validação.

Tabela: Resultados no conjunto de teste do servo6dof (1.000 imagens)
| Métrica | Transferência (pesos 2025) | Baseline (ImageNet) |
|---|---|---|
| MAE médio das 5 juntas (°) | 12,68 | 13,51 |
| Erro 3D médio dos keypoints (mm) | 58,7 | 88,3 |
| Erro 3D mediano dos keypoints (mm) | 41,1 | 65,7 |
| AUC-ADD 0–100 mm | 0,471 | 0,265 |
| Acurácia ADD@60 mm (%) | 68,0 | 32,8 |
| Acurácia ADD@100 mm (%) | 91,2 | 69,7 |
| Acurácia ADD@150 mm (%) | 96,7 | 90,2 |
| Erro 2D médio (px, imagem 1280×720) | 12,0 | 17,7 |
| PCK@10 px por keypoint (%) | 61,7 | 43,6 |
| Épocas de treino | 20 | 12 |

O modelo de 2025 adaptado ao servo6dof atingiu MAE de 12,68° nas cinco juntas, erro 3D médio de 58,7 mm (mediana de 41,1 mm) e acurácia@60 mm de 68,0%. Em relação ao baseline, o erro 3D médio caiu cerca de 34% e a acurácia@60 mm mais que dobrou, enquanto o MAE melhorou menos (13,51° para 12,68°). Como o baseline teve menos épocas, a comparação de mesmo orçamento é a da validação na época 12, que confirma a vantagem da transferência na precisão 3D. Exemplos de predições no teste são apresentados abaixo.

![Predições do modelo de transferência (vermelho) e verdade obtida por cinemática direta com as juntas reais (verde) sobre imagens do teste nas duas câmeras, para poses nos percentis 25, 50 e 75 do erro 3D](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/predicoes_vs_gt_transfer.png){w=16}

A tabela seguinte coloca lado a lado os resultados de 2025 e de 2026, que **não são diretamente comparáveis**: robôs, escala, câmeras e dados diferem. Como o servo6dof tem cerca de 2,4 vezes o alcance do Panda, 60 mm correspondem a aproximadamente 3% do alcance, contra cerca de 7% no Panda; as câmeras ficam a cerca de 3,6 m (frontal) e 4,4 m (diagonal) da base; os dados de 2026 são sintéticos, o recorte não usa o gabarito, não houve etapa autossupervisionada e o MAE se refere a conjuntos de juntas distintos. Com limiar proporcional ao tamanho do robô (cerca de 140 mm), a acurácia@150 mm é de 96,7%.

Tabela: Acurácia@60 mm em 2025 (Panda) e 2026 (servo6dof); robôs, escalas, câmeras e dados diferentes
| Modelo | Robô / dados | ADD@60 mm (%) | AUC-ADD | MAE (°) |
|---|---|---|---|---|
| RoboPose [@robopose] | Panda / DREAM real | 74,3 | — | — |
| HPRE | Panda / DREAM real | 75,2 | — | — |
| Modelo de 2025 (HPE + DA-V2) | Panda / DREAM real | 75,4 | 0,547 | 11,58 |
| Modelo de 2025 com transferência | servo6dof / sintético | 68,0 | 0,471 | 12,68 |
| Mesma arquitetura, ImageNet | servo6dof / sintético | 32,8 | 0,265 | 13,51 |

Os valores de RoboPose e HPRE reproduzem os do relatório de 2025; os do modelo de 2025 foram conferidos no arquivo de resultados do treino de 2025. As principais limitações desta etapa são: dados exclusivamente sintéticos; uso do estado final do treino de 2025 em vez dos pesos da época de 75,4%; baseline com menos épocas que a transferência; etapa 1 treinada num subconjunto (o modelo final e as avaliações usaram o dataset completo); e orçamento de treino de cerca de uma hora em GPU compartilhada.

Código e evidências: [repositório cerise-2026-pose-servo6dof (privado)](https://github.com/cerise-ufg/cerise-2026-pose-servo6dof)

## Avaliação de precisão e robustez do modelo de pose

Esta etapa corresponde à Atividade 9 do Objetivo 3, que previa avaliar o modelo de detecção de pose quanto à precisão e à robustez no novo cenário. Avaliou-se o modelo de 2025 adaptado ao servo6dof por transferência (Atividade 8), comparando-o, quando pertinente, ao baseline com inicialização ImageNet. Todas as medições foram feitas sobre os dados sintéticos do servo6dof.

### Protocolo de avaliação

A avaliação usou o conjunto de teste (1.000 imagens), nunca visto no treino nem usado na seleção do checkpoint, e compreendeu:

- erro absoluto médio (MAE) por junta, em graus, entre os ângulos estimados e os reais;
- erro 3D dos keypoints no referencial da câmera (média e mediana) e acurácia ADD, isto é, a fração de imagens cujo erro 3D médio dos 7 keypoints é menor ou igual a um limiar, com AUC-ADD entre 0 e 100 mm calculado com a mesma implementação do código de 2025;
- PCK 2D a 5, 10 e 20 px na imagem original 1280×720;
- generalização entre câmeras, com um modelo treinado apenas com a câmera frontal e testado nas duas;
- robustez a sete perturbações da imagem de entrada, em três ou quatro severidades cada, num subconjunto fixo de 400 imagens do teste, com a profundidade do Depth Anything V2 recalculada sobre a imagem perturbada (pipeline completo); exemplos das perturbações são mostrados na figura a seguir;
- latência de inferência com lote 1 na GPU GB10, compartilhada com outros serviços.

![Exemplos das perturbações aplicadas ao recorte de entrada de 256×256 px nos testes de robustez: ruído gaussiano, desfoque de movimento, brilho, contraste, oclusão, compressão JPEG e resolução reduzida](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/amostras_perturbacoes.png){w=16}

### Precisão por junta, por keypoint e por câmera

Tabela: Erro por junta no conjunto de teste
| Junta | Transferência: MAE (°) | Transferência: mediana (°) | Baseline: MAE (°) |
|---|---|---|---|
| joint_1 (base) | 4,19 | 2,94 | 7,20 |
| joint_2 (ombro) | 3,04 | 1,89 | 3,87 |
| joint_3 (cotovelo) | 3,91 | 2,54 | 5,41 |
| joint_4 (punho) | 10,52 | 6,64 | 9,25 |
| joint_5 (rotação da garra) | 41,73 | 42,49 | 41,83 |

As juntas 1 a 3 (base, ombro e cotovelo) são estimadas com MAE entre 3,0° e 4,2° e a junta 4 (punho) com 10,5°. A junta 5, rotação da garra em torno do eixo do antebraço, apresenta MAE de 41,7° nos dois modelos, valor compatível com um preditor que não extrai informação dessa junta: o keypoint da garra está praticamente sobre o eixo de rotação dela, de modo que sua variação quase não altera os keypoints e as perdas geométricas não a supervisionam. Excluída a junta 5, o MAE médio das juntas 1 a 4 é de 5,4°. O erro 3D por keypoint é mínimo no keypoint de referência (cotovelo, 27 mm) e cresce em direção à extremidade da cadeia, atingindo 110 mm na garra, conforme ilustrado abaixo. No plano da imagem, 30,1%, 61,7% e 87,1% dos keypoints ficam a menos de 5, 10 e 20 px da posição verdadeira. Com as duas câmeras no treino, o desempenho é equivalente nas duas vistas: erro 3D de 57,4 mm e acurácia@60 mm de 69,0% na frontal, contra 60,0 mm e 67,0% na diagonal, com MAE de 12,70° e 12,65°.

![Erro absoluto médio por junta e erro 3D médio por keypoint no conjunto de teste, para a transferência dos pesos de 2025 e para o baseline ImageNet](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/erro_por_junta.png){w=16}

![Curvas ADD (porcentagem de imagens com erro 3D médio até o limiar, com o limiar de 60 mm de 2025 destacado) e PCK 2D (porcentagem de keypoints com erro até o limiar, em pixels da imagem 1280×720) no conjunto de teste](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/curvas_add_pck.png){w=15}

### Generalização entre câmeras

O modelo treinado apenas com a câmera frontal (experimento reduzido: 3.151 poses de treino, 10 épocas, melhor checkpoint na época 6) degrada fortemente na câmera não vista: o erro 3D passa de 140,4 mm na frontal para 418,5 mm na diagonal, a acurácia@60 mm cai de 8,6% para 0,0% e o MAE sobe de 23,1° para 32,6°. Como esse experimento usou menos dados e épocas que o modelo final, a comparação absoluta com o modelo treinado nas duas câmeras é apenas indicativa; a evidência relevante é a degradação de cerca de três vezes no erro 3D entre a vista conhecida e a desconhecida. O modelo aprende implicitamente a relação entre câmera e robô da vista de treino; generalizar para câmeras novas exige variar a pose da câmera nos dados de treino ou fornecer os parâmetros extrínsecos como entrada.

![Generalização entre câmeras: modelo treinado com as duas câmeras e modelo treinado apenas com a câmera frontal, avaliados separadamente em cada câmera do teste](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/generalizacao_cameras.png){w=16}

### Robustez a perturbações da imagem

A tabela a seguir apresenta uma seleção das condições avaliadas; as curvas completas são mostradas na figura subsequente.

Tabela: Robustez em subconjunto fixo de 400 imagens do teste, com profundidade recalculada sobre a imagem perturbada
| Perturbação | Severidade | Transf.: erro 3D (mm) | Transf.: ADD@60 (%) | Transf.: MAE (°) | Baseline: erro 3D (mm) |
|---|---|---|---|---|---|
| Sem perturbação | — | 57,4 | 68,0 | 12,41 | 88,2 |
| Ruído gaussiano | σ = 0,05 | 99,0 | 24,5 | 15,64 | 109,7 |
| Ruído gaussiano | σ = 0,10 | 213,2 | 2,0 | 23,57 | 169,7 |
| Desfoque de movimento | 7 px | 96,0 | 23,5 | 15,21 | 113,0 |
| Desfoque de movimento | 15 px | 206,6 | 1,0 | 20,44 | 162,1 |
| Brilho | ×0,4 | 60,5 | 64,2 | 12,68 | 93,7 |
| Contraste | ×0,3 | 67,2 | 52,0 | 13,24 | 93,1 |
| Oclusão | 30% da caixa | 94,3 | 33,2 | 15,59 | 114,5 |
| JPEG | qualidade 30 | 83,5 | 37,0 | 14,35 | 132,0 |
| JPEG | qualidade 15 | 113,8 | 14,2 | 16,19 | 214,6 |
| Resolução reduzida | escala 0,25 | 109,2 | 14,8 | 15,49 | 130,0 |

O modelo mostrou-se robusto a variações de brilho e contraste (erro 3D de no máximo 68 mm mesmo com brilho ×0,4 ou contraste ×0,3), o que é coerente com as augmentations fotométricas herdadas do treino de 2025. É, porém, sensível a perturbações de alta frequência: ruído gaussiano com σ = 0,05 eleva o erro 3D de 57 para 99 mm, o desfoque de 7 px para 96 mm e a compressão JPEG com qualidade 30 para 84 mm; a oclusão de 30% da caixa do robô leva a 94 mm e a redução da resolução para 25% a 109 mm. Em todas as perturbações o MAE das juntas degrada mais lentamente que o erro 3D, que acumula também os erros de profundidade e de rotação da raiz. O baseline ImageNet parte de um erro maior, mas degrada menos sob ruído e desfoque fortes (σ = 0,10: 170 mm contra 213 mm; desfoque de 15 px: 162 mm contra 207 mm) e mais sob compressão JPEG (qualidade 15: 215 mm contra 114 mm); sob brilho, contraste, oclusão, JPEG e resolução reduzida a transferência permanece melhor em todas as severidades.

![Robustez: erro 3D médio (linha cheia) e MAE das juntas (tracejado) em função da severidade de cada perturbação, para a transferência e para o baseline ImageNet, em subconjunto fixo de 400 imagens do teste](E:/CERISE/FRENTES/ROBOTICA/POSE_SERVO6DOF/evidencias/curvas_robustez.png){w=16}

### Latência e limitações

O modelo final foi empacotado num módulo de inferência (`PosePredictor`) destinado ao gêmeo digital do Objetivo 4, que recebe uma imagem RGB 1280×720 e devolve os ângulos das cinco juntas e os keypoints 2D e 3D. Em 100 chamadas com lote 1, a latência ponta a ponta foi de 162,5 ms em média (mediana de 170,1 ms e percentil 95 de 174,1 ms), ou 6,15 quadros por segundo, com pico de 2,94 GB de memória de GPU. Os valores são pessimistas, pois a GPU estava compartilhada com serviços em produção e com outras frentes. Numa medição separada, feita com um treino rodando em paralelo, o Depth Anything V2 (ViT-L) respondeu por cerca de 65% do tempo total (138,9 ms de 213,8 ms), enquanto a rede HPE isolada levou 74,9 ms (13,3 quadros por segundo); versões menores do Depth Anything V2 ou a otimização com TensorRT são as alternativas para operação em tempo real.

As principais limitações da avaliação são: medições apenas em dados sintéticos e com duas câmeras fixas, sem verificação em imagens reais do braço físico; a junta 5 não é observável com os keypoints escolhidos e a abertura da garra não é estimada; o experimento entre câmeras usou um subconjunto dos dados; a robustez foi medida num subconjunto de 400 imagens; e a latência foi medida em GPU compartilhada. Como próximos passos, propõem-se adicionar keypoints nas pontas das pinças, randomizar pose de câmera, iluminação e texturas na geração de dados, incluir ruído, desfoque e compressão nas augmentations, capturar imagens reais para aplicar a etapa autossupervisionada de 2025 e reduzir a latência do ramo de profundidade.

Código e evidências: [repositório cerise-2026-pose-servo6dof (privado)](https://github.com/cerise-ufg/cerise-2026-pose-servo6dof)

<!-- REFERENCIAS
[@hpe]: BAN, S.; FAN, J.; MA, X.; ZHU, W.; QIAO, Y.; WANG, Y. Real-time holistic robot pose estimation with unknown states. In: EUROPEAN CONFERENCE ON COMPUTER VISION (ECCV), 2024. Anais [...]. Cham: Springer, 2024.
[@depthanythingv2]: YANG, L.; KANG, B.; HUANG, Z.; ZHAO, Z.; XU, X.; FENG, J.; ZHAO, H. Depth Anything V2. In: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NeurIPS), 37., 2024. Anais [...]. 2024.
[@dream]: LEE, T. E.; TREMBLAY, J.; TO, T.; CHENG, J.; MOSIER, T.; KROEMER, O.; FOX, D.; BIRCHFIELD, S. Camera-to-robot pose estimation from a single image. In: IEEE INTERNATIONAL CONFERENCE ON ROBOTICS AND AUTOMATION (ICRA), 2020. Anais [...]. IEEE, 2020. p. 9426-9432.
[@robopose]: LABBÉ, Y.; CARPENTIER, J.; AUBRY, M.; SIVIC, J. Single-view robot pose and joint angle estimation via render & compare. In: IEEE/CVF CONFERENCE ON COMPUTER VISION AND PATTERN RECOGNITION (CVPR), 2021. Anais [...]. IEEE, 2021. p. 1654-1663.
[@hrnet]: SUN, K.; XIAO, B.; LIU, D.; WANG, J. Deep high-resolution representation learning for human pose estimation. In: IEEE/CVF CONFERENCE ON COMPUTER VISION AND PATTERN RECOGNITION (CVPR), 2019. Anais [...]. IEEE, 2019. p. 5693-5703.
[@resnet]: HE, K.; ZHANG, X.; REN, S.; SUN, J. Deep residual learning for image recognition. In: IEEE CONFERENCE ON COMPUTER VISION AND PATTERN RECOGNITION (CVPR), 2016. Anais [...]. IEEE, 2016. p. 770-778.
-->
