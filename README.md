# Trust No Body — exploração da casa

**Regras atuais de fome e sede:** a HUD inclui a previsão do dia atual; dias completos são registrados somente ao dormir. Sem água desde o início, o dia 3 começa com sede 2/2 e pode ser explorado inteiro, mas dormir sem água causa derrota sem iniciar o dia 4. Com água suficiente e sem comida, o equivalente ocorre no dia 4 com fome 3/3. Conseguir e consumir a ração no dia crítico zera a privação. O dia 1 continua de tolerância. Veja [previsão e encerramento diário](docs/previsao_privacao.md), que substitui as descrições anteriores dos limites.

No terminal do VS Code, aberto na raiz do projeto:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Janela de 1280 × 720. Dependências verificadas: Python 3.12.10, Pillow 12.2.0 e Pygame 2.6.1.

| Tecla | Ação |
|---|---|
| WASD / setas | Andar |
| E | Interagir com a porta ou objeto mais próximo |
| I | Abrir/fechar suprimentos (ESC tamb?m fecha) |
| F6 | Alternar dia/noite sem mudar a posição |
| F3 | Alternar depuração de colisões, interações, posição e escala |
| S ou Enter / N ou ESC | Dormir / cancelar na confirmação da cama |
| Enter / Espaço | Fechar mensagem |
| ESC | Voltar/fechar interfaces; encerrar durante a exploração |

O corredor conecta Sala, Quarto, Cozinha e Banheiro, nessa ordem da esquerda para a direita. Com a câmera horizontal, caminhe para os lados para ver as quatro portas. O retorno ocorre diante da mesma porta, com fade de 220 ms para escurecer e 220 ms para clarear.

No quarto, use E pelas bordas acessíveis da cama para dormir e avançar um dia, ou perto da TV para assistir ao noticiário. A partida começa no quarto, no dia 1, com comida e água zeradas e sanidade 8/8. O dia não avança por tempo real nem pela tecla F6. Assista ao boletim inicial e resolva visitantes aguardando na porta antes de dormir. A TV oferece o boletim atual e um histórico apenas das transmissões assistidas. Interfaces pausam a movimentação. Ricardo mantém conversa, investigação visual, decisões e estado entre os dias.

A HUD superior mostra dia, sanidade e a privação prevista incluindo o dia atual sem ração disponível. I ou a geladeira abre SUPRIMENTOS DA CASA, somente com comida e água armazenadas; I/ESC fecha. O dia 1 não consome recursos nem acumula fome ou sede para nenhum morador. A partir do dia 2, cada morador vivo consome 0,5 de cada recurso ao encerrar o dia. Sem água desde o início, o dia 3 começa com sede prevista 2/2: é possível explorar e obter recursos, mas dormir sem a ração causa derrota sem avançar. Com água suficiente e sem comida, o equivalente ocorre no dia 4 com fome prevista 3/3. Conseguir recursos atualiza a previsão; somente consumir ao dormir zera os dias completos registrados. Desde o dia 1, um dia inteiro sozinho reduz a sanidade em 1; companhia recupera 1, entre 0 e 8. Solidão continua causando derrota após cinco dias consecutivos sozinho. Consulte [previsão e contadores](docs/previsao_privacao.md), [sobrevivência](docs/sobrevivencia.md) e [cama e HUD](docs/cama_hud.md). A lógica de infecção permanece reservada ao grupo.

Controles, estrutura e validação do calendário: [dias, sono e televisão](docs/dias_sono_tv.md).

## Movimento e animação

A velocidade permanece em 220 pixels por segundo, com diagonal normalizada e controle por tempo. Cada quadro dura 140 ms. O ciclo lateral é `passo 1 → parado → passo 2 → parado → passo 3 → parado`; frente e costas continuam com três passos. Soltar as teclas mostra o sprite parado da última direção. Mudanças de direção reiniciam o ciclo.

O jogador conserva telas de **64 × 96 pixels em todos os cômodos**, sem redimensionamento ao atravessar portas. Os pés ficam alinhados na linha 93 dos sprites e a colisão usa uma base de 20 × 10 pixels. A animação é compartilhada com `teste_movimentacao.py`.

