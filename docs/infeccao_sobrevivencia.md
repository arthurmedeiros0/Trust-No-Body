# Infecção, investigação e desfecho da campanha

Atualização: a integração agora usa os três padrões do grupo e inclui [conversas progressivas e seleção de padrões no Modo Teste](terceiro_padrao_conversas.md). Infectados exclusivos do terceiro padrão começam a expor no dia 17 e podem causar derrota no dia 18. As validações e hashes registrados abaixo são históricos da implementação anterior.

As correções foram feitas nos arquivos locais. Nenhum commit ou push foi realizado.

## Arquivos alterados

| Arquivos | Alteração |
| --- | --- |
| `dados/visitantes/marina.json` | Sexto exame e referências às imagens existentes da Marina |
| `casa/visitors.py` | Geração coerente da condição real e sintomas, diagnóstico futuro saudável, exposição e eliminação |
| `casa/survival.py` | Contagem de exposição, derrota por infecção e vitória após encerrar o dia 20 |
| `casa/days.py` | Encerramento idempotente do dia 20, sem iniciar o dia 21 |
| `casa/game.py` | Ação de eliminação, retirada dos atores, transição narrativa e bloqueio da exploração após o desfecho |
| `casa/visitor_ui.py` | Opção Eliminar, confirmação e apresentação futura do diagnóstico saudável |
| `casa/survival_ui.py` | Tela de vitória, causa da derrota com quebra de linha, dia do desfecho e nova partida |
| `main.py` | Rótulo “condição real” no Modo Teste, distinguindo-o do diagnóstico lógico |
| `README.md` | Descrição das regras atuais e instruções de uso |
| `tests/test_infeccao_sobrevivencia.py` (novo) | Treze testes de consistência, exposição, eliminação, Marina e desfechos, incluindo interface |
| `tests/support.py` | Condições saudáveis explícitas nas fixtures de exploração |
| `tests/test_calendario_balanceamento.py` | Isolamento dos recursos/calendário da infecção e encerramento final pela sessão |
| `tests/test_dias_tv.py` | Vitória após assistir ao boletim e encerrar o dia 20; eventos sem duplicação |
| `tests/test_investigacao_progressiva.py` | Nova opção de eliminar e isolamento da progressão dos exames |
| `tests/test_laura.py`, `tests/test_ricardo_caminhada.py`, `tests/test_ricardo_correcoes.py`, `tests/test_sobrevivencia.py`, `tests/test_visitantes.py` | Substituição das expectativas de condição pendente e sorteio independente pela condição real definida no início |

`personagens/visitantes/marina/investigacao/mao_tremendo.png` já estava presente como arquivo não rastreado no início da tarefa. Foi utilizado sem alterações; não foi criado nem substituído pelo agente.

## Marina

O cadastro agora contém `tremores_involuntarios` tanto em `investigation_features` quanto em `investigation`. As imagens são:

- Normal: `personagens/visitantes/marina/investigacao/mao_normal.png`.
- Alterada: `personagens/visitantes/marina/investigacao/mao_tremendo.png`.

Ambas existem e são carregadas pelo mecanismo já usado pelos outros exames. O original de tremores fornecido já possui transparência. No Modo Normal, o exame depende da leitura do boletim que o libera; no Modo Teste, está disponível imediatamente. Nenhuma imagem adicional precisa ser colocada no projeto.

## Condição real e sintomas

Todos os sete visitantes recebem `Visitor.diagnosis` igual a `infectado` ou `saudavel` ao iniciar a sessão. Primeiro é sorteada a condição; os sintomas são escolhidos entre combinações coerentes com ela.

Para encontrar essas combinações, o jogo enumera os seis sintomas e consulta exclusivamente `logica_infeccao.diagnosticar`, com todos os sintomas conhecidos e os IDs `boletim_07`, `boletim_14` e `boletim_17`. Não há cópia das implicações matemáticas. Infectados precisam ter retorno `infectado`; saudáveis não podem apresentar esse retorno com os dados completos. Um resultado inconclusivo obtido durante investigação parcial nunca define a condição real.

As probabilidades de sinais benignos de Gabriel e Antônio são preservadas na seleção ponderada: manchas de trabalho podem aparecer em Gabriel saudável, e Antônio saudável pode apresentar palidez e tremores de condições anteriores. Todos os conjuntos continuam passando pelo validador do grupo. Os intervalos de suprimentos dos cadastros e as regras/dias de chegada foram preservados.

Investigar, conversar, consultar notícias e passar os dias não sorteiam novamente a condição. O início de um teste específico de Gabriel ou Antônio pode selecionar outra condição, como já previsto no menu; nesse caso, as observações anteriores desse visitante são limpas para evitar evidências incompatíveis com o novo teste.

O diagnóstico lógico segue separado: envia cópias apenas dos sintomas observados e dos IDs das notícias assistidas. No Modo Teste recebe também os boletins do protocolo, sem alterar o histórico real de leitura. O retorno futuro `saudavel` é aceito e exibido somente se vier da função matemática; o jogo não o deduz por conta própria.

