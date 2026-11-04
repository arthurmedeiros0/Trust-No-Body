# Terceiro padrão e conversas progressivas

Implementação feita diretamente nos arquivos locais, preservando as alterações anteriores. Sem commits ou pushes.

## Arquivos desta implementação

| Arquivo | Alteração |
| --- | --- |
| `casa/visitors.py` | Registro do padrão atribuído e padrões detectados, seleção de combinações coerentes e condições de teste dos três padrões |
| `casa/visitor_dialogue.py` | Progresso por visitante/contexto, duas perguntas pendentes e registro da pergunta/resposta escolhida |
| `casa/visitor_ui.py` | Apresentação, perguntas e resposta em etapas; painel inferior; retomada e paginação; retrato também na conversa com moradores |
| `casa/menu.py` | Seis condições de teste disponíveis para os sete visitantes |
| `dados/noticiarios.json` | Apenas título e parágrafos do boletim 17 foram substituídos pelo conteúdo solicitado |
| `tests/test_terceiro_padrao.py` (novo) | Seis testes da geração, diagnóstico, boletim, exposição, eliminação e Modo Teste |
| `tests/test_conversas_progressivas.py` (novo) | Seis testes da progressão completa, retomada, contextos, geometria e decisões |
| `tests/test_dialogos_paginados.py`, `tests/test_visitantes.py` | Adaptação ao fluxo com apresentação e resposta separadas, preservando as verificações de texto, retrato e decisões |
| `tests/test_infeccao_sobrevivencia.py` | Cenários genéricos de exposição começam no dia 17, quando os três padrões já foram publicados |
| `tests/test_dias_tv.py`, `tests/test_sobrevivencia.py` | Expectativas narrativas atualizadas para a notícia solicitada do dia 17 |
| `README.md`, `docs/dialogos_exposicao.md`, `docs/infeccao_sobrevivencia.md`, este relatório | Documentação atual e indicação de quais descrições anteriores são históricas |

## Três padrões sem duplicar implicações

`logica_infeccao.py` já continha a terceira condição quando a tarefa começou. O arquivo foi somente lido e importado; nenhuma expressão foi alterada ou copiada para outro módulo.

Na geração inicial, o jogo escolhe a condição real de saúde e, para um infectado, um identificador de padrão oficial. Enumera as combinações possíveis dos seis sintomas e mantém somente aquelas validadas pela função do grupo para a condição e o padrão escolhidos. Saudáveis não satisfazem nenhum dos três padrões completos.

`Visitor.infection_pattern` registra o boletim do padrão atribuído. `infection_patterns` registra todos os padrões efetivamente comprovados pela função matemática com os sintomas reais, permitindo reconhecer eventuais combinações de padrões. Esses campos são internos e não aparecem no Modo Normal. Condição e sintomas permanecem estáveis durante a partida; somente o início de um teste escolhido pode redefini-los.

Os pesos dos sinais benignos de Gabriel e Antônio continuam sendo usados entre combinações válidas. Os intervalos de suprimentos e a configuração do calendário não foram alterados. Todos os sete cadastros possuem os seis exames, inclusive Marina.

## Noticiário, diagnóstico e exposição

O boletim mantém `id=boletim_17`, `day=17` e a lista de investigações já existente. Seu título é **URGENTE — Cientistas identificam terceiro padrão de infecção**, com os três parágrafos fornecidos no pedido. Nenhum outro boletim foi modificado. Continua disponível na data correta e pode ser assistido pelo histórico depois.

O diagnóstico do jogador continua usando somente observações registradas e notícias assistidas. Um infectado exclusivamente pelo terceiro padrão permanece inconclusivo sem o boletim 17, mesmo que o jogador tenha observado todos os sintomas e assistido aos anteriores. Sintomas desconhecidos permanecem omitidos; não viram ausências.

A exposição usa a consulta interna já existente: sintomas reais completos e boletins publicados até o dia encerrado. A integração passa a reconhecer o terceiro padrão automaticamente pela função atualizada do grupo.

| Padrão exclusivo | Primeiro encerramento com exposição | Segundo encerramento consecutivo, com derrota |
| --- | --- | --- |
| Primeiro | Dia 7 | Dia 8 |
| Segundo | Dia 14 | Dia 15 |
| Terceiro | Dia 17 | Dia 18 |

Quem apresenta mais de um padrão usa o primeiro marco aplicável. A publicação ativa a regra do mundo, independentemente de leitura. Não há contagem retroativa ou duplicada. Saudáveis não expõem. Eliminar todos os infectados relevantes interrompe a sequência no próximo encerramento, sem alterar fome, sede, solidão, recursos ou penalidades de sanidade.

## Modo Teste

Execute `python main.py`, escolha **TESTAR PERSONAGENS — MODO TESTE**, selecione qualquer visitante e altere **CONDIÇÃO** por clique ou setas:

1. Aleatória.
2. Saudável.
3. Infectado.
4. Infectado — padrão 1.
5. Infectado — padrão 2.
6. Infectado — padrão 3.

