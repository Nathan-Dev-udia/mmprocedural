# Pendências

Rascunho do que ficou para depois (atualizado na versão 1.7.0).

## Livros
- **Cyberpunk:** os dois livros foram revisados, corrigidos e publicados em `dados/livros/`. A ficha da moto do clã, as descrições de equipamento, complicações, limites de NP, custos e opções de compra foram alinhados aos dados e ao gerador.
- **Faroeste:** revisão contra o gerador concluída. Os livros explicam comida, lotes, carga e montaria, o dinheiro guardado no sorteio, a dívida e a distribuição de pontos (nova seção 15 do Livro do Jogador). O exemplo do Jesse inclui as rações e a carga, e a tabela de locomoção usa as Velocidades do catálogo. Preços e pesos das tabelas batem com o `equipment.json`. Os livros ainda aguardam leitura editorial do usuário.
- **Carga no gerador do faroeste:** o gerador não tira itens por causa do peso. Cerca de 5% das fichas (só as com Força 0) saem com carga pesada. O livro avisa; falta decidir se o sorteio deve mandar peso para a montaria ou evitar Força 0.
- **Dados do faroeste:** o `equipment.json` continua sendo a fonte da verdade (não há script gerador, como na fantasia); os testes de `test_player.py` conferem peso em kg, preço e comércio de todos os itens. Os pesos marcados como estimados (kits, chapéus, baioneta, cartucheira) não vêm do livro.
- **Fantasia:** revisão mecânica concluída. Custos de poderes, Axii, o exemplo de Sariel, poção de cura, complicação fixa, armaduras e exemplo do mago rúnico foram alinhados ao catálogo e ao código. Os livros ainda aguardam leitura editorial do usuário.

## Regras e dados da fantasia
- **Armaduras:** as graduações de Proteção seguem as equivalências adotadas do Manual dos Mecanismos Lite; os preços permanecem conversões do gênero. As fichas-base de hobgoblin e soldado usam cota de malha para continuar válidas com a meia-armadura em Proteção 5.
- **Fichas incomuns mas válidas:** podem surgir combinações que não pareçam adequadas ao conceito, como um Campeão com Presença 4 ou um bugbear NP 7 com Furtividade +16. Ajustar manualmente quando o resultado não combinar com a cena.
- **Mago rúnico:** o foco pode priorizar Runas e Prestidigitação em vez de uma perícia de ataque mágico; o livro agora explica como priorizar magia manualmente.

## Escudo do Mestre
- **Fantasia, Faroeste e Cthulhu:** feitos (aba no site, impressão, PDF e planilha). Conteúdo em `dados/escudo/fantasia.json`, `dados/escudo/faroeste.json` e `dados/escudo/cthulhu.json`; queda, tempo de viagem, veículos/montarias, carga e medidas são calculados dinamicamente em `nucleo/escudo.py`.
- **Impressão pelo navegador:** a aba Viagem ocupa duas folhas; o PDF baixado cabe em 7 páginas.
- **Cyberpunk:** ainda sem escudo; basta criar `dados/escudo/cyberpunk.json`.

## Gênero Chamado de Cthulhu (anos 20)
- **Implementação base concluída:** gerador de gênero ativado com dados completos (`dados/generos/cthulhu/` contendo `genero.json`, `equipment.json`, `player.json`, `archetypes.json`, `modules.json`, `complications.json`, `names.json`).
- **15 Ocupações clássicas e 6 faixas de crédito/riqueza:** Professor, Detetive, Médico, Jornalista, Antiquário, Veterano, Policial, Bibliotecário, Diletante, Membro do Clero, Escritor, Parapsicólogo, Enfermeira, Advogado e Criminoso.
- **Mecânica de Sanidade d100 integrada (`nucleo/sanidade.py`):** cálculo inicial derivado de Vontade (`45 + 5 * Vontade`, teto 99 reduzido por Mythos), rolagem d100 (01 sucesso automático, 100 desastre / 96-100 para SAN < 50, perda >= 5 com teste de Intelecto CD 10 para insanidade temporária, perda no dia >= 20% para insanidade indefinida).
- **Página 3 no PDF da Ficha (Registro de Sanidade):** implementada em `nucleo/sanidade_pdf.py` e anexada automaticamente em `nucleo/pdf_export.py`. Traz contador visual de 00 a 99, estatísticas vitais, regras resumidas de Sanidade, tabela d10 de Acessos de Loucura, registro de Fobias e Manias, e diário de Criaturas e Tomos do Mythos.
- **Escudo do Mestre (Site, PDF e XLSX):** 7 abas especializadas em `dados/escudo/cthulhu.json` cobrindo testes investigativos, combate nos anos 20, condições, aba dedicada de Sanidade & Horror, viagens e veículos de 1920 (Ford Modelo T, Packard, trem), perigos/explosivos e serviços da metrópole (hotéis, hospitais, speakeasies).
- **Testes automatizados:** `tests/test_cthulhu.py` e `tests/test_escudo.py` com validação completa de dados, cálculos, geração de PDFs, planilhas e rotas web. Todos os 442 testes do projeto passando com 100% de sucesso.
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
- **Próximos passos opcionais:** Livro do Jogador/Mestre de Cthulhu e Escudo do Mestre para Cyberpunk.

## Outros
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
