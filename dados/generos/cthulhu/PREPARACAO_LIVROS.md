# Livros de Chamado de Cthulhu: preparação

Instruções para quem for escrever o **Livro do Jogador** e o **Livro do Mestre** do gênero Chamado de Cthulhu (anos 1920).
Leia este arquivo inteiro antes de começar. O gênero, o escudo e o bestiário já estão prontos; só faltam os livros.

## 1. O que entregar

- `dados/livros/cthulhu_jogador.md` e `dados/livros/cthulhu_mestre.md`, em Markdown simples: títulos `#`, `##`, `###`, listas,
  tabelas, citações `>`, **negrito** e *itálico*. É o que `nucleo/livros.py` sabe converter para .docx.
- Assim que os dois arquivos existirem, o site mostra os botões de download sozinho (`livros.livros_disponiveis`).
- No fim de cada livro, o programa acrescenta um **apêndice gerado dos dados**: ocupações e especialidades, equipamento com preços,
  condições financeiras, complicações e, no livro do mestre, os NPCs. **Não copie essas tabelas para o texto.** Explique as regras
  e remeta ao apêndice ("veja o preço no apêndice"), para o livro não ficar desatualizado quando um JSON mudar.
- Atualize `tests/test_livros.py`: em `test_faroeste_e_fantasia_tem_os_dois_livros`, acrescente
  `assert livros.livros_disponiveis("cthulhu") == ["jogador", "mestre"]`. O teste `test_livros_disponiveis_e_download` já
  passa a baixar os livros novos.
- Ao terminar, atualize o `README.md` (seção "Livros do Jogador e do Mestre") e o `PENDENCIAS.md`.

## 2. Modelos a seguir

Os livros do cyberpunk são o melhor molde: foram revisados contra o livro básico e contra o gerador.

| Livro | Molde | Seções (copie a ordem e adapte) |
|----|----|----|
| Jogador | `dados/livros/cyberpunk_jogador.md` | Antes de começar · Como se joga · Combate · Dano, condições e recuperação · Esforço extra e pontos heroicos · Criando seu personagem · Habilidades e defesas · Perícias · Complicações · Vantagens · Dinheiro · Equipamento · (Sanidade, no lugar de Implantes e Netrunning) · Ocupações · Usando o gerador · Exemplo de ficha · Avanço · Referência rápida |
| Mestre | `dados/livros/cyberpunk_mestre.md` | Como usar · O básico do sistema · Criação de personagem · Ocupações · Combate · Dano letal · Cura · Sanidade (regra completa) · Tomos e magia · Equipamento · Dinheiro e Riqueza · Reputação · A cidade e seus perigos · Locomoção · Lei · Coadjuvantes e criaturas · Apêndice de vantagens · Notas de conversão |

As seções de regras gerais de M&M (testes, combate, condições, dano, Moribundo, Tratamento, esforço extra, pontos heroicos) podem
seguir de perto o texto do cyberpunk, trocando os exemplos para os anos 20. Elas já estão conferidas com o livro básico.

## 3. Regras de escrita

- **Português do Brasil**, frases curtas, voz ativa, termos do M&M em português como no resto do projeto (graduação, CD, NP, PP,
  Esquiva, Aparar, Fortitude, Resistência, Vontade, ferido, tonto, abatido, incapacitado, moribundo).
- **Marque a origem de cada regra** no título da seção, como nos outros livros: **[Básico]** (livro básico de M&M),
  **[Guia do Mestre]**, **[CoC]** (Chamado de Cthulhu 7ª edição, convertido) e **[Casa]** (criada para o projeto).
  Nunca apresente uma regra da casa como se fosse do livro.
- **Não copie trechos** dos livros de referência. Descreva com palavras próprias. O PDF do CoC tem uma **marca d'água com o nome e o
  e-mail do comprador** repetida nas páginas: ela não pode aparecer em nada do projeto, nem em citação.
- Nada de super-herói: os investigadores são pessoas comuns, NP 1 a 5 (padrão 3).
- Termos do CoC ficam em português, com o original em itálico só na primeira vez quando ajudar (*Keeper* → Guardião, aqui "mestre").

