# Gerador de fichas · M&M 3ª edição

Gera fichas de Mutantes & Malfeitores 3e para vários gêneros de campanha (hoje: **Faroeste**, **Cyberpunk** e **Fantasia medieval**). Cada gênero tem duas abas:

- **Ficha de jogador:** um personagem por vez, num passo a passo (Gênero → Nome → Raça, só na fantasia → Arquétipo ou Classe → Vantagens → Implantes ou Magias, nos gêneros com poderes → Armas e itens → Complicações → Ficha). O último passo resume as escolhas antes de gerar. Feito a partir dos arquétipos de jogador do gênero. Gasta exatamente 15 PP por NP e exige Motivação e mais uma complicação. O equipamento é comprado com o dinheiro inicial: dólares no faroeste, eurobucks no cyberpunk (preços do Cyberpunk RED), peças de ouro na fantasia (preços do Livro do Jogador de D&D 5e). No cyberpunk, o personagem também pode ter implantes, que custam PP e eurobucks; na fantasia, magias e dons de classe e traços raciais.
- **Fichas de NPC:** grupos a partir de fichas-base dos livros e módulos cadastrados em JSON. A ficha sobe até 70–100% dos limites do NP escolhido.

## Como rodar

```
pip install -r requirements.txt
python app.py
```

A página abre sozinha em http://127.0.0.1:5000/ (gênero padrão: faroeste; `?genero=cyberpunk` abre direto no outro). Para parar, use Ctrl+C no terminal.

Testes:

```
python -m pytest
```

## Arquivos

| Caminho | O que faz |
|----|----|
| `app.py` | Rotas do Flask: a página e a API (`/api/gerar`, `/api/regerar`, `/api/jogador/...`, downloads). Toda chamada leva o `genero`. |
| `nucleo/generator.py` | NPCs: escolhe a ficha-base, sorteia módulos conforme o estilo, aplica e tenta de novo se a combinação não servir. |
| `nucleo/player.py` | Monta fichas de personagem de jogador (equipamento em dinheiro ou em pontos, implantes). |
| `nucleo/escalar.py` | Sobe a ficha passo a passo (+1 por vez) seguindo prioridades, sempre dentro dos limites do NP. |
| `nucleo/validator.py` | Calcula valores, custos e limites do NP de uma ficha pronta e define o status. Não sorteia nada. |
| `nucleo/rules.py` | Tabelas do livro básico: custos, perícias, limites do NP. |
| `nucleo/poderes.py` | Transforma um poder do catálogo (Perfis de Poder) em poder da ficha: custo, ajustes, ataque. |
| `nucleo/data_loader.py` | Lê e confere os JSON de cada gênero. Mostra todos os erros de uma vez. |
| `nucleo/formatter.py` | Monta os textos do cartão e o bloco para copiar. |
| `nucleo/pdf_export.py`, `nucleo/docx_export.py` | Ficha editável em PDF e fichas em Word. |
| `dados/comum/` | O que vale para todos os gêneros: `settings.json`, `styles.json`, `vantagens.json`, a ficha editável e o catálogo de poderes. |
| `dados/generos/<id>/` | Um gênero: `genero.json`, `archetypes.json`, `modules.json`, `equipment.json`, `names.json`, `player.json`, `complications.json` e, se tiver, `powers.json`. |
| `ferramentas/` | Scripts de apoio: extração do Perfis de Poder e criação da base do cyberpunk e da fantasia. |
| `templates/`, `static/` | A página (HTML, CSS e JavaScript). |
| `tests/` | Testes com sementes fixas. |

## Gêneros

Cada pasta em `dados/generos/` com um `genero.json` vira uma opção na página:

```json
{
  "id": "cyberpunk",
  "nome": "Cyberpunk",
  "descricao": "Texto do seletor.",
  "perfis_de_poder": ["Blindados", "Tecnológicos", "Sensoriais", "Elétricos", "Velozes", "Fortes"],
  "configuracoes": {
    "rotulo_poderes": "Implantes",
    "equipamento": "dinheiro",
    "moeda": "eb",
    "implantes_em_dinheiro": true,
    "prioridades_gerais": ["defesa:Esquiva", "pericia:Veículos"],
    "pericias_de_reserva": ["Percepção", "Tecnologia", "Veículos"]
  }
}
```

