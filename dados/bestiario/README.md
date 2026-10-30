# Bestiário — formato das fichas e guia de conversão

Este é o guia para quem (pessoa ou IA) for **criar, converter ou revisar** criaturas em `dados/bestiario/`. O código
que lê estas fichas está em `nucleo/bestiario.py` (catálogo, filtros, escala de NP), `nucleo/bestiario_pdf.py` e
`nucleo/bestiario_docx.py` (downloads). Os testes ficam em `tests/test_bestiario.py`.

## Princípios

1. **Genérico.** O bestiário serve a qualquer campanha de fantasia (alta fantasia, sombria, The Witcher, Ravenloft...).
   Nada de itens, magias ou nomes que só existem num cenário: sem óleos e Sinais de bruxo, sem "contrato", sem
   regras de um livro de campanha. Uma criatura de folclore pode entrar; a ficha descreve a criatura, não a campanha.
2. **Só regras de Mutantes & Malfeitores 3e.** Todo traço vira um efeito, vantagem, perícia ou complicação do livro
   básico (com modificadores do livro: Área, Multiataque, Reação, Limitado, Ligado...). Mecânicas do D&D que não
   existem em M&M (recarga de sopro, ações e resistências lendárias, pontos de vida, CA) **não** são traduzidas
   como regra da casa: ficam de fora ou viram uma construção do livro.
3. **Sem dicas de mestre.** A ficha não traz conselhos de encontro, de covil ou de como usar a criatura. O único
   texto narrativo é a `descricao` e uma `tatica` curta (o que a criatura faz em combate).
4. **Fichas cadastradas não são alteradas.** Uma ficha que já está no git fica como foi feita, mesmo que tenha
   números discutíveis (veja "Problemas conhecidos"). Para outra versão, crie uma **variante** na mesma família.
   Para outro nível de poder, use a escolha de NP da tela (abaixo), que não mexe no arquivo.
5. **Fonte honesta.** O campo `fonte` diz de onde veio a criatura e termina em "adaptado para M&M 3e" quando é
   conversão. Ficha montada sem bloco de estatísticas (folclore, ideia própria) diz isso.

## Arquivo de uma criatura

Um JSON por criatura em `dados/bestiario/<gênero>/<categoria>/<id>.json`. O id da criatura é o caminho sem a
extensão (`fantasia/mortos_vivos/carnical`) e precisa bater com o campo `id`.

Categorias em uso na fantasia: `aberracoes`, `construtos`, `dragoes`, `feras`, `goblins`, `monstruosidades`,
`mortos_vivos`, `sobrenatural`.

```json
{
  "id": "fantasia/monstruosidades/lobisomem",
  "genero": "fantasia",
  "familia": "Lobisomem",
  "variante": "Forma Híbrida",
  "padrao": true,
  "nome": "Lobisomem",
  "tipo": "Monstruosidade",
  "subtipo": "Amaldiçoado",
  "papel": "Predador / Chefe",
  "chefe": true,
  "tamanho": "Médio",
  "nivel_poder": 8,
  "ambientes": ["Florestas", "Aldeias isoladas"],
  "descricao": "Uma ou duas frases: o que a criatura é.",
  "tatica": "Uma ou duas frases: o que ela faz em combate.",
  "complicacoes": ["Maldição: na lua cheia não controla a transformação."],
  "fonte": "Manual dos Monstros (D&D 5e), p. 205 (Licantropos), adaptado para M&M 3e",
  "ficha": {
    "habilidades": {"For": 5, "Vig": 5, "Agi": 4, "Des": 1, "Lut": 7, "Int": 0, "Pro": 3, "Pre": 1},
    "defesas": {"Esquiva": 8, "Aparar": 8, "Fortitude": 8, "Resistencia": 8, "Vontade": 6},
    "pericias": {"Percepção": 7, "Combate Corpo-a-Corpo: Garras e Mordida": 1},
    "vantagens": ["Iniciativa Aprimorada", "Ataque Poderoso"],
    "poderes": [{"nome": "Pele Amaldiçoada", "construcao": "Imunidade 20 (dano de armas comuns; prata e magia passam)."}],
    "ataques": [{"nome": "Garras", "bonus": 8, "dano": 7, "critico": 19, "descricao": "Pode derrubar"}],
    "equipamento": []
  }
}
```

### Campos