As três opções de padrão geram casos exclusivos, permitindo testar cada marco separadamente. As opções anteriores continuam disponíveis, incluindo Gabriel e Antônio. Todos os exames e os boletins do protocolo ficam disponíveis para a consulta lógica no contexto do teste, sem antecipar conhecimento na partida normal. Ainda é preciso examinar as características para obter o diagnóstico investigativo.

## Conversas em etapas

A interface usa os JSON existentes, sem alterar perguntas, respostas, personalidades ou referências entre visitantes:

1. **Apresentação:** mostra a fala inicial com nome e retrato. Continuar termina as páginas e abre as perguntas.
2. **Perguntas:** mostra as duas primeiras perguntas ainda não realizadas, na ordem original. Não há uma lista de respostas simultânea.
3. **Resposta:** mostra nome, pergunta escolhida e resposta. Continuar percorre as páginas restantes e retorna às opções.

A pergunta selecionada é registrada como realizada. A não selecionada permanece disponível junto da próxima pendente. Por exemplo: escolher a segunda de `[0, 1]` resulta em `[0, 2]`; depois escolher a primeira resulta em `[2, 3]`. Todos os diálogos podem ser explorados sem reiniciar a conversa. Sem perguntas pendentes, aparece uma indicação discreta de conclusão; a conversa continua aberta até o jogador sair.

O progresso é armazenado no próprio visitante, em `conversations`, com contextos independentes `door` e `resident`. O registro preserva perguntas realizadas, etapa atual, pergunta selecionada, resposta apresentada e página. Fechar e reabrir a interação, inclusive criando outra instância de interface, retoma o estado. Uma nova partida cria novos registros. O jogo não possui gravação de partida em disco.

Respostas dinâmicas continuam sendo calculadas por `Dialogue.answer()` no momento da escolha, usando suprimentos e estados conhecidos da sessão. Ao interromper a leitura, a resposta apresentada é conservada para retomar o mesmo texto. Dentro da casa são usados `resident_intro` e `resident_questions`; o progresso da porta não consome perguntas de morador.

**Voltar/ESC** permite sair em qualquer etapa. As decisões não exigem completar as perguntas. Conversar já permite voltar e aceitar/rejeitar, com as confirmações e consequências existentes. Investigação física e eliminação de moradores continuam funcionando.

## Apresentação e legibilidade

O painel de conversa ocupa a região inferior, a partir de y=405, preservando o rosto e o tronco do retrato. Nome, pergunta escolhida, resposta, navegação e ações têm áreas próprias. O retrato mantém imagem, proporção, tamanho e ancoragem originais; nas conversas com moradores, a mesma imagem aparece sobre a cena escurecida.

A renderização conserva a fonte legível, mede a largura das linhas e limita os pixels à caixa de texto. Respostas e apresentações longas têm páginas, indicador e navegação por mouse, setas ou Page Up/Page Down. Continuar não pula o restante do texto: percorre as páginas antes de retornar às perguntas. O texto aparece imediatamente, sem animação obrigatória ou espera artificial.

Foram inspecionadas capturas Pygame das perguntas em pares, resposta, próxima dupla, apresentação de morador e seleção do terceiro padrão no menu, em SDL sem janela visível.

## Testes e pendências

`python main.py --smoke-test`: **190 testes executados, 185 aprovados, cinco falhas preexistentes e nenhum erro**. Os 12 testes novos passaram. Uma execução isolada das suítes anteriores de paginação, diagnóstico, infecção e visitantes também passou: 32 testes.

A nova cobertura verifica:

- Geração consistente dos três padrões e saudáveis nos sete visitantes, em 50 sementes, sem revelar a condição pelo diagnóstico inicial.
- Diagnóstico do terceiro padrão somente após observação e leitura do boletim 17; disponibilização e histórico da notícia.
- Ausência de exposição até encerrar o dia 16, primeira exposição no 17, derrota no 18, idempotência e interrupção por eliminação.
- Seleção de cada padrão exclusivo para todos os visitantes no Modo Teste.
- Todas as perguntas originais acessíveis por escolhas alternadas em pares, nos sete visitantes e nos dois contextos, sem modificar os JSON.
- Perguntas não escolhidas preservadas, resposta separada, conclusão, retomada inclusive de página e isolamento entre contextos, visitantes e partidas.
- Respostas dinâmicas de suprimentos, aceitação/rejeição antes de esgotar perguntas, investigação, geometria e preservação do retrato.

Os testes antigos foram adaptados ao novo fluxo, à notícia solicitada e ao novo marco máximo de exposição. Nenhuma verificação foi desativada para esconder falhas.

As cinco pendências anteriores continuam registradas: interação com geladeira em duas suítes, prioridade entre morador e geladeira, escala divergente do backup e hash histórico de `colisoes/cozinha.json`. Nenhum cenário ou colisão foi alterado para fazê-las passar.

## Arquivo reservado preservado

SHA-256 de `logica_infeccao.py` antes e depois desta tarefa:

`F021C9FCA5D1219C0012ED81380AFAEAE6704D35D89EA6D4FD1D91634A9D2361`

O arquivo já estava modificado pelo usuário em relação ao Git ao iniciar esta tarefa; essa alteração foi preservada integralmente. Também não houve modificação de imagens, sprites, cenários, colisões, histórias, configuração de chegada, intervalos de suprimentos ou regras de sanidade.
