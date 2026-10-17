# Cama, privação e HUD

**Contagem atual:** a HUD usa a [previsão do dia atual](previsao_privacao.md), separada do histórico. Sem ração, sede causa derrota ao encerrar o dia 3 e fome ao encerrar o dia 4; atingir o limite visual durante a exploração permite continuar jogando até o sono.

**Atualização de balanceamento:** o dia 1 é de tolerância, sem consumo ou privação. Sanidade e solidão contam desde o início. Sede 2/2 e fome 3/3 permitem sobreviver: somente o próximo encerramento sem a respectiva ração causa derrota. Sem água, isso acontece ao encerrar o dia 4; sem comida e com água suficiente, ao encerrar o dia 5. Veja [as regras atuais](tolerancia_dia1.md). As descrições de datas abaixo registram a etapa anterior.

A cama agora usa uma área de interação retangular em coordenadas da arte: `(232, 125, 131, 215)`, abrangendo da cabeceira aos pés. O alcance continua em 58 pixels do mundo, calculado pela menor distância entre a hitbox dos pés e esse retângulo. As demais interações continuam usando seus pontos anteriores.

É possível usar E pelas duas laterais e pelos pés. A cabeceira está acima do piso acessível; não foi criado acesso através das paredes ou móveis. Colisões, escala e movimentação não foram alteradas. F3 desenha a região da cama em amarelo; a colisão continua separada, em vermelho. O retângulo recebe a mesma transformação de escala e câmera que o cenário.

## Contagem de sobrevivência

O problema de morte na primeira noite **não foi reproduzido no código disponível**. A inicialização já atribui zero aos contadores; `Survival.close_day` armazena o resultado por dia, e `DayCycle` encerra o dia antes de avançar, sem repetir consumo ao acordar. Não foi identificada evidência de uma causa que justificasse alterar essas regras. Foram adicionados testes de regressão pelo fluxo real de cama e confirmação, além dos testes unitários existentes.

Resultados verificados:

- Sem água: encerrar o dia 1 registra sede 1/2 e permite explorar o dia 2 inteiro. A derrota ocorre somente ao encerrar o dia 2 novamente sem água, mantendo o calendário no dia 2.
- Receber e consumir 0,5 água no encerramento do dia 2 zera a sede e permite acordar no dia 3.
- Sem comida, mas com água suficiente: a derrota ocorre somente ao encerrar o terceiro dia consecutivo sem alimentação.
- Receber uma ração zera seu contador correspondente. Repetir a confirmação não encerra outro dia. Recursos nunca ficam negativos.

Não foram acrescentadas penalidades ao acordar ou à fome narrativa. Cada pessoa viva continua consumindo 0,5 de cada recurso por dia; solidão e sanidade mantêm as regras anteriores.

## Interfaces

A faixa superior, fora do viewport dos cenários, apresenta permanentemente durante a exploração:

`Dia 2/20 | Sanidade: 8/8 | Fome: 1/3 dias | Sede: 1/2 dias`

O texto consulta o estado real a cada desenho. Fome e sede representam dias de privação, e não o estoque. A linha de objetivos ou depuração F3 permanece abaixo, sem sobreposição; os cenários mantêm suas dimensões. Interfaces que ocupam a tela podem ocultar a HUD.

**I** abre SUPRIMENTOS DA CASA, mostrando somente comida e água armazenadas; I ou ESC fecha. A geladeira abre essa mesma interface após a primeira mensagem narrativa de estoque vazio. Se já houver recursos na primeira consulta, abre diretamente o inventário. Consultar não altera o estoque. Nada foi acrescentado ao sistema de obtenção de recursos.

## Arquivos e testes

Alterados: `casa/config.py` (região da cama), `casa/interactions.py` (distância entre retângulos), `casa/scenes.py` (transformação e desenho F3), `casa/game.py` (HUD e geladeira), `casa/survival_ui.py` (inventário simplificado), `tests/test_editor_colisoes.py` e `tests/test_ricardo_individual.py` (expectativas históricas dos arquivos de interação), `README.md` e `docs/sobrevivencia.md`.

Criados: `tests/test_cama_hud.py`, `conferir_cama_hud.py`, este relatório e três capturas. Os sete testes novos verificam bordas acessíveis, distância e colisão, desenho com câmera, dia 2 jogável, recuperação de hidratação, fome no dia 3, confirmação repetida, HUD em todos os cômodos e inventário compartilhado com a geladeira.

Validação: `python main.py --smoke-test` passou os **103 testes**, incluindo os sete novos; `python conferir_cama_hud.py` gerou as capturas. Elas usam SDL dummy e foram inspecionadas visualmente, sem sessão manual completa:

- [Cama e F3](cama_interacao_f3.png)
- [HUD no dia 2, após uma noite sem água](hud_dia2.png)
- [Inventário simplificado](suprimentos_simplificado.png)

A lógica de infecção permanece reservada aos alunos. A limitação de balanceamento com apenas Ricardo continua: não há suprimentos suficientes para os 20 dias e não foi criado reabastecimento artificial.