| Campo | Regra |
|----|----|
| `familia`, `variante`, `padrao` | Criaturas da mesma família aparecem juntas (chips de variante na ficha). **Uma** variante por família tem `"padrao": true`: é ela que a lista mostra quando "Agrupar famílias" está ligado. |
| `tipo` | Um dos tipos em uso: Aberração, Besta, Construto, Demônio, Dragão, Fada, Goblinoide, Monstruosidade, Morto-Vivo, Planta. Evite criar tipo novo sem motivo: ele vira opção no filtro. |
| `subtipo` | Livre (Ilitide, Amaldiçoado, Relicto, Draconídeo...). Entra na busca. |
| `papel` | Partes separadas por " / " (Bruto, Soldado, Emboscador, Lacaio, Conjurador, Artilharia, Predador, Montaria, Guardião, Líder, Chefe...). "(Solo)" pode vir no fim. Cada parte vira uma opção do filtro de papel. **Lacaio** faz o DOCX imprimir a regra de capanga. |
| `chefe` | `true` marca um possível chefe (a luta principal de uma sessão). Sem o campo, conta como chefe quem tem Chefe ou Líder no papel, ou "(Solo)". |
| `tamanho` | Diminuto, Miúdo, Pequeno, Médio, Grande, Enorme, Imenso. Só descreve; os números vêm de Encolhimento/Crescimento. |
| `nivel_poder` | O **NP padrão** da criatura (veja "Escolhendo o NP padrão"). |
| `complicacoes` | Fraquezas, maldições, restrições e motivações, como as complicações do livro básico. Aparecem na tela, no DOCX e nos campos de Complicações do PDF. **Não** ponha complicação dentro de `poderes`. |
| `habilidades` | Valores finais, **já com Crescimento ou Encolhimento somados**. Habilidade ausente (Vigor de morto-vivo ou construto, Força de incorpóreo) é `null` e aparece como "—". Fichas antigas usam `-5` para isso; não copie. |
| `defesas` | Totais. A chave é `Resistencia` (sem acento). Defesa que não existe (Fortitude de quem não tem Vigor) é a string `"Imune"`. |
| `pericias` | **Graduações**, não o total. A tela mostra "Furtividade 6 (+8)" somando a habilidade da perícia. Combate e Especialidade levam especialização: `"Combate Corpo-a-Corpo: Garras"`, `"Combate à Distância: Arcos"`, `"Especialidade: Magia"`. |
| `poderes` | `nome` + `construcao` no formato do livro: "Aflição 8 (resistida por Fortitude; Impedido, Imóvel, Transformado), Percepção (visual), Cumulativo." |
| `ataques` | `bonus` e `dano` inteiros; `critico` (20, ou 19 com Perigosa/Crítico Aprimorado); `descricao` curta. Efeito de área sem teste de ataque usa `"bonus": 0` e diz a CD na descrição: "Área Cone 18 m (CD 23 de Esquiva para metade)". Aflição pura (sem dano) fica só em `poderes`, não em `ataques`. |
| `equipamento` | Texto livre. Armadura no formato "Couro batido (+2 Resistência)". |

## Escolhendo o NP padrão

O NP padrão é o nível em que a criatura costuma aparecer. **Escolha pelo papel e pela competência, não pelo ND do
D&D**: o ND mede o perigo para um grupo de quatro personagens; o NP mede o quanto a criatura é boa no que faz.

Referências do **Guia do Mestre de Jogo** (fichas de M&M): Esqueleto e Zumbi NP 2; Lobo e Cavalo NP 3; Diabrete NP 4;
Gárgula NP 5; Urso e Demônio Guerreiro NP 6; Árvore Animada e Demônio Brutamontes NP 8; Dragão NP 9.

Conversões do D&D já no bestiário (use como régua, não como fórmula):

| ND no D&D | Criatura | NP padrão |
|----|----|----|
| 1 | Carniçal | 4 |
| 2 | Ogro, Grifo | 5 |
| 3 | Lobisomem (como chefe) | 8 |
| 4 | Ettin | 8 |
| 5 | Troll / Cria Vampírica | 7 / 6 |
| 6 | Medusa, Serpe (wyvern) | 8 |
| 7 | Devorador de Mentes | 9 |
| 8 | Hidra / Gigante do Gelo | 9 / 10 |
| 13 | Vampiro / Observador | 11 / 12 |
| 15–17 | Strahd, Dragão Vermelho Adulto | 13 |
| 21 | Lich | 14 |

Regra prática: **lacaios** (caem num golpe, vêm em bando) ficam 1 a 3 NP abaixo dos heróis; **tenentes** no NP dos
heróis; **chefes** 1 a 3 NP acima. Uma criatura que só funciona como chefe (lobisomem, medusa) pode ter o NP padrão
acima do que o ND sugere.

## Escala de NP (a tela e os downloads)

A ficha abre no NP padrão. O campo NP leva a criatura a qualquer NP de 1 a 20 (`bestiario.no_np`; `?np=12` na API
e nos downloads) **sem alterar o arquivo**. Cada NP a mais (ou a menos) vale ±1 em:

- Força, Vigor, Agilidade, Destreza, Luta e Prontidão (Intelecto e Presença não mudam; habilidade ausente continua
  ausente);
