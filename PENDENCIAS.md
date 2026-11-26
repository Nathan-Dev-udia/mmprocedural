# Pendências

Rascunho do que ficou para depois (atualizado na versão 1.19.0, em 25/11/2026).

## Livros
- **NP mínimo, nível da campanha e referência (feito na versão 1.19.0):** o bloco **Na ficha** de cada subclasse no Livro das Classes e a tabela de focos do apêndice de todos os gêneros mostram o NP mínimo, gerados dos dados (`nucleo/livros.py`); numa escola, só se for diferente do da subclasse. O passo a passo dos Livros do Jogador dos cinco gêneros explica o nível da campanha, o link com `?np=` e a referência do personagem no fim dos downloads.
- **Ainda falta nos livros:** a seção de panteões e divindades no Livro das Classes, a explicação das infusões do Artífice e a seção "Níveis de letalidade" no Livro do Mestre (detalhes nas seções abaixo). O Livro do Mestre ainda não fala do nível da campanha; vale uma linha onde ele explica como escolher o NP.
- **Chamado de Cthulhu:** o Livro do Jogador (`dados/livros/cthulhu_jogador.md`) e o Livro do Mestre (`dados/livros/cthulhu_mestre.md`) foram publicados em `dados/livros/`, integrados aos testes e ao download `.docx`, e aguardam leitura editorial do usuário.
- **Cyberpunk:** os dois livros foram revisados, corrigidos e publicados em `dados/livros/`. A ficha da moto do clã, as descrições de equipamento, complicações, limites de NP, custos e opções de compra foram alinhados aos dados e ao gerador.
- **Faroeste:** revisão contra o gerador concluída. Os livros explicam comida, lotes, carga e montaria, o dinheiro guardado no sorteio, a dívida e a distribuição de pontos (nova seção 15 do Livro do Jogador). O exemplo do Jesse inclui as rações e a carga, e a tabela de locomoção usa as Velocidades do catálogo. Preços e pesos das tabelas batem com o `equipment.json`. Os livros ainda aguardam leitura editorial do usuário.
- **Carga no gerador do faroeste (resolvido):** com montaria, o que passa da carga leve e não se usa no corpo (rações, ferramentas, bebida) vai no animal (`nucleo/validator.py`). Os PJs começam com Força 1 (`forca_minima` no `genero.json`), exceto o Jogador de Pôquer e o Médico de Fronteira; no NP 2, a Força fica em 0 quando passaria do limite do NP (a baioneta do veterano). Sobram com carga pesada só alguns jogadores de pôquer e médicos sem cavalo, por 1 ou 2 kg. Os livros do faroeste foram atualizados.
- **Dados do faroeste:** o `equipment.json` continua sendo a fonte da verdade (não há script gerador, como na fantasia); os testes de `test_player.py` conferem peso em kg, preço e comércio de todos os itens. Os pesos marcados como estimados (kits, chapéus, baioneta, cartucheira) não vêm do livro.
- **Fantasia:** revisão mecânica concluída. Custos de poderes, Axii, o exemplo de Sariel, poção de cura, complicação fixa, armaduras e exemplo do mago rúnico foram alinhados ao catálogo e ao código. Os livros ainda aguardam leitura editorial do usuário.

## Regras e dados da fantasia
- **Armaduras:** as graduações de Proteção seguem as equivalências adotadas do Manual dos Mecanismos Lite; os preços permanecem conversões do gênero. As fichas-base de hobgoblin e soldado usam cota de malha para continuar válidas com a meia-armadura em Proteção 5.
- **Fichas incomuns mas válidas:** podem surgir combinações que não pareçam adequadas ao conceito, como um Campeão com Presença 4 ou um bugbear NP 7 com Furtividade +16. Ajustar manualmente quando o resultado não combinar com a cena.
- **Mago rúnico:** o foco pode priorizar Runas e Prestidigitação em vez de uma perícia de ataque mágico; o livro agora explica como priorizar magia manualmente.

## Divindades da fantasia (versão 1.14.0)
- **Feito:** panteões grego, nórdico, egípcio e maia em `dados/generos/fantasia/divindades.json`, só com deuses de mitologias em domínio público (nada de D&D nem Pathfinder). A divindade não dá pontos: ela direciona a arma (principal no clérigo ou quando já é principal da classe; de reserva nas outras), as perícias (no fim das prioridades da classe), o treino da arma (mesmo em quem ataca com magia) e o dogma, que entra como complicação extra. É obrigatória só no clérigo, que só pode ter um domínio do seu deus; nas outras classes o padrão é "Sem divindade".
- **Livro das Classes:** falta uma seção sobre os panteões e as divindades (como escolher, o que cada deus muda na ficha, a lista por panteão com domínios, arma e dogma).
- **Domínios do compêndio (feito na versão 1.16.0):** Natureza, Forja, Sepultura, Arcanismo, Ordem, Paz e Crepúsculo viraram subclasses do clérigo, e `dominios_pendentes` no `divindades.json` ficou vazio. Se um domínio novo for planejado antes de existir, ele entra nessa lista (o carregador acusa erro se ficar nos dois lugares). O panteão maia declara `dominios_ausentes: ["forja"]`: o clérigo maia não pode ser da Forja. O rascunho de cada um (conceito, vantagens, perícias, magias novas necessárias) está em `dados/generos/fantasia/subclasses_compendio.json` (o gerador não lê esse arquivo; é o catálogo de apoio feito a partir do `referencias/dd/compendio-de-classes-e-subclasses.pdf`).
- **Panteão maia sem Forja:** de propósito (a metalurgia chegou tarde à região). Völund entrou no nórdico como herói ferreiro, não deus.
- **Mais panteões:** celta e eslavo seriam os próximos candidatos. Evitar religiões vivas (orixás, deuses hindus).
- **Catálogo do compêndio:** o `subclasses_compendio.json` só tem o Clérigo. As subclasses das outras classes entraram direto no gerador (versões 1.15 a 1.17), então catalogar o resto serve só como documentação de apoio; não bloqueia nada.

