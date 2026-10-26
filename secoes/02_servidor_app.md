## Servidor de geração 3D: arquitetura, gargalos e múltiplas requisições

Esta etapa corresponde à Atividade 5 do Objetivo 2 do plano de trabalho, que prevê a análise da arquitetura do servidor do aplicativo e a identificação de gargalos no atendimento a múltiplas requisições, e abrange também as metas associadas de otimização do servidor para solicitações simultâneas e de adequação da arquitetura para maior escalabilidade e confiabilidade. O servidor executa o modelo de geração 3D selecionado e otimizado na frente de modelos generativos (Hunyuan3D-2 Turbo [@hunyuan3d2]) e está hospedado na estação NVIDIA DGX Spark (GB10) do CERISE, compartilhada com os serviços de IA em produção.

### Arquitetura de 2025 e gargalos identificados

O servidor de 2025 era um aplicativo Flask executado com o servidor de desenvolvimento, em modo de depuração. A rota `POST /` recebia as fotografias, executava `time.sleep(67)` para simular o processamento e devolvia sempre o mesmo arquivo GLB. A leitura do código evidenciou os seguintes gargalos:

- processamento dentro da requisição, com a conexão HTTP presa durante toda a geração;
- ausência de fila e de limite de concorrência, de modo que pedidos simultâneos resultariam em chamadas concorrentes à mesma GPU e aos mesmos objetos do modelo;
- nenhum estado persistente (identificador de pedido, progresso, cancelamento ou retomada) e arquivos com nomes fixos, sujeitos a sobrescrita entre pedidos;
- ausência de validação de entrada, autenticação, TLS, métricas e registros estruturados.

Como a espera simulada não exercita a GPU, a arquitetura de 2025 foi reproduzida com o modelo real, substituindo o `sleep` pela chamada ao pipeline de geração. Foram medidos dois modos: sem trava, que corresponde ao código original ao receber o modelo, e com trava global, a correção mínima que serializa o uso da GPU, mas mantém as conexões presas. Sem trava, a partir de dois clientes simultâneos todos os pedidos falharam com HTTP 500, porque as chamadas concorrentes compartilham o *scheduler* da difusão, cujo índice de passo é estado mutável, conforme ilustrado abaixo.

![Execução da arquitetura de 2025 com o modelo real e sem trava: a partir de dois clientes simultâneos todos os pedidos falham com HTTP 500 devido ao estado compartilhado do scheduler de difusão](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/srv_term_baseline_2025_nolock.png){w=14}

### Arquitetura implementada em 2026

A nova arquitetura separa a recepção dos pedidos do processamento na GPU, conforme a figura a seguir. A API, em FastAPI [@fastapi], nunca acessa a GPU: valida e normaliza a foto (até 15 MB, orientação EXIF aplicada, metadados e GPS removidos), registra o job e responde `202` em milissegundos, com identificador, posição e estimativa de tempo. Os jobs ficam numa fila persistente em SQLite no modo WAL [@sqlitewal], com reserva atômica e ordem FIFO com prioridade por *preset* e envelhecimento (deslocamentos de 0, 30 e 90 s para os *presets* rápido, padrão e alto). Um processo de GPU carrega o modelo uma vez e processa um job por vez (configuração de produção) ou dois *slots* com pesos compartilhados e travas por componente; aplica tempo limite, devolve à fila o job interrompido por reinício ou falta de memória e só aceita novo job com ao menos 10 GB livres no hospedeiro. Completam a arquitetura o cache por *hash* SHA-256 da imagem, das opções e da versão do pipeline, a coalescência de pedidos idênticos, os limites de fila (32 jobs, com resposta 429), de pedidos por cliente e de taxa, a retenção máxima de 7 dias e a implantação em Docker Compose com reinício automático e porta publicada apenas na interface de *loopback*.

![Arquitetura de 2026: API assíncrona, fila persistente em SQLite e processo de GPU com o modelo carregado; acesso restrito ao loopback da estação e a encaminhamento local por SSH](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/srv_arquitetura_2026.png){w=16}

### Testes de carga e resultados

