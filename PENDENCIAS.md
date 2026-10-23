# Pendências

Rascunho do que ficou para depois (atualizado na versão 1.7.0).

## Livros
- **Cyberpunk:** os dois livros foram revisados, corrigidos e publicados em `dados/livros/`. A ficha da moto do clã, as descrições de equipamento, complicações, limites de NP, custos e opções de compra foram alinhados aos dados e ao gerador.
- **Faroeste:** os textos são os antigos de `referencias/`. Não foram revisados depois das mudanças no gerador (comida, quantidades, distribuição de pontos). O apêndice gerado dos dados está atualizado.
- **Fantasia:** revisão mecânica concluída. Custos de poderes, Axii, o exemplo de Sariel, poção de cura, complicação fixa, armaduras e exemplo do mago rúnico foram alinhados ao catálogo e ao código. Os livros ainda aguardam leitura editorial do usuário.

## Regras e dados da fantasia
- **Armaduras:** as graduações de Proteção seguem as equivalências adotadas do Manual dos Mecanismos Lite; os preços permanecem conversões do gênero. As fichas-base de hobgoblin e soldado usam cota de malha para continuar válidas com a meia-armadura em Proteção 5.
- **Fichas incomuns mas válidas:** podem surgir combinações que não pareçam adequadas ao conceito, como um Campeão com Presença 4 ou um bugbear NP 7 com Furtividade +16. Ajustar manualmente quando o resultado não combinar com a cena.
- **Mago rúnico:** o foco pode priorizar Runas e Prestidigitação em vez de uma perícia de ataque mágico; o livro agora explica como priorizar magia manualmente.

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
