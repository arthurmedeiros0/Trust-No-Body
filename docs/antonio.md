# Antônio — Visitante 03

Implementado pelo cadastro automático de `dados/visitantes/antonio.json`, com
história e falas em `antonio_dialogos.json`. Não exige cadastro manual na agenda.
Os suprimentos usam os intervalos padrão do gerador, sem quantidades fixas.

`casa/visitors.py` reutiliza o sorteio de condição de Gabriel para Antônio.
Palidez e tremores também podem ocorrer quando saudável, assim como manchas e
dentes amarelados. A exposição familiar não determina infecção. Os estados são
gerados na criação da sessão ou no início do teste e permanecem estáveis.
Os exames usam os nomes reais dos nove arquivos existentes de investigação.
No modo normal, seu desbloqueio continua dependendo do jornal.

`casa/menu.py` habilita Aleatória, Saudável e Infectado para Antônio. Execute
`python main.py`, selecione TESTAR PERSONAGENS, Antônio, condição e INICIAR TESTE.
F1 permite reiniciar, selecionar outro personagem ou voltar ao menu principal.
O diagnóstico real aparece apenas na faixa do modo teste já existente.

A movimentação usa `Resident` e o carregador de animações existente: dois passos
por direção, repouso correspondente, espelhamento lateral e alinhamento dos pés
em 94 na superfície de 64 × 96. A velocidade é 32, igual à de Marina. Como os
demais moradores, permanece no cômodo de acolhimento; o sistema atual não faz
NPCs atravessarem portas autonomamente.

Aceitação, recusa, recursos, necessidades e companhia utilizam os mesmos caminhos
dos demais visitantes. Não há consequências específicas da infecção implementadas
no projeto; `logica_infeccao.py` permanece reservado aos alunos. Esta entrega não
inventa regras de diagnóstico ou contágio.

Arquivos criados: os dois JSONs, `tests/test_antonio.py` e este documento.
Arquivos alterados: `casa/visitors.py`, `casa/menu.py`, `casa/visitor_assets.py`
e `tests/test_laura.py`. O carregador permite espelhar os quadros finais por uma
opção ativada apenas em Antônio, preservando os pixels após a redução.
O teste de recusa de Laura foi isolado de chegadas futuras para continuar
verificando Laura após a adição de mais visitantes. Nenhuma imagem foi alterada.

Validação: testes de carregamento, agenda, condições, estabilidade dos exames,
diálogos, menu, imagens normais/alteradas, decisão, transferência única de recursos,
morador, movimento, colisões, repouso e desenho real em SDL dummy. A porta também
foi renderizada e conferida em captura. Não houve sessão manual interativa.

Os registros completos estão em `antonio_test_results.txt` e
`antonio_baseline_results.txt`. Cinco falhas antigas foram reproduzidas com Antônio
excluído do cadastro: duas expectativas sobre texto da geladeira, prioridade de
interação próxima à geladeira, escala esperada pelo teste do editor e hash de
`colisoes/cozinha.json`. Esses sistemas não foram alterados nesta entrega.