Os testes foram executados em 26/10/2026 com os serviços de produção de IA ativos na mesma GPU, de modo que os valores refletem uma máquina compartilhada. O cliente de carga (asyncio e httpx) rodou no próprio hospedeiro, excluindo a latência de rede, e utilizou 64 imagens (renderizações do Google Scanned Objects e fotografias CC0) sem repetição dentro de cada cenário. O cenário principal consistiu em rajadas de 1, 2, 4, 8 e 16 clientes simultâneos, totalizando 33 jobs do *preset* rápido por configuração, com sondas de leitura paralelas para medir a responsividade.

Tabela: Resumo por configuração (33 jobs do preset rápido em rajadas de 1 a 16 clientes; latência do envio ao GLB baixado)
| Configuração | Atendidos | Latência p50 / p95 (s) | p95 com 16 clientes (s) | Vazão com 16 clientes (jobs/min) | Leituras com GPU ocupada, p95 / p99 (ms) |
|---|---|---|---|---|---|
| 2025, sem trava | 3/33 | 12,3 / 12,5 (só 1 cliente) | sem sucesso | 0 | 102,4 / 213,0 |
| 2025, com trava | 33/33 | 52,1 / 199,0 | 210,2 | 4,37 | 123,4 / 228,6 |
| 2026, fila e 1 *worker* | 33/33 | 49,6 / 174,1 | 184,1 | 4,99 | 6,6–6,7 / 8,3–8,6 |
| 2026, fila e 2 *slots* | 33/33 | 46,5 / 155,6 | 164,4 | 5,63 | 6,6–6,7 / 9,0–9,2 |

A taxa de erro caiu de 90,9 % (30 de 33 pedidos na arquitetura de 2025 sem trava) para zero nas configurações novas. Com 16 clientes, a fila com 1 *worker* reduziu a latência p95 em 12 % e elevou a vazão em 14 % em relação à versão síncrona com trava; com 2 *slots*, os ganhos foram de 22 % e 29 %. A espera passou a ocorrer na fila, sem conexão presa, e as rotas de leitura responderam de 15 a 19 vezes mais rápido que o Flask no p95, inclusive sob *polling* de cerca de 50 req/s (9.569 sondas, sem erros).

![Latência ponta a ponta (p50 e p95), espera na fila, vazão e taxa de erro em função do número de clientes simultâneos para as quatro configurações](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/srv_carga_latencia_vazao_erros.png){w=15}

Tabela: Cenários adicionais na configuração de produção (1 worker)
| Cenário | Pedidos | Atendidos | Execuções na GPU | Resultado |
|---|---|---|---|---|
| Reenvio de imagens já processadas (cache) | 10 | 10 | 0 | 0,02 s por pedido |
| 8 clientes com a mesma imagem nova (coalescência) | 8 | 8 | 1 | 12,31 s (p50) |
| Misto com prioridade por *preset* (12 rápidos, 4 padrão) | 16 | 16 | 16 | p50: rápido 66,0 s; padrão 131,9 s |
| Misto em FIFO pura (mesmos pedidos) | 16 | 16 | 16 | p50: rápido 99,7 s; padrão 85,1 s |
| 16 clientes com fila máxima de 8 | 16 | 9 | 9 | 7 recusados com 429 em 0,32 s |

A prioridade reduziu em 34 % a latência mediana dos jobs rápidos, com média geral praticamente inalterada (86,0 s para 82,9 s); a espera máxima de um job padrão aumentou 29,9 s, dentro do envelhecimento de 30 s configurado, sem inanição. O limite de fila converteu esperas de até 192 s em recusas imediatas que o aplicativo pode exibir ao usuário.

![Responsividade das rotas de leitura com a GPU ocupada, em escala logarítmica: Flask de 2025 contra a API de 2026](E:/CERISE/FRENTES/REALIDADE AUMENTADA/GERACAO_3D/evidencias/srv_carga_api_responsividade.png){w=15}

### Discussão e limitações

O gargalo dominante é a própria GPU: com 2 *slots*, a execução mediana de cada job subiu de 11,9 s para 21,0 s, enquanto a espera média nas travas foi de 0,05 a 0,2 s por componente, razão pela qual dois *slots* rendem só 13 % mais vazão que um. A capacidade sustentada medida é de cerca de 5 jobs/min no *preset* rápido; um objetivo de p95 de 1 min comporta rajadas de 4 a 5 pedidos (p95 de 46,7 s com 4 clientes e de 93,5 s com 8). O pico por job foi de 18,9 GiB alocados (22,9 GiB do processo), abaixo do teto de 24 GiB da frente. Os 18 testes automatizados do servidor, com motor simulado, foram aprovados, incluindo retomada após reinício, retenção e *backpressure*. Em dois desligamentos não planejados da estação, os contêineres retornaram automaticamente com a fila preservada; uma corrupção do cache de compilação do numba causada pelo primeiro foi corrigida passando esse cache para memória temporária.