## 4. Onde está a verdade (confira antes de escrever um número)

O código é a fonte da verdade. Se o texto e o código discordarem, o código vence; se o código parecer errado, anote em
`PENDENCIAS.md` em vez de inventar.

| Assunto | Onde |
|----|----|
| Sanidade: inicial, máxima, teste d100, insanidade temporária e indefinida, ponto de ruptura | `nucleo/sanidade.py` (funções e constantes) |
| Acessos de loucura (d10), duração, estados de loucura, recuperação de SAN | constantes `ACESSOS_DE_LOUCURA`, `DURACAO_DO_ACESSO`, `ESTADOS_DE_LOUCURA`, `RECUPERACAO_DE_SANIDADE` em `nucleo/sanidade.py` |
| Ocupações, especialidades (focos), prioridades, itens | `dados/generos/cthulhu/player.json`, gerado por `ferramentas/criar_cthulhu_base.py` |
| Condições financeiras e dinheiro inicial | `riqueza` no `player.json` (Pobretão $20 · Pobre $75 · Classe média $250 · Abastado $1.000 · Rico $10.000 · Ricaço $50.000) |
| Equipamento, preços, Velocidade dos veículos | `dados/generos/cthulhu/equipment.json` |
| NPCs do gerador (cultista, policial de ronda) e módulos | `archetypes.json` e `modules.json` |
| Criaturas e perda de SAN ("0/1D6") | `dados/bestiario/cthulhu/` (cultistas e aberrações: carniçal, profundo, mi-go, shoggoth) |
| Resumo de mesa já pronto | `dados/escudo/cthulhu.json`, gerado por `ferramentas/criar_cthulhu_escudo.py`; regras gerais em `ferramentas/escudo_mm.py` |
| Decisões do gênero e mapa de páginas do CoC | `dados/generos/cthulhu/PREPARACAO_GENERO.md` |
| Livro básico de M&M | `referencias/mm/` (PDF) |
| Livro básico do CoC 7ª edição | `referencias/cthulhu/chamado-de-cthulhu---livro-basico-7-edicao.pdf` (páginas no `PREPARACAO_GENERO.md`) |

Para ler os PDFs no Windows, use `PYTHONIOENCODING=utf-8` e extraia página por página (há páginas que quebram a codificação).

## 5. Decisões já tomadas (não reabrir sem o usuário)

- **Época:** anos 1920, Nova Inglaterra (Arkham, Boston, Nova York). Equipamento em dólares da época.
- **Sanidade não é defesa nem habilidade:** é um contador de 0 a 99, rolado em d100. O resto da ficha é M&M com d20.
  - SAN inicial = 45 + 5 × Vontade (máximo 99, nunca acima da SAN máxima).
  - SAN máxima = 99 − 5 × graduação em `Especialidade: Mythos de Cthulhu`. Mythos não se compra na criação: vem de tomos e
    encontros (o cultista do gerador já tem 2 graduações).
  - Teste: d100 ≤ SAN atual é sucesso. 01 sempre sucesso; 100 é desastre (96–100 com SAN abaixo de 50) e perde o máximo.
  - Perdeu 5 ou mais de uma vez: d20 + Intelecto contra CD 10. **Passar** quer dizer que entendeu o horror e enlouquece
    (insanidade temporária); falhar reprime a memória.
  - Perdeu 1/5 da SAN do início do dia (o **ponto de ruptura**, arredondado para cima): insanidade indefinida.
  - SAN 0: insanidade permanente; o investigador deixa de ser PJ.
  - A tabela d10 de acessos de loucura com efeitos em condições do M&M é **[Casa]** (redigida para o projeto, não vem do CoC).
- **Fobias, manias e insanidade indefinida** viram complicações da ficha e dão ponto heroico quando atrapalham.
- **Ocupação** é o arquétipo (rótulo `rotulo_arquetipo`), e **Especialidade** é o foco (`rotulo_foco`). São 15 ocupações.
- **Perícias do CoC → M&M:** tabela em `PREPARACAO_GENERO.md`. Montaria é `Especialidade: Cavalgar` (baseada em Agilidade,
  livro básico p. 76), separada de Veículos; nos anos 20 o gerador prefere Veículos.
