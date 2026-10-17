# Relatório: escala, banheiro, sala e sombra

## Arquivos modificados

- `casa/config.py`: escalas por cenário, sombra configurável, banheiro e navegação/obstáculos da sala.
- `casa/shadow.py` (novo): elipse transparente com bordas mais leves.
- `casa/player.py`: desenho da sombra antes do sprite, com a mesma câmera.
- `casa/game.py`: contorno da sombra no F3.
- `teste_movimentacao.py`: mesma sombra no teste isolado.
- `tests/test_correcoes.py`: expectativa atualizada para uma única saída da sala.
- `tests/test_pes_sombra_sala.py` (novo): cinco testes adicionais.
- `README.md`, coordenadas, escalas e capturas em `docs/`: documentação atualizada.

## Escalas e proporção

A janela continua em 1280 × 720. O jogador permanece em 64 × 96, com 88 pixels de altura visual, sem variação entre cômodos. A velocidade continua em 220 pixels/s. Os novos fatores são corredor 0,90, quarto 0,88, cozinha 0,90, banheiro 0,92 e sala 0,68. Foram reduzidos em relação à etapa anterior para aproximar a altura do protagonista das portas, cadeiras e armários; a cama e o sofá continuam mais extensos, como na arte original.

Os fatores usam referência visual dos objetos, não apenas largura do arquivo. A mesma transformação proporcional é aplicada a imagem, obstáculos e pontos interativos. Cenários menores ficam centralizados, e o corredor mantém câmera horizontal. O suporte existente à câmera vertical foi preservado. As perspectivas das imagens diferem, portanto os fatores continuam sujeitos a avaliação artística manual.

## Hitbox e banheiro

A hitbox já era de pés e foi preservada: 20 × 10 pixels, centralizada, com a base na posição do jogador. Não depende da imagem/quadros de animação. F3 a mostra em ciano.

No banheiro, a região transitável passa a acompanhar o recuo da entrada inferior por um polígono. Pia/armário, vaso, lixeira, box, planta/estante, prateleiras e cestos têm retângulos separados na configuração. Os espaços livres deixam de ser bloqueados por uma faixa única. Os limites inferiores bloqueiam paredes e áreas pretas, preservando o acesso à porta. As mesmas colisões valem de dia e à noite. As demais colisões já funcionais foram preservadas, com ajuste automático de escala.

## Sala e passagem

As versões oficiais de dia/noite continuam sendo as duas imagens corrigidas. Ao vir do corredor, o jogador aparece em `(343, 636)`, em piso livre diante da porta inferior; E em proximidade de `(343, 663)` retorna ao corredor. A porta superior não tem interação nem transição; sua coordenada fica apenas reservada na configuração.

Sofá, mesa de centro, poltrona e mesinha usam as bases dos móveis no chão em vez de toda a altura desenhada. Isso libera o trajeto entre sofá e mesa: foi testada a travessia horizontal nos dois sentidos, em y=450 da arte original. O personagem pode se sobrepor visualmente às partes elevadas dos móveis, como ocorre com uma colisão de pés; não foi implementada uma camada de oclusão da arte estática. As capturas `sala_passagem.png` e `sala_debug.png` ajudam a avaliar esse limite visual.

## Sombra

A sombra é uma elipse preta em superfície RGBA, com anéis externos de alfa menor. Valores padrão: 34 × 12, opacidade máxima 65/255, deslocamento vertical +2. Todos são configuráveis em `casa/config.py`. A superfície é criada uma vez por jogador e desenhada antes do sprite. Ela acompanha os pés menos o deslocamento da câmera, mantém o tamanho nos cinco ambientes e aparece tanto de dia quanto à noite. Não altera hitbox, física ou animação. F3 mostra seu contorno em lilás.

## Testes e verificações

Executados os quinze testes da exploração e o teste isolado de movimentação. Além das regressões anteriores, verificam hitbox independente dos quadros, movimento contra cada categoria de obstáculo do banheiro, limites/porta inferior, entrada e retorno da sala, porta superior sem transição, travessia entre sofá e mesa, alfa/posição/tamanho da sombra, ordem de desenho e funcionamento com câmera.

O teste de integridade confirma que as imagens dos cenários e do protagonista não foram alteradas. Foram geradas capturas dos cinco ambientes de dia, noite e depuração; renderizações de sala, passagem, banheiro e quarto foram inspecionadas. Não havia novas capturas do usuário junto do texto anexado.

## Pendências manuais

- Jogar na janela real para avaliar teclado, fluidez, tamanho aparente dos objetos e legibilidade da sombra sobre pisos claros/escuros; os testes usam SDL dummy.
- Conferir a sobreposição visual ao atravessar atrás do sofá: colisão de pés não adiciona profundidade/oclusão à imagem única.
- Refinar contornos arredondados dos móveis se necessário. Não foram alterados sprites ou imagens para simular novas proporções.
- Os passos laterais originais continuam semelhantes; o ciclo com poses paradas foi preservado.
