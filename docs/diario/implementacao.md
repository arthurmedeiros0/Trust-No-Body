# Diário de investigação

Implementação em Pygame, sem dependências novas e com persistência apenas na sessão atual.

## Arquivos

Criados: `casa/diario.py`, `casa/diario_ui.py`, `tests/test_diario.py`, este relatório e cinco capturas em `docs/diario/`.

Modificados: `casa/config.py`, `casa/game.py`, `casa/visitors.py`, `casa/visitor_dialogue.py`, `casa/visitor_ui.py`, `tests/test_diagnostico.py`, `tests/test_infeccao_sobrevivencia.py`, `tests/test_editor_colisoes.py`.

## Acesso e controles

O objeto fica sobre a mesinha inferior esquerda do quarto, ao lado do cabideiro. A interação `journal` usa o ponto **(160, 390) da arte original 747 × 561**, convertido por `Scene.point` com a escala .88 e o deslocamento do cenário. A câmera usa as transformações existentes. A aproximação é verificada por `nearest` e pelo raio existente de 58 unidades; um ponto livre validado próximo é (200, 425) na arte. Não houve mudanças nos móveis, imagens, polígonos nem obstáculos.

Perto do objeto aparece `[E] Consultar diário de investigação`. E abre durante dia e noite; ESC ou Voltar fecha. O diário captura os eventos e interrompe o movimento e outras interfaces enquanto está aberto.

As abas Personagens, Noticiários, Anotações e Linha do Tempo funcionam com mouse. A coluna esquerda seleciona os visitantes encontrados. A roda do mouse rola o conteúdo da página. Somente controles completamente visíveis aceitam cliques. Há recorte de desenho para textos extensos e indicação de rolagem.

## Registros independentes

`VisitorSession.journal` armazena um `Case` por visitante encontrado: identidade pública, dia efetivo de chegada, situação conhecida, seis marcações, conclusão, texto e conversas. Os registros não contêm condição real nem cópias dos sintomas reais.

Cada sintoma começa como Não verificado. Clicar alterna Presente, Ausente e Não verificado. A conclusão alterna Ainda não sei, Suspeito que esteja infectado e Acredito que esteja saudável. Não há validação, correção nem comparação com os padrões. Exames continuam alimentando exclusivamente o estado interno de observação anterior.

Em Anotações, selecione uma ficha e clique na página. A entrada usa TEXTINPUT para preservar acentos; permite inserir em qualquer posição, mover o cursor com esquerda/direita e Home/End, apagar com Backspace/Delete e inserir linhas com Enter. Clicar no texto reposiciona o cursor. Textos longos quebram dentro da página e têm rolagem. Fechar, reabrir ou avançar dias preserva tudo. Criar outra sessão/reiniciar cria outro diário vazio.

## Notícias, conversas e cronologia

Noticiários consulta `NewsArchive.bulletins`, filtrando apenas `read=True`. O texto oficial permanece intacto. Os resumos dos padrões usam os identificadores oficiais boletim_07, boletim_14 e boletim_17 e aparecem somente após assistir ao boletim, inclusive no histórico. Nenhuma comparação é realizada com as fichas.

`Dialogue.ask` registra a pergunta e a resposta já resolvida naquele momento, depois de validar que a pergunta está disponível. Isso preserva respostas dinâmicas e o contexto original sem expor perguntas futuras. Foi acrescentado o campo `Visitor.conversations`, que já era utilizado pelo diálogo, mas faltava na definição do visitante.

A linha do tempo recebe chegadas, acolhimento, rejeição, eliminação e primeiras visualizações de notícias, incluindo novas características investigáveis e padrões divulgados. Um boletim antigo registra o dia em que foi assistido e informa seu dia original. Reassistir não duplica os eventos. Não são consultados a agenda futura ou o diagnóstico.

## Diagnóstico e preservação

A faixa de diagnóstico foi removida de `VisitorUI.draw`; `diagnosis_indicator` retorna None e não chama o classificador. O método foi mantido como interface compatível. As verificações internas em `VisitorSession`, a exposição, a sobrevivência, os recursos e a sanidade continuam com os cálculos anteriores. Diálogos, notícias, calendário, sprites e cenários não foram editados.

`logica_infeccao.py` não foi modificado. Não foram feitos commits nem pushes.

## Validação

Os 10 testes em `tests/test_diario.py` passaram: alcance e acesso pelo quarto, dia/noite, ESC, captura de movimento/inventário, fichas encontradas e seleção, ciclo e alteração das seis marcações, independência dos exames, manutenção de conclusão errada para infectado, boletins assistidos e os três padrões, respostas realizadas, edição Unicode com rolagem, persistência e reinício, decisões, cronologia e desenho de todas as abas para os sete visitantes.

Os testes anteriores de diagnóstico foram atualizados para esperar ausência de revelação e nenhuma chamada ao classificador pela interface. O teste histórico de interações ignora apenas a nova interação do diário ao comparar os móveis antigos. Capturas em 1280 × 720 foram inspecionadas: `secao_0.png` a `secao_3.png` e `ficha_rolagem.png`.

A suíte completa foi executada com `python main.py --smoke-test`: 195 testes, 188 aprovados, cinco falhas e dois erros preexistentes. Consulte `testes_completos.txt` e `comparacao_anterior.txt` nesta pasta.

## Pendências anteriores ao diário

A suíte contém testes incompatíveis com o estado atual da cozinha (escala/pontos antigos, comparação com backup e hash histórico de colisões), e testes de padrões que esperam `PATTERN_CONDITIONS` e a escolha de padrões exclusivos no modo de teste, APIs ausentes na versão original de `visitors.py`. Essas falhas foram reproduzidas com os módulos do HEAD executados em memória, adicionando apenas a inicialização de `conversations` para ultrapassar o bloqueio anterior do diálogo. Os dados de cenário e os algoritmos não foram alterados para atender a essas expectativas antigas.

A revisão visual foi realizada com SDL dummy e capturas; a sensação dos controles em janela física ainda merece uma conferência manual. Não há salvamento em disco, conforme o escopo solicitado.
