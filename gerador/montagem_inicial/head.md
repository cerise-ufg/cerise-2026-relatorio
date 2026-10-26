# Introdução e contextualização

Neste relatório, são apresentadas as atividades e os resultados obtidos como bolsista do CERISE entre janeiro e outubro de 2026, referentes ao plano de trabalho individual intitulado “Pesquisa, Desenvolvimento e Inovação em Gêmeos Digitais, Tecnologias Imersivas, Robótica e Navegação Autônoma no escopo do CERISE/EMC/UFG”.

Primeiramente, apresenta-se uma introdução com a contextualização do trabalho. Em seguida, são expostos os objetivos constantes no plano de trabalho, as atividades desenvolvidas, os resultados obtidos e uma comparação entre as atividades previstas e aquelas efetivamente executadas, incluindo as pendências.

A realidade aumentada (RA) vem se destacando como uma tecnologia emergente com potencial para transformar diversas áreas da sociedade. Ao mesclar elementos virtuais ao ambiente físico em tempo real, a RA possibilita interações mais dinâmicas e informativas, com impacto direto em setores como saúde, educação, engenharia e entretenimento [@azuma1997]. Um dos avanços mais notáveis está relacionado à sua crescente acessibilidade, impulsionada por dispositivos móveis: mapeamento tridimensional, reconhecimento de objetos e processamento em tempo real tornaram a RA mais precisa e adaptável a diferentes contextos [@billinghurst2015]. Em aplicações industriais, a RA tem sido empregada em manutenção, treinamento técnico e assistência remota, enquanto no campo educacional enriquece experiências de aprendizado por meio de simulações imersivas [@chen2017], e na área da saúde apoia procedimentos e treinamentos médicos [@barsom2016].

Um gargalo recorrente dessas aplicações é a obtenção de conteúdo tridimensional. Em 2025, foi desenvolvido um aplicativo capaz de capturar fotografias de um objeto e enviá-las a um servidor para a construção do modelo 3D correspondente, etapa que, naquela versão, era apenas simulada pelo servidor. Em 2026, a evolução de redes neurais generativas de imagem para 3D, capazes de produzir malhas texturizadas a partir de uma única fotografia em segundos, motivou a integração de um modelo dessa classe ao aplicativo, com otimização de desempenho e com um servidor capaz de atender múltiplos usuários simultaneamente.

Paralelamente, o conceito de gêmeo digital, uma representação virtual sincronizada com um sistema físico, depende de mecanismos de percepção capazes de estimar o estado do sistema real. No caso de braços robóticos, a estimação de pose a partir de imagens, sem acesso aos estados das juntas, permite construir gêmeos digitais de robôs sem instrumentação adicional. Em 2025, foi treinado um modelo de estimação de pose de braço robótico baseado em visão computacional e profundidade monocular; em 2026, o trabalho avançou para a geração de um novo conjunto de dados com um braço robótico virtual, a validação do modelo nesse novo cenário e a construção do gêmeo digital do braço.

Por fim, no eixo de Navegação Autônoma, o uso cooperativo de múltiplos drones para monitoramento de áreas, por exemplo para detecção e contagem de pessoas, exige a divisão da área de atuação entre as aeronaves, o planejamento de rotas de cobertura e um enlace de comunicação de longo alcance e baixo consumo, papel para o qual a tecnologia LoRa é candidata natural.

# Objetivos do plano de trabalho

O objetivo geral deste plano de trabalho é realizar pesquisa, desenvolvimento e inovação em gêmeos digitais, tecnologias imersivas, robótica e navegação autônoma no escopo do CERISE/EMC/UFG. O plano está organizado em dois eixos:

- Desenvolvimento, aprimoramento e validação de soluções baseadas em inteligência artificial e visão computacional, visando à geração de objetos tridimensionais com textura e melhor desempenho no aplicativo desenvolvido em 2025; à utilização de um braço robótico, físico ou virtual, para a geração de novos conjuntos de dados; à validação do modelo de detecção de pose desenvolvido no ano anterior; ao desenvolvimento de um gêmeo digital do braço robótico; e ao desenvolvimento de software para segmentação de áreas em cenários com múltiplos drones.
- Desenvolvimento e consolidação da infraestrutura computacional, dos sistemas embarcados e dos mecanismos de comunicação do projeto, incluindo a otimização do servidor do aplicativo para múltiplas solicitações simultâneas, a publicação do aplicativo na Play Store e a continuidade do projeto de comunicação baseado em LoRa.

