# Sobrevivência, recursos e introdução

**Contagem atual:** consulte [previsão de privação](previsao_privacao.md). A HUD inclui o dia atual sem ração, sem registrar privação antecipadamente. A derrota é verificada somente ao dormir: dia 3 sem água ou dia 4 sem comida, mantendo tolerância no dia 1.

**Regras atuais:** [tolerância do dia 1 e sanidade diária](tolerancia_dia1.md). O dia 1 não consome recursos nem acumula privação; sanidade e solidão contam normalmente desde o início. Os detalhes e capturas abaixo também registram etapas anteriores.

Atualização: consulte [cama, privação e HUD](cama_hud.md) para a revisão da interação da cama, o inventário simplificado e os testes adicionais.

A partida começa no quarto, no dia 1, com comida e água zeradas, sanidade 8/8 e somente o protagonista. A fome da mensagem inicial não acrescenta dias aos contadores.

## Como jogar

Feche a mensagem com Enter ou Espaço. Verifique a geladeira na cozinha, assista ao boletim atual na TV do quarto e investigue a porta principal na Entrada. Os objetivos somem conforme são concluídos. Ricardo só chega depois de assistir à transmissão inicial. É necessário assistir a ela e resolver o visitante aguardando antes de dormir.

Pressione **I** durante a exploração para abrir SUPRIMENTOS DA CASA; **I ou ESC** fecha. O inventário pausa a movimentação e mostra somente comida e água armazenadas. A HUD superior apresenta dia, sanidade e contadores de privação. A geladeira abre a mesma interface após sua mensagem inicial de estoque vazio: nunca fornece recursos.

Use **E** perto da cama e confirme para encerrar o dia. Cancelar não consome recursos. Após sobreviver à noite, o resumo apresenta o consumo efetivo, moradores, sanidade e avisos de ração ausente. A derrota mostra causa e dia, sem avançar o calendário. **Enter, R ou o botão Nova partida** reinicia tudo, incluindo os sorteios dos visitantes; ESC encerra. Não existe menu inicial.

## Regras implementadas

- A partir do dia 2, cada morador vivo recebe 0,5 lata e 0,5 garrafa por encerramento de dia, conforme disponibilidade. O dia 1 não consome nem registra privação. Não há consumo durante a exploração. O estoque usa unidades inteiras de meia ração, evitando erros decimais e valores negativos.
- A função configurável `protagonist_first`, em `casa/survival.py`, prioriza o protagonista, depois os identificadores dos outros moradores em ordem fixa. Comida e água são distribuídas independentemente. Encerrar novamente o mesmo dia reutiliza o resultado, sem novo consumo.
- Cada ração recebida zera seu respectivo contador; a ausência incrementa um dia, desconsiderando o dia 1. Fome 3/3 e sede 2/2 são estados críticos ainda vivos: o protagonista morre somente se completar outro dia sem a respectiva ração. Sem recursos desde o início, sede mata ao encerrar o dia 4; fome, com água suficiente, ao encerrar o dia 5. NPCs mantêm registros próprios, sem morte automática por privação.
- Cinco dias inteiros consecutivos sem outro morador vivo causam derrota por solidão. Aceitar companhia zera a sequência no encerramento; rejeitar ou conversar na porta não conta como companhia.
- Desde o dia 1, passar o dia inteiro sozinho reduz a sanidade em um ponto; ter companhia viva durante o dia recupera um ponto, uma vez por dia. `change_sanity` limita os valores entre 0 e 8 e permite alterações futuras. Sanidade zero não mata; não foram implementadas eliminações ou penalidades por diagnóstico.
- Aceitar transfere os suprimentos uma única vez ao estoque compartilhado e torna o visitante morador permanente. Seu estoque individual disponível fica zerado, mantendo apenas os valores históricos do encontro. Rejeitar não transfere nada. Não há expulsão ou devolução de suprimentos.
- Ricardo traz de 2 a 3 unidades de cada recurso. `initial_supplies` no cadastro permite outras distribuições para futuros visitantes; o padrão é de 0 a 3. A estrutura de moradores vivos/falecidos e o consumo aceitam vários visitantes, sem regras de consumo específicas de Ricardo.

## Narrativa e preservação

A apresentação de Ricardo continua identificando-o como médico de 42 anos. O hospital foi isolado enquanto ele estava fora; sua casa fica numa Zona Vermelha, e os abrigos não têm vagas. As quatro perguntas anteriores foram preservadas, com respostas adaptadas, e foram acrescentadas perguntas sobre hospital, casa e busca por abrigo. A resposta de suprimentos apresenta as quantidades reais sorteadas.