Como limitações, as configurações foram medidas em sequência numa máquina compartilhada, sem controle da carga de fundo; o cenário misto não incluiu jobs do *preset* alto; a escala para várias GPUs ou máquinas foi apenas projetada; o monitoramento sobre as métricas não foi ligado; e o servidor não foi exposto publicamente, sendo acessível apenas por encaminhamento local. Uma proposta de exposição, com opções e riscos, está documentada no repositório e aguarda decisão.

Código e evidências: [repositório cerise-2026-gen3d, pasta server (privado)](https://github.com/cerise-ufg/cerise-2026-gen3d)

## Aplicativo CERISE AR com geração de objetos 3D texturizados

Esta etapa corresponde à Atividade 2 do Objetivo 1 do plano de trabalho, que prevê a integração do modelo de rede neural selecionado ao aplicativo e a entrega de uma versão funcional com suporte à geração de objetos 3D texturizados. O aplicativo CERISE AR, reescrito em 2026 em React Native com Expo [@expo] para Android e iOS, passou a permitir que o usuário fotografe um objeto, envie a imagem ao servidor descrito na subseção anterior, acompanhe a fila e o processamento, baixe o modelo GLB texturizado e o visualize em 3D e em realidade aumentada.

### Implementação

Aplicativo e servidor foram desenvolvidos em paralelo sobre um contrato REST fixado previamente (`/api/v1`: verificação de estado, envio da foto com as opções, consulta do job, *download* do GLB e da miniatura e exclusão). Enquanto o servidor não estava disponível, um servidor simulado (*mock*) reproduziu o contrato, devolvendo GLBs de exemplo identificados na tela como tal. No aplicativo, destacam-se:

- cliente da API com envio multipart com progresso, tempo limite, cancelamento e mensagens de erro em português;
- gerenciador de jobs com *polling* (2 s na fila e 1,5 s em processamento), recuo exponencial em falhas de rede, *download* do GLB e da miniatura, medição do tempo de cada etapa, persistência local e retomada de jobs ao reabrir o aplicativo;
- leitura do cabeçalho do GLB para obter a caixa envolvente com as transformações da cena, usada para normalizar a escala na RA;
- visualizador 3D sem rede, com o `<model-viewer>` [@modelviewer] embutido numa WebView;
- RA com ViroReact [@viro] (posicionamento por toque, escala e rotação), aberta somente após a confirmação de suporte do ARCore/ARKit, o que eliminou o encerramento do processo observado quando a sessão não podia ser criada.

No servidor, o motor de geração reporta o progresso por etapa e entrega o GLB no formato exigido pelo aplicativo: glTF 2.0 [@gltf2], apoiado em y = 0, centralizado, maior dimensão de 0,30 m, textura JPEG e sem compressões Draco, meshopt ou KTX2; a rota legada de 2025 passou a devolver um modelo efetivamente gerado. Num teste a partir de um computador externo, uma foto CC0 no *preset* padrão produziu o GLB em 16,1 s (15,3 s de GPU), aprovado no Khronos glTF-Validator sem erros nem avisos. Esse teste revelou que a textura era gravada em PNG; corrigido o pós-processamento, o GLB caiu de 2,97 MB para 0,72 MB (−76 %) no *preset* padrão e de 2,60 MB para 0,44 MB (−83 %) na rota legada, sem alteração mensurável no tempo de geração.

### Validação ponta a ponta com o servidor real

A integração foi validada no emulador Android 16 (API 36, x86_64 com tradução ARM), que alcançou o servidor por encaminhamento SSH local restrito ao *loopback*, sem exposição pública. Foram usadas imagens reais CC0 de objetos (pato de borracha, bule de prata e estatuetas de gato e de burro), escolhidas pelo seletor de fotos do sistema; não se trata de fotografias tiradas pela câmera de um celular. Para observar a fila, um segundo cliente enviou um job do *preset* alto imediatamente antes de um pedido do aplicativo, e a foto do pato foi reenviada para exercitar o cache. Os tempos foram registrados pelo aplicativo e conferidos com o estado dos jobs na API.

Tabela: Tempos medidos pelo aplicativo no emulador contra o servidor real (com textura e remoção de fundo; tamanho do GLB em KiB, como exibido no aplicativo)
| Objeto e *preset* | Envio (s) | Fila: app / servidor (s) | Geração no app / execução no servidor (s) | Download (s) | Total (s) |
|---|---|---|---|---|---|
| Pato, rápido (340 KiB) | 0,41 | 1,25 / 0,24 | 11,19 / 11,20 | 0,67 | 13,5 |
| Burro, rápido (398 KiB) | 0,49 | 1,35 / 0,20 | 11,24 / 11,26 | 0,45 | 13,5 |
| Bule, padrão (622 KiB) | 0,66 | 1,36 / 0,09 | 14,42 / 14,73 | 0,61 | 17,1 |
| Gato, alto (1,44 MiB) | 0,39 | 1,21 / 0,22 | 29,04 / 30,17 | 0,90 | 31,5 |
| Gato, padrão, atrás de 1 job alto | 0,40 | 28,25 / 27,85 | 15,81 / 15,88 | 0,46 | 44,9 |
| Pato, rápido, reenvio (cache) | 0,29 | 0,28 / 0 | 0 / 0 | 0,43 | 1,0 |

Sem concorrência, o tempo percebido variou de 13,5 s (rápido) a 31,5 s (alto), dominado pela execução na GPU (83 % a 96 % do total); envio e *download* somaram no máximo 1,3 s. A fila de 1,2 a 1,4 s registrada no aplicativo é artefato da resolução do *polling*, pois o servidor registrou de 0,09 a 0,24 s. Com um job alto à frente, a espera (27,85 s no servidor) praticamente igualou a execução desse job (28,2 s), como esperado para um único processo de GPU. Todos os sete GLBs gerados nesse teste tinham textura JPEG, maior dimensão de 0,30 m e nenhuma extensão de compressão.

![Fluxo de geração no Android com o servidor real: envio da foto, geração da malha, texturização multivista e resultado com o GLB texturizado baixado em 13,5 s no total](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig14-android-real-fluxo-geracao.png){w=16}

![Fila e cache reais: pedido em posição 1 atrás de um job de outro cliente, geração após a fila, resultado em 44,9 s e reenvio da mesma foto atendido pelo cache do servidor em 1,0 s](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig15-android-real-fila-cache.png){w=16}

![Tempo por etapa de cada pedido medido no aplicativo, com o tempo de execução informado pelo servidor](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig19-grafico-tempos-real.png){w=15}

O teste com o servidor real motivou ajustes no aplicativo, todos em JavaScript. O *download* de um GLB de 398 KiB levava 5,0 s, embora o servidor respondesse em cerca de 1 ms; após deixar de gravar a lista de modelos a cada evento de progresso e baixar a miniatura em paralelo, o *download* caiu para 0,45 s e o total, de 18,0 s para 13,5 s (as mudanças foram aplicadas juntas, sem isolar a contribuição de cada uma). Passaram também a ser tratados os estados de servidor iniciando ou em pausa e as respostas do cache, e a exclusão de um modelo no aplicativo passou a apagar a cópia no servidor, verificado pela consulta do job, que passou de 200 para 404.

![Visualizador 3D do aplicativo com modelos gerados pelo servidor a partir das fotos: pato no preset rápido, bule no padrão e gato no alto, com maior dimensão de 0,30 m lida do GLB](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig17-android-real-visualizador-3d.png){w=13}

### iOS

O *build* Release para o Simulador iOS foi gerado num Mac mini M4 (Xcode 26.6) em 72 s de compilação, após a instalação de 100 dependências nativas, resultando num pacote de 41 MB (iOS mínimo 17.6), executado no simulador do iPhone 17 Pro. Como a biblioteca nativa de RA não possui versão para simulador, esse *build* exclui o módulo de RA. O fluxo de geração, a lista de modelos e o visualizador 3D foram validados apenas contra o servidor simulado, como ilustrado abaixo; o modelo exibido é um GLB de exemplo, não gerado a partir da foto. O iOS não foi retestado contra o servidor real, pois o Mac utilizado não alcança a estação; as mudanças da integração são apenas de JavaScript e valem para as duas plataformas.

![Simulador iOS no iPhone 17 Pro: tela inicial, pedido na fila, resultado e visualizador 3D com o GLB de exemplo devolvido pelo servidor simulado](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig05-ios-simulador.png){w=16}

### Limitações

A validação com o servidor real ocorreu apenas no emulador e pela rede interna, sem teste em aparelho físico, em rede móvel ou com fotografias da câmera. A RA dos modelos gerados não foi validada nesta versão, porque o ARCore não carrega no emulador x86_64 com bibliotecas ARM traduzidas e o simulador iOS não executa a biblioteca de RA. A estimativa de espera exibida na fila foi superestimada para o *preset* alto (1 min 21 s para 28 s reais), por depender de um valor inicial de 82 s ainda não recalibrado no servidor. Por fim, o uso fora da rede interna depende da exposição pública do servidor, ainda não decidida.

Código e evidências: [repositório cerise-ar, branch feat/2026-gen3d-playstore, pull request em rascunho (privado)](https://github.com/cerise-ufg/cerise-ar/pull/1)

## Adequação do aplicativo para publicação na Play Store

Esta etapa corresponde à Atividade 6 do Objetivo 2 do plano de trabalho, que prevê a publicação do aplicativo na Play Store. O trabalho concentrou-se na adequação técnica e normativa do aplicativo e na preparação e verificação do pacote de publicação. A publicação propriamente dita não foi realizada: as etapas no Play Console exigem autenticação na conta de desenvolvedor, e dois pré-requisitos, a publicação da política de privacidade e a exposição pública do servidor de geração 3D, aguardam decisão.

### Adequação técnica

A configuração nativa foi declarada nos arquivos de configuração do Expo e em *plugins* próprios, de modo que os projetos Android e iOS são gerados de forma reprodutível. A versão 1.1.0 (código de versão 110) declara apenas as permissões de câmera e de internet e bloqueia no manifesto as permissões acrescentadas por bibliotecas (gravação de áudio, armazenamento e mídia, localização, sobreposição de janelas, identificador de publicidade, vibração e NFC). A galeria usa o seletor de fotos do sistema, que dispensa permissão de mídia. As arquiteturas nativas foram restritas a `armeabi-v7a` e `arm64-v8a`, as únicas distribuídas pelo ViroReact; com as quatro arquiteturas padrão, o aplicativo encerrava ao iniciar em dispositivos x86_64. O tráfego sem criptografia foi proibido, exceto para endereços locais de teste, e os artefatos foram assinados com uma chave de *upload* dedicada (RSA 4096), mantida fora do controle de versão, para uso com o Play App Signing. Após a integração com o servidor real, o AAB e o APK foram recompilados e as verificações foram repetidas, com os resultados a seguir.

Tabela: Verificações no AAB e no APK release finais do CERISE AR 1.1.0
| Requisito | Resultado medido |
|---|---|
| Nível de API | targetSdkVersion 36, compileSdk 36, minSdk 24 |
| Páginas de memória de 16 KB [@android16kb] | 30/30 bibliotecas de 64 bits alinhadas a 16 KB no AAB e no APK; zipalign -c -P 16 bem-sucedido |
| Permissões no APK | CAMERA, INTERNET, ACCESS_NETWORK_STATE e permissão interna do AndroidX |
| Componentes exportados | apenas a atividade principal e um receptor do AndroidX protegido por permissão |
| Assinatura | APK e AAB assinados com o certificado de upload do CERISE/EMC/UFG |
| Tamanho | AAB de 55,16 MB; download estimado de 35,65 MB (arm64-v8a) e 34,09 MB (armeabi-v7a) |

A restrição de arquiteturas, além de eliminar a falha em x86_64, reduziu o AAB de 75,84 MB para 55,16 MB (−27 %) e o APK universal de 116,82 MB para 83,30 MB (−29 %), conforme a figura a seguir, cujos valores estão em MiB.

![Verificação do AAB e do APK release: alinhamento das bibliotecas nativas a páginas de 16 KB, nível de API alvo 36 e permissões finais](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig07-terminal-playstore-16kb.png){w=15}

![Tamanho dos artefatos Android antes e depois da restrição às arquiteturas ARM e tamanho de download estimado por aparelho, em MiB](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig11-grafico-tamanhos.png){w=14}

### Adequação normativa e pacote da loja

Os requisitos normativos e de conteúdo foram tratados da seguinte forma:

- política de privacidade em português, conforme a LGPD [@lgpd], descrevendo o uso da câmera e das fotos, o envio ao servidor do CERISE apenas para gerar o modelo, a exclusão em até 7 dias (ou imediata quando o usuário exclui o modelo), a ausência de anúncios e de rastreamento e os direitos do titular;
- respostas preparadas para o formulário de segurança dos dados, o questionário de classificação etária IARC e a definição de público-alvo (13 anos ou mais);
- remoção do catálogo da versão de loja de modelos de personagens de franquias, em atenção à política de propriedade intelectual, e créditos das licenças dos demais modelos na tela Sobre;
- atualizações remotas restritas ao código JavaScript interpretado, sem *download* de código nativo;
- ficha da loja com limites de texto verificados automaticamente (nome com 26 de 30 caracteres, descrição curta com 69 de 80, descrição completa com 2.251 de 4.000 e notas da versão com 397 de 500), ícone 512×512, recurso gráfico 1024×500 e sete capturas de tela, três delas do teste com o servidor real;
- guia de publicação com as etapas de teste interno, teste fechado com 12 testadores por 14 dias (exigido de contas pessoais novas) e produção.

![Pacote gráfico da Play Store: recurso gráfico 1024×500, ícone 512×512 e sete capturas de tela do emulador, das quais as de números 2, 3 e 7 provêm do teste com o servidor 3D real](E:/CERISE/FRENTES/REALIDADE AUMENTADA/APP_CERISE_AR/evidencias/fig10-pacote-play-store.png){w=16}

### Situação e pendências

O pacote de publicação está pronto e verificado, mas o aplicativo não foi publicado, razão pela qual a atividade é considerada parcialmente concluída. Permanecem pendentes: a criação do aplicativo no Play Console, o envio do AAB ao teste interno, a condução do teste fechado e o preenchimento dos formulários, que exigem autenticação na conta de desenvolvedor; a publicação da política de privacidade no endereço público previsto, que respondia com erro 404 em 26/10/2026; e a exposição pública do servidor de geração 3D, pois o endereço padrão configurado no aplicativo ainda não responde e a revisão de produção não deve ser solicitada antes disso. Caso a exposição adote chave de API, o aplicativo deverá ser recompilado com a chave. Também devem ser verificadas a disponibilidade do nome de pacote na loja e a cópia de segurança da chave de *upload*. No iOS, a compilação assinada para aparelho e o envio ao TestFlight foram documentados, mas não executados.

Código e evidências: [repositório cerise-ar, pull request em rascunho com o pacote da loja (privado)](https://github.com/cerise-ufg/cerise-ar/pull/1)

<!-- REFERENCIAS
[@hunyuan3d2]: TENCENT HUNYUAN3D TEAM. Hunyuan3D 2.0: scaling diffusion models for high resolution textured 3D assets generation. arXiv preprint arXiv:2501.12202, 2025.
[@fastapi]: RAMÍREZ, S. FastAPI. Disponível em: https://fastapi.tiangolo.com.
[@sqlitewal]: SQLITE. Write-Ahead Logging. Disponível em: https://www.sqlite.org/wal.html.
[@expo]: EXPO. Expo documentation. Disponível em: https://docs.expo.dev.
[@modelviewer]: GOOGLE. model-viewer: easily display interactive 3D models on the web and in AR. Disponível em: https://modelviewer.dev.
[@viro]: REACTVISION. ViroReact: AR and VR for React Native. Disponível em: https://github.com/ReactVision/viro.
[@gltf2]: KHRONOS GROUP. glTF 2.0 Specification. Beaverton: Khronos Group, 2021. Disponível em: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html.
[@android16kb]: GOOGLE. Support 16 KB page sizes. Android Developers. Disponível em: https://developer.android.com/guide/practices/page-sizes.
[@lgpd]: BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). Diário Oficial da União, Brasília, DF, 15 ago. 2018.
-->
