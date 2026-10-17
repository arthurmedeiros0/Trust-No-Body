# Privação concluída e previsão da HUD

O estado `Survival.people['protagonista']` guarda somente dias completos sem ração. `Survival.predicted_needs(day, living_ids)` calcula separadamente a previsão do encerramento atual, sem consumir recursos nem alterar contadores, sanidade ou solidão.

No dia 1, a previsão é zero. Nos demais dias, se a distribuição atual garantir a ração do protagonista, o indicador correspondente prevê zero; caso contrário, mostra dias completos mais o dia atual, limitado a 3 para fome e 2 para sede. A previsão respeita a função configurável de distribuição, inclusive quando o protagonista não é o primeiro. Receber recursos atualiza a HUD imediatamente sem apagar o histórico de dias completos.

| Momento sem recursos desde o início | Fome na HUD | Sede na HUD |
|---|---|---|
| Dia 1 | 0/3 | 0/2 |
| Início do dia 2 | 1/3 | 1/2 |
| Início do dia 3 | 2/3 | 2/2 |
| Início do dia 4, com água suficiente | 3/3 | 0/2 |

Chegar visualmente ao limite durante a exploração não mata. Confirmar o sono distribui as rações disponíveis, atualiza os dias completos uma vez e verifica derrota: sede ao completar dois dias sem água, fome ao completar três sem comida. Sem água desde o início, a derrota ocorre ao encerrar o dia 3, sem iniciar o dia 4. Com água suficiente e sem comida, ocorre ao encerrar o dia 4, sem iniciar o dia 5. Obter a ração nesses dias críticos permite consumi-la, zerar o respectivo histórico e sobreviver.

O resultado de um dia já encerrado é reutilizado durante a transição: a HUD não adiciona novamente esse mesmo dia. A sanidade, a solidão e a tolerância do dia 1 mantêm suas regras. F6 continua apenas visual. Sono, inventário, visitantes, sprites, animações, colisões e lógica de infecção não foram reestruturados.

Arquivos ajustados: `casa/survival.py` (previsão e verificação no encerramento), `casa/game.py` (fonte dos indicadores da HUD), `tests/test_sobrevivencia.py`, `tests/test_cama_hud.py`, `conferir_sobrevivencia.py` (dia da derrota), README e relatórios. O layout da HUD permanece igual.

Validação: **108 testes passaram** com `python main.py --smoke-test`. Incluem derrota sem água no dia 3 e sem comida no dia 4, resgate por suprimentos de visitante nos dias críticos, previsão sem efeitos colaterais, política de distribuição alternativa, preservação do histórico ao receber recursos, consumo único, bloqueio de avanço após derrota e invariância por F6. Os scripts `conferir_sobrevivencia.py` e `conferir_cama_hud.py` também executaram com sucesso e regeneraram as capturas.