## Classes e subclasses do compêndio
Comparação do `referencias/dd/compendio-de-classes-e-subclasses.pdf` com o gerador. Equivalentes com outro nome contam como existentes: Caminho da Besta = Coração de fera, Adepto das Sombras = Linhagem sombria, Feiticeiro da Tempestade = Alma da tempestade, Mentor = Mestre da intriga, Perseguidor Obscuro = Perseguidor sombrio. A Lâmina Maldita ficou de fora por ser parecida com o Pacto da lâmina. A "Besta do Mar" do compêndio é um animal companheiro do Mestre das Bestas, não uma subclasse.

| Classe | Falta no gerador | Qtd. | Situação |
|---|---|---|---|
| Artífice | A classe inteira, mais Alquimista, Armeiro, Artilheiro e Ferreiro de Batalha | 1 + 4 | **feito** (versão 1.17.0) |
| Clérigo | Natureza, Forja, Sepultura, Arcanismo, Ordem, Paz, Crepúsculo | 7 | **feito** (versão 1.16.0) |
| Guerreiro | Arqueiro Arcano, Samurai, Ginete, Cavaleiro do Eco, Cavaleiro Psiônico, Cavaleiro Rúnico | 6 | **feito** (versão 1.15.0; o Ginete entrou como Porta-estandarte, porque é o Cavaleiro Dragão Púrpura, não um cavaleiro montado) |
| Mago | Invocação, Mago da Guerra, Cronurgia, Graviturgia, Ordem dos Escribas | 5 | **feito** (versão 1.15.0) |
| Bárbaro | Fúria de Batalha, Arauto da Tempestade, Fanático, Caminho da Magia | 4 | **feito** (versão 1.15.0) |
| Ladino | Inquiridor, Batedor, Fantasma, Lâmina da Alma | 4 | **feito** (versão 1.16.0) |
| Monge | Kensei, Morte Extensa, Misericórdia, Eu Astral | 4 | **feito** (versão 1.15.0) |
| Paladino | Redenção, Glória, Vigilantes, Quebrador de Juramento (bom para vilões) | 4 | **feito** (versão 1.16.0) |
| Bruxo | Eterno, Abissal, Gênio | 3 | **feito** (versão 1.16.0) |
| Patrulheiro | Andarilho do Horizonte, Exterminador de Monstros, Protetor do Enxame | 3 | **feito** (versão 1.16.0) |
| Bardo | Eloquência, Criação | 2 | **feito** (versão 1.16.0) |
| Feiticeiro | Alma Favorecida, Alma Mecânica | 2 | **feito** (versão 1.16.0) |
| Druida | Círculo dos Sonhos | 1 | **feito** (versão 1.16.0) |

- **Artífice (versão 1.17.0):** classe nova com as vantagens Artífice e Inventor, Tecnologia e a tradição **Infusões de artífice** (Elixir experimental, Canhão arcano, Manoplas trovejantes; Defensor de aço e Servo homúnculo ficam fora do arranjo, como o Companheiro animal). Conferir na mesa. O Livro do Jogador e o do Mestre só citam a classe na tabela e na contagem; uma explicação maior das infusões pode entrar na próxima revisão dos livros.
- **Magias novas da versão 1.16.0** (conferir na mesa): Olhos da noite (Crepúsculo, visão no escuro fora do arranjo), Lâmina psíquica (Lâmina da alma, usa Adagas), Tentáculo das profundezas (Abissal) e Enxame (Protetor do enxame). As outras 22 subclasses da versão reaproveitam magias que já existiam.
- **Magias novas da versão 1.15.0** (conferir na mesa se não ficaram fortes demais): Flecha arcana (Arqueiro arcano, disparada com o arco), Aura da tempestade (Arauto da tempestade, dano em área sem ataque, só em fúria), Braços do eu astral (Eu Astral, usa Briga), Estase momentânea (Cronurgia), Pressão gravitacional (Graviturgia) e Invocar elemental (Invocação, fora do arranjo).

## Ficha de jogador: NP mínimo, nível da campanha e referência
- **Referência do personagem (versão 1.18.0):** o PDF, o DOCX e o TXT terminam com o que cada vantagem, poder e item faz, o teste do alvo com as CDs, quanto custa subir uma graduação e os termos de regra citados (`nucleo/referencia.py` e `nucleo/referencia_pdf.py`). Os resumos de efeitos, modificadores e condições foram escritos para o projeto: vale uma leitura. As vantagens usam o resumo curto de `dados/comum/vantagens.json`; algumas ficam vagas (Ataque Acurado, por exemplo), e um campo de regra completa ajudaria.
- **NP mínimo por subclasse (versão 1.19.0):** o menor NP em que todos os poderes essenciais cabem nos 35% do orçamento reservados aos poderes (`player.np_minimo`). Hoje: caçador de monstros e Círculo da Lua no NP 4; Ilusão, Adivinhação, Invocação, ferreiro de batalha e olho da rede no NP 3. `"np_minimo"` no `player.json` (classe, subclasse ou variante) pode pedir mais. A medição de força feita na mesma revisão não achou subclasse apelona: no mesmo NP, as fichas ficam entre ~0,7 e ~1,3 da mediana, conforme o papel.
- **Nível da campanha (versão 1.19.0):** campo opcional no primeiro passo. Preenchido, trava o NP e desabilita o que não cabe; em branco, deixa tudo liberado com aviso e só avança num NP válido. Fica lembrado por gênero, e `?np=5` no endereço já abre nele.
- **Fonte da página de referência (para revisar):** o novo visual da página (logo, cabeçalho, cartões de vantagens, quadros arredondados) usa Helvetica nos títulos e no texto. A ficha usa a fonte em quadrinhos NewsflashBB, que está embutida só em parte no modelo `dados/comum/ficha_editavel.pdf` (só os caracteres usados) e é comercial, então não dá para reaproveitar. Para ficar mais próximo do desenho, escolher uma fonte livre parecida (condensada, em caixa alta, estilo gibi, como Bangers, Anton ou Oswald, todas sob licença aberta), embutir o `.ttf` no projeto e registrá-la no reportlab para os títulos. Conferir também que ela tem os acentos do português. O campo "Identidade" do cabeçalho sai em branco, porque o gerador não tem esse dado.
- **Aard:** a estatística diz "superada por Fortitude", mas o ataque calculado sai contra Vontade. Conferir qual dos dois está certo em `dados/generos/fantasia/powers.json`.
- **Cyberpunk:** os implantes também custam eurobucks; numa condição financeira baixa, um implante essencial ainda pode ficar de fora no sorteio. Depende do dinheiro, não do NP.

