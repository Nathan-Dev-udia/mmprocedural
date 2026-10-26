# Fichas traduzidas

Versões em português de fichas da DC, conferidas uma a uma com a página do livro (`referencias/dc/`). Quando existe um
arquivo aqui, a tela e os dois PDFs usam a tradução no lugar do texto extraído em inglês.

Ficam fora de `dc/` porque `python ferramentas/extrair_fichas_dc.py` regenera e sobrescreve aquela pasta inteira; o
caminho repete o id da ficha (`traducoes/dc/volume1/batman.json` traduz `dc/volume1/batman`).

Formato:

- `nome_pt`, `conferida_em` e `pagina_do_livro` (a numeração impressa, não a página do PDF);
- `ficha.habilidades` com as siglas do projeto (For, Vig, Agi, Des, Lut, Int, Pro, Pre);
- `ficha.poderes` e `ficha.equipamento` como linhas de texto. Uma linha que começa com `• ` faz parte do poder anterior
  (efeito alternativo de um arranjo ou componente de um dispositivo); `•• ` é um nível abaixo;
- `ficha.pericias` com `nome` (igual a `rules.PERICIAS`, com especialização depois de `:`), `graduacoes` e `total`;
- `ficha.ataques` com `nome`, `bonus` (ou `null`), `alcance`, `dano` (número ou texto) e `observacao` opcional;
- `ficha.defesas`, `observacao_defesas`, `ficha.custos`, `ficha.total` e `ficha.complicacoes` (`titulo` e `texto`);
- `notas`: o que a conferência achou (erros da extração, contas do livro que não fecham) e quadros úteis do livro.

Os números são os impressos no livro, mesmo quando a conta não fecha; a diferença fica registrada em `notas`. Os nomes
de efeitos, modificadores e vantagens seguem a tradução brasileira do M&M 3e (os mesmos termos de `dados/comum`).
