# Gênero Chamado de Cthulhu (anos 20): preparação

Anotações usadas para construir o gênero. **O gênero já está implementado** (gerador, Sanidade, escudo e bestiário); este arquivo
fica como registro das decisões e do mapa de páginas do CoC. O que falta, os livros, está em `PREPARACAO_LIVROS.md`.

## Decisões já tomadas

- **Época:** aventura clássica, anos 1920. Era moderna fica para depois.
- **Sanidade:** usar a mecânica de d100 do Chamado de Cthulhu, não a de Medo e Corrupção do Supernatural Handbook.
  Se a rolagem passar da Sanidade atual, o investigador perde pontos. Detalhes abaixo.
- **Classes:** as ocupações do CoC viram arquétipos de PJ. As especialidades dos investigadores (História, Medicina, Ocultismo…)
  viram perícias de Especialidade do M&M.

## Decisões em aberto

1. **Id e nome do gênero:** sugestão `cthulhu` e "Chamado de Cthulhu (anos 20)". A pasta de referências se chama `cutullu`;
   o id não precisa seguir esse nome.
2. **Sanidade inicial:** no CoC ela é igual ao POD (3d6 × 5, média 52, faixa 15–90). Em M&M, duas opções:
   - **(a) Derivada da Vontade** (sugestão): `SAN inicial = 45 + 5 × Vontade`, com teto de 99. Vontade 0 dá 45, Vontade 3 dá 60 e Vontade 6 dá 75.
     Vantagem: acompanha a ficha, e o PP gasto em Vontade passa a valer também para a Sanidade.
   - **(b) Sorteada à parte:** 3d6 × 5, como no CoC, independente da ficha. É mais fiel, mas não conversa com o M&M.
3. **NP dos investigadores:** sugestão de NP 3 por padrão, com faixa de 2 a 5. São pessoas comuns.
4. **Teste de Intelecto da insanidade temporária:** sugestão de d20 + Intelecto contra CD 10 (ver abaixo).

## Referências

Para os dois livros, a página impressa coincide com a página do PDF.

**`referencias/cutullu/chamado-de-cthulhu---livro-basico-7-edicao.pdf`** (440 páginas):

| Assunto | Páginas |
|---|---|
| Criação de investigadores (cap. 3) | 28 |
| Referência rápida da criação | 34 |
| Exemplo completo (Harvey Walters) | 38 |
| Nível de Crédito e os seis padrões de vida | 39 |
| Exemplos de Ocupações | 40–45 |
| Tabela II: Dinheiro e Patrimônio | 46 |
| Lista de Perícias (cap. 4) | 56 |
| Sanidade (cap. 8) | 152–169 |
| Testes de SAN | 154 |
| Insanidade | 155 |
| Acessos de loucura (Tabelas VII e VIII) | 157–159 |
| Fobias e Manias | 159–161 |
| Tratamento e Recuperação | 164 |
| Acostumando-se com o Horrível | 169 |
| Magia (cap. 9) | 170 |
| Tomos (cap. 9) | 173 |
| Aprendendo um Feitiço | 176 |
| Tomos de Conhecimento Arcano (cap. 11) | 222 |
| Grimório (cap. 12) | 240 |
| Artefatos e Dispositivos Alienígenas (cap. 13) | 266 |
| Monstros do Mythos (cap. 14) | 282 |
| Divindades | 310 |
| Horrores Tradicionais | 332 |
| Feras | 335 |
| Cenários prontos (cap. 15) | 344 |
| Equipamento da década de 1920 | 396–398 |
| Tabela de Armas | 401 |
| Resumo das Regras | 407 |
| Ficha de investigador dos anos 20 | 430 |

Há também a ficha editável do CoC, `referencias/cutullu/chamado-de-cthulhu---ficha-editavel-7-edicao.pdf`. Serve só de inspiração
para o layout; a ficha exportada continua sendo a do M&M.

