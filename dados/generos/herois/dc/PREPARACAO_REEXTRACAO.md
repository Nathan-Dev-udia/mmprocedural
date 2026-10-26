# DC — preparação para reextrair as fichas (LEIA ANTES DE MEXER)

Aviso para quem (pessoa ou IA) for corrigir as fichas da DC: este arquivo resume o que a auditoria achou, onde estão as
causas e o que **não** fazer. A reextração é a parte cara; a Marvel já foi corrigida à parte.

## Estado medido (auditoria de 23/10/2026)

Rode `python ferramentas/auditar_herois.py dados/generos/herois/dc/auditoria_extracao.json --editora dc` para refazer.
O arquivo `auditoria_extracao.json` desta pasta é o retrato **antes** da reextração; use-o como linha de base e confira
se os números caem depois (nenhum código de problema deve crescer).

| Nível | Fichas (de 536) | Significa |
|---|---|---|
| jogável | 252 | habilidades, defesas, perícias e ataques completos e coerentes |
| ressalvas | 284 | divergência de custo, perícia ou limite de NP; o Mestre deve conferir |
| revisar | 0 | falta algo essencial (defesa ou habilidade) — saneado em 25/10/2026 |

Problemas por causa, em ordem de impacto:

1. **Defesas ausentes no JSON (58 fichas sem o campo `defesas`; ~40 com defesa "Immune" ou "—")**. A seção "Defense" não
   foi extraída (ex.: `dc/volume2/artemis`, `dc/volume1/black_manta`). Em `amazo` e `blackbriar_thorn` o livro imprime
   "Immune"/"—" em Fortitude: isso é legítimo e deve ficar como `null`/texto, nunca virar 0.
2. **Seção `pontos_poder` ausente ou truncada (71 + 45 fichas)**. Ex.: `artemis` só tem "Defenses 18 = Total 158".
3. **Texto de uma seção invadindo a outra**. Em `black_manta` a história do personagem ("THE MONSTER OF DEVIL'S DEEP…")
   foi parar dentro de `pericias`; em `ace_iii` o número de página/pontos ("150 150") caiu no fim das complicações.
4. **Complicações ausentes (165) ou cortadas (27)**, e algumas com o título comido (`blockbuster_roland_desmond`:
   "for His Own Good").
5. **Letra capitular separada** no Vol. I: "d odge 10 f or titude 12", "e xoskeleton", "f lying Ca rd". As palavras de
   estrutura já são religadas em `nucleo/herois_pdf.py` (`_religar`), mas o texto dos JSONs continua com as letras soltas.
   O certo é corrigir na extração.
6. **Perícias** com total menor que graduação + habilidade (72 fichas) e `pericias` com itens não lidos (~109):
   pode ser colunas trocadas na extração ou erro/errata do próprio livro. Confira a página do PDF antes de "corrigir".
7. **Ataques**: 69 fichas sem ataque lido. Há dois formatos no livro: `Unarmed +11 Close, Damage 11` (Vol. I) e
   `Unarmed +8 (Close, Damage 1)` (Vol. II). Alguns têm dano negativo, Affliction ou só "Initiative" — nesses casos o
   texto original é preservado nas notas do PDF.
8. **Custos de poderes** (`CUSTO_PODERES_DIVERGE`, 244): provavelmente ruído da auditoria no Vol. II (formato de custo
   diferente de "• N points"). Não trate como erro de dados sem verificar.
9. Habilidades como "15/5" ou "---" (51 fichas): formas alternativas ou criaturas sem o atributo. Preservar como texto.

## Regras para a reextração

- **Não invente dados.** Campo que o livro não traz fica ausente ou `null`, como o README desta pasta já diz.
- **Não edite os JSONs à mão em massa.** `python ferramentas/extrair_fichas_dc.py` regenera tudo e sobrescreve. Corrija o
  extrator e regenere; correção manual só para um caso isolado e registrado.
- Os PDFs ficam em `referencias/dc/` (fora do git). A página de cada ficha está em `fonte.pagina_pdf`: confira lá.
- **Mantenha os ids** (nome do arquivo = id da ficha) e a estrutura `ficha_publicada` com as mesmas chaves. O catálogo
  (`nucleo/herois.py`), o PDF (`nucleo/herois_pdf.py`) e os testes (`tests/test_herois.py`, que contam 536 fichas)
  dependem deles. Se o número de fichas mudar, atualize o teste de propósito.
- Os JSONs desta pasta ficam em inglês, como no livro. A tradução vai em `../traducoes/dc/` (veja "Tradução: o que falta
  fazer" no README desta pasta), que a reextração não toca.
- Depois de regenerar: `python ferramentas/auditar_herois.py <saida.json> --editora dc`, compare com a linha de base,
  e rode `python -m pytest` (a suíte gera o PDF das 652 fichas). Atualize `auditoria_extracao.json` e a tabela acima.
- Se mudar o formato de algum campo, ajuste `_ler_dc` em `nucleo/herois_pdf.py` e crie um teste com uma ficha real.

## Onde olhar

- `ferramentas/extrair_fichas_dc.py`: o extrator (colunas por coordenada em `_coordinate_profile_sections`,
  fallback por texto em `_extract_sections`).
- `nucleo/herois_pdf.py`: leitura das fichas DC para o PDF (`_ler_dc`, `_ataques_dc`, `_religar`).
- `ferramentas/auditar_herois.py`: os códigos de problema e as regras conferidas.
