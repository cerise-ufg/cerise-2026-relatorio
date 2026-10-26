## Geração e documentação do novo dataset do braço robótico

Esta etapa corresponde à Atividade 7 do Objetivo 3 do plano de trabalho: gerar, com um braço robótico virtual, um conjunto de dados estruturado e documentado para o treinamento e a avaliação do modelo de estimação de pose (Atividades 8 e 9) e para o gêmeo digital do braço (Atividades 11 e 12). Optou-se pelo braço virtual servo6dof, cujo pacote ROS 2 (descrição, controladores, configuração do MoveIt 2 e câmeras) foi fornecido pelo Prof. Dr. Alisson Assis Cardoso e adaptado para um estúdio fotográfico no simulador. O braço possui cinco juntas de revolução (`joint_1` a `joint_5`) e uma junta de garra (`joint_6`).

### Metodologia de geração

As poses foram definidas por um plano fixo e reprodutível (`plano_poses.json`, semente 20260909) com 5.000 configurações sorteadas uniformemente em ±90° para as juntas do braço e em [−40°; 30°] para a garra, descontada uma folga de 5 % em cada extremo (faixa efetiva de ±81° nas juntas do braço). A simulação utilizou ROS 2 Humble [@macenski2022] e Ignition Gazebo Fortress [@koenig2004] em contêineres Docker na estação NVIDIA DGX Spark (GB10), com renderização ogre2 por GPU em modo *headless* (EGL). Para cada pose, o script de captura comanda a trajetória por `FollowJointTrajectory` (3 s de tempo simulado mais 0,5 s de assentamento), descarta os quadros antigos e grava seis imagens PNG de 1280×720 pixels — RGB, profundidade (inteiro, em milímetros) e mapa de rótulos de segmentação (braço, chão e fundo) — das câmeras frontal e diagonal, além de um JSON com as juntas comandadas e as juntas efetivamente alcançadas (`juntas_reais`, lidas de `/joint_states` no instante da captura). A geração foi paralelizada em oito instâncias isoladas do Gazebo, com retomada automática a partir do que já existia em disco.

Sobre a saída foram implementadas ferramentas de indexação (`index.csv`, uma linha por pose), verificação de integridade com decodificação integral de cada imagem, estatísticas de distribuição e cobertura do espaço de juntas, comparação entre juntas reais e comandadas e reconstrução da linha do tempo da geração. A documentação segue o formato de *datasheet* proposto por Gebru et al. [@gebru2021] (`docs/DATASET.md`), com motivação, composição, processo de coleta, formato, *splits* recomendados, usos e limitações; uma amostra de 8 poses (4,2 MB) está versionada no repositório. O *split* determinístico por identificador (`id` mod 10) define 4.000 poses de treino, 500 de validação e 500 de teste.

### Resultados

A geração foi concluída com as 5.000 poses do plano, totalizando 30.000 imagens e 2,51 GB, conforme a composição apresentada a seguir. As anotações JSON somam 7,7 MB, e o volume médio é de 0,50 MB por pose.

Tabela: Composição do dataset por modalidade e câmera (5.000 poses; tamanhos medidos em disco)
| Modalidade | Câmera frontal | Câmera diagonal | Total |
|---|---|---|---|
| RGB (PNG 8 bits) | 0,60 GB (116 KB/img.) | 0,50 GB (98 KB/img.) | 1,10 GB |
| Profundidade (PNG inteiro, mm) | 0,24 GB (47 KB/img.) | 1,05 GB (206 KB/img.) | 1,30 GB |
| Segmentação (rótulos 0/1/2) | 0,05 GB (10 KB/img.) | 0,05 GB (11 KB/img.) | 0,11 GB |

![Amostras do dataset nas duas câmeras: imagem RGB, profundidade colorizada e mapa de segmentação, com o rótulo do braço destacado em laranja](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a7_grade_amostras.png){w=16}