## Ideias novas (25/11/2026)
- **Deuses de D&D:** adicionar um panteão com os deuses de D&D em `dados/generos/fantasia/divindades.json`. Atenção: a decisão da versão 1.14.0 foi usar só mitologias em domínio público. Os nomes e as descrições dos deuses de D&D são conteúdo protegido (os Reinos Esquecidos, por exemplo), então vale decidir se entram só os nomes, ou como panteão opcional e separado, antes de começar.
- **Melhorar a folha de descrição:** a página de referência do personagem (`nucleo/referencia.py`) pode ficar mais completa, sobretudo nos itens e habilidades. Ponto de partida: as vantagens usam só o resumo curto de `vantagens.json`; um campo de regra completa ajudaria.
- **Pets e companheiros:** o personagem pode ter um pet, e o pet ganha ficha própria no PDF, DOCX e TXT (cavalo no Faroeste e na Fantasia, entre outros). O desenho completo, com as opções a decidir, está na seção "Pets e companheiros (desenho)" logo abaixo.
- **Livro das Magias (para baixar):** um livro por gênero com magia (`fantasia_magias.md` e `escola_de_magia_magias.md`, este com os 57 feitiços), gerado dos dados em `nucleo/livros.py`, como o Livro das Classes, para acompanhar qualquer magia nova sem trabalho manual. Cada magia traz efeito e graduação, custo em PP, teste do alvo com a CD, modificadores, custo de subir uma graduação e quais classes ou subclasses a usam. Aparece junto dos outros livros no passo do gênero, nos mesmos formatos de download. A decidir: agrupar por classe, por escola ou em ordem alfabética; se entram as magias só para NPC (as Maldições Imperdoáveis); um equivalente para os implantes do Cyberpunk fica para depois.
- **Fichas de grupo:** gerar o grupo inteiro de uma vez, com papéis que se complementam (por exemplo tanque, curandeiro, furtivo e conjurador), todos no mesmo NP da campanha, e baixar tudo junto no zip. Usa o nível da campanha que já existe. A decidir: quantos personagens (de 2 a 6), se o jogador trava alguns papéis e deixa o resto sortear, e se o grupo evita repetir classe e raça.
- **Aviso de equilíbrio na ficha:** um alerta quando a ficha foge muito da mediana do NP (a medição da versão 1.19.0 mostrou que as subclasses ficam entre ~0,7 e ~1,3 da mediana, então o aviso pegaria só fichas fora do comum ou editadas à mão). Aproveita a medição de força que já foi feita.
- **Código de ficha montado por IA:** o usuário descreve o personagem para uma IA (Claude, Gemini, NotebookLM), cola junto uma documentação do sistema, recebe um código e o cola no app para gerar a ficha. O desenho está na seção "Código de ficha montado por IA (desenho)" mais abaixo.

## Pets e companheiros (desenho)
Desenho para o personagem ter um pet e o pet ganhar ficha própria. Partiu de uma pesquisa no NotebookLM
(`referencias/conv.txt`), conferida contra a 3ª edição e contra o que o projeto já tem.

### O que já existe no projeto
- **Vantagens:** Capanga (15 PP de ficha por graduação) e Parceiro (5 PP de ficha por graduação) em `dados/comum/vantagens.json`.
- **Poder:** o perfil "Companheiro animal" (Invocar, Heroico, Movimentação Individual) em `dados/comum/poderes/perfis_de_poder.json`.
- **Animais à venda:** pônei, cavalo de montaria, de guerra e de tração e mastim em `dados/generos/fantasia/equipment.json`; cavalo e sela no `equipment.json` do Faroeste, com itens marcados `vai_na_montaria` (a carga já pressupõe o cavalo).
- **Fichas prontas:** cavalo de guerra, lobo, lobo atroz e urso em `dados/bestiario/fantasia/feras/`. O Faroeste não tem ficha de cavalo no bestiário.

### O que corrigir na pesquisa do NotebookLM
- *Mecha & Mangá* e *Warriors & Warlocks* são da 2ª edição, e os custos tirados deles não valem. O "Lobo, 23 PP"
  por acaso bate com o lobo da 3e (Guia do Mestre, p. 227), mas a fonte certa é o Guia.
- Elo Telepático, Interpor Monstrinho e Ordem Rápida não são vantagens da 3e. Se entrarem, entram como **regra da casa**, marcadas assim no livro. A vantagem que existe é Interpor-se, em que o herói se joga na frente do aliado.
- ~~Ordem como ação de movimento falta conferir~~ **Confirmado:** Comandar é ação de movimento (Livro Básico, p. 188).

### Fontes (todas em `referencias/mm/`, 3ª edição)
Não precisa de referência externa. Os livros de M&M 3e que já temos cobrem regras, custos e fichas; D&D serve só
para conceito.

