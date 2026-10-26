## Protótipo de comunicação LoRa entre dois dispositivos

Esta etapa corresponde à Atividade 10 do Objetivo 3 do plano de trabalho, que prevê o desenvolvimento de um protótipo de comunicação LoRa capaz de enviar e receber dados entre dois dispositivos. O protótipo foi concebido como o enlace entre um nó embarcado no drone (papel *node*) e uma estação de solo (papel *gateway*). Foram desenvolvidos o protocolo de mensagens, o firmware dos dois papéis, testes automatizados e ferramentas de análise e de registro. A gravação nas placas e o ensaio físico de envio e recebimento não foram realizados, porque os módulos de rádio ainda não foram adquiridos; toda a verificação descrita a seguir foi feita sem hardware de rádio, por compilação, testes, validação cruzada e simulação.

### Protocolo e firmware

O protocolo `cerise_proto` v1 foi implementado em C99 como biblioteca compartilhada pelo firmware e pelos testes. Cada quadro possui cabeçalho de 8 bytes (versão e tipo, flags, identificador de rede, origem, destino, número de sequência de 16 bits e tamanho do payload), payload de layout fixo por tipo e CRC-16/CCITT-FALSE, conforme ilustrado abaixo. Os tipos de mensagem foram alinhados com a frente de segmentação de áreas entre drones: `HEARTBEAT`, `POS` (telemetria de posição, bateria e contagem), `AREA_ASSIGN` (área atribuída pela estação de solo), `COVERAGE_DONE`, `COUNT_REPORT` e `ACK`, que devolve ao nó o RSSI e o SNR medidos no gateway. Três tipos propostos por aquela frente (`AREA_POLY`, `TASK_BID` e `TASK_AWARD`) foram incorporados como extensão aditiva, sem mudança de versão. O payload do `POS` foi dimensionado em 14 bytes para que o quadro completo, de 24 B, permaneça abaixo de 400 ms no ar até SF10.

![Formato do quadro cerise_proto v1, layout do payload de cada tipo de mensagem e tempo no ar por tipo em SF7, SF9 e SF10 (BW 125 kHz, CR 4/5)](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_formato_quadro.png){w=15}

O firmware foi escrito com PlatformIO (framework Arduino), RadioLib 7.8.1 [@radiolib] e U8g2, tendo a Heltec WiFi LoRa 32 V3 (ESP32-S3 e SX1262) como placa principal e a TTGO LoRa32 v2.1 (ESP32 e SX1276) como alternativa. O papel *node* gera um `POS` a cada 5 s com variação aleatória de ±10 %, aguarda o ACK por ToA(ACK) + 160 ms e repete a transmissão até três vezes com recuo aleatório exponencial; antes de transmitir, executa detecção de atividade no canal (CAD) e bloqueia quadros com mais de 400 ms no ar. O papel *gateway* valida os CRCs, descarta duplicatas e tráfego de outras redes, responde com ACK, estima a taxa de entrega de pacotes (PDR) por nó pelas lacunas de sequência, mantém uma fila de downlink e emite uma linha JSON por evento na serial. A troca de mensagens prevista é representada na figura a seguir.

![Sequência de mensagens entre node e gateway, com confirmação (ACK), retentativa após perda e downlink AREA_ASSIGN entregue logo após o ACK](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_sequencia.png){w=14}

Os parâmetros de rádio seguiram o enquadramento brasileiro: plano AU915-928 [@ttn_freq] [@anatel_res680], canal único de 916,8 MHz para a bancada, 14 dBm e limite de 400 ms no ar por quadro, compatível com o tempo de ocupação do item 10.2.5 do Ato ANATEL nº 14.448/2017 [@anatel_ato14448].

### Verificação e análise