A orientação após atravessar uma porta vem do campo `direction` de cada conexão em `ROOMS`, em `casa/config.py`. Corredor → sala usa `costas` pela porta inferior; Entrada → sala usa `frente` pela porta superior. Retornos ao corredor usam `frente`; quarto, cozinha, banheiro e Entrada usam `costas`. O método central `House.change_room()` aplica a direção da passagem, seleciona a pose parada e reinicia a animação, preservando a posição de chegada.

Os três passos laterais dos originais são muito semelhantes. Inserir a pose parada atende ao novo ciclo, mas uma caminhada com pernas alternadas ainda depende de novos desenhos. Os sprites existentes não foram alterados.

## Escala, cenários e colisões

`casa/config.py` centraliza resoluções, escalas, entradas, saídas e interações. As colisões são carregadas de `colisoes/<comodo>.json`, em coordenadas da imagem original. Cenário, colisões e interações recebem a mesma transformação; a câmera altera apenas o desenho.

A escala agora é calibrada por ambiente: corredor 0,90; quarto 0,88; cozinha 0,90; banheiro 0,92; sala 0,68. Esses valores reduzem a altura aparente dos móveis em relação ao protagonista, usando portas, cama, sofá e armários como referência visual. O personagem mantém 64 × 96 em todos os ambientes. Os fatores estão em `ROOMS`, em `casa/config.py`, multiplicados por `SCENE_SCALE = 1.0`.

O corredor usa câmera horizontal para preservar a escala, em vez de reduzir toda a imagem até caber na janela. Os outros ambientes ficam centralizados com margens. O redimensionamento usa vizinho mais próximo, sem esticar os eixos nem suavizar a pixel art.

As imagens oficiais da sala são `trust_no_body_sala_dia_corrigida.png` e `trust_no_body_sala_noite_corrigida.png`. A porta inferior continua ligada ao corredor: entrada em `(343, 636)` e interação em `(343, 663)`. A porta superior agora leva à **Entrada**, com fade; o retorno aparece diante dessa mesma porta superior. As colisões dos cômodos antigos não foram alteradas nesta integração.

## Entrada da casa e olho mágico

Na sala, aproxime-se da porta superior e pressione E. Na Entrada, o personagem aparece pela passagem inferior, voltado para dentro. A passagem inferior retorna à sala; a porta principal superior é fechada e serve apenas para observar a rua.

Perto da porta principal aparece **[E] Olhar pelo olho mágico**. E abre a cena externa com fade. O protagonista fica oculto e imóvel, mantendo posição e orientação para o retorno. Use **ESC** ou o botão **Voltar** com o mouse. Com Ricardo aguardando, aparecem Conversar, Investigar, Aceitar, Rejeitar e Voltar. Sem visitante, Observar apenas mantém a vista. F6 alterna dia/noite também nessa tela.

Os arquivos originais foram preservados. Cópias `dia.png` e `noite.png` nas pastas `cenarios/entrada/` e `cenarios/olho_magico/` oferecem caminhos explícitos. A imagem diurna da rua disponível retrata o entardecer; a noturna retrata o luar. A visualização preserva proporção e perspectiva frontal, sem efeito circular ou olho de peixe.

A Entrada usa escala 0,50, com imagem original de 1536 × 1024 exibida em 768 × 512 e centralizada. O protagonista mantém 64 × 96, animações e sombra existentes. `colisoes/entrada.json` define móveis, plantas, sapateiras, porta fechada e limites; F3 e o editor F4 com `--dev` funcionam nesse cômodo, inclusive salvamento.

`casa/peephole.py` separa fundo, apresentação do visitante e interface. Ricardo tem posição e altura de retrato configuradas em `dados/visitantes/ricardo.json`. O grupo de sprites permanece disponível para futuras entidades. Relatório histórico da cena: [Entrada e olho mágico](docs/entrada_olho_magico.md).

## Ricardo: conversar, investigar e decidir

Ricardo chega à porta no primeiro dia depois de assistir ao boletim inicial na televisão. Acesse corredor → sala → porta superior → Entrada → porta principal. Conversar apresenta sua história e sete perguntas; a resposta sobre comida e água usa as quantidades sorteadas. Investigar permite examinar mãos, dentes, olhos, pescoço, palidez e tremores. As características já examinadas recebem `[visto]`; podem ser abertas novamente. ESC volta uma tela por vez.