| Livro (arquivo) | Seção | O que usamos |
|---|---|---|
| Livro Básico (`mutantes malfeitores 3a edicao.pdf`) | Vantagem Parceiro, p. 85 | 5 PP de ficha por graduação; não segue as regras de capanga; **o total de PP do parceiro tem de ser menor que o do herói**; parceiro não tem pontos heroicos |
| Livro Básico | Vantagem Capanga, p. 81; Capangas, p. 186 | 15 PP de ficha por graduação; regras de capanga (cai na primeira falha de Resistência); perdidos são repostos entre aventuras |
| Livro Básico | Efeito Invocar, p. 111 | familiar e companheiro mágico; extras Ativo (age sem a condição tonto) e Capangas Múltiplos (dobra a quantidade) |
| Livro Básico | Ação Comandar, p. 188 | dar ordem ao pet é ação de movimento |
| Livro Básico | Crescimento, p. 100; perícia Veículos | ajustar porte (pônei, mastim, pantera); **montar é Especialidade: Cavalgar, com Agilidade** (Atletismo só a critério do mestre), regra que o projeto já usa |
| Guia do Mestre de Jogo (`Guia do Mestre de Jogo.pdf`) | Capítulo Animais, p. 223 a 229 | fichas prontas da 3e com o total de PP (tabela abaixo); variações (cavalo de carga +1 For, de guerra mais Luta); o Guia sugere Atletismo para montar, mas vale a regra do Livro Básico (Cavalgar) |
| Supernatural Handbook (`Mutants & Masterminds 3e - Supernatural Handbook.pdf`) | Cap. 2, modelo Familiar (homúnculo, 39 pontos), p. 45 | base de poderes do familiar mágico do mago (é um familiar independente, então é encolhido para caber como Parceiro ou Invocar) |
| D&D 5e (`referencias/dd/`: Manual dos Monstros, Livro do Jogador) | Apêndice de feras; Patrulheiro (Mestre das Bestas); magia Encontrar Familiar | **só conceito**: que bichos existem e como o companheiro se comporta na história. Os números não convertem para M&M |

Cuidado: o *Livro de Magia* (`mutantes malfeitores o livro de magia.pdf`) cita "cavalo (M&M, página 230)", que é
da 2ª edição; não usar os números de lá.

### Fichas e custos (Guia do Mestre de Jogo, 3e)
Custo como **Parceiro** = total ÷ 5, arredondado para cima. Como **Capanga** = total ÷ 15, arredondado para cima.
Os totais são os impressos no Guia; na hora de criar o JSON, recalcular com `validator.calcular_custos` e usar o
nosso número se o livro tiver erro.

| Animal | Página | NP | Total (PP de ficha) | Parceiro (PP do herói) | Capanga (PP do herói) |
|---|---|---|---|---|---|
| Cão | 223 | 2 | 10 | 2 | 1 |
| Cavalo | 223 | 3 | 9 | 2 | 1 |
| Coruja | 224 | 2 | 19 | 4 | 2 |
| Gato | 226 | 3 | 15 | 3 | 1 |
| Falcão (e outras aves de rapina) | 226 | 4 | 38 | 8 | 3 |
| Lobo | 227 | 3 | 23 | 5 | 2 |
| Rato | 227 | 3 | 12 | 3 | 1 |
| Macaco | 228 | 3 | 24 | 5 | 2 |
| Morcego | 228 | 0 | 15 | 3 | 1 |
| Leão | 227 | 6 | 48 | 10 | 4 |
| Urso | 229 | 6 | 36 | 8 | 3 |

**Derivados (não estão no Guia), montados a partir de uma ficha da 3e e com custo recalculado:**
- **Mastim:** do Cão, com +1 For e +1 Vig e sem Encolhimento.
- **Mula:** do Cavalo, como cavalo de carga (+1 For, regra do Guia), com Velocidade menor.
- **Pônei:** do Cavalo, com Crescimento menor.
- **Cavalo de guerra:** o do bestiário (`cavalo_guerra.json`, já adaptado do Guia, p. 223).
- **Pantera:** do Leão, com menos Crescimento e mais Furtividade.
- **Sapo:** do Rato, com Salto e Natação no lugar do Faro.
- **Familiar do mago:** um animal pequeno (coruja, gato, rato, morcego ou sapo) mais um pacote mágico tirado do
  modelo Familiar do Supernatural Handbook. O elo com o dono sai do efeito Comunicação (mental, limitado ao dono),
  com custo real em PP, em vez de uma vantagem da casa. Conferir o custo do pacote no Livro Básico.
- As fichas atuais de `lobo.json` e `urso.json` no bestiário devem ser comparadas com o Guia para não haver duas
  versões do mesmo bicho.

### As quatro formas de ter um pet
| Forma | Custo | Força do pet | Em combate | Uso |
|---|---|---|---|---|
| **Animal comprado** | dinheiro, 0 PP | ficha fixa do bestiário | o mestre controla; pode fugir quando ferido | cavalo de viagem, mula, cão de guarda |
| **Parceiro** | 1 PP por graduação = 5 PP de ficha | resiste como herói (não é capanga) | age sob comando do jogador | o "pet principal": cão de combate, montaria de elite |
| **Capanga** | 1 PP por graduação = 15 PP de ficha | capanga: cai na primeira falha de Resistência | age sob comando do jogador | matilha, falcões batedores, vários bichos fracos |
| **Invocar** | 2 PP por graduação (+1 com Heroico) | 15 PP de ficha por graduação | aparece com uma ação padrão | familiar, espírito animal, companheiro mágico |

**Recomendação:** o jogador escolhe entre **Nenhum**, **Animal comprado** e **Parceiro**. Capanga e Invocar ficam para as subclasses que já pedem companheiro (Mestre das Bestas, druida, familiar do mago), em que vêm automáticos no lugar de escolha.

### Opções a decidir
1. **Onde entra nos passos de criação.**
   - (a) Passo próprio "Companheiro", opcional, depois do equipamento. **Recomendado:** não pesa nos passos que já existem e dá espaço para mostrar a ficha do bicho.
   - (b) Um campo dentro do passo da classe.
2. **Quanto PP o Parceiro custa.**
   - (a) O jogador escolhe o animal e o gerador calcula a graduação (custo da ficha ÷ 5, arredondado para cima). **Recomendado:** é mais fácil de entender.
   - (b) O jogador escolhe a graduação e o gerador monta o melhor animal que cabe.
3. **Limite para não ficar apelão.**
   - NP do pet ≤ NP do herói, e o total de PP do Parceiro menor que o do herói (Livro Básico, p. 85).
   - Teto de custo em PP do herói, por exemplo 15% a 20% do orçamento. Um cavalo de guerra de 30 PP custa 6 PP do herói, cerca de 8% no NP 5.
   - Animal que passa do teto aparece desabilitado com "(a partir do NP X)", como as subclasses.