**`referencias/mm/Mutants & Masterminds 3e - Supernatural Handbook.pdf`** (153 páginas):

| Assunto | Páginas |
|---|---|
| Arquétipos sobrenaturais (cap. 2) | o "Massacre Survivor", na p. 41, é um bom exemplo de NP baixo |
| Investigation 101 | 51 |
| Fear, Corruption e Madness (cap. 3) | 64–68 |
| Build-A-Critter | 110 |
| Monster Archetypes | 115 |

Do Supernatural Handbook vem só o apoio: fichas de NP baixo, a regra de Medo como Aflição e a construção de monstros.
A Sanidade **não** vem dele.

**Cuidado com o texto dos livros:** descrever as regras com palavras próprias, como foi feito nos outros gêneros, sem copiar trechos.
O PDF do CoC tem uma marca d'água com o nome e o e-mail de quem o comprou, repetida nas páginas. Ela não pode aparecer em nada do projeto.

## Sanidade

### Regra do CoC, que é a base (p. 154–156)

- **Teste de SAN:** rola d100. Se o resultado for **menor ou igual** à Sanidade atual, é sucesso; se for **maior**, é fracasso.
  - Cada fonte de horror tem uma perda no formato `sucesso/fracasso`. O carniçal, por exemplo, é `0/1D6`: perde 0 no sucesso e 1D6 no fracasso.
  - Um encontro com vários monstros iguais conta como uma perda só.
  - **01** é sempre sucesso.
  - **100** é desastre e perde o **máximo** da perda de fracasso. Com SAN abaixo de 50, desastre vai de 96 a 100.
- **Sanidade máxima:** 99 − Mythos de Cthulhu.
- **Insanidade temporária:** perdeu 5 ou mais pontos de uma vez → teste de INT.
  - Se **passar**, o investigador entende o que viu e fica insano por 1D10 horas.
  - Se **falhar**, ele reprime a memória e não enlouquece.
- **Insanidade indefinida:** perdeu 1/5 ou mais da SAN atual dentro de um "dia" de jogo. Dura até tratar ou se recuperar.
- **Insanidade permanente:** SAN 0. O investigador deixa de ser personagem jogador.
- **Acesso de loucura:** dura 1D10 rodadas, ou vira resumo; ver as Tabelas VII e VIII.
  - O Guardião controla o personagem durante o acesso.
  - Durante o acesso, o investigador não perde mais SAN.
  - Depois do acesso vem a insanidade latente: qualquer nova perda provoca outro acesso.
- **Fobias e manias:** enquanto o investigador está são, servem só para interpretação. Insano, dão dado de penalidade.

### Adaptação para M&M

O mais importante da adaptação: a Sanidade **não é uma defesa nem uma habilidade do M&M**. É um contador à parte, de 0 a 99, rolado em d100.
O resto da ficha continua sendo M&M puro, com d20.

| Peça do CoC | Em M&M |
|---|---|
| SAN inicial (POD) | Decisão 2 em aberto; sugestão: `45 + 5 × Vontade`, teto de 99 |
| Mythos de Cthulhu (%) | Perícia `Especialidade: Mythos de Cthulhu`. Cada graduação vale 5 pontos de Mythos: SAN máxima = `99 − 5 × graduação` |
| Teste de INT da insanidade temporária | d20 + Intelecto contra CD 10. **Sucesso** = fica insano, como no CoC |
| Acesso de loucura | Durante o acesso, o personagem fica sob a condição *controlado* (o Mestre decide as ações), ou o Mestre usa as tabelas como no CoC |
| Dado de penalidade das fobias | Circunstância desfavorável (−2) nos testes, ou −5 se for grave |
| Ponto heroico | Regra opcional a decidir: gastar 1 ponto heroico para rerrolar um teste de SAN. Reduz a letalidade e conversa com o M&M |
| Fobias, manias e insanidade indefinida | Viram **Complicações** da ficha. Quando entram em jogo, dão ponto heroico, como manda o M&M |

