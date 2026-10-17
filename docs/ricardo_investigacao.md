# Ricardo — primeiro visitante e investigação visual

## Como experimentar

Execute `python main.py` e siga corredor → sala → porta superior → Entrada → porta principal. Pressione E para olhar pelo olho mágico. Ricardo está aguardando no primeiro dia. Não foi criado um calendário completo ou sistema de chegada de outros visitantes.

Conversar mostra os dois relatos iniciais e quatro perguntas. As respostas ficam em arquivo separado e incluem o Hospital Municipal São Lucas, a saída naquela manhã, o contato durante atendimentos e os suprimentos reais do sorteio. Marina aparece apenas como uma ligação narrativa, sem personagem implementado.

Investigar abre seis opções. Cada exame mostra uma imagem proporcional e centralizada, com o cenário escurecido. A variante é escolhida diretamente pelo booleano daquele atributo; isso não representa uma conclusão sobre infecção. Características examinadas são marcadas com `[visto]`. Os botões funcionam com mouse; ESC retorna da imagem ao menu e do menu à vista da porta. Na raiz, ESC/Voltar fecha o olho mágico, preservando a posição do protagonista.

Após conversar ou examinar pelo menos uma característica, Aceitar/Rejeitar pede confirmação. Cancelar não altera o estado. Confirmar acolhimento muda o estado para `acolhido`, remove o retrato externo e posiciona o sprite parado de Ricardo na sala. Confirmar rejeição muda para `rejeitado`, registra a decisão e remove o retrato. Não é possível decidir novamente nem reaparecer ao reabrir a porta nesta mesma partida.

## Dados e randomização

`VisitorSession` é criada uma vez por `House`, no início da partida. Usa `random.getrandbits(1)` para cada um dos seis booleanos e `random.randint(0, 3)` para comida e água. Não existe seed exposta na interface. Reiniciar o aplicativo começa uma nova partida; não há save de sessões nesta etapa.

Campos: `manchas_maos`, `dentes_deteriorados`, `olhos_alterados`, `veias_escurecidas`, `palidez_anormal` e `tremores_involuntarios`. Valores ficam em `Visitor.symptoms`; quantidades em `food` e `water`; decisão em `state`; exames em `examined`; conversa em `talked`. As decisões são registradas em `VisitorSession.decisions`, com dia, visitante e escolha.

Nome, 42 anos, profissão de médico, personalidade, história e ligação com Marina estão em `dados/visitantes/ricardo.json`. O mesmo cadastro configura os caminhos reais dos arquivos, posição/altura do retrato e posição/direção do sprite acolhido.

## Limite acadêmico e integração dos alunos

**Não foi implementada nenhuma lógica proposicional de infecção.** Não há implicações tautológicas, diagnóstico automático, inferência com notícias ou combinações de sintomas. Aceitar/rejeitar é uma decisão do jogador, sem alterar o diagnóstico.

O arquivo raiz `logica_infeccao.py` contém somente comentários para o código de autoria do grupo. O campo `Visitor.diagnosis` permanece com `diagnostico_pendente`, independentemente dos sintomas, notícias ou decisão. O módulo ainda não é importado nem chamado para classificar ninguém.

Para a integração futura, o grupo poderá receber os dados de `Visitor.symptoms` e o armazenamento `VisitorSession.knowledge.published`, implementar seu próprio código no arquivo reservado e integrar o resultado ao campo de diagnóstico. A definição das expressões e de quando avaliá-las permanece com os alunos. O teste que verifica o arquivo somente com comentários deverá ser revisto quando essa integração for autorizada.

`JournalKnowledge.published` é apenas um dicionário para notícias já publicadas; não contém notícias prontas, regras, interpretação ou deduções. Não foram adicionados jornal completo, sobrevivência, sanidade ou eliminação.

## Imagens

As 17 imagens foram inspecionadas visualmente: retrato, quatro direções e 12 imagens individuais de investigação. Não há pares de condições na mesma imagem que precisem ser divididos. O cadastro usa os nomes reais como `ricardo_mao_anormal.png`, `ricardo_dente_amarelo.png` e `ricardo_tremendo.png`.

