# Laura: segunda visitante jogável

Laura, 24 anos, estudante universitária, está integrada ao cadastro e gerenciador existentes. Ricardo continua chegando no dia 1 após o noticiário; Laura chega uma única vez, no dia 2 ou 3 sorteado no início da partida. Nenhum sistema paralelo de visitantes foi criado.

## Uso e estados

Inicie com `python main.py`, assista à TV e resolva Ricardo. Ao dormir, avance até o dia planejado de Laura. Acesse a porta principal pela Entrada e pressione E. O olho mágico apresenta o retrato, nome, idade, profissão, conversa, seis exames e decisões de Laura.

Aceitá-la adiciona de **1 a 2 latas** e de **1 a 2 garrafas**, sorteadas uma vez, ao estoque compartilhado. Ela passa a morar na sala, movimentando-se com seus próprios sprites. A transferência acontece uma vez; não existe expulsão. Rejeitá-la não altera recursos ou moradores, e ela não retorna. Ricardo pode permanecer na casa simultaneamente, sem compartilhar estado de animação, sintomas ou sprite com Laura.

Sua história permanece a mesma com qualquer sorteio: separou-se da família durante uma evacuação, não consegue retornar ao bairro bloqueado e procura um local seguro. Os quatro tópicos de conversa são solidão, retorno para casa, suprimentos reais e notícias sobre a doença. Antes da confirmação aparecem as falas sobre precisar de um lugar seguro e não querer causar problemas. Não há diagnóstico ou informação lógica de infecção.

## Imagens preservadas e processamento

As **21 fontes fornecidas já possuem alpha transparente**, apesar de parecerem ter fundo preto em alguns visualizadores. `preparar_laura.py` preserva esses valores RGBA, sem remover cores, aplicar erosão, reconstruir pixels ou usar IA. Os hashes dos originais são registrados e verificados em `dados/animacoes/laura.json`.

Os resultados ficam exclusivamente em `personagens/visitantes/laura/processados/`. Nenhuma imagem original foi renomeada, excluída ou sobrescrita. Foram gerados:

- Quatro sprites parados e oito de caminhada: canvas **64 × 96**, recorte do espaço transparente, escala proporcional NEAREST e apoio dos pés em **y=94**.
- Retrato com recorte transparente, exibido com altura 465 na porta, abaixo dos 490 de Ricardo.
- Onze painéis de investigação em 900 × 460, com fundo escuro, proporção preservada e escala NEAREST. Há somente um painel derivado de `rosto_normal.png`.
- Comparação dos sprites em `processados/comparacao.png`.

A altura visível é normalizada para aproximadamente 86 pixels em todas as poses. Cada imagem é redimensionada proporcionalmente, sem esticar os eixos. Laura fica aproximadamente da altura do protagonista e abaixo de Ricardo, que mantém o aumento visual de 8%. `visual_scale` no cadastro de Laura permite ajustar somente sua escala final; pés, sombra e hitbox continuam ancorados na posição lógica.

Como os originais já estavam transparentes, a solução conserva os contornos fornecidos em vez de tentar limpá-los agressivamente. As prévias em fundos claros e escuros foram conferidas; não foi observada uma moldura preta ou branca residual. Não há correção artística das diferenças de desenho entre as poses originais.

## Animações

Frente, costas e direita usam os três parados e seis passos fornecidos. Esquerda espelha os parados e passos da direita, sem criar desenhos novos. Para Laura, o ciclo é:

`passo 1 → parado → passo 2 → parado`

O intervalo permanece configurado em 180 ms por quadro, usando o sistema de tempo do NPC. Ao parar ou colidir, a pose parada da direção substitui imediatamente a caminhada. A opção `walk_step_first` ativa essa ordem somente para cadastros que a solicitam; o ciclo anterior de Ricardo continua igual.

## Associação dos exames

| Característica | Normal | Alterada |
|---|---|---|
| Manchas nas mãos | `mao_sem_mancha.png` | `mao_mancha.png` |
| Dentes | `dente_branco.png` | `dente_amarelo.png` |
| Olhos | `rosto_normal.png` | `olho_vermelho.png` |
| Veias no pescoço | `pescoco_normal.png` | `pescoco_veia_roxa.png` |
| Palidez | `rosto_normal.png` | `rosto_palido.png` |
| Tremores | `mao_normal.png` | `mao_tremendo.png` |

