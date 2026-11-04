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
- **Fantasia:** feito (aba no site, impressão, PDF e planilha). Conteúdo em `dados/escudo/fantasia.json`; queda, tempo de viagem, montarias, carga e medidas são calculados em `nucleo/escudo.py`. As regras novas de forçar a montaria, comida e caça e carga estão no Livro do Mestre (14.8 a 14.10) e ainda aguardam leitura editorial.
- **Impressão pelo navegador:** a aba Viagem ocupa duas folhas; o PDF baixado cabe em 7 páginas.
- **Faroeste e cyberpunk:** ainda sem escudo; basta criar `dados/escudo/<gênero>.json`.

## Gênero Chamado de Cthulhu (anos 20)
- Planejado, não iniciado. Decisões, referências dos livros, adaptação da Sanidade em d100 e passo a passo em
  `dados/generos/cthulhu/PREPARACAO_GENERO.md`.

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