A verificação completa decodificou as 30.000 imagens em 86 s (6 processos) sem nenhum problema: todas têm 1280×720 pixels e o modo de cor esperado, as 10.000 máscaras contêm exatamente os rótulos {0, 1, 2}, não há arquivos órfãos nem poses faltantes e não há quadro RGB duplicado entre poses distintas, o que indica ausência de captura de quadros desatualizados. Os principais indicadores estão reunidos na tabela a seguir, e o registro do terminal dessa verificação é mostrado na figura subsequente.

Tabela: Indicadores de integridade, distribuição e geração do dataset
| Indicador | Valor medido |
|---|---|
| Imagens verificadas sem problema | 30.000 de 30.000 |
| PNGs órfãos / faltantes / RGB duplicados | 0 / 0 / 0 |
| Área média ocupada pelo braço (frontal / diagonal) | 8,8 % / 6,0 % da imagem |
| Desvio-padrão dos ângulos comandados (juntas 1 a 5) | 45,9° a 46,7° (uniforme: 46,8°) |
| Cobertura dos pares de juntas (grade 20×20) | 100 % nos 10 pares |
| Maior correlação de Pearson entre juntas (em módulo) | 0,024 |
| Poses com juntas reais diferentes das comandadas (> 0,01 rad) | 34,1 % |
| Duração da geração (8 instâncias) e vazão média | 3,64 h; 0,38 pose/s |

![Registro do terminal com a indexação e a verificação de integridade das 30.000 imagens do dataset completo](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/term_a7_integridade.png){w=15}

Os ângulos comandados ocupam exatamente a faixa do plano, com média próxima de zero e dispersão compatível com a distribuição uniforme. A distância média ao vizinho mais próximo no espaço de juntas normalizado (0,1265) é praticamente igual à de uma amostra uniforme de mesmo tamanho (0,1262), o que confirma a cobertura homogênea ilustrada abaixo.

![Cobertura do espaço de juntas por pares de juntas e matriz de correlação de Pearson entre as juntas](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a7_cobertura_correlacao.png){w=16}

A comparação entre juntas reais e comandadas mostrou divergência superior a 0,01 rad em 34,1 % das poses, concentrada em `joint_1` a `joint_3` (19,8 %, 26,9 % e 21,9 % das poses). A cinemática direta do modelo digital explica a maior parte dos casos: 19,7 % das configurações comandadas levariam algum elo abaixo do plano do chão, e todas elas divergem, enquanto nenhuma configuração real fica abaixo de −5 cm — o braço é barrado pelo chão e o JSON registra a posição em que ele parou. As imagens confirmam que o rótulo correto é a junta real: nas 670 imagens de poses divergentes avaliadas, o IoU médio entre a silhueta do modelo e a máscara do simulador foi de 0,930 com as juntas reais e de 0,547 com as comandadas.

![Divergência entre juntas reais e comandadas por junta e em função da altura mínima do braço na configuração comandada](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a7_real_vs_comandado.png){w=16}

A geração ocorreu em 26/10/2026, da primeira pose às 00h41 até a última às 04h19 (3,64 h), com mediana de 12,8 s por pose em cada instância e pico de 45 poses/min em janelas de 5 minutos; a mediana dessas janelas foi de 17,5 poses/min, pois a vazão caiu quando a estação passou a ser compartilhada com outras tarefas. Uma primeira rodada gravou 4.747 poses, e uma segunda rodada completou as 253 restantes; cada instância terminou com 625 poses.

### Discussão e limitações

O dataset é íntegro, uniforme e documentado, mas apresenta limitações que orientam o seu uso. As juntas comandadas não são verdade-base em 34,1 % das poses, de modo que o campo `juntas_reais` deve ser adotado como rótulo; além disso, cerca de 2 % das imagens (estimativa sobre 1.000 poses) apresentam silhueta incompatível com as juntas registradas e devem ser filtradas por IoU. Na segmentação, o braço recebe o rótulo 0, compartilhado com regiões sem objeto, e a máscara do braço deve ser obtida como rótulo 0 com profundidade válida. O Gazebo Fortress não aplica as juntas *mimic* da garra, cuja geometria nas imagens difere parcialmente do modelo cinemático. Por fim, o domínio é sintético e fixo (duas câmeras, iluminação, fundo e materiais constantes), e a transferência para o braço físico exigirá randomização de domínio [@tobin2017] ou ajuste fino com imagens reais.

