# DC Adventures — fichas em JSON

Os arquivos em `volume1/` e `volume2/` foram extraídos dos livros
`DC Adventures: Heroes and Villains, Vol. I` e `Vol. II` (os PDFs ficam em `referencias/dc/`, fora do git). Os dois livros usam
Mutants & Masterminds 3ª edição; portanto, estas fichas preservam os dados
publicados e **não são conversões de edição**.

Cada personagem tem um JSON com:

- `nome`, `nivel_poder` e `pontos_poder_publicados`;
- `fonte.arquivo` e `fonte.pagina_pdf` (página do PDF, começando em 1);
- `ficha_publicada`, com as habilidades e as seções mecânicas encontradas no
  perfil. Nomes de efeitos, perícias e vantagens permanecem no idioma original
  do livro para evitar traduções ambíguas.

O extrator não recalcula pontos, não ajusta limites de NP e não inventa
complicações. Campos que não aparecem no perfil podem estar ausentes; o total de
pontos fica `null` quando não foi possível extraí-lo. Um travessão em uma
habilidade é preservado como publicado.

Os PDFs têm layouts em colunas e alguns glifos podem ser ambíguos na extração
automática. Quando uma informação parecer incompleta ou fora de contexto,
confira a página indicada no arquivo de origem. Para regenerar os arquivos,
execute `python ferramentas/extrair_fichas_dc.py` a partir da raiz do projeto.

Algumas fichas já foram conferidas com o livro e traduzidas: ficam em `../traducoes/dc/` (veja o README de lá) e têm
precedência sobre o JSON desta pasta na tela e nos PDFs. A reextração não as apaga.

## Qualidade da extração e reextração

A extração tem falhas conhecidas (defesas e pontos ausentes em parte das fichas, texto de seções misturado, letras
capitulares separadas). **Antes de mexer, leia `PREPARACAO_REEXTRACAO.md`**: ele traz o diagnóstico, a linha de base
(`auditoria_extracao.json`) e as regras para corrigir. Para medir: `python ferramentas/auditar_herois.py`.
