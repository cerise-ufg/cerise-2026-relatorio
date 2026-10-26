# Comparação entre o plano original e o executado

A tabela a seguir compara as 14 atividades do plano de trabalho com o que foi efetivamente entregue. A situação de cada atividade foi atribuída a partir dos resultados medidos e das evidências guardadas nos repositórios: considera-se concluída a atividade cuja entrega prevista foi produzida e verificada, ainda que com ressalvas, e parcial aquela em que parte essencial da entrega não pôde ser realizada.

Tabela: Situação das atividades do plano de trabalho 2026
| Atividade | Entrega prevista | Situação | Observação |
|---|---|---|---|
| 1. Análise comparativa de modelos de geração 3D | Comparação de redes de geração 3D com textura e seleção do modelo | Concluída | 10 modelos levantados e 6 medidos; 4 bloqueados por falta de versão aarch64 ou acesso restrito |
| 2. Aplicativo com geração 3D | Versão funcional do aplicativo com objetos 3D texturizados | Concluída | Validada no emulador Android contra o servidor real; sem aparelho físico |
| 3. Aplicativo otimizado e relatório de desempenho | Otimização e relatório de desempenho | Parcial | Tempos medidos; tamanhos de GLB a remedir após a correção da textura |
| 4. Validação | Relatório de validação e resultados experimentais | Concluída | 58/58 testes; sem fotos tiradas pela câmera do celular |
| 5. Integração e servidor | Análise de gargalos e servidor para múltiplas requisições | Concluída | Erro de 90,9 % para 0 %; servidor não exposto publicamente |
| 6. Play Store | Publicação do aplicativo | Parcial | Pacote pronto e verificado; publicação não realizada |
| 7. Dataset | Dataset estruturado e documentado | Concluída | Braço virtual; 5.000 poses e 30.000 imagens |
| 8. Resultados do modelo | Resultados do modelo de pose de 2025 no novo dataset | Concluída | ADD@60 mm de 68,0 %; dados sintéticos |
| 9. Avaliação | Avaliação de precisão e robustez | Concluída | Somente em simulação, sem imagens reais |
| 10. Protótipo LoRa | Envio e recebimento entre dois dispositivos | Parcial | Software verificado sem rádio; ensaio físico pendente |
| 11. Modelo digital | Modelo físico e cinemático do braço | Concluída | Massas e inércias não calibradas |
| 12. Gêmeo digital | Gêmeo com o modelo de pose integrado | Concluída | Validado somente em simulação |
| 13. Segmentação de áreas | Software funcional de segmentação entre drones | Concluída | Validação 2D; sem SITL nem voo |
| 14. Relatório e artigo | Relatório técnico-científico | Concluída (este relatório) | Resultados rastreáveis aos repositórios |

Das 14 atividades, 11 foram concluídas e 3 ficaram parciais. Todas as conclusões, porém, têm ressalvas que precisam ser explicitadas. As atividades com robótica foram realizadas inteiramente em simulação, com o braço virtual servo6dof, e a validação com o braço físico e com imagens reais não foi feita. A segmentação de áreas e a colaboração entre drones foram validadas apenas em nível algorítmico, em planta, sem simulação de voo nem voo real. Os tempos de geração 3D, de servidor e de inferência foram medidos numa estação compartilhada com serviços de IA em produção e devem ser lidos como limites superiores.

As pendências decorrem de quatro causas principais. A primeira é a falta de hardware: as placas LoRa e as antenas não foram adquiridas, de modo que o protótipo LoRa (Atividade 10) não passou pelo ensaio físico entre dois dispositivos e, no Objetivo 5, a construção dos módulos de comunicação definitivos e a adequação dos drones ficaram apenas em projeto, assim como a adequação física dos drones para a detecção e a contagem de pessoas, cujo pipeline foi validado com o conjunto público VisDrone. A segunda são as ações que exigem autenticação do bolsista: a publicação na Play Store (Atividade 6) depende do Play Console, e a conclusão do benchmark de geração 3D depende do aceite de licenças no Hugging Face. A terceira é a decisão, ainda não tomada, sobre a exposição pública do servidor de geração 3D e do visualizador do gêmeo digital: nada foi exposto à internet, e o aplicativo só funcionará fora da rede interna depois dessa exposição; a publicação da política de privacidade no endereço público previsto também aguarda decisão. A quarta é um defeito encontrado no fim do período: a recodificação da textura em JPEG não ocorria no pipeline empacotado, o que invalidou os tamanhos de arquivo medidos na rodada de *presets* (Atividade 3). O defeito foi corrigido no servidor e no repositório, mas a rodada ainda precisa ser refeita.

# Próximos passos

Os próximos passos foram priorizados pelo quanto destravam as entregas pendentes:

- **Decisões e ações do bolsista**: decidir sobre a exposição pública do servidor de geração 3D e do visualizador do gêmeo digital; publicar a política de privacidade no endereço previsto; criar o aplicativo no Play Console e conduzir o teste interno, o teste fechado e o pedido de produção; aceitar no Hugging Face as licenças do Stable Fast 3D, do SPAR3D e do DINOv3 para completar o benchmark; e definir o acesso dos avaliadores aos repositórios privados.
- **Aquisição de hardware e ensaios de rádio**: adquirir as placas Heltec WiFi LoRa 32 V3 e as antenas da lista de materiais, gravar o firmware, executar o ensaio de alcance e de taxa de entrega e medir o consumo e a massa reais do módulo; em seguida, implementar o TDMA sincronizado por GPS, o salto de frequência e a cifragem com autenticação, encaminhar a homologação, testar a realocação entre drones com os rádios e instalar os módulos nos drones.
- **Remedições e consolidação**: reconstruir a imagem Docker do pipeline com a correção da textura e refazer, numa janela ociosa da GPU, a rodada de *presets*, os tamanhos de GLB e a suíte de carga do servidor; exigir textura JPEG nos testes automatizados; recalibrar a estimativa de tempo do *preset* alto; e ligar o monitoramento das métricas do servidor.
- **Validação em condições reais**: testar o aplicativo em aparelhos físicos Android e iOS, com fotografias da câmera, rede móvel e RA dos modelos gerados; capturar imagens do braço servo6dof físico para aplicar a etapa autossupervisionada de 2025 e validar o modelo de pose e o gêmeo digital fora da simulação, incluindo pontos-chave nas pinças para estimar a rotação e a abertura da garra; executar as missões de drones no QGroundControl e em SITL antes de voos no Campus Samambaia; e coletar imagens próprias em nádir para ajustar o detector de pessoas.

