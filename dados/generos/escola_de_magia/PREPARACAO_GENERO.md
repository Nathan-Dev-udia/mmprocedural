# Escola de magia (inspirado em Harry Potter): preparação

Nada implementado. Leia antes o passo a passo comum em `dados/generos/IDEIAS_DE_TEMAS.md`.

## Premissa

Estudantes de uma escola de magia escondida do mundo comum, divididos em casas, aprendendo feitiços ano a ano enquanto
enfrentam mistérios dentro e fora da escola. Campanhas possíveis: um ano letivo por arco, ou adultos formados (aurores,
curandeiros) na era moderna.

## O que reaproveita (quase tudo vem da fantasia)

- **Magias como poderes** com arranjo (`"arranjo"` no `powers.json`; livro básico cap. 6): a varinha conjura um feitiço
  por vez, e o arranjo faz isso de graça. Molde: `magia(...)` em `ferramentas/criar_fantasia_base.py`.
- **Raças** (`racas` no `player.json`) para as casas, como um pacote pequeno de perícia ou vantagem; ou foco do arquétipo.
- **Poções**: as da fantasia (`referencias/fantasia/pocoes.xlsx`, `referencias/Witcher_Pocoes_MM.xlsx`) como molde de
  ingredientes e efeitos.
- **Bestiário** para as criaturas mágicas; **Rolagem de Eventos** (`dados/viagem/`) para eventos na escola e na floresta.

## Decisões em aberto

1. **Varinha:** sugestão de falha **Removível** em todos os feitiços (livro básico: barateia o poder, e sem varinha o
   bruxo não conjura). É a regra central do tema.
2. **Casas: raça ou foco?** Raça permite qualquer casa com qualquer estilo de estudante (sugestão). Foco obriga a escolher
   entre casa e estilo.
3. **NP por ano escolar:** sugestão 1º e 2º ano NP 2; 3º e 4º NP 3; 5º NP 4; 6º NP 5; 7º NP 6; adultos NP 7 a 9.
4. **Feitiços por ano:** cada feitiço com `ano_minimo`, que vira NP mínimo (como o "nível mínimo pelo NP" pensado para as
   magias da fantasia). O gerador só sorteia feitiços até o ano do personagem.
5. **Letalidade padrão:** Heroica ou Equilibrada (a escola não é mortal; feitiços proibidos são a exceção).
6. **Dinheiro:** moedas de ouro, prata e bronze com taxa fixa (como as peças de ouro da fantasia). Material escolar como
   `itens_basicos`.

## Arquétipos sugeridos

- **Estudante:** um arquétipo só, com focos por estilo (estudioso, duelista, encrenqueiro, herbologista, artilheiro de
  quadribol). As casas entram como raça.
- **Adultos:** auror, curandeiro, inominável (pesquisador), domador de criaturas, comerciante do beco.
- **NPCs:** professor, monitor, comensal (vilão), criatura das trevas, fantasma da escola.

## Matérias como perícias

| Matéria | Perícia no M&M |
|----|----|
| Poções | `Especialidade: Poções` |
| Herbologia | `Especialidade: Herbologia` |
| Transfiguração, Feitiços | Perícia de ataque mágico ou `Especialidade: Teoria Mágica` |
| Defesa contra as Artes das Trevas | `Especialidade: Artes das Trevas` (conhecimento) e ataque com a varinha |
| Trato das Criaturas | `Especialidade: Criaturas Mágicas` |
| Astronomia, História da Magia | `Especialidade: <nome>` |
| Voo de vassoura | Veículos ou `Especialidade: Voo` |

## Feitiços (lista inicial de 30 a 50)

Converter cada feitiço num efeito do Perfis de Poder (`dados/comum/poderes/perfis_de_poder.json`), como na fantasia:
desarmar (Desarmar à distância), atordoar (Aflição), escudo (Defesa ou Deflexão), levitação (Mover Objeto), luz
(Ambiente), abrir trancas, reparo, convocar objeto, patrono (Criar ou Invocar), transfigurar (Transformar), feitiços
proibidos (Dano letal, Controle, Aflição grave) só para NPCs.

## Fontes

- Nenhum livro em `referencias/`. Existem RPGs de fãs; sem livro, tudo é [Casa].
- `referencias/mm/mutantes malfeitores o livro de magia.pdf` (2ª edição, passa pelo conversor
  `referencias/mm/conversor 2e para a 3e.pdf`) e o Perfis de Poder (capítulo de magia).
