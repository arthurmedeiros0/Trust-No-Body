# Ricardo: sprites individuais e idle entre os passos

## Ajuste visual dentro da casa: +8%

`casa/resident_render.py` define `RICARDO_VISUAL_SCALE = 1.08`. O render da casa
amplia em memoria todos os parados e passos do Ricardo com `pygame.transform.scale`,
de canvas 64x96 para 69x104 (dimensoes arredondadas). As superficies ampliadas sao
reutilizadas por cache. Nenhum PNG ou original foi redimensionado em disco.

A ancora passa de (32,94) para (34,102), acompanhando a escala efetiva arredondada.
Assim, o ultimo pixel dos pes continua imediatamente acima da posicao logica do
chao. A sombra e a hitbox mantem seus tamanhos e posicoes. Os ciclos, intervalos,
estado de repouso e movimento automatico permanecem intactos; porta, exames,
retratos e protagonista nao passam por esse render ampliado.

[Conferencia lado a lado no render da sala](ricardo_escala_108.png).
**72 testes aprovados**, incluindo escala dos 12 quadros, ancora dos pes, pixels
NEAREST, preservacao da imagem fonte, ordem sombra/personagem, hitbox, posicao,
ciclos, retorno ao idle e suite existente. O teste isolado de movimentacao
tambem passou. A captura foi inspecionada visualmente com ambos apoiados na mesma
linha do piso; nao houve sessao manual interativa.

Os valores de altura e canvas descritos a seguir referem-se aos arquivos fonte,
antes deste aumento exclusivo da renderizacao interna.

Os sprites internos ativos agora sao os novos arquivos individuais. Protagonista,
porta, investigacao e retratos de dialogo nao foram substituidos.

## Identificacao visual das fontes

Todos os nove PNGs estao em `personagens/visitantes/ricardo/referencias/` e medem
585x585. Foram inspecionados visualmente, incluindo pernas e orientacao do rosto.

| Direcao | Parado | Passo 1 | Passo 2 |
| --- | --- | --- | --- |
| Frente | `frente.png` | `andandofrente1.png` | `andandofrente2.png` |
| Costas | `costas.png` | `andandocostas1.png` | `andandocostas2.png` |
| Direita | `lado.png` | `andandolado1.png` | `andandolado2.png` |
| Esquerda | espelho de direita | espelho de direita | espelho de direita |

Nao foi encontrada uma imagem olhando para a esquerda. Os dois arquivos
`andandolado` olham para a direita e apresentam passadas semelhantes, com
variacao de abertura das pernas. Nao foram criadas poses novas nem aproveitados
sprites de frente/costas para completar as laterais. O espelhamento foi usado
somente para obter a direcao ausente, conforme autorizado.

## Processamento conservador com Pillow

Os arquivos fornecidos ja sao RGBA, com alpha externo zero. O preto mostrado em
alguns visualizadores e a area transparente, nao um fundo preto do arquivo. Por
isso o processamento preserva o alpha existente; nao aplica limiar de branco,
erosao, filtros de contorno, recorte por componente nem composicao de partes do
corpo. Os pixels claros da borda tambem foram conservados para proteger jaleco,
solas e detalhes originais. Ha uma rotina de inundacao de branco ligado as bordas
para futuras fontes opacas; ela nao foi necessaria nestes nove PNGs.

O recorte usa a caixa do alpha original. Todos recebem um fator proporcional
comum de **2/9**, interpolacao NEAREST e canvas RGBA **64x96**, com o ultimo pixel
visivel apoiado em y=93 (linha de apoio y=94). Nao ha escala individual para fazer
cabecas ou bolsas crescerem entre quadros, nem esticamento separado dos eixos.
Os testes comparam o alpha e todos os pixels visiveis reduzidos com as fontes.

**Limites das fontes:** a distancia entre cabelo e sola varia com a postura das
pernas; a altura visivel final fica entre **84 e 88 pixels**. Esse pequeno balanco
vertical preserva o mesmo fator de escala e o alinhamento dos pes. Nao normalizei
cada pose para 88 px, pois isso alteraria o tamanho da cabeca/corpo. Nas laterais,
as duas imagens nao representam claramente pernas opostas. O ciclo usa os dois
quadros existentes com idle intermediario; uma alternancia lateral mais distinta
precisaria de outra imagem original. Alguns pixels claros de contorno das fontes
continuam visiveis em fundo escuro, sem uma nova limpeza agressiva.

## Organizacao e carregamento

```text
personagens/visitantes/ricardo/
  referencias/                       nove originais intactos
  sprites/{frente,costas,direita,esquerda}.png
  andando/{frente,costas,direita,esquerda}/{1,2}.png
dados/animacoes/ricardo_individual.json
```