- **Vantagens:** o gênero é "realista" como o faroeste (`player.vantagens_do_jogador`): só aparecem as que combinam.
- **Dano letal** para tiros, lâminas, garras e mordidas (Guia do Mestre), como no escudo.
- **Magia:** o gênero ainda não tem `powers.json`. No livro do mestre, trate feitiços e tomos como material de campanha
  (efeitos do M&M com falhas pesadas e custo em SAN), marcados [Casa], sem prometer que o gerador os sorteia.

## 6. Conteúdo por livro

**Livro do Jogador** (o que o jogador precisa para montar e jogar um investigador):
- o tom do horror cósmico e o que é um investigador (pessoa comum, NP baixo, fugir é uma opção);
- regras gerais de M&M com exemplos dos anos 20;
- Sanidade do ponto de vista do jogador: o contador, o teste, o que acontece ao enlouquecer, como recuperar;
- criação: NP, PP, ocupações e especialidades (explicar o papel de cada uma; os números ficam no apêndice);
- perícias com a tabela de conversão do CoC, vantagens recomendadas, complicações de época (Lei Seca, preconceito, trauma da guerra);
- dinheiro e condição financeira, equipamento da época (armas, lanterna, câmera, automóvel);
- como usar o gerador e um **exemplo de ficha completo** gerado pelo próprio site (rode o gerador e transcreva; não invente valores).

**Livro do Mestre** (o que o mestre precisa para conduzir):
- a regra completa de Sanidade, com as tabelas de `nucleo/sanidade.py`, perdas típicas e como pedir o teste;
- insanidade temporária, indefinida e permanente; acessos de loucura; tratamento (sanatório, psicanálise) e recuperação;
- tomos do Mythos: o que ler custa (tempo, SAN) e o que dá (graduações de Mythos, feitiços);
- criaturas: como usar o bestiário, a perda de SAN de cada uma e como escalar o NP (`bestiario.no_np`);
- investigação: pistas, testes de Investigação e Percepção, como não travar a história num teste falho;
- a cidade dos anos 20, a lei, viagens (trem, automóvel), perigos;
- coadjuvantes do gerador (cultista, policial) e apêndice de vantagens.

## 7. Armadilhas já encontradas neste projeto

Erros que apareceram nos escudos e foram corrigidos. Não os repita:
- **Moribundo:** Fortitude CD 15 na hora e a cada rodada; dois graus de sucesso estabilizam; três graus de falha somados matam.
  (Não é CD 10 + 1, nem "três sucessos".)
- **Dano:** 2º grau é **tonto** (não atordoado); 3º grau é **abatido** (tonto e impedido), e no letal também desabilitado.
- **Aflição:** três graus. O salvamento no fim de cada turno tira as condições de 1º e 2º grau; as de 3º grau pedem um minuto ou ajuda.
- **Caído:** atacantes corpo a corpo têm +5 e à distância têm –5.
- **Não existem no M&M 3e:** Transpassado, Dominado, Desprevenido, Ataque Total, Tiro Preciso, Desengajar, Imobilizar,
  Recuperar-se "1/cena". O nome certo é Ataque Imprudente; Recuperar-se é uma vez por conflito.
- **Feito heroico** (ponto heroico) dura até o fim do próximo turno, não a cena inteira.
- **Ponto de ruptura** arredonda para cima (SAN 62 → 13).

## 8. Como conferir antes de entregar

1. `python -m pytest -q -p no:cacheprovider` (cerca de 2,5 minutos; no Windows, com `PYTHONIOENCODING=utf-8`).
2. Baixe os dois livros pelo site (`python app.py`, depois `/livros/cthulhu/jogador.docx` e `/livros/cthulhu/mestre.docx`) e
   abra o .docx: títulos, tabelas e o apêndice no fim.
3. Confira cada número do texto contra a tabela da seção 4 (SAN, preços, NP, perdas de SAN das criaturas).
4. Procure no texto: "atordoado" no 2º grau de dano, "CD 10" no Moribundo e qualquer nome da lista da seção 7.
5. Peça ao usuário a leitura editorial; os livros do faroeste e da fantasia também esperam essa leitura.