**Exemplo:** um investigador tem SAN 60 e vê um carniçal (perda 0/1D6).
- Rola 42: passou e não perde nada.
- Rola 83: fracassou e rola 1D6. Tira 4 e fica com SAN 56.
- Se tivesse tirado 5 ou mais no 1D6, faria o teste de Intelecto CD 10.

### No software

- **Funções puras** num módulo novo, `nucleo/sanidade.py`, cada uma com teste:
  - `sanidade_inicial(vontade)`;
  - `sanidade_maxima(graduacao_mythos)`;
  - `teste_de_sanidade(rolagem, atual, perda)`, que devolve sucesso ou fracasso, a perda e se o investigador precisa do teste de insanidade temporária;
  - `insanidade_indefinida(perdido_no_dia, atual_no_inicio_do_dia)`.
- **Ficha gerada:** guardar algo como `npc["sanidade"] = {"inicial": 60, "atual": 60, "maxima": 99}`.
- **PDF do M&M:** não há campo de Sanidade. Escrever em "Notas & Condições", por exemplo "Sanidade 60 (máx. 99) · Mythos 0",
  em `pdf_export.valores_dos_campos`.
  - Se quiser que o campo se atualize, dá para criar uma fórmula com `_aplicar_formulas` ligada à Vontade.
  - A fórmula seguiria o padrão de `formula_da_iniciativa`, com `_js_so_quando_mudar` para só recalcular quando a Vontade mudar.
- **DOCX e texto (`formatter.py`):** uma linha de Sanidade logo abaixo das defesas.
- **Planilha da ficha (ideia de exportar em xlsx, ainda não feita):** Sanidade inicial e máxima como fórmula
  (`=MIN(99;45+5*Vontade)`), e a Sanidade atual como célula de entrada.
- **Interface (opcional, depois):** um botão "Teste de SAN" que rola d100 e aplica a perda.

## Ocupações → arquétipos

**Formato:** o mesmo do `player.json` do faroeste. Cada arquétipo tem:
- `vantagens_essenciais` e `vantagens_opcionais`;
- `prioridades` (`habilidade:`, `pericia:`, `defesa:`);
- `sugestoes` (motivações e complicações);
- `focos`, cada um com vantagens, prioridades, armas e itens próprios;
- `armas` (principais e secundárias);
- `itens` (essenciais e opcionais).

O modelo está em `dados/generos/faroeste/player.json`; o "Médico de Fronteira" serve de exemplo.

**Ocupações sugeridas:** 15, a partir das páginas 40 a 45 do livro, com prioridade para as clássicas de Lovecraft.

| Arquétipo | Focos (exemplos) | Prioridades principais |
|---|---|---|
| Professor universitário | Historiador, Arqueólogo, Antropólogo, Linguista | Int; Especialidade: História, Arqueologia, Antropologia ou Línguas Antigas; Investigação |
| Antiquário | Colecionador, Avaliador, Contrabandista de relíquias | Especialidade: Antiguidades e História; Percepção; Persuasão |
| Bibliotecário | Arquivista, Bibliotecário de obras raras | Investigação; Especialidade: Ocultismo e Línguas; Int |
| Médico | Clínico, Cirurgião, Legista, Psiquiatra | Tratamento; Especialidade: Medicina; Intuição. O psiquiatra tem Especialidade: Psicanálise e trata a insanidade |
| Enfermeira | De hospital, De guerra | Tratamento; Intuição; Percepção |
| Jornalista | Repórter policial, Fotógrafo, Colunista social | Investigação; Enganação; Percepção; Especialidade: Fotografia |
| Detetive particular | Ex-policial, Agente da Pinkerton | Investigação; Percepção; Intuição; Combate à Distância: Pistolas |
| Oficial de polícia | Patrulheiro, Detetive | Percepção; Intimidação; Combate à Distância: Pistolas; Especialidade: Direito |
| Advogado | Criminalista, De família rica | Especialidade: Direito; Persuasão; Intuição |
| Membro do clero | Padre, Pastor, Rabino | Especialidade: Teologia e Ocultismo; Persuasão; Vontade |
| Diletante | Herdeiro, Aventureiro rico | Riqueza alta; Especialidade: Arte ou Línguas; Persuasão |
| Escritor | Romancista, Poeta, Ocultista amador | Especialidade: Literatura e Ocultismo; Intuição |
| Parapsicólogo | Investigador psíquico, Desmascarador de médiuns | Especialidade: Ocultismo; Investigação; Especialidade: Fotografia |
| Veterano da Grande Guerra | Infantaria, Piloto, Sapador | Combate à Distância: Rifles; Atletismo; Furtividade; Vontade |
| Criminoso | Contrabandista da Lei Seca, Arrombador, Golpista | Furtividade; Prestidigitação; Enganação; Combate à Distância: Pistolas |

