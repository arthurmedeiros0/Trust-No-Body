# Entrada da casa e olho mágico

## Execução e percurso

Execute `python main.py` ou `python main.py --dev` para habilitar também o editor F4. Vá do corredor à sala pela primeira porta; a porta inferior da sala continua voltando ao corredor. A porta superior da sala agora abre a Entrada com E e fade.

O personagem aparece na Entrada em `(768, 870)`, voltado de costas para a câmera, olhando para dentro. A passagem inferior, em `(768, 925)`, retorna à sala em `(826, 274)`, diante da porta superior, voltado para a sala. Essas são coordenadas da arte original. As colisões antigas da sala e dos demais ambientes foram preservadas.

A porta principal da Entrada está no alto, com ponto de interação em `(768, 402)`. Ela permanece fechada e não permite sair da casa. E abre a observação frontal da rua. ESC ou o botão Voltar inicia o fade de retorno à Entrada, sem alterar posição ou direção do protagonista. Na visão externa, WASD não move o jogador e o sprite/sombra não são desenhados. Observar mantém a visualização, sem investigação ou visitantes nesta etapa.

## Imagens e estrutura

```text
cenarios/
    entrada/
        entrada_dia.png       original preservado
        entrada_noite.png     original preservado
        dia.png               cópia idêntica da versão diurna
        noite.png             cópia idêntica da versão noturna
    olho_magico/
        Rua Deserta ao Entardecer.png   original diurno disponível
        Rua Suburbana Sob o Luar.png    original noturno
        dia.png                        cópia da imagem de entardecer
        noite.png                      cópia da imagem com luar
```

As quatro imagens foram analisadas visualmente. Todas têm 1536 × 1024. Não há uma versão da rua ao meio-dia: a imagem disponível de entardecer foi usada para o período dia, sem inventar ou editar um substituto. Nenhuma imagem original foi excluída, renomeada ou sobrescrita.

A Entrada usa escala 0,50: 768 × 512, centralizada na área existente, com posição-base `(256, 114)`. O protagonista segue em 64 × 96, com sua escala, sombra, velocidade e animação preservadas. O fundo externo é enquadrado proporcionalmente em uma área de 1240 × 570; fica com 855 × 570 e margens laterais. Não há distorção de lente, recorte circular ou efeitos sobre as características físicas.

F6 muda Entrada e rua de acordo com o mesmo período global, sem mudar posição, objetos ou colisões. F3 mostra piso, obstáculos, hitbox, sombra, interações, posição, escala e câmera na Entrada. O editor encontra a Entrada também por Tab.

## Colisões

`colisoes/entrada.json` inclui piso poligonal acompanhando a entrada inferior, planta esquerda, banco/sapateira superior, planta direita, aparador lateral, sapateira inferior, porta-guarda-chuvas e porta principal fechada. A área central/tapete permanece livre. Os valores estão na resolução original e recebem a mesma transformação da imagem. O JSON pode ser editado por F4 e salvo com Ctrl+S; os backups seguem o mecanismo existente.

## Organização e arquivos

- Novo `casa/peephole.py`: carregamento dos fundos, cena frontal, camada futura de visitantes e botões.
- Novo `colisoes/entrada.json`: obstáculos e limites da Entrada.
- Novas cópias `dia.png`/`noite.png` nas duas pastas de imagens.
- `casa/config.py`: Entrada, conexões da sala e configurações da cena externa.
- `casa/interactions.py`: parâmetros opcionais de chegada, orientação e texto do prompt.
- `casa/game.py`: transições entre cômodos, estado de observação, bloqueio de movimento e renderização independente.
- `main.py`: ESC fecha a observação antes de encerrar o aplicativo; edição e transições também capturam ESC.
- Novo `tests/test_entrada_olho_magico.py` e atualização dos testes que esperavam a porta superior reservada ou apenas cinco cômodos.
- README e capturas `entrada_dia.png`, `entrada_noite.png`, `entrada_debug.png`, `entrada_porta.png`, `olho_magico_dia.png` e `olho_magico_noite.png` em `docs/`.

## Camadas para visitantes futuros

A ordem é fundo → grupo vazio de visitantes → interface → textos/botões. `visitor_layer` não contém sprites nesta etapa. A posição-base e escala são configuráveis em `FUTURE_VISITOR_POSITION` e `FUTURE_VISITOR_SCALE`. O método `draw_visitors` permite uma futura entidade sobre a rua sem acoplar esse desenho à física dos cômodos. Não foram implementadas pessoas, infecção ou decisões sobre visitantes.

## Verificações e pendências

Os 25 testes passaram: entrada/retorno sala ↔ Entrada, retorno inferior sala ↔ corredor, posição/orientação de chegada, colisões e acesso às interações, porta principal fechada, editor da Entrada, persistência JSON, observação sem protagonista/movimento, Observar/Voltar com mouse, ESC, dia/noite, posição preservada, ordem das camadas e cópias idênticas aos originais. As regressões antigas continuam passando. Também foi executado o teste isolado de movimentação e a compilação dos módulos.

Renderizações de Entrada, porta e rua foram inspecionadas. Os testes usam SDL dummy; falta avaliar teclado, mouse e fluidez em janela real. Plantas, aparador e sapateiras podem precisar de pequenos ajustes de contorno no editor. A escala artística dos novos ambientes pode ser refinada após jogar, sem alterar o tamanho do protagonista. A versão diurna externa continua com iluminação de entardecer, conforme o arquivo disponível.
