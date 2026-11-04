# Etapa 2 — Diário de Investigação

Implementação local sobre o commit `5ef3c90f4965cd92f080e72e37ad2efd4401e5d2` e sobre as melhorias locais da Etapa 1, preservadas nesta tarefa.

## 1. Arquivos criados e modificados nesta etapa

Modificados:

- `casa/diario.py`: separação entre fichas e rascunhos, promoção ao acolher, dias de acolhimento/eliminação e histórico factual dos exames.
- `casa/diario_ui.py`: novo fichário, marcas manuais, navegação, notícias, cronologia, retratos compartilhados, editor e botão de acesso rápido.
- `casa/game.py`: acesso modal por J/ícone/objeto, prioridade de eventos e desenho sobre a interface anterior.
- `casa/visitor_ui.py`: acrescentada apenas a chamada ao registro factual do exame após a observação existente; mantidas as melhorias locais da Etapa 1.
- `main.py`: a faixa do modo de teste deixa espaço para o ícone e fica oculta durante o diário. Nenhuma regra desse modo foi alterada.
- `tests/test_diario.py`: atualizada a suíte anterior para fichas após acolhimento e seleção explícita das marcações/conclusões.

Criados:

- `casa/diario_paper.py`: identidade de papel, fichário, abas, separadores e nomes riscados.
- `casa/diario_editor.py`: layout Unicode do texto e navegação do cursor pelas linhas visuais.
- `tests/test_diario_etapa2.py`: vinte testes novos de dados, progressão, contexto modal, editor e layout.
- `conferir_diario_etapa2.py`: roteiro reproduzível de capturas em uma sessão de demonstração.
- Esta pasta: relatório, dezesseis capturas, registros das duas execuções de testes e `preservacao.json`, com hashes dos arquivos protegidos antes da implementação.

Os arquivos novos/modificados da Etapa 1 que já estavam presentes no início foram preservados; não devem ser confundidos com alterações novas desta etapa no status do Git.

## 2. Visual e navegação

O diário agora tem duas páginas, lombada com argolas, papel envelhecido com textura discreta, margem avermelhada, pautas, canto dobrado e fotografias presas por fita. Os nomes e títulos têm maior destaque; textos corridos usam fonte legível e limites de desenho definidos.

As quatro abas permanecem fixas na parte superior: Personagens, Noticiários, Anotações e Linha do Tempo. A aba atual possui marca de tinta. A coluna esquerda mostra as fichas permanentes e, quando aberto a partir de uma visita pendente, uma área separada de rascunho. O conteúdo principal tem rolagem e indicador lateral. As posições de leitura são guardadas por seção e personagem.

Os controles parcialmente visíveis continuam desenhados com recorte; apenas a parte visível aceita cliques. A geometria é reconstruída no evento de clique, evitando áreas antigas depois de rolar ou trocar de aba. A lista comporta os sete visitantes em 1280 × 720.

## 3. Fichas permanentes e rascunhos

`InvestigationJournal.cases` contém somente pessoas já acolhidas, inclusive eliminadas. `drafts` utiliza o mesmo tipo `Case`, exclusivamente para visitantes pendentes; não existe um segundo sistema de investigação.

`meet()` registra o encontro e cria apenas o rascunho de quem ainda aguarda. `conversation()` acrescenta a pergunta e a resposta já resolvida a esse mesmo registro. Ao acolher, `decision()` transfere o próprio objeto de `drafts` para `cases`, preservando sintomas manuais, conclusão, texto, respostas e histórico de exames. O dia original da visita é mantido e o dia do acolhimento é registrado separadamente.

Ao rejeitar, o rascunho é descartado e nenhuma ficha permanente é criada. O encontro e a rejeição continuam na cronologia. Reabrir o diário enquanto a visita está pendente recupera o mesmo rascunho. Durante exploração, a lista não mostra rascunhos de pessoas aguardando em outro contexto.

## 4. Sintomas progressivos e marcações

Os campos visíveis consultam diretamente `session.medical.known`. Não há contador paralelo nem desbloqueio por data:

- Boletim 4: mãos e dentes.
- Boletim 7: olhos, além da recapitulação anterior.
- Boletim 10: veias e palidez, além das características anteriores.
- Boletim 14: tremores, além das características anteriores.
- Boletim 17: terceiro padrão; não existe uma sétima característica. O conhecimento segue as recapitulações já fornecidas pelo sistema existente.

Somente assistir ao boletim, inclusive pelo histórico, alimenta o conhecimento existente. Avançar os dias ou apenas abrir o arquivo não libera campos. Antes das primeiras notícias, a página explica que nenhuma característica física foi divulgada.

Cada campo conhecido tem três opções explícitas: Não verificado, Presente e Ausente. Os indicadores usam a mesma tinta azul, sem sugerir que Presente significa infecção. A conclusão também possui três escolhas manuais. Não há correção de hipóteses nem comparação com padrões.

## 5. Histórico de exames

Após um exame bem-sucedido na interface existente, `journal.examination(visitor, feature, day)` registra o primeiro dia em `Case.examined_days`. A chamada não recebe o resultado do exame.

O diário usa esse registro e `visitor.examined` para mostrar Disponível / ainda não examinado ou Exame realizado / dia. Campos ainda desconhecidos ficam ocultos. Registros anteriores sem data ainda podem mostrar Exame realizado. Reexaminar não apaga a primeira data.

Um exame nunca altera `Case.marks`: Não verificado permanece até o jogador selecionar uma marcação.

## 6. Retratos e eliminados

A ficha reutiliza `face_portraits.draw` da Etapa 1, com a imagem de palidez normal e seus recortes individuais em memória. Não utiliza corpo inteiro reduzido, variante alterada ou condição clínica para escolher a imagem. A escala mantém as proporções e o fallback da Etapa 1 continua disponível.

