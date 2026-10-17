# Tolerância inicial e sanidade diária

**Atualização:** a [separação entre previsão e dias completos](previsao_privacao.md) substitui as datas de derrota descritas nesta etapa: a HUD inclui o dia atual, e a derrota é verificada ao dormir no dia 3 sem água ou no dia 4 sem comida. Tolerância, sanidade e solidão abaixo permanecem válidas.

O encerramento do **dia 1** não distribui rações, não desconta recursos de nenhum morador, não incrementa fome/sede e não verifica derrota por privação. O resumo registra consumo zero. A partir do dia 2, cada morador vivo volta a consumir 0,5 unidade de cada recurso, com a mesma prioridade e estoque compartilhado anteriores.

Sem recursos desde o início:

| Encerramento | Fome | Sede | Sanidade se sozinho |
|---|---|---|---|
| Dia 1 | 0/3 | 0/2 | 7/8 |
| Dia 2 | 1/3 | 1/2 | 6/8 |
| Dia 3 | 2/3 | 2/2: crítico, vivo | 5/8 |
| Dia 4 | 3/3: crítico, vivo | Próximo dia sem água: derrota | 4/8 |

Os limites são inclusivos: atingir sede 2/2 ou fome 3/3 não mata. A derrota ocorre somente se o próximo dia sem a respectiva ração ultrapassaria o limite. Sem água desde o início, ocorre ao encerrar o **dia 4**. Com água suficiente, mas sem comida, ocorre ao encerrar o **dia 5**. Receber e consumir a ração correspondente no estado crítico zera seu contador e evita essa derrota. Não há penalidade ao acordar. O contador do protagonista permanece limitado à faixa da HUD, inclusive no encerramento fatal.

A sanidade é calculada desde o primeiro encerramento: **−1** após um dia inteiro sozinho ou **+1** se houve outro morador vivo como companhia durante o dia. A alteração ocorre uma vez, independentemente da quantidade de moradores. O valor fica entre 0 e 8; chegar a zero não causa derrota. Não há perda de sanidade adicional por fome ou sede.

Solidão continua independente: cinco dias consecutivos inteiros sozinho causam derrota, contando desde o dia 1. Acolher um visitante vivo conta como companhia; rejeitar não conta.

A mudança de produção está concentrada em `casa/survival.py`. Sono, estoque, visitantes e HUD usam o mesmo estado anterior, sem alterações em aparência, sprites, colisões ou investigação. A HUD continua lendo os contadores reais: ao acordar no dia 2, fome e sede ainda mostram zero. F6 continua sendo somente visual.

Arquivos ajustados: `casa/survival.py`, `tests/test_sobrevivencia.py`, `tests/test_cama_hud.py`, `conferir_sobrevivencia.py`, README e relatórios de sobrevivência/cama. Os testes anteriores foram adaptados aos novos dias de derrota; foram acrescentados casos para tolerância com vários moradores e sanidade desde o primeiro dia. As capturas `sobrevivencia_*.png`, `cama_interacao_f3.png`, `hud_dia2.png` e `suprimentos_simplificado.png` foram regeneradas pelos scripts existentes.

Validação: `python main.py --smoke-test` passou **106 testes**, cobrindo consumo, limites inclusivos, recuperação a partir dos estados críticos, companhia, solidão, HUD, sono, repetição da confirmação e regressões do restante do jogo. `python conferir_sobrevivencia.py` também executou com sucesso e regenerou as capturas. A revisão dos limites alterou `casa/survival.py`, os testes de sobrevivência/cama e a sequência de derrota em `conferir_sobrevivencia.py`, além desta documentação. Recursos extras em testes permanecem exclusivos das ferramentas de validação. A lógica de infecção continua reservada ao grupo.
