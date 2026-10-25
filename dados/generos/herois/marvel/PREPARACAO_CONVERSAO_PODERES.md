# Marvel — completar a conversão dos poderes (LEIA ANTES DE MEXER)

Aviso para quem (pessoa ou IA) for continuar o trabalho nas fichas da Marvel.

## O que já está feito e o que falta

- **A extração está completa.** O livro é um só: `referencias/marvel/mutants-masterminds-marvel-files-pr_e5850f76d9cea8b6721dc9f1fe9fe08e.pdf`
  (117 páginas). A página 1 não tem ficha; as páginas 2 a 117 têm um perfil cada, e há 116 JSONs, um por página
  (`fonte.pagina`), sem repetição e sem página com dois perfis. **Não há personagem faltando.** Não procure outros livros.
- **O que falta é fechar a conversão da 2ª para a 3ª edição**, principalmente dos poderes complexos (arrays, dispositivos, formas alternativas e efeitos com modificadores sem equivalência direta):
  - Todas as 116 fichas já possuem o bloco `custos_3e` padronizado (incluindo as 10 fichas de `absorbing_man` a `bullseye` e `bishop`), com `habilidades`/`habilidades_base`, `defesas` (1 PP por graduação comprada), `pericias` (1 PP a cada 2 graduações) e `vantagens` preenchidos.
  - **104 fichas** já estão com `pontos_poder_3e` e `custos_3e.total` totalmente fechados (incluindo os lotes de fechamento: `adam-x`, `archangel`, `avalanche`, `baron_zemo`, `beast`, `bishop`, `black_cat`, `black_panther`, `blink`, `bullseye`, `cannonball`, `captain_america`, `captain_britain`, `colossus`, `cyclops`, `daredevil`, `deadpool`, `doctor_octopus`, `domino`, `dust`, `elektra`, `elixir`, `forge`, `gambit`, `green_goblin`, `havok`, `hawkeye`, `hellion`, `human_torch`, `iceman`, `invisible_woman`, `iron_fist`, `iron_man`, `jean_grey`, `jubilee`, `kingpin`, `longshot`, `luke_cage`, `mach_iv`, `mary_jane_watson`, `mercury`, `mister_fantastic`, `moon_knight`, `multiple_man`, `mystique`, `nightcrawler`, `nocturne`, `northstar`, `prodigy`, `puck`, `punisher`, `quicksilver`, `red_skull`, `rogue`, `sandman`, `scarlet_witch`, `shadowcat`, `shocker`, `silver_samurai`, `siryn`, `speedball`, `spider_man`, `storm`, `sunfire`, `surge`, `tag`, `taskmaster`, `thing`, `toad`, `tombstone`, `vulture`, `wallflower`, `white_queen`, `wind_dancer`, `wither`, `wolfsbane`). `beast` é o **modelo original de ficha completa**: leia-o primeiro.
  - **12 fichas** têm `custos_3e.poderes_pendentes: true`. Nelas, poderes de equivalência direta já têm `custo_3e_pp` preenchido e somado em `poderes_conhecidos`, mas poderes dependentes de julgamento de design permanecem como `custo_3e_pp: null` até seu respectivo lote de fechamento.
  - Vantagens e ataques de todas as 116 fichas traduzidos para o português canônico de M&M 3e, com suporte completo no gerador de PDF e visualizador.
  - Regra de habilidades negativas confirmada no livro oficial de M&M 3e (pág. 56: *"Ganhe 2 pontos de poder para cada -1 de graduação de habilidade"*); `giant_man` e `hulk` foram ajustados e todas as ressalvas de habilidades foram zeradas (0 ressalvas).
- Fichas com valor `null` **de propósito**: `chamber` e `sentinel` (o livro imprime travessão; são construtos sem
  Constituição). Não preencha com 0.

## Linha de base e conferência