4. **Sorteio ou escolha.**
   - O jogador escolhe ou deixa sortear pelo arquétipo: patrulheiro → lobo ou falcão; cavaleiro → cavalo de guerra; caçador de monstros → cavalo; mago → familiar; pistoleiro do Faroeste → cavalo.
5. **Cavalo automático no Faroeste.**
   - (a) Todo personagem já sai com um cavalo comprado, porque a carga `vai_na_montaria` pressupõe. **Recomendado.**
   - (b) O cavalo continua sendo só um item a comprar.
6. **Evolução na campanha.** O Parceiro sobe comprando mais graduações (+5 PP de ficha cada). O livro explica; o gerador pode aceitar "pontos extras para o pet" no futuro.
7. **Montaria.** Montar usa **Especialidade: Cavalgar, com Agilidade** (Livro Básico, perícia Veículos; já está em `rules.py` e nos livros da Fantasia, seção 9.8, e do Faroeste). Atletismo fica a critério do mestre. Falta decidir: a carga do cavalo some do peso do personagem?
8. **Regras da casa opcionais.** Truques treinados (Atacar, Defender, Buscar, Ficar, Rastrear, Proteger) para animais de Intelecto -4 ou -5, e ordem como ação livre com uma vantagem da casa. Ficam marcadas como opcionais.

### Pets por gênero (fichas a criar ou converter)
- **Fantasia:** cão e mastim, falcão, coruja, gato, pantera, mula, pônei e cavalo de montaria (o cavalo de guerra, o lobo, o lobo atroz e o urso já existem). Fonte: Guia do Mestre e derivados acima.
- **Faroeste:** cavalo de montaria, mula e cão. Fonte: Guia do Mestre, p. 223.
- **Escola de Magia:** coruja, gato e sapo, os bichos de estimação dos alunos. Quase sempre comprados, sem PP. Fonte: Guia do Mestre (coruja e gato) e sapo derivado do rato.
- **Chamado de Cthulhu:** cão. Fonte: Guia do Mestre, p. 223.
- **Cyberpunk:** cão robô ou drone, que pode ser outro tipo de companheiro (equipamento) e fica para depois.

### Saída da ficha
- Página extra **"Companheiro"** no PDF, antes da referência do personagem, com habilidades, defesas, ataques, perícias e poderes do pet.
- No DOCX e no TXT, uma seção igual.
- A referência do personagem também explica os poderes e as vantagens do pet, e a vantagem usada (Parceiro ou Capanga).

### Ordem sugerida de implementação
1. Fichas dos pets com o custo em PP calculado e testado (base de tudo). **Feito o básico:** os pets ficam em
   `dados/comum/companheiros/` no formato de ficha do validador (não no bestiário, que guarda só valores finais),
   lidos por `nucleo/companheiros.py`; Crescimento e Encolhimento são aplicados pela regra do Livro Básico.
   `tests/test_companheiros.py` confere cada pet contra os valores impressos no Guia e contra os limites do NP.
   Cadastrados: cão, cavalo, coruja e lobo (todos batem com o Guia). Faltam os outros animais da tabela e os
   derivados; o gato, o rato e o macaco pedem suporte a "Atletismo baseado em Agilidade" (vantagem Benefício), e o
   rato e o falcão têm contas do Guia que não fecham (registrar a divergência ao cadastrar).
2. Animal comprado: escolha nos passos de criação, desconto do dinheiro e página "Companheiro" no PDF, DOCX e TXT.
3. Parceiro com PP: custo, teto e desabilitar o que não cabe.
4. Cavalo automático no Faroeste e sorteio por arquétipo.
5. Companheiro automático nas subclasses (Capanga ou Invocar).
6. Livros: seção de pets no Livro do Jogador de cada gênero e as regras da casa no Livro do Mestre.

## Código de ficha montado por IA (desenho)
Ideia: o usuário pede, em linguagem natural, algo como "um mago de combate com foco em furtividade, misturando mago
com ladrão". A IA lê a documentação do sistema e devolve um código, o usuário o cola no app e a ficha sai pronta.
Não tem custo de API para o projeto e funciona com a IA que o usuário já usa.

### Por que não serve a semente atual
- A semente que o app já aceita (`semente` em `app.py`, `_rng`) só alimenta o `random.Random`. É um número opaco:
  nenhuma IA consegue calcular qual semente gera um "mago furtivo". Ela inventaria um número e o resultado sairia
  aleatório, parecendo proposital.

### O formato: um código que descreve as escolhas
- O código lista as escolhas da ficha, como uma receita. A semente vai junto só para reproduzir a mesma ficha:
  `MMP1 fantasia | mago/combate | np8 | pericias:furtividade+,enganacao+ | vantagens:ataque_furtivo | semente:4821`
- A documentação não é um catálogo de fichas prontas, é o **vocabulário de peças** (gêneros, arquétipos, focos,
  perícias, vantagens, poderes, com os IDs). A IA combina as peças na hora, então nenhuma combinação precisa ser
  cadastrada antes.
- Texto legível, não base64: o usuário consegue ler e corrigir, e LLMs erram muito ao codificar base64.
- Prefixo com versão (`MMP1`), para que códigos antigos continuem valendo quando o formato mudar.

### Partes
1. **Formato e leitor do código:** definir a gramática, ler o código e convertê-lo nos parâmetros de
   `player.gerar_personagem` (arquétipo, foco, NP, vantagens manuais etc.).
2. **Validação tolerante:** a IA vai errar IDs. O erro deve dizer o que está errado e sugerir os parecidos
   ("vantagem `ataque-furtivo` não existe; parecidas: `ataque_furtivo`"), para o usuário colar o erro de volta na IA.
3. **Campo "Colar código" nos passos de criação** e botão **"Copiar código"** em toda ficha gerada. O caminho inverso é útil
   mesmo sem IA: gerar, gostar da ficha e compartilhar o código.
4. **Documentação gerada dos dados:** uma ferramenta em `ferramentas/` exporta um `.md` por gênero a partir de
   `dados/`, com o formato, os IDs válidos, uma linha sobre cada peça e exemplos de pedido → código. Feita à mão,
   ela desatualiza e a IA passa a sugerir IDs que não existem. Disponível para baixar junto dos livros.
