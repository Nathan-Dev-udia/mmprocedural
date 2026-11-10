"""Gera o arquivo dados/escudo/cyberpunk.json para o Escudo do Mestre do Cyberpunk.

O conteúdo resume o Livro do Mestre do gênero (dados/livros/cyberpunk_mestre.md): as regras do livro básico de M&M
com os exemplos do Futuro Sombrio e as conversões do Cyberpunk RED (munição, lesões críticas, Humanidade, NET,
custo de vida). Cada bloco cita a seção do livro de onde saiu. Os blocos 'gerado' são calculados por
nucleo/escudo.py.

Uso: python ferramentas/criar_cyberpunk_escudo.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "dados" / "escudo" / "cyberpunk.json"


def tabela(titulo, colunas, linhas, nota=None, **extra):
    bloco = {"tipo": "tabela", "titulo": titulo, "colunas": colunas, "linhas": linhas}
    if nota:
        bloco["nota"] = nota
    return dict(bloco, **extra)


def lista(titulo, itens, tipo="lista"):
    return {"tipo": tipo, "titulo": titulo, "itens": itens}


# ---------------------------------------------------------------- Testes (seções 2.1 a 2.3, 2.6 e 2.7)

TESTES = {"id": "testes", "nome": "Testes", "blocos": [
    lista("Fórmulas", [
        "**Teste** = d20 + graduação + modificadores, contra a CD",
        "**Rotina** = 10 + graduação (sem pressão; o jogador pode rolar se o 10 não bastar)",
        "**Ataque** = d20 + bônus de ataque, contra defesa + 10 (Aparar corpo a corpo, Esquiva à distância)",
        "**Salvamento contra efeito** = d20 + defesa, contra 10 + graduação",
        "**Salvamento contra dano** = d20 + Resistência, contra 15 + Dano",
        "**DV do RED** → CD = DV + 5 (DV 13 → CD 18; DV 15 → CD 20; DV 17 → CD 22)",
    ], tipo="formulas"),
    tabela("Classes de dificuldade", ["CD", "Dificuldade", "Exemplo no Futuro Sombrio"], [
        ["0", "Muito fácil", "Perceber um drone de propaganda bem à vista"],
        ["5", "Fácil", "Subir uma escada de incêndio enferrujada"],
        ["10", "Médio", "Ouvir o elevador chegando ao andar"],
        ["15", "Difícil", "Desligar o alarme de uma loja comum"],
        ["20", "Desafiador", "Invadir o sistema de um prédio residencial"],
        ["25", "Formidável", "Escalar a fachada de vidro de uma torre corporativa"],
        ["30", "Heroico", "Convencer o segurança corporativo a deixar você subir sem crachá"],
        ["35", "Super-heroico", "Seguir o rastro digital de um netrunner veterano"],
        ["40", "Quase impossível", "—"],
    ]),
    tabela("Graus de sucesso e de falha", ["Resultado", "Grau"], [
        ["CD + 15 ou mais", "4 graus de sucesso"],
        ["CD + 10 a + 14", "3 graus de sucesso"],
        ["CD + 5 a + 9", "2 graus de sucesso"],
        ["CD a CD + 4", "1 grau de sucesso"],
        ["CD – 1 a CD – 5", "1 grau de falha"],
        ["CD – 6 a CD – 10", "2 graus de falha"],
        ["CD – 11 a CD – 15", "3 graus de falha"],
        ["CD – 16 ou menos", "4 graus de falha"],
    ], nota="20 natural: o resultado sobe um grau. Em ataques, 20 sempre acerta e 1 sempre erra."),
    tabela("Testes opostos", ["Situação", "Quem age", "Quem resiste"], [
        ["Esgueirar-se pelo corredor da corporação", "Furtividade", "Percepção"],
        ["Blefar para o segurança da boate", "Enganação", "Intuição"],
        ["Bater a carteira (ou o Agente) no metrô", "Prestidigitação", "Percepção"],
        ["Encarada (Facedown) antes do tiroteio", "Intimidação", "Intimidação"],
        ["Fintar no combate", "Enganação", "Enganação ou Intuição"],
        ["Derrubar", "Acrobacia ou Atletismo", "Acrobacia ou Atletismo"],
        ["Agarrar", "Ataque", "Força ou Esquiva"],
        ["Escapar de quem agarra", "Acrobacia ou Atletismo", "Força de quem agarra"],
        ["Passar por um ICE na NET", "Tecnologia", "d20 + 2 × graduação do ICE"],
        ["Esconder uma pistola na roupa", "Prestidigitação", "Percepção"],
    ], nota="Os dois lados rolam e vence o maior total. Empate: vence quem tem o maior bônus."),
    lista("Modificadores e ajuda", [
        "**Circunstância:** +2 ou –2 para uma pequena vantagem ou desvantagem; +5 ou –5 para uma grande.",
        "**Ferramentas:** sem a ferramenta certa, –5; com ferramenta improvisada, –2. No Futuro Sombrio, a "
        "ferramenta certa quase sempre é eletrônica: Bolsa Tech, Bolsa Medtech, cyberdeck, Agente.",
        "**Teste de equipe:** os ajudantes fazem o mesmo teste contra CD 10. Um grau de sucesso dá +2 ao líder; três "
        "graus ou mais, +5; dois graus de falha, –2.",
        "**Ter algo à mão:** com permissão do mestre, 1 ponto heroico faz um item comum aparecer na cena.",
    ]),
    lista("Esforço extra", [
        "Uma vez por turno, ação livre. Escolha: **ação** padrão extra; **+2** num teste (ou +2 vira +5); "
        "**salvamento** extra contra efeito em andamento; **+1 Velocidade ou Força** até o próximo turno; "
        "**+1 num implante** ou uma façanha de poder.",
        "**Custo:** fatigado no início do próximo turno (fatigado vira exausto; exausto vira incapacitado). Um ponto "
        "heroico anula a fadiga.",
        "Equipamento não aceita esforço extra (gaste um ponto heroico); implantes são poderes e aceitam.",
    ]),
    lista("Pontos heroicos", [
        "Cada jogador começa a sessão com **1 ponto heroico**; os não gastos não passam para a próxima aventura.",
        "**Melhorar uma rolagem:** rerrole o d20; de 1 a 10 no novo dado, some 10 (fica entre 11 e 20).",
        "**Feito heroico:** uma graduação de vantagem (que não seja de sorte) até o fim do próximo turno.",
        "**Recuperar-se:** remove tonto, atordoado ou fatigado sem gastar ação, ou converte exausto em fatigado.",
        "**Editar a cena**, **Inspiração** (uma pista do mestre) ou **repelir** um efeito como reação.",
    ]),
]}

# ---------------------------------------------------------------- Combate (seções 2.5 e 5.1 a 5.6)

COMBATE = {"id": "combate", "nome": "Combate", "blocos": [
    tabela("Ações", ["Ação", "Tipo", "Efeito"], [
        ["Atacar", "Padrão", "Um teste de ataque contra um alvo ao alcance."],
        ["Mirar", "Padrão", "+5 no próximo ataque corpo a corpo ou à queima-roupa; +2 à distância. Fica vulnerável "
                            "enquanto mira, e a próxima ação tem de ser o ataque."],
        ["Agarrar", "Padrão", "Ataque; o alvo resiste com Força ou Esquiva. 1 grau: restrito; 2 ou mais: amarrado."],
        ["Ajudar", "Padrão", "Ataque contra CD 10; o aliado ganha +2 no ataque ou na defesa (+5 com três graus)."],
        ["Carga", "Padrão", "Move-se a toda velocidade em linha reta e ataca corpo a corpo com –2."],
        ["Defender-se", "Padrão", "Até o próximo turno, a defesa ativa vira teste oposto; 10 ou menos no dado vale +10."],
        ["Derrubar", "Padrão", "Ataque corpo a corpo com –2; depois, teste oposto de Acrobacia ou Atletismo."],
        ["Desarmar", "Padrão", "Ataque com –2 (–5 à distância), depois dano contra a Força do alvo."],
        ["Quebrar", "Padrão", "Ataque com –5 contra um objeto segurado."],
        ["Recuperar-se", "Padrão", "Uma vez por conflito: remove a pior condição de dano ou fadiga (ou dá um "
                                   "salvamento extra) e +2 nas defesas ativas até o próximo turno."],
        ["Preparar", "Padrão", "Define uma ação e o gatilho; age como reação quando ele acontecer."],
        ["Mover-se", "Movimento", "Até a sua velocidade. Atletismo CD 15 (livre) dá +1 de velocidade por uma rodada."],
        ["Sacar ou guardar arma", "Movimento", "Livre com a vantagem Saque Rápido."],
        ["Recarregar", "Movimento", "Troca o carregador. Livre com Saque Rápido."],
        ["Levantar-se", "Movimento", "Livre com Acrobacia CD 20 ou com a vantagem De Pé."],
        ["Comandar", "Movimento", "Dá uma ordem a um capanga ou drone."],
        ["Dirigir", "Movimento", "Teste de Veículos. Com Interface neural, dirige sem as mãos e atira com as duas."],
        ["Jogar-se no chão", "Livre", "Fica caído (–5 para quem atira em você de longe)."],
        ["Atrasar", "Nenhuma", "Age mais tarde na ordem de iniciativa."],
    ]),
    tabela("Manobras", ["Manobra", "Efeito"], [
        ["Ataque Acurado", "Até –2 no efeito para +2 no ataque."],
        ["Ataque Poderoso", "Até –2 no ataque para +2 no efeito."],
        ["Ataque Defensivo", "Até –2 no ataque para +2 em Esquiva e Aparar."],
        ["Ataque Imprudente", "Até –2 em Esquiva e Aparar para +2 no ataque."],
        ["Ataque de Equipe", "Atiradores atrasam para o mesmo ponto da iniciativa; cada acerto extra soma +2 (+5 com "
                             "três graus) ao dano principal."],
        ["Ataque Surpresa", "Alvo pego de surpresa fica vulnerável."],
        ["Ataque Final", "Contra alvo indefeso ao alcance perto: ataque de rotina, ou rolado e todo acerto é crítico."],
        ["Desmoralizar", "Intimidação contra Intuição ou Vontade: alvo prejudicado (desabilitado com quatro graus) até "
                         "o fim do próximo turno dele."],
        ["Fintar", "Enganação contra Enganação ou Intuição: alvo vulnerável contra o seu próximo ataque."],
        ["Encontrão", "Durante uma carga (de moto, por exemplo), o dano usa a velocidade +1; você sofre metade."],
    ], nota="Os ajustes valem até o início do próximo turno. Com a vantagem de mesmo nome, a troca vai até 5 pontos."),
    tabela("Alcance", ["Alcance", "Distância", "Ataque"], [
        ["Curto", "graduação de dano × 7,5 m", "sem penalidade"],
        ["Médio", "graduação de dano × 15 m", "–2"],
        ["Longo", "graduação de dano × 30 m", "–5"],
    ], nota="Além do alcance longo, não dá para atacar. Fuzil de assalto (Dano 5): 37,5 m sem penalidade."),
    tabela("Camuflagem e cobertura", ["Situação", "Ataque", "Exemplos"], [
        ["Camuflagem parcial", "–2", "Pouca luz, chuva ácida, fumaça, neon piscando"],
        ["Camuflagem total", "–5", "Escuridão total, granada de fumaça (cyberolhos com visão noturna ignoram o escuro)"],
        ["Cobertura parcial", "–2", "Metade do corpo atrás da porta do carro ou de uma pilastra"],
        ["Cobertura total", "–5", "Três quartos protegidos: atirando por cima do balcão do bar"],
        ["Cobertura completa", "não ataca", "100% atrás da barreira: só com Indireto, Ricochetear ou destruindo-a"],
    ], nota="A cobertura soma o mesmo valor na Esquiva contra explosões. Ataque Preciso ignora a penalidade "
            "(cobertura completa continua impedindo)."),
    lista("Iniciativa, surpresa e capangas", [
        "**Iniciativa:** d20 + Agilidade + 4 por graduação de Iniciativa Aprimorada. Empate: Esquiva, depois "
        "Agilidade, depois Prontidão. Capangas rolam uma vez para o grupo.",
        "**Surpresa:** quem foi pego desprevenido fica atordoado e vulnerável na rodada de surpresa; os demais só têm "
        "uma ação padrão ou de movimento.",
        "**Capangas:** gangueiros e seguranças de portaria não fazem críticos contra quem não é capanga; os heróis os "
        "atacam com testes de rotina; qualquer falha num salvamento aplica o pior grau.",
        "**Força e dano:** armas brancas e arremessadas somam a Força; armas de fogo e arcos não.",
    ]),
]}

# ---------------------------------------------------------------- Armas e armaduras (seções 5.7, 5.8 e 10.4)

ARMAS = {"id": "armas", "nome": "Armas e armaduras", "blocos": [
    tabela("Modos de disparo", ["Modo", "Custo", "Efeito"], [
        ["Tiro simples", "Padrão, 1 bala", "Ataque normal com o dano da arma."],
        ["Rajada", "Padrão, 10 balas", "Só com Multiataque. Alvo único: +2 no dano com dois graus de sucesso, +5 com "
                                       "três. Vários alvos: um ataque contra cada, com penalidade igual ao número de "
                                       "alvos."],
        ["Fogo de supressão", "Padrão, 10 balas", "Só com Multiataque. Todos a pé num raio de 25 m à frente, fora de "
                                                  "cobertura, fazem Vontade CD 10 + seu bônus de ataque; quem falha "
                                                  "usa a próxima ação de movimento (e, se preciso, a padrão) para se "
                                                  "proteger."],
        ["Tiro mirado [Casa]", "Padrão, –5", "Não pode ser rajada. Cabeça: conta como crítico (+5 na CD) e rola "
                                             "lesão da cabeça. Perna: impedido até Tratamento CD 15. Item segurado: "
                                             "Desarmar sem o –5 extra à distância."],
    ], nota="Smartgun ligada por Interface neural: +2 no ataque com aquela arma (conta no limite do NP)."),
    tabela("Carregadores (RED, p. 94)", ["Arma", "Tiros"], [
        ["Pistola média", "12"],
        ["Pistola pesada e muito pesada", "8"],
        ["SMG", "30"],
        ["SMG pesada", "40"],
        ["Fuzil de assalto", "25"],
        ["Escopeta e fuzil de precisão", "4"],
        ["Lança-granadas", "2"],
    ], nota="Trocar o carregador: ação de movimento (livre com Saque Rápido). Munição básica: 10eb a cada 10 tiros."),
    lista("Escopetas, granadas e explosivos", [
        "**Escopeta com balote:** Dano 5 normal. **Com chumbo:** +2 no ataque, mas Dano no máximo 3 contra quem "
        "tem Proteção.",
        "**Granada:** Área de Explosão; quem está na área faz Esquiva CD 10 + graduação para sofrer metade. "
        "Cobertura entre o alvo e a explosão soma à Esquiva; cobertura que o dano não destrói protege por completo.",
    ]),
    lista("Armadura que se desgasta [RED, opcional]", [
        "Cada salvamento de Resistência **falho** contra uma arma tira **1** da Proteção da armadura vestida "
        "(mínimo 0); munição anti-blindagem tira **2**.",
        "**Conserto:** Tecnologia CD 10 e 1 hora com uma Bolsa Tech devolvem toda a Proteção. Blindagem subdérmica e "
        "Placas dérmicas se recuperam sozinhas, 1 ponto por dia de descanso.",
        "**Golpes contra colete:** coletes balísticos não protegem contra armas brancas; jaqueta de couro, traje "
        "corporal e implantes protegem contra tudo.",
        "**Armaduras pesadas [Casa]:** –1 ou –2 em Esquiva, Acrobacia e Furtividade; –1 de velocidade na flak.",
    ]),
]}

# ---------------------------------------------------------------- Condições, dano e cura (seções 2.8, 5.1, 6 e 7)

CONDICOES = {"id": "condicoes", "nome": "Condições e dano", "blocos": [
    tabela("Dano: padrão e letal", ["Grau de falha", "Padrão (socos, borracha, atordoantes)",
                                    "Letal (tiros, lâminas, explosivos, implantes de ataque)"], [
        ["Sucesso", "Sem efeito.", "Sem efeito."],
        ["1º grau (1 a 5)", "–1 nos próximos salvamentos de Resistência (cumulativo).", "Ferido: –1 na Resistência "
                                                                                       "(cumulativo)."],
        ["2º grau (6 a 10)", "–1 e tonto até o fim do próximo turno.", "Ferido e tonto até o fim do próximo turno."],
        ["3º grau (11 a 15)", "–1 e abatido. Se já estava abatido, aplique o 4º grau.",
         "Ferido, abatido e desabilitado (–5 em todos os testes). Rola uma lesão crítica."],
        ["4º grau (16 ou mais)", "Incapacitado.", "Incapacitado e moribundo. Rola uma lesão crítica."],
    ], nota="Salvamento: d20 + Resistência contra 15 + Dano. Incapacitado que falha fica moribundo; moribundo que "
            "falha morre. Opcional: cinco ou mais graus de falha contra dano letal matam na hora."),
    tabela("Aflição: condição por grau de falha", ["Grau de falha", "Condições possíveis"], [
        ["1º grau (falha por 1 a 5)", "Tonto, em transe, fatigado, impedido, prejudicado ou vulnerável"],
        ["2º grau (falha por 6 a 10)", "Atordoado, caído, compelido, desabilitado, exausto, imóvel ou vulnerável"],
        ["3º grau (falha por 11 a 15)", "Adormecido, controlado, desatento, incapacitado, paralisado ou transformado"],
    ], nota="O efeito define uma condição para cada grau; graus mais altos substituem os mais baixos. No fim de cada "
            "turno, o alvo faz um salvamento para tirar as condições de 1º e 2º grau; as de 3º grau exigem um minuto "
            "ou ajuda (Tratamento CD 10 + graduação)."),
    tabela("Condições básicas", ["Condição", "Efeito"], [
        ["Prejudicado", "–2 em todos os testes (ou nos indicados)."],
        ["Desabilitado", "–5 em todos os testes (ou nos indicados). Sobrepõe prejudicado."],
        ["Tonto", "Só ações livres e uma ação padrão por turno."],
        ["Atordoado", "Não pode fazer nenhuma ação, nem livre. Sobrepõe tonto."],
        ["Impedido", "Move-se à metade (–1 graduação de velocidade)."],
        ["Imóvel", "Não se move do lugar. Sobrepõe impedido."],
        ["Vulnerável", "Esquiva e Aparar pela metade, arredondando para cima."],
        ["Indefeso", "Esquiva e Aparar 0. Atacantes podem fazer ataques de rotina; um ataque rolado que acerte vira "
                     "crítico. Sobrepõe vulnerável."],
        ["Desatento", "Não percebe o ambiente nem age com base nele."],
        ["Fatigado", "Impedido. Some com 1 hora de descanso."],
        ["Compelido / Controlado", "Ações ditadas por outro (um ICE, uma droga, a cyberpsicose)."],
    ]),
    tabela("Condições combinadas", ["Condição", "Efeito"], [
        ["Abatido", "Tonto e impedido."],
        ["Exausto", "Prejudicado e impedido. Some com 1 hora de descanso em lugar confortável."],
        ["Caído", "Impedido; –5 nos ataques corpo a corpo; atacantes têm +5 corpo a corpo e –5 à distância. "
                  "Levantar-se: ação de movimento."],
        ["Restrito", "Impedido e vulnerável (imóvel se preso a algo fixo)."],
        ["Amarrado", "Indefeso, imóvel e prejudicado."],
        ["Surpreso", "Atordoado e vulnerável."],
        ["Cego", "Impedido, visualmente desatento e vulnerável; tudo tem camuflagem total contra ele."],
        ["Incapacitado", "Indefeso, atordoado e desatento; normalmente caído."],
        ["Moribundo", "Incapacitado; Fortitude CD 15 na hora e a cada rodada: dois graus de sucesso estabilizam, três "
                      "graus de falha somados matam."],
    ]),
    lista("Moribundo e cura", [
        "**Moribundo:** Fortitude CD 15 na hora e a cada rodada. Sucesso: nada muda; dois graus de sucesso: "
        "estabiliza (continua incapacitado); três graus de falha somados: morte.",
        "**Estabilizar:** Tratamento CD 15 (ação padrão); com Airhypo e estabilizante, ação de movimento. Duro de "
        "Matar estabiliza sozinho. A Trauma Team chega em minutos e estabiliza o cliente.",
        "**Relógio da cura [Casa]:** 1 condição por dia de descanso, da pior para a melhor (incapacitado → abatido → "
        "ferido; cada –1 na Resistência, 1 dia). Com Medtech cuidando (Tratamento CD 15), 16 horas por condição.",
        "**Ponto heroico:** remove tonto, atordoado ou fatigado na hora. **Nanorreparo:** Regeneração 2.",
    ]),
    tabela("Tratamento (só treinado; sem Bolsa Medtech, –5)", ["Tarefa", "CD", "Efeito"], [
        ["Diagnosticar (1 minuto)", "10", "+2 nos testes seguintes de Tratamento. O escâner médico dá +2."],
        ["Estabilizar (padrão)", "15", "Estanca o sangramento de um moribundo."],
        ["Reviver (padrão)", "15", "Remove tonto ou atordoado; não remove ferimentos."],
        ["Longo prazo (no descanso)", "15", "Reduz a recuperação em 1 graduação de tempo (1 dia → 16 horas)."],
        ["Doença, veneno ou droga", "15", "+2 no salvamento do paciente (+5 com três graus de sucesso)."],
    ], nota="Tratar a si mesmo: só diagnosticar, longo prazo e doenças, venenos ou drogas, com –5."),
]}

# ---------------------------------------------------------------- Lesões críticas e socorro (seções 6.2 e 7.3)

LESOES = {"id": "lesoes", "nome": "Lesões críticas", "blocos": [
    tabela("Lesões no corpo (2d6)", ["2d6", "Lesão", "Efeito", "Correção rápida", "Tratamento"], [
        ["2", "Braço desmembrado", "Perde o braço e solta o que segurava; complicação até ganhar um cyberbraço.", "—",
         "Cirurgia CD 22"],
        ["3", "Mão desmembrada", "Perde a mão e solta o que segurava; complicação até ganhar uma mão cibernética.", "—",
         "Cirurgia CD 22"],
        ["4", "Pulmão perfurado", "Impedido; –2 em Fortitude.", "CD 20", "Cirurgia CD 20"],
        ["5", "Costelas quebradas", "Cada turno em que se move mais da metade da velocidade, novo salvamento de "
                                    "Resistência CD 15 (letal).", "CD 18", "CD 20 ou Cirurgia CD 18"],
        ["6", "Braço quebrado", "Não usa o braço e solta o que segurava.", "CD 18", "CD 20 ou Cirurgia CD 18"],
        ["7", "Objeto alojado", "Como costelas quebradas.", "CD 18", "A correção resolve de vez"],
        ["8", "Perna quebrada", "Impedido (imóvel se já estava impedido).", "CD 18", "CD 20 ou Cirurgia CD 18"],
        ["9", "Lesão muscular", "–2 nos ataques corpo a corpo.", "CD 18", "A correção resolve de vez"],
        ["10", "Lesão na coluna", "Atordoado no próximo turno; depois, prejudicado.", "CD 20", "Cirurgia CD 20"],
        ["11", "Dedos esmagados", "–5 em tudo que use aquela mão.", "CD 18", "Cirurgia CD 20"],
        ["12", "Perna desmembrada", "Imóvel sem muleta; vulnerável; complicação até ganhar uma cyberperna.", "—",
         "Cirurgia CD 22"],
    ], nota="Acontece num crítico com dano letal, no 3º grau de falha ou pior contra dano letal, ou quando um "
            "moribundo é atingido de novo. Soma –1 na Resistência. Lesão repetida: role de novo. Capangas só caem.",
        larga=True),
    tabela("Lesões na cabeça (2d6, tiro mirado na cabeça)", ["2d6", "Lesão", "Efeito", "Correção rápida",
                                                             "Tratamento"], [
        ["2", "Olho perdido", "–5 em ataques à distância e Percepção visual; complicação até ganhar um cyberolho.", "—",
         "Cirurgia CD 22"],
        ["3", "Lesão cerebral", "Prejudicado em tudo.", "—", "Cirurgia CD 22"],
        ["4", "Olho danificado", "–2 em ataques à distância e Percepção visual.", "CD 20", "Cirurgia CD 18"],
        ["5", "Concussão", "Prejudicado em tudo.", "CD 18", "A correção resolve de vez"],
        ["6", "Mandíbula quebrada", "–5 em Persuasão, Enganação e Intimidação.", "CD 18", "CD 18"],
        ["7", "Objeto alojado", "Cada turno em que se move mais da metade da velocidade, novo salvamento de "
                                "Resistência CD 15.", "CD 18", "A correção resolve de vez"],
        ["8", "Lesão no pescoço", "–2 nos testes de Fortitude do moribundo.", "CD 18", "CD 18"],
        ["9", "Fratura no crânio", "Tiros mirados na cabeça contra ele ganham mais +2 no dano.", "CD 20", "CD 20"],
        ["10", "Ouvido danificado", "–2 em Percepção auditiva; depois de correr, não se move no turno seguinte.",
         "CD 18", "Cirurgia CD 18"],
        ["11", "Traqueia esmagada", "Não consegue falar.", "—", "Cirurgia CD 20"],
        ["12", "Orelha perdida", "–5 em Percepção auditiva; depois de correr, não se move no turno seguinte.", "—",
         "Cirurgia CD 22"],
    ], nota="Correção rápida: Tratamento, 1 minuto, remove o efeito até o fim do dia (em si mesmo, –5). Tratamento: "
            "4 horas, remove de vez (não em si mesmo). Cirurgia: Tratamento treinado e Especialidade: Medicina ou "
            "Cibernética, com Bolsa Medtech num lugar limpo. Cyberbraço, cyberperna ou cyberolho: Tecnologia.",
        larga=True),
    tabela("Socorro pago (RED, p. 376)", ["Serviço", "Preço", "No M&M"], [
        ["Tratamento hospitalar simples", "50eb", "Um médico faz Tratamento CD 15 por você."],
        ["Tratamento hospitalar", "100eb", "Correção rápida ou tratamento de uma lesão de CD 18."],
        ["Tratamento hospitalar", "500eb", "Lesão de CD 20."],
        ["Tratamento hospitalar", "1.000eb", "Lesão de CD 22 (cirurgia)."],
        ["Trauma Team Prata", "500eb por mês", "Chega em minutos e estabiliza; a cirurgia é cobrada à parte."],
        ["Trauma Team Executivo", "1.000eb por mês", "Igual, com a cirurgia incluída."],
    ]),
]}

# ---------------------------------------------------------------- Humanidade e NET (seções 8 e 9)

HUMANIDADE_E_NET = {"id": "humanidade", "nome": "Humanidade e NET", "blocos": [
    tabela("Trilha de Humanidade [Casa]", ["Passo", "Estado", "Efeito"], [
        ["0", "Humano", "Nenhum."],
        ["1", "Distante", "–2 em Intuição e Persuasão."],
        ["2", "Frio", "–5 em Intuição e Persuasão; ganha uma complicação de Peculiaridade ou Irritação ligada ao "
                      "cromo."],
        ["3", "Instável", "Igual a Frio. Em tensão, Vontade CD 15 ou fica compelido a atacar a ameaça mais próxima até "
                          "o fim da cena."],
        ["4", "Cyberpsicose", "Vira PNJ, a menos que o grupo o contenha e pague a terapia extrema. A Max-Tac é "
                              "chamada."],
    ]),
    lista("Quando testar a Humanidade", [
        "**Instalar um implante:** Vontade contra CD 10 + metade do custo do implante em PP (para cima) + 1 por "
        "implante que já tem. Com falha, sobe um passo.",
        "**Trauma:** tortura, uma morte horrível, um mês numa zona de guerra: Vontade CD 10 a 20; com falha, sobe um "
        "passo. **Black Lace:** Vontade CD 15 a cada dose.",
        "**Na criação:** começa Humano com até três implantes; a partir do quarto, testa cada um na ordem de compra.",
        "**Terapia:** 500eb por semana, Tratamento (ou Especialidade: Psicologia) CD 20, desce um passo; extrema, "
        "1.000eb, CD 22, desce dois (única saída da Cyberpsicose). Piso: até 3 implantes, Humano; 4 a 6, Distante; "
        "7 ou mais, Frio.",
    ]),
    tabela("Arquiteturas da NET", ["Arquitetura", "DV do RED", "CD", "Graduação do ICE"], [
        ["Básica (lojas, apartamentos)", "6", "15", "4"],
        ["Padrão (empresas pequenas, delegacia)", "8", "20", "6"],
        ["Incomum (filial corporativa)", "10", "25", "8"],
        ["Avançada (sede de megacorporação)", "12", "30", "10"],
    ], nota="Aqui não vale a regra DV + 5: a escala da NET no RED é outra. Cada sistema tem de 3 a 18 andares."),
    lista("Ações na NET", [
        "**Precisa de:** Interface neural e cyberdeck. Sem eles, Tecnologia com –5, só para tarefas simples.",
        "**Descer um andar:** ação padrão, Tecnologia (ou Especialidade: Computação) contra a CD; senha ou arquivo "
        "protegido, –2. **Nó de controle:** outro teste dá controle de câmeras, portas, torretas e drones.",
        "**ICE:** teste oposto de Tecnologia contra d20 + 2 × graduação do ICE. Vencendo, passa sem ser notado ou "
        "ataca (ICE comum cai com um sucesso; ICE negro, com dois). Perdendo, resiste ao ICE com Vontade.",
        "**Programas:** +2 de circunstância num tipo de teste (descer, evitar, atacar ou resistir); 7 vagas no deck.",
        "**Desconectar:** livre; com ICE ativo, Vontade CD 15 ou fica tonto uma rodada. **Ação extra:** esforço "
        "extra. **O corpo:** desatento (sem óculos virtuais) e vulnerável enquanto mergulha.",
    ]),
    tabela("ICE", ["ICE", "Efeito quando vence"], [
        ["Sentinela", "Dispara o alarme e avisa o dono do sistema. Sem dano."],
        ["Vespa", "Aflição (graduação do ICE), Vontade: tonto, atordoado, incapacitado."],
        ["Cão infernal (negro)", "Dano letal (graduação do ICE + 2), resistido por Vontade."],
        ["Kraken (negro)", "Não deixa desconectar até vencer outro teste oposto."],
        ["Liche (negro)", "Aflição (graduação do ICE + 2), Vontade: prejudicado, desabilitado, controlado."],
    ], nota="O Firewall cortical soma +2 na Vontade contra ICE e nos testes de Humanidade."),
]}

# ---------------------------------------------------------------- Locomoção (seções 10.9 e 16)

LOCOMOCAO = {"id": "viagem", "nome": "Locomoção", "blocos": [
    lista("Fórmulas", [
        "**Tempo** = distância – velocidade",
        "**Distância** = tempo + velocidade",
        "**Trânsito de Night City:** +2 graduações de tempo",
    ], tipo="formulas"),
    {"tipo": "gerado", "fonte": "tempo_de_viagem"},
    tabela("Veículos (RED, p. 190–191)", ["Veículo", "Preço", "Velocidade", "Ficha do livro básico"], [
        ["Moto estradeira", "20.000eb", "5 (161 km/h)", "Motocicleta"],
        ["Moto estradeira do clã (gerador)", "emprestada", "6", "Ficha do veículo do Nômade"],
        ["Superbike", "100.000eb", "7 (483 km/h)", "Motocicleta, com +2 de velocidade"],
        ["Carro compacto", "30.000eb", "5 (161 km/h)", "Carro"],
        ["Carro esportivo", "50.000eb", "6 (322 km/h)", "Carro esportivo"],
        ["Supercarro", "100.000eb", "7 (483 km/h)", "Carro esportivo, com +1 de velocidade"],
        ["Jetski", "20.000eb", "5 (97 km/h)", "Lancha"],
        ["Veículos aéreos (girocóptero, AV-4)", "20.000 a 100.000eb", "5 a 7", "Helicóptero ou jato"],
    ], nota="Todos são Super Luxuosos: nenhuma faixa de dinheiro inicial abaixo de Apartamento compra uma moto. Vidro "
            "comum não é cobertura; vidro blindado é."),
    {"tipo": "gerado", "fonte": "carga"},
]}

# ---------------------------------------------------------------- Perigos (seções 10.10 e 15)

PERIGOS = {"id": "perigos", "nome": "Perigos", "blocos": [
    {"tipo": "gerado", "fonte": "queda"},
    lista("Espiral de Fortitude, sono e fome", [
        "**Espiral:** Fortitude CD 10, +1 por teste anterior. Cada falha desce um passo: fatigado, exausto, "
        "incapacitado, moribundo.",
        "**Sem dormir:** cada dia sem 6 horas de sono dá prejudicado cumulativo (–2, depois –5), até dormir.",
        "**Dormir mal:** na rua, Fortitude CD 20; no ermo, Especialidade: Sobrevivência CD 20 (o Nômade rola pelo "
        "grupo). Com falha, acorda fatigado.",
        "**Sede:** 1 dia sem água sem penalidade; depois, Fortitude por hora (CD 10, +1 por hora). **Fome:** 3 dias "
        "sem penalidade; depois, Fortitude por dia. Estilo de vida atrasado: uma semana, depois a espiral de fome.",
    ]),
    tabela("Ar, radiação e química", ["Ameaça", "Exemplo", "Teste"], [
        ["Smog pesado", "Dia ruim na Zona de Combate, perto das refinarias", "Fortitude CD 10 por hora sem máscara; "
                                                                             "falha: fatigado"],
        ["Gás tóxico", "Vazamento industrial, gás de combate", "Fortitude CD 15 a 20 por rodada, ou Dano (ignora "
                                                               "armadura)"],
        ["Radiação", "Ruínas da 4ª Guerra Corporativa", "Fortitude CD 15 por hora; falha: Enfraquecer Vigor 1"],
        ["Chuva ácida", "Tempestade sobre a baía", "Fortitude CD 10 por hora sem abrigo"],
    ], nota="Máscara antismog, Pulmões e filtros sintéticos e a vantagem Tolerância Maior protegem."),
    lista("Outras ameaças", [
        "**Choque elétrico:** fiação exposta é Dano 3 a 5 (ignora armadura de couro e kevlar).",
        "**Afogamento:** prende a respiração por 10 rodadas + 2 × Vigor; depois, Fortitude CD 10 (+1 por teste) "
        "a cada rodada.",
        "**Doença:** Fortitude CD 10 + graduação. Os bairros sem saneamento ainda têm cólera e tuberculose.",
    ]),
    tabela("Drogas (RED, p. 357–358)", ["Droga", "Preço", "Efeito no M&M", "Vício"], [
        ["Black Lace", "50eb", "Ignora o desabilitado do 3º grau letal por 24 horas; teste de Humanidade CD 15.",
         "CD 22"],
        ["Blue Glass", "20eb", "Por 4 horas, o mestre pode deixá-lo tonto por uma rodada de vez em quando.", "CD 20"],
        ["Boost", "50eb", "+1 em Intelecto por 24 horas. Viciado: –1 em Intelecto sem a droga.", "CD 22"],
        ["Smash", "10eb", "+2 em Persuasão e Enganação por 4 horas; –2 em Intuição.", "CD 20"],
        ["Synthcoke", "20eb", "+2 na iniciativa e +1 em Esquiva por 4 horas; paranoia. Viciado: –1 em Destreza.",
         "CD 20"],
    ], nota="Quando a dose passa, Fortitude contra a CD de vício; com falha, ganha a complicação Vício. A terapia de "
            "dependência (1.000eb por semana, Tratamento CD 20) tira o vício."),
]}

# ---------------------------------------------------------------- Objetos (seções 2.4 e 5.3)

OBJETOS = {"id": "objetos", "nome": "Objetos e medidas", "blocos": [
    lista("Fórmulas", [
        "**Arremesso:** distância = Força – massa do objeto",
        "**Quebrar um objeto:** dano do golpe ou tiro contra a Resistência do material",
        "**Destruir a cobertura:** cada grau de falha do objeto abre um buraco maior; com três, ela deixa de existir",
    ], tipo="formulas"),
    tabela("Resistência dos materiais", ["Material", "Fino", "Grosso", "Exemplos (RED, p. 183)"], [
        ["Gesso, espuma, plástico", "0 (não é cobertura)", "2", "Divisória de escritório (fino), sofá (grosso)"],
        ["Vidro comum", "1", "—", "Para-brisa: não é cobertura"],
        ["Madeira", "3", "5", "Porta e mesa virada (fino); balcão do bar e árvore (grosso)"],
        ["Vidro blindado", "5", "7", "Para-brisa à prova de balas (fino); vidro do banco (grosso)"],
        ["Concreto e pedra", "5", "7", "Barricada de concreto, estátua (grosso)"],
        ["Aço", "9", "11", "Porta de carro, contêiner, geladeira (fino); bloco do motor, porta do cofre (grosso)"],
    ], nota="Fino é a Resistência do livro básico para alguns centímetros; grosso soma +2."),
    {"tipo": "gerado", "fonte": "medidas"},
]}

# ---------------------------------------------------------------- Dinheiro e rua (seções 12.2 a 12.5)

DINHEIRO = {"id": "dinheiro", "nome": "Dinheiro e rua", "blocos": [
    tabela("Estilo de vida (por mês)", ["Estilo", "Preço", "Como é"], [
        ["Kibble", "100eb", "Comida que você não daria ao seu cachorro. Um filme ou braindance por mês."],
        ["Prepak genérico", "300eb", "Bem melhor que kibble; uma saída por semana a um bom bar."],
        ["Prepak bom", "600eb", "Comida de restaurante, quase igual à real; um show por mês."],
        ["Comida fresca", "1.500eb", "Comida de verdade; bar de executivo."],
    ], nota="Paga todo dia 1º, com a moradia. Sem pagar, uma semana de prazo; depois, a espiral de fome."),
    tabela("Moradia", ["Moradia", "Aluguel por mês", "Compra"], [
        ["Na rua ou no carro", "—", "— (Fortitude CD 20 toda noite ou acorda fatigado)"],
        ["Hotel-cápsula", "500eb", "—"],
        ["Contêiner de carga", "1.000eb", "15.000eb"],
        ["Quitinete", "1.500eb", "25.000eb"],
        ["Apartamento de dois quartos", "2.500eb", "35.000eb"],
        ["Conapt de luxo", "7.500eb", "85.000eb"],
        ["Cobertura de luxo", "15.000eb", "500.000eb"],
        ["Casa / mansão em Beaverville", "—", "200.000eb / 500.000eb"],
    ]),
    tabela("Serviços e diversão (RED, p. 376)", ["Serviço", "Preço"], [
        ["Refeição: fast food / boa / excelente / de primeira", "10 / 20 / 50 / 500eb"],
        ["Bebida (de boteco a bar de executivo)", "10 a 100eb"],
        ["Cinema / videogame / braindance / braindance interativo", "20 / 50 / 20 / 50eb"],
        ["Show ao vivo ou evento esportivo", "100eb"],
        ["Hotel por noite / hotel de luxo", "100 / 500eb"],
        ["Táxi", "20eb"],
        ["Profissional bom por hora / excelente por hora / de primeira por trabalho", "100 / 500 / 5.000eb"],
        ["Escultura corporal (padrão / exótica)", "500 / 1.000eb"],
        ["Instalar cyberware achado (shopping / clínica / hospital)", "100 / 500 / 1.000eb"],
    ]),
    tabela("Teste de Riqueza (opcional)", ["Categoria", "Preço", "CD de compra"], [
        ["Barato", "10eb", "5"],
        ["Quotidiano", "20eb", "8"],
        ["Oneroso", "50eb", "10"],
        ["Premium", "100eb", "13"],
        ["Caro", "500eb", "18"],
        ["Muito Caro", "1.000eb", "20"],
        ["Luxuoso", "5.000eb", "25"],
        ["Super Luxuoso", "10.000eb", "30 (+2 a cada vez que o preço dobra)"],
    ], nota="d20 + Riqueza contra a CD; até Riqueza + 10 é compra de rotina. Acima da Riqueza, perde 1 graduação a "
            "cada 5 pontos (volta 1 por mês). Caro ou acima só com Fixer ou num Mercado Noturno (Investigação ou "
            "Especialidade: Manha CD 15). Vender: um quinto do preço sem Fixer, metade com Fixer."),
    tabela("Trabalhos e bicos", ["Resultado", "NP até 5", "NP 6 a 8", "NP 9 ou mais"], [
        ["Trabalho fácil / típico / perigoso", "500 / 1.000 / 2.000eb por pessoa", "idem", "idem"],
        ["Bico: falha", "0eb", "100eb", "300eb"],
        ["Bico: 1 grau de sucesso", "100eb", "200eb", "500eb"],
        ["Bico: 2 graus de sucesso", "200eb", "300eb", "600eb"],
        ["Bico: 3 ou mais graus", "300eb", "500eb", "800eb"],
    ], nota="Bico: uma semana livre e um teste da perícia principal do papel contra CD 15."),
]}

# ---------------------------------------------------------------- Rua, reputação e lei (seções 14, 15.1 e 17)

RUA = {"id": "rua", "nome": "Reputação e lei", "blocos": [
    lista("Reputação", [
        "**Graduação:** igual ao NP da campanha, +2 por graduação de Benefício (Renome), +1 a +4 por feitos "
        "conhecidos (metade da Reputação do RED).",
        "**Teste do PNJ:** d20 + reputação do personagem + Intelecto do PNJ contra CD 20 (ou uma perícia ligada à "
        "fama, como Especialidade: Manha).",
        "**Reconhecido:** opinião positiva dá metade da reputação em Enganação e Persuasão; negativa, a mesma "
        "penalidade, mas o valor vira bônus em Intimidação.",
        "**Encarada (Facedown):** teste oposto de Intimidação (+ metade da reputação de quem foi reconhecido). Empate: "
        "nada acontece. Quem perde recua ou fica prejudicado contra o vencedor até derrotá-lo uma vez.",
    ]),
    tabela("Atitudes", ["Atitude", "Comportamento"], [
        ["Hostil", "Corre riscos para atacar ou prejudicar o personagem."],
        ["Desfavorável", "Insulta, engana ou cria problemas."],
        ["Indiferente", "Age como o esperado socialmente."],
        ["Favorável", "Conversa, aconselha e oferece ajuda."],
        ["Prestativo", "Corre riscos para ajudar ou proteger o personagem."],
    ]),
    tabela("Zonas da cidade", ["Zona", "Como é", "Quem responde a um tiroteio"], [
        ["Executiva", "Subúrbios corporativos murados (Beaverville)", "Segurança particular, em minutos"],
        ["Corporativa", "Torres, sedes, conapts", "Segurança corporativa e polícia, rápido e bem armado"],
        ["Moderada", "Bairros de trabalhadores, comércio", "Polícia, quando dá"],
        ["Combate", "Ruínas, gangues, mercados ilegais", "Ninguém. Ou a gangue dona do quarteirão"],
    ]),
    tabela("Crimes e consequências [Casa]", ["Ofensa", "Consequência típica"], [
        ["Matar um executivo, invadir uma sede", "A corporação manda uma equipe de extração ou de limpeza."],
        ["Assassinato, sequestro", "Prisão longa, ou reabilitação num programa corporativo."],
        ["Roubo grande, contrabando", "Prisão, ou uma dívida com quem foi roubado."],
        ["Arma pesada numa Zona Corporativa", "Confisco e multa; resistência vira tiroteio."],
        ["Implantes de combate ilegais", "Multa ou confisco, se a polícia estiver com vontade."],
        ["Drogas", "A polícia não incomoda, a menos que procure uma desculpa."],
    ], nota="Max-Tac caça cyberpsicopatas (NP alto, armas pesadas). Recompensa: o valor de trabalho; um "
            "cyberpsicopata vivo vale o de trabalho perigoso."),
]}

escudo_cyberpunk = {
    "_fonte": "Resumo do Livro do Mestre do cyberpunk (dados/livros/cyberpunk_mestre.md): regras do livro básico "
              "de M&M e conversões do Cyberpunk RED. Gerado por ferramentas/criar_cyberpunk_escudo.py; os blocos "
              "'gerado' são calculados por nucleo/escudo.py.",
    "genero": "cyberpunk",
    "titulo": "Escudo do Mestre: Cyberpunk",
    "abas": [TESTES, COMBATE, ARMAS, CONDICOES, LESOES, HUMANIDADE_E_NET, LOCOMOCAO, PERIGOS, OBJETOS, DINHEIRO, RUA],
}

if __name__ == "__main__":
    DESTINO.write_text(json.dumps(escudo_cyberpunk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gravado {DESTINO}")