### Perícias do CoC → M&M

| CoC | M&M |
|---|---|
| Antropologia, Arqueologia, História, Direito, Ocultismo, Ciência (cada uma), Línguas, Contabilidade, Avaliação | `Especialidade: <nome>` |
| Mythos de Cthulhu | `Especialidade: Mythos de Cthulhu`. Não se compra na criação: vem da campanha e reduz a SAN máxima |
| Medicina | `Especialidade: Medicina`, mais Tratamento |
| Primeiros Socorros | Tratamento |
| Psicanálise | `Especialidade: Psicanálise`. Trata a insanidade, ver p. 164 |
| Usar Bibliotecas | Investigação, ou a vantagem Bem Informado |
| Encontrar, Escutar | Percepção |
| Psicologia | Intuição |
| Charme, Persuasão | Persuasão |
| Lábia | Enganação |
| Intimidação | Intimidação |
| Furtividade | Furtividade |
| Chaveiro, Prestidigitação | Prestidigitação |
| Rastrear, Sobrevivência | `Especialidade: Sobrevivência` |
| Dirigir Automóveis, Pilotar | Veículos |
| Consertos Mecânicos e Elétricos, Operar Maquinário Pesado | Tecnologia |
| Arte/Ofício | `Especialidade: <ofício>` |
| Armas de Fogo (Pistolas, Rifles/Espingardas, Submetralhadoras) | `Combate à Distância: <tipo>` |
| Lutar (Briga) | `Combate Corpo-a-Corpo: Briga` |
| Esquivar | Esquiva |
| Saltar, Escalar, Nadar, Arremessar | Atletismo |
| Nível de Crédito | Riqueza; ver a seção abaixo |

**Antes de usar uma especialização nova** (Mythos de Cthulhu, Psicanálise, Antiguidades…), confira se `rules.pericia_valida` a aceita.
O `data_loader` recusa perícia desconhecida.

## Riqueza (Nível de Crédito)

O CoC tem seis padrões de vida (p. 39 e Tabela II, p. 46). Eles batem com as seis faixas de riqueza que os outros gêneros usam:

| CoC | Faixa do `player.json` |
|---|---|
| Pobretão (Crédito 0) | Riqueza 4, devolve 1 PP |
| Pobre (1–9) | Riqueza 4 |
| Médio (10–49) | Riqueza 8 |
| Abastado (50–89) | Benefício: Riqueza 1 |
| Rico (90–98) | Benefício: Riqueza 2 a 4 |
| Ricaço (99) | Benefício: Riqueza 6 |

**Dinheiro inicial:** em dólares dos anos 20, tirado da Tabela II e ajustado aos preços das p. 396–398.
- O formato `$` do faroeste em `formatter.texto_dinheiro` serve.
- No CoC, os itens do padrão de vida não são pagos (p. 47). É parecido com os "itens básicos" do faroeste.
- Manter as regras de dinheiro que já existem: a parte guardada de 15% e o piso de 5% em `nucleo/player.py`.

