# Ideias de temas (gêneros futuros)

Lista dos temas pensados para o gerador, com o que cada um reaproveita e o que falta. Cada tema tem um
`PREPARACAO_GENERO.md` na própria pasta, com as decisões, as fontes e o passo a passo. **Nada aqui está implementado.**
As pastas não têm `genero.json`, então o gerador as ignora (`data_loader.generos_disponiveis` só lista as pastas com
`genero.json`).

Os nomes das pastas são genéricos de propósito: Delta Green, Pacific Rim, Star Wars e Harry Potter são marcas. Para uso na
mesa não há problema (como já acontece com Cyberpunk e Witcher). Se o projeto um dia for público, os gêneros precisam de
nome, termos e personagens próprios.

## Resumo

| Tema | Pasta | Inspiração | Reaproveita | Falta | Esforço |
|----|----|----|----|----|----|
| Horror moderno com agentes federais | `delta_green/` | Delta Green | Cthulhu inteiro (Sanidade d100, bestiário do Mythos, escudo) | Ocupações e armas modernas, regra de cobertura e burocracia | Baixo |
| Escola de magia | `escola_de_magia/` | Harry Potter | Magias, arranjos, raças e poções da fantasia | Varinha como requisito, catálogo de feitiços por ano, matérias como perícias | Médio |
| Japão feudal | `samurai/` | Filmes de samurai, Lenda dos Cinco Anéis | Molde realista do faroeste (dano mortal, duelos), armas arcaicas | Honra como trilha, clãs, armas e armaduras japonesas | Médio |
| Pilotos de mecha contra kaiju | `kaiju/` | Pacific Rim | Livro *Mecha & Mangá* (`referencias/mm/`), bestiário para os kaiju | **Fichas de mecha** (o projeto não tem veículos com ficha), escala de tamanho, ponte neural | Alto |
| Ópera espacial | `space_opera/` | Star Wars | Raças e magias da fantasia (espécies e a Força), implantes do cyberpunk | **Naves com ficha** (mesmo bloqueio do kaiju), equilíbrio da Força | Alto |

**Ordem sugerida:** Delta Green → Escola de magia ou Samurai → Kaiju e Ópera espacial juntos, depois de decidir o
sistema de veículos e mechas (os dois dependem dele; vale fazer uma vez só).

## Passo a passo comum a todo gênero novo

Foi assim que Cthulhu e Cyberpunk foram construídos. Siga a mesma ordem.

1. **Decisões e fontes** no `PREPARACAO_GENERO.md` da pasta. Livros de referência vão em `referencias/<tema>/` (fora do git).
   Sem livro, toda regra do gênero é **[Casa]** e precisa dizer isso.
2. **Script gerador** `ferramentas/criar_<id>_base.py`, que grava todos os JSON do gênero. O script é a fonte da verdade:
   não edite os JSON à mão. Moldes: `criar_cthulhu_base.py` (sem poderes, com Sanidade) e `criar_fantasia_base.py`
   (raças, magias, kits, pesos).
   - Arquivos exigidos pelo `data_loader`: `genero.json`, `player.json`, `archetypes.json`, `modules.json`,
     `equipment.json`, `names.json`, `complications.json`; `powers.json` se houver poderes.
   - Perícias novas (`Especialidade: ...`) precisam passar em `rules.pericia_valida`.
   - Gêneros "realistas" escondem vantagens de super-herói: hoje é uma lista fixa em `player.vantagens_do_jogador`
     (faroeste e cthulhu); acrescente o id novo ou transforme em configuração do `genero.json`.
   - `forca_minima` nas configurações (como no faroeste) evita fichas fracas demais onde isso não faz sentido.
3. **Testes** `tests/test_<id>.py`, no molde de `tests/test_cthulhu.py`: o gênero carrega, todos os arquétipos e focos
   geram fichas válidas nos NPs permitidos, gastam o orçamento exato e o dinheiro inicial nunca é 0.
4. **Escudo do Mestre:** `ferramentas/criar_<id>_escudo.py`, no molde de `criar_cthulhu_escudo.py`. As regras gerais
   (ações, manobras, condições, Tratamento) vêm de `ferramentas/escudo_mm.py`; dano, Aflição e recuperação são blocos
   gerados (`{"tipo": "gerado", "fonte": "dano"}` etc.) com a chave `"letalidade"` (padrão, quais ataques são letais,
   cura no modo mortal). Inclua o gênero nos testes parametrizados de `tests/test_escudo.py`.
5. **Bestiário:** `dados/bestiario/<id>/<categoria>/*.json` e o nome em `NOMES_DOS_GENEROS` (`nucleo/bestiario.py`).
6. **Livros:** `dados/livros/<id>_jogador.md` e `<id>_mestre.md`, seguindo `dados/generos/cthulhu/PREPARACAO_LIVROS.md`
   (as regras de escrita e as armadilhas de lá valem para qualquer gênero).
7. **Documentação:** `README.md` e `PENDENCIAS.md`.

## Armadilhas de regra já encontradas

Valem para qualquer tema (lista completa em `dados/generos/cthulhu/PREPARACAO_LIVROS.md`, seção 7):
Moribundo é Fortitude CD 15 (dois graus de sucesso estabilizam, três de falha matam); o 2º grau de dano é **tonto**;
Aflição tem três graus no livro básico; condições e manobras de outros sistemas (Ataque Total, Tiro Preciso,
Transpassado, Desprevenido) não existem no M&M 3e.
