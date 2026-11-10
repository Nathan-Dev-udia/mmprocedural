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
- **Impressão pelo navegador:** a aba Viagem ocupa duas folhas; o PDF baixado cabe em 7 páginas.
- **Faroeste, regras gerais a revisar:** além de Moribundo, Caído e Aflição (já corrigidos), as abas Combate e Condições ainda têm itens fora do livro básico: 2º grau de dano como "Atordoado" (o livro diz tonto) e 3º como "Cambaleando"; Indefeso com "+5"; condições inexistentes (Transpassado, Dominado, Surdo); ações e manobras de outro sistema (Desengajar, Imobilizar, Ataque Total, Tiro Preciso –4, Recuperar-se "1/cena"). O Cthulhu copiou parte dessas abas. Referência certa: seções 2.8, 5.4, 5.5 e 6 do Livro do Mestre do Cyberpunk.

## Gênero Chamado de Cthulhu (anos 20)
- **Implementação base concluída:** gerador de gênero ativado com dados completos (`dados/generos/cthulhu/` contendo `genero.json`, `equipment.json`, `player.json`, `archetypes.json`, `modules.json`, `complications.json`, `names.json`).
- **15 Ocupações clássicas e 6 faixas de crédito/riqueza:** Professor, Detetive, Médico, Jornalista, Antiquário, Veterano, Policial, Bibliotecário, Diletante, Membro do Clero, Escritor, Parapsicólogo, Enfermeira, Advogado e Criminoso.
- **Mecânica de Sanidade d100 integrada (`nucleo/sanidade.py`):** cálculo inicial derivado de Vontade (`45 + 5 * Vontade`, teto 99 reduzido por Mythos), rolagem d100 (01 sucesso automático, 100 desastre / 96-100 para SAN < 50, perda >= 5 com teste de Intelecto CD 10 para insanidade temporária, perda no dia >= 20% para insanidade indefinida).
- **Página 3 no PDF da Ficha (Registro de Sanidade):** implementada em `nucleo/sanidade_pdf.py` e anexada automaticamente em `nucleo/pdf_export.py`. Traz contador visual de 00 a 99, estatísticas vitais, regras resumidas de Sanidade, tabela d10 de Acessos de Loucura, registro diário de Sanidade (ponto de ruptura), registro de Fobias e Manias, e diário de Criaturas e Tomos do Mythos. Cabe numa folha mesmo com complicações longas.
- **Escudo do Mestre (Site, PDF e XLSX):** 7 abas especializadas em `dados/escudo/cthulhu.json` cobrindo testes investigativos, combate nos anos 20, condições, aba dedicada de Sanidade & Horror, viagens e veículos de 1920 (Ford Modelo T, Packard, trem), perigos/explosivos e serviços da metrópole (hotéis, hospitais, speakeasies).
- **Testes automatizados:** `tests/test_cthulhu.py` e `tests/test_escudo.py` com validação de dados, cálculos, geração de PDFs, planilhas e rotas web. Na revisão de 10/11/2026 a suíte tinha 447 testes, todos passando.
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
- **Escudos conferidos com o livro básico (Moribundo, Caído, Aflição):** faroeste e Cthulhu usavam Moribundo com CD 10 (+1) e três sucessos; agora seguem o livro e os Livros do Mestre (Fortitude CD 15, dois graus de sucesso estabilizam, três graus de falha somados matam). A Aflição usa a tabela do livro (três graus) também na fantasia, e Caído dá –5 à distância contra o alvo.
- **Próximos passos opcionais:** Livro do Jogador/Mestre de Cthulhu.

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