## Equipamento

- Use a configuração `"equipamento": "dinheiro"`, como no faroeste.
- **Fonte dos preços:** p. 396–398 do livro (anos 20). As armas estão na tabela da p. 401.
- **Armas:** converter para o M&M pelos mesmos critérios das armas de fogo do faroeste. Calibres semelhantes recebem o mesmo Dano.
  As de destaque nos anos 20 são:
  - revólver .38;
  - pistola .45 automática;
  - espingarda calibre 12;
  - rifle de ferrolho;
  - submetralhadora Thompson;
  - faca, porrete e soqueira;
  - dinamite.
- **Itens típicos:** lanterna elétrica, câmera fotográfica, kit médico, kit de arrombamento, mapas, binóculos, lampião,
  pá e pé de cabra, automóvel Ford Modelo T, passagens de trem e navio.
- **Comércios:** reaproveitar a ideia de `COMERCIO_POR_CATEGORIA` da fantasia com lojas da época. Exemplos:
  - loja de departamentos;
  - farmácia;
  - loja de armas;
  - livraria e antiquário;
  - concessionária;
  - loja de ferragens;
  - mercado negro, para a Lei Seca.
- **Tomos do Mythos** (cap. 11): itens especiais que não estão à venda. Ler um tomo dá graduações em Mythos de Cthulhu, custa SAN
  e pode ensinar feitiços. Ficam como itens de campanha ou de bestiário, não do sorteio de PJ.

## Magia do Mythos (powers.json)

- É opcional para PJ e rara. Os arquétipos começam **sem** feitiços; o PJ só aprende em jogo, por tomos.
- **Lista curta**, com 10 a 15 feitiços do Grimório (cap. 12, p. 240). Exemplos:
  - Contatar (uma entidade);
  - Encantar Faca;
  - Sinal de Voor;
  - Encolher;
  - Dominar;
  - Ferir;
  - Convocar/Comandar (servidor);
  - Portal;
  - Sinal Arcano.
- **Conversão:** cada feitiço vira um efeito do catálogo do Perfis de Poder, como já se faz na fantasia (`magia(...)` em
  `ferramentas/criar_fantasia_base.py`), com falhas pesadas:
  - **Efeito Colateral:** perde SAN. Anote a perda no formato do CoC, por exemplo "custa 1D6 de SAN".
  - Também Cansativo, Concentração ou Ritual (tempo de conjuração longo).
- **Para os NPCs (cultistas, feiticeiros)** esses feitiços entram normalmente.

## Complicações (complications.json)

- **Fobias e manias:** usar as listas do livro (p. 160–161), de umas 20 cada, como detalhes da complicação "Fobia" e de "Mania"/Peculiaridade.
- **Complicações de época:** Lei Seca, preconceito, dívida, vício (álcool contrabandeado, láudano), trauma da Grande Guerra, segredo de família.
- **Antecedentes do CoC** (p. 39): Ideologia/Crenças, Pessoas Significativas, Locais Importantes, Pertences Queridos e Características
  combinam com Motivação e Complicações. Cada arquétipo pode ganhar sugestões nesse formato.

## Nomes (names.json)

Nomes americanos e da Nova Inglaterra dos anos 20, mais nomes de imigrantes (irlandeses, italianos, alemães e judeus do Leste Europeu),
que combinam com Arkham, Boston e Nova York.

## Bestiário

Fica para uma segunda etapa, depois do gênero de PJ funcionando.
- **Pastas:** `dados/bestiario/cthulhu/<tipo>/`, por exemplo mythos, horrores e feras. Registrar o gênero em
  `NOMES_DOS_GENEROS` (`nucleo/bestiario.py`, linha 67).
