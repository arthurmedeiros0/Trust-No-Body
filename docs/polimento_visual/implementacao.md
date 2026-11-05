# Polimento visual

Arquivos de jogo modificados: casa/menu.py, casa/peephole.py,
casa/visitor_presentation.py, casa/game.py e main.py.
Novo componente: casa/message_ui.py.
Testes: test_polimento_visual.py (novo), test_antonio.py,
test_entrada_olho_magico.py e test_terceiro_padrao.py (atualizados).

Menu: logo/logo.png original, proporcao preservada, escala nearest-neighbor,
fundo preto integrado, botoes Jogar/Sair com teclado, mouse, hover e clique.
Removidos os caminhos de selecao, configuracao e inicializacao de teste em main.
VisitorSession.start_test permanece como ferramenta interna compartilhada.

Mensagens: painel compartilhado para narrativa, informacao, destaque, resumo e
confirmacao. Quebra de linha preserva paragrafos. Corpo entre 26 e 260 pixels;
altura total entre 158 e 392 pixels. Excesso de conteudo recebe paginacao.
Setas/PageUp/PageDown navegam; Enter/Espaco avancam e fecham na ultima pagina.
ESC fecha. Confirmacao preserva S/Enter para dormir e N/ESC para cancelar.

Conversas: nome e metadados em linhas separadas, retrato reservado a esquerda,
conteudo medido antes do desenho, respostas com ate 156 pixels e paginacao,
perguntas com altura calculada e intervalos de 16 pixels. Cabecalho, corpo e
rodape com areas distintas. Inspecoes, perguntas progressivas, decisoes e diario
preservados. Rua vazia mostra somente Voltar; ESC tambem retorna.

Validacao: 45 testes direcionados aprovados. Suite completa: 250 testes,
243 aprovados, 4 falhas e 3 erros. Os mesmos sete problemas foram reproduzidos
com os modulos originais do Git carregados em memoria, sem alterar os arquivos:
- Dois testes de geladeira usam posicoes/expectativas antigas.
- Um teste nao encontra a interacao da geladeira na posicao esperada.
- Editor espera escala 0.9, mas a configuracao existente usa 0.44.
- Hash historico de colisoes/cozinha.json diverge do arquivo existente.
- Depuracao padrao_3 nao esta disponivel em VisitorSession.start_test.
- test_terceiro_padrao nao importa PATTERN_CONDITIONS de casa.visitors.
Esses sistemas nao foram alterados nesta tarefa.

Renderizacoes reais em SDL dummy conferidas: menu.png, mensagem.png,
conversa.png. Nenhuma nova arte foi criada; capturas documentam a interface.
Limitacao: verificacao automatizada e visual estatica, sem partida manual completa.

logica_infeccao.py intacto, SHA256 antes/depois:
32935779C677379966CF940B35AE7B61D09C1CA29BC4362F9DA4C6993F253F0E
Logo original, dados, textos narrativos, sprites, cenarios e regras preservados.
Sem commits ou pushes.
