# Chegada e agendamento de visitantes

O cadastro completo atual inclui Ricardo e **Laura**, integrada com seus próprios assets e dados. Ricardo chega no dia 1 após a TV, e Laura no dia 2 ou 3, conforme a agenda da partida. Nenhum personagem provisório foi adicionado. A introdução permanece: quarto, geladeira vazia, TV do lockdown e Ricardo na porta no dia 1. Ambos nunca retornam após aceitação ou rejeição. Veja o [relatório da Laura](laura.md).

## Organização

`VisitorSession` continua sendo o estado da partida e o ponto de integração com notícias, sobrevivência e decisões. O novo `VisitorManager`, em `casa/visitor_schedule.py`, mantém a agenda e a fila, referenciando os mesmos objetos `Visitor`. A definição JSON contém os dados permanentes; cada `Visitor` guarda os sintomas, recursos, estado, chegada e decisão daquela partida.

Informações disponíveis em `session.manager`:

- `plan`: identificador → dia planejado; Ricardo sempre recebe dia 1.
- `available`: visitantes planejados que ainda não apareceram.
- `eligible`: cadastros completos aprovados na validação.
- `unscheduled`: completos que ficaram sem vaga na capacidade configurada.
- `seen`: identificadores que já foram apresentados, sem duplicatas.
- `current`: único visitante atualmente aguardando decisão, ou `None`.
- `queue`: próximos identificadores, apresentados um por vez.
- `accepted`, `rejected`, `residents`: consultas aos estados atuais; moradores incluem somente aceitos vivos.
- `opportunities`: dias prioritários e respectivos identificadores planejados. Com somente Ricardo, os dias 2 e 3 ficam com listas vazias.
- `opportunity_results`: ao consultar um dia prioritário, registra `planejado` ou `sem_candidatos`.

`session.unavailable` registra motivos pelos quais cadastros incompletos não podem ser agendados. Não existe diagnóstico de infecção: os seis sintomas continuam sendo dados booleanos sorteados, sem classificação médica ou proposicional.

## Planejamento por partida

A agenda é criada uma única vez, após o sorteio dos sintomas e suprimentos. Entrar em cômodos, abrir o olho mágico, usar F6 ou atualizar frames não altera o plano e não sorteia dados novamente.

`dados/agendamento_visitantes.json` centraliza:

```json
{
  "first_day": 2,
  "last_day": 20,
  "max_per_day": 1,
  "priority_days": [2, 3],
  "minimum_encounters": 1
}
```

O intervalo aplica-se aos visitantes posteriores a Ricardo, sempre entre 2 e 20. Os candidatos completos são embaralhados. O sistema reserva inicialmente pelo menos uma oportunidade prioritária quando houver candidato e dia prioritário dentro do intervalo; o parâmetro `minimum_encounters` pode ampliar essa reserva até a quantidade de dias prioritários e candidatos disponíveis. As vagas restantes do intervalo são embaralhadas e preenchidas pelos demais candidatos, respeitando `max_per_day`. Cadastros excedentes ficam explicitamente em `unscheduled`.

Com os padrões atuais, um novo visitante completo pode cair no dia 2 ou 3, e os demais se distribuem pelos dias restantes. A oportunidade inicial é reservada independentemente de aceitar ou rejeitar Ricardo, atendendo também ao caso em que ele é rejeitado. Não há garantia de estoque, aceitação ou sobrevivência. Nenhum candidato é inventado para preencher vagas vazias.

Sem Ricardo completo, os demais não são apresentados: o primeiro encontro obrigatório precisa ser corrigido no cadastro antes de permitir a sequência. Configurações com intervalo fora de 2–20 ou capacidade menor que 1 são rejeitadas.

## Chegada, fila e porta

Assistir ao boletim inicial ativa a chegada obrigatória. O evento `day_start` consulta a agenda uma vez para o novo dia. Os visitantes daquele dia entram na fila; somente o primeiro recebe `arrived=True` e é apresentado. Enquanto alguém aguarda decisão, a fila não o substitui, e dormir continua bloqueado.