5. **Pesos para híbridos:** hoje o gerador trabalha com arquétipo + foco. Para uma mistura de verdade (mago que
   "puxa" para furtividade), o código precisa de prioridades (`pericias:furtividade+`) que o motor respeite ao
   distribuir os pontos. Sem isso, a IA só escolhe o arquétipo mais próximo e força algumas vantagens.

### Cuidados para não quebrar o motor
- **Sempre passar por `player.gerar_personagem`.** O leitor só traduz o código para os parâmetros que a função já
  aceita; nunca monta a ficha por fora. Assim continuam valendo todas as verificações atuais (NP mínimo, orçamento
  de PP, itens além do dinheiro, vantagens manuais). Colar um código equivale a preencher os passos de criação.
- **O código guarda o resultado dos sorteios, não só a semente.** Se guardar só a semente, qualquer mudança em
  `dados/` (uma vantagem nova, por exemplo) muda a sequência de sorteios e o mesmo código passa a gerar outra ficha.
  O "Copiar código" grava foco, variante, raça, divindade, vantagens e equipamento que saíram; a semente cobre só o
  que sobrar.
- **Sem pesos, comportamento idêntico bit a bit.** O código dos pesos não pode fazer nenhuma chamada extra ao `rng`
  quando não há pesos, porque isso desloca todos os sorteios seguintes. Os testes atuais usam sementes fixas
  (`random.Random(42)` etc.) e têm de passar **sem nenhum ajuste**; se um teste antigo precisar mudar, algo vazou.
- **Peso empurra, não manda.** O peso só aumenta a chance de uma perícia ou vantagem ser escolhida. Orçamento de PP,
  limites do NP e custos continuam os mesmos.
- **Testes novos:** um código colado gera a mesma ficha que os passos de criação com as mesmas escolhas; copiar o código de uma
  ficha e colá-lo de volta gera a ficha idêntica (ida e volta); códigos inválidos dão erro claro, nunca exceção.

### Cuidados para não quebrar o conceito do personagem
- **O núcleo da classe é intocável.** Os poderes, perícias e vantagens fixos do arquétipo e do foco entram sempre; os
  pesos só agem sobre os pontos livres. Um "mago furtivo" continua sendo mago, com a magia de combate do foco, e
  ganha furtividade com o que sobra.
- **Teto para o peso.** Os pontos puxados por pesos para fora do perfil da classe têm um limite (por exemplo, uma
  fração dos pontos livres), para o híbrido não esvaziar a função principal.
- **Pedido incoerente vira aviso, não ficha estranha.** Se o código pede algo que a classe não pode ter (uma
  vantagem restrita, um poder de outro arquétipo), o app avisa e sugere o arquétipo ou foco que tem aquilo, em vez
  de gerar uma ficha que contradiz a classe.
- **Medição de força.** Rodar a medição da versão 1.19.0 com fichas pesadas e conferir que ficam na faixa de ~0,7 a
  ~1,3 da mediana do NP. Combina com o "Aviso de equilíbrio na ficha" das ideias novas.
- **Documentação para a IA explica os limites.** O `.md` diz o que é fixo em cada classe e até onde os pesos vão,
  para a IA não prometer ao usuário uma mistura que o motor não entrega.

### A decidir
- Quais campos o código aceita na primeira versão (só o que os passos de criação já têm, ou já com os pesos).
- O que fazer com um código parcialmente válido: recusar ou gerar ignorando as peças erradas, com aviso.
- Se a documentação para a IA sai num arquivo por gênero ou num arquivo único.
- Ordem sugerida: partes 1 a 4 primeiro (já funcionam com o que o motor tem hoje), a 5 depois.

## Aventuras a serem criadas
- **Horror moderno: Vampiro: A Máscara e Delta Green (um gênero só):** juntar os dois num mesmo gênero de horror moderno, com agentes federais (Delta Green) e vampiros (Vampiro: A Máscara), mais as aventuras de cada um. A base é a pasta `dados/generos/delta_green/` (só `PREPARACAO_GENERO.md` por enquanto) e o Cthulhu inteiro (Sanidade d100, bestiário do Mythos, escudo). Falta decidir como o lado vampírico entra: clãs e disciplinas viram arquétipos/focos com poderes, e a Fome e a Humanidade precisam de uma regra de condição própria. Seguir a regra do projeto: para a mesa não há problema usar os nomes; se o projeto virar público, nome, termos e personagens têm de ser próprios (`dados/generos/IDEIAS_DE_TEMAS.md`).

## Escudo do Mestre
- **Fantasia, Faroeste, Cthulhu e Cyberpunk:** feitos (aba no site, impressão, PDF e planilha). Conteúdo em `dados/escudo/<gênero>.json`; o de Cthulhu e o de Cyberpunk são gerados por `ferramentas/criar_*_escudo.py` (edite o script, não o JSON). O do Cyberpunk resume o Livro do Mestre do gênero em 11 abas (uma página de PDF cada), com armas e modos de disparo, lesões críticas, Humanidade, NET, dinheiro e reputação; queda, tempo de viagem, veículos/montarias, carga e medidas são calculados dinamicamente em `nucleo/escudo.py`.
- **Impressão pelo navegador:** a aba Viagem ocupa duas folhas. O PDF baixado tem uma página por aba (teste `test_regras_gerais_seguem_o_livro_basico`).
- **Letalidade escolhível:** Heroica, Equilibrada ou Mortal, num seletor da aba (vale para PDF e planilha). As tabelas de dano, Aflição e recuperação são geradas por `nucleo/escudo.py`; o que muda por gênero fica em `"letalidade"` no JSON do escudo. Os livros ainda descrevem só o modo padrão de cada gênero; uma seção "Níveis de letalidade" no Livro do Mestre fica para quando os livros forem revistos.
- **Regras gerais dos escudos (resolvido):** ações, manobras, condições, dano, Aflição, pontos heroicos e Tratamento vêm de `ferramentas/escudo_mm.py`, conferido com o livro básico e com os Livros do Mestre. O script do Cthulhu usa o módulo; o `faroeste.json` foi corrigido com ele (as linhas próprias do faroeste, como tipos de disparo e recuperação por hora, saem do Livro do Mestre do gênero). A Aflição do faroeste voltou a ter o 4º grau, marcado [Casa], como no livro. O Cyberpunk já seguia o livro, e a fantasia estava certa.

