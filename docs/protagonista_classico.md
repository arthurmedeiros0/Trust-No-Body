# Protagonista anterior as novas spritesheets

A exploracao e o teste isolado voltaram a carregar exatamente os 16 PNGs antigos.
A fonte foi `backups/sheets_20261017_150406_128619/personagens/protagonista/processados/`,
backup criado antes da primeira substituicao pelas sheets. Os arquivos foram
copiados byte a byte, sem reencodar, filtrar, limpar ou recriar imagens.

## Arquivos ativos

```text
personagens/protagonista/classicos/
  parado/{frente,costas,direita,esquerda}.png
  andando/{frente,costas,direita,esquerda}/{1,2,3}.png
  manifesto.json
  comparacao.png
```

Sao quatro parados e doze passos, todos em RGBA 64x96. O manifesto e a comparacao
do conjunto antigo tambem foram copiados. Origem, hashes dos 16 PNGs e caminho
da verificacao dos arquivos preservados estao em `dados/protagonista_classico.json`.

As sheets novas, os sprites recentes em `processados/`, retratos, expressoes e
referencias permaneceram intactos. A pasta `classicos/` separa os arquivos ativos
dos assets recentes guardados para uso futuro. Nenhum projeto ou commit inteiro
foi revertido.

## Animacao e codigo

- `casa/config.py`: `PLAYER_ASSET_ROOT` aponta para `classicos/` e
  `PLAYER_LATERAL_CYCLE` restaura `(0, None, 1, None, 2, None)`.
- `casa/sprites.py`: carrega os 16 PNGs dessa pasta.
- `casa/animation.py`: usa o ciclo antigo como padrao para o protagonista. O
  Ricardo recebe explicitamente sua configuracao atual, preservando seus ciclos.
- `teste_movimentacao.py`: utiliza o mesmo caminho ativo da exploracao.
- `preparar_sprites.py`: reconhece o conjunto classico ativo e nao o reprocessa
  nem encaminha para o preparador das sheets.
- Testes de ciclo/carregamento foram atualizados para o protagonista classico;
  `tests/test_protagonista_classico.py` verifica os bytes e os assets preservados.

Laterais: **passo 1 → parado → passo 2 → parado → passo 3 → parado**.
Frente e costas: **passo 1 → passo 2 → passo 3**. Intervalo original mantido:
**0,14 segundo por pose**, ciclo lateral completo de 0,84 segundo.
Ao interromper o movimento, volta ao parado da direcao correspondente.
Nao foram alterados movimento fisico, velocidade, sombra, hitbox ou transicoes.

## Validacao

- `python main.py --smoke-test`: **65 testes aprovados**.
- `python teste_movimentacao.py --smoke-test`: aprovado.
- Os 16 PNGs ativos sao identicos em bytes aos do backup; as superficies
  carregadas pelo jogo tambem foram comparadas nas quatro direcoes.
- A suite verifica ciclos, repouso, FPS, escala, sombra, hitbox, portas,
  transicoes, colisoes, visitantes e investigacao.
- Hashes de todos os arquivos atuais do Ricardo e dos sprites/referencias recentes
  do protagonista conferidos contra a captura anterior a esta restauracao em
  `backups/protagonista_classico_20261017_155757/preservados.json`.
- [Comparacao original dos 16 sprites](../personagens/protagonista/classicos/comparacao.png)
  e [captura do protagonista classico na sala](protagonista_classico_sala.png)
  inspecionadas visualmente. A captura veio do render real do Pygame com SDL
  dummy; nao houve sessao manual interativa.

Ricardo, investigacao, mapas, dialogos, olho magico, dia/noite e logica
proposicional nao foram revertidos. As alteracoes anteriores desses sistemas
permaneceram no workspace.