- `perfis_de_poder`: quais capítulos do Perfis de Poder o gênero pode usar. O faroeste usa `[]` (sem poderes).
- `configuracoes` sobrescreve `dados/comum/settings.json` só para esse gênero:
  - `rotulo_poderes`: o nome da seção de poderes na ficha ("Traços naturais", "Implantes"...).
  - `equipamento`: `dinheiro` (compra com o dinheiro inicial, regra de equipamento gratuito do Guia do Mestre) ou `pontos` (vantagem Equipamento, 5 pontos por graduação, livro básico cap. 7).
  - `moeda`: `$` (padrão), `eb` ou `po`. Moeda com letras vai depois do número ("2.550eb", "15 po").
  - `rotulo_arquetipo` e `rotulo_foco`: como a tela chama arquétipo e foco ("Classe" e "Subclasse" na fantasia).
  - `np_padrao_jogador`: o NP que a tela sugere (a fantasia começa no NP 5; dá para escolher do 2 ao 10).
  - `itens_basicos`: itens que todo PJ leva (comida, no faroeste e na fantasia).
  - `implantes_em_dinheiro`: os implantes custam também o preço do cyberware, além dos PP.
  - `prioridades_gerais` e `pericias_de_reserva`: o que o gerador sobe quando as prioridades do arquétipo acabam.

Se um gênero tiver erro nos dados, os outros continuam funcionando e a página lista os erros.

### Faroeste

Sem poderes. Equipamento em dólares, com as condições financeiras do Guia do Mestre. 7 arquétipos de jogador e os NPCs do Oeste (pistoleiros, xerifes, capangas, cavalos...).

### Cyberpunk

- **NPCs** (`archetypes.json`): fichas-base dos coadjuvantes do livro básico adaptadas: gangue (Bandido; líder), segurança corporativa (Policial; Policial de Elite), mercenário (Soldado), netrunner (Cientista adaptado), atravessador (Informante; Senhor do Crime) e agente (Agente do Governo).
- **Módulos** (`modules.json`): implantes (blindagem, braço cibernético, olhos, reflexos, interface neural, braço-canhão a partir do NP 5, taser, camuflagem óptica, netrunner veterano), perícias (atirador, brutamontes, infiltrador, piloto, médico de rua, negociador) e o modelo **Ciborgue**, convertido do Mecha & Mangá (2ª edição) pelo guia de conversão.
- **Jogador** (`player.json`): os 10 Papéis do Cyberpunk RED (Rockerboy, Solo, Netrunner, Tech, Medtech, Media, Exec, Policial/Lawman, Fixer e Nômade), cada um com 3 focos. Os itens essenciais são o kit inicial do Papel no RED (p. 98 e 103).
- **Dinheiro inicial** (eurobucks): Hotel-cápsula 800eb (+1 PP), Contêiner 2.550eb (padrão: o Pacote Completo do RED, p. 104), Quitinete 7.500eb (1 PP), Apartamento 25.000eb (2 PP), Conapt de luxo 100.000eb (4 PP), Cobertura 500.000eb (6 PP). É a mesma escada de Riqueza/Benefício do faroeste; os nomes são da moradia típica de cada faixa no RED.
- **Armaduras** custam o conjunto corpo + cabeça (no RED são duas peças). A flak (Proteção 5 contra balísticos) é um item à parte; a "armadura militar" (Proteção 3) é a do Soldado do livro básico.
- **O Nômade** recebe a moto do clã, emprestada, por 0eb (Habilidade de Papel Moto do RED).
- **Guia do mestre:** `referencias/cyberpunk_mm_regras.md` (e `.docx`) traz as regras do gênero e a conversão dos preços.
- **Equipamento** (`equipment.json`): estatísticas de M&M (livro básico, cap. 7) com o preço do RED (`preco`, `categoria_de_preco`, `fonte_preco`). Itens sem equivalente no RED (armas de energia, metralhadora, explosivo plástico, GPS...) têm o preço típico da categoria e `preco_estimado: true`; a tela marca "(estimado)". Os coletes à prova de balas valem só contra ataques balísticos (veja abaixo). NPCs continuam pagando o equipamento com a vantagem Equipamento, como as fichas do livro.
- **Implantes** (`powers.json`): 21 poderes do Perfis de Poder com nome de implante. Custam os PP do livro (por isso as fichas com implantes ficam com status "Custos calculados") **e** o preço do cyberware equivalente no RED (ex.: Reflexos turbinados = Link Neural + Sandevistan = 1.000eb). O cyberware entra no contador de dinheiro; se passar, vale a mesma regra do faroeste (subir a Riqueza com PP ou ficar devendo, de preferência a um ripperdoc).
- Os preços são aplicados por `ferramentas/precos_cyberpunk_red.py`; edite a tabela lá e rode de novo.

