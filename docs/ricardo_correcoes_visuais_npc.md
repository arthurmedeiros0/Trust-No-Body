# Ricardo — correções de imagem, movimento e colisão

Execute `python main.py`, converse/examine Ricardo no olho mágico e confirme o acolhimento para vê-lo caminhar na sala. F3 mostra os pés do protagonista em ciano e os de Ricardo em laranja.

## Imagens de investigação

Todas as 12 variantes agora são cópias processadas de 900 × 460, com a mesma moldura/fundo escuro da interface (`#17232e`). As mãos recebem remoção do branco conectado às bordas. As demais imagens já tinham fundos escuros e mantêm o conteúdo original sobre o painel padronizado, evitando apagar olhos, veias, dentes, tremores, cabelo ou jaleco. O encaixe proporcional com vizinho mais próximo preserva a pixel art; não há alongamento de eixos.

Arquivos: `personagens/visitantes/ricardo/investigacao_processada/<atributo>/<variante>_v2_<hash>.png`. Os arquivos brutos de `investigacao/` permanecem intactos. O carregamento usa essas cópias, não as versões antigas com branco. Os exames continuam sendo apenas seleção visual por booleano; nenhuma inferência ou diagnóstico foi introduzido.

## Retrato e halo

O tratamento continua identificando o branco conectado às bordas, mas agora também corrige a mistura com branco nos pixels próximos à transparência. A cor e a cobertura alfa das bordas são reconstruídas a partir do interior próximo. Regiões claras internas do jaleco não participam da remoção. O recorte-base foi mantido para conservar proporção, altura de 490 pixels e âncora `(640, 625)` na rua.

O novo retrato e os sprites usam arquivos com versão `v2` em `processados/`, invalidando os recortes antigos sem apagá-los. Originais não foram alterados. As bordas foram conferidas na renderização sobre a rua; fios de cabelo e contornos finos continuam sujeitos a avaliação artística manual, pois as imagens originais contêm antialiasing e estilos diferentes.

## Posição, movimento e colisão

O ponto preferido do Ricardo acolhido passou para `(860, 575)`, nas coordenadas originais da sala, afastado do protagonista e das portas. Antes de criá-lo, o sistema verifica cenário, outros atores e distância das chegadas. Caso o ponto esteja ocupado, procura outro livre; se nenhum for encontrado, não conclui o acolhimento.

`Resident` alterna pausas de 2–4 segundos e passos de 0,7–1,4 segundo a 34 pixels de tela por segundo, dentro de um raio máximo de 72 pixels do ponto inicial. Direções e durações são escolhidas sem alterar os sintomas ou suprimentos. Ele usa os quatro sprites parados já existentes, voltando-se conforme a direção; não foram inventados quadros de caminhada. A sombra e a ordem de desenho por altura dos pés foram mantidas.

Os parâmetros ficam em `resident` no cadastro `dados/visitantes/ricardo.json`. Ricardo permanece exclusivamente na sala. Sua movimentação pausa durante menus, observação, fade, edição e enquanto o jogador está em outro cômodo.

`ActorCollisions` combina a colisão estática com retângulos dinâmicos dos pés de 20 × 10. A movimentação do protagonista usa os pés de Ricardo como obstáculo; os passos de Ricardo verificam os pés do protagonista. Os passos do NPC são subdivididos em até 3 pixels para evitar atravessar pessoas ou móveis em atualizações longas. Não há empurrões nem alteração dos arquivos de colisão do cenário.

O raio de circulação fica distante das portas e da passagem estreita entre mesa e sofá. Ao encontrar um obstáculo, Ricardo para e tenta outra direção após uma pausa. Ele não possui busca de caminhos, objetivos ou transições automáticas. Se o editor criar um obstáculo sobre ele, o NPC pausa em vez de forçar uma saída atravessando a colisão; corrija o retângulo ou reinicie a partida.

## Arquivos modificados

- Novo `casa/visitor_image_processing.py`: remoção do branco, descontaminação das bordas e painéis dos exames.
- Modificado `casa/visitor_assets.py`: carregamento dos processados versionados e das 12 cópias de investigação.
- Novo `casa/resident.py`: ponto livre, movimento do NPC e colisões dinâmicas.
- Modificado `casa/game.py`: criação do morador, atualização dos dois atores, direção do sprite e depuração.
- Modificado `dados/visitantes/ricardo.json`: posição inicial e parâmetros do NPC.
- Novo `tests/test_ricardo_correcoes.py`: nove testes adicionais.
- README, esta documentação e capturas em `docs/` atualizados.

Escalas dos cenários, sprites/movimento do protagonista, sombras, portas, editor, diálogos, sorteios, diagnóstico pendente e a reserva da lógica dos alunos foram preservados. `main.py`, `logica_infeccao.py` e os JSONs de colisão não precisaram ser modificados.

## Verificação e limites

Os 44 testes verificam os painéis das 12 variantes, ausência de branco nas margens das mãos, correção de uma borda sintética contaminada sem apagar branco interno, integridade dos originais, posição afastada e alternativa de spawn, movimento prolongado na sala, bloqueio de móveis, colisão nos dois sentidos e pausas dos menus, além das regressões anteriores. O teste isolado de movimentação e a compilação dos módulos também foram executados.

Renderizações conferidas: `ricardo_porta_corrigida.png`, `ricardo_maos_corrigidas.png`, `ricardo_exames_padronizados.png` e `ricardo_npc.png`. Os testes usam SDL dummy; a sensação da movimentação e os detalhes de recorte ainda devem ser avaliados na janela real. O NPC muda a pose de direção, mas desliza durante os passos porque não existem quadros de caminhada próprios. A sessão continua sem salvamento entre execuções. Nenhuma lógica de infecção foi implementada.
