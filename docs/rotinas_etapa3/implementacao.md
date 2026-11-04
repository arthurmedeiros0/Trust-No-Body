# Etapa 3 — Distribuição e rotinas da casa

Implementação sobre os arquivos locais atuais, preservando as Etapas 1 e 2. O [repositório indicado](https://github.com/arthurmedeiros0/Trust-No-Body) foi consultado como referência de estrutura, sem escrita remota.

## Arquivos desta etapa

Criados:

- `casa/resident_routines.py`: preferências dos sete personagens, limites de ocupação e pontos em coordenadas originais da arte.
- `casa/resident_manager.py`: validação dos espaços, acolhimento, distribuição diária, atualização dos moradores visíveis, remoção e linha de interação.
- `tests/test_rotinas_moradores.py`: 24 testes novos de distribuição, circulação, animação, interação, persistência e recuperação.
- `conferir_rotinas.py`: roteiro reproduzível de capturas e medição de atualização/desenho com sete moradores.
- Esta pasta: relatório, 17 capturas, `testes_completos.txt`, `validacao_visual_desempenho.json` e `preservacao.json`.

Modificados:

- `casa/game.py`: integração com o gerenciador; cômodo dinâmico no desenho, colisões e interação; criação e remoção dos atores; inscrição no início do dia.
- `casa/resident.py`: pontos opcionais de circulação, validação integral de trechos e pausa visual sem reiniciar os temporizadores. A física e as animações existentes continuam sendo utilizadas.
- `tests/test_dias_tv.py` e `tests/test_sobrevivencia.py`: mantêm a verificação da identidade e dos dados do visitante após dormir, permitindo a mudança diária da posição e exigindo um novo local válido.
- `tests/test_laura.py`: verifica caminhada e colisões no cômodo atual de cada morador, em vez de pressupor que os dois estão sempre na sala.
- `tests/test_investigacao_progressiva.py`: verifica que o morador retoma algum movimento durante o intervalo, sem exigir que termine longe da origem após poder caminhar e retornar.

Os arquivos já modificados/não rastreados das Etapas 1 e 2 foram mantidos. Não houve commits ou pushes.

## Distribuição e cômodos

A localização atual fica em `Resident.room` e `Resident.feet`, dentro do estado da casa. `resident_positions` mantém referências aos mesmos vetores de pés por compatibilidade. `ResidentManager.locations` fornece um mapa auxiliar interno, sem exibir a localização no diário.

Ao acolher, o gerenciador considera ocupação, preferência de rotina, posição do protagonista e pontos seguros. O novo morador é acrescentado sem reposicionar os anteriores. Os limites são:

| Ambiente | Máximo | Pontos centrais validados na geometria atual |
|---|---:|---:|
| Sala | 3 | 5 |
| Cozinha | 2 | 6 |
| Corredor | 2 | 4 |
| Entrada/hall interno | 2 | 5 |
| Banheiro | 1 | 2 |
| Quarto | 0 | Nenhum |

São limites superiores, não metas de ocupação. A primeira distribuição de demonstração com sete moradores usa quatro ambientes e deixa o banheiro vazio. Em outro dia, uma rotina pode utilizar o banheiro, sempre com apenas um morador.

O quarto e a cena externa do olho mágico não fazem parte das opções de distribuição. Um acolhido deixa de ser desenhado na porta pelo comportamento já existente dessa interface.

## Rotinas diárias

Cada personagem tem preferências próprias: Ricardo alterna prioritariamente sala/cozinha/entrada; Laura prioriza corredor/sala/cozinha; Gabriel utiliza entrada/cozinha/corredor; Helena tem pausas maiores; Daniel favorece distância de outros moradores; Marina tende a pontos próximos, conservando a separação mínima. Antônio anda a 60% da velocidade configurada e espera entre cinco e nove segundos, tornando seu movimento mais discreto.

O gerenciador utiliza um gerador aleatório próprio, separado da geração da condição real, dos sintomas e da agenda. Os atores também possuem geradores próprios para as pausas e passos.

As rotinas são revistas exclusivamente ao acolher alguém e no evento existente `day_start`. A distribuição diária gira preferências, considera os espaços ocupados e reutiliza os mesmos atores. Não há relógio adicional, troca autônoma contínua de cômodos ou alteração de rotina por F6.

Durante o sono normal, o protagonista está no quarto e a redistribuição ocorre sob a transição existente. Se um novo dia for avançado por ferramentas enquanto um cômodo de NPCs está visível, seus moradores permanecem no lugar e nenhum outro é transferido para esse cômodo naquele evento. A revisão é transacional: se não houver plano completo seguro, todos conservam os locais anteriores. Repetir o mesmo evento de dia não redistribui novamente.

Sair e voltar a um cômodo não sorteia posições nem reinicializa rotinas. Fora do cômodo atual, os moradores não consomem tempo de caminhada. Ao sair, apenas a apresentação da animação é pausada; posição, direção e plano são mantidos.

## Posições e segurança

Os pontos ficam em pixels das imagens originais, separados da configuração original dos visitantes. São convertidos com `Scene.point`, respeitando escala, deslocamento e câmera de cada ambiente.

A validação utiliza o piso, polígonos, obstáculos e a mesma hitbox dos pés do jogo. Uma verificação em grade de oito unidades confirma a conexão com o ponto de entrada do cômodo. Essa verificação é armazenada em cache por geometria; não serve como navegação por caminhos durante os quadros.

Os locais e pontos de circulação mantêm pelo menos 72 unidades de distância dos pontos de interação, spawns e chegadas das conexões. Isso inclui as portas do corredor, geladeira e olho mágico. Cama, televisão e diário físico ficam no quarto, onde nenhum morador é permitido.

Na distribuição, os moradores mantêm separação de pelo menos 96 unidades, ou 116 ao posicionar Daniel. A colocação também evita a proximidade do protagonista no cômodo atual. Os testes verificaram a acessibilidade de todas as portas e objetos de progressão com os sete moradores presentes.

Se os pontos centrais estiverem indisponíveis, a recuperação usa `free_spawn`, com busca determinística em torno dos locais revisados e as mesmas restrições. Se todos os ambientes estiverem sem espaço seguro, o acolhimento é recusado como operação: o visitante continua aguardando, não aparece em posição inválida e nenhum recurso é transferido.

## Circulação, colisões e animações

Os moradores gerenciados caminham entre o ponto central e pequenos pontos laterais previamente validados. Os deslocamentos são cardinais e curtos, derivados de deslocamentos de 30 pixels horizontais ou 24 verticais da arte, convertidos pela escala do cômodo.

Antes de iniciar um trecho, toda a linha é verificada. Durante o deslocamento, a atualização existente de `Resident` divide os passos em no máximo três unidades e usa `ActorCollisions`/`feet_rect`, incluindo móveis, protagonista e outros moradores. A circulação conserva ainda uma distância de 68 unidades dos demais NPCs e a reserva de 72 unidades das interações. Um destino bloqueado é descartado; o morador repousa e pode tentar novamente depois, sem ser forçado através do obstáculo.

São reutilizados os mesmos ciclos de caminhada, sprites parados, escala e âncora dos pés de `resident_render.py`. A caminhada só aparece quando há deslocamento; pausa, bloqueio e interação exibem repouso. A direção é preservada ao parar; sem destino seguro o personagem pode apenas se virar.

Chamadores antigos de `Resident` sem pontos opcionais continuam compatíveis. O sistema de animação/movimento do protagonista não foi editado.

## Interações e diário

Renderização, colisão e interação consultam o cômodo atual do ator, não `definition['room']`. O jogador pode se aproximar e pressionar E em qualquer ambiente permitido. A linha entre os pés do jogador e do morador precisa estar livre dos sólidos do cenário, impedindo conversas através de um móvel, mesmo se a distância for curta. Outros cômodos não fornecem interações.

Iniciar interação para o morador uma vez. Enquanto conversa, inspeção, diário, inventário ou transição capturam a entrada, não há avanço dos passos. A pausa visual não sorteia um novo plano ou temporizador a cada quadro. Ao fechar, o morador pode retomar a circulação.

Conversar, Investigar, Eliminar e Voltar permanecem disponíveis. Perguntas, respostas, exames, rascunhos, anotações e fichas continuam no estado original da sessão. J, ícone e objeto do quarto não foram alterados. O diário não recebeu indicação da localização exata dos moradores.

## Eliminação e sobrevivência

A eliminação continua passando pela função existente da sessão, com a mesma sanidade e consequências internas. Depois disso, o gerenciador interrompe o ator, remove sua representação e libera a posição. O eliminado não é atualizado, desenhado, selecionado nem considerado em novos planos. A limpeza também reconhece eliminações efetuadas diretamente no estado da sessão.

A ficha e o nome riscado permanecem no diário. Os cálculos de alimentação, água, exposição, infecção, vitória e derrota continuam dependendo do estado real dos visitantes e não dos cômodos.

## Testes e revisão visual

- **24 testes novos aprovados**: sete moradores em vários ambientes, exclusão do quarto/rua, conectividade, portas, limites, posições persistentes, dias reais, F6, perfis, passos seguros, animação e recuperação de bloqueio, comparação em 30/60/120 FPS, interação nos cinco cômodos, linha bloqueada por móvel, diário, remoção, acolhimento atômico e preservação de condições/recursos.
- A simulação de caminhada foi verificada nos cinco cômodos, e os planos diários foram validados até o dia 20, mantendo as mesmas instâncias dos atores.
- `python main.py --smoke-test`: **248 testes, 241 aprovados, quatro falhas e três erros**. Os sete casos pendentes são os mesmos já registrados nas etapas anteriores: testes com pontos/escala/hashes antigos da cozinha e APIs ausentes dos modos `padrao_3`/`PATTERN_CONDITIONS`. O teste de proximidade no ponto antigo da cozinha agora não encontra interação, em vez de selecionar o morador através de um obstáculo. As posições atuais e acessíveis da geladeira são verificadas pela nova suíte.
- O Modo Teste existente foi validado com Antônio saudável; seus recursos de escolha exclusiva de padrões, já ausentes antes desta etapa, não foram implementados nem alterados.
- As 17 capturas foram abertas para revisão visual: quantidades de um, três e sete moradores; ambientes interiores; quarto vazio; novo dia; conversa; diário; eliminado.
- `git diff --check` e auditoria por hash foram executados.

A medição reproduzível com sete moradores, resolução 1280 × 720 e SDL dummy utilizou 240 quadros medidos por cômodo após aquecimento:

| Ambiente | Média de atualização + desenho | Percentil 95 |
|---|---:|---:|
| Sala | 0,42 ms | 0,52 ms |
| Cozinha | 0,44 ms | 0,54 ms |
| Corredor | 0,38 ms | 0,46 ms |
| Entrada | 0,33 ms | 0,38 ms |
| Banheiro | 0,36 ms | 0,43 ms |

O FPS configurado permanece em 60. Não houve novo planejamento ou reconstrução da geometria durante os quadros medidos. Não há carregamento de imagens na atualização/desenho dos moradores. Os números não incluem apresentação em uma janela física nem garantem o desempenho de outro computador.

Reproduzir a revisão e medição: `python conferir_rotinas.py`. Detalhes e posições em coordenadas da arte constam em `validacao_visual_desempenho.json`.

## Capturas

1. `01_um_morador_sala.png`
2. `02_tres_moradores_sala.png`
3. `03_tres_moradores_corredor.png`
4. `04_sete_sala.png`
5. `05_sete_cozinha.png`
6. `06_sete_corredor.png`
7. `07_sete_entrada.png`
8. `08_sete_banheiro.png` — vazio na primeira distribuição.
9. `09_quarto_reservado.png`
10. `10_rotina_banheiro.png`
11. `11_novo_dia_sala.png`
12. `12_novo_dia_cozinha.png`
13. `13_novo_dia_corredor.png`
14. `14_novo_dia_entrada.png`
15. `15_conversa_no_comodo.png`
16. `16_diario_preservado.png`
17. `17_eliminado_preservado.png`

## Preservação e limites

A auditoria de `preservacao.json` confirmou **406 arquivos idênticos ao início da Etapa 3**, incluindo as artes, colisões originais, dados, diálogos, notícias, geração de condição/sintomas, regras da simulação, diário e interfaces das Etapas 1 e 2.

`logica_infeccao.py` permanece byte a byte intacto, com SHA-256 `32935779c677379966cf940b35ae7b61d09c1ca29bc4362f9da4c6993f253f0e`.

A mudança entre ambientes ocorre em revisões diárias seguras; não existe caminhada autônoma passando de porta em porta. Fora do cômodo atual, os temporizadores de circulação ficam pausados. Em um ambiente sem espaço seguro, ele pode permanecer vazio. Essas decisões mantêm a implementação simples e evitam teletransporte visível e navegação complexa.

As sete incompatibilidades anteriores de testes continuam pendentes. A revisão visual e de desempenho utilizou capturas SDL dummy; a fluidez dos controles em janela física ainda pode ser conferida manualmente. Não houve alteração de sprites, cenários, colisões, FPS, regras de sobrevivência ou lógica matemática.