### Fantasia medieval

Classes, subclasses e raças do Livro do Jogador de D&D 5e, convertidas para M&M 3e. Tudo é gerado por `ferramentas/criar_fantasia_base.py` (rode de novo depois de mudar a tabela lá; ele recria os arquivos, exceto `archetypes.json` e `modules.json`).

- **Jogador** (`player.json`): as 12 classes (Guerreiro, Bárbaro, Ladino, Mago, Feiticeiro, Bruxo, Clérigo, Paladino, Patrulheiro, Druida, Monge, Bardo), cada uma com 3 subclasses como focos (ex.: Mago → Evocação, Ilusão, Abjuração).
- **Raças** (`racas` no `player.json`): Humano, Anão, Elfo, Halfling, Draconato, Gnomo, Meio-elfo, Meio-orc e Tiefling. Cada raça tem ajustes de habilidade, vantagens, perícias e poderes raciais, e **tudo custa PP do orçamento** (o humano não tem traços: os pontos ficam livres). O nome sorteado segue a raça (`nomes`). Um gênero sem `racas` não mostra o passo.
- **Magias** (`powers.json`): 51 magias e dons de classe e 7 traços raciais, todos apontando para o catálogo. As magias de cada tradição (arcana, divina, da natureza, de pacto, bárdica) formam um **Arranjo**; as de ataque usam a perícia única *Combate à Distância: Magia*, como os "Feitiços" do Cultista Arcano do Guia do Mestre.
- **Equipamento** (`equipment.json`): armas, armaduras e escudos do livro básico de M&M (cap. 7) com o preço do Livro do Jogador em peças de ouro (1 pp = 0,1 po; 1 pc = 0,01 po). Armas que o M&M não tem (espada grande, arco longo, besta pesada...) são a arma mais próxima com +1 de Dano e +1 ponto; a `fonte` diz "adaptado". **Escudos** dão +1/+2/+3 em Esquiva e Aparar (`defesas_ativas`); se o escudo ou a armadura estourar o limite do NP, sai da ficha e o dinheiro volta.
- **Dinheiro inicial**: Camponês 30 po (+1 PP), Aventureiro 120 po (padrão, perto da média do ouro inicial das classes), Burguês 400 po (1 PP), Mercador próspero 1.600 po (2 PP), Nobre menor 6.000 po (4 PP), Grande nobre 30.000 po (6 PP).

### Arranjos e magias que acompanham o NP

- **Arranjo** (livro básico, cap. 6, Efeitos Alternativos): poderes com o mesmo `"arranjo"` são usados um de cada vez. O mais caro é o efeito principal e paga o custo cheio; cada outro custa 1 PP. A ficha mostra "Arranjo Magia arcana: efeito principal" e "efeito alternativo (1 PP)", e o contador da tela faz a mesma conta. Fichas escritas à mão também podem usar `"arranjo"` (é assim que o Cultista Arcano fecha os 15 PP de poderes do livro).
- **`graduacao_np`**: a graduação do poder é o NP do personagem mais esse ajuste (mínimo 1). O Raio de fogo (`0`) é Dano 5 no NP 5 e Dano 8 no NP 8; a Armadura arcana (`-3`) é Proteção 2 no NP 5. Custo e graduação mudam na tela quando o NP muda.
- **`estatistica`** reescreve a linha do catálogo com o descritor do gênero ("Dano à Distância, Multiataque (força)" no lugar de "(Laser)"), e **`pericia`** troca a perícia do ataque.
- **`so_racial`**: o poder só vem com a raça; não aparece na lista de magias.

## Catálogo de poderes

`dados/comum/poderes/perfis_de_poder.json` tem 940 poderes extraídos do *Perfis de Poder* (`ferramentas/extrair_perfis.py`), cada um com perfil, categoria, estatística, custo do livro e o efeito-base interpretado (alcance, área, defesa). 81 entradas estão marcadas `conferir` (custo ou efeito que o extrator não entendeu) e não entram nas buscas.

