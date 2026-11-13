# Pendências

Rascunho do que ficou para depois (atualizado na versão 1.7.0).

## Livros
- **Cyberpunk:** os dois livros foram revisados, corrigidos e publicados em `dados/livros/`. A ficha da moto do clã, as descrições de equipamento, complicações, limites de NP, custos e opções de compra foram alinhados aos dados e ao gerador.
- **Faroeste:** revisão contra o gerador concluída. Os livros explicam comida, lotes, carga e montaria, o dinheiro guardado no sorteio, a dívida e a distribuição de pontos (nova seção 15 do Livro do Jogador). O exemplo do Jesse inclui as rações e a carga, e a tabela de locomoção usa as Velocidades do catálogo. Preços e pesos das tabelas batem com o `equipment.json`. Os livros ainda aguardam leitura editorial do usuário.
- **Carga no gerador do faroeste (resolvido):** com montaria, o que passa da carga leve e não se usa no corpo (rações, ferramentas, bebida) vai no animal (`nucleo/validator.py`). Os PJs começam com Força 1 (`forca_minima` no `genero.json`), exceto o Jogador de Pôquer e o Médico de Fronteira; no NP 2, a Força fica em 0 quando passaria do limite do NP (a baioneta do veterano). Sobram com carga pesada só alguns jogadores de pôquer e médicos sem cavalo, por 1 ou 2 kg. Os livros do faroeste foram atualizados.
- **Dados do faroeste:** o `equipment.json` continua sendo a fonte da verdade (não há script gerador, como na fantasia); os testes de `test_player.py` conferem peso em kg, preço e comércio de todos os itens. Os pesos marcados como estimados (kits, chapéus, baioneta, cartucheira) não vêm do livro.
- **Fantasia:** revisão mecânica concluída. Custos de poderes, Axii, o exemplo de Sariel, poção de cura, complicação fixa, armaduras e exemplo do mago rúnico foram alinhados ao catálogo e ao código. Os livros ainda aguardam leitura editorial do usuário.

## Regras e dados da fantasia
- **Armaduras:** as graduações de Proteção seguem as equivalências adotadas do Manual dos Mecanismos Lite; os preços permanecem conversões do gênero. As fichas-base de hobgoblin e soldado usam cota de malha para continuar válidas com a meia-armadura em Proteção 5.
- **Fichas incomuns mas válidas:** podem surgir combinações que não pareçam adequadas ao conceito, como um Campeão com Presença 4 ou um bugbear NP 7 com Furtividade +16. Ajustar manualmente quando o resultado não combinar com a cena.
- **Mago rúnico:** o foco pode priorizar Runas e Prestidigitação em vez de uma perícia de ataque mágico; o livro agora explica como priorizar magia manualmente.

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
- **Próximo passo:** Livro do Jogador e Livro do Mestre de Cthulhu. Instruções para a IA (estrutura, fontes, decisões e armadilhas) em `dados/generos/cthulhu/PREPARACAO_LIVROS.md`.

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

## Heróis conhecidos (Marvel e DC)
- **DC:** a extração dos PDFs tem falhas (101 fichas sem defesa ou habilidade essencial, 207 com divergências de custo ou
  perícia). Diagnóstico, linha de base e regras da reextração em `dados/generos/herois/dc/PREPARACAO_REEXTRACAO.md`.
- **Marvel:** a extração do livro está completa (116 perfis, nenhum faltando). Falta fechar a conversão dos poderes
  (97 fichas pendentes, 105 sem total de PP); instruções em `dados/generos/herois/marvel/PREPARACAO_CONVERSAO_PODERES.md`.
  Confirmar a regra de reembolso de habilidade negativa (Giant Man, Hulk).
- **Nomes em inglês:** vantagens, efeitos e especializações ficam em inglês nas fichas e nos PDFs; falta um glossário
  inglês→português.
- Ferramenta: `python ferramentas/auditar_herois.py` mede a qualidade das 652 fichas sem alterar nada.
