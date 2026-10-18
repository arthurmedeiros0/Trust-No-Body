# Investigação progressiva e moradores

A partida começa sem conhecimento dos seis sinais físicos. Ricardo e Laura continuam conversando e podendo ser aceitos/rejeitados pela porta, mas **Investigar fica oculto** até o protagonista assistir a um boletim que ensine algum exame. O requisito anterior de conversar ou examinar antes de confirmar uma decisão continua sendo atendido por conversar; não é necessário ter investigação desbloqueada.

## Notícias e aprendizado

| Boletim assistido | Investigações disponíveis após a recapitulação |
|---|---|
| Dia 1 | Nenhuma |
| Dia 4 | Mãos e dentes |
| Dia 7 | Mãos, dentes e olhos |
| Dia 10 | Mãos, dentes, olhos, pescoço e palidez |
| Dia 14 | Todos os seis, incluindo tremores |
| Dia 17 | Revisão dos seis; não adiciona outro exame |

Chegar ao dia correspondente não ensina nada automaticamente. `NewsArchive.watch` notifica a primeira leitura do boletim; `VisitorSession` entrega a lista explícita `investigations` ao conhecimento do protagonista. O aprendizado é permanente até reiniciar, e assistir novamente não repete efeitos ou avisos.

Os dias 7, 10, 14 e 17 recapitulam os sinais anteriores listados na tabela. Assim, perder uma transmissão não bloqueia esses exames permanentemente, desde que o jogador assista à recapitulação posterior. Boletins sem menções explícitas não desbloqueiam outros sinais. A notícia da cura do dia 20 permanece igual.

O texto do dia 4 agora menciona somente mãos e dentes; olhos aparecem no dia 7. O dia 10 não antecipa tremores, que são apresentados no dia 14. As informações narrativas dos dois padrões e do protocolo continuam disponíveis nos boletins, sem qualquer código que as interprete para diagnosticar pessoas.

Ao fechar a televisão, uma mensagem informa somente as investigações novas. Enter/Espaço fecha. Se vários boletins forem vistos antes de sair da TV, os novos sinais são reunidos em um aviso, sem nomes repetidos.

## Visitantes e moradores

Na porta, somente os exames conhecidos aparecem. Imagens de exames bloqueados também são protegidas na função que as fornece; forçar uma página de imagem desconhecida volta ao menu, sem mostrar a imagem ou o nome do sinal.

Dentro da casa, aproxime-se de um morador aceito e vivo e pressione **E**. Aparecem Conversar, Investigar (se houver exames conhecidos) e Voltar. ESC retorna uma tela por vez e fecha a interação no menu inicial. Não há aceitar novamente, rejeitar, expulsar ou eliminar no menu de moradores.

As conversas internas usam poucas falas próprias: Ricardo comenta a organização e a cautela diante das notícias; Laura fala da segurança da casa e da preocupação com a família. Não repetem o pedido para entrar. O painel de investigação é o mesmo `VisitorUI` usado na porta, com os mesmos assets e o mesmo objeto `Visitor`.

A escolha da tecla E compara a distância do objeto interativo mais próximo com a distância entre a hitbox dos pés do protagonista e a do morador. O alcance permanece em 58 pixels do mundo. Só moradores do cômodo atual entram na seleção; empates mantêm a ordem anterior de objetos. Uma única interface é aberta. Cama, portas, televisão e geladeira continuam usando suas interações existentes.

Ao começar a interação, o morador volta à pose parada. A interface modal pausa a movimentação do protagonista e dos NPCs, como as outras interfaces existentes. Ao fechar, a atualização normal dos atores retorna. Sprites, escala, animações e colisões não foram modificados nesta etapa.

## Três estados separados

- **Reais:** `Visitor.symptoms`, os seis booleanos sorteados uma vez, não são alterados pela aprendizagem ou observação.
- **Conhecidos:** `VisitorSession.medical.known`, sinais ensinados pelas notícias assistidas, compartilhados por todos os visitantes/moradores.
- **Observados:** `medical.observations[visitor_id][feature]`, somente os valores efetivamente examinados naquela pessoa. Não são preenchidos automaticamente pelo conhecimento.

`medical.status(id, feature)` retorna `desconhecido`, `nao_observado`, `presente` ou `ausente`. O registro existente `Visitor.examined` continua sustentando a indicação `[visto]`. Ricardo e Laura mantêm seus próprios sintomas e imagens; o rosto normal compartilhado da Laura continua servindo para olhos e palidez normais.

Não há diário visual ou conclusões automáticas. O registro interno está preparado para uma futura interface, sem antecipar valores não observados.

## Arquivos desta etapa

Criados:

- `casa/medical_knowledge.py`: aprendizado, fila de avisos, observações e consulta de estado.
- `tests/test_investigacao_progressiva.py`: testes dos desbloqueios e moradores.
- `conferir_investigacao_progressiva.py`, este relatório e `docs/investigacao_*.png`: roteiro e capturas.

Modificados:

- `casa/news.py`: lista de sinais ensinados em cada boletim.
- `dados/noticiarios.json`: metadados dos desbloqueios e textos/recapitulações dos marcos médicos.
- `casa/visitors.py`: conhecimento por partida e aprendizado no evento de notícia assistida.
- `casa/visitor_ui.py`: filtro/proteção de exames e modo de morador reutilizando o painel.
- `casa/game.py`: seleção de interação com NPC, pausa modal e aviso após TV.
- `dados/visitantes/ricardo_dialogos.json` e `laura_dialogos.json`: falas internas separadas das conversas da porta.
- `tests/support.py`, `tests/test_laura.py` e `tests/test_agendamento_visitantes.py`: preparação explícita de conhecimento nos testes históricos de assets/UI e assinatura da UI simulada. A partida real continua começando sem exames.
- README: controles e progresso atual.

## Validação e pendências

**134 testes passaram** com `python main.py --smoke-test`, incluindo dez novos. Eles verificam início bloqueado, decisões na porta, progressão e recuperação por notícias posteriores, idempotência, aviso após TV, proteção contra acesso direto, observações distintas por personagem, conversas internas, distância/prioridade, pausa/retorno, sono, mudanças de cômodo e reinício. As regressões existentes cobrem sobrevivência, agenda, imagens, animações e colisões.

`python conferir_investigacao_progressiva.py` executa o roteiro das capturas. Para chegar aos dias avançados, injeta estoque **somente nesse script de validação**, nunca na partida normal. Usa o sono e o noticiário reais; nenhuma regra de fome, sede, sanidade ou solidão foi alterada.

- [Porta sem investigação no dia 1](investigacao_porta_bloqueada.png)
- [Morador sem investigação no dia 1](investigacao_morador_dia1.png)
- [Notícia do dia 4](investigacao_tv_dia4.png)
- [Aviso de descoberta](investigacao_descoberta.png)
- [Ricardo: mãos e dentes](investigacao_ricardo_dia4.png)
- [Laura: seis exames no dia 14](investigacao_laura_dia14.png)

As capturas foram inspecionadas visualmente em SDL dummy; não houve sessão manual completa. Permanecem pendentes diário visual, eliminação de moradores, persistência em disco e lógica acadêmica de infecção. `logica_infeccao.py` e as interfaces reservadas ao grupo permanecem preservados. Nenhum commit ou push foi realizado.