A verificação foi organizada em quatro partes: (i) 30 testes unitários nativos (Unity, executados no PC); (ii) um espelho do protocolo em Python, comparado byte a byte com a implementação em C por meio de vetores aleatórios gerados por um programa em C; (iii) uma calculadora de tempo no ar baseada na formulação da Semtech [@semtech_an1200]; e (iv) uma simulação de eventos discretos de N drones compartilhando o canal, validada contra a expressão analítica do ALOHA puro [@abramson1970]. Os testes unitários cobrem, entre outros casos, a detecção de todos os erros de 1 bit (192), de 2 bits (18 336) e de rajadas de até 16 bits (2 952) em um quadro de 24 B, conforme a saída de terminal abaixo. Os cinco ambientes de firmware compilaram sem avisos; o *node* da Heltec V3 ocupa 22 400 B de RAM (6,8 %) e 376 241 B de Flash (11,3 %), e o *gateway*, 30 552 B (9,3 %) e 355 821 B (10,6 %).

![Saída do terminal com a execução dos 30 testes unitários nativos do protocolo (pio test -e native), todos aprovados](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/term_pio_test_native.png){w=11}

Tabela: Verificação do software do protótipo, realizada sem hardware de rádio
| Item verificado | Resultado |
|---|---|
| Testes unitários nativos (Unity) | 30/30 aprovados |
| Testes em Python (pytest) | 21/21 aprovados |
| Quadros válidos idênticos entre C e Python | 3 000/3 000 |
| Linhas JSON idênticas entre C e Python | 3 000/3 000 |
| Quadros corrompidos rejeitados com o mesmo código | 3 000/3 000 |
| Combinações de tempo no ar idênticas | 9 360/9 360 |
| Ambientes de firmware compilados | 5/5, sem avisos |

O tempo no ar do quadro `POS` resultou em 61,7 ms, 205,8 ms e 370,7 ms em SF7, SF9 e SF10. O `AREA_ASSIGN` (32 B) ocupa 452,6 ms em SF10 e, portanto, deve ser enviado com SF ≤ 9; SF11 e SF12 não comportam nenhum quadro dentro do limite de 400 ms.

A simulação totalizou 1 130 execuções (5 sementes de 1 800 s simulados por configuração). O simulador reproduziu a teoria do ALOHA puro com erro absoluto médio de 0,56 p.p. e máximo de 1,47 p.p. entre N = 2 e N = 20. A tabela a seguir e a figura subsequente apresentam a PDR média para SF9 e `POS` a cada 5 s.

Tabela: PDR simulada (%) em função do número de drones N, em SF9, com POS de 24 B a cada 5 s
| N | ALOHA puro | ALOHA + ACK | CSMA/CAD + ACK | Slotted ALOHA | TDMA + ACK |
|---|---|---|---|---|---|
| 2 | 91,1 | 99,7 | 100,0 | 93,0 | 100,0 |
| 5 | 71,4 | 67,6 | 100,0 | 83,7 | 100,0 |
| 8 | 54,5 | 26,6 | 97,9 | 72,8 | 100,0 |
| 10 | 46,0 | 15,1 | 62,6 | 67,2 | 100,0 |
| 12 | 38,4 | 8,1 | 44,0 | 61,0 | 100,0 |
| 15 | 30,1 | 3,2 | 26,5 | 54,2 | 83,5 |
| 20 | 19,2 | 0,7 | 11,2 | 43,7 | 62,6 |

![Resultados da simulação de eventos discretos em SF9: PDR, latência média e colisões no gateway em função do número de drones para cinco esquemas de acesso ao canal](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_sim_vs_N.png){w=16}

Três conclusões orientam o projeto. Primeiro, o ACK com retransmissão no mesmo canal piora o desempenho sob carga: com 10 drones, a ocupação somada do canal chega a 145 % (transmissões sobrepostas) e a PDR cai para 15,1 %, contra 46,0 % sem ACK; esse resultado motivou a alteração do recuo de retransmissão no firmware para uma janela proporcional a (ToA + espera do ACK)·2ᵏ. Segundo, a escuta prévia do canal (CAD) mantém PDR ≥ 97,9 % até 8 drones, mas também satura acima disso. Terceiro, o TDMA com slots sincronizados por GPS (slot de 401 ms em SF9) entrega 100 % até 12 drones, ao custo de maior latência (2 214 ms em média com 10 drones, contra 206 ms no ALOHA puro). Com efeito captura de 6 dB, a PDR do ALOHA puro com 10 drones sobe para 62,6 %, o que indica que a tabela é conservadora.