Retrato e sprites recebem cópias processadas em `personagens/visitantes/ricardo/processados/`. O processamento remove apenas o branco conectado às bordas, preservando regiões claras internas do jaleco, recorta o espaço vazio e usa vizinho mais próximo para redimensionar. O retrato tem altura visual de 490 pixels e fica centralizado na rua. Os sprites usam telas transparentes de 64 × 96 e linha dos pés compatível com o protagonista. Originais não são sobrescritos.

Os exames usam cópias em `investigacao_processada/`, em painéis escuros padronizados. O branco das mãos foi removido, mantendo as características e os originais. As versões normal/alterada não são rotuladas na interface; o jogador deve analisar a imagem. Os hashes dos originais estão em `dados/visitantes/ricardo_originais.sha256`. Cópias processadas incluem versão e hash no nome e são reutilizadas durante a execução.

## Ricardo dentro da sala

A posição preferida é `(860, 575)` na resolução original da sala, com sprite frontal. A colisão real do cenário verifica se esse ponto está livre, afastado de atores e portas. Se um ajuste no editor ocupá-lo, o sistema procura posições próximas em piso livre. Se não encontrar uma posição, a aceitação falha sem concluir a decisão. A interface informa que não foi possível concluir.

Ricardo agora alterna pausas e passos lentos numa área restrita da sala, com sombra e desenho em ordem vertical em relação ao protagonista. Há colisão mútua pelos pés, combinada com o cenário; os arquivos de colisão dos cômodos permanecem intactos. Sintomas e suprimentos não são consumidos nem ressorteados ao acolher. Detalhes atuais em [correções visuais e NPC](ricardo_correcoes_visuais_npc.md).

## Arquivos e expansão

Novos módulos:

- `casa/visitors.py`: cadastro, sessão, sorteio, estados, registro de decisões e notícias conhecidas.
- `casa/visitor_assets.py`: remoção de fundo, cópias processadas, carregamento e cache de imagens.
- `casa/visitor_dialogue.py`: respostas e substituição das quantidades de recursos.
- `casa/visitor_ui.py`: conversa, investigação, marcas de exame e confirmações.
- `logica_infeccao.py`: espaço reservado, somente comentários.
- `dados/visitantes/ricardo.json` e `ricardo_dialogos.json`: cadastro e textos.
- `tests/test_visitantes.py`: sete testes de dados, recursos, interface e decisões.

Modificados: `casa/game.py` para criar a sessão, tratar decisões e desenhar o acolhido; `casa/peephole.py` para integrar retrato e menus; um teste antigo de observação sem visitante; README e documentação. `main.py`, escalas, sprites do protagonista, sombras existentes, movimentos, portas e arquivos de colisão não foram alterados nesta etapa.

Para cadastrar outro visitante, crie um JSON com a mesma estrutura em `dados/visitantes/` e um `<id>_dialogos.json`, apontando para suas próprias imagens. Os módulos reutilizam cadastro, sorteio e interfaces. `House.present_visitor(id)` seleciona um visitante cadastrado para apresentação. Apenas Ricardo é apresentado automaticamente; programação de chegadas dos demais fica para outra etapa. Não duplique a interface nem crie regras de infecção nesse cadastro.

## Validação e pendências

Os 35 testes passaram: regressões da exploração/editor/transições, sorteios por partida, limites de suprimentos, estabilidade ao abrir menus, diagnóstico pendente, arquivo de lógica somente comentado, seis exames com imagens normais/alteradas, marcas de visto, diálogos e valores reais, hierarquia ESC, bloqueio de movimento, confirmações/cancelamento, aceitação única, rejeição sem reaparecimento, sprite em piso livre, ordem de desenho e integridade/transparência das imagens. Não há testes de dedução ou classificação por sintomas.

Capturas da primeira integração em `docs/`: `ricardo_porta.png`, `ricardo_dialogo.png`, `ricardo_exame.png` e `ricardo_sala.png`; capturas atuais estão listadas no relatório de correções. A janela real ainda precisa de avaliação manual de mouse, leitura, contornos do recorte e proporções. O retrato e os sprites fornecidos têm estilos/proporções diferentes; foram mantidos, sem regenerar arte. O NPC usa poses direcionais durante seus passos porque não há quadros de caminhada próprios. A partida não é salva entre execuções. O módulo lógico dos alunos continua inteiramente pendente.
