# Horror moderno com agentes federais (inspirado em Delta Green): preparação

Nada implementado. Leia antes o passo a passo comum em `dados/generos/IDEIAS_DE_TEMAS.md`.

## Premissa

Agentes de órgãos federais (FBI, CDC, Exército, NSA) recrutados por uma conspiração dentro do governo que combate o
horror cósmico em segredo. Época atual. Os agentes não podem contar a ninguém o que fazem; cada missão custa sanidade,
relações pessoais e carreira.

## O que reaproveita

- **Quase todo o gênero Cthulhu** (`dados/generos/cthulhu/`, `ferramentas/criar_cthulhu_base.py`):
  - Sanidade d100 (`nucleo/sanidade.py`), a 3ª página da ficha (`nucleo/sanidade_pdf.py`) e o escudo com a aba de Sanidade;
  - o bestiário do Mythos (`dados/bestiario/cthulhu/`): carniçal, profundo, mi-go, shoggoth, cultistas;
  - a tabela de conversão de perícias do CoC (`dados/generos/cthulhu/PREPARACAO_GENERO.md`).
- **Armas modernas** do cyberpunk (`dados/generos/cyberpunk/equipment.json`) como ponto de partida para pistolas, fuzis
  e coletes, trocando os preços para dólares atuais.

## Decisão principal em aberto

1. **Gênero próprio ou época dentro do Cthulhu?**
   - (a) **Gênero próprio** `delta_green` (sugestão): ocupações, equipamento e escudo diferentes o bastante; reaproveita
     `nucleo/sanidade.py` sem duplicar código (basta `"sanidade": true` no `genero.json`).
   - (b) **Época dentro do Cthulhu:** exigiria um seletor de época no gerador, que não existe.

## Outras decisões

2. **NP:** sugestão 4 a 6, padrão 5. Agentes são treinados (mais que um investigador de 1920, NP 3).
3. **Letalidade padrão:** Mortal ou Equilibrada.
4. **Vínculos** (pessoas importantes para o agente, que se desgastam com o trabalho): virar complicações
   (Relacionamento) ou uma trilha própria, como a de Humanidade do cyberpunk. Sugestão: complicações, para não criar outro
   contador além da Sanidade.
5. **Cobertura e burocracia:** regra [Casa] de "exposição" (quanto a missão chamou atenção), com teste de Enganação ou de
   Especialidade: Burocracia no relatório final.
6. **Equipamento:** em dinheiro (a agência fornece o básico) ou em pontos (vantagem Equipamento, como os NPCs do livro
   básico). Sugestão: dinheiro, com um kit de serviço gratuito por ocupação.

## Ocupações sugeridas (arquétipos)

| Ocupação | Focos (exemplos) | Prioridades |
|----|----|----|
| Agente especial do FBI | Investigador, Perfilador, Antiterrorismo | Investigação, Intuição, Combate à Distância: Pistolas |
| Militar das forças especiais | Operador, Atirador, Sapador | Combate à Distância: Rifles, Atletismo, Furtividade |
| Médico-legista ou epidemiologista (CDC) | Patologista, Epidemiologista | Tratamento, Especialidade: Medicina, Investigação |
| Analista de inteligência (NSA, CIA) | Criptógrafo, Hacker, Analista | Tecnologia, Especialidade: Computação, Investigação |
| Policial ou xerife local | Detetive, Policial rodoviário | Percepção, Intimidação, Veículos |
| Cientista | Físico, Biólogo, Antropólogo | Especialidade: Ciência, Investigação |
| Agente de campo da CIA | Espião, Contato | Enganação, Persuasão, Furtividade |
| Piloto | Helicóptero, Avião | Veículos, Percepção |

## Fontes

- Nenhum livro de Delta Green em `referencias/` ainda. Com o livro, a conversão segue o mesmo caminho do CoC 7e (os dois
  usam d100).
- `referencias/mm/mutantes malfeitores 3a edicao.pdf`: armas e veículos modernos (cap. 7) e os arquétipos de
  agente do governo.
- `referencias/mm/Mutants & Masterminds 3e - Supernatural Handbook.pdf`: investigação e horror moderno.

## Passo a passo específico

1. Decidir a questão 1. Se for gênero próprio, copiar `criar_cthulhu_base.py` para `criar_delta_green_base.py` e trocar
   ocupações, riqueza (salário federal), equipamento e nomes.
2. Reaproveitar o bestiário: o Bestiário filtra por gênero pela pasta; ou copiar as criaturas para
   `dados/bestiario/delta_green/`, ou ensinar `nucleo/bestiario.py` a ler a pasta de outro gênero (decidir).
3. Escudo: copiar `criar_cthulhu_escudo.py`, trocar as abas da cidade dos anos 1920 por operações (cobertura, perícia
   forense, tempo de resposta da polícia, armas modernas).