## Gênero Chamado de Cthulhu (anos 20)
- **Implementação base concluída:** gerador de gênero ativado com dados completos (`dados/generos/cthulhu/` contendo `genero.json`, `equipment.json`, `player.json`, `archetypes.json`, `modules.json`, `complications.json`, `names.json`).
- **15 Ocupações clássicas e 6 faixas de crédito/riqueza:** Professor, Detetive, Médico, Jornalista, Antiquário, Veterano, Policial, Bibliotecário, Diletante, Membro do Clero, Escritor, Parapsicólogo, Enfermeira, Advogado e Criminoso.
- **Mecânica de Sanidade d100 integrada (`nucleo/sanidade.py`):** cálculo inicial derivado de Vontade (`45 + 5 * Vontade`, teto 99 reduzido por Mythos), rolagem d100 (01 sucesso automático, 100 desastre / 96-100 para SAN < 50, perda >= 5 com teste de Intelecto CD 10 para insanidade temporária, perda no dia >= 20% para insanidade indefinida).
- **Página 3 no PDF da Ficha (Registro de Sanidade):** implementada em `nucleo/sanidade_pdf.py` e anexada automaticamente em `nucleo/pdf_export.py`. Traz contador visual de 00 a 99, estatísticas vitais, regras resumidas de Sanidade, tabela d10 de Acessos de Loucura, registro diário de Sanidade (ponto de ruptura), registro de Fobias e Manias, e diário de Criaturas e Tomos do Mythos. Cabe numa folha mesmo com complicações longas.
- **Escudo do Mestre (Site, PDF e XLSX):** 8 abas especializadas em `dados/escudo/cthulhu.json` cobrindo testes investigativos, combate nos anos 20, condições, aba dedicada de Sanidade & Horror, viagens e veículos de 1920 (Ford Modelo T, Packard, trem), perigos/explosivos e serviços da metrópole (hotéis, hospitais, speakeasies).
- **Testes automatizados:** `tests/test_cthulhu.py` e `tests/test_escudo.py` com validação de dados, cálculos, geração de PDFs, planilhas e rotas web. Na revisão de 12/11/2026 a suíte tinha 469 testes, todos passando.
- **Bestiário do Mythos integrado ao sistema de Bestiário (`dados/bestiario/cthulhu/`):**
  - 7 criaturas cadastradas sob regras estritas de M&M 3e e testadas de NP 1 a 20:
    1. Cultista Iniciado (NP 2, Humanoide, Lacaio, padrão da família Cultista)
    2. Cultista Fanático (NP 3, Humanoide, Bruto / Lacaio)
    3. Sumo Sacerdote do Culto (NP 5, Humanoide, Líder / Conjurador / Chefe)
    4. Carniçal dos Mythos (NP 4, Aberração, Emboscador / Lacaio)
    5. Profundo (NP 5, Aberração, Soldado / Predador)
    6. Mi-Go (NP 6, Aberração, Conjurador / Voador)
    7. Shoggoth (NP 9, Aberração, Bruto / Chefe Solo, Tamanho Enorme)
  - Filtro por gênero "Chamado de Cthulhu" na aba do Bestiário, rotas de API, exportação DOCX agrupada/multi-cópia e geração de PDFs editáveis.
- **Revisão de regras (10/11/2026):** escudo, página de Sanidade e bestiário alinhados ao M&M 3e e ao CoC 7e. As tabelas de Sanidade (acessos, durações, recuperação, ponto de ruptura) têm fonte única em `nucleo/sanidade.py`. As criaturas ganharam o campo `sanidade` (perda "x/y"). O cultista usa "Especialidade: Mythos de Cthulhu", que reduz a SAN máxima.
- **Regra própria do projeto:** a tabela d10 de acessos de loucura com efeitos em condições de M&M foi redigida para o projeto (não vem do livro).
- **Escudos conferidos com o livro básico (Moribundo, Caído, Aflição):** faroeste e Cthulhu usavam Moribundo com CD 10 (+1) e três sucessos; agora seguem o livro e os Livros do Mestre (Fortitude CD 15, dois graus de sucesso estabilizam, três graus de falha somados matam). A Aflição usa a tabela do livro (três graus); fantasia e faroeste acrescentam um 4º grau marcado [Casa], como nos livros deles. Caído dá –5 à distância contra o alvo.
- **Livros publicados (aguardam revisão editorial):** Livro do Jogador (`dados/livros/cthulhu_jogador.md`) e Livro do Mestre (`dados/livros/cthulhu_mestre.md`) criados segundo `dados/generos/cthulhu/PREPARACAO_LIVROS.md` e integrados ao download `.docx`. Aguardam leitura editorial do usuário.