Olhos normais e palidez normal compartilham tanto o mesmo arquivo derivado quanto a mesma Surface carregada. Os sintomas são seis booleanos independentes: olhos alterados não definem palidez, manchas não definem tremores e história não define infecção. Seus valores permanecem ao dormir, conversar, investigar, trocar de cômodo ou aceitar.

## Arquivos

Criados nesta etapa:

- `dados/visitantes/laura.json`: identidade, caminhos, investigação, suprimentos, escala e parâmetros do NPC.
- `dados/visitantes/laura_dialogos.json`: apresentação, quatro perguntas e falas antes da decisão.
- `dados/animacoes/laura.json`: quadros ativos, recortes, escalas, pés e hashes das fontes/derivados.
- `preparar_laura.py`: processamento reproduzível com Pillow.
- `personagens/visitantes/laura/processados/`: assets ativos derivados, separados das fontes.
- `tests/test_laura.py`: nove testes da integração real.
- `conferir_laura.py`, este relatório e capturas `docs/laura_*`.

Modificados:

- `casa/visitor_assets.py`: carregamento direto de assets já preparados, compartilhamento dos painéis por caminho e comparação em pasta configurável.
- `casa/animation.py`: opção de iniciar o ciclo no passo, mantendo o padrão anterior.
- `casa/resident_render.py` e `casa/game.py`: escala visual opcional por cadastro, com ancoragem nos pés.
- `casa/visitor_ui.py`: falas opcionais antes da confirmação; Ricardo não possui esse campo e mantém sua tela anterior.
- `tests/support.py`, testes de cama/sobrevivência/visitantes/agendamento: isolamento explícito dos cenários históricos com somente Ricardo e expectativas de sorteio para dois visitantes. Os testes de Laura usam a agenda real, sem suprimir sua chegada.
- `conferir_sobrevivencia.py` e `conferir_dias_tv.py`: resolvem a nova visitante em seus roteiros de captura.
- README e relatório de agendamento: cadastro atual e instruções.

O algoritmo do gerenciador, o sistema de movimentação dos moradores, as colisões dos cenários, os sprites do protagonista/Ricardo, suas animações, notícias, sono e regras de sobrevivência não foram reescritos.

## Testes e capturas

**124 testes passaram** com `python main.py --smoke-test`, incluindo nove novos de Laura. Verificam arquivos originais e derivados por hash, pixels NEAREST reconstruídos a partir do recorte original, pés/altura/espelhamento, animações em diferentes FPS e parada imediata, todos os pares de investigação, compartilhamento do rosto normal, chegada variável em 2/3, diálogos, aceitação/rejeição sem duplicação, três moradores consumindo 1,5 de cada recurso e dois NPCs em movimento respeitando móveis, protagonista e um ao outro.

`python conferir_laura.py` executou o fluxo real de TV, chegada pelo sono, porta e acolhimento e gerou:

- [Laura na porta](laura_porta.png)
- [Conversa](laura_dialogo.png)
- [Seis pares de investigação](laura_exames.png)
- [Quadros em fundos claros e escuros](laura_ciclos.png)
- [Protagonista, Ricardo e Laura na sala](laura_moradores.png)
- [Prévia animada dos moradores](laura_moradores.gif)

As capturas foram inspecionadas visualmente. A validação usa SDL dummy e não equivale a uma sessão manual completa. Para regenerar os derivados e prévias:

```powershell
python preparar_laura.py
python conferir_laura.py
```

## Git e pendências

Estão novos e precisam ser adicionados ao repositório: `personagens/visitantes/laura/` **inteiro**, incluindo os 21 originais e derivados; os três JSONs de Laura; `preparar_laura.py`; `conferir_laura.py`; `tests/test_laura.py`; `docs/laura.md` e as imagens/GIF `docs/laura_*`. Os arquivos de código/testes/documentação modificados listados acima também precisam integrar a revisão. Nenhum commit ou push foi realizado. Arquivos `__pycache__` gerados pela execução não são assets ou código-fonte a adicionar.

Os demais visitantes continuam pendentes. Ricardo e Laura não bastam para garantir uma campanha de 20 dias; não foi criado reabastecimento artificial. Persistência da partida em disco e a lógica acadêmica de infecção permanecem fora desta etapa. Os contornos e o nível de detalhe originais foram preservados; a qualidade ampliada do retrato é limitada pela imagem fornecida de 198 × 264.
