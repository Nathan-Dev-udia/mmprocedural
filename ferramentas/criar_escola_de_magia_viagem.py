"""Gera dados/viagem/escola_de_magia.json: a Rolagem de Eventos da Escola de Magia (castelo, terrenos,
Floresta Proibida e Hogsmeade).

Usa os mesmos campos e as mesmas regras de dados de dados/viagem/fantasia.json (nucleo/viagem.py não muda):
clima (d100 por estação), acontece algo (d20 contra o limiar da área), tipo (d100), qual evento (d6),
criatura (d100 pesado por área, período e lugar) e intensidade (d6).

Enquanto o Bestiário de Criaturas Mágicas não existe, as criaturas apontam para fichas equivalentes do
bestiário de fantasia (com a adaptação em "ficha_base") ou para os arquétipos de NPC do gênero.

Uso: python ferramentas/criar_escola_de_magia_viagem.py  (edite este script, não o JSON)
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "dados" / "viagem" / "escola_de_magia.json"

AREAS_ID = ["Rotina", "Fora de hora", "Proibida", "Mortal"]


def pesos(rotina, fora, proibida, mortal):
    return dict(zip(AREAS_ID, (rotina, fora, proibida, mortal)))


AREAS = [
    {"id": "Rotina", "quando": "Castelo e terrenos em dia comum, com professores e monitores por perto",
     "limiar": 17, "mod_intensidade": -1, "np": "NP 1–3",
     "exemplos": "Ir para a aula, almoço no salão principal, tarde na biblioteca ou nas estufas"},
    {"id": "Fora de hora", "quando": "Lugares permitidos em hora errada, ou cantos pouco vigiados",
     "limiar": 14, "mod_intensidade": 0, "np": "NP 2–4",
     "exemplos": "Corredores depois do toque de recolher, beira do lago, passeio a Hogsmeade"},
    {"id": "Proibida", "quando": "Onde aluno não pode ir: orla da Floresta Proibida, corredor interditado, masmorras fundas",
     "limiar": 11, "mod_intensidade": 1, "np": "NP 3–6",
     "exemplos": "Detenção na Floresta, a ala interditada, passagens secretas para fora do castelo"},
    {"id": "Mortal", "quando": "Coração da Floresta, câmaras esquecidas, noite de lua cheia, ano de ameaça declarada",
     "limiar": 8, "mod_intensidade": 2, "np": "NP 5–9",
     "exemplos": "Ninho de acromântulas, câmara secreta sob o castelo, casa assombrada do vilarejo"},
]

PERIODOS = [
    {"id": "Manhã", "horario": "Café da manhã e aulas da manhã", "mod_evento": -2, "mod_tipo": -10,
     "notas": "Castelo cheio e vigiado. Bom para social, obstáculos e pistas deixadas durante a noite."},
    {"id": "Tarde", "horario": "Aulas da tarde, treinos e tempo livre", "mod_evento": 0, "mod_tipo": 0,
     "notas": "Rivais, treinos de quadribol, aulas nos terrenos; o fim da tarde traz presságios."},
    {"id": "Noite", "horario": "Jantar até a meia-noite (toque de recolher)", "mod_evento": 2, "mod_tipo": 10,
     "notas": "Monitores de ronda, portas trancadas. O que vive na Floresta sai."},
    {"id": "Madrugada", "horario": "Meia-noite ao amanhecer", "mod_evento": 3, "mod_tipo": 15,
     "notas": "A hora das trevas. Prefira sinais e pressão antes do combate."},
]

SITUACOES = [
    {"id": "Circulando", "descricao": "Indo de um lugar a outro ou explorando à vista de todos.", "mod_evento": 0},
    {"id": "Em incursão", "descricao": "Fora da cama ou fora dos limites: chama monitores e o que vive no escuro.",
     "mod_evento": 1},
    {"id": "Escondido", "descricao": "Capa de invisibilidade, passagem secreta ou sala vazia trancada.", "mod_evento": -2},
    {"id": "Lugar protegido", "descricao": "Sala comunal, aula ou ala hospitalar. Só acontece algo se for importante.",
     "mod_evento": -6},
]

ESTACOES = ["Primavera", "Verão", "Outono", "Inverno"]

TERRENOS = [
    {"id": "Corredores", "inclui": "Corredores, escadarias que mudam, salas de aula, torres, biblioteca, salão principal"},
    {"id": "Masmorras", "inclui": "Masmorras, porões, passagens secretas, encanamento, câmaras esquecidas"},
    {"id": "Jardins e lago", "inclui": "Gramados, estufas, lago, campo de quadribol, cabana do guarda-caça"},
    {"id": "Floresta", "inclui": "Floresta Proibida e bosques em volta da escola"},
    {"id": "Vilarejo", "inclui": "Hogsmeade, a estrada até a escola, a estação e a casa assombrada"},
]

ATIVIDADE = {
    "Diurna": {"Manhã": 1.5, "Tarde": 1.5, "Noite": 0.5, "Madrugada": 0.25},
    "Noturna": {"Manhã": 0.25, "Tarde": 0.5, "Noite": 1.5, "Madrugada": 2},
    "Qualquer": {"Manhã": 1, "Tarde": 1, "Noite": 1, "Madrugada": 1},
}


def clima(nome, prim, ver, out, inv, mod_evento, mod_tipo, efeito, regra):
    return {"nome": nome, "pesos": dict(zip(ESTACOES, (prim, ver, out, inv))), "mod_evento": mod_evento,
            "mod_tipo": mod_tipo, "viagem": efeito, "regra": regra}


# Mesmos pesos da fantasia (clima frio e úmido do norte); efeitos pensados para o castelo e os terrenos.
CLIMAS = [
    clima("Céu limpo", 25, 35, 15, 15, 0, 0, "Terrenos cheios de alunos; bom dia para treino de quadribol.",
          "Sem modificadores."),
    clima("Calor intenso", 0, 18, 0, 0, -1, 0, "Alunos no lago e à sombra; as masmorras viram refúgio.",
          "Esforço ao sol à tarde (treino, corrida): Fortitude CD 10 ou Fatigado."),
    clima("Nublado", 20, 12, 25, 20, 0, 0, "Céu de chumbo sobre as torres; o dia parece mais curto.",
          "Sem modificadores."),
    clima("Garoa", 15, 6, 15, 0, 0, 0, "Gramados escorregadios, capas úmidas, lama nas botas.",
          "−1 em Percepção (audição); +2 para seguir pegadas frescas na lama."),
    clima("Chuva forte", 12, 8, 12, 3, -1, 0, "Todo mundo dentro do castelo; o lago sobe e os corredores enchem.",
          "−2 em Percepção; ataques à distância −2 ao ar livre; voo de vassoura: Pilotagem CD 12 por rodada de manobra."),
    clima("Tempestade", 6, 10, 5, 2, -2, 0, "Raios sobre as torres; treino cancelado; o salgueiro se agita.",
          "Ao ar livre: −5 em Percepção e ataques à distância −5; voar exige Pilotagem CD 15 ou cair."),
    clima("Neblina", 12, 4, 15, 10, 2, 10, "O lago some na névoa; a orla da Floresta parece mais perto.",
          "Camuflagem além de 10 m (−5 em Percepção visual); Sobrevivência CD 12 para não se perder nos terrenos."),
    clima("Ventania", 7, 7, 10, 10, 0, 0, "Janelas batem, velas apagam, vassouras desviam.",
          "Ataques à distância −2 ao ar livre; Percepção auditiva −2; voar: Pilotagem CD 10 para manter o rumo."),
    clima("Frio intenso", 3, 0, 3, 20, -1, 0, "Lareiras acesas o dia todo; o lago congela nas bordas.",
          "Fora do castelo sem agasalho ou feitiço de aquecimento: Fortitude CD 10 por período ou Fatigado."),
    clima("Neve", 0, 0, 0, 15, -1, 0, "Terrenos brancos, guerra de bolas de neve, pegadas por toda parte.",
          "+5 para seguir rastros; fora dos caminhos é terreno difícil."),
    clima("Nevasca", 0, 0, 0, 5, -3, 0, "Castelo isolado; o vilarejo e as estufas ficam fora de alcance.",
          "Ao ar livre: −5 em Percepção; deslocamento a 1/4; Fortitude CD 15 por período exposto ou Fatigado."),
]

PISTA = "Pista / presságio"

TIPOS = [
    {"nome": "Encontro social", "pesos": pesos(35, 20, 10, 5), "categoria": None,
     "descricao": "Gente da escola: colegas, professores, fantasmas, retratos, rumores e ganchos."},
    {"nome": "Obstáculo", "pesos": pesos(25, 18, 12, 7), "categoria": None,
     "descricao": "O castelo atrapalha: escada que muda, porta com senha, poltergeist, feitiço mal desfeito."},
    {"nome": "Descoberta", "pesos": pesos(18, 12, 8, 6), "categoria": None,
     "descricao": "Algo para achar: passagem secreta, livro esquecido, objeto perdido, sala que não estava ali."},
    {"nome": PISTA, "pesos": pesos(12, 15, 15, 14), "categoria": "Criatura mágica",
     "descricao": "Sinal de uma criatura sem ela aparecer. A criatura sorteada é quem deixou o sinal."},
    {"nome": "Encrenca com bruxos", "pesos": pesos(5, 13, 13, 10), "categoria": "Bruxo",
     "descricao": "Monitores, zelador, rivais de outra Casa, contrabandistas e bruxos das trevas."},
    {"nome": "Bicho mágico", "pesos": pesos(4, 12, 14, 14), "categoria": "Bicho mágico",
     "descricao": "Criaturas menores (classificação X a XXX): diabretes, fadas mordentes, grindylows, hipogrifos."},
    {"nome": "Criatura perigosa", "pesos": pesos(1, 7, 18, 28), "categoria": "Criatura mágica",
     "descricao": "Criaturas XXXX e XXXXX: trasgos, acromântulas, lobisomens, cão de três cabeças, basilisco."},
    {"nome": "Magia das trevas", "pesos": pesos(0, 3, 10, 16), "categoria": "Trevas",
     "descricao": "Dementadores, bichos-papões, inferi, estátuas enfeitiçadas e maldições antigas."},
]


def ev(nome, descricao, opcoes, reviravolta, periodos):
    return {"nome": nome, "descricao": descricao, "opcoes": opcoes, "reviravolta": reviravolta, "periodos": periodos}


EVENTOS = {
    "Encontro social": [
        ev("Fantasma fofoqueiro", "Um fantasma da Casa atravessa a parede e puxa conversa sobre o que viu ontem à noite.",
           "Ouvir, perguntar, bajular, pedir que vigie alguém.",
           "Ele viu algo de verdade — mas confunde séculos e mistura com uma lembrança de quando era vivo.", "Qualquer"),
        ev("Professor pede um favor", "Um professor chama o grupo no fim da aula: levar um recado, buscar um ingrediente, ajudar um aluno.",
           "Aceitar, negociar pontos para a Casa, inventar uma desculpa.",
           "O favor leva exatamente para perto do mistério; ou o professor está testando o grupo.", "Manhã / Tarde"),
        ev("Aluno do primeiro ano perdido", "Um aluno pequeno chora num patamar; a escada mudou e ele perdeu a aula.",
           "Levar até a sala, ensinar o caminho, ignorar.",
           "Ele ouviu uma voz atrás da parede — ou é o irmão mais novo de um rival.", "Manhã / Tarde"),
        ev("Retrato com segredo", "Um retrato antigo chama o grupo pelo nome e oferece uma informação em troca de companhia.",
           "Conversar, prometer voltar, levar um quadro amigo para visitá-lo.",
           "O retrato conheceu o culpado em vida; ou repassa tudo o que ouve para outro retrato.", "Tarde / Noite"),
        ev("Rumor no salão principal", "Na mesa da Casa, todos comentam um ataque, um sumiço ou um castigo.",
           "Ouvir, perguntar a quem espalhou, desmentir, aumentar o boato.",
           "O boato exagera — ou acerta num detalhe que só o culpado poderia saber.", "Manhã / Noite"),
        ev("Monitor que precisa de ajuda", "Um monitor da Casa admite que perdeu algo importante (a lista de senhas, um aluno, uma chave).",
           "Ajudar em troca de vista grossa, chantagear, denunciar.",
           "O objeto foi roubado de propósito; quem pegou quer que o monitor caia em desgraça.", "Tarde / Noite"),
    ],
    "Obstáculo": [
        ev("A escada mudou", "A escadaria gira no meio do caminho e deixa o grupo num andar errado, diante de uma porta falsa.",
           "Esperar, pular para o patamar (Acrobacia CD 12), achar outro caminho.",
           "O andar errado é o corredor interditado; ou alguém viu o grupo chegar.", "Qualquer"),
        ev("Senha trocada", "O retrato da entrada da sala comunal não aceita a senha de ontem.",
           "Esperar alguém da Casa, convencer o retrato (Persuasão CD 15), procurar o monitor.",
           "Trocaram a senha por causa de uma invasão na noite passada.", "Noite / Madrugada"),
        ev("Poltergeist", "Um poltergeist bloqueia o corredor jogando giz, tinta e cantando o que o grupo está tramando.",
           "Ameaçar com o nome de quem ele teme, subornar, correr (Atletismo CD 12).",
           "O barulho atrai o zelador; ou o poltergeist sabe onde está o que o grupo procura.", "Qualquer"),
        ev("Porta que não abre", "Uma porta trancada por feitiço, e o feitiço comum de destrancar não funciona.",
           "Teoria Mágica CD 15 para descobrir o contrafeitiço, forçar (Força CD 20), procurar outra entrada.",
           "A tranca é recente e de magia avançada: alguém de fora está usando aquela sala.", "Tarde / Noite"),
        ev("Planta solta", "Uma muda das estufas escapou: visgo que se enrosca nas pernas ou mandrágora berrando num vaso caído.",
           "Luz ou fogo contra o visgo, abafadores de ouvido, chamar a professora de Herbologia.",
           "Visgo: Agarrar contra Esquiva CD 15; berro de mandrágora jovem: Fortitude CD 12 ou Atordoado por uma rodada.", "Manhã / Tarde"),
        ev("Feitiço rebatido", "Um feitiço errado de outra turma acerta alguém do grupo: cabelo azul, voz de sapo, pés colados no chão.",
           "Procurar a ala hospitalar, achar o contrafeitiço, ir à aula assim mesmo.",
           "Não foi acidente: um rival quer o grupo fora do treino ou da prova de hoje.", "Manhã / Tarde"),
    ],
    "Descoberta": [
        ev("Passagem secreta", "Uma tapeçaria se mexe com a corrente de ar: atrás dela, um túnel estreito.",
           "Explorar agora, marcar e voltar depois, contar a alguém.",
           "O túnel leva para fora do castelo — e alguém andou por ele há pouco.", "Qualquer"),
        ev("Livro esquecido", "Um livro sem título numa mesa da biblioteca, com anotações à mão nas margens.",
           "Ler, devolver, mostrar a um professor.",
           "As anotações ensinam um feitiço que não está em nenhum currículo; o dono vai querer o livro de volta.", "Tarde / Noite"),
        ev("Sala que não estava ali", "No corredor do sétimo andar, uma porta que o grupo nunca tinha visto.",
           "Entrar, pensar com cuidado no que se quer, sair.",
           "A sala mostra o que o grupo precisa — e guarda vestígios de quem a usou antes.", "Noite / Madrugada"),
        ev("Objeto perdido", "Uma varinha, um diário ou um espelho caído atrás de uma armadura.",
           "Devolver ao dono, guardar, examinar (Teoria Mágica CD 12).",
           "O objeto está enfeitiçado; ou o dono está desaparecido desde a semana passada.", "Qualquer"),
        ev("Ingredientes raros", "Na orla da Floresta ou na estufa trancada, plantas e restos de criaturas úteis para poções.",
           "Colher (Especialidade: Poções CD 12 para não estragar), vender, guardar para a prova.",
           "Algo maior também gosta desse lugar; ou o professor de Poções conta o estoque.", "Manhã / Tarde"),
        ev("Mapa ou recado escondido", "Um pergaminho em branco que reage à varinha, ou um recado preso no fundo de uma gaveta.",
           "Revelar (Aparecium), copiar, levar a um professor.",
           "O recado é de um aluno de décadas atrás e fala do mesmo mistério de agora.", "Tarde / Noite"),
    ],
    PISTA: [
        ev("Pegadas estranhas", "Pegadas recentes na lama dos terrenos ou no pó de um corredor de pedra.",
           "Seguir (Percepção CD 12), medir, avisar o guarda-caça.",
           "As pegadas somem numa parede ou numa passagem; ou aparecem onde nada deveria entrar.", "Manhã / Tarde"),
        ev("Animais mortos", "Galos, corujas ou um cervo mortos perto dos terrenos, alguns sem ferimento visível.",
           "Examinar (Investigação CD 15), contar ao guarda-caça, procurar um padrão.",
           "Alguém está matando ou alimentando a criatura de propósito.", "Manhã"),
        ev("Mascotes em pânico", "Corujas agitadas no corujal, gatos de pelo eriçado, sapos fugindo dos dormitórios.",
           "Acalmar os bichos, ver para onde olham, avisar a Casa.",
           "Os animais sentem o que o grupo ainda não percebeu.", "Qualquer"),
        ev("Marcas na pedra", "Arranhões, teia, gosma ou queimadura numa parede, numa porta ou num tronco.",
           "Examinar (Teoria Mágica ou Natureza CD 12), copiar, comparar com um livro da biblioteca.",
           "A marca é antiga e se repete a cada poucos anos; ou foi feita ontem.", "Qualquer"),
        ev("Som que não é humano", "Um uivo, um sibilo nos canos ou passos pesados do outro lado de uma parede.",
           "Escutar, se trancar, investigar de manhã.",
           "Pode ser uma vítima de verdade — ou uma isca.", "Noite / Madrugada"),
        ev("Covil abandonado", "Ossos roídos, penas, cheiro forte num canto escuro da Floresta ou das masmorras.",
           "Vasculhar, armar uma vigília, contar a um professor.",
           "Está vazio... por enquanto.", "Qualquer"),
    ],
    "Encrenca com bruxos": [
        ev("Pego no flagra", "Uma voz atrás do grupo: \"O que vocês fazem aqui a essa hora?\"",
           "Mentir (Enganação contra Intuição), correr, se esconder, assumir a culpa.",
           "Perder pontos ou ganhar detenção — e a detenção leva a um lugar interessante.", "Noite / Madrugada"),
        ev("Provocação em público", "Alguém hostil encara o grupo diante de plateia e espera uma reação.",
           "Responder com feitiço, responder com palavras, ignorar, chamar um professor.",
           "Ele quer provocar a detenção do grupo; ou só quer ser visto ganhando de alguém.", "Manhã / Tarde"),
        ev("Chantagem", "Alguém sabe da última escapada do grupo e quer um favor em troca de silêncio.",
           "Pagar o favor, virar o jogo, contar tudo antes.",
           "O chantagista também está encrencado e precisa de ajuda de verdade.", "Tarde / Noite"),
        ev("Negócio escuso", "No vilarejo, num banheiro abandonado ou na orla da Floresta, alguém faz uma troca às escondidas.",
           "Observar (Furtividade CD 12), interromper, seguir quem sai.",
           "O que muda de mãos é perigoso; quem fornece é quem o grupo procura.", "Tarde / Noite"),
        ev("Encapuzados", "Figuras de capuz conversam baixo num lugar onde não deveria haver ninguém.",
           "Escutar (Furtividade CD 15), segui-los, avisar um professor.",
           "Um deles é alguém conhecido; ou perceberam o grupo e vão segui-lo de volta.", "Noite / Madrugada"),
        ev("Armadilha armada", "Um feitiço armado na porta, no caldeirão ou na vassoura de alguém do grupo.",
           "Perceber antes (Percepção CD 15), desarmar (Teoria Mágica CD 15), revidar.",
           "A armadilha foi feita para outra pessoa — e quem armou não é um aluno.", "Qualquer"),
    ],
    "Bicho mágico": [
        ev("Gaiola aberta", "Alguém soltou as criaturas da aula de Trato ou de um aluno; estão espalhadas por perto.",
           "Capturar, imobilizar, chamar o professor.",
           "Não foi acidente: alguém queria distrair todo mundo para entrar numa sala.", "Manhã / Tarde"),
        ev("Infestação", "Um ninho numa sala vazia, num armário, no telhado da estufa ou num barco do lago.",
           "Limpar com feitiços, fechar e avisar, vender o que der para alguém.",
           "No meio do ninho está algo que alguém escondeu ali.", "Qualquer"),
        ev("Território marcado", "A criatura se planta no caminho e avança para testar o grupo.",
           "Recuar devagar, mostrar respeito (Intuição CD 12 para notar como), oferecer comida.",
           "Se o grupo recuar, não há confronto; tratada bem, pode virar aliada.", "Manhã / Tarde"),
        ev("Ataque da água ou do mato", "A criatura sai do lago, do mato alto ou de um cano quebrado.",
           "Soltar-se (Força ou Esquiva CD 12), afastar-se, lutar no terreno dela.",
           "Está agitada porque algo maior se mexe por perto.", "Qualquer"),
        ev("Debandada", "Bichos passam correndo pelos terrenos ou pelo corredor, fugindo de algo.",
           "Sair da frente (Esquiva CD 12), seguir na direção contrária, ver do que fogem.",
           "Funciona como presságio de algo maior.", "Qualquer"),
        ev("Mãe com filhotes", "Um ninho com filhotes num canto dos terrenos ou da Floresta.",
           "Recuar, observar, levar um filhote (péssima ideia).",
           "Ferir a mãe atrai a ira do guarda-caça — e de algo da Floresta.", "Manhã / Tarde"),
    ],
    "Criatura perigosa": [
        ev("Gritos adiante", "Um aluno ou um animal grita um pouco à frente.",
           "Correr para ajudar, chamar professores, distrair a criatura.",
           "Salvar alguém rende pontos para a Casa, um aliado ou uma dívida.", "Qualquer"),
        ev("Fora da trilha", "O grupo se desviou do caminho e está no lugar da criatura.",
           "Voltar para a trilha, luz forte, lutar de costas umas para as outras.",
           "A criatura pode ser convencida a deixar o grupo sair em troca de algo.", "Noite / Madrugada"),
        ev("Algo guardado", "Atrás de uma porta trancada, uma criatura vigia um alçapão, um baú ou uma passagem.",
           "Fechar a porta, distrair, descobrir o ponto fraco antes de voltar.",
           "Quem a pôs ali é um adulto da escola, e o que ela guarda é o centro do mistério.", "Noite / Madrugada"),
        ev("Perseguição", "Algo segue o grupo há horas pela Floresta ou pelos corredores, sem se mostrar.",
           "Correr para um lugar iluminado, montar uma armadilha, enfrentar.",
           "Ataca quando o grupo parar; ou só queria afastá-lo do covil.", "Noite / Madrugada"),
        ev("Solta no castelo", "A criatura está onde nunca deveria estar: no banheiro, na biblioteca, no salão vazio.",
           "Trancar, distrair, lutar, correr para os professores.",
           "Alguém a soltou de propósito, para desviar a atenção de outro lugar.", "Qualquer"),
        ev("Detenção na Floresta", "O guarda-caça precisa de ajuda: algo está ferindo as criaturas da Floresta.",
           "Seguir o rastro, ficar em grupo, sinalizar com faíscas vermelhas.",
           "Vira missão; não precisa terminar nesta noite.", "Noite"),
    ],
    "Magia das trevas": [
        ev("Frio e escuridão", "As tochas enfraquecem, a respiração vira fumaça e todos lembram de algo triste.",
           "Fugir para um lugar iluminado, buscar ajuda, enfrentar com a varinha erguida.",
           "A coisa não deveria estar ali; alguém abriu uma brecha nas proteções da escola.", "Noite / Madrugada"),
        ev("Sala vazia", "Uma sala, armário ou corredor que todos evitam; algo se move lá dentro.",
           "Abrir e enfrentar (Vontade), trancar, chamar um professor.",
           "O que está ali conhece o pior medo de cada um.", "Qualquer"),
        ev("Guardião desperto", "Algo parado há muito tempo acorda quando o grupo passa.",
           "Recuar, procurar quem o despertou, descobrir o que ele guarda.",
           "Foi deixado ali há séculos para guardar algo, e reconhece o grupo como intruso.", "Noite / Madrugada"),
        ev("Água escura", "Num lago subterrâneo, no lago da escola ou numa poça grande demais, formas pálidas sob a superfície.",
           "Não tocar na água, fogo, recuar devagar.",
           "Estão guardando um objeto amaldiçoado; tocá-lo acorda todos.", "Noite / Madrugada"),
        ev("Objeto amaldiçoado", "Um colar, um livro ou uma taça que chama a mão de quem olha.",
           "Não tocar (Vontade CD 15), embrulhar, levar a um professor.",
           "A maldição já pegou alguém da escola, que agora age estranho; a criatura sorteada o protege.", "Qualquer"),
        ev("Sinal no céu", "Uma marca verde brilha sobre o vilarejo ou sobre a Floresta.",
           "Correr para o castelo, procurar feridos, ir ver de perto.",
           "É um recado para alguém da escola; ou uma distração para outra coisa.", "Noite / Madrugada"),
    ],
}


def criatura(categoria, nome, ficha_base, bestiario_id, np, atividade, terrenos, grupo, p, nota):
    return {"categoria": categoria, "nome": nome, "ficha_base": ficha_base, "bestiario_id": bestiario_id, "np": np,
            "atividade": atividade, "terrenos": terrenos, "grupo": grupo, "pesos": pesos(*p), "nota": nota}


CRIATURAS = [
    # Bruxos (arquétipos de NPC do gênero)
    criatura("Bruxo", "Monitor de ronda", "Arquétipo: Monitor da Escola", None, "2–4", "Noturna",
             ["Corredores", "Masmorras"], "1–2", (6, 6, 3, 1),
             "Não quer ferir ninguém: tira pontos e leva à detenção. Lábia ou fuga resolvem."),
    criatura("Bruxo", "Zelador e sua gata", "Arquétipo: Monitor da Escola (sem varinha; Percepção +4)", None, "2–3",
             "Qualquer", ["Corredores", "Masmorras"], "1 + a gata (Percepção +8)", (5, 5, 3, 1),
             "Não duela: tudo o que vê vira detenção. A gata chega um turno antes dele."),
    criatura("Bruxo", "Rivais de outra Casa", "Arquétipo: Estudante Rival", None, "1–3", "Diurna",
             ["Corredores", "Jardins e lago", "Vilarejo"], "2–3 alunos (NP do grupo −1)", (6, 6, 4, 2),
             "Duelam por orgulho e fogem se aparecer um professor. Nada letal."),
    criatura("Bruxo", "Contrabandista", "Arquétipo: Bruxo das Trevas (NP −2; sem Maldições Imperdoáveis)", None, "3–4",
             "Qualquer", ["Vilarejo", "Floresta"], "1–2", (1, 3, 4, 3),
             "Prefere negociar e sumir a lutar com alunos. Leva artefatos e ovos de criaturas proibidas."),
    criatura("Bruxo", "Caçador de criaturas", "Arquétipo: Bruxo das Trevas (sem Maldições; + Sobrevivência e armadilhas)",
             None, "4–5", "Diurna", ["Floresta", "Jardins e lago"], "1–3", (1, 3, 5, 4),
             "Caça ilegal na Floresta. Usa redes e Feitiços Estuporantes, não feitiços letais."),
    criatura("Bruxo", "Patrulha do Ministério", "Arquétipo: Auror do Ministério", None, "5–7", "Qualquer",
             ["Vilarejo", "Jardins e lago"], "2", (1, 2, 3, 3),
             "Hostil só com quem está onde não devia. Interroga, confisca varinhas, avisa o diretor."),
    criatura("Bruxo", "Bruxo das trevas infiltrado", "Arquétipo: Bruxo das Trevas", None, "5–8", "Noturna",
             ["Floresta", "Masmorras", "Vilarejo"], "1 + 1–3 seguidores (Estudante Rival)", (0, 1, 4, 6),
             "O único que pode usar Maldições Imperdoáveis. Foge se for reconhecido."),

    # Bichos mágicos (X a XXX): fichas equivalentes do bestiário de fantasia
    criatura("Bicho mágico", "Diabretes azuis", "Diabrete (sem fogo; voo e arremesso de objetos)",
             "fantasia/sobrenatural/diabrete", "2–3", "Diurna", ["Corredores", "Jardins e lago"],
             "Enxame de 6–10 (trate como 2–3 capangas)", (6, 5, 3, 2),
             "Bagunçam mais do que ferem: roubam varinhas, puxam orelhas, penduram alunos no lustre."),
    criatura("Bicho mágico", "Fadas mordentes", "Fada Trapaceira (+ mordida venenosa: Aflição de Fortitude, Tonto)",
             "fantasia/sobrenatural/fada", "2–3", "Diurna", ["Corredores", "Jardins e lago", "Vilarejo"],
             "4–8 (trate como 2 capangas)", (4, 4, 2, 1),
             "Infestam cortinas e armários velhos. Um borrifo de repelente resolve o ninho."),
    criatura("Bicho mágico", "Gnomos de jardim", "Goblin Saqueador (sem armas; mordida)",
             "fantasia/goblins/goblin_saqueador", "1–2", "Diurna", ["Jardins e lago", "Vilarejo"], "3–6", (4, 3, 1, 1),
             "Girar e arremessar um gnomo longe resolve. Voltam em uma hora."),
    criatura("Bicho mágico", "Grindylows", "Goblin Saqueador (+ Natação; dedos que agarram)",
             "fantasia/goblins/goblin_saqueador", "2–3", "Qualquer", ["Jardins e lago", "Masmorras"], "2–5", (2, 4, 3, 2),
             "Só atacam na água ou na margem. Dedos frágeis: quebrar a pegada é Força CD 10."),
    criatura("Bicho mágico", "Hipogrifo", "Grifo de Montaria (orgulhoso; ataca quem não fizer reverência)",
             "fantasia/monstruosidades/grifo_montaria", "4–5", "Diurna", ["Jardins e lago", "Floresta"], "1",
             (1, 4, 5, 3), "Reverência e olhar firme (Intuição CD 15) evitam o ataque e podem render um voo."),
    criatura("Bicho mágico", "Lobos da Floresta", "Lobo", "fantasia/feras/lobo", "2–3", "Noturna",
             ["Floresta", "Jardins e lago"], "3–6", (0, 2, 5, 5),
             "Medrosos perto de luz e fogo. Fogem ao perder dois da matilha."),

    # Criaturas perigosas (XXXX e XXXXX)
    criatura("Criatura mágica", "Trasgo montanhês", "Troll (NP −2; Intelecto −4; porrete; sem regeneração)",
             "fantasia/monstruosidades/troll", "5", "Qualquer", ["Masmorras", "Floresta", "Corredores"], "1",
             (2, 3, 4, 4), "Burro e lento: trancar numa sala ou fazer o porrete cair na cabeça dele vale como vitória."),
    criatura("Criatura mágica", "Salgueiro furioso", "Árvore Animada (NP −3; não se desloca; alcance 10 m)",
             "fantasia/sobrenatural/arvore_animada", "5", "Qualquer", ["Jardins e lago"], "1", (1, 3, 2, 1),
             "Não sai do lugar: sair do alcance encerra o combate. Tocar o nó da raiz o imobiliza."),
    criatura("Criatura mágica", "Centauros hostis", "Hobgoblin Soldado (Velocidade 2; arco longo; Especialidade: Astronomia)",
             "fantasia/goblins/hobgoblin_soldado", "4–5", "Qualquer", ["Floresta"], "2–4", (0, 2, 5, 4),
             "Não toleram humanos na mata deles. Respeito e conversa sobre as estrelas abrem caminho."),
    criatura("Criatura mágica", "Acromântulas", "Lobo Atroz (oito patas; Escalar paredes; mordida venenosa, Aflição de Fortitude)",
             "fantasia/feras/lobo_atroz", "4–6", "Noturna", ["Floresta"],
             "2–6; a matriarca (NP +2) só no ninho", (0, 1, 5, 8),
             "Fogo e luz forte as afastam. Algumas falam, e todas querem carne fresca."),
    criatura("Criatura mágica", "Lobisomem", "Lobisomem", "fantasia/monstruosidades/lobisomem", "6–8", "Noturna",
             ["Floresta", "Jardins e lago", "Vilarejo"], "1", (0, 1, 3, 4),
             "Só na lua cheia. A mordida transmite a licantropia (complicação permanente). É alguém de dia."),
    criatura("Criatura mágica", "Cão de três cabeças", "Quimera (três cabeças caninas; sem asas nem fogo)",
             "fantasia/monstruosidades/quimera", "7–8", "Qualquer", ["Masmorras", "Corredores"], "1", (0, 1, 3, 3),
             "Guarda alguma coisa. Música o faz dormir (Atuação CD 15 por rodada)."),
    criatura("Criatura mágica", "Basilisco", "Basilisco (olhar: Aflição de Fortitude; pelo reflexo, só Paralisado)",
             "fantasia/monstruosidades/basilisco", "8–9", "Qualquer", ["Masmorras"], "1", (0, 0, 1, 3),
             "Vive nos canos e câmaras sob o castelo. O canto do galo o fere; olhar por espelho salva vidas."),
    criatura("Criatura mágica", "Dragão jovem", "Serpe (sopro de fogo em vez do ferrão)", "fantasia/dragoes/serpe",
             "7–8", "Diurna", ["Floresta", "Jardins e lago"], "1", (0, 0, 1, 2),
             "Contrabandeado para a escola ou trazido para um torneio. Protege os ovos acima de tudo."),

    # Trevas
    criatura("Trevas", "Bicho-papão", "Sombra Voraz (toma a forma do maior medo; dano de Vontade em vez de Força)",
             "fantasia/mortos_vivos/sombra", "3–5", "Qualquer", ["Corredores", "Masmorras"], "1", (3, 3, 2, 1),
             "Riddikulus e uma risada (Vontade CD 12) o desfazem. Grupos o confundem."),
    criatura("Trevas", "Estátua enfeitiçada", "Gárgula (estátua ou armadura animada por feitiço antigo)",
             "fantasia/sobrenatural/gargula", "4–5", "Noturna", ["Corredores", "Masmorras"], "1–2", (2, 2, 2, 1),
             "Guarda uma porta ou um objeto. Para de atacar quem sai do corredor."),
    criatura("Trevas", "Inferi", "Zumbi (frio, molhado; fogo causa +2 de dano)", "fantasia/mortos_vivos/zumbi",
             "3–4", "Noturna", ["Masmorras", "Jardins e lago"], "3–8", (0, 1, 3, 5),
             "Saem da água escura quando algo é tocado. Fogo os mantém à distância."),
    criatura("Trevas", "Vampiro", "Cria Vampírica", "fantasia/mortos_vivos/cria_vampirica", "6", "Noturna",
             ["Vilarejo", "Floresta"], "1", (0, 1, 2, 3),
             "Frequenta o vilarejo à noite. Educado, faminto e sempre com uma proposta."),
    criatura("Trevas", "Dementador", "Aparição (Aflição de Vontade: Tonto, Atordoado, Incapacitado; o Beijo é Dreno)",
             "fantasia/mortos_vivos/aparicao", "7", "Qualquer", ["Jardins e lago", "Vilarejo", "Floresta"],
             "1–3; dezenas em ano de ameaça", (0, 1, 3, 5),
             "O Patrono o afasta (Teoria Mágica CD 15 para conjurar; CD 20 sob o efeito). Chocolate depois."),
]

INTENSIDADE = [
    {"nome": "Só sinais", "descricao": "Está longe ou evita o grupo. Deixa rastros, sons ou restos.",
     "solo": "Ótimo para tensão; nenhum teste obrigatório."},
    {"nome": "Avistamento", "descricao": "Percebe o grupo e observa. Furtividade, Enganação ou voltar pelo mesmo caminho evitam o confronto.",
     "solo": "Deixe o jogador escolher se quer o confronto."},
    {"nome": "Encontro menor", "descricao": "Mínimo do grupo típico, ou um indivíduo jovem, sozinho ou distraído.",
     "solo": "Confronto curto e vencível."},
    {"nome": "Encontro padrão", "descricao": "Grupo típico, sem vantagens especiais.",
     "solo": "Use o grupo típico como teto."},
    {"nome": "No terreno dela", "descricao": "Grupo típico com vantagem de terreno: água, escuridão, teias, corredor estreito.",
     "solo": "Correr para o castelo iluminado deve ser uma saída real."},
    {"nome": "Grupo grande", "descricao": "Máximo do grupo típico, ou reforço chega na 3ª rodada.",
     "solo": "Troque inimigos extras por pressão: perseguição, porta fechando, toque de recolher."},
    {"nome": "Emboscada", "descricao": "Surpreende o grupo (rodada de surpresa) a menos que alguém passe em Percepção CD 15.",
     "solo": "Surpresa sim; dano extra não."},
    {"nome": "Emboscada + complicação", "descricao": "Como 7, e algo piora: uma varinha cai longe, um monitor vem chegando ou uma segunda ameaça observa.",
     "solo": "A complicação é o problema; o inimigo continua do tamanho padrão."},
]


def montar():
    return {
        "genero": "escola_de_magia",
        "nome": "Escola de Magia",
        "descricao": "Um dia no castelo: corredores, masmorras, terrenos, Floresta Proibida e Hogsmeade, "
                     "com criaturas adaptadas do bestiário e os NPCs do gênero.",
        "areas": AREAS,
        "periodos": PERIODOS,
        "situacoes": SITUACOES,
        "estacoes": ESTACOES,
        "terrenos": TERRENOS,
        "atividade": ATIVIDADE,
        "fator_fora_do_terreno": 0.1,
        "climas": CLIMAS,
        "tipos": TIPOS,
        "eventos": EVENTOS,
        "criaturas": CRIATURAS,
        "intensidade": INTENSIDADE,
    }


def main():
    dados = montar()
    for estacao in ESTACOES:
        assert sum(c["pesos"][estacao] for c in CLIMAS) == 100, estacao
    for area in AREAS_ID:
        assert sum(t["pesos"][area] for t in TIPOS) == 100, area
    assert all(len(EVENTOS[t["nome"]]) == 6 for t in TIPOS)
    DESTINO.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gerado {DESTINO.relative_to(RAIZ)}: {len(CRIATURAS)} criaturas, "
          f"{sum(len(v) for v in EVENTOS.values())} eventos.")


if __name__ == "__main__":
    main()