Se uma futura alteração da função não oferecer nenhuma combinação compatível com uma condição, a geração informa um erro explícito em vez de inventar regras ou produzir um visitante contraditório. A geração coerente requer a função matemática disponível; o fallback inconclusivo da consulta do jogador continua preservado.

## Dois dias de exposição

Atualização: a contagem respeita a publicação do padrão correspondente. O primeiro padrão só permite exposição no encerramento do dia 7; o segundo padrão exclusivo, no dia 14. Um infectado com ambos os padrões começa pelo primeiro marco. A leitura dos boletins não é necessária para ativar essa regra do mundo; continua obrigatória para o diagnóstico investigativo. Veja [correção e testes](dialogos_exposicao.md).

Ao encerrar o dia, a sessão verifica se existe pelo menos um visitante vivo, acolhido, realmente infectado e cujo padrão já foi publicado. Para isso, consulta a função do grupo com os sintomas reais completos e somente os IDs dos boletins com data de publicação até o dia encerrado. O sistema de sobrevivência incrementa uma única contagem diária, independentemente do número de infectados relevantes. O primeiro encerramento conta um dia; o segundo consecutivo causa derrota, registra o dia e mostra:

> Você permaneceu tempo demais em contato com pessoas infectadas. A infecção foi fatal.

Sem infectados relevantes vivos acolhidos no encerramento, a contagem volta a zero. Visitantes rejeitados ou aguardando não contam, assim como infectados exclusivamente pelo segundo padrão antes do dia 14. A lógica usa a condição real mesmo que nenhum exame tenha sido realizado. Relatórios e eventos de encerramento são idempotentes: repetir o encerramento não consome novamente recursos nem duplica a exposição.

## Eliminação

Interaja com um morador usando **E**, escolha **Eliminar** e confirme. Voltar/ESC cancela a confirmação. A ação retira o ator e sua posição da casa, marca o visitante como eliminado e morto e remove suas necessidades de consumo. Ele deixa de ser companhia e de causar exposição. A ação só pode ocorrer uma vez.

A sanidade diminui 2 para um infectado ou 3 para um saudável, respeitando o limite inferior zero já existente. A penalidade usa a condição real. Há uma transição escura breve e uma mensagem narrativa, sem imagens ou animações violentas. Os suprimentos já transferidos à casa não são concedidos novamente nem removidos.

## Vitória

Chegar ao dia 20 ainda permite explorar e assistir ao boletim da cura. Encerrar esse dia executa primeiro as verificações de comida, água, solidão e infecção. Somente sobreviver a todas elas produz a vitória. A derrota tem prioridade caso qualquer limite seja atingido no encerramento final.

A tela de vitória anuncia a cura e informa o dia 20. Enter/R ou o botão Nova partida reinicia a sessão. A exploração fica bloqueada após vitória ou derrota. Não existe avanço para o dia 21, nem novo consumo ao repetir o encerramento.

## Validação

Executado `python main.py --smoke-test`, com SDL sem janela: **164 testes, 159 aprovados e 5 falhas preexistentes**. Todos os treze testes novos passaram. Também foi executada isoladamente a nova suíte, com treze aprovações.

A cobertura nova inclui consistência dos sete visitantes em 100 sementes; condições específicas de Antônio/Gabriel; sintomas desconhecidos; exposição idempotente; múltiplos infectados; interrupção da exposição; penalidades e retirada de moradores; as duas imagens de tremores da Marina; confirmação e cancelamento; ausência de movimento após eliminação; vitória, derrotas no dia 20, congelamento da exploração e reinício. Os testes existentes de fome, sede, solidão, suprimentos e agenda continuam sendo executados.

As expectativas antigas foram atualizadas porque os novos requisitos substituem `diagnostico_pendente` por uma condição real e permitem encerrar o dia 20. As fixtures de exploração/calendário/recursos agora usam visitantes saudáveis para isolar essas funcionalidades; os novos testes exercitam explicitamente os infectados. Nenhuma falha foi ocultada com remoção ou desativação de testes.

As cinco falhas restantes foram reproduzidas com os módulos e fixtures anteriores carregados do HEAD em memória, sem sobrescrever os arquivos locais:

1. `test_cama_hud`: interação com a geladeira não produz o diálogo esperado.
2. `test_sobrevivencia`: mesma divergência na interação inicial com a geladeira.
3. `test_investigacao_progressiva`: prioridade retorna `resident` onde o teste espera `fridge`.
4. `test_editor_colisoes`: escala atual `0.44` difere do backup histórico `0.9`.
5. `test_ricardo_individual`: hash atual de `colisoes/cozinha.json` difere do registro histórico.

Esses problemas permanecem como pendências anteriores, sem alterações em cenários, colisões ou seus registros históricos. A interface foi exercitada por eventos e renderização Pygame em SDL sem janela; não houve validação manual em uma janela visível.

## Preservação

`logica_infeccao.py` não foi modificado. SHA-256 antes e depois:

`2D610702CC53398DAC1197CDCA900458E37575BF318D0AB9921950A264FBE26E`

Não houve alteração de implicações, imagens originais, sprites, cenários, colisões, diálogos, calendário de visitantes ou intervalos de suprimentos. Nenhuma regra matemática foi duplicada.
