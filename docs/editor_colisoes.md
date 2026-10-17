# Editor visual e correções de colisão

Execute `python main.py --dev` e pressione F4. `python main.py` mantém o jogo normal, com F3 disponível e sem edição.

## Utilização

Clique e arraste num espaço sem obstáculos para criar um retângulo. Clique num obstáculo para selecioná-lo; arraste seu interior para mover. As oito alças brancas redimensionam os lados e cantos. Delete exclui apenas o obstáculo selecionado. ESC desfaz o arraste atual; pressionado sem arraste, sai da edição. F4 também alterna a ferramenta.

Ctrl+S salva apenas o cômodo atual e exibe confirmação. Solte o mouse antes de salvar; salvar durante um arraste cancela esse arraste incompleto. O asterisco identifica alterações pendentes. As alterações permanecem em memória ao sair do editor, mas só persistem após Ctrl+S. Fechar o programa descarta alterações não salvas.

Tab alterna entre os cinco cômodos para editar; essa é uma ferramenta de desenvolvimento, sem alterar a navegação normal por portas. Setas deslocam a câmera enquanto o jogador fica parado. F3 e F6 continuam funcionando.

P alterna para edição do piso. Nos pisos poligonais, arraste as alças dos vértices; nos pisos retangulares, use as alças dos lados/cantos ou arraste o interior. Delete não apaga o piso. Preserve a ordem dos vértices e evite cruzar suas arestas. Pressione P novamente para voltar aos obstáculos.

As regiões amarelas das interações não são selecionáveis. Os pontos de entrada, saídas, escalas, animações e sombra permanecem nas configurações anteriores.

## Persistência e backups

Cada cômodo tem seu arquivo em `colisoes/`: `banheiro.json`, `sala.json`, `corredor.json`, `quarto.json` e `cozinha.json`. O JSON contém versão, nome do cômodo, resolução original, limite/polígono do piso e obstáculos identificados por nome. Todos os valores usam pixels da arte original, antes de escala e câmera. Esses arquivos são carregados automaticamente na inicialização.

Antes da migração, `casa/config.py` e as colisões de todos os cômodos foram copiados para `backups/colisoes_antes_editor/`. As colisões de corredor, quarto e cozinha foram importadas sem mudanças. O conjunto anterior de obstáculos de banheiro e sala também está preservado nesse backup.

Cada Ctrl+S valida os dados, cria uma cópia datada do JSON anterior em `colisoes/backups/` e substitui o arquivo por meio de um temporário. Em caso de erro, a interface mostra a falha. Nenhuma imagem original é modificada.

## Correções realizadas

No banheiro, pia/armário, vaso, lixeira e box receberam limites correspondentes à área ocupada. O piso começa abaixo da faixa de móveis, impedindo a posição indevida entre pia e vaso mostrada na captura. Estante, planta e cestos continuam separados, com espaço central livre. O polígono inferior acompanha o recuo das paredes, mantendo a porta acessível.

Na sala, a mesa de centro e a poltrona agora bloqueiam toda a sua projeção ocupada, e a mesinha lateral foi corrigida. O sofá tem um retângulo central e dois braços separados, permitindo o acesso à faixa estreita entre mesa e sofá sem liberar a antiga posição sobre o assento. O teste percorre essa faixa nos dois sentidos em y=425 da arte. A posição y=450, antes permitida sobre o sofá, é bloqueada.

Escalas, dimensões, hitbox dos pés, sombra, animações, navegação e dia/noite não foram alterados. A ferramenta edita somente dados de colisão.

## Arquivos criados ou modificados

- Novos: `casa/collision_data.py`, `casa/collision_editor.py`, cinco arquivos em `colisoes/`, backups iniciais e `tests/test_editor_colisoes.py`.
- Modificados: `main.py`, `casa/game.py`, `casa/scenes.py` e `casa/config.py` para integrar o editor e retirar as coordenadas antigas da fonte Python.
- Testes existentes adaptados para consultar a fonte JSON e percorrer a passagem corrigida.
- README, documentação de coordenadas e capturas de banheiro/sala atualizados.

## Testes e ajustes manuais

Os vinte testes automatizados passaram, incluindo circulação/saídas, bloqueios do banheiro e sofá, passagem entre mesa e sofá, eventos de criação/movimento/redimensionamento/exclusão/cancelamento, salvamento e recarga, backup, edição do piso, câmera, isolamento das interações e regressões de escala/sombra/animação. O teste isolado de movimentação também foi executado.

Capturas atualizadas: `banheiro_editor.png`, `sala_editor.png`, `banheiro_debug.png` e `sala_passagem.png`. As renderizações do banheiro e da passagem da sala foram inspecionadas. Os testes usam SDL dummy; o uso do mouse e a sensação da passagem estreita ainda devem ser avaliados numa janela real.

Não há bloqueio conhecido das portas. Os cantos arredondados da poltrona, os braços do sofá e as bases dos cestos podem receber ajustes finos no editor. A faixa entre mesa e sofá é estreita na própria imagem; não foi ampliada artificialmente nem resolvida alterando a escala. Partes superiores do sprite podem se sobrepor visualmente aos móveis porque a física usa os pés e o cenário é uma imagem única.