- Esquiva, Aparar, Fortitude, Vontade e Resistência (strings como "Imune" não mudam);
- bônus e dano de cada ataque;
- graduações de **Dano**, **Aflição**, **Enfraquecer \<habilidade\>** e **Anular**, e as **CDs**, onde aparecerem no
  texto dos poderes e das descrições de ataque;
- sem Vigor, a **primeira** "Proteção N" dos poderes (é de onde vem a Resistência).

As graduações de perícia não mudam (o total sobe com a habilidade). Como os limites do NP crescem 2 por NP e cada soma
(ataque + efeito, defesa + Resistência, Fortitude + Vontade) também cresce 2, **uma ficha dentro dos limites continua
dentro em qualquer NP acima**. O teste `test_subir_o_np_nunca_estoura_limites` garante isso.

Consequência para quem escreve fichas: **escreva as graduações no formato que a escala reconhece** ("Dano 8",
"Aflição 9", "Enfraquecer Vigor 4", "Anular 12", "CD 18"). "Dano baseado em Força +2" ou "dano de 8" não escalam.

## Limites do NP (confira antes de salvar)

| Limite | Regra |
|----|----|
| Ataque + efeito | bônus de ataque + Dano (ou Aflição, Enfraquecer...) ≤ 2 × NP |
| Efeito sem teste de ataque | Área e Percepção: graduação ≤ NP |
| Defesas | Esquiva + Resistência ≤ 2 × NP; Aparar + Resistência ≤ 2 × NP; Fortitude + Vontade ≤ 2 × NP |
| Perícias | habilidade + graduações ≤ NP + 10 |

Coerência interna (não é limite, mas a ficha deve fechar):

- **Resistência** = Vigor + Proteção + armadura do `equipamento` (+ Rolamento Defensivo, se tiver). Sem Vigor, só
  Proteção e armadura.
- **Bônus de ataque** = Luta (corpo a corpo) ou Destreza (à distância) + a perícia de Combate daquele ataque.
- **Dano de golpe físico** = Força + a arma ou a arma natural.
- **Esquiva ≥ Agilidade**, **Aparar ≥ Luta**, **Fortitude ≥ Vigor**, **Vontade ≥ Prontidão**, salvo quando o
  Crescimento reduz Esquiva e Aparar.

## Conversão do D&D 5e para M&M 3e

Não transponha números (PV, CA, modificadores de dano). Pegue o **conceito** e as **habilidades especiais** e
escolha o efeito equivalente. O Livro do Mestre da fantasia (`dados/livros/fantasia_mestre.md`, seções 9.9 e 13.7)
tem a mesma tabela para o gerador de NPCs.

### Habilidades

O modificador do D&D é um bom ponto de partida para a habilidade de M&M (FOR 18, +4 → Força 4), antes do tamanho.
Depois some o Crescimento ou o Encolhimento. Luta vem da precisão corpo a corpo da criatura (o bônus de ataque do
D&D menos o modificador da habilidade dá uma ideia); Prontidão vem de Sabedoria e Percepção.

### Tamanho

| D&D | M&M | Efeito nas habilidades |
|----|----|----|
| Pequeno | Encolhimento 4 (Permanente, Inato) | –1 Força, +2 Esquiva e Aparar, +4 Furtividade, –2 Intimidação |
| Grande | Crescimento 4 | +1 Força e Vigor por graduação; –1 Esquiva e Aparar a cada 2 graduações |
| Enorme | Crescimento 8 | idem |
| Imenso | Crescimento 12 | idem |

Escreva o poder como "Crescimento 4 (já somado em Força, Vigor e defesas; Permanente, Inato)".

### Traços e ações