Os seis sintomas booleanos e os suprimentos de Ricardo, de 2 a 3 unidades de cada recurso, são sorteados uma única vez por partida, com `random`. Abrir menus, alternar dia/noite e sair/voltar ao olho mágico não sorteiam novamente. Aceitar transfere seus recursos uma vez ao estoque compartilhado e o torna morador permanente. Reiniciar inicia uma nova partida. Não há gravação da partida em disco.

Após conversar ou examinar, Aceitar/Rejeitar abre uma confirmação. Confirmar o acolhimento remove o retrato da rua e coloca Ricardo em uma posição livre da sala, mais afastada das portas. Ele pausa de 2 a 4 segundos, escolhe uma direção e anda lentamente por 0,7 a 1,4 segundo, restrito a uma área próxima ao ponto inicial. A caminhada usa três quadros por direção, a cada 180 ms; ao descansar, aparece a pose parada correspondente. Seus pés colidem com móveis e protagonista; o protagonista também é bloqueado por ele. Confirmar a rejeição registra a decisão e remove o retrato. Nenhuma opção pode ser aplicada duas vezes ao mesmo visitante, e os valores sorteados são preservados.

**A lógica matemática fica exclusivamente com o grupo.** `logica_infeccao.py` contém apenas comentários. O estado é sempre `diagnostico_pendente`; não há expressões de infecção, classificações, deduções ou regras provisórias. `JournalKnowledge.published` apenas armazena notícias futuras.

Cadastro, parâmetros do NPC e caminhos: `dados/visitantes/ricardo.json`. Diálogos: `dados/visitantes/ricardo_dialogos.json`. Os originais foram preservados; retrato e quatro sprites transparentes ficam em `personagens/visitantes/ricardo/processados/`, agora com tratamento de contaminação branca nas bordas. Os 12 exames usam painéis escuros em `investigacao_processada/`, com proporções preservadas e fundo branco removido das mãos. Relatório atual: [correções visuais e NPC](docs/ricardo_correcoes_visuais_npc.md). Integração e novos cadastros: [Ricardo e investigação visual](docs/ricardo_investigacao.md).

Os nove originais de caminhada ficam intactos em `sprites_movimento/`. `dados/animacoes/ricardo.json` registra classificação visual e hashes. O carregamento prepara `andando/{frente,costas,direita,esquerda}/1.png` a `3.png`; a esquerda é espelhada da direita. Todos os quadros têm 64 × 96, altura visual de 88 e pés na linha 93. Compare em `personagens/visitantes/ricardo/andando/comparacao.png`. Os originais de caminhada têm cabeça proporcionalmente menor que os parados; isso não foi corrigido por deformação. Relatório desta etapa: [caminhada e resíduos claros](docs/ricardo_caminhada.md).

O banheiro usa um piso poligonal que acompanha a entrada estreita, com obstáculos individuais para pia/armário, vaso, lixeira, box, estante, planta e cestos. Seu limite superior bloqueia a faixa dos móveis que antes permitia ficar entre a pia e o vaso. Na sala, sofá e braços são separados; a passagem estreita entre mesa e sofá fica em torno de y=425 da arte original, e a antiga posição sobre o sofá em y=450 é bloqueada. As colisões dos outros ambientes foram importadas sem mudanças.

## Editor visual de desenvolvimento

```powershell
python main.py --dev
```

Pressione **F4** para editar. No jogo normal, sem `--dev`, o editor fica desabilitado.

| Controle | Ação no editor |
|---|---|
| Clique e arraste no vazio | Criar obstáculo retangular |
| Clique num obstáculo e arraste | Selecionar e mover |
| Arrastar alças brancas | Redimensionar selecionado |
| Delete | Excluir selecionado |
| Ctrl+S | Salvar o cômodo atual, com confirmação e backup |
| ESC | Cancelar arraste atual; sem arraste, sair da edição |
| F4 | Alternar edição |
| Tab | Alternar cômodo para editar |
| Setas | Deslocar câmera durante a edição |
| P | Alternar obstáculos/piso; arrastar vértices do piso poligonal |