- **Criaturas prioritárias:**
  - Monstros do Mythos: Profundo, Carniçal, Mi-Go, Byakhee, Shoggoth e Cão de Tíndalos (Monstros do Mythos, p. 282);
  - Cultistas como NPCs, que já podem sair do gerador.
- **Campo extra em cada ficha:** `perda_de_sanidade`, por exemplo "0/1D6" (carniçal). O PDF da criatura precisa mostrar essa perda,
  nas Notas.
- **Ferramentas de conversão:** o Build-A-Critter (Supernatural Handbook, p. 110) ajuda a converter. Seguir o mesmo processo das fichas
  da fantasia (testes em `tests/test_bestiario.py`, `FICHAS_NOVAS`).
- **Divindades** (Cthulhu, Nyarlathotep…): ficam fora do NP de jogo. Quando muito, servem de ficha "conceitual"
  (`status_dados: "conceitual"`).

## Passo a passo da construção

1. **Gerador:** criar `ferramentas/criar_cthulhu_base.py`, que gera todos os JSON do gênero. O script é a fonte da verdade:
   não editar os JSON à mão.
   - Seguir o molde de `criar_fantasia_base.py`, com `gravar()`, `item()`, `com_pesos()` e `com_comercio()`.
   - Gerar `genero.json`, `player.json`, `archetypes.json` (NPCs: cultista, policial, capanga, mafioso, médico do sanatório),
     `modules.json`, `equipment.json`, `names.json`, `complications.json` e `powers.json`.
   - O `data_loader` exige os arquivos de `ARQUIVOS_DO_GENERO`: archetypes, modules, equipment, names, player e complications.
2. **`genero.json`:**
   - `"id": "cthulhu"`;
   - `"perfis_de_poder": []`, ou só os perfis usados pelos feitiços;
   - `"configuracoes": {"rotulo_poderes": "Feitiços do Mythos", "equipamento": "dinheiro", "sanidade": true}`.
3. **Código específico de gênero:** em `nucleo/player.py`, perto da linha 95, o filtro de vantagens está fixo no faroeste
   (`dados["genero"]["id"] == "faroeste"`). Transformar o filtro numa configuração do `genero.json`, ou acrescentar uma coluna
   equivalente em `dados/comum/vantagens.json`, para Cthulhu também esconder vantagens que não combinam (as de super-herói).
4. **Sanidade:** criar `nucleo/sanidade.py` e ligá-lo:
   - no gerador, para guardar `npc["sanidade"]`;
   - em `formatter.py`, `pdf_export.py` e `docx_export.py`.
5. **Testes:** criar `tests/test_cthulhu.py`, no molde de `test_cyberpunk.py` e `test_fantasia.py`. Ele deve cobrir:
   - o gênero carrega sem DataError;
   - os 15 arquétipos geram fichas válidas no NP 3 e respeitam os limites do NP;
   - o dinheiro inicial nunca é 0;
   - a Sanidade inicial e a máxima estão certas;
   - o teste de SAN com 01, 100, desastre abaixo de 50, perda de 5+ e perda de 1/5;
   - a Sanidade aparece no PDF.
6. **Livros:** criar `dados/livros/cthulhu_jogador.md` e `cthulhu_mestre.md`, no padrão da fantasia, e acrescentá-los aos testes
   de `tests/test_livros.py`.
   - O livro do jogador traz as ocupações, a Sanidade e o equipamento.
   - O do mestre traz a perda de SAN por criatura, as tabelas de loucura resumidas, os tomos e os feitiços.
7. **Bestiário:** segunda etapa; ver a seção acima.
8. **Atualizar a documentação:** o `README.md` e o `PENDENCIAS.md`.

## Para mais tarde (fora do escopo dos anos 20)

- **Era moderna:** equipamento nas p. 399–400 do livro. Pode virar uma opção de época dentro do mesmo gênero.
- **Planilha xlsx da ficha** com fórmulas, incluindo a Sanidade. Foi discutida antes e não começou.