Todos os resultados desta seção e das seções seguintes referem-se à versão do dataset com o braço em cinza (5.000 poses, 2,51 GB), preservada integralmente na estação DGX Spark. Posteriormente, foi iniciada uma nova renderização do dataset com o braço na cor laranja, ainda em andamento na data deste relatório e sem resultados aqui reportados.

Código e evidências: [cerise-2026-servo6dof-gemeo-digital](https://github.com/EduardoCaixeta/cerise-2026-servo6dof-gemeo-digital) (repositório privado).

## Modelo digital do braço robótico

Esta etapa corresponde à Atividade 11 do Objetivo 4: modelar o braço robótico em ambiente virtual, com suas características físicas e cinemáticas. O modelo digital é a base comum do dataset, do planejamento de movimento e do gêmeo digital, e por isso foi caracterizado e validado de forma independente.

### Metodologia

O URDF foi gerado a partir do xacro do pacote de descrição, com os mesmos parâmetros utilizados pelo Gazebo na geração do dataset. A partir dele foram extraídas as tabelas de elos e juntas e a árvore cinemática, e foi implementada uma cinemática direta própria em Python e NumPy (`modelo_digital/cinematica.py`), que compõe as transformações das origens (convenção RPY) com rotações de eixo-ângulo (fórmula de Rodrigues), resolve as juntas *mimic* e opera em lotes vetorizados. Essa implementação foi validada contra o TF publicado pelo `robot_state_publisher` do ROS 2 para o mesmo URDF, em 300 configurações aleatórias e 11 elos. O espaço de trabalho foi estimado por Monte Carlo com 100.000 configurações uniformes nos limites das juntas. Também foi implementado o modelo *pinhole* das câmeras do estúdio (pose do SDF, campo de visão horizontal de 60°, 1280×720 pixels), que permite projetar as malhas STL posicionadas pela cinemática direta sobre as imagens do dataset e medir o IoU entre a silhueta do modelo e a máscara de segmentação do simulador. Por fim, o MoveIt 2 [@coleman2014] foi executado sem interface gráfica, com `move_group`, planejador OMPL [@sucan2012] RRTConnect [@kuffner2000], cinemática inversa KDL e `ros2_control` com hardware simulado (`mock_components/GenericSystem`); um cliente da ação de planejamento solicitou cinco objetivos, com dez pedidos de planejamento por objetivo.

### Resultados

O URDF possui 13 elos e 12 juntas: 11 de revolução, das quais 6 são ativas (`joint_1` a `joint_6`) e 5 são *mimic* de `joint_6`, e uma junta fixa entre o referencial do mundo e a base. O braço tem 5 graus de liberdade e a garra, 1. A tabela a seguir resume a cadeia ativa; as distâncias entre origens consecutivas da cadeia principal são 0,23, 0,57, 0,63, 0,78 e 0,36 m, e as malhas STL são aplicadas com fator de escala 6. As massas somam 1,51 kg, e todas as inércias têm valor de preenchimento (1 kg·m²), de modo que o modelo é cinematicamente completo, mas não dinamicamente calibrado.

Tabela: Juntas ativas do modelo digital extraídas do URDF
| Junta | Elo pai → elo filho | Origem xyz (m) | Eixo | Limites (°) |
|---|---|---|---|---|
| joint_1 | base_link → primeiro_elo | (0; −0,23; −0,01) | z | −90 a 90 |
| joint_2 | primeiro_elo → segundo_elo | (−0,05; −0,03; 0,57) | x | −90 a 90 |
| joint_3 | segundo_elo → terceiro_elo | (0,06; 0; 0,63) | x | −90 a 90 |
| joint_4 | terceiro_elo → quarto_elo | (0; 0,78; 0) | x | −90 a 90 |
| joint_5 | quarto_elo → base_garra | (0,02; 0,36; 0) | y | −90 a 90 |
| joint_6 (garra) | base_garra → garra_elo1 | (−0,072; 0,12; 0,01) | z | −40 a 30 |

![Árvore cinemática do braço servo6dof extraída do URDF, com as juntas ativas, seus eixos e limites e as juntas mimic da garra](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a11_arvore_cinematica.png){w=9}

As verificações do modelo estão reunidas na tabela seguinte. A cinemática direta própria coincidiu com o TF do ROS 2 no nível do arredondamento numérico, inclusive nos elos *mimic* da garra, e a cinemática do visualizador web, usada no gêmeo digital, coincidiu com a do servidor dentro da precisão de ponto flutuante de 32 bits.

Tabela: Verificações do modelo digital
| Verificação | Amostra | Resultado medido |
|---|---|---|
| Cinemática direta própria × TF do ROS 2 | 300 configurações × 11 elos | erro máx. 1,9×10⁻¹⁵ m e 4,2×10⁻⁸ rad |
| Cinemática do front-end (three.js) × própria | capturas do visualizador | até 7,6×10⁻⁷ m |
| Espaço de trabalho da ponta da garra | 100.000 configurações | alcance horizontal 2,05 m; z de −0,82 a 2,58 m |
| Silhueta do modelo × máscara (câmera frontal) | 1.000 imagens | IoU médio 0,950 (mediana 0,965) |
| Silhueta do modelo × máscara (câmera diagonal) | 1.000 imagens | IoU médio 0,938 (mediana 0,951) |
| MoveIt 2 headless | 5 objetivos × 10 pedidos | 50/50 planos; 12,9 a 17,0 ms em média |

O fecho convexo do espaço de trabalho tem 27,8 m³, e o volume efetivamente ocupado, medido em voxels de 5 cm, é de 7,9 m³. Cerca de 20 % das configurações dentro dos limites levariam a ponta da garra abaixo do plano do chão, propriedade que explica parte das divergências entre juntas comandadas e reais observadas no dataset.

![Espaço de trabalho da ponta da garra estimado com 100.000 configurações: nuvem 3D, vista de topo e vista lateral radial com o plano do chão](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a11_espaco_trabalho.png){w=16}

A projeção das malhas posicionadas pelas juntas registradas sobre as imagens do simulador coincide visualmente com o braço renderizado, o que valida simultaneamente o modelo cinemático, o modelo de câmera e os rótulos do dataset. Em 2,05 % das imagens avaliadas (41 de 2.000), o IoU ficou abaixo de 0,8, casos em que o braço aparece numa configuração diferente da registrada e que devem ser filtrados para treino.

![Malhas do modelo digital (verde translúcido) e cadeia cinemática (laranja) projetadas sobre imagens do dataset nas câmeras frontal e diagonal](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a11_sobreposicao_modelo_dataset.png){w=14}

No MoveIt 2, os cinco objetivos — três em espaço de juntas, um alvo cartesiano de posição e o retorno à posição inicial — foram planejados e executados com sucesso, com trajetórias de 17 a 28 pontos e duração de 1,56 a 2,63 s. No alvo cartesiano, a posição final de `base_garra` ficou a 1,6 cm do alvo, dentro da tolerância de 2 cm especificada no pedido.

![Trajetórias de juntas planejadas pelo MoveIt 2 com OMPL RRTConnect e estados de junta publicados durante a execução com hardware simulado](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a11_moveit_trajetoria.png){w=15}

### Discussão e limitações

O modelo digital é cinematicamente consistente com o simulador e com o ROS 2, o que o qualifica como referência para o gêmeo digital. As limitações são de natureza dinâmica e de fidelidade da garra: as massas são simbólicas e as inércias são valores de preenchimento, inadequados para simulação dinâmica fiel; o Gazebo Fortress não implementa as juntas *mimic*, de modo que a geometria da garra nas imagens difere da do modelo e responde por parte do erro residual de silhueta; e o planejamento não inclui o chão como objeto de colisão. O MoveIt 2 foi exercitado apenas com hardware simulado, e a validação com o braço físico, assim como a calibração de massas e inércias a partir do CAD ou de medições, permanece como trabalho futuro.

Código e evidências: [cerise-2026-servo6dof-gemeo-digital](https://github.com/EduardoCaixeta/cerise-2026-servo6dof-gemeo-digital) (repositório privado).

## Gêmeo digital do braço robótico

Esta etapa corresponde à Atividade 12 do Objetivo 4: integrar o modelo de detecção de pose ao ambiente virtual do braço robótico, com o resultado esperado de um gêmeo digital capaz de reproduzir o comportamento do braço a partir dos dados capturados [@grieves2017]. No sistema desenvolvido, o braço de referência segue a verdade-base do simulador (`juntas_reais`), enquanto o gêmeo digital segue apenas as juntas estimadas pelo modelo de pose a partir de uma única imagem RGB, sem acesso a qualquer anotação; a comparação quadro a quadro entre os dois mede a fidelidade do gêmeo.

### Arquitetura e implementação

O servidor do gêmeo (FastAPI com WebSocket) executa em contêiner na estação DGX Spark e é publicado apenas na interface local da máquina, com acesso por túnel SSH local. A estimação é feita por um componente plugável (`Predictor`), com implementações de oráculo (verdade-base), de ruído sintético (apenas para demonstração do painel), de chamada HTTP e de adaptação ao modelo da frente de estimação de pose (Atividades 8 e 9), que combina profundidade monocular Depth Anything V2 [@yang2024dav2] com um estimador de pose e devolve os ângulos `joint_1` a `joint_5`; a garra não é estimada. O front-end, em three.js r160 com urdf-loader 0.13.1, carrega o mesmo URDF e as malhas STL duas vezes (referência sólida e gêmeo verde translúcido), lado a lado ou sobrepostos na vista da câmera do dataset, e exibe a imagem com o esqueleto 2D previsto, os ângulos por junta e o gráfico de erro.

Antes da integração, a infraestrutura foi validada com o oráculo (12 malhas carregadas por braço, sem erros, e cinemática do navegador coincidente com a do servidor). A avaliação usa o mesmo conjunto de teste da frente de pose (500 poses × 2 câmeras = 1.000 imagens, nenhuma usada no treino). Para medir latência, o WebSocket opera em malha fechada: cada quadro só é enviado após o front-end confirmar que o anterior foi desenhado no canvas, em Chromium *headless* (Playwright) com WebGL acelerado pela GPU da própria estação. No ROS 2, o nó `gemeo_twin` publica `/twin/joint_states` a partir das imagens, e um segundo `robot_state_publisher` (prefixo `twin/`) alimenta o RViz 2 em tela virtual.

### Resultados

A tabela a seguir apresenta o erro absoluto por junta nos 1.000 quadros. A média das cinco juntas no gêmeo (12,68°) é igual à da avaliação *offline* da frente de pose nas mesmas imagens, o que indica que a integração (leitura da imagem, recorte, inferência, adaptação e conversão de unidades) não acrescenta erro. O viés médio é inferior a 1° em módulo nas juntas 1 a 4.

Tabela: Erro absoluto por junta no gêmeo digital, em graus (conjunto de teste, apenas imagem)
| Junta | Frontal (média) | Diagonal (média) | Total (média) | Total (mediana) | Total (p95) |
|---|---|---|---|---|---|
| joint_1 (base) | 4,08 | 4,30 | 4,19 | 2,92 | 11,9 |
| joint_2 (ombro) | 3,12 | 2,96 | 3,04 | 1,89 | 9,0 |
| joint_3 (cotovelo) | 4,09 | 3,73 | 3,91 | 2,54 | 11,6 |
| joint_4 (punho) | 10,46 | 10,57 | 10,52 | 6,63 | 36,1 |
| joint_5 (rotação da garra) | 41,75 | 41,71 | 41,73 | 42,49 | 78,0 |
| Média das juntas 1 a 4 | 5,44 | 5,39 | 5,41 | 3,83 | 15,4 |

O erro de posição do efetuador, calculado pela cinemática direta com as juntas previstas e verdadeiras, teve mediana de 76,4 mm, média de 107,1 mm, p95 de 275,0 mm e máximo de 991,4 mm; 64,5 % dos quadros ficaram abaixo de 100 mm e 27,2 % abaixo de 50 mm. Como a ponta da garra alcança até 2,09 m de distância do ombro, 1° de erro no ombro desloca a garra em até cerca de 37 mm.

![Gêmeo digital com o modelo de pose em um quadro de baixo erro: braço de referência e gêmeo lado a lado, esqueleto 2D previsto sobre a imagem, ângulos por junta e erro do efetuador de 1,5 cm](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a12i_gemeo_baixo_erro_lado.png){w=16}

![Distribuição do erro por junta no gêmeo por câmera e comparação entre média e p95 do gêmeo e a avaliação offline da frente de pose](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a12i_erro_por_junta_gemeo.png){w=15}

A latência entre a leitura da imagem e o gêmeo desenhado está decomposta na tabela seguinte. O modelo de pose domina o tempo: a mediana ponta a ponta supera a do modelo em cerca de 22 ms, parcela atribuível às demais etapas da integração.

Tabela: Latência por etapa, em milissegundos (1.000 quadros, malha fechada, WebGL na GPU)
| Etapa | Mediana | Média | p95 |
|---|---|---|---|
| Leitura do PNG 1280×720 | 8,4 | 10,0 | 18,2 |
| Modelo de pose (recorte, profundidade e pose) | 77,7 | 103,1 | 180,4 |
| Cinemática direta e JPEG da câmera | 3,6 | 4,4 | 8,6 |
| Serialização e WebSocket | 1,3 | 1,4 | 2,2 |
| Atualização no three.js até o canvas | 14,1 | 15,0 | 18,2 |
| Ponta a ponta medido | 99,6 | 134,5 | 216,9 |

Em malha fechada, a sessão da câmera frontal sustentou 9,76 quadros/s e a da diagonal, 5,93 quadros/s; com taxas-alvo fixas, foram medidos 2,00, 5,00 e 9,97 quadros/s para alvos de 2, 5 e 10. A diferença entre câmeras decorre da carga da GPU, compartilhada com serviços de produção e outras tarefas: num controle com 120 chamadas alternando as câmeras, a latência do modelo foi de 65,2 ms (frontal) e 64,6 ms (diagonal). O pico de memória de GPU do modelo foi de 2,94 GB alocados. Com rasterização por software (SwiftShader), o navegador caiu para 0,42 quadro/s, o que mostra a necessidade de WebGL acelerado.

![Latência imagem → predição → gêmeo desenhado por etapa, distribuição da latência em 1.000 quadros e taxa de quadros sustentada por sessão](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a12i_latencia_fps.png){w=16}

Na análise de falhas, o principal modo identificado foi o braço cortado pelo enquadramento da câmera: em uma amostra de 200 quadros, isso ocorreu em 22,5 % deles, com erro mediano do efetuador de 117 mm contra 70 mm nos demais, e esteve presente em 45 % dos 20 piores quadros. O pior caso (991 mm) é uma ambiguidade de configuração do tipo "cotovelo invertido", com erros de +111° no ombro e −118° no cotovelo e silhueta 2D semelhante à verdadeira. O erro também cresce com o giro da base (correlação de Spearman de 0,36 com o módulo de `joint_1`), situação de escorço em relação às câmeras.

![Piores quadros do gêmeo pelo erro do efetuador e um quadro de baixo erro, com esqueleto verdadeiro em branco e previsto em verde](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a12i_piores_quadros.png){w=16}

No teste em ROS 2 (40 s, imagens da câmera frontal do conjunto de teste publicadas a 2 Hz), o tópico `/twin/joint_states` foi publicado a 2,00 Hz, com 79 pares casados com a referência pelo carimbo de tempo. O atraso entre a imagem e a mensagem do gêmeo teve mediana de 255 ms (p95 de 282 ms), dos quais 87 ms correspondem ao modelo via HTTP e o restante ao transporte da imagem bruta; os erros médios por junta foram de 4,2, 5,3, 4,6, 11,0 e 37,6°, e o erro mediano do efetuador, de 77 mm, coerentes com a avaliação pelo navegador.

![RViz 2 em tela virtual com o braço de referência e o gêmeo digital, deslocado lateralmente, movido por /twin/joint_states a partir das imagens](E:/CERISE/FRENTES/ROBOTICA/SERVO6DOF_GEMEO/evidencias/a12i_rviz_gemeo_2.png){w=13}

### Discussão e limitações

O gêmeo reproduz o comportamento do braço nas juntas que o modelo observa bem: nas juntas 1 a 4, o erro mediano é de 3,8°, e 64,5 % dos quadros têm o efetuador a menos de 10 cm da posição real, com cerca de 10 quadros/s e latência mediana de 0,1 s, adequados ao acompanhamento visual. O resultado depende essencialmente do modelo de pose, pois a integração não acrescenta erro e acrescenta pouco tempo. Como limitações, a validação foi feita apenas em simulação, com imagens sintéticas e as mesmas duas câmeras fixas do treino; a rotação da garra (`joint_5`, 41,7°) não é estimada de forma útil e a abertura da garra não é estimada (no ROS 2 ela é fixada em 0 rad apenas para completar a árvore TF); a latência foi medida com a GPU compartilhada e o navegador no mesmo host, sem garantia de tempo real; e cada quadro é tratado de forma independente, sem filtro temporal, sobre uma sequência de poses independentes, não um movimento contínuo. O visualizador não foi exposto publicamente, o que depende de decisão do bolsista. Como próximos passos, propõem-se a avaliação com o braço físico e câmera calibrada, a fusão das duas câmeras com filtragem temporal e a inclusão de pontos-chave nas pinças da garra.

Código e evidências: [cerise-2026-servo6dof-gemeo-digital](https://github.com/EduardoCaixeta/cerise-2026-servo6dof-gemeo-digital) (repositório privado).

<!-- REFERENCIAS
[@gebru2021]: GEBRU, T. et al. Datasheets for datasets. Communications of the ACM, v. 64, n. 12, p. 86-92, 2021.
[@macenski2022]: MACENSKI, S. et al. Robot Operating System 2: design, architecture, and uses in the wild. Science Robotics, v. 7, n. 66, eabm6074, 2022.
[@koenig2004]: KOENIG, N.; HOWARD, A. Design and use paradigms for Gazebo, an open-source multi-robot simulator. In: IEEE/RSJ INTERNATIONAL CONFERENCE ON INTELLIGENT ROBOTS AND SYSTEMS (IROS), 2004, Sendai. Proceedings [...]. IEEE, 2004. p. 2149-2154.
[@tobin2017]: TOBIN, J. et al. Domain randomization for transferring deep neural networks from simulation to the real world. In: IEEE/RSJ INTERNATIONAL CONFERENCE ON INTELLIGENT ROBOTS AND SYSTEMS (IROS), 2017, Vancouver. Proceedings [...]. IEEE, 2017. p. 23-30.
[@coleman2014]: COLEMAN, D. et al. Reducing the barrier to entry of complex robotic software: a MoveIt! case study. Journal of Software Engineering for Robotics, v. 5, n. 1, p. 3-16, 2014.
[@sucan2012]: ŞUCAN, I. A.; MOLL, M.; KAVRAKI, L. E. The Open Motion Planning Library. IEEE Robotics & Automation Magazine, v. 19, n. 4, p. 72-82, 2012.
[@kuffner2000]: KUFFNER, J. J.; LAVALLE, S. M. RRT-Connect: an efficient approach to single-query path planning. In: IEEE INTERNATIONAL CONFERENCE ON ROBOTICS AND AUTOMATION (ICRA), 2000, San Francisco. Proceedings [...]. IEEE, 2000. p. 995-1001.
[@grieves2017]: GRIEVES, M.; VICKERS, J. Digital twin: mitigating unpredictable, undesirable emergent behavior in complex systems. In: KAHLEN, F.-J.; FLUMERFELT, S.; ALVES, A. (ed.). Transdisciplinary perspectives on complex systems. Cham: Springer, 2017. p. 85-113.
[@yang2024dav2]: YANG, L. et al. Depth Anything V2. In: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NeurIPS), 37., 2024. Proceedings [...]. 2024.
-->