Por fim, o leitor serial do gateway (dashboard) foi exercitado com 600 s simulados de três drones a 1,0 km, 4,6 km e 6,4 km da estação, usando o caminho real de codificação e decodificação dos quadros sobre um canal sintético (log-distância com n = 3, sombreamento de 4 dB, colisões e 10 % de perda de ACK). Foram lidas 593 linhas sem nenhuma inválida, e a PDR calculada pelo dashboard coincidiu com a reportada pelo gateway simulado: 98,6 % (137/139), 97,8 % (135/138) e 94,8 % (129/136), conforme o painel abaixo.

![Painel gerado pelo dashboard do gateway a partir de fluxo serial simulado com três drones em SF9: RSSI, SNR, PDR por drone e trajetórias reportadas](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_dashboard_sim.png){w=15}

### Discussão e limitações

O software do protótipo está completo e verificado, mas a atividade permanece parcial: nenhum ensaio físico foi realizado, de modo que RSSI, SNR, PDR real, alcance e temporização do ACK não foram medidos. Os resultados do dashboard validam o software de registro, não o enlace, pois provêm de um canal sintético; a simulação adota sincronismo ideal no TDMA. O protótipo opera em canal único: a conformidade plena ao Ato nº 14.448/2017 requer salto de frequência com no mínimo 35 canais ou o enquadramento como modulação digital, além da homologação (alterações posteriores do Ato não foram verificadas). O protocolo também não possui cifragem nem autenticação. O próximo passo é adquirir duas placas Heltec V3 e antenas, gravar o firmware e executar o ensaio de alcance e PDR descrito na subseção seguinte.

