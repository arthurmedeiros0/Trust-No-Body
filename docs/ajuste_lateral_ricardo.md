# Idle lateral oficial e revisao visual do Ricardo

**Superado pela [restauracao da arte e correcao do repouso](restauracao_sprites_idle.md).**
As composicoes de tronco/pernas descritas abaixo foram removidas.

A fonte nova e `personagens/protagonista/referencias/protagonista_parado_lado.png`
(PNG 1254x1254). Ela agora gera os parados direita/esquerda usados no jogo, sem
reconstrucao de pernas nem reutilizacao de pose de caminhada. A esquerda e o
espelhamento da direita. O manifesto registra caminho e SHA-256 dessa fonte.

## Tratamento dos sprites

O recorte lateral remove o fundo por conectividade. A mascara recupera interiores
escuros e protege especificamente a mochila quase preta com um poligono no
espaco da referencia. Os pixels originais da mochila sao preservados; nao ha
repintura. O resultado usa NEAREST, RGBA 64x96, altura corporal de 88 px e apoio
em y=94, como os demais sprites.

Nos 32 sprites ativos, a limpeza de pequenas saliencias passou a abranger tambem
o corpo, a partir de y=30, combinando cor neutra escura, espessura e vizinhanca.
Antes de remover um pixel, verifica se ele liga partes relevantes da silhueta:
isso protege pescoco, cabelo, maos e bolsa. Ilhas externas sao descartadas.
Preto interno e detalhes claros nao sao apagados por limiar global.

A inspeção do render identificou ainda residuos em gancho presos a sola esquerda
do protagonista em `parado/frente.png` e `andando/frente/2.png`. Essas duas pequenas
regioes recebem mascaras explicitas, fora do sapato real; um teste protege esses
retoques. Isso evita aumentar a agressividade da limpeza sobre todos os desenhos.

## Caminhada

Protagonista: direita usa **idle → passo 1 → idle → passo 3**; esquerda usa
**idle → passo 2 → idle → passo 3**. O idle vem sempre da nova referencia oficial.
Frente/costas permanecem com os tres passos. Velocidade e intervalo de 0,14 s
por pose permanecem iguais.

Para evitar mudanca de rosto entre o novo idle e a sheet antiga, os passos
laterais do protagonista tambem preservam o tronco da referencia oficial; as
pernas continuam vindo dos quadros de caminhada, sem modificar a fisica.

Ricardo: nao bastava inserir idle. As poses variavam rosto, tronco e bolsa,
produzindo oscilacao visual. Os quadros internos foram compostos com o tronco
do idle correspondente e as pernas dos passos, a partir de y=67. Essa parte
superior permanece identica pixel a pixel, sem recentralizacao entre quadros.
O passo 3 direito recebe a fase de pernas do passo 2 esquerdo espelhada; o
tronco e a bolsa continuam orientados pela pose direita original.

Agora todas as direcoes do Ricardo intercalam o parado: direita 1/3; esquerda,
frente e costas 2/3. Sao quatro poses, **idle → passo A → idle → passo B**, com
0,18 s por pose. Ao parar, aparece o idle correspondente. Ha uma escolha visual
deliberada de tronco mais estavel, com menos balanco dos bracos, em vez das
mudancas de rosto e bolsa entre os desenhos da sheet.

Somente o carregador seleciona esses ciclos. A logica de movimento automatico,
velocidade, pausas, colisoes e sombra do NPC nao foi modificada nesta revisao.

## Conferencia visual

- [Protagonista ampliado e ciclos](animacoes_protagonista.png)
- [Ricardo ampliado e ciclos](animacoes_ricardo.png)
- [Capturas do render real, quatro fases nas quatro direcoes](ajuste_lateral_render.png)
- [Sala com os novos sprites](ajuste_lateral_sala.png)
- [GIF do render real do jogo](ajuste_lateral_jogo.gif)
- [GIF do protagonista](animacoes_protagonista.gif) e [GIF do Ricardo](animacoes_ricardo.gif)

As imagens ampliadas e o painel do render real foram inspecionados. A verificacao
nao ficou restrita a testes de ordem dos quadros: confirmou mochila do novo idle,
pe apoiado, sombra sobre o piso e estabilidade do tronco do Ricardo no desenho
produzido por `House.draw`. O script percorre fases conhecidas e gera um GIF com
os tempos reais de cada personagem. Nao houve uma sessao manual interativa;
nao afirmo ter avaliado a sensacao de controle por teclado ou assistido ao GIF
em um reprodutor. Pequenas diferencas de textura nas pernas da sheet permanecem;
uma uniformizacao artistica total exigiria redesenhar os passos. Nao identifiquei
outro residuo evidente que exija correcao manual nas conferencias finais.

## Arquivos e reproducao

Alterados: `casa/sprite_cleanup.py`, `preparar_sheets.py`, `casa/animation.py`,
`casa/visitor_assets.py`, `conferir_animacoes.py`, `tests/test_limpeza_animacao.py`,
os dois manifestos em `dados/sheets/`, 32 sprites ativos e imagens de conferencia.
Criados: `validar_animacoes_jogo.py`, este relatorio, capturas e GIF do render.

Backup anterior a qualquer substituicao desta revisao:
`backups/sheets_20261017_153705_349708/`. Seu caminho esta tambem em
`dados/sheets/backup_ajuste_lateral.txt`. Contem sprites, configuracao e copias dos
scripts anteriores. O backup da integracao inicial e os originais continuam intactos.

Reproduzir:

```powershell
python preparar_sheets.py
python conferir_animacoes.py
python validar_animacoes_jogo.py
python main.py --smoke-test
python teste_movimentacao.py --smoke-test
```

Validacao automatizada: **63 testes**, cobrindo tambem a fonte oficial, pixels do
tronco do Ricardo, idle nas quatro direcoes, mascaras retocadas, alinhamento,
FPS, sombras, colisoes, portas, editor, dia/noite, investigacao e visitantes.
O teste isolado de movimentacao tambem passou. Porta, investigacao e caches
protegidos do Ricardo foram conferidos por SHA-256 contra o backup; nenhum mudou.
Mapas, dialogos, olho magico e logica de infeccao foram preservados.
