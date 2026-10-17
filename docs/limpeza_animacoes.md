# Limpeza dos sprites e revisao da caminhada

Foram revisados os 32 sprites ativos (quatro parados e doze quadros por personagem).
Eles continuam em RGBA 64x96, com apoio dos pes em y=94 e altura visual de 88 px.

## Limpeza e idle

`casa/sprite_cleanup.py` conserva o componente principal da mascara e descarta
fragmentos desconectados. Junto ao chao, elimina apenas espuroes escuros e neutros
de um pixel de espessura que nao pertencem ao nucleo da silhueta. Esse criterio
combina geometria e cor: nao apaga o preto interno nem aplica erosao global ao
cabelo, roupa, maos, jaleco ou detalhes claros dos sapatos. Nao ha suavizacao.
O resultado e recentralizado e alinhado novamente, com NEAREST quando necessario.

O idle lateral do protagonista foi reconstruido a partir da primeira pose da
linha ESQUERDA, a pose com os pes mais proximos. O torso e a mochila foram
preservados; abaixo da barra da roupa, os pixels da perna de apoio foram
reorganizados em duas pernas verticais com sapatos apoiados. A pose resultante
foi orientada para a direita, e a esquerda e seu espelhamento exato. Assim, os
parados laterais deixam de repetir um quadro de passada ou um pe levantado.
Nenhum retrato foi recriado.

## Ciclos usados no jogo

O protagonista e o Ricardo compartilham a montagem dos ciclos em
`casa/animation.py`, configurada em `casa/config.py`:

| Direcao | Ordem | Protagonista | Ricardo |
| --- | --- | --- | --- |
| Direita | idle → quadro 1 → idle → quadro 3 | 0,14 s por pose | 0,18 s por pose |
| Esquerda | idle → quadro 2 → idle → quadro 3 | 0,14 s por pose | 0,18 s por pose |
| Frente e costas | quadro 1 → quadro 2 → quadro 3 | 0,14 s por pose | 0,18 s por pose |

A linha esquerda inicia com uma pose quase parada; por isso os passos 2 e 3
foram selecionados para evitar um idle duplicado. Os tres arquivos originais de
caminhada continuam disponiveis. Frente e costas mantiveram os tres passos:
inserir poses paradas ali acrescentava repeticao a linhas que ja sao discretas.

Ao parar, ambos mostram imediatamente o idle correspondente. O tempo e acumulado
em segundos, preservando independencia do FPS. A velocidade de deslocamento e
os tempos configurados por pose nao foram alterados; o ciclo lateral agora tem
quatro poses. O NPC apenas consulta `assets.cycles` em vez de `assets.walk` para
desenhar, sem mudancas em sua escolha de direcao, pausas, trajetoria ou colisoes.

## Conferencias

- [Protagonista: antes, idle reconstruido e sequencias ampliadas](animacoes_protagonista.png)
- [Ricardo: antes, parados e sequencias ampliadas](animacoes_ricardo.png)
- [GIF do protagonista](animacoes_protagonista.gif)
- [GIF do Ricardo](animacoes_ricardo.gif)

Os PNGs usam ampliacao 3x NEAREST, fundo xadrez e linha vermelha nos pes. Os GIFs
usam a mesma ordem de quadros e duracao por pose do jogo. Regerar com
`python conferir_animacoes.py`. Para reextrair e limpar os sprites, executar
`python preparar_sheets.py` (faz backup antes de escrever).

## Arquivos alterados e preservacao

- Criados: `casa/sprite_cleanup.py`, `conferir_animacoes.py`,
  `tests/test_limpeza_animacao.py`, este relatorio e quatro conferencias PNG/GIF.
- Ajustados: `preparar_sheets.py`, `casa/animation.py`, `casa/config.py`,
  `casa/visitor_assets.py`, `casa/resident.py`, os testes de ciclo existentes,
  `dados/sheets/{protagonista,ricardo}.json`, os 32 sprites e suas conferencias.
- Backup anterior a limpeza: `backups/sheets_20261017_152232_838869/`.
  Alem dos sprites, contem o preparador e os arquivos anteriores de animacao,
  configuracao e NPC. O caminho tambem esta em `dados/sheets/backup_antes_limpeza.txt`.
- Fontes das sheets, porta do Ricardo, investigacao e exames processados foram
  preservados. Os hashes de protecao da integracao anterior continuam validados.
  Nao foram alterados mapas, colisoes, sombras, dialogos, randomizacao, dia/noite
  ou logica de infeccao.

## Validacao e limites

`python main.py --smoke-test`: **59 testes aprovados**.
`python teste_movimentacao.py --smoke-test`: aprovado.

Os testes verificam os 32 sprites como um unico componente, transparencia,
dimensoes e apoio; preservacao de preto interno e detalhes claros; remocao de
ilhas e espuroes sinteticos; espelhamento e identidade propria do novo idle;
ordem dos ciclos, repouso e reinicio; movimento e fase em 30/60/120 FPS;
sombras, colisoes, portas, camera, editor e demais sistemas existentes.

As duas conferencias ampliadas foram inspecionadas visualmente. Os residuos
e fragmentos evidentes junto aos pes foram removidos. Nao identifiquei um quadro
que obrigue a refazer manualmente o recorte. As diferencas de desenho entre poses
da sheet continuam presentes, especialmente o rosto e a mochila; melhorar essa
consistencia artistica exigiria redesenho. A naturalidade em uma sessao manual
interativa nao foi validada: o jogo foi testado com SDL dummy, e os GIFs ficam
disponiveis para revisar o ritmo em movimento.
