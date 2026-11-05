# HUD superior e mudança de dia

Arquivos desta etapa:
- `casa/hud.py`: novo componente de apresentação.
- `casa/game.py`: substituição dos textos soltos pelo cabeçalho; linha de depuração abaixo dele.
- `casa/sleep.py`: nova cartela e fade do conteúdo.
- `tests/test_hud_transicao_visual.py`: testes de geometria, valores, diário, cache e duração.
- Esta documentação, capturas reais da renderização e log de validação.

A HUD utiliza a faixa existente de y=9 até y=53, acima do cenário (y=65).
Local/período e objetivo ficam à esquerda. Dia, sanidade, fome e sede ocupam
segmentos separados à direita. As colunas se distribuem pela largura disponível,
reservando 12 pixels antes do alvo real do diário. Fontes são ajustadas ao espaço.
O botão do diário mantém sua geometria e desenho existentes, agora alinhados aos
painéis. A tecla J e o clique seguem pelos mesmos manipuladores de eventos.

O cabeçalho lê os mesmos valores de `predicted_needs` utilizados anteriormente;
desenhar não consome suprimentos nem altera necessidades. `survival_hud()` foi
preservado para compatibilidade. Os objetivos conservam seus textos originais.

A mudança de dia apresenta cartela central, título destacado, subtítulo original,
linha divisória, cantos bege e textura estática discreta. Cores, componentes e
hierarquia usam `ui_theme`, também empregado pelo noticiário. A cartela é
renderizada uma vez por dia/resolução e reutilizada durante o fade.

Os tempos permanecem 0,45 s para escurecer + 1,6 s de cartela + 0,45 s para
retornar (2,5 s totais). O avanço continua no mesmo callback. O novo fade de
0,22/0,24 s do conteúdo ocorre dentro da espera original, sem prolongá-la.
Nenhuma alteração em `update()` ou nas regras de sono, alimentação e sanidade.

Validação: transição/callback único, cache, atualização de dia/sanidade/necessidades,
estoque refletido sem consumo antecipado, todos os cômodos de dia e noite,
geometria em 1024/1280/1600 pixels de largura, acesso ao diário por J e clique.
Também executadas as suítes existentes de dias/TV, cama/HUD e diário etapa 2.
Resultado final: **41 testes executados, 40 aprovados e 1 falha preexistente**.
Os três testes novos passaram. `git diff --check` sem erros de whitespace.
A falha conhecida de `test_fridge_opens_same_stock_only_inventory` permanece:
o teste usa uma posição que não encontra a geladeira no mapa atual. Já foi
reproduzida com os módulos originais na etapa anterior; não pertence a esta mudança.

Capturas conferidas em 1280 × 720: `hud_quarto.png`, `hud_cozinha_noite.png`,
`novo_dia.png`. Limitação: verificação automatizada com SDL dummy e capturas;
não foi realizada uma partida manual completa.

`logica_infeccao.py` intacto. SHA-256 antes/depois:
`32935779C677379966CF940B35AE7B61D09C1CA29BC4362F9DA4C6993F253F0E`.
Lógica do diário, noticiário, eventos, regras e arquivos de dados preservados.
Alterações locais da etapa anterior preservadas. Sem commits ou pushes.