Um gênero usa os poderes de duas formas:

- **Direto do catálogo**, numa ficha ou módulo: `{"catalogo": "blindados__armadura", "graduacao": 2}`.
- **Pelo `powers.json` do gênero**, que dá nome e descrição a um poder do catálogo (`"Blindagem subdérmica"`): `{"do_genero": "blindagem_subdermica"}`. Quando o livro dá dois preços (Defesa Rápida: 1 PP por graduação de uma defesa, 2 PP pelas duas), a entrada traz `custo_por_graduacao`.

O programa entende os efeitos que mudam habilidades e defesas (Força Aumentada, Esquiva/Aparar/Vontade Aumentada, Proteção) e os efeitos de ataque (Dano, Aflição, Enfraquecer, Pasmar, Armadilha, Nulificar), corpo a corpo, à distância, em área ou de percepção. Ataques de poder entram na checagem de limites do NP como qualquer arma.

## Downloads

Cada cartão tem três formatos:

- **Baixar PDF (ficha editável)** (botão em destaque): preenche a ficha de personagem editável de M&M. O PDF continua editável, e os números seguem as fórmulas do próprio formulário.
- **Baixar DOCX:** a ficha em Word, com tabelas (habilidades, defesas, ataques, perícias), vantagens, poderes, equipamento, custos, descrição, tática e validação.
- **Baixar TXT:** o mesmo bloco de texto do botão "Copiar texto".

**Baixar todas as fichas (.zip)** traz `docx/` e `pdf/` com uma ficha por NPC, mais `todas_as_fichas.docx` (uma ficha por página) e `todas_as_fichas.txt`. **Baixar JSON** traz os dados completos do grupo.

O modelo usado é `dados/comum/ficha_editavel.pdf` (campo `ficha_pdf` em `settings.json`). Se o arquivo não existir, a página mostra só o download em texto. Na cópia gerada, o programa limpa os campos que vieram preenchidos no modelo e corrige a fórmula do total do 2º Combate à Distância, que somava o nome da especialização.

Ajustes da ficha:
- **Especialidade: Cavalgar** usa Agilidade, mas a ficha soma Intelecto nas Especialidades. A diferença vai na coluna "Outros", e o total fica certo.
- Ataques além de 4, perícias especializadas além das linhas disponíveis e vantagens além de 11 vão para Notas & Condições ou para a última linha.

## Como o NP é usado

| | Ficha de jogador | Ficha de NPC |
|----|----|----|
| Pontos | Exatamente 15 × NP (+1 se a Riqueza for baixa). | Sem orçamento; o custo é só informativo, como o livro trata PdMs. |
| Como sobe | Gasta os pontos por prioridade (foco → perícias das armas que carrega → arquétipo → gerais) até fechar o total. | Depois dos módulos, sobe por prioridade até a ficha chegar a uma fração sorteada (70–100%) dos tetos do NP. |
| Limites | Todos os limites do NP; Sorte até metade do NP. | Iguais. |

Tetos que o gerador respeita ao subir vantagens: Crítico Aprimorado 4 e Sorte até metade do NP (livro); Iniciativa Aprimorada até NP ÷ 3 (escolha do gerador, porque o livro não limita a iniciativa). Habilidades até 7, o ápice humano da tabela do livro.

**Proteção:** bônus de armadura não se somam a outros bônus de Proteção; vale o maior (livro básico, cap. 7). Coletes à prova de balas ("Res 6/2" no livro) são Proteção limitada a ataques balísticos: contam para Esquiva + Resistência, mas não para Aparar + Resistência, e a ficha mostra as duas Resistências.

As prioridades ficam nos dados: `prioridades` em cada arquétipo (`archetypes.json` e `player.json`) e `prioridades_gerais` (em `settings.json` ou no `genero.json`), no formato `"tipo:nome"`, por exemplo `"pericia:Tratamento"`, `"habilidade:Des"`, `"defesa:Esquiva"` ou `"vantagem:Ataque à Distância"`. Os módulos de NPC usam como prioridade o que eles acrescentam, a menos que tenham uma lista `prioridades` própria.

## Ficha de jogador

