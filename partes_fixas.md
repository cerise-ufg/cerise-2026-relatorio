# Introdução e contextualização

Neste relatório, são apresentadas as atividades e os resultados obtidos como bolsista do CERISE ao longo de 2026, referentes ao plano de trabalho individual intitulado "Pesquisa, Desenvolvimento e Inovação em Gêmeos Digitais, Tecnologias Imersivas, Robótica e Navegação Autônoma no escopo do CERISE/EMC/UFG".

Primeiramente, apresenta-se uma introdução com a contextualização do trabalho. Em seguida, são expostos os objetivos constantes no plano de trabalho, as atividades desenvolvidas, os resultados obtidos e uma comparação entre as atividades previstas e aquelas efetivamente executadas, incluindo as pendências.

A realidade aumentada (RA) vem se destacando como uma tecnologia emergente com potencial para transformar diversas áreas da sociedade. Ao mesclar elementos virtuais ao ambiente físico em tempo real, a RA possibilita interações mais dinâmicas e informativas, com impacto direto em setores como saúde, educação, engenharia e entretenimento [1]. Um dos avanços mais notáveis está relacionado à sua crescente acessibilidade, impulsionada por dispositivos móveis: mapeamento tridimensional, reconhecimento de objetos e processamento em tempo real tornaram a RA mais precisa e adaptável a diferentes contextos [2]. Em aplicações industriais, a RA tem sido empregada em manutenção, treinamento técnico e assistência remota, enquanto no campo educacional enriquece experiências de aprendizado por meio de simulações imersivas [3], e na área da saúde apoia procedimentos e treinamentos médicos [4].

Um gargalo recorrente dessas aplicações é a obtenção de conteúdo tridimensional. Em 2025 foi desenvolvido um aplicativo capaz de capturar fotografias de um objeto e solicitar a um servidor a construção do modelo 3D correspondente. Em 2026, a evolução de redes neurais generativas de imagem para 3D — capazes de produzir malhas texturizadas a partir de uma única fotografia em segundos — motivou a integração de um modelo dessa classe ao aplicativo, com otimização de desempenho e de um servidor capaz de atender múltiplos usuários simultaneamente.

Paralelamente, o conceito de gêmeo digital — uma representação virtual sincronizada com um sistema físico — depende de mecanismos de percepção capazes de estimar o estado do sistema real. No caso de braços robóticos, a estimação de pose a partir de imagens, sem acesso aos estados das juntas, permite construir gêmeos digitais de robôs sem instrumentação adicional. Em 2025 foi treinado um modelo de estimação de pose de braço robótico baseado em visão computacional e profundidade monocular; em 2026, o trabalho avança para a geração de um novo conjunto de dados com um braço robótico virtual, a validação do modelo nesse novo cenário e a construção do gêmeo digital do braço.

Por fim, no eixo de Navegação Autônoma, o uso cooperativo de múltiplos drones para monitoramento de áreas — por exemplo, detecção e contagem de pessoas — exige a divisão da área de atuação entre as aeronaves, o planejamento de rotas de cobertura e um enlace de comunicação de longo alcance e baixo consumo, papel para o qual a tecnologia LoRa é candidata natural.

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