Sao **quatro idles e oito passos ativos**. Os terceiros passos antigos foram
retirados da pasta ativa depois de copiados para o backup. Os antigos originais
`sprites/ricardo_*.png` e `sprites_movimento/` permanecem preservados e inativos.

`dados/visitantes/ricardo.json` aponta para `internal_sprite_manifest`; o carregador
le exatamente as listas de quadros desse manifesto, aceitando quantidades
variaveis. O arquivo registra fonte, recorte, escala, posicionamento, espelhamento
e hashes de cada output. O manifesto antigo da sheet e os dados das animacoes
anteriores permanecem historicos e nao controlam estes novos quadros.

Backup anterior a substituicao:
`backups/ricardo_individual_20261017_172450_454639/`. Contem `sprites/`, `andando/`,
configuracao anterior e `preservados.json`, com hashes dos originais e dos
sistemas que esta tarefa nao pode alterar. Reprocessamentos fazem outro backup.

## Ciclo e estado de repouso

Em **todas as quatro direcoes**, o ciclo e exatamente:

**parado correspondente → passo 1 → parado correspondente → passo 2 → repetir**.

Mantido o intervalo configurado de **0,18 s por pose**, totalizando 0,72 s por
ciclo. O tempo e acumulado em segundos, sem depender do numero de frames da tela.
O protagonista continua com os sprites e ciclos classicos, sem alteracoes.

O NPC expoe `animation_state` (`idle` ou `walk`). A selecao visual exige tanto
intencao de caminhar quanto deslocamento efetivo. Cada subpasso so marca
`moving` se a posicao realmente mudou; velocidade zero nao anima caminhada.
Quando parado ou bloqueado, o contador e zerado, a ultima direcao e conservada
e `sprites/{direcao}.png` aparece imediatamente. Uma flag antiga de movimento
nao pode sobrepor um estado de repouso. O encerramento exato do deslocamento
ao final do dt e a interrupcao por colisao continuam chamando `rest()`.

Nao foram alterados velocidade fisica, escolha automatica de caminho, pausas,
limites da sala, hitbox, colisoes com protagonista/moveis ou sombra.

## Conferencia visual e execucao do jogo

- [Sequencias ampliadas, com idle repetido em cada direcao](ricardo_individual_ciclos.png)
- [Quatro fases desenhadas por House.draw no cenario](ricardo_individual_render.png)
- [Repouso real apos Resident.update encerrar o movimento](ricardo_individual_reposo.png)
- [GIF das quatro direcoes no render](ricardo_individual_jogo.gif)
- [Movimentacao automatica real: GIF de 12 segundos](ricardo_individual_automatico.gif)
- [Capturas das mudancas automaticas de estado](ricardo_individual_automatico.png)
- [Registro de tempos, direcoes e posicoes](ricardo_individual_automatico.json)

As fontes, sequencias ampliadas, painel do render, repouso e capturas automaticas
foram inspecionados visualmente. A simulacao automatica usou `House.update` a
60 FPS durante 12 segundos, sem impor direcoes ou fases ao NPC, registrando
deslocamentos e pausas. As capturas confirmam que a aparencia de repouso volta
apos os movimentos. A execucao foi com SDL dummy; nao houve sessao manual por
teclado nem afirmacao de ter assistido ao GIF em um reprodutor. Os limites de
fluidez das duas passadas laterais semelhantes continuam registrados acima.

## Arquivos alterados e testes

Criados: `preparar_ricardo_individual.py`, `conferir_ricardo_individual.py`,
`dados/animacoes/ricardo_individual.json`, `tests/test_ricardo_individual.py`,
este relatorio e conferencias. Alterados: `casa/visitor_walk_assets.py`, somente
a montagem de ciclos do NPC em `casa/animation.py`, `casa/resident.py`, cadastro
do Ricardo, 12 PNGs internos ativos e comparacao. O restaurador legado recebeu
uma protecao para nao recolocar a sheet sobre os novos PNGs individuais.
Os testes antigos dependentes de tres quadros/sheet foram adaptados ao novo
contrato; os testes dos originais antigos e dos sistemas preservados continuam.

**70 testes aprovados** em `python main.py --smoke-test`. Tambem aprovado:
`python teste_movimentacao.py --smoke-test`. A suite cobre pixels/alpha, escala
comum, fontes intactas, espelhamento, carregamento, idle entre todos os passos,
interrupcao em cada fase, colisao com parede/movel/protagonista, velocidade zero,
tempo de animacao, FPS, sombra, hitbox, transicoes e demais sistemas existentes.

Os hashes confirmaram protagonista classico e todos seus assets recentes,
referencias do Ricardo, porta, investigacao, caches dos exames, retratos de
dialogo, mapas e scripts protegidos sem alteracoes. Nenhuma logica de infeccao
foi implementada.

Reproduzir os assets: `python preparar_ricardo_individual.py`.
Reproduzir as conferencias e simulacao: `python conferir_ricardo_individual.py`.