`player.json` (em cada gênero) tem as opções de riqueza e os arquétipos. Cada arquétipo traz conceito, vantagens essenciais e opcionais, prioridades, equipamento inicial, sugestões de complicações e focos (cada foco com vantagens, prioridades, equipamento e implantes extras). Em gêneros com `powers.json`, o arquétipo também tem `implantes.essenciais` e `implantes.opcionais`. `complications.json` traz as motivações e complicações.

Vantagens, equipamento e implantes têm dois modos na tela:

| | Sortear de acordo com o arquétipo | Escolher |
|----|----|----|
| **Vantagens** | Essenciais do arquétipo e do foco, mais 0 a 2 opcionais do arquétipo. | O jogador marca as vantagens (as do arquétipo já vêm marcadas). O gerador só sobe graduações das marcadas. |
| **Armas e itens** | 1 arma principal (ou a do foco), talvez 1 secundária, a munição certa de cada arma de fogo, os itens básicos do gênero (comida, no faroeste), os itens essenciais e 1 a 3 opcionais. Armas que não cabem no NP nem entram no sorteio. (Num gênero com equipamento em pontos, no máximo ~1/6 do orçamento vai para Equipamento.) | O jogador marca o que quer, com as sugestões do arquétipo no topo e um contador de dinheiro (dólares ou eurobucks; pontos de equipamento nos gêneros em pontos). Arma que não cabe no NP fica de fora. Comida, munição e bebida têm um campo de quantidade (1 a 99 pacotes; o preço é multiplicado e a ficha mostra "×3"). |
| **Implantes** (cyberpunk) | Essenciais do arquétipo e do foco, mais 0 a 2 opcionais, até ~35% do orçamento em PP e só o que o dinheiro que sobrou dos itens paga. | O jogador marca os implantes, cada um com o custo em PP e em eurobucks; o preço entra no contador de dinheiro. |

`itens_basicos` (em `configuracoes` do `genero.json`) lista os itens que todo PJ do gênero leva: entram no sorteio e já vêm marcados no modo Escolher. No faroeste, são as rações de viagem; no cyberpunk, a comida já está no custo de vida da condição financeira.

Implantes que passariam de algum limite do NP ficam de fora, e a ficha anota quais e por quê ("Ficou de fora"). Se as escolhas (vantagens + Equipamento + implantes) já passarem do orçamento, o contador fica amarelo e o servidor recusa com uma mensagem clara.

**Passar do dinheiro (modo Escolher):** o contador avisa (em amarelo) quanto passou e oferece duas saídas:
- **Pagar com pontos** (padrão): sobe para a condição financeira mais barata que cobre a compra, comprando Benefício (Riqueza). Esses PP saem do orçamento. A condição nunca desce, e um Trabalhador que sobe perde o PP extra que a Riqueza baixa dava.
- **Ficar devendo:** a ficha sai com a dívida anotada no dinheiro, para resolver na história.

Condições financeiras do faroeste: Trabalhador ($75, +1 PP), Classe média ($250), Em ascensão ($750, 1 PP), Próspero ($2.500, 2 PP), Rico ($10.000, 4 PP), Muito rico ($50.000, 6 PP). As do cyberpunk estão na seção do gênero. Num gênero com equipamento em pontos, o campo some.

**Teto do NP:** perícias, ataques e defesas podem chegar ao máximo do NP, mas é raro. A chance de escolher algo cai muito conforme ele se aproxima do teto, e o passo que o leva exatamente ao teto só é aceito com 1% de chance, ou quando não sobra outra opção.

## Como o gerador decide (NPCs)

1. **Ficha-base:** cada arquétipo tem faixas de NP com fichas reais dos livros. O gerador usa a de maior NP que cabe no NP escolhido. NPs abaixo da menor faixa não aparecem.
2. **Módulos candidatos:** os do arquétipo cujo `requisitos.np_min`/`np_max` aceitam o NP.
3. **Sorteio pelo estilo:**
   - `uniforme` (Aleatório): todos os módulos com o mesmo peso.
   - `preferencia` (Combate, Utilidade): módulos que listam o estilo pesam `peso_preferido` vezes mais.
   - `tematico`: só módulos temáticos, sem módulo extra, sem repetir o principal enquanto houver opções.

   Pode entrar um módulo extra compatível, com a chance `chance_extra` do estilo.
