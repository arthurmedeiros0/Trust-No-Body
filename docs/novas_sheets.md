# Novas sheets do protagonista e do Ricardo

Ricardo agora usa [os novos sprites individuais e ciclos com idle](ricardo_individual.md).
As secoes anteriores sobre a sheet do Ricardo sao historicas.

**Estado atual:** o protagonista voltou aos [sprites e ciclos classicos](protagonista_classico.md).
As novas sheets, retratos, expressoes e sprites desta integracao foram preservados
para uso futuro. Ricardo permanece na versao atual.

**Revisao mais recente:** [restauracao da arte e idle do Ricardo](restauracao_sprites_idle.md).

Estado atual: [idle lateral oficial e revisao do Ricardo](ajuste_lateral_ricardo.md).
Essa revisao substitui o idle reconstruido pela nova referencia fornecida.

**Atualizacao:** os recortes e ciclos foram refinados posteriormente. Consulte
[limpeza e animacoes](limpeza_animacoes.md) para o estado atual, idle lateral
reconstruido, novas conferencias e validacao de 59 testes. As limitacoes e ciclos
descritos abaixo registram a integracao inicial.

O jogo usa agora o novo protagonista e os novos sprites internos do Ricardo.
Foram extraidos 46 assets: 16 sprites e cinco retratos do protagonista; 16 sprites,
cinco retratos e quatro detalhes do Ricardo. As imagens de dialogo ficam apenas
organizadas em disco, sem novas telas ou associacao com sintomas.

## Arquivos e estrutura

```text
preparar_sheets.py                         extracao reproduzivel e backup
dados/sheets/{protagonista,ricardo}.json    origem, SHA-256 e cada recorte/output
personagens/protagonista/
  referencias/novo_design.png              sheet original intacta
  originais/                              13 imagens antigas preservadas
  processados/
    parado/{frente,costas,esquerda,direita}.png
    andando/{direcao}/{1,2,3}.png
    retratos/{principal,normal,surpreso,preocupado,determinado}.png
    conferencia_sheet.png
personagens/visitantes/ricardo/
  referencias/novo_design.png              sheet original intacta
  sprites/{frente,costas,esquerda,direita}.png
  sprites/ricardo_*.png                    originais antigos preservados
  sprites_movimento/                      nove originais antigos preservados
  andando/{direcao}/{1,2,3}.png
  dialogo/principal.png
  dialogo/expressoes/{normal,surpreso,preocupado,determinado}.png
  dialogo/detalhes/{olhos,costas,mao,sapato}.png
  conferencia_sheet.png
  retratos/porta.png                       PRESERVADO
  investigacao/                           PRESERVADO
  investigacao_processada/                PRESERVADO
docs/sheets_integradas_sala.png            captura real do render Pygame
tests/test_sheets.py                       testes especificos da integracao
```

Substituidos: os 16 PNGs de movimento do protagonista e os 12 quadros de caminhada
do Ricardo. Os quatro novos parados do Ricardo tem nomes novos; os antigos continuam
intactos. A comparacao de caminhada do Ricardo e atualizada pelo carregador.

Alteracoes em Python/JSON: `casa/visitor_assets.py`, `casa/visitor_walk_assets.py`,
`dados/visitantes/ricardo.json` e `preparar_sprites.py`. O campo `sheet_sprites`
seleciona os PNGs transparentes diretamente, evitando o processamento de fundo
branco dos antigos sprites e a regeneracao da caminhada antiga. Porta e exames
continuam no carregamento anterior. Os testes anteriores de espelhamento foram
adaptados para poses laterais independentes; hashes antigos do protagonista sao
verificados no backup, e os novos no manifesto da sheet.

## Backup e reproducao

O backup original, criado antes da primeira substituicao, esta em
`backups/sheets_20261017_150406_128619/`. Contem sprites anteriores, configuracao
anterior do Ricardo, preparador anterior e `preservados.json`, com hashes das
imagens da porta, investigacao, exames processados e demais caches do Ricardo.
Os testes conferem esses hashes, incluindo os arquivos efetivamente carregados.
O manifesto anterior do protagonista permanece como registro dos 13 originais;
o manifesto ativo das novas imagens esta em `dados/sheets/protagonista.json`.

Execute `python preparar_sheets.py` para extrair novamente. Cada execucao faz um
novo backup antes de escrever. `python preparar_sprites.py` encaminha para esse
preparador quando encontra a nova sheet, evitando restaurar o design antigo.

## Tratamento e limites visuais

Os recortes excluem titulos e molduras. O fundo e removido por conectividade com
as bordas e criterio de cor, nunca apagando todos os pixels pretos. Os interiores
escuros de retratos sao recuperados entre as bordas visiveis; ruido desconectado
e filtrado nos sprites. A reducao usa NEAREST, escala proporcional, canvas RGBA
64x96, altura visual de 88 pixels e apoio no y=94, como antes.

As linhas direcionais tem quatro poses: foram selecionadas as tres primeiras de
cada linha. Esquerda e direita sao recortes independentes, preservando assimetrias
do desenho e da bolsa do Ricardo. A terceira pose idle do protagonista repete a
frente; para a esquerda foi aproveitada a primeira pose da linha esquerda. A pose
idle direita fornecida ja tem um pe levantado. Para parados laterais rigorosamente
neutros, esses dois quadros do protagonista merecem desenho manual futuro.

Os sprites da sheet ja sao pequenos (aproximadamente 110–130 pixels de altura).
Nao faltam quadros para executar as animacoes; os retratos maiores tem qualidade
superior. Os contornos escuros, especialmente junto aos sapatos, ainda podem
beneficiar-se de retoque pixel a pixel: nao ha uma garantia automatica de ausencia
absoluta de residuos ou irregularidades em qualquer cor de fundo. As conferencias
usam xadrez claro para deixar esses detalhes visiveis. Nenhum asset foi recriado
por IA ou ampliado com suavizacao.

## Validacao

- `python main.py --smoke-test`: 55 testes aprovados.
- `python teste_movimentacao.py --smoke-test`: aprovado.
- Conferencia visual das sheets, dos recortes, dos paineis e do render da sala.
- Testes de hashes de fontes, outputs, backup e imagens protegidas; alinhamento
  dos 32 sprites; carregamento exato dos pixels; preservacao de preto interno.
- Suite existente: movimento, FPS, animacao, repouso, sombras, colisoes, portas,
  camera, editor, dia/noite, olho magico, investigacao e comportamento dos moradores.

A validacao do jogo foi automatizada com SDL dummy, sem uma sessao manual
interativa. Nenhuma logica de infeccao foi implementada; `logica_infeccao.py`
permanece reservado aos alunos. Fisica, escala dos cenarios, hitboxes, sombra e
posicoes de entrada nao foram alteradas.