`python ferramentas/auditar_herois.py dados/generos/herois/auditoria_marvel.json --editora marvel` mede a qualidade sem
alterar nada. O arquivo `dados/generos/herois/auditoria_marvel.json` é o retrato atualizado (114 jogáveis, 0 com ressalvas,
2 "revisar" que são os `null` intencionais). **Não guarde esse JSON dentro de `marvel/`**: o catálogo lê todo `*.json`
dessa pasta como ficha. Depois de cada lote: rode a auditoria e `python -m pytest`.

## Como converter um poder (ficha a ficha)

1. Abra a página `fonte.pagina` do PDF (pypdf conta páginas a partir de 1, como o JSON) e o guia
   `referencias/marvel/conversor 2e para a 3e.pdf`. Há rascunhos de exemplo em `referencias/marvel/rascunhos/`.
2. Em cada item de `ficha.poderes`, defina `construcao_3e` (efeito, graduação e modificadores 3e) e `custo_3e_pp`.
   Mantenha `custo_2e_pp` como está: é o custo impresso na fonte.
3. Se algum efeito, extra ou falha não tiver equivalente seguro, **não adivinhe**: deixe `custo_3e_pp: null`, mantenha
   `poderes_pendentes: true` e explique em `notas_conversao`. Só feche o total quando todos os poderes tiverem custo.
4. Com todos os custos conhecidos: preencha `custos_3e.poderes`, `custos_3e.total` e `pontos_poder_3e` (iguais),
   ponha `poderes_pendentes: false` e remova `subtotal_conhecido`, como em `beast`. Use as chaves de `beast`
   (`habilidades_base`, `poderes`, `total`) e não crie variantes novas.
5. Registre decisões em `notas_conversao` (o que mudou, o que foi omitido e por quê).

## Custos 3e (confira sempre)

- **Habilidades:** 2 PP por graduação, calculado sobre `habilidades_base` quando os aumentos vêm de poderes
  (Enhanced Strength etc.); senão pagaria duas vezes. Habilidade abaixo de 0 reembolsa PP? **Regra ainda não confirmada**
  (afeta `giant_man` e `hulk`, em que o JSON ignora o reembolso); confirme no livro básico antes de mudar.
- **Perícias:** 1 PP a cada **2 graduações**. (Erro já corrigido em 28 fichas: o custo estava igual às graduações.)
- **Defesas:** 1 PP por graduação comprada. **Vantagens:** 1 PP por graduação/vantagem. **Poderes:** custo do efeito.
- `ficha.pericias` guarda **graduações 3e** (bônus impresso menos a habilidade). Limite: NP + 10.
- Limites de NP: ataque + dano, Esquiva + Resistência, Aparar + Resistência e Fortitude + Vontade, cada par ≤ 2 × NP.
  Quando a fonte estoura, reduza o valor, registre o ajuste e marque `status_conversao: convertida_com_ajustes_de_np`.

## Erros que já aconteceram (não repita)

- Somar duas perícias distintas em uma só (Icarus: Perform [Singing] 12 + Perform [Stringed Instruments] 12 viraram
  "Performance 24", acima do limite). Cada perícia especializada do livro é uma entrada separada.
- Usar o custo de perícias igual ao número de graduações.
- Inventar vantagem, perícia ou complicação sem equivalente; o correto é omitir e anotar.
- Preencher com 0 um valor que o livro imprime como travessão.

## Convenções

- Abreviações das habilidades: `For, Vig, Agi, Des, Lut, Int, Pro, Pre`.
- Perícias: Drive e Pilot viram `Veículos`; Survival vira `Especialidade: Sobrevivência`; Computers vira `Tecnologia`;
  Knowledge (Technology) vira `Especialidade: Tecnologia` (são perícias distintas; não elimine).
- Nomes de vantagens e efeitos ficam em inglês; as explicações, em português.
- Mantenha o nome do arquivo (é o id da ficha), a indentação de 2 espaços e o fim de linha CRLF dos arquivos.
- `nucleo/herois.py` e `nucleo/herois_pdf.py` leem estas fichas; o teste conta 116 da Marvel. Se mudar o esquema,
  ajuste `_ler_marvel` e crie um teste com uma ficha real.