4. **Aplicação:** cada módulo `remove`, depois `substitui`, depois `adiciona`. Substituir algo que a ficha não tem torna o módulo inaplicável a ela.
5. **Validação:** se a ficha passar de algum limite do NP, a combinação é descartada. Depois de `tentativas_maximas`, o gerador desiste e explica os motivos.
6. **Variedade:** na primeira metade das tentativas, combinações já usadas no grupo são recusadas.

## Status de uma ficha

| Status | Quando |
|----|----|
| **Validada (regras implementadas)** | Todos os custos foram calculados pelo programa e todos os limites do NP conferidos. |
| **Custos calculados** | Limites conferidos, mas algum custo foi copiado da fonte (traços naturais do cavalo, implantes do Perfis de Poder). |
| **Custos parciais** | Há algo sem custo cadastrado ou marcado como `pendente`. |
| **Conceitual** | Há módulo só com descrição, sem números. |
| **Inválida** | Passa de algum limite. O gerador nunca entrega fichas assim. |

"Validada" quer dizer validada **pelas regras já implementadas**: custos de habilidades, defesas, perícias, vantagens e equipamento, e os limites do NP.

Módulos com `"status_dados": "ilustrativo"` têm números criados para o protótipo. O cartão avisa isso.

## Como cadastrar

### Novo gênero

1. Crie `dados/generos/<id>/genero.json` (veja **Gêneros**).
2. Copie os outros arquivos de um gênero parecido e troque o conteúdo. Todos são obrigatórios, menos `powers.json`.
3. Rode `python -m pytest` e abra a página: os erros de dados aparecem listados no topo.

### Novo módulo (`modules.json`)

```json
{
  "id": "domador",
  "nome": "Domador",
  "epiteto": "o Domador",
  "descricao": "Texto narrativo.",
  "tatica": "Como ele age em combate.",
  "tags": ["animais"],
  "estilos": ["utilidade", "tematico"],
  "arquetipos": ["capanga"],
  "papel": "ambos",
  "requisitos": {"np_min": 3},
  "adiciona": {
    "habilidades": {"Pro": 1},
    "pericias": {"Especialidade: Cavalgar": 4},
    "vantagens": {"Empatia com Animais": 1},
    "equipamento": ["faca"],
    "poderes": {"olhos": {"do_genero": "olhos_ciberneticos"}}
  },
  "substitui": {"equipamento": {"revolver_leve": "derringer"}},
  "remove": {"pericias": ["Intimidação"]},
  "incompativel_com": ["bruto"],
  "status_dados": "ilustrativo",
  "fonte": "De onde vieram os números"
}
```

- `papel`: `principal`, `extra` ou `ambos`.
- `status_dados`: `validado` (números de um livro), `ilustrativo`, `pendente` ou `conceitual`.
- Perícias usam os nomes do livro; as que têm especialização usam `"Perícia: tipo"`.
- Vantagens precisam existir em `vantagens.json` (detalhes entre parênteses são livres: `"Ambiente Favorito (deserto)"`).
- Todo equipamento citado precisa existir em `equipment.json`.
- Poderes: `{"do_genero": id}`, `{"catalogo": id, "graduacao": n}` ou um poder escrito à mão com `nome`, `nome_curto`, `custo_informado` e `ajustes`.

### Novo arquétipo (`archetypes.json`)

Copie um arquétipo existente e troque `id`, `nome`, `descricao`, `nomes` (lista em `names.json`), `np_maximo` e as `faixas`. Cada faixa tem `np`, `nome`, `fonte`, `status_dados`, `observacao` e a `ficha`.

### Novo equipamento (`equipment.json`)

Itens com `custo` em pontos de equipamento (e `preco` em dólares, nos gêneros com dinheiro). Armas têm `ataque` (`tipo`: `corpo`, `distancia`, `area` ou `percepcao`; `efeito`; `pericia`; `soma_forca`; `critico`; `multiataque`). Armaduras têm `protecao`, e `limitada_a` quando só valem contra um tipo de ataque.

## O que ainda não existe

- Magias do *Livro da Magia* (2ª edição: precisa passar pelo conversor para a 3e) e do *Supernatural Handbook*. Hoje a fantasia usa só magias do Perfis de Poder.
- Arranjos dinâmicos (2 PP por efeito alternativo) e efeitos Variável, Invocar e Transformar nas buscas automáticas.
- Mechas e veículos do Mecha & Mangá.
- Edição de arquétipos e módulos pela interface.
- Biblioteca de fichas salvas e imagens.
