# DC Adventures — fichas em JSON

Os arquivos em `volume1/` e `volume2/` foram extraídos dos livros
`DC Adventures: Heroes and Villains, Vol. I` e `Vol. II` (os PDFs ficam em `referencias/dc/`, fora do git). Os dois livros usam
Mutants & Masterminds 3ª edição; portanto, estas fichas preservam os dados
publicados e **não são conversões de edição**.

Cada personagem tem um JSON com:

- `nome`, `nivel_poder` e `pontos_poder_publicados`;
- `fonte.arquivo` e `fonte.pagina_pdf` (página do PDF, começando em 1);
- `ficha_publicada`, com as habilidades e as seções mecânicas encontradas no
  perfil, no idioma original do livro (inglês). A tradução fica em outra pasta
  (veja "Tradução" abaixo).

O extrator não recalcula pontos, não ajusta limites de NP e não inventa
complicações. Campos que não aparecem no perfil podem estar ausentes; o total de
pontos fica `null` quando não foi possível extraí-lo. Um travessão em uma
habilidade é preservado como publicado.

Os PDFs têm layouts em colunas e alguns glifos podem ser ambíguos na extração
automática. Quando uma informação parecer incompleta ou fora de contexto,
confira a página indicada no arquivo de origem. Para regenerar os arquivos,
execute `python ferramentas/extrair_fichas_dc.py` a partir da raiz do projeto.

## Tradução: o que falta fazer

A meta é ter todas as fichas da DC em português, conferidas com o livro. Cada ficha traduzida é um arquivo em
`../traducoes/dc/<volume>/<id>.json` (formato no README de lá). Esse arquivo tem precedência sobre o JSON desta pasta na
tela e nos dois PDFs, e a reextração não o apaga.

### Situação em 26/10/2026

Traduzidas e conferidas: **8 de 536**. São elas: Aquaman, Batman, Flash (Barry Allen), Arqueiro Verde (Oliver Queen) e
Lanterna Verde (Hal Jordan), do Vol. I; Super-Homem, Mulher-Maravilha e Caçador de Marte, do Vol. II.

### Pendências

1. **Traduzir as 528 fichas restantes.** Sugestão de ordem: primeiro os outros heróis da Liga da Justiça (Lanternas
   Verdes John Stewart, Guy Gardner e Kyle Rayner; Flashes Wally West e Jay Garrick; Canário Negro, Ciborgue, Gavião
   Negro, Zatanna etc.), depois os vilões mais usados (Coringa, Lex Luthor, Sinestro, Mulher-Leopardo, Arraia Negra
   etc.), depois o resto. Para achar as fichas com mais problemas de extração, que mais ganham com a conferência, use
   `auditoria_extracao.json`.
2. **Traduzir as descrições dos personagens.** Hoje só a parte mecânica (o bloco de estatísticas) é guardada. Cada
   perfil do livro também tem:
   - **Identidade:** nome real, ocupação, afiliação e base;
   - **Textos de apresentação:** história de origem, Personalidade, Poderes & Habilidades, Aliados e Inimigos;
   - **Quadros laterais:** kryptonita, flechas extras, façanhas de poder sugeridas e afins;
   - **Variações e coadjuvantes:** versões alternativas (como o Rei Guerreiro do Aquaman) e fichas curtas de
     coadjuvantes na mesma página (como Tom Kalmaku e Iris Allen).

   Para isso falta criar campos no formato da tradução (por exemplo, `identidade` e `descricao` com uma entrada por
   seção), mostrá-los na tela (`_secoes_traduzidas` em `nucleo/herois.py`) e decidir o que vai para o PDF padrão. Por
   enquanto, nas 8 fichas prontas, só os quadros que importam para o jogo foram resumidos em `notas`.
3. **Criar um glossário inglês → português** (efeitos, modificadores, vantagens, condições, nomes de personagens e
   lugares). Hoje os termos estão espalhados pelas 8 fichas e pelos dados em `dados/comum`; um glossário único evita
   que fichas diferentes usem traduções diferentes para o mesmo termo.

### Como traduzir uma ficha

1. Abra a página do livro (`fonte.pagina_pdf` no JSON desta pasta, PDFs em `referencias/dc/`) e copie os dados **do
   livro**, não do JSON extraído. A extração costuma misturar a história com as perícias, cortar o equipamento e perder
   as complicações.
2. **Termos de jogo:** use a tradução brasileira do M&M 3e, com os mesmos termos de `dados/comum` (Aflição, Ataque
   Imprudente, Tolhido, Suporte Vital...).
3. **Nomes:** use os nomes publicados no Brasil (Super-Homem, Mulher-Leopardo, Planeta Diário, Asa Noturna).
4. **Unidades:** converta milhas por hora para km/h.
5. **Números:** mantenha os impressos no livro. Confira cada custo de poder e de equipamento pela tabela de custos e
   corrija só o item que estiver errado (como a Telepatia do Caçador de Marte, impressa com 31 em vez de 42). As parcelas
   e o total ficam como no livro, e toda diferença vai para `notas`.
6. Rode a conferência de contas (habilidades × 2, graduações ÷ 2, soma das parcelas) e `python -m pytest`. Inclua a
   ficha na lista `TRADUZIDAS` de `tests/test_herois.py`.

## Qualidade da extração e reextração

A extração tem falhas conhecidas (defesas e pontos ausentes em parte das fichas, texto de seções misturado, letras
capitulares separadas). **Antes de mexer, leia `PREPARACAO_REEXTRACAO.md`**: ele traz o diagnóstico, a linha de base
(`auditoria_extracao.json`) e as regras para corrigir. Para medir: `python ferramentas/auditar_herois.py`.
