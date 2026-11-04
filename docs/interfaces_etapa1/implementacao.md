# Etapa 1 — Interfaces e experiência visual

Referência: `5ef3c90f4965cd92f080e72e37ad2efd4401e5d2`. Implementação local em Pygame, sem novas dependências.

## Arquivos

Modificados:

- `casa/visitor_ui.py`: delegação da geometria e desenho; feedback breve de clique, preservando o fluxo de perguntas, exames e decisões.
- `casa/television.py`: moldura de televisão, transmissão e arquivo, navegação e paginação do corpo dos boletins.
- `casa/peephole.py`: componentes visuais compartilhados nos controles do olho mágico vazio.

Criados:

- `casa/ui_theme.py`: paleta, fontes em cache, painéis semitransparentes, botões, estados visuais, quebra de linha, recorte e paginação.
- `casa/face_portraits.py`: seleção da imagem facial normal, recortes individuais e fallback.
- `casa/visitor_presentation.py`: layouts e renderização das ações, conversas, inspeção e confirmações.
- `tests/test_interfaces_etapa1.py`: nove testes novos que percorrem os sete visitantes e os vinte boletins.
- `conferir_interfaces.py`: geração reproduzível das quinze capturas desta pasta.
- Este relatório, `testes_completos.txt`, `testes_direcionados.txt` e as quinze imagens abaixo.

## Conversas e retratos

A conversa ocupa um painel inferior semitransparente com nome em destaque, idade/profissão discretas, rosto à esquerda e fala à direita. As perguntas possuem indicador de escolha, alinhamento à esquerda e até duas opções por vez. O personagem da porta continua visível; moradores conservam a apresentação do personagem sobre o cenário durante a conversa. Os sprites e suas posições na simulação permanecem iguais.

Os rostos vêm exclusivamente do caminho `investigation.palidez_anormal.normal` de cada definição. Nenhum retrato é escolhido pela condição real ou pelos sintomas sorteados. Foram revisadas as sete imagens originais, incluindo a imagem larga da Laura e o enquadramento vertical da Helena. As proporções de recorte estão em `FACE_CROPS` e são aplicadas em memória, sem gravar novas imagens na pasta dos personagens. A redução conserva a proporção; um busto neutro e a inicial do nome servem de fallback quando faltar a imagem.

O fluxo de perguntas, seus textos, respostas dinâmicas e progresso por contexto não foram reescritos. Falas longas usam as mesmas ações Continuar, Anterior e Próxima, com indicador de página; Enter/Espaço e as setas/Page Up/Page Down continuam disponíveis. O conteúdo é limitado à região da fala e não invade os controles. Não foi adicionado efeito de digitação.

## Televisão

A TV tem moldura, cantos de tela, seletores, saída de som, luz de funcionamento e textura discreta de transmissão desenhados com Pygame. A textura fica sob os textos e não pisca. Cabeçalho, dia da transmissão, manchete e corpo possuem áreas distintas. A altura do corpo se adapta ao número de linhas da manchete.

O arquivo mantém oito transmissões por página, com dia, manchete integral em até duas linhas e situação de leitura em coluna própria. As transmissões futuras continuam indisponíveis. Abrir o arquivo não marca nada como assistido; escolher um boletim chama o mesmo `NewsArchive.watch` existente. O retorno de um boletim antigo leva ao arquivo, que permite retornar ao início e abrir a transmissão atual.

O corpo das notícias agora tem paginação por botões, esquerda/direita, Page Up/Page Down e roda do mouse. Controles sem página anterior/seguinte ficam desabilitados. ESC retorna à tela anterior e desliga a TV a partir do início. Todos os vinte textos oficiais foram verificados quanto à preservação integral na paginação; o JSON não mudou.

## Inspeção e decisões

A seleção de exames usa uma lista de evidências com nome do visitante, indicadores PENDENTE/OBSERVADO e altura proporcional à quantidade de exames conhecidos. O indicador informa somente se o exame foi feito. A visualização tem moldura de inspeção, imagem centralizada com escala proporcional, nome do exame e retorno separado. Não há diagnóstico automático nem preenchimento do diário.

Conversar/Investigar ficam à esquerda; Aceitar/Rejeitar ficam à direita, antes de Voltar. Eliminar ocupa o grupo de decisões, afastado das ações comuns, em vermelho-escuro com hover próprio. Sua confirmação usa painel compacto com detalhe vermelho, aviso de irreversibilidade, Confirmar eliminação e Cancelar neutro. Não informa condição clínica nem antecipa o valor da penalidade de sanidade.

A legenda de movimento do cenário é ocultada sob essas interfaces para não aparecer através da região dos botões. Isso é feito no desenho da interface, sem alterar `game.py` ou controles da simulação.

## Testes e revisão visual

- Nove testes novos aprovados: rostos normais/fallback, perguntas para os sete visitantes nos dois contextos, geometria, imagens proporcionais, registros de exames, decisões, confirmação, vinte boletins integrais, histórico, desbloqueios, paginação longa, hover/pressionado/desabilitado e recorte de texto.
- 59 testes direcionados aprovados, cobrindo também as suítes anteriores de paginação, conversas, TV, diário e diagnóstico/sobrevivência. A seleção exclui explicitamente apenas o teste já incompatível com o modo `padrao_3`; ele foi executado e reportado na suíte completa.
- Suíte completa: `python main.py --smoke-test` — **204 testes, 197 aprovados, cinco falhas e dois erros preexistentes**. Os mesmos sete casos constam no relatório anterior do commit de referência, em `../diario/testes_completos.txt`.
- As falhas anteriores envolvem pontos/escala da cozinha, comparação com backup/hash antigo de colisões, importação de `PATTERN_CONDITIONS` ausente e o modo de teste `padrao_3` não implementado. Não foram alteradas regras ou dados para contornar essas incompatibilidades.
- As capturas foram abertas e inspecionadas visualmente em 1280 × 720. Após a revisão, foram ajustados espaçamento da confirmação, alinhamento do arquivo, altura do corpo da notícia e ocultação da legenda inferior. Os testes direcionados foram repetidos após esses ajustes.

Reproduzir capturas: `python conferir_interfaces.py`. O script usa uma sessão de demonstração própria e SDL dummy; não altera os dados originais da partida.

## Capturas

1. `01_acoes_porta.png`
2. `02_conversa_apresentacao.png`
3. `03_perguntas.png`
4. `04_resposta.png`
5. `05_inspecao.png`
6. `06_exame.png`
7. `07_confirmar_acolhimento.png`
8. `08_conversa_morador.png`
9. `09_acoes_morador.png`
10. `10_eliminacao.png`
11. `11_tv_inicio.png`
12. `12_tv_atual.png`
13. `13_tv_arquivo.png`
14. `14_tv_antiga.png`
15. `15_retratos_normais.png`

## Preservação e pendências

Foi verificada a ausência de diferenças em relação ao commit de referência para `logica_infeccao.py`, os dados, diálogos, notícias, cenários, colisões, personagens, diário, geração de condição, sobrevivência, conhecimento médico, agenda, residentes, jogador, configuração e controlador da casa.

`logica_infeccao.py` permanece intacto. Não houve commits ou pushes. As Etapas 2 e 3 não foram implementadas.

As sete incompatibilidades anteriores de testes continuam pendentes. A revisão visual usou capturas SDL dummy; uma conferência final da sensação dos controles em janela física ainda é recomendada. O layout desta etapa é destinado à resolução atual de 1280 × 720.
