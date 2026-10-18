# Notícias perdidas, histórico e aprendizado tardio

Referência analisada: commit `f50c388`, incluindo televisão, calendário, visitantes, conhecimento médico e testes. A correção modifica apenas a seleção do histórico, o fluxo de leitura e a indicação visual; `dados/noticiarios.json` não foi alterado.

## Causa e correção

Havia duas falhas complementares:

1. `NewsArchive.history` exigia `read=True`, excluindo notícias publicadas mas ainda não assistidas.
2. `Television.choose('news:...')` abria o conteúdo sem chamar `NewsArchive.watch`, impedindo os efeitos da primeira leitura pelo histórico.

Agora `available` indica publicação: o dia do boletim já chegou. `read` indica que o jogador abriu seu conteúdo, pela transmissão atual ou pelo histórico. Publicar não marca leitura, não ensina sintomas e não dispara callbacks de primeira leitura.

`NewsArchive.history` lista os boletins disponíveis com dia menor que o dia atual, em ordem decrescente. No dia 5 são os dias 4, 3, 2 e 1; o dia 5 fica em Noticiário atual. No dia 20 são 19 boletins anteriores, distribuídos em páginas de até oito, sem incluir a transmissão atual ou qualquer notícia futura.

Cada linha mostra `[NÃO ASSISTIDA]` em tom quente ou `[ASSISTIDA]` em tom neutro. O status permanece legível mesmo quando uma manchete precisa ser abreviada. Os controles por mouse, setas, Enter/Espaço e ESC, assim como o retorno do conteúdo à mesma página da lista, continuam funcionando.

## Recuperar uma notícia

Abra a TV com E, escolha Notícias anteriores e selecione o boletim desejado. A seleção aceita somente identificadores presentes no histórico publicado. Antes de mostrar o conteúdo, chama `NewsArchive.watch`, o mesmo método usado por Noticiário atual.

Exemplo validado: após dormir até o dia 5 sem assistir ao boletim do dia 4, mãos e dentes continuam bloqueados. O boletim aparece como não assistido. Abri-lo marca a leitura, ensina os dois exames e deixa o aviso de descoberta pendente até fechar a TV. Os exames ficam disponíveis tanto na porta quanto nos moradores Ricardo e Laura.

O dia original da publicação permanece 4; o calendário continua no dia 5. Não é necessário voltar ao passado nem mudar os sintomas reais. Reabrir o mesmo boletim não repete callbacks, aviso, sorteios ou chegada de visitantes. A introdução e a chegada de Ricardo após a primeira transmissão do dia 1 permanecem iguais.

As recapitulações posteriores continuam sendo outra forma de aprender: assistir diretamente ao dia 7 ensina mãos, dentes e olhos mesmo sem leitura anterior do dia 4. Nenhuma regra de conhecimento, sobrevivência ou infecção foi acrescentada.

## Arquivos e validação

Modificados: `casa/news.py`, `casa/television.py`, `tests/test_dias_tv.py`, `tests/test_investigacao_progressiva.py`, `README.md`, `docs/dias_sono_tv.md` e `docs/investigacao_progressiva.md`.

Criados: este relatório, `conferir_historico_tv.py` e quatro capturas `docs/historico_*.png`.

O teste antigo que exigia histórico somente de assistidos foi substituído. A paginação no dia 20 agora espera 19 boletins anteriores. Foram acrescentados testes integrados de notícia perdida no dia 5, aprendizado tardio para visitantes/moradores, status da lista, callbacks únicos, releitura do primeiro boletim sem nova chegada, bloqueio de notícias futuras/atuais pelo histórico, recapitulação e paginação incluindo notícias nunca assistidas.

**137 testes passaram** com `python main.py --smoke-test`. Também executado com sucesso: `python conferir_historico_tv.py`. Este roteiro avança pelo sono real e usa estoque extra exclusivamente na ferramenta de teste para isolar a verificação da TV; a partida normal não recebe recursos extras.

- [Boletim perdido listado como não assistido](historico_nao_assistidas.png)
- [Conteúdo antigo aberto no dia 5](historico_boletim_antigo.png)
- [Status atualizado após leitura](historico_assistida.png)
- [Aviso de aprendizado após fechar a TV](historico_descoberta_tardia.png)

As capturas foram inspecionadas em SDL dummy, sem sessão manual completa. Sprites, animações, colisões, visitantes, sono, sobrevivência, textos dos boletins e lógica reservada ao grupo permanecem preservados. Nenhum commit ou push foi realizado.
