# Restauracao da arte e repouso correto do Ricardo

Esta revisao substitui as composicoes e limpezas experimentais anteriores.

## O que estava errado

Os caminhos de direcao do carregador do protagonista estavam corretos. O problema
estava no conteudo dos PNGs: os seis passos laterais tinham recebido o tronco do
novo idle, substituindo partes dos desenhos de caminhada. A erosao tambem havia
alterado pixels da silhueta. Esses passos voltaram aos desenhos integrais do
backup `backups/sheets_20261017_152232_838869/`, anterior a essas alteracoes.
Os demais passos e parados frente/costas dos dois personagens tambem usam essa
base mais integra. Nao ha mais composicao de pernas/tronco no fluxo oficial.

O idle esquerdo do Ricardo vinha do primeiro quadro da linha de caminhada
esquerda. Agora usa o espelhamento do parado direito autentico da sheet. Frente
e costas usam seus respectivos parados; nenhum deles e escolhido pelo indice
da caminhada. O parado lateral do protagonista continua vindo da referencia
oficial `referencias/protagonista_parado_lado.png`, sem erosao final do corpo.

## Arquivos realmente carregados

| Personagem | Estado | Caminho |
| --- | --- | --- |
| Protagonista | parado direita/esquerda | `personagens/protagonista/processados/parado/{direcao}.png` |
| Protagonista | andando direita/esquerda | `personagens/protagonista/processados/andando/{direcao}/{1,2,3}.png` |
| Ricardo | parado nas quatro direcoes | `personagens/visitantes/ricardo/sprites/{direcao}.png` |
| Ricardo | andando nas quatro direcoes | `personagens/visitantes/ricardo/andando/{direcao}/{1,2,3}.png` |

O protagonista usa idle → passo 1 → idle → passo 3 para direita e idle → passo 2
→ idle → passo 3 para esquerda. Frente/costas mantem tres quadros. O Ricardo
intercala idle nas quatro direcoes: passos 1/3 para direita, 2/3 nas demais.
Ao parar, ambos usam o parado da ultima direcao, sem reaproveitar o ultimo passo.
Os intervalos por pose e a velocidade fisica permanecem iguais.

## Fim do deslocamento do NPC

`Resident.update` agora chama `rest()` tambem quando o tempo de deslocamento
termina exatamente ao final do dt. Antes, esse caso deixava o estado de caminhada
ativo ate a atualizacao seguinte. `Resident.image` exige tanto `walking` quanto
`moving` para desenhar um passo; uma flag `moving` antiga nao supera o repouso.
O repouso zera a fase e usa `assets.sprites[direction]`. A escolha automatica
de trajetoria, a velocidade, as colisoes e a sombra foram preservadas.

## Limpeza conservadora

O restaurador nao afina contornos nem apaga pixels do componente principal.
Descarta somente componentes desconectados fora da caixa do corpo. Componentes
pequenos dentro dela sao conservados, pois podem ser detalhes reais. Quando uma
ultima linha era apenas ruido externo, o desenho e deslocado verticalmente ate
o apoio y=94, sem redimensionar o corpo. Os canvases continuam RGBA 64x96.

Permanecem apenas os dois retoques externos ja conferidos nos ganchos junto a
sola esquerda do protagonista (parado frente e passo 2 frente). Os testes
comparam todos os pixels do componente corporal dos 24 passos com o backup,
descontando somente esse retangulo explicitamente retocado e a translacao de
apoio. Isso protege cabelo, rosto, mochila, jaqueta, pernas e sapatos.

Ainda ha pequenas irregularidades escuras nos contornos de alguns passos da
sheet, especialmente entre as pernas e perto das solas (frente 3 e costas 3 do
protagonista). Foram conservadas quando ligadas ao corpo e ambiguas, conforme
a prioridade de preservar a arte. A nova referencia lateral e a sheet de passos
tambem tem pequenas diferencas artisticas de rosto/mochila. Nao afirmo que todas
essas irregularidades desapareceram; uniformizacao completa exigiria retoque
artistico localizado, sem um filtro global.

## Conferencia no jogo

- [Repouso real do Ricardo apos terminar o deslocamento, nas quatro direcoes](ricardo_reposo_real.png)
- [Render Pygame com protagonista e Ricardo nas quatro direcoes e fases](ajuste_lateral_render.png)
- [Protagonista ampliado: todos os parados e ciclos](animacoes_protagonista.png)
- [Ricardo ampliado: todos os parados e ciclos](animacoes_ricardo.png)
- [Todos os 16 quadros do protagonista](../personagens/protagonista/processados/conferencia_sheet.png)
- [Todos os 16 quadros do Ricardo](../personagens/visitantes/ricardo/conferencia_sheet.png)
- [GIF do render do jogo](ajuste_lateral_jogo.gif)

As conferencias ampliadas e os recortes de `House.draw` foram inspecionados.
O painel de repouso usa `Resident.update`, deixa o deslocamento terminar, confirma
que nao ha movimento no intervalo seguinte e so entao captura o sprite exibido.
Nao e uma imagem escolhida manualmente como idle. A captura usa SDL dummy;
nao houve sessao interativa por teclado nem avaliacao continua em reprodutor GIF.

## Arquivos e verificacoes

Criado: `restaurar_sprites_integros.py`. Alterados: `preparar_sheets.py` (fluxo
oficial chama o restaurador), `casa/sprite_cleanup.py` (referencia sem erosao
final), `casa/resident.py`, scripts de conferencia/captura, testes, manifestos,
32 sprites e conferencias. A lista completa dos outputs permanece nos JSONs
`dados/sheets/{protagonista,ricardo}.json`.

Backup da aparencia anterior a esta revisao:
`backups/sheets_20261017_155014_688409/`. O backup base de restauracao tambem foi
preservado, assim como as sheets e os originais. Porta, investigacao e caches
protegidos do Ricardo continuam com os mesmos hashes. Nenhuma logica de infeccao
foi implementada.

Validacao: **63 testes aprovados** em `python main.py --smoke-test`, incluindo
preservacao dos pixels corporais, fonte oficial, ciclos, carregamento, repouso
no limite exato de dt, flag antiga de movimento, FPS, sombras, colisoes, portas,
editor, dia/noite e investigacao. `python teste_movimentacao.py --smoke-test`
tambem passou.

Reproduzir com `python preparar_sheets.py`, `python conferir_animacoes.py` e
`python validar_animacoes_jogo.py`. O preparador faz backup antes de escrever e
restaura a base integra; nao reaplica a erosao nem as composicoes anteriores.