Os objetivos específicos para a consecução do plano de trabalho são:

- Objetivo 1 — Inteligência artificial aplicada à geração de modelos tridimensionais: integrar ao aplicativo um modelo de rede neural capaz de gerar objetos 3D com textura, otimizar o processamento e validar a aplicação em uso real.
- Objetivo 2 — Infraestrutura computacional e implantação do aplicativo: otimizar o servidor para múltiplas solicitações, adequar a arquitetura para escalabilidade e confiabilidade e publicar o aplicativo na Play Store.
- Objetivo 3 — Geração de dados e validação de modelos de detecção de pose: utilizar um braço robótico (físico ou virtual) para gerar um novo conjunto de dados, validar o modelo de detecção de pose do ano anterior e analisar seu desempenho e robustez.
- Objetivo 4 — Desenvolvimento de gêmeo digital do braço robótico: modelar o braço em ambiente virtual, integrar o modelo de detecção de pose ao ambiente digital e reproduzir o comportamento do braço com base nos dados capturados.
- Objetivo 5 — Planejamento e adequação de sistema com drones para detecção e contagem de pessoas: planejar o sistema, desenvolver software de segmentação da área de atuação entre os drones, construir os módulos de comunicação definitivos e adequar os drones para recebê-los.

# Atividades realizadas

As atividades foram organizadas em frentes de trabalho (geração 3D, servidor e aplicativo, dataset e gêmeo digital do braço robótico, estimação de pose, comunicação LoRa e drones). Cada frente produziu código versionado, resultados medidos e guardados em arquivos (JSON e CSV) e evidências na forma de gráficos, capturas de tela e saídas de terminal. Nesta etapa, foram realizados:

(1) análise comparativa de 10 modelos abertos de geração 3D texturizada a partir de imagem e medição de 6 modelos ou variantes na estação NVIDIA DGX Spark (GB10) com 13 objetos do Google Scanned Objects, que resultou na seleção do Hunyuan3D-2 Turbo;

(2) otimização do modelo selecionado, com definição de três configurações de qualidade (*presets*) e empacotamento do pipeline de geração numa classe Python e numa imagem Docker;

(3) validação dos objetos 3D gerados, com testes automatizados, carregamento dos arquivos GLB nos visualizadores usados pelo aplicativo e análise qualitativa com fotografias reais de licença CC0;

(4) análise da arquitetura do servidor de 2025, reprodução dos seus gargalos com o modelo real e implantação de uma arquitetura assíncrona com fila persistente, cache, prioridade e controle de admissão, avaliada por testes de carga;

(5) integração do aplicativo CERISE AR 1.1.0 (React Native com Expo) ao servidor real de geração 3D, com validação ponta a ponta no emulador Android e compilação para o Simulador iOS;

(6) adequação técnica e normativa do aplicativo para a Play Store e preparação do pacote de publicação (AAB assinado, política de privacidade, formulários e ficha da loja), sem a publicação propriamente dita;

(7) geração, verificação integral e documentação de um dataset sintético do braço robótico virtual servo6dof, com 5.000 poses e 30.000 imagens, em Gazebo e ROS 2;

(8) porte do modelo de estimação de pose de 2025 para a estação DGX Spark, adaptação ao braço servo6dof por transferência de aprendizado e avaliação de precisão, generalização entre câmeras, robustez e latência;

(9) caracterização e validação do modelo digital do braço (URDF, cinemática direta, espaço de trabalho, projeção sobre as imagens do dataset e planejamento com MoveIt 2);

(10) integração do modelo de pose a um gêmeo digital do braço, com visualizador web e nó ROS 2, avaliado em simulação;

(11) desenvolvimento e verificação, sem hardware de rádio, do software do protótipo de comunicação LoRa (protocolo, firmware, testes, simulação de acesso ao canal e dashboard) e projeto do módulo de comunicação dos drones;

(12) desenvolvimento de um pacote de software para segmentação da área de atuação entre drones heterogêneos e de algoritmos de realocação dinâmica, avaliados em simulação 2D;

(13) ajuste fino e avaliação de um detector YOLO11 para detecção e contagem de pessoas em imagens aéreas do conjunto VisDrone e validação, por simulação, da agregação das contagens entre drones;

