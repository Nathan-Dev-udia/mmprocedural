"""Gera o arquivo dados/escudo/escola_de_magia.json para o Escudo do Mestre de Escola de Magia.

As regras gerais de M&M (ações, manobras, condições, dano, tratamento) vêm de ferramentas/escudo_mm.py.
A aba de Relacionamentos traz a tabela e a mecânica do Mapa de Relacionamentos de Mecha & Mangá (pp. 122–124).

Uso: python ferramentas/criar_escola_de_magia_escudo.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "ferramentas"))

import escudo_mm as mm  # noqa: E402

DESTINO = RAIZ / "dados" / "escudo" / "escola_de_magia.json"

# ---------------------------------------------------------------- Testes

TESTES = {
    "id": "testes",
    "nome": "Testes",
    "blocos": [
        {
            "tipo": "formulas",
            "titulo": "Fórmulas",
            "itens": [
                "**Teste** = d20 + graduação + modificadores, contra a CD",
                "**Rotina** = 10 + graduação (sem pressão; só com treino na perícia)",
                "**Ataque com varinha** = d20 + Combate à Distância: Varinha, contra Esquiva + 10",
                "**Salvamento contra feitiço** = d20 + defesa (Vontade, Fortitude ou Esquiva), contra 10 + graduação",
                "**Salvamento contra dano** = d20 + Resistência, contra 15 + Dano",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Classes de dificuldade",
            "colunas": ["CD", "Dificuldade", "Exemplo na escola"],
            "linhas": [
                ["0", "Muito fácil", "Acender a varinha com Lumus ou lembrar o nome da própria Casa"],
                ["5", "Fácil", "Levitar uma pena em aula básica de Feitiços"],
                ["10", "Médio", "Preparar uma poção simples seguindo o livro didático"],
                ["15", "Difícil", "Abrir uma porta trancada por magia simples sem fazer barulho"],
                ["20", "Desafiador", "Transfigurar um objeto complexo ou manter o controle no vendaval em vassoura"],
                ["25", "Formidável", "Conjurar um Patrono corpóreo cercado por Dementadores"],
                ["30", "Heroico", "Resistir a uma Maldição Imperius ou decifrar um tomo restrito antigo"],
                ["35", "Super-heroico", "Executar magia sem varinha sob pressão mortal"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Graus de sucesso e de falha",
            "nota": "20 natural: o resultado sobe um grau. Em ataques, 20 sempre acerta e 1 sempre erra.",
            "colunas": ["Resultado", "Grau"],
            "linhas": [
                ["CD + 15 ou mais", "4 graus de sucesso"],
                ["CD + 10 a + 14", "3 graus de sucesso"],
                ["CD + 5 a + 9", "2 graus de sucesso"],
                ["CD a CD + 4", "1 grau de sucesso"],
                ["CD – 1 a CD – 5", "1 grau de falha"],
                ["CD – 6 a CD – 10", "2 graus de falha"],
                ["CD – 11 a CD – 15", "3 graus de falha"],
                ["CD – 16 ou menos", "4 graus de falha"],
            ],
        },
        {
            "tipo": "lista",
            "titulo": "Matérias escolares como perícias",
            "itens": [
                "**Especialidade: Teoria Mágica:** fundamentos de Feitiços, Transfiguração e runas.",
                "**Especialidade: Poções:** preparo de elixires, antídotos e reconhecimento de ingredientes.",
                "**Especialidade: Herbologia:** cuidado de plantas mágicas perigosas (mandrágoras, visgo-do-diabo).",
                "**Especialidade: Criaturas Mágicas:** comportamento e fraquezas de feras e seres encantados.",
                "**Especialidade: Artes das Trevas:** reconhecer maldições, objetos sombrios e defesas.",
                "**Veículos (Vassoura):** manobras aéreas, mergulhos e disputas de Quadribol.",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Testes opostos",
            "nota": "Os dois lados rolam e vence o maior total. Empate: vence quem tem o maior bônus.",
            "colunas": ["Situação", "Quem age", "Quem resiste"],
            "linhas": [
                ["Passar pelos corredores após o toque de recolher", "Furtividade", "Percepção"],
                ["Inventar desculpa para um professor ou monitor", "Enganação", "Intuição"],
                ["Disputar o Pomo ou um mergulho no Quadribol", "Veículos / Acrobacia", "Veículos / Acrobacia"],
                ["Fintar num duelo mágico", "Enganação", "Enganação ou Intuição"],
                ["Arrancar a varinha da mão com Expelliarmus", "Ataque / Dano", "Força ou Esquiva (desarme)"],
            ],
        },
        mm.esforco_extra("um feitiço ou uma vassoura"),
        mm.PONTOS_HEROICOS,
    ],
}

# ---------------------------------------------------------------- Combate

COMBATE = {
    "id": "combate",
    "nome": "Combate e Duelos",
    "blocos": [
        {
            "tipo": "lista",
            "titulo": "Turno de combate e duelo",
            "itens": [
                "**Iniciativa:** d20 + Agilidade + 4 por graduação de Iniciativa Aprimorada.",
                "**Desarmar varinha:** sem a varinha em mãos, o bruxo não pode conjurar feitiços do arranjo **Varinha (Removível)**.",
                "**Falar o encantamento:** feitiços sob *Travalíngua* ou em silêncio absoluto ficam bloqueados, salvo magia não-verbal.",
            ],
        },
        mm.acoes([
            ["Trocar feitiço do arranjo", "Livre", "Alterna o feitiço ativo na varinha (uma vez por turno)."],
            ["Voar em vassoura", "Movimento", "Conduz a vassoura até a Velocidade dela; manobras difíceis pedem Veículos."],
        ], comandar="um animal de estimação ou criatura invocada"),
        mm.manobras("de vassoura, por exemplo"),
        {
            "tipo": "tabela",
            "titulo": "Camuflagem e cobertura",
            "colunas": ["Situação", "Ataque", "Exemplos"],
            "linhas": [
                ["Camuflagem parcial", "–2", "Névoa na Floresta Proibida, fumaça de poção, penumbra"],
                ["Camuflagem total", "–5", "Escuridão total sem Lumus, capa encantada de desilusão"],
                ["Cobertura parcial", "–2", "Pilastra de pedra, mesa do Salão Principal, estante"],
                ["Cobertura total", "–5", "Muro de alvenaria, estátua grande, parede do castelo"],
            ],
        },
    ],
}

# ---------------------------------------------------------------- Condições

CONDICOES = {
    "id": "condicoes",
    "nome": "Condições e graus",
    "blocos": [
        {"tipo": "gerado", "fonte": "aflicao"},
        {"tipo": "gerado", "fonte": "dano"},
        mm.condicoes_basicas("Ações ditadas pela fonte (feitiço Imperio, Confundus, encantamento)."),
        mm.CONDICOES_COMBINADAS,
        {"tipo": "gerado", "fonte": "recuperacao"},
        mm.tratamento("estojo de poções e bandagens", extras=[
            ["Usar Poção Wiggenweld", "—", "Remove 1 condição de dano ou fadiga (uso único)."],
        ]),
    ],
}

# ---------------------------------------------------------------- Magia & Varinha

MAGIA = {
    "id": "magia",
    "nome": "Magia e Varinha",
    "blocos": [
        {
            "tipo": "lista",
            "titulo": "Arranjo Varinha e progressão por missão [Casa]",
            "itens": [
                "**Arranjo Varinha (Removível):** todos os feitiços da varinha formam um único Arranjo. Você só conjura **um feitiço por vez**, trocando entre eles como ação livre.",
                "**Custo inicial:** o feitiço mais caro do arranjo paga o custo cheio em PP (com **–1 PP** pela falha Removível). Cada outro feitiço do arranjo custa apenas **1 PP** (Efeito Alternativo).",
                "**Ganho por missão (1 PP):** ao concluir uma missão ou mistério na escola, o jogador ganha **1 PP**, podendo aprender imediatamente **1 novo feitiço** no arranjo Varinha (ou guardar PP para melhorar habilidades, perícias e defesas).",
                "**Ritualista e Poções:** com a vantagem *Ritualista*, o bruxo pode preparar encantamentos fora de combate; poções seguem *Especialidade: Poções*.",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Progressão escolar por ano (NP sugerido)",
            "colunas": ["Ano escolar", "NP", "PP totais", "Exemplos de feitiços liberados"],
            "linhas": [
                ["1º e 2º ano", "NP 2", "30 PP", "Lumus, Nox, Wingardium Leviosa, Alohomora, Reparo, Expelliarmus, Petrificus Totalus"],
                ["3º e 4º ano", "NP 3", "45 PP", "Aresto Momentum, Riddikulus, Expecto Patronum, Accio, Depulso, Estupefaça, Aguamenti"],
                ["5º ano (N.O.M.s)", "NP 4", "60 PP", "Salvio Hexia / Protego, Cave Inimicum, Confundus, Episkey, Braquium Remendo"],
                ["6º e 7º ano (N.I.E.M.s)", "NP 5–6", "75–90 PP", "Homenum Revelio, Obliviate, Avifors, Homorfo, Aparatação"],
                ["Adultos / Aurores", "NP 7–10", "105–150 PP", "Domínio completo, magia silenciosa e combate contra bruxos das trevas"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Maldições Imperdoáveis (apenas NPCs / Proibidas)",
            "nota": "Uso por estudantes é proibido e rende prisão imediata ou expulsão; dano é sempre Letal.",
            "colunas": ["Maldição", "Efeito em M&M 3e", "Resistência"],
            "linhas": [
                ["Avada Kedavra", "Aflição Letal à Percepção (3º grau: Moribundo / Morte)", "Esquiva / Fortitude"],
                ["Crucio", "Aflição à Distância (Tonto, Atordoado, Incapacitado por dor)", "Vontade"],
                ["Imperio", "Aflição à Percepção (Transe, Compelido, Controlado)", "Vontade"],
            ],
        },
    ],
}

# ---------------------------------------------------------------- Relacionamentos (Mecha & Mangá)

RELACIONAMENTOS = {
    "id": "relacionamentos",
    "nome": "Relacionamentos",
    "blocos": [
        {
            "tipo": "lista",
            "titulo": "Mapa de Relacionamentos (Mecha & Mangá, pp. 122–124)",
            "itens": [
                "**Espaços de Relacionamento:** cada jogador rola `1d20 ÷ 3` (arredondado para baixo) e soma sua **Presença** (mínimo 1). Esse é o total de laços importantes com colegas, professores ou rivais.",
                "**Direção e intensidade (+1 a +5):** cada laço tem sentimento **Positivo** (amizade, admiração, paixão, lealdade) ou **Negativo** (rivalidade, rancor, inveja, medo), graduado de **+1** (leve) a **+5** (profundo).",
                "**Jogando com Relacionamentos:** sempre que surgir uma cena ligada a um laço, o jogador pode **gastar 1 Ponto Heroico** (ou o Mestre **conceder 1 Ponto Heroico** como complicação) para somar o valor numérico do laço (**+1 a +5**) como bônus flutuante durante o encontro.",
                "**Custo emocional:** após usar um bônus de relacionamento, o personagem fica emocionalmente esgotado — sofre **–2** em salvamentos de **Vontade** e testes de perícias de **interação** até ter chance de descansar.",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Tabela de Vetores do Mapa de Relacionamentos (Mecha & Mangá)",
            "nota": "Role 1d20 para a Natureza e 1d20 para a Direção (ou escolha livremente na criação).",
            "colunas": ["1d20", "Natureza do vínculo (adaptado à escola)", "Direção e intensidade"],
            "linhas": [
                ["1–2", "Conhecido de escola / outra Casa", "Profundamente negativo (+5)"],
                ["3–4", "Amigo antigo / de infância", "Fortemente negativo (+4)"],
                ["5–6", "Mentor, professor ou monitor (ou protegido)", "Muito negativo (+3)"],
                ["7–8", "Parente mais jovem (irmão menor, primo)", "Moderadamente negativo (+2)"],
                ["9–10", "Parente mais velho (pais, tio, irmão mais velho)", "Levemente negativo (+1)"],
                ["11–12", "Parente da mesma geração (irmão gêmeo, primo)", "Levemente positivo (+1)"],
                ["13–14", "Colega de Casa ou de dormitório", "Moderadamente positivo (+2)"],
                ["15–16", "Rival de escola / de Quadribol", "Muito positivo (+3)"],
                ["17–18", "Inimigo declarado", "Fortemente positivo (+4)"],
                ["19–20", "Role duas vezes na Natureza (ignore 19–20)", "Profundamente positivo (+5)"],
            ],
        },
    ],
}

# ---------------------------------------------------------------- Viagem & Vassouras

VIAGEM = {
    "id": "viagem",
    "nome": "Viagem e Vassouras",
    "blocos": [
        {"tipo": "gerado", "fonte": "tempo_de_viagem"},
        {"tipo": "gerado", "fonte": "montarias"},
        {"tipo": "gerado", "fonte": "carga"},
        {"tipo": "gerado", "fonte": "queda"},
        {"tipo": "gerado", "fonte": "medidas"},
    ],
}

# ---------------------------------------------------------------- Escola, Casas & Moedas

ESCOLA = {
    "id": "escola",
    "nome": "Escola e Moedas",
    "blocos": [
        {
            "tipo": "lista",
            "titulo": "Moeda bruxa e custos",
            "itens": [
                "**Conversão fixa:** **1 Galeão (G) = 17 Sicles (S) = 493 Nuques (N)** (1 Sicle = 29 Nuques).",
                "**Refeição / Cerveja Amanteigada:** 2 Sicles (~0,12 G).",
                "**Diária em pousada bruxa (Caldeirão Furado / Três Vassouras):** 1 Galeão.",
                "**Passagem no Nôitibus Andante:** 11 Sicles (com chocolate quente: 13 Sicles).",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "As quatro Casas (pacotes de base — 2 PP)",
            "colunas": ["Casa", "Virtude", "Bônus de base"],
            "linhas": [
                ["Grifinória", "Coragem e ousadia", "Destemido + Atletismo +2"],
                ["Corvinal", "Estudo e inteligência", "Memória Eidética + Investigação +2"],
                ["Lufa-Lufa", "Lealdade e trabalho duro", "Trabalho em Equipe + Especialidade: Herbologia +2"],
                ["Sonserina", "Ambição e astúcia", "Bem Informado + Enganação +2"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Pontos das Casas (guia rápido do Mestre)",
            "colunas": ["Feito ou infração", "Pontos sugeridos"],
            "linhas": [
                ["Resposta brilhante em aula ou ajuda a colega", "+5 a +10 pontos"],
                ["Desvendar mistério ou ato de coragem excepcional", "+25 a +50 pontos"],
                ["Pego fora do dormitório após o toque de recolher", "–10 a –20 pontos"],
                ["Duelo nos corredores ou uso de feitiço perigoso", "–20 a –50 pontos + detenção"],
            ],
        },
    ],
}

# ---------------------------------------------------------------- Quadribol (Quadribol Através dos Séculos)

QUADRIBOL = {
    "id": "quadribol",
    "nome": "Quadribol",
    "blocos": [
        {
            "tipo": "lista",
            "titulo": "Rodada de Quadribol e as 4 Posições [Casa / Quadribol Através dos Séculos]",
            "itens": [
                "**1. Artilheiros (3 por time, Goles — +10 pts):** cada passe bem-sucedido entre colegas (Veículos ou Atletismo CD 10) soma **+1 cumulativo** (máx. +3) no arremesso ao aro. O arremesso é um teste oposto contra o **Goleiro**.",
                "**2. Goleiro (1 por time):** defende os três aros em teste oposto de **Veículos**, **Acrobacia** ou **Atletismo** contra o Artilheiro.",
                "**3. Batedores (2 por time, 2 Balaços de ferro — Dano 3):** teste de **Combate Corpo a Corpo: Bastão** ou **Atletismo** (CD 12). **1 grau:** bloqueia 1 balaço; **2 graus:** bloqueia ambos; **3+ graus:** redireciona um balaço contra o Apanhador ou Artilheiro rival (alvo faz Esquiva ou Veículos CD 14; se falhar, sofre Dano 3 ou perde a ação de quadra).",
                "**4. Apanhador (1 por time, Pomo de Ouro — +150 pts e encerra o jogo):** a cada rodada, ganha **+1 cumulativo** no teste de **Percepção** (CD 20) para avistar o Pomo. Avistado o Pomo, disputa oposta de **Veículos** (primeiro a somar 3 graus de sucesso captura o Pomo).",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Manobras Clássicas de Quadribol (Quadribol Através dos Séculos, cap. 10)",
            "nota": "Exige ação de movimento/tática e teste de Veículos ou Acrobacia (CD 14) antes da ação principal.",
            "colunas": ["Manobra", "Posição", "Efeito mecânico em M&M 3e"],
            "linhas": [
                ["Finta de Wronski (Wronski Feint)", "Apanhador", "Mergulho suicida falso: Enganação vs. Intuição do Apanhador rival. Se vencer, o rival deve passar em Veículos CD 16 ou colide com o chão (Dano 4 e perde o turno)."],
                ["Passe de Plumpton (Plumpton Pass)", "Apanhador", "Guinada displicente recolhendo o Pomo na manga: +2 no teste de captura, mas se falhar perde a próxima ação de movimento."],
                ["Pêndulo Estrela-do-Mar (Starfish and Stick)", "Goleiro", "Segura a vassoura na horizontal com um pé e uma mão: +5 na defesa contra arremesso normal ou anula Fazer Escada, mas fica vulnerável na rodada seguinte."],
                ["Defesa de Oito Duplo (Double Eight Loop)", "Goleiro", "Contorna os três aros em alta velocidade: +2 na defesa contra cobrança de pênalti."],
                ["Ardil de Porskoff (Porskoff Ploy)", "Artilheiros", "Sobe com a Goles e deixa cair para colega abaixo: exige Trabalho em Equipe; concede +3 no arremesso do colega."],
                ["Pinça de Parkin (Parkin's Pincer)", "Artilheiros", "Dois cercam pelos lados e o 3º voa de frente: impõe –4 no teste de Veículos/arremesso do Artilheiro alvo."],
                ["Formação Cabeça-de-Falcão (Hawkshead)", "Artilheiros", "Os três voam em V fechado: Intimidação em grupo; imuniza os artilheiros contra faltas físicas na rodada."],
                ["Passe de Revés (Reverse Pass)", "Artilheiro", "Lança a Goles por cima do ombro (–2 no passe, mas se acertar surpreende o Goleiro com +4 no arremesso)."],
                ["Zigue-Zague de Woollongong (Shimmy)", "Artilheiro", "Zigue-zague veloz: alvo faz Veículos CD 14 ou fica pendurado no cabo (impedido na rodada)."],
                ["Rebate Falso (Bludger Backbeat)", "Batedor", "Rebate o balaço para trás: Enganação/Bastão que impõe –2 na defesa/Esquiva do alvo."],
                ["Dupla-Defesa (Dopplebeater Defence)", "Batedores", "Os dois Batedores rebatem juntos o mesmo balaço: aumenta a CD para evitar o balaço para 16 (Dano 4)."],
                ["Giro da Preguiça (Sloth Grip Roll)", "Todos", "Pendura-se debaixo do cabo com pés e mãos (Acrobacia CD 12): evita automaticamente um balaço na rodada."],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "As 10 Faltas Mais Comuns (Departamento de Jogos e Esportes Mágicos)",
            "nota": "Cometer falta pede Furtividade ou Enganação contra a Percepção do Árbitro (CD 12 amador, 15 escolar, 18 profissional). Se visto, pênalti para o rival!",
            "colunas": ["Falta", "Quem comete", "Descrição e efeito se não for contida"],
            "linhas": [
                ["Mutretar (Blagging)", "Todos", "Segurar a cauda da vassoura do adversário para atrasá-lo (impõe –2 no teste de voo dele)."],
                ["Trombar (Blatching)", "Todos", "Voar com intenção de colidir (ataque de encontrão; Dano 2 para ambos se falhar por 2+ graus)."],
                ["Guidonar (Blurting)", "Todos", "Engatar os cabos das vassouras para tirar o rival de curso (alvo fica Impedido na rodada)."],
                ["Catimbar (Bumphing)", "Batedores", "Rebater balaço para a arquibancada, forçando pausa/distração para impedir gol iminente."],
                ["Acotovelar (Cobbing)", "Todos", "Uso excessivo de cotoveladas (ataque corpo a corpo Dano 1 + Força; se atingir, alvo perde a ação)."],
                ["Bloquear (Flacking)", "Goleiro", "Enfiar braço ou corpo por trás do aro para empurrar a Goles para fora (impõe –4 ao Artilheiro)."],
                ["Conduzir (Haversacking)", "Artilheiros", "Enterrar a Goles mantendo a mão nela ao atravessar o aro (impõe –4 ao Goleiro, mas anula o gol se visto)."],
                ["Furar a goles (Quaffle-pocking)", "Artilheiros", "Furar ou adulterar a Goles para cair em zigue-zague (+3 no arremesso)."],
                ["Roubar o pomo (Snitchnip)", "Não-Apanhador", "Qualquer jogador que não seja o Apanhador tocar ou agarrar o Pomo de Ouro (falta gravíssima)."],
                ["Fazer escada (Stooging)", "Artilheiros", "Mais de um Artilheiro entrar na pequena área para confundir/bloquear o Goleiro."],
            ],
        },
    ],
}

ESCUDO = {
    "genero": "escola_de_magia",
    "titulo": "Escudo do Mestre — Escola de Magia",
    "subtitulo": "Mutantes & Malfeitores 3ª edição · Arranjo Varinha · Relacionamentos (Mecha & Mangá)",
    "letalidade": {
        "padrao": "heroica",
        "ataques_letais": "Apenas Maldições Imperdoáveis e ataques mortais de criaturas causam dano letal.",
        "cura_mortal": "Ala hospitalar e poções restauradoras (Tratamento CD 15).",
    },
    "abas": [TESTES, COMBATE, CONDICOES, MAGIA, RELACIONAMENTOS, QUADRIBOL, VIAGEM, ESCOLA],
}

DESTINO.write_text(json.dumps(ESCUDO, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Escudo gravado em", DESTINO)
