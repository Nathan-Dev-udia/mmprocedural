# Pendências

Rascunho do que ficou para depois (atualizado na versão 1.7.0).

## Livros
- **Cyberpunk:** os dois livros estão em `dados/livros/rascunhos/` e não aparecem no site. Para publicar, revisar e mover para `dados/livros/`. Divergências entre o Livro do Mestre do cyberpunk e os dados:
  - O guia cita as complicações Procurado, Cyberpsicose e Lesão duradoura, que não existem em `complications.json`.
  - A moto do Nômade tem Velocidade 6 nos dados e 5 no guia (§10.9 e §16.1).
  - Descrições de itens diferentes do `equipment.json`: rádio, gravador, localizador, binóculos, ferramenta de arrombamento, máscara, lanterna, câmera, algemas e granadas de gás e de fumaça.
- **Faroeste:** os textos são os antigos de `referencias/`. Não foram revisados depois das mudanças no gerador (comida, quantidades, distribuição de pontos). O apêndice gerado dos dados está atualizado.
- **Fantasia:** os dois livros foram escritos agora e merecem uma leitura sua.

## Regras e dados da fantasia
- **Custos do catálogo:** a parte fixa dos custos ("3 pontos por graduação + 2 pontos") passou a ser cobrada (`nucleo/poderes.py`). Algumas magias ficaram mais caras, e os números de custo citados nos livros podem ter mudado em 1 a 3 PP.
- **Axii** custa 1 PP por graduação (base do catálogo limitada), mas a linha dele promete tonto, compelido e controlado. Rever o custo ou o texto.
- **Goblin bardo:** o texto do módulo diz que a Zombaria custa 3 PP por graduação; o `powers.json` cobra 4 + 1.
- **Elixires, óleos e poção de cura** têm preço mas nenhum efeito de regra. O livro do mestre sugere regras da casa.
- **Complicação fixa** do caçador de monstros: entra pela tela e pelo botão Sortear, mas não é obrigatória se a ficha for gerada direto pela API.
- **Peças de armadura sem penalidade:** a cota de talas (Proteção 5, 200 po) é melhor que a meia-armadura (Proteção 4, 750 po), porque o M&M não tem penalidade de armadura.
- **Fichas estranhas mas válidas:** às vezes saem habilidades sem relação com a classe, como um Campeão com Presença 4, ou perícias no teto (bugbear NP 7 com +16).
- **Mago rúnico:** às vezes sai com pouca perícia de magia, porque as perícias do foco (Runas, Prestidigitação) gastam a cota de perícias primeiro.

## Outros
- Biblioteca de fichas salvas, edição de arquétipos pela interface e mechas, como já estava no README.
