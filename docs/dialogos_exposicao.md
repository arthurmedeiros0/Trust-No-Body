# Correção de diálogos e exposição por publicação

Evolução posterior: o [terceiro padrão e as conversas progressivas](terceiro_padrao_conversas.md) acrescentam o marco do dia 17 e substituem a lista completa de perguntas por duas opções pendentes e uma tela separada de resposta. Os detalhes abaixo registram a correção anterior de limites e publicação.

As alterações partem dos arquivos locais, preservando as mudanças anteriores ainda sem commit. Não houve commit ou push.

## Arquivos desta correção

- `casa/visitor_ui.py`: áreas separadas de nome, fala, perguntas e ações; quebra de linha; paginação; limites reais de renderização.
- `casa/visitors.py`: validação interna da exposição com sintomas reais e boletins já publicados no dia encerrado.
- `tests/test_dialogos_paginados.py` (novo): seis testes de renderização, geometria, integridade do texto e navegação.
- `tests/test_exposicao_publicacao.py` (novo): oito testes dos marcos de exposição e separação do conhecimento do jogador.
- `tests/test_infeccao_sobrevivencia.py`: os testes de exposição consecutiva agora começam após a publicação dos dois padrões, em vez de exigir mortes nos dias 1 e 2.
- `tests/test_entrada_olho_magico.py`: o objeto que registra a ordem das camadas ganhou as operações de recorte usadas pela nova renderização. As verificações de ordem foram preservadas.
- `README.md`, `docs/infeccao_sobrevivencia.md` e este relatório: instruções e descrição da regra atualizada.

`casa/visitor_dialogue.py` e `casa/peephole.py` foram analisados e não precisaram de alterações. As histórias e respostas carregadas do JSON permanecem intactas.

## Causa e solução dos diálogos

O método `text()` quebrava linhas pela largura, mas incrementava a coordenada vertical sem respeitar a altura do retângulo nem o recorte da superfície. Além disso, a área de fala começava em y=177 com altura 195, enquanto as perguntas começavam em y=335: havia uma interseção de 37 pixels antes mesmo de considerar o transbordamento do texto. Ao voltar à tela inicial, a fala completa era desenhada em uma área de apenas 30 pixels de altura, perto do nome e das ações.

A tela de conversa agora tem título separado, uma caixa delimitada de fala, uma faixa de navegação, perguntas abaixo e Voltar no rodapé. A tela inicial e as confirmações também têm suas próprias caixas e paginação. As perguntas dos sete visitantes cabem nos botões correspondentes, incluindo os personagens com nove perguntas.

A quebra de linha usa a largura medida pela fonte do Pygame, preserva os parágrafos e também divide palavras que excedam uma linha inteira. Cada página contém somente a quantidade de linhas que cabe na altura da caixa. O desenho fica recortado à interseção da caixa com o recorte original da superfície, restaurando esse recorte ao terminar. Assim, texto nenhum pode invadir o nome, as perguntas ou as ações.

Falas extensas podem ser lidas integralmente usando **Anterior/Próxima**, **←/→** ou **Page Up/Page Down**. O indicador mostra a página atual e o total. Escolher outra resposta ou voltar de tela reinicia a paginação. As frases originais não foram encurtadas nem substituídas.

O retrato continua sendo desenhado pelo mecanismo existente, com a mesma imagem, tamanho, proporção e posição. A solução vale na porta e nas interações com moradores. A aparência foi conferida em capturas renderizadas pelo Pygame para conversa, retorno à tela inicial e confirmação, sem janela visível.

## Causa e solução da exposição prematura

Antes, `_end_day()` verificava apenas se existia um morador vivo, acolhido e realmente infectado. Por isso, o encerramento do dia 1 contava uma exposição e o encerramento do dia 2 causava a derrota, sem considerar os marcos de publicação.

Agora a sessão monta um conjunto dos identificadores dos boletins com data de publicação até o dia encerrado. Para cada infectado vivo acolhido, consulta a própria função do grupo com uma cópia dos sintomas reais completos e esse conjunto de boletins. Só é relevante para exposição quem produz `infectado` nessa consulta interna.

Isso reutiliza as implicações existentes sem copiá-las:

| Padrão real | Dias sem exposição por esse padrão | Primeira exposição | Segunda exposição e derrota |
| --- | --- | --- | --- |
| Primeiro | 1 a 6 | Encerramento do dia 7 | Encerramento do dia 8 |
| Segundo exclusivo | 1 a 13 | Encerramento do dia 14 | Encerramento do dia 15 |
| Ambos | 1 a 6 | Encerramento do dia 7 | Encerramento do dia 8 |

A publicação depende da data do boletim; não exige que o jogador o tenha assistido. Não há contagem retroativa. Infectados de padrão ainda não divulgado, saudáveis, visitantes aguardando e rejeitados não provocam exposição.

Múltiplos infectados relevantes contam uma única exposição por dia. Sem nenhum relevante vivo acolhido no encerramento, a sequência é interrompida, mesmo que exista alguém exclusivamente do segundo padrão antes do dia 14. Eliminar somente parte dos infectados relevantes não interrompe a sequência. Sair de cômodos ou acessar interfaces não muda o contador. O registro diário idempotente existente continua impedindo duplicidade.

O diagnóstico apresentado ao jogador permanece separado: `diagnosticar_visitante()` envia apenas as observações e notícias assistidas, com a exceção já existente do protocolo disponibilizado no Modo Teste. Nenhuma avaliação interna é mostrada na interface. A condição real e a geração dos sintomas permanecem inalteradas nesta correção.

## Testes

A execução final de `python main.py --smoke-test` executou **178 testes: 173 aprovados, 5 falhas preexistentes e nenhum erro**. Os 14 testes novos passaram. As cinco falhas são as mesmas registradas na implementação anterior: interação com a geladeira em duas suítes, prioridade entre morador e geladeira, escala divergente do backup e hash histórico de `colisoes/cozinha.json`.

A execução isolada dos dois arquivos novos e da suíte anterior de infecção passou: **27 testes aprovados**. Os testes novos cobrem:

- Todas as introduções e respostas originais dos sete visitantes na porta e como moradores.
- Falas curtas e muito longas; parágrafos; palavras maiores que a largura; todas as páginas acessíveis sem perder texto.
- Ausência de interseção entre caixa de fala e botões; limites de largura e altura; recorte real dos pixels e restauração do recorte anterior.
- Navegação por mouse e teclado, limites da paginação, reinício ao selecionar outra resposta e preservação dos pixels do retrato.
- Primeiro padrão desde o acolhimento no dia 1 até a derrota no dia 8; segundo padrão exclusivo até o dia 15; ambos no primeiro marco.
- Exposição sem assistir ao boletim, sem antecipar o diagnóstico investigativo.
- Eliminação do único infectado relevante; outro infectado ainda não divulgado; múltiplos moradores; saudáveis; repetição do encerramento e interfaces sem reiniciar o contador.

As regras de fome, sede, solidão, suprimentos, vitória, eliminação e agenda continuam nas suítes de regressão existentes. Os cinco problemas já conhecidos de geladeira, prioridade de interação e divergências históricas de escala/hash permanecem fora desta correção; seus testes não foram removidos ou desativados.

## Preservação

`logica_infeccao.py` permaneceu intacto, com SHA-256 antes e depois:

`2D610702CC53398DAC1197CDCA900458E37575BF318D0AB9921950A264FBE26E`

Nenhum diálogo original, sprite, imagem, cenário, colisão, calendário de chegada ou quantidade de suprimentos foi alterado nesta correção.