Ao resolver a decisão, o próximo visitante da fila é disponibilizado. `House` recebe o evento de chegada e cria uma `VisitorUI` com os assets, diálogos, sintomas e recursos daquele identificador. As imagens nunca se sobrepõem. Mudar de cômodo não limpa a fila ou o encontro atual. Um visitante futuro só entra na casa após acolhimento pelo fluxo já existente, com posição livre e colisões existentes.

O padrão limita o planejamento a um encontro por dia; aumentar `max_per_day` habilita a fila de vários encontros. Os identificadores já apresentados não podem voltar à fila. Decisões são irreversíveis e a transferência de suprimentos continua ocorrendo uma única vez. Nenhum sorteio ocorre durante a chegada, a decisão ou o sono.

## Adicionar um visitante completo

1. Crie `dados/visitantes/<id>.json`, usando o formato de Ricardo como referência estrutural e um identificador único. Informe nome, idade, profissão, história, `asset_root`, retrato, altura/âncora do retrato, quatro sprites parados, sala, posição e direção inicial de morador. Use arquivos próprios do novo personagem.
2. Cadastre as seis características em `investigation`, com `label`, `normal` e `alterado`: `manchas_maos`, `dentes_deteriorados`, `olhos_alterados`, `veias_escurecidas`, `palidez_anormal` e `tremores_involuntarios`.
3. Forneça as animações no formato já suportado: preferencialmente `sheet_sprites: true` e `internal_sprite_manifest`, com `frames` contendo listas de caminhos por direção, relativos a `asset_root`. Também permanecem suportados os caminhos e manifestos anteriores do projeto.
4. Crie `dados/visitantes/<id>_dialogos.json`, com `intro` e `questions` (`question` e `answer`). As respostas podem usar `{food}` e `{water}`.
5. Configure `initial_supplies`, por exemplo `{"food": [0, 3], "water": [0, 3]}`. Sem configuração específica, continua o padrão de 0 a 3. Ricardo permanece com 2 a 3 de cada recurso.
6. Reinicie a partida. O cadastro e os arquivos passam por validação de leitura antes de entrar na agenda. Caminhos ausentes, imagens ilegíveis, características, animações ou diálogos incompletos deixam o personagem fora das chegadas, com motivo em `session.unavailable`.

Não é necessário alterar o algoritmo de planejamento ou o código principal para acrescentar Laura, Antônio, Gabriel, Helena, Daniel ou Marina quando seus materiais estiverem prontos. Não copie a aparência de Ricardo para representar esses personagens na partida normal. As simulações de múltiplos visitantes estão exclusivamente nos testes.

## Arquivos e validação

Criados: `casa/visitor_schedule.py`, `casa/visitor_registry.py`, `dados/agendamento_visitantes.json`, `tests/test_agendamento_visitantes.py` e este relatório.

Modificados: `casa/visitors.py` (agenda, validação e notificações), `casa/game.py` (apresentação dinâmica e proteção do visitante atual), `tests/test_sobrevivencia.py` (resolver Ricardo antes de inserir moradores simulados) e README. Os cadastros e assets de Ricardo permanecem iguais.

**115 testes passaram** com `python main.py --smoke-test`, incluindo sete testes novos de agendamento. Eles cobrem introdução, somente Ricardo, oportunidades sem candidatos, aleatoriedade entre partidas, estabilidade na mesma partida, capacidade e intervalo, fila múltipla, bloqueio de substituição, decisões sem retorno, duplicatas, preservação de sintomas e suprimentos, recursos sem duplicação, cadastro incompleto, chegada pelo sono e permanência dos moradores/cenários ao mudar de cômodo. As regressões existentes também verificam investigação, animações, colisões, sobrevivência, HUD e notícias. A validação usa SDL dummy; múltiplos personagens são simulados somente nos testes.

## Pendências

Os personagens posteriores a Laura ainda precisam de seus próprios cadastros narrativos e assets completos. A partida normal tem Ricardo e Laura e não foi artificialmente equilibrada para durar 20 dias. Regras de fome/sede, tolerância inicial, sanidade, solidão, HUD e geladeira permanecem iguais. Não foi criada persistência em disco da agenda; assim como os demais dados da partida, ela existe durante a sessão. A lógica de infecção continua reservada aos alunos.
