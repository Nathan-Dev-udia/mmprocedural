# Pilotos de mecha contra kaiju (inspirado em Pacific Rim): preparação

Nada implementado. Leia antes o passo a passo comum em `dados/generos/IDEIAS_DE_TEMAS.md`.

## Premissa

Futuro próximo: monstros gigantes saem de uma fenda no fundo do oceano. A humanidade responde com robôs gigantes
pilotados por duas pessoas ligadas por uma ponte neural. Os PJs são pilotos, técnicos e cientistas de uma base que pode
ser a última.

## O bloqueio: mechas com ficha

O projeto ainda não tem veículos nem mechas com ficha própria (está em "O que ainda não existe" no `README.md`). Este tema
depende disso, e a ópera espacial (`space_opera/`) também, para as naves. **Decida o sistema de veículos antes, uma vez,
para os dois temas.**

Opções:
1. **Mecha como veículo do livro básico** (cap. 7: Tamanho, Força, Velocidade, Defesa, Resistência e poderes do veículo),
   pago com a vantagem Equipamento. Simples, mas as fichas de veículo não usam as perícias do piloto da mesma forma.
2. **Mecha como Forma Alternativa / poder do piloto** (Perfis de Poder): o mecha é um poder com a falha Removível. Usa o
   motor de poderes que já existe, mas mistura o piloto com a máquina.
3. **Regras do *Mecha & Mangá*** (`referencias/mm/mutantes e malfeitores mecha e manga.pdf`, 2ª edição: precisa do
   conversor `conversor 2e para a 3e.pdf`). É o mais fiel ao gênero; o cyberpunk já converteu o modelo Ciborgue desse livro.

Sugestão: opção 3 para a lógica de construção, com a ficha final no formato da opção 1, e um gerador de mechas separado
do gerador de PJ (uma aba nova, como o Bestiário).

## Decisões em aberto

1. **Sistema de mechas** (acima).
2. **Ponte neural:** os dois pilotos dividem o controle. Regra [Casa] possível: o mecha usa a melhor perícia de cada piloto
   para cada tarefa, e a falha de sincronia é uma Aflição na Vontade dos dois.
3. **Escala:** kaiju e mechas são Enormes a Colossais. A Tabela de Medidas e o tamanho (`rules.TAMANHOS`) cobrem; falta
   decidir como um humano interage com essa escala (normalmente não interage: o combate é mecha contra kaiju).
4. **NP:** pilotos NP 4 a 6 (pessoas); mechas e kaiju com NP próprio, alto (10 a 14).
5. **Letalidade:** Mortal para os pilotos dentro do mecha destruído; o mecha tem a própria tabela de dano de objeto.

## Arquétipos sugeridos

- **Piloto** (focos: atacante, defensor, veterano, recruta), **técnico de manutenção**, **cientista de kaiju**
  (biólogo, matemático da fenda), **oficial de comando**, **piloto de helicóptero de transporte**.
- **Bestiário:** kaiju por categoria (I a V), cada categoria um NP; o campo NP do bestiário já escala (`bestiario.no_np`).

## Fontes

- `referencias/mm/mutantes e malfeitores mecha e manga.pdf` (mechas, escala, combate de gigantes).
- `referencias/mm/mutantes malfeitores 3a edicao.pdf`, cap. 7 (veículos) e regras de tamanho.
