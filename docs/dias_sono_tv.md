# Dias, sono e noticiario

Atualiza??o: o sono agora tamb?m consome recursos, verifica derrotas e apresenta
o resumo da noite. A introdu??o come?a no quarto e libera Ricardo ap?s a TV.
Consulte o [estado atual da sobreviv?ncia](sobrevivencia.md); o restante deste
relat?rio registra a implementa??o original do calend?rio.

## Como jogar

Uma nova partida inicia em **Dia 1 / 20**, durante o dia. O contador aparece no
cabecalho. Nao ha relogio que avance os dias automaticamente. F6 continua apenas
alternando os cenarios diurno/noturno: nao publica boletins nem dispara eventos.

No quarto, aproxime-se da cama e pressione **E**. Escolha **Dormir** clicando no
botao ou pressionando **S/Enter**; **Cancelar**, **N** ou **ESC** fecha sem avancar.
Enquanto houver um visitante aguardando na porta, uma mensagem pede que a
situacao seja resolvida antes de dormir. Dialogos, TV, olho magico, editor e
transicoes impedem abrir outra operacao de sono.

Confirmar bloqueia o movimento, escurece por 0,45 s, avanca exatamente um dia,
mostra a cartela escura por 1,6 s e clareia por 0,45 s. O protagonista acorda
no quarto, olhando de frente, perto da cama e em uma posicao validada pelas
colisoes. O periodo volta a diurno. A confirmacao e o controle de repeticao de E
impedem avancar varios dias com a tecla mantida pressionada. Nao ha dia 21:
no dia 20, a cama informa o limite e a partida continua acessivel, inclusive a TV.

Na televisao existente do quarto, pressione **E**. Escolha **Noticiario atual**,
**Noticias anteriores** ou **Voltar**. Use mouse ou setas e Enter/Espaco. ESC
retorna uma pagina e, no menu principal, fecha a TV. O historico possui paginacao
para comportar as 20 transmissoes. So abrir o menu nao marca uma noticia como
assistida: e preciso abrir seu conteudo.

## Calendario e boletins

Os marcos narrativos ocorrem nos dias 1, 4, 7, 10, 14, 17 e 20, conforme o
cronograma solicitado. Os outros 13 dias possuem boletins intermediarios sobre
a crise recente, sem novas regras de infeccao nem antecipacao dos marcos.
O dia 7 apresenta as tres condicoes do primeiro padrao e ressalva que sua
ausencia nao prova saude; o dia 14 apresenta o segundo conjunto independente;
o dia 17 anuncia o protocolo completo; o dia 20 anuncia a cura, sem tela de vitoria.

Cada boletim possui id, dia, manchete, paragrafos e estados separados
`available`/`read`. Ao acordar, os boletins ate aquele dia ficam disponiveis;
a TV abre o do dia atual. O historico mostra somente os efetivamente assistidos.
Uma transmissao perdida nao surge no historico apenas porque sua data passou.
Nenhuma noticia futura pode ser aberta pela interface.

O estado fica na instancia da partida, em `VisitorSession`, incluindo calendario,
noticias, conhecimento publicado e visitantes. Reiniciar o jogo inicia outra
partida: salvamento/carregamento em disco nao foi acrescentado nesta etapa.

## Organizacao e eventos futuros

Criados:

- `casa/days.py`: `DayCycle`, limite 20 e eventos `day_end`/`day_start`.
- `casa/sleep.py`: `SleepTransition`, reutilizando a base de fade existente.
- `casa/news.py`: boletins e estados de disponibilidade/leitura, sem desenho.
- `casa/television.py`: interface modal do noticiario e historico.
- `dados/noticiarios.json`: dados narrativos dos 20 dias.
- `tests/test_dias_tv.py`: testes integrados da nova mecanica.
- `conferir_dias_tv.py`: capturas reproduziveis da interface real.
- Este relatorio e capturas em `docs/sono_*.png` e `docs/tv_*.png`.

Modificados: `casa/game.py` (integracao, input, bloqueios e cabecalho),
`casa/visitors.py` (calendario/noticias da mesma partida), `casa/config.py`
(apenas a acao da TV existente), README e testes que ainda esperavam os
placeholders de TV/sono. `main.py` nao foi alterado. Nenhum arquivo
`ESTADO_DO_PROJETO.md` foi encontrado para atualizar.

Os eventos recebem `DayEvent(day, previous_day, next_day)`. Exemplo de extensao:

```python
game.days.subscribe('day_end', ao_terminar_o_dia)
game.days.subscribe('day_start', ao_comecar_o_dia)
```

O primeiro ocorre antes do incremento; o segundo, depois. A disponibilizacao
de noticias e assinante do inicio do dia. Nao ha consumo de comida/agua,
penalidades, sanidade, chegadas automaticas ou consequencias de moradores.
Nenhum contador ficticio foi criado. As noticias assistidas registram apenas
id, dia e manchete em `JournalKnowledge.published`; nao ha avaliacao de sintomas,
expressoes proposicionais, inferencia, diagnostico ou classificacao automatica.
`logica_infeccao.py` permaneceu intacto e reservado aos alunos.

## Preservacao do Ricardo

Dormir nao recria `VisitorSession`, visitantes ou moradores. Sao mantidas as
mesmas instancias, sintomas, comida, agua, decisao, exames vistos, diagnostico
pendente, animacao e posicao do morador. Aceitos e rejeitados nao reaparecem.
Durante a tela modal, a simulacao da exploracao fica pausada; ao retornar, o
Ricardo segue o comportamento automatico existente quando a sala estiver ativa.
As decisoes futuras usam o dia corrente do mesmo calendario.

Nao foram alterados sprites, escalas, sombra, hitboxes, arquivos de colisoes,
cenarios, coordenadas dos moveis, portas, olho magico ou imagens de investigacao.

## Validacao

**82 testes aprovados**: `python main.py --smoke-test`.
Teste isolado aprovado: `python teste_movimentacao.py --smoke-test`.

A suite verifica inicio diurno no dia 1; ausencia de avanco por tempo/F6;
cancelamento e confirmacao por teclado/mouse; bloqueio por visitante pendente;
um unico avanco ao manter E; fade, cartela e retorno valido ao quarto;
eventos disparados uma vez; limite 20 mantendo a TV acessivel; acesso por
proximidade; leitura separada de disponibilidade; historico paginado so dos
assistidos; bloqueio de futuras; marcos dos dias 7/14/17/20; modalidades;
preservacao de Ricardo aceito e rejeitado, sem novo sorteio; transicao a
30/60/120 FPS e suite existente de movimento, colisoes, sprites, sombra e portas.

Capturas inspecionadas visualmente, produzidas pelo render real do Pygame:

- [Confirmacao da cama](sono_confirmacao.png)
- [Cartela do dia 2](sono_dia_2.png)
- [Retorno ao quarto](sono_acordou.png)
- [Menu da TV](tv_menu.png)
- [Boletim do dia 7](tv_dia_7.png)
- [Historico assistido](tv_historico.png)

A validacao usou SDL dummy, sem sessao manual interativa. Para regerar as
capturas, execute `python conferir_dias_tv.py`.

Permanecem para etapas futuras: logica academica, diagnosticos, novos
visitantes/eventos e encerramento definitivo. Sobrevivencia, recursos,
sanidade e derrotas foram implementados na etapa seguinte (ver relatorio acima). O limite de 20 dias nao declara vitoria nem derrota.