(14) criação de cinco repositórios privados no GitHub, um por frente: [cerise-2026-gen3d](https://github.com/EduardoCaixeta/cerise-2026-gen3d), [cerise-2026-pose-servo6dof](https://github.com/EduardoCaixeta/cerise-2026-pose-servo6dof), [cerise-2026-servo6dof-gemeo-digital](https://github.com/EduardoCaixeta/cerise-2026-servo6dof-gemeo-digital), [cerise-2026-drones-segmentacao](https://github.com/EduardoCaixeta/cerise-2026-drones-segmentacao) e [cerise-2026-lora-prototipo](https://github.com/EduardoCaixeta/cerise-2026-lora-prototipo); as alterações de 2026 do aplicativo estão no repositório [cerise-ar](https://github.com/EduardoCaixeta/cerise-ar), no [pull request #1](https://github.com/EduardoCaixeta/cerise-ar/pull/1), aberto como rascunho;

(15) uso da infraestrutura computacional do CERISE e de apoio: a estação NVIDIA DGX Spark, com GPU GB10 (arquitetura Blackwell), CPU aarch64 e 128 GB de memória unificada, compartilhada com serviços de IA em produção, para os experimentos com GPU, o servidor de geração 3D e as simulações do braço; um Mac mini M4 com Xcode para a compilação iOS; e um notebook com Windows e o Android SDK para as compilações Android, o emulador e a manutenção dos repositórios;

(16) elaboração deste relatório técnico-científico, com os resultados rastreáveis aos arquivos de medição guardados nos repositórios.

# Resultados obtidos

Nesta seção, é apresentado um resumo dos resultados obtidos:

1) Análise comparativa e seleção do modelo de geração 3D: o Hunyuan3D-2 Turbo foi selecionado, com a melhor geometria medida (distância de Chamfer de 0,032 e F-score@0,05 de 0,951);

2) Otimização do modelo integrado e desempenho: redução de cerca de 38 % no tempo de geração e três *presets* com tempos medianos de 23,9 s, 30,4 s e 82,1 s;

3) Validação dos objetos 3D gerados: 58 de 58 testes automatizados aprovados e 7 de 7 arquivos GLB carregados nos visualizadores;

4) Servidor de geração 3D: taxa de erro reduzida de 90,9 % para zero e latência p95 até 22 % menor com 16 clientes simultâneos;

5) Aplicativo CERISE AR com geração de objetos 3D texturizados: fluxo da foto ao modelo texturizado validado no emulador contra o servidor real, em 13,5 s a 31,5 s sem fila;

6) Adequação do aplicativo para a Play Store: pacote 1.1.0 pronto e verificado, com publicação pendente;

7) Dataset do braço robótico: 5.000 poses e 30.000 imagens, verificadas integralmente e documentadas;

8) Aplicação do modelo de pose de 2025 ao novo dataset: acurácia ADD@60 mm de 68,0 % com transferência de aprendizado, contra 32,8 % do baseline;

9) Avaliação de precisão e robustez do modelo de pose: robustez a brilho e contraste, sensibilidade a ruído, desfoque e compressão e latência de 162,5 ms por imagem;

10) Modelo digital do braço robótico: cinemática validada contra o ROS 2 e IoU de silhueta de 0,950 e 0,938 nas duas câmeras;

11) Gêmeo digital do braço robótico: erro médio de 5,41° nas juntas 1 a 4 e latência mediana de 99,6 ms, em simulação;

12) Protótipo de comunicação LoRa: software verificado sem hardware (51 testes automatizados e 1.130 execuções de simulação), com o ensaio físico pendente;

13) Projeto dos módulos de comunicação para os drones: requisitos, gabinete e estimativas de enlace e de energia, sem fabricação;

14) Segmentação da área de atuação entre drones: menor makespan em 31 de 40 casos com o DARP com refinamento por tempo;

15) Colaboração entre drones e realocação dinâmica: cobertura de pelo menos 99,7 % após o abandono de um drone, com aumento médio de 23,1 % no makespan;

16) Detecção e contagem de pessoas em imagens aéreas: mAP50 de pessoa de 0,528 (validação) e 0,316 (test-dev) após ajuste fino.

Serão apresentadas a seguir seções abordando com mais detalhes cada um dos tópicos acima.

