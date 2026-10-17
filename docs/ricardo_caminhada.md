# Ricardo — caminhada e limpeza de resíduos claros

## Identificação visual

Foram examinados exclusivamente os nove PNGs em `sprites_movimento/`, sem ambiguidade de direção. Todos têm 1122 × 1402, embora o enquadramento e o tamanho do personagem variem. Os arquivos compartilham o prefixo `Imagem do ChatGPT 17 de out. de 2026, `:

| Direção | Passo 1 | Passo 2 | Passo 3 |
|---|---|---|---|
| Direita | `14_06_11-1.png` | `14_06_13-2.png` | `14_06_14-3.png` |
| Frente | `14_06_15-4.png` | `14_06_16-5.png` | `14_06_17-6.png` |
| Costas | `14_06_18-7.png` | `14_06_20-8.png` | `14_06_21-9.png` |
| Esquerda | Espelho da direita 1 | Espelho da direita 2 | Espelho da direita 3 |

A ordem segue as poses observadas: passada aberta, aproximação das pernas e nova abertura/variação. Os quadros de frente e costas são semelhantes e não constituem uma alternância perfeita das pernas. Nenhuma pose nova foi inventada.

O mapeamento explícito e os hashes SHA-256 estão em `dados/animacoes/ricardo.json`. Se um original mudar, o processamento pede revisão do manifesto; não classifica a direção automaticamente pelo nome.

## Processamento e pastas

```text
personagens/visitantes/ricardo/
    sprites_movimento/           nove originais preservados
    andando/
        frente/                 1.png, 2.png, 3.png
        costas/                 1.png, 2.png, 3.png
        direita/                1.png, 2.png, 3.png
        esquerda/               1.png, 2.png, 3.png
        comparacao.png
        processamento.json
    processados/                retrato e parados tratados, versionados
    investigacao_processada/    exames tratados, versionados
```

O fundo quase preto dos novos quadros é removido somente quando conectado às bordas. Detalhes escuros internos do cabelo, sapatos e bolsa são mantidos. A escala usa a referência comum dos parados: 88 pixels de altura visual, proporção preservada, centralização horizontal e mesma linha de apoio. Um fator global de encaixe limita a largura sem distorcer o conjunto. As telas têm 64 × 96, último pixel dos pés na linha 93 e redimensionamento NEAREST.

O carregamento prepara/reutiliza os arquivos processados automaticamente. `andando/processamento.json` registra versão, assinatura dos recursos, tamanhos e escalas aplicadas. `comparacao.png` mostra parado e três passos por direção ampliados 3×, com quadriculado e linha de apoio. As versões espelhadas da esquerda também aparecem.

## Resíduos brancos e preservação da arte

A receita atual, identificada por `PROCESSING_VERSION`, invalida os caches antigos sem alterar originais. Ela combina conectividade com as bordas, cobertura alfa, cor neutra do fundo e análise de componentes claros pequenos. Ilhas externas sem ligação ao personagem são descartadas; detalhes claros internos conectados à silhueta são preservados. O fundo cinza misturado nas bordas também é considerado, incluindo ligações diagonais.

Nos punhos das imagens de mãos, uma máscara adicional protege a faixa de pele e encerra a limpeza ao alcançar a manga azul. A máscara remove resíduos neutros externos, sem recolorir a pele nem alterar manchas. O jaleco e os demais detalhes claros permanecem protegidos. Olhos, dentes, pescoço, palidez e tremores mantêm o conteúdo original nos painéis escuros existentes; não receberam um filtro global para apagar pixels brancos.

Enquadramento do retrato, âncora `(640, 625)`, altura de 490 e dimensões dos painéis de 900 × 460 foram preservados. As cores internas não foram recoloridas para esconder ruído. Originais das 17 imagens anteriores e dos nove quadros novos continuam intactos e têm hashes verificados.

## Integração da animação

`Resident` conserva o movimento, pausas, velocidade, raio, colisões e sombra anteriores. Agora registra apenas o tempo efetivamente caminhado. `Resident.image(assets)` seleciona um dos três passos da direção atual a cada 180 ms, com tempo configurável em `resident.frame_seconds`. Ao descansar ou encontrar um bloqueio, o tempo é reiniciado e o sprite parado correspondente é mostrado. Um novo trecho de caminhada reinicia o ciclo.

A seleção visual não altera pés, hitbox ou posição lógica. A direção esquerda usa as imagens espelhadas. O desenho da sombra continua antes do sprite, com as mesmas dimensões. Não foram intercaladas poses paradas no ciclo, pois a diferença de proporções artísticas entre parado e caminhada ficaria repetida em cada passo.

## Arquivos criados ou modificados

- Novo `dados/animacoes/ricardo.json`: nove fontes e classificação visual.
- Novo `casa/visitor_walk_assets.py`: preparação, espelhamento e comparação.
- `casa/visitor_image_processing.py`: remoção de preto e limpeza conservadora de resíduos claros/punhos.
- `casa/visitor_assets.py`: carregamento dos três quadros por direção e novas versões dos exames/retrato.
- `casa/resident.py`: estado visual da animação, preservando os passos e colisões.
- `casa/game.py`: desenho pelo quadro atual do NPC.
- `dados/visitantes/ricardo.json`: referência ao manifesto e duração dos quadros.
- Novo `tests/test_ricardo_caminhada.py`, README e capturas/documentação.

## Limitações e revisão manual

A comparação mostra uma diferença importante nos próprios desenhos: todos os nove quadros novos têm cabeça menor e corpo mais alongado que os quatro sprites parados, especialmente os quadros de costas. Altura total e pés estão consistentes, mas não é possível igualar essas proporções internas só com escala uniforme. Para uma transição artística perfeita, refaça o conjunto de caminhada no mesmo estilo dos parados ou forneça parados compatíveis. Nenhuma dessas imagens foi deformada ou regenerada.

Frente 1–3, costas 1–3 e direita 1/3 têm poses próximas; vale refazer fases com a perna oposta e uma passagem intermediária mais distinta. Permanecem tons claros legítimos de jaleco, pele e sapatos, e alguns detalhes finos do contorno precisam de avaliação artística em zoom; não foram apagados indiscriminadamente. A máscara dos punhos foi calibrada para as duas imagens atuais, devendo ser revisada se forem substituídas.

As renderizações do retrato, mãos e comparação dos 16 sprites foram inspecionadas. Os testes usam SDL dummy; fluidez percebida e detalhes finos ainda precisam ser avaliados jogando numa janela real.

## Verificação

Foram aprovados os **51 testes** de `python main.py --smoke-test`, o teste isolado de movimentação e a compilação dos módulos. Os testes incluem nove fontes/hashes, 12 arquivos RGBA 64 × 96, altura de 88, linha dos pés, centralização, espelhamento exato, presença dos detalhes claros, fundo preto conectado às bordas sem apagar preto interno, remoção de ilha branca externa com branco interno preservado, proteção da pele/manga na máscara dos punhos, três fases em todas as direções, repouso, reinício e comparação em 30/60/120 FPS. Também verificam que selecionar/desenhar a imagem não altera hitbox, sombra, sintomas ou diagnóstico, além de todas as regressões existentes de colisões, NPC, portas, investigação e decisões.

O módulo da lógica dos alunos continua somente com comentários e o diagnóstico permanece pendente.