As alterações afetam a colisão em memória imediatamente. **Salve cada cômodo com Ctrl+S antes de fechar o jogo.** O asterisco indica alterações pendentes. Sair do editor mantém as alterações em memória, sem salvar automaticamente. O jogador fica parado durante a edição; F3 e F6 continuam disponíveis. As interações amarelas são apenas referências e não podem ser editadas por essa ferramenta.

O backup inicial está em `backups/colisoes_antes_editor/`. Cada salvamento posterior preserva o JSON anterior em `colisoes/backups/`. Mais detalhes e arquivos modificados: [editor e relatório atual](docs/editor_colisoes.md).

A sombra é uma elipse de 34 × 12 pixels, com opacidade máxima 65/255 e deslocamento vertical de 2 pixels. É desenhada antes do protagonista, independe do cenário e não participa das colisões. Ajuste `SHADOW_SIZE`, `SHADOW_OPACITY` e `SHADOW_OFFSET_Y` em `casa/config.py`. F3 contorna a sombra em lilás, mantendo a hitbox em ciano.

O piso do corredor é poligonal e acompanha os recuos inferiores. Quarto e banheiro têm colisões específicas para cadeira, cabideiro e lixeira. A sala recebeu novos obstáculos para sofá, mesa de centro, poltrona, mesas laterais, estante e plantas. Os demais obstáculos existentes foram preservados.

F3 mostra piso em verde, obstáculos em vermelho, base dos pés em ciano, regiões de interação em amarelo e um painel com cômodo, escala, coordenadas originais dos pés e deslocamento da câmera.

Consulte [coordenadas e dimensões](docs/coordenadas.md) e o [relatório das correções](docs/relatorio_correcoes.md). Capturas em `docs/*_dia.png`, `docs/*_noite.png` e `docs/*_debug.png` permitem comparar o resultado.

## Estrutura

```text
main.py
casa/
    config.py          configurações centralizadas
    animation.py       ciclos compartilhados
    sprites.py         carregamento dos sprites
    scenes.py          escala e câmera dos cenários
    player.py          movimento e animação do jogador
    shadow.py          sombra visual compartilhada
    peephole.py        observação frontal independente
    collisions.py      pisos e obstáculos
    interactions.py    objetos interativos
    transitions.py     fade
    game.py            exploração e interface
personagens/protagonista/
    originais/         13 imagens originais preservadas
    processados/
        parado/        frente.png, costas.png, direita.png, esquerda.png
        andando/
            frente/    1.png, 2.png, 3.png
            costas/    1.png, 2.png, 3.png
            direita/   1.png, 2.png, 3.png
            esquerda/  1.png, 2.png, 3.png
        comparacao.png
        manifesto.json
cenarios/              imagens originais preservadas
preparar_sprites.py
teste_movimentacao.py
tests/
docs/
```

Para reproduzir o processamento: `python preparar_sprites.py`. O manifesto registra classificação visual, escala, recorte e hash de cada original; esquerda andando é espelhada da direita.

## Testes

```powershell
python main.py --smoke-test
python teste_movimentacao.py --smoke-test
```

Os testes cobrem as regressões anteriores, dados/sorteios, seis exames nas duas variantes, diálogos e decisões, além de painéis, tratamento das bordas, spawn seguro, passos do NPC, limites da sala e colisões mútuas. Incluem a identificação dos nove originais, dimensões/alinhamento dos 12 quadros, espelhamento, três fases em cada direção, repouso e animação em diferentes FPS. Os originais e `diagnostico_pendente` são verificados. Nenhum teste implementa ou resolve regras de infecção.

Os testes usam SDL dummy. A avaliação manual de teclado, fluidez e contornos finos dos móveis continua necessária. Como as imagens têm perspectivas e proporções artísticas diferentes, a calibração dos cenários não garante proporções anatômicas idênticas entre todos os objetos.

## Novas sheets dos personagens

O novo protagonista e os sprites internos do Ricardo ja estao integrados. Execute python preparar_sheets.py para reprocessar com backup. Porta e investigacao do Ricardo permanecem preservadas. Estrutura, conferencias e limites visuais: [relatorio das sheets](docs/novas_sheets.md).