Foram atualizados os boletins dos dias **1** (lockdown, evacuação, abastecimento e abrigos), **3** (conflitos e impossibilidade de atender ocorrências) e **6** (confrontos fatais e desespero). As descobertas médicas dos dias **4, 7, 10, 14, 17 e 20** e a interface/histórico foram preservados. Não há interpretação lógica das notícias, diagnóstico ou morte por infecção. `logica_infeccao.py` permanece reservado ao grupo.

Nesta etapa não foram processadas ou sobrescritas imagens, alterados ciclos de animação, escalas, sombras, hitboxes, colisões dos cenários ou rotas entre portas. A movimentação automática de Ricardo continua usando o sistema existente. Interfaces e derrota pausam a simulação.

## Arquivos desta etapa

Criados:

- `casa/survival.py`: estoque, distribuição, contadores, sanidade, relatório e derrota.
- `casa/survival_ui.py`: inventário e tela de derrota.
- `tests/test_sobrevivencia.py`: 14 testes novos, unitários e integrados.
- `tests/support.py`: preparação explícita de partidas para regressões de exploração e calendário.
- `conferir_sobrevivencia.py`, este relatório e capturas `docs/sobrevivencia_*.png`.

Modificados:

- `casa/game.py`: introdução, inventário, geladeira, integração do sono, resumo e reinício.
- `casa/visitors.py`: chegada após notícia, suprimentos, moradores e integração do encerramento diário.
- `casa/days.py`: encerramento idempotente e interrupção do avanço quando houver derrota.
- `casa/news.py`: notificação da primeira visualização de cada boletim.
- `casa/config.py`: ação da geladeira, preservando posição.
- `casa/visitor_ui.py`: espaço para as sete perguntas.
- `dados/visitantes/ricardo.json`, `ricardo_dialogos.json` e `dados/noticiarios.json`: recursos e narrativa.
- Suítes anteriores em `tests/`: uso da preparação de exploração; ajustes das expectativas de introdução, geladeira, diálogos e sobrevivência no calendário.
- `conferir_dias_tv.py`, `conferir_ricardo_individual.py` e `validar_animacoes_jogo.py`: preparação compatível com a introdução.
- `README.md` e `docs/dias_sono_tv.md`: estado atual e instruções.

Os demais arquivos já modificados no workspace pertencem às etapas anteriores; não houve reversão geral do projeto.

## Validação

Executados com sucesso:

```powershell
python main.py --smoke-test
python teste_movimentacao.py --smoke-test
python conferir_sobrevivencia.py
```

A suíte principal passou **96 testes**. Os 14 novos verificam início zerado, geladeira, chegada após TV, transferência única, rejeição, permanência, distribuição com 1, 2, 3, 5 e 12 moradores, racionamento parcial, política configurável, limites e reinício dos contadores, solidão, sanidade, pausa do inventário, encerramento único, derrota sem avanço, nova partida e notícias. As regressões cobrem animações e arquivos protegidos, transições, sombras, investigação, movimento de Ricardo, colisões e editor.

As capturas usam SDL dummy e foram inspecionadas visualmente; não equivalem a uma sessão manual completa de jogo:

- [Introdução](sobrevivencia_intro.png)
- [Inventário inicial](sobrevivencia_inventario_zero.png)
- [Lockdown](sobrevivencia_lockdown.png)
- [Conversa com Ricardo](sobrevivencia_ricardo_dialogo.png)
- [Inventário após acolhimento](sobrevivencia_inventario_ricardo.png)
- [Resumo da noite](sobrevivencia_resumo.png)
- [Derrota](sobrevivencia_derrota.png)

As preparações de testes de calendário e o script de capturas dos dias avançados usam estoque artificial **somente nessas ferramentas**, para isolar as verificações. A partida normal não recebe esses recursos e não possui atalhos de reabastecimento.

## Pendências

A sobrevivência por 20 dias exige futuros visitantes e balanceamento: os recursos de Ricardo são temporários e não bastam para completar a campanha. Não foi criada comida para contornar essa limitação. Permanecem pendentes novos visitantes, persistência da partida em disco, encerramento definitivo da campanha, mortes de NPCs, consequências de sanidade zero e a lógica acadêmica de infecção. O limite do calendário continua no dia 20, sem declarar vitória automaticamente.