Código e evidências: [repositório cerise-2026-lora-prototipo (privado)](https://github.com/cerise-ufg/cerise-2026-lora-prototipo)

## Projeto dos módulos de comunicação para os drones

Esta etapa corresponde aos itens 3 e 4 do Objetivo 5 do plano de trabalho, que preveem a construção dos módulos de comunicação definitivos e a adequação dos drones para recebê-los. Foi executada apenas a parte de projeto: especificação do hardware, lista de materiais, diagrama de ligação, gabinete paramétrico, requisitos de integração, estimativas de enlace e de energia e procedimento de ensaio. A fabricação dos módulos, a instalação nos drones e as medições dependem da aquisição das placas de rádio e permanecem pendentes.

### Arquitetura e requisitos

O módulo definitivo foi especificado como um modem LoRa transparente para o computador de bordo do drone, o mesmo que executa o planejamento de cobertura e a contagem de pessoas. O computador de bordo envia comandos de linha pela UART (3,3 V, GPIO47/48, 115200 bps) e recebe o log em linhas JSON, inclusive os downlinks `AREA_ASSIGN`; assim, o rádio não depende da controladora de voo, e a integração com MAVLink ou ROS 2 permanece no computador de bordo. A alimentação de 5 V vem de um BEC dedicado ou da placa de distribuição do frame, e a antena dipolo de 915 MHz fica na vertical, voltada para baixo, a pelo menos 10 cm do receptor GNSS e dos cabos dos ESCs. A lista de materiais prevê duas placas Heltec V3, antenas de 3 dBi (solo) e 2 dBi (drone), *pigtails* U.FL–SMA, baterias LiPo 1S, GPS opcional para o ensaio de alcance, BEC de 5 V e chicote JST-GH. A figura a seguir apresenta a ligação da bancada e a do módulo no drone.

![Diagrama de ligação: (a) protótipo de bancada com duas placas Heltec V3 e notebook de solo; (b) módulo definitivo no drone, com BEC de 5 V, UART para o computador de bordo e antena dipolo](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_diagrama_ligacao.png){w=15}

Foram documentados quinze requisitos (R1 a R15), que cobrem mensagens, taxa de telemetria, ocupação do canal, alcance, entrega, acesso múltiplo, massa, dimensões, alimentação, interface, fixação, antena, regulamentação, robustez e segurança da informação. A tabela a seguir resume os principais e indica a natureza de cada valor.

Tabela: Principais requisitos do módulo de comunicação definitivo e natureza dos valores de projeto
| Requisito | Valor de projeto | Natureza |
|---|---|---|
| Ocupação por quadro | ≤ 400 ms (POS até SF10; AREA_ASSIGN até SF9) | calculado |
| Alcance | ≥ 3 km com margem de 10 dB, drone a 60 m | estimativa |
| Acesso múltiplo | até 12 drones por canal em SF9 (TDMA) | simulação |
| Massa | ≤ 40 g; gabinete de 12,9 g | meta; estimativa |
| Alimentação | 5 V; 0,23 a 0,34 W médios | estimativa |
| Interface | UART 3,3 V, 115200 8N1, JST-GH 4 vias | especificação |
| Regulamentação | salto de frequência (≥ 35 canais) e homologação | pendente |
| Segurança | autenticação e cifragem AES-128-CCM | não implementado |

### Gabinete

O gabinete foi modelado de forma paramétrica em Python (trimesh e manifold3d), com base e tampa exportadas em STL. A base tem trilhos de apoio da placa, recortes para USB-C, conector SMA e passa-cabo, e quatro orelhas para parafusos M3 ou abraçadeiras, com furos espaçados de 30,5 mm no sentido do comprimento; a tampa tem janela para o display OLED e furos de ventilação sobre o amplificador de potência. As dimensões externas resultaram em 55,0 × 44,3 × 17,2 mm (internas de 51,4 × 26,7 × 14,0 mm). As malhas da base (7,68 cm³) e da tampa (2,45 cm³) são estanques, o que corresponde a 12,9 g de PETG com preenchimento total, valor tomado como limite superior. As dimensões da placa usadas no modelo (50,2 × 25,5 mm) ainda devem ser conferidas com paquímetro antes da impressão.

![Gabinete paramétrico do módulo: vista explodida da base e da tampa e cortes da base com as orelhas de fixação M3](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_gabinete.png){w=14}

### Enlace e energia estimados

O orçamento de enlace considerou 14 dBm, antenas de 2 dBi (drone) e 3 dBi (solo), 1,5 dB de perdas em cabos e conectores, margem de 10 dB, sensibilidade teórica do receptor e antena de solo a 2 m. Os alcances para o drone a 60 m foram estimados pelos modelos log-distância e Okumura–Hata [@hata1980], este com o drone tratado como antena elevada.

Tabela: Alcance estimado ar–solo por fator de espalhamento (14 dBm, drone a 60 m, margem de 10 dB)
| SF | Sensibilidade (dBm) | Perda máx. (dB) | Log-dist. n = 2,7 (km) | Hata suburbano (km) | Hata urbano (km) |
|---|---|---|---|---|---|
| 7 | −124,5 | 132,0 | 5,21 | 4,24 | 2,12 |
| 8 | −127,0 | 134,5 | 6,44 | 5,04 | 2,52 |
| 9 | −129,5 | 137,0 | 7,97 | 5,99 | 3,00 |
| 10 | −132,0 | 139,5 | 9,87 | 7,12 | 3,57 |

A altitude do drone tem efeito marcante: no modelo suburbano em SF9, o alcance estimado passa de 4,13 km a 30 m para 5,99 km a 60 m e 9,11 km a 120 m, conforme ilustrado abaixo. Esses valores são estimativas de projeto e precisam ser confirmados em campo.

![Efeito da altitude do drone no alcance estimado pelo modelo de Okumura–Hata suburbano, com 14 dBm e antena de solo a 2 m, para SF7, SF9, SF10 e SF12](E:/CERISE/FRENTES/NAVEGACAO AUTONOMA/LORA/evidencias/fig_alcance_altitude.png){w=13}

O consumo foi estimado com correntes típicas de datasheet do SX1262 (recepção de 4,6 mA; transmissão de 45 mA a 14 dBm e de 118 mA a 22 dBm) e com a hipótese de 40 mA para o ESP32-S3 com Wi-Fi e Bluetooth desligados. O consumo médio resultou entre 0,23 W e 0,34 W na entrada de 5 V (SF7 a SF10, com e sem OLED), o que corresponde a 0,11 % a 0,17 % de uma potência média de voo de referência de 200 W.

### Adequação dos drones e ensaio previsto

A adequação dos drones foi definida em nível de projeto: fixação do gabinete pelas orelhas M3 ou por abraçadeiras, com fita dupla-face de espuma para amortecimento; derivação de 5 V do BEC; chicote JST-GH de quatro vias (5 V, GND, TX e RX) até o computador de bordo; e posição da antena fora da sombra do frame de carbono. Para a validação, foi redigido um protocolo de ensaio de alcance e PDR com 200 quadros por ponto, distâncias de 50 m a 3 km e SF7, SF9 e SF10; com 200 quadros e PDR próxima de 0,9, a meia-largura do intervalo de confiança de 95 % é de aproximadamente 4,2 p.p. Para o firmware do módulo definitivo, foram previstos TDMA sincronizado por GPS, ACK apenas para mensagens críticas, salto de frequência sobre os canais AU915, ajuste de SF e potência a partir do RSSI e do SNR devolvidos no ACK, e cifragem com autenticação.

### Discussão e limitações

O projeto reúne os elementos necessários para a construção dos módulos assim que as placas forem adquiridas, e a interface com o computador de bordo já é compatível com o formato adotado pela frente de drones. Entretanto, nenhum módulo foi fabricado nem instalado, e os valores de alcance, massa e consumo são estimativas por modelo e por dados típicos de datasheet. A operação em voo também depende do salto de frequência, da homologação do equipamento e da implementação de autenticação, ainda não realizados.

Código e evidências: [repositório cerise-2026-lora-prototipo (privado)](https://github.com/cerise-ufg/cerise-2026-lora-prototipo)

<!-- REFERENCIAS
[@radiolib]: GROMEŠ, J. RadioLib: universal wireless communication library for embedded devices. Versão 7.8.1. Disponível em: https://github.com/jgromes/RadioLib.
[@ttn_freq]: THE THINGS NETWORK. Frequency plans by country. Disponível em: https://www.thethingsnetwork.org/docs/lorawan/frequencies-by-country/. Acesso em: out. 2026.
[@anatel_res680]: AGÊNCIA NACIONAL DE TELECOMUNICAÇÕES (ANATEL). Resolução nº 680, de 27 de junho de 2017. Aprova o Regulamento sobre Equipamentos de Radiocomunicação de Radiação Restrita. Brasília: Anatel, 2017.
[@anatel_ato14448]: AGÊNCIA NACIONAL DE TELECOMUNICAÇÕES (ANATEL). Ato nº 14.448, de 4 de dezembro de 2017. Aprova os requisitos técnicos para a avaliação da conformidade de equipamentos de radiocomunicação de radiação restrita. Brasília: Anatel, 2017.
[@semtech_an1200]: SEMTECH CORPORATION. AN1200.13: LoRa Modem Designer's Guide. Camarillo: Semtech, 2013.
[@abramson1970]: ABRAMSON, N. The ALOHA System: another alternative for computer communications. In: FALL JOINT COMPUTER CONFERENCE, 1970, Houston. Proceedings [...]. New York: ACM, 1970. p. 281-285.
[@hata1980]: HATA, M. Empirical formula for propagation loss in land mobile radio services. IEEE Transactions on Vehicular Technology, v. 29, n. 3, p. 317-325, 1980.
-->
