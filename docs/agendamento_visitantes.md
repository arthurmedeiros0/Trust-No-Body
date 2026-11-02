# Calendário fixo e balanceamento

O modo normal cria o plano uma única vez, em `VisitorManager.__init__`.
`dados/agendamento_visitantes.json` define Ricardo no dia 1, Laura no dia 2 e
as vagas restantes nos dias 4, 6, 9, 13 e 17. Somente os identificadores dos
outros visitantes disponíveis são embaralhados, a partir de uma lista ordenada.
A mesma semente e os mesmos cadastros produzem o mesmo plano.

Cadastros incompletos continuam indisponíveis. Uma vaga fixa de personagem
indisponível fica vazia; candidatos além das vagas ficam em `unscheduled`.
A configuração permite repetir dias para testar a fila, mas o calendário padrão
possui apenas uma chegada por dia. As regras anteriores de intervalo, prioridade
e quantidade mínima foram substituídas por `fixed_visitors` e `arrival_days`.

Ricardo aguarda o primeiro noticiário. Os demais são ativados pelo evento
`day_start`, inclusive durante a animação de sono. Decisões não alteram o plano.
A fila preserva visitantes pendentes e recupera vagas vencidas se uma ativação
for atrasada. Os identificadores apresentados não voltam à fila. A interface
continua guardada durante diálogos e trocas de cômodo. Dormir continua bloqueado
até decidir sobre o visitante na porta.

`VisitorSession.start_test` marca a sessão como teste e apresenta imediatamente
o personagem escolhido. Eventos de dia e o primeiro noticiário não introduzem
outros visitantes nessa sessão. Reiniciar pelo menu cria uma nova sessão real,
como antes; não há implementação duplicada de personagens.

## Recursos

O protagonista permanece sem estoque inicial. O consumo continua em 0,5 de cada
recurso por pessoa por dia, respeitando a tolerância existente do primeiro dia.
Fome, sede, sanidade, investigação e infecção não foram modificadas.

Intervalos independentes de comida e água, sorteados uma vez por visitante:

| Visitante | Comida | Água |
|---|---|---|
| Ricardo | 2–3 (inalterado) | 2–3 (inalterado) |
| Laura | 3–5 | 3–5 |
| Antônio, Gabriel, Helena, Daniel e Marina | 6–11 | 6–11 |

Acolher todos exige 43,5 unidades de cada recurso entre os dias 2 e 19, ou 47,5
incluindo a ração do dia 20. Os intervalos antigos forneciam em média apenas
cerca de 9,5 unidades por recurso: aumentar apenas a frequência das chegadas
não poderia sustentar oito moradores. Os novos intervalos fornecem em média
49 unidades por recurso, com variação entre 35 e 63. O ajuste maior nos últimos
visitantes acompanha o crescimento da casa; não há reposição automática nem
estoque criado em função de uma derrota iminente.

A prioridade de distribuição existente favorece o protagonista. Portanto, chegar
ao dia 20 não significa que todos os moradores receberam todas as rações.
Os resultados abaixo medem o protagonista, sem simular consequências de infecção
que ainda não estão implementadas no projeto.

## Validação

500 sementes (0 a 499), com os cadastros ordenados como na sessão normal:

| Decisões | Chega ao dia 20 | Sobrevive também à ração do dia 20 |
|---|---:|---:|
| Acolher todos | 489/500 | 325/500 |
| Acolher Ricardo; depois acolher quando o menor estoque for inferior a 5 | 453/500 | 310/500 |
| Recusar todos | 0/500 | 0/500 |

Recusar todos causa derrota por sede no dia 3. Os testes também verificam
ordens distintas, unicidade, calendário imutável após decisões, recuperação de
ativação atrasada, isolamento do modo teste e todos os avanços reais pelo sono
até o dia 20, com passagem por cômodos e bloqueio de sono enquanto houver visita.
O teste de transições adiciona recursos apenas à sua fixture; as simulações de
balanceamento não adicionam recursos artificiais.

O jogo continua suspendendo avanços no dia 20. A simulação fecha a ração desse
dia separadamente para não confundir alcançar o dia 20 com sobreviver a ele.

Execute `python main.py --smoke-test`. Registro: `calendario_test_results.txt`.
Há cinco falhas preexistentes já registradas na entrega anterior: duas relativas
ao texto da geladeira, uma de prioridade de interação perto da geladeira, uma
de escala esperada no editor e uma de hash de `colisoes/cozinha.json`. Não foram
alteradas imagens, cenários, colisões, histórias ou falas nesta correção.

Resultado final: 145 testes executados, 140 aprovados e as cinco falhas
preexistentes acima. Os cinco testes novos de calendário e balanceamento passaram.

Arquivos alterados: `casa/visitor_schedule.py`, `casa/visitors.py`,
`dados/agendamento_visitantes.json`, os seis cadastros com novos intervalos
(Laura e os cinco visitantes finais), `tests/test_agendamento_visitantes.py`,
`tests/test_laura.py` e este documento. Criados:
`tests/test_calendario_balanceamento.py` e o registro da execução.