Eliminar mantém o mesmo registro, grava `eliminated_day`, risca o nome tanto na lista quanto na ficha e aplica aparência mais apagada à identificação e fotografia. Anotações, marcações e conversas permanecem consultáveis e editáveis. Nenhuma condição clínica é revelada. As consequências de sanidade continuam exclusivamente no sistema anterior.

## 7. J, ícone e preservação do contexto

`House.open_journal()` reaproveita a única instância de `JournalUI`. Funciona na exploração de todos os cômodos e nas telas de visitantes/moradores, inclusive respostas paginadas, seleção de exames, imagem do exame e confirmação pendente.

O diário é desenhado por último, inclusive no caminho de retorno antecipado do olho mágico. A interface anterior permanece instanciada e conserva pergunta, resposta, página, seleção de exame e decisão. ESC, Voltar ou J fora do editor fecha somente o diário. Os eventos do diário retornam antes de chegar à interface anterior; a simulação e o movimento ficam bloqueados enquanto ele está aberto.

No campo de anotações, J não fecha a interface: seu texto chega por TEXTINPUT, preservando caracteres como j/J e acentos. Sair do editor interrompe sua entrada de texto. As demais interfaces atuais não possuem campos de texto a restaurar.

O ícone de caderno fica em `(1198, 9, 56, 44)`, fora da área da HUD. Tem dica Diário [J] e chama o mesmo método do atalho. O acesso pelo objeto do quarto continua usando a posição e o sistema de proximidade anteriores. A legenda inferior também informa J.

O acesso fica desabilitado durante vitória, derrota, fades, sono, editor de colisões, TV e suprimentos; esses dois últimos contextos não faziam parte dos acessos exigidos. Não há alteração do menu inicial.

## 8. Notícias e cronologia

Noticiários mostra recortes organizados pelo dia do boletim, filtrando somente `read=True`, com manchete e parágrafos originais completos. Os padrões dos boletins 7, 14 e 17 recebem destaque em tinta, somente após sua leitura. O diário não compara padrões com pessoas.

A Linha do Tempo organiza os eventos conhecidos por dia, preservando a ordem dos acontecimentos no mesmo dia. Cada evento tem marcador, indicação de dia e descrição. Notícias antigas registram quando foram assistidas e identificam seu dia de publicação. Nenhuma agenda futura ou condição oculta é consultada.

## 9. Editor e persistência

Cada ficha/rascunho possui texto próprio. O editor tem borda, cursor, pautas, suporte a Unicode, quebra em espaços e também em palavras compridas. Aceita Backspace, Delete, Enter, esquerda/direita, cima/baixo e Home/End. Cliques reposicionam o cursor. A navegação vertical considera linhas visuais e mantém a coluna desejada quando possível.

A rolagem acompanha o cursor; trocar de pessoa/seção e reabrir recupera texto e posição de edição. As informações persistem durante a sessão, inclusive após avançar dias. Uma nova `VisitorSession` cria fichas, rascunhos, cronologia e notícias registrados vazios. Não foi adicionado salvamento em disco.

## 10. Testes e pendências

- Os **20 testes novos da Etapa 2** passaram, cobrindo os requisitos funcionais, de contexto e de layout.
- A suíte anterior do diário, com **10 testes atualizados**, passou.
- A execução direcionada reúne **79 testes aprovados**, incluindo regressões da Etapa 1, diálogos paginados, TV, diário, diagnóstico e sobrevivência. Ela exclui apenas o teste conhecido que exige o modo `padrao_3` ausente; esse teste foi executado na suíte completa.
- `python main.py --smoke-test`: **224 testes, 217 aprovados, cinco falhas e dois erros preexistentes**. Os sete casos são os mesmos registrados em `../interfaces_etapa1/testes_completos.txt`: incompatibilidades de testes com a cozinha/colisões atuais e APIs ausentes dos modos de teste dos padrões.
- `testes_completos.txt` e `testes_direcionados.txt` contêm as execuções. `git diff --check` também foi executado.
- Dezesseis capturas foram geradas e abertas para revisão visual em 1280 × 720, incluindo a ficha vazia, progressão, editor longo, eliminado, lista com sete fichas e retorno à conversa/imagem.

A conferência por hash confirmou a preservação dos 398 arquivos listados em `preservacao.json`. Isso inclui as artes, dados oficiais, notícias, diálogos, regras da simulação e componentes compartilhados da Etapa 1. `logica_infeccao.py` permanece byte a byte idêntico, com SHA-256 `32935779c677379966cf940b35ae7b61d09c1ca29bc4362f9da4c6993f253f0e`.

As sete incompatibilidades anteriores continuam pendentes. A revisão usou SDL dummy e capturas; a sensação dos controles em janela física ainda pode ser conferida manualmente. Não foram implementadas rotinas, distribuição ou movimentação entre cômodos da Etapa 3. Não houve commits ou pushes.

## 11. Capturas

Reproduzir: `python conferir_diario_etapa2.py`.

1. `01_diario_vazio.png`
2. `02_rascunho_sem_sintomas.png`
3. `03_dois_sintomas.png`
4. `04_rascunho_conversa.png`
5. `05_conversa_restaurada.png`
6. `06_exame_sem_preenchimento.png`
7. `07_imagem_restaurada.png`
8. `08_ficha_acolhido.png`
9. `09_editor.png`
10. `10_editor_longo.png`
11. `11_recortes.png`
12. `12_terceiro_padrao.png`
13. `13_linha_do_tempo.png`
14. `14_eliminado.png`
15. `15_acesso_rapido.png`
16. `16_sete_fichas.png`