## Gênero Escola de Magia (inspirado em Harry Potter)
- **Implementação base e revisão concluídas:** gênero ativado em `dados/generos/escola_de_magia/` via `ferramentas/criar_escola_de_magia_base.py` (`genero.json`, `equipment.json`, `powers.json`, `player.json`, `archetypes.json`, `modules.json`, `complications.json`, `names.json`).
- **57 feitiços e dons com custos em M&M 3e:** 56 feitiços baseados em `referencias/harry potter/Tabela de magias.pdf` (incluindo Maldições Imperdoáveis marcadas com `so_npc: true` e filtradas do seletor de jogador em `nucleo/player.py`) + `Aparatação`. Feitiços utilitários (*Lumus*, *Nox*, *Colloportus*, *Pericullum*, *Aparecium*) usam efeitos não ofensivos para não criar ataques falsos nem alterar defesas na ficha; feitiços de ataque mirados usam `Combate à Distância: Varinha`. Todos os feitiços de varinha usam o Arranjo `"Varinha"` com falha **Removível** (`-1 PP`): o jogador ganha **1 PP por missão** na escola e aprende 1 feitiço novo no arranjo.
- **4 Casas + Visitante como pacotes base (2 PP):** Grifinória, Corvinal, Lufa-Lufa, Sonserina e Sem Casa (Adulto/Visitante), livres para os 2 arquétipos (`Estudante` com 5 focos e `Bruxo formado` com 3 focos).
- **NPCs e módulos validados:** 4 arquétipos de NPC (`estudante_rival`, `monitor_escolar`, `bruxo_das_trevas`, `auror_patrulha`) e 3 módulos (`duelista_treinado`, `batedor_vassoura`, `especialista_azaracoes`) equilibrados nos limites de NP para todos os estilos.
- **Livros do Jogador e do Mestre publicados (`dados/livros/escola_de_magia_jogador.md` e `escola_de_magia_mestre.md`):** completos com regras de M&M 3e, Arranjo da Varinha e evolução de 1 PP/missão, Mapa de Relacionamentos de *Mecha & Mangá*, Taça das Casas, provas (N.O.M.s/N.I.E.M.s), regras completas de **Quadribol** (*Quadribol Através dos Séculos*: as 4 posições, bônus de passe, Balaços, Pomo de Ouro, as 12 Manobras Clássicas e as 10 Faltas Mais Comuns), Poções, Maldições Imperdoáveis, exemplo de ficha real (**Cedric Spinnet**, NP 2) e apêndice automático.
- **Planilhas `.xlsx` de Escola de Magia (`armas.xlsx`, `itens.xlsx`, `poderes.xlsx` e `pocoes.xlsx`):** geradas dinamicamente via `nucleo/planilhas.py` (com filtro por loja do Beco Diagonal / Hogsmeade na aba *"Por comércio"*) e `ferramentas/criar_escola_de_magia_pocoes.py` (`dados/generos/escola_de_magia/pocoes.xlsx` e `alquimia.json`, sincronizados com `equipment.json`).
- **Escudo do Mestre (`dados/escudo/escola_de_magia.json`):** gerado por `ferramentas/criar_escola_de_magia_escudo.py` (8 abas, letalidade padrão Heroica). Inclui abas dedicadas de **Magia e Varinha** (progressão de 1 PP/missão), **Relacionamentos** (*Mecha & Mangá*, pp. 122–124) e **Quadribol** (posições, 12 manobras e 10 faltas).
- **Testes automatizados:** `tests/test_escola_de_magia.py`, `tests/test_livros.py` e `tests/test_escudo.py`.
- **Rolagem de Eventos (feito):** `dados/viagem/escola_de_magia.json`, gerado por `ferramentas/criar_escola_de_magia_viagem.py`. Áreas por nível de perigo (Rotina, Fora de hora, Proibida, Mortal), lugares (Corredores, Masmorras, Jardins e lago, Floresta, Vilarejo), situações de aluno (em incursão, escondido, lugar protegido), 48 eventos e 26 criaturas. As criaturas usam os arquétipos de NPC do gênero ou fichas equivalentes do bestiário de fantasia, com a adaptação descrita em `ficha_base`; quando o Bestiário de Criaturas Mágicas existir, troque os `bestiario_id` no script. Ainda não há planilha `.xlsx` de mesa, como a da fantasia.
- **Próximos passos (pendências futuras de Escola de Magia):**
  - **Bestiário de Criaturas Mágicas (`dados/bestiario/escola_de_magia/`):** criar `ferramentas/criar_escola_de_magia_bestiario.py` usando `referencias/harry potter/Animais Fantasticos e Onde Habitam.pdf` (classificação `X` a `XXXXX` do Ministério da Magia) e comparando com fichas equivalentes do bestiário de Fantasia/D&D (ex.: *Diabrete da Cornualha*, *Trasgo Montanhês*, *Hipogrifo*, *Acromântula*, *Lobisomem*, *Testrálio*, *Dementador* e *Basilisco*).

## Outros
- **Novos temas (só preparação):** `dados/generos/IDEIAS_DE_TEMAS.md` lista Delta Green, samurai, kaiju e ópera espacial, com um `PREPARACAO_GENERO.md` em cada pasta. Kaiju e ópera espacial dependem de decidir o sistema de veículos e mechas.
- Biblioteca de fichas salvas, edição de arquétipos pela interface e mechas, como já estava no README.

## Heróis conhecidos (Marvel, DC, Invencível e Outros)
- **Marvel (revisão e tradução concluídas):** todas as **116 fichas** estão convertidas para M&M 3e, com custos fechados (`0` poderes pendentes), vantagens alinhadas a `dados/comum/vantagens.json`, perícias normalizadas com acentuação canônica e **116/116 classificadas como jogáveis** em `dados/generos/herois/auditoria_marvel.json` (incluindo `chamber` e `sentinel`, cujos valores `null` por travessão na fonte representam construtos/Imunidade a Fortitude).
- **DC (glossário e traduções atualizados):** das **536 fichas**, **532 possuem tradução em `dados/generos/herois/traducoes/dc/`** (`8` revisadas manualmente contra o livro e `524` geradas via `ferramentas/traduzir_dc.py`, todas com defesas extraídas e glossário inglês→português unificado) e **4 são mantidas sem tradução** para os testes de fallback bruto em `tests/test_herois.py`. As discrepâncias herdadas do PDF original listadas em `dados/generos/herois/dc/auditoria_extracao.json` (`253 jogáveis`, `283 com ressalvas`) dependem dos PDFs brutos (`referencias/dc/`), que não estão no repositório local, para conferência editorial página a página.
- **Invencível (11 fichas) e Outros (1 ficha — Kratos):** regeneradas a partir de `dados/livros/invencivel.md` via `ferramentas/importar_invencivel.py`, livres de escapes Markdown residuais e integradas à auditoria (`9 jogáveis` e `2 ressalvas` em Invencível por limites da ficha fonte; `1 jogável` em Outros).
- **Glossário e Auditoria:** `ferramentas/tradutor_herois.py` alinhado aos termos canônicos brasileiros do M&M 3e; `python ferramentas/auditar_herois.py` cobre todas as **664 fichas** (`0` erros de leitura ou escapes residuais).