| No D&D | Em M&M |
|----|----|
| Visão no escuro | Sentidos 2 (Visão no Escuro) |
| Faro, visão aguçada, percepção às cegas | Sentidos (Olfato Aguçado, Rastrear, Visão Estendida, Sentido Acurado) |
| Armadura natural | Proteção |
| Resistência a um tipo de dano | Imunidade ao descritor, Limitado a metade do efeito |
| Imunidade a um tipo de dano | Imunidade ao descritor (fogo, frio, veneno: 10; um descritor amplo: 20) |
| "Só armas mágicas ou de prata ferem" | Imunidade 20 (dano de armas comuns; prata e magia passam) |
| Imune a veneno, doença, sono, sufocamento | Imunidade às condições (Imunidade 30 a efeitos de Fortitude para mortos-vivos e construtos) |
| Imune a medo, enfeitiçar | Imunidade a efeitos de emoção/controle mental, ou a vantagem Destemido |
| Vantagem em salvamentos contra magia | +2 em Fortitude e Vontade, Limitado a efeitos mágicos |
| Morto-vivo, construto | `Vig: null`, `Fortitude: "Imune"`, Imunidade 30 (efeitos de Fortitude); Resistência só por Proteção |
| Incorpóreo | Insubstancial 4, ou Imunidade a dano físico comum (com o que passa, como prata ou magia) |
| Ataques múltiplos | Um ataque mais forte, ou Multiataque no efeito |
| Ataque que agarra | A vantagem Agarrar Aprimorado (ou Agarrar Rápido) e "Pode agarrar" na descrição |
| Derrubar no acerto | A vantagem Derrubar Aprimorado |
| Sopro, cone, linha | Dano com Área (Cone ou Linha); CD de Esquiva 10 + graduação para metade. Sem recarga |
| Veneno, doença | Aflição ou Enfraquecer resistidos por Fortitude, Ligados ao ataque |
| Olhar (petrificar, enfeitiçar, apavorar) | Aflição com Percepção (visual), as condições certas e, se for o caso, Cumulativo |
| Paralisia, sono, medo, encanto | Aflição com as condições de cada grau (Tonto/Impedido → Atordoado/Imóvel → Incapacitado/Paralisado/Controlado) |
| Drenar vida, força | Enfraquecer \<habilidade\> |
| Regeneração | Regeneração (com Limitado: "não age no turno seguinte a sofrer dano de fogo/prata/radiante") |
| Voo, natação, escalada, escavação | Voo, Natação, Movimento (Escalar Paredes), Escavação |
| Magia inata, lista de magias | Um **Arranjo**: a magia mais cara é o efeito principal; cada outra, "efeito alternativo, 1 PP" |
| Invocar aliados, animar mortos | Invocar \<graduação\> (criatura), Múltiplos |
| Teleporte, porta dimensional | Teleporte |
| Metamorfose | Morfar; forma de névoa ou etérea com Insubstancial |
| Táticas de matilha | Trabalho em Equipe |
| Fuga ágil, ação bônus de mover | Ação em Movimento |
| Camuflagem, esconder-se | Esconder-se à Plena Vista, Ocultamento (Limitado ao terreno) |
| Reação a quem sai do alcance | Efeito com o modificador Reação |
| Sempre alerta, não é surpreendido | Sentidos 1 (Sentido de Perigo) |
| Vulnerabilidade, proibições, maldição | **Complicação** em `complicacoes` |
| Ações lendárias, resistência lendária, ações de covil, recarga | Não existem em M&M: ficam de fora |

### Depois de converter

1. Confira os limites do NP e a coerência interna (tabelas acima).
2. Acrescente a criatura à tupla `FICHAS_NOVAS` em `tests/test_bestiario.py`: o teste verifica os limites do NP
   e que a ficha não tem termos de um cenário só nem dicas de mestre.
3. Rode `python -m pytest tests/test_bestiario.py`.

## Livros de referência

Os PDFs ficam em `referencias/` (fora do git). Em `referencias/dd/`: Manual dos Monstros, Mordenkainen Apresenta
Monstros do Multiverso, Tomo dos Monstros (Kobold Press, com muitas criaturas do folclore eslavo: leshy, likho,
rusalka, vila), Theros, Ravenloft e o Goblestiário têm texto extraível com `pypdf`. O **Livro dos Dragões** e a
**Maldição de Strahd** são escaneados (sem texto). Em `referencias/mm/`: Guia do Mestre de Jogo (fichas de
monstros com NP), Supernatural Handbook (em inglês), Livro de Magia e Perfis de Poder.

Para procurar um bloco de estatísticas, extraia o livro para texto (uma vez) e busque o nome em maiúsculas:

```python
import pypdf
leitor = pypdf.PdfReader("referencias/dd/old-dd-5e-manual-dos-monstros-biblioteca-elfica.pdf")
texto = "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)
```

## Problemas conhecidos nas fichas antigas

Ficam registrados aqui porque, pelo princípio 4, as fichas não são corrigidas no lugar:

- **Limites do NP:** Goblin Elétrico, Goblin de Areia e Esqueleto Guerreiro passam 1 ou 2 do limite de ataque +
  efeito; o Ogro passa 1 na Clava Gigante.
- **Resistência que não fecha** com Vigor + Proteção + armadura em cerca de dez fichas (Darakhul, Sombra, Fada,
  Bruxa do Mar, Gárgula, Minotauro, entre outras). Algumas usam "Crescimento (... Proteção +2)", que não é uma regra
  do livro.
- **Bônus de ataque** que não bate com habilidade + perícia em cerca de vinte ataques (goblins, hobgoblins, bruxas).
- **Vigor ausente** escrito como `-5` (mortos-vivos e construtos), em vez de `null`.

Se a ideia for corrigir uma delas, crie uma variante nova na família e deixe a antiga como está.
