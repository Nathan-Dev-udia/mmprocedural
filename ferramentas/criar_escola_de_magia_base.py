"""Gera os arquivos básicos do gênero escola_de_magia (inspirado em Harry Potter):
gênero, equipamento, feitiços, casas, arquétipos, módulos, nomes e complicações.

Uso: python ferramentas/criar_escola_de_magia_base.py

- Base estrita de Mutantes & Malfeitores 3ª edição.
- Varinha como Arranjo ("Varinha") com falha Removível (-1 PP): o feitiço mais caro
  paga o custo cheio e cada feitiço adicional aprendido custa 1 PP (Efeito Alternativo).
  Isso permite a progressão de campanha onde cada missão rende 1 PP para aprender
  um novo feitiço.
- Lista de feitiços baseada em referencias/harry potter/Tabela de magias.pdf,
  convertida para os efeitos de dados/comum/poderes/perfis_de_poder.json.

ATENÇÃO: este script recria os JSONs de dados/generos/escola_de_magia/ do zero.
"""

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "dados" / "generos" / "escola_de_magia"
PASTA.mkdir(parents=True, exist_ok=True)


def gravar(nome, conteudo):
    (PASTA / nome).write_text(json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- genero.json

gravar("genero.json", {
    "id": "escola_de_magia",
    "nome": "Escola de Magia",
    "descricao": (
        "Estudantes de uma escola de magia oculta do mundo comum, divididos em quatro Casas, "
        "aprendendo feitiços ano a ano enquanto desvendam mistérios dentro e fora do castelo."
    ),
    "perfis_de_poder": [
        "Mágicos", "Luminosos", "Mentais", "Ilusórios", "Vitais", "Cinéticos",
        "Flamejantes", "Congelantes", "Aquáticos", "Climáticos", "De Tamanho & Massa",
        "De Teleporte", "De Transformação", "Fatais", "Animais", "Sensoriais",
        "Sombrios", "Elementais",
    ],
    "configuracoes": {
        "rotulo_poderes": "Feitiços e dons",
        "rotulo_arquetipo": "Perfil",
        "rotulo_foco": "Especialização",
        "equipamento": "dinheiro",
        "moeda": "G",
        "np_padrao_jogador": 2,
        # 1º-2º ano: NP 2; 3º-4º: NP 3; 5º: NP 4; 6º: NP 5; 7º: NP 6; adultos/professores: NP 7-10.
        "nps_disponiveis": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "itens_basicos": ["uniforme_escolar", "kit_estudante"],
        "prioridades_gerais": [
            "defesa:Esquiva", "defesa:Vontade", "defesa:Fortitude", "defesa:Aparar",
            "pericia:Percepção", "pericia:Intuição", "pericia:Atletismo",
            "vantagem:Rolamento Defensivo", "habilidade:Vig",
        ],
        "pericias_de_reserva": [
            "Percepção", "Intuição", "Atletismo", "Investigação", "Furtividade",
            "Persuasão", "Enganação", "Acrobacia", "Prestidigitação",
            "Especialidade: Teoria Mágica", "Especialidade: Poções",
        ],
    },
    "letalidade": {
        "padrao": "heroica",
        "ataques_letais": "Nenhum feitiço escolar comum é letal (letalidade Heroica). "
                          "Apenas Maldições Imperdoáveis, fogo sombrio e venenos letais de monstros "
                          "causam dano letal.",
        "cura_mortal": "Sem cura mágica imediata, ferimentos graves exigem repouso na ala hospitalar "
                       "e poções restauradoras (Tratamento CD 15).",
    },
})


# ---------------------------------------------------------------- equipment.json

def item(id_, nome, cat, preco, descricao="", custo=1, comercio="Beco Diagonal", **extra):
    dados = {
        "id": id_,
        "nome": nome,
        "categoria": cat,
        "comercio": comercio,
        "custo": custo,
        "preco": preco,
        "descricao": descricao,
        "fonte": "Catálogo Escola de Magia [Casa]; preços em Galeões (1 G = 17 Sicles = 493 Nuques)",
    }
    dados.update(extra)
    return dados


EQUIPAMENTOS = [
    # ---- Varinhas e focos (Olivaras)
    item("varinha_padrao", "Varinha escolar", "Varinhas", 7,
         "Madeira e núcleo mágico sintonizados ao bruxo (pena de fênix, fibra cardíaca de dragão ou pelo de unicórnio). Exigida para conjurar os feitiços do arranjo Varinha; também dispara centelhas básicas.",
         comercio="Olivaras (Varinhas)", peso=0.1,
         ataque={"tipo": "distancia", "efeito": 1, "critico": 20, "pericia": "Combate à Distância: Varinha",
                 "descritor": "centelhas mágicas"}),
    item("varinha_duelo", "Varinha equilibrada de duelo", "Varinhas", 25,
         "Entalhe de precisão para movimentos rápidos; exigida para o arranjo Varinha e dispara centelhas mágicas.",
         comercio="Olivaras (Varinhas)", peso=0.1,
         ataque={"tipo": "distancia", "efeito": 1, "critico": 20, "pericia": "Combate à Distância: Varinha",
                 "descritor": "centelhas mágicas"}),
    item("bastao_batedor", "Bastão de Batedor (Quadribol)", "Varinhas", 6,
         "Bastão curto de madeira reforçada magicamente para rebater balaços de ferro.",
         comercio="Artigos de Qualidade para Quadribol", peso=1.2,
         ataque={"tipo": "corpo", "efeito": 2, "soma_forca": True, "critico": 20,
                 "pericia": "Combate Corpo-a-Corpo: Bastão", "descritor": "contusão"}),
    item("estojo_varinha", "Coldre de varinha", "Material escolar", 2,
         "Preso ao antebraço ou às vestes; sacar a varinha passa a ser ação livre.",
         comercio="Olivaras (Varinhas)", peso=0.2),

    # ---- Vassouras e transportes (Artigos de Qualidade para Quadribol)
    item("vassoura_escolar", "Vassoura escolar (Shooting Star / Cleansweep antiga)", "Vassouras", 20,
         "Modelo robusto da escola, estável para iniciantes.",
         comercio="Artigos de Qualidade para Quadribol", velocidade=3, carga=100, peso=2.5),
    item("vassoura_passeio", "Vassoura de passeio (Cleansweep / Comet)", "Vassouras", 45,
         "Boa manobrabilidade e Feitiço de Freagem para viagens curtas e partidas escolares.",
         comercio="Artigos de Qualidade para Quadribol", velocidade=4, carga=110, peso=2.2),
    item("vassoura_corrida", "Vassoura de corrida (Nimbus / Firebolt)", "Vassouras", 120,
         "Modelo esportivo de alta velocidade e giro de 360º para Quadribol competitivo.",
         comercio="Artigos de Qualidade para Quadribol", velocidade=5, carga=120, peso=2.0),
    item("kit_manutencao_vassoura", "Kit de manutenção de vassoura", "Material escolar", 5,
         "Cera de polimento para o cabo, tesoura de aparar galhos e bússola de encaixar. Concede +2 em testes de manutenção.",
         comercio="Artigos de Qualidade para Quadribol", peso=1.0),

    # ---- Material escolar e vestuário
    item("uniforme_escolar", "Uniforme e capa da escola", "Material escolar", 4,
         "Veste tradicional com o brasão da Casa e bolsos internos para varinha e pergaminhos.",
         comercio="Madame Malkin (Vestes)", peso=1.2),
    item("luvas_couro_dragao", "Luvas protetoras de couro de dragão", "Material escolar", 3,
         "Exigidas nas aulas de Herbologia e Poções para manusear plantas e ingredientes cáusticos.",
         comercio="Madame Malkin (Vestes)", peso=0.4),
    item("kit_estudante", "Kit de estudante (pergaminho, pena e tinta)", "Material escolar", 2,
         "Material básico para anotações em sala e deveres.",
         comercio="Floreios e Borrões (Livraria)", peso=0.8),
    item("livros_ano", "Conjunto de livros didáticos do ano", "Material escolar", 12,
         "Manuais de Feitiços, Transfiguração, Herbologia, Poções, História da Magia e Defesa.",
         comercio="Floreios e Borrões (Livraria)", peso=3.5),
    item("caldeirao_estanho", "Caldeirão de estanho nº 2", "Material escolar", 15,
         "Exigido nas aulas de Poções; inclui pinça e frascos graduados.",
         comercio="Boticário", peso=4.0),
    item("kit_pocoes", "Estojo de ingredientes básicos de Poções", "Material escolar", 10,
         "Raízes secas, vagens, espinhos de porco-espinho e frascos de vidro cristal.",
         comercio="Boticário", peso=1.5),
    item("telescopio_latao", "Telescópio de latão", "Material escolar", 5,
         "Para as aulas noturnas de Astronomia.",
         comercio="Boticário", peso=1.0),
    item("balanca_latao", "Balança de latão", "Material escolar", 3,
         "Medição precisa de ingredientes alquímicos.",
         comercio="Boticário", peso=0.6),

    # ---- Poções e elixires (Boticário — sincronizado com alquimia.json e pocoes.xlsx)
    item("pocao_furunculos", "Poção para Curar Furúnculos", "Poções", 4,
         "Remove furúnculos, urticárias e irritações leves causadas por azarações ou plantas (1º ano, CD 10).",
         comercio="Boticário", peso=0.2),
    item("pocao_esquecimento", "Poção do Esquecimento", "Poções", 6,
         "Causa confusão mental passageira (Aflição 2 resistida por Vontade: Tonto / Compelido a esquecer os últimos minutos; 1º ano, CD 12).",
         comercio="Boticário", peso=0.2),
    item("pocao_cura", "Poção Wiggenweld (cura)", "Poções", 8,
         "Restaura o fôlego e remove 1 condição de dano ou fadiga, ou desperta alguém do Sono Mágico (1º ano, CD 12).",
         comercio="Boticário", peso=0.2),
    item("pocao_estimulante", "Poção Estimulante (Pepperup)", "Poções", 6,
         "Remove imediatamente Fatigado, hipotermia e resfriados; faz sair fumaça pelas orelhas por algumas horas (2º ano, CD 13).",
         comercio="Boticário", peso=0.2),
    item("pocao_inchaco", "Solução de Inchaço", "Poções", 7,
         "Faz a parte atingida inflar (Aflição 3 resistida por Fortitude: Impedido / Desabilitado; 2º ano, CD 13).",
         comercio="Boticário", peso=0.2),
    item("pocao_encolhedora", "Solução Encolhedora", "Poções", 12,
         "Antídoto da Solução de Inchaço; também reduz o tamanho de pequenos animais ou objetos (Encolhimento 2; 3º ano, CD 15).",
         comercio="Boticário", peso=0.2),
    item("antidoto_comum", "Antídoto para venenos comuns", "Poções", 10,
         "Concede novo teste de Fortitude imediato com +5 contra venenos comuns e picadas (3º ano, CD 14).",
         comercio="Boticário", peso=0.2),
    item("pocao_esquelece", "Esquelece (Skele-Gro)", "Poções", 18,
         "Regenera ossos partidos ou removidos após 8 horas de repouso doloroso (4º ano, CD 16).",
         comercio="Boticário", peso=0.3),
    item("filtro_paz", "Filtro da Paz", "Poções", 15,
         "Acalma ansiedade e pânico; concede +4 em Vontade contra medo e remove Abalado/Assustado (5º ano N.O.M., CD 18).",
         comercio="Boticário", peso=0.2),
    item("pocao_morto_vivo", "Poção do Morto-Vivo (sonífera)", "Poções", 25,
         "Sonífero poderosíssimo (Aflição Cumulativa 6 resistida por Fortitude: Tonto / Exausto / Adormecido profundo; 6º ano N.I.E.M., CD 20).",
         comercio="Boticário", peso=0.2),
    item("pocao_polissuco", "Poção Polissuco (dose)", "Poções", 60,
         "Assume a aparência física exata de outro humano por 1 hora (Morfo 3; exige fio de cabelo; CD 22, 1 mês de preparo).",
         comercio="Boticário", peso=0.2),
    item("veritaserum", "Veritaserum (Soro da Verdade)", "Poções", 90,
         "Três gotas obrigam a dizer a verdade (Aflição Cumulativa 8 resistida por Vontade; controlada pelo Ministério; CD 25).",
         comercio="Boticário", peso=0.1),
    item("felix_felicis", "Felix Felicis (1 gole)", "Poções", 150,
         "Sorte líquida: concede 1 Ponto Heroico extra e a vantagem Sorte 2 durante uma cena/missão (CD 28, 6 meses de preparo).",
         comercio="Boticário", peso=0.1),

    # ---- Plantas mágicas e reagentes de criaturas (Boticário — sincronizado com alquimia.json)
    item("ing_mandragora", "Folha de Mandrágora", "Ingredientes e Plantas", 5,
         "Base essencial para reverter petrificação e feitiços de transformação permanentes.",
         comercio="Boticário", peso=0.1),
    item("ing_guelricho", "Guelricho (Gillyweed — 1 porção)", "Ingredientes e Plantas", 12,
         "Planta aquática que cria guelras e membranas entre os dedos por 1 hora (Imunidade a Afogamento + Natação 2).",
         comercio="Boticário", peso=0.1),
    item("ing_bezoar", "Bezoar (pedra estomacal de cabra)", "Ingredientes e Plantas", 20,
         "Engolido em emergência, neutraliza quase qualquer veneno mágico instantaneamente (Nulificar Veneno 6).",
         comercio="Boticário", peso=0.1),
    item("ing_bubotubera", "Pus de Bubotúbera (frasco)", "Ingredientes e Plantas", 4,
         "Líquido amarelado com cheiro de gasolina; diluído cura acne severa, puro causa furúnculos ao contato.",
         comercio="Boticário", peso=0.2),
    item("ing_aconito", "Acônito (Licoctono / Lupária)", "Ingredientes e Plantas", 6,
         "Planta altamente tóxica usada na Poção Mata-Cão e em elixires de vigília.",
         comercio="Boticário", peso=0.1),
    item("ing_boomslang", "Pele de Araramboia picada", "Ingredientes e Plantas", 18,
         "Ingrediente raro e controlado usado na Poção Polissuco.",
         comercio="Boticário", peso=0.1),
    item("ing_bicornio", "Chifre de Bicórnio em pó", "Ingredientes e Plantas", 15,
         "Reagente raro utilizado na Poção Polissuco e em poções de vigor.",
         comercio="Boticário", peso=0.1),
    item("ing_acromantula", "Veneno de Acromântula (frasco)", "Ingredientes e Plantas", 50,
         "Secreção raríssima (100 G o meio litro; frasco de 1 dose = 50 G) colhida de Acromântulas recém-abatidas.",
         comercio="Boticário", peso=0.1),
    item("ing_cinzal", "Ovos de Cinzal congelados", "Ingredientes e Plantas", 25,
         "Ovos incandescentes da serpente mágica Cinzal (XXX); usados em poções de amor e contra febres agudas.",
         comercio="Boticário", peso=0.2),
    item("ing_unicornio", "Crina de Unicórnio (fio)", "Ingredientes e Plantas", 10,
         "Fio prateado da cauda de um Unicórnio (XXXX); excelente ligante para poções curativas como a Wiggenweld.",
         comercio="Boticário", peso=0.05),

    # ---- Itens mágicos, logros e doces
    item("lembrol", "Lembrol", "Itens mágicos", 5,
         "Esfera de vidro que fica vermelha quando o dono esqueceu algo.",
         comercio="Gemialidades e Logros", peso=0.2),
    item("bisbilhotoscopio", "Bisbilhotoscópio", "Itens mágicos", 12,
         "Gira e apita quando há alguém desonesto ou hostil por perto.",
         comercio="Gemialidades e Logros", peso=0.3),
    item("orelha_extensivel", "Orelhas Extensíveis (par)", "Itens mágicos", 8,
         "Fio encantado para ouvir conversas atrás de portas fechadas (+5 em Percepção auditiva à distância).",
         comercio="Gemialidades e Logros", peso=0.1),
    item("po_escurecedor", "Pó Escurecedor Instantâneo Peruano", "Itens mágicos", 15,
         "Cria uma nuvem de escuridão resistente a Lumus comuns por 2 rodadas (Camuflagem Visual Total na área).",
         comercio="Gemialidades e Logros", peso=0.1),
    item("desiluminador", "Apagador de luzes (Desiluminador)", "Itens mágicos", 35,
         "Absorve e devolve fontes de luz próximas.",
         comercio="Gemialidades e Logros", peso=0.2),
    item("capa_invisibilidade", "Capa encantada de desilusão", "Itens mágicos", 180,
         "Concede camuflagem visual enquanto vestida (rara).",
         comercio="Madame Malkin (Vestes)", peso=0.8),
    item("sapo_chocolate", "Sapo de Chocolate (com figurinha)", "Doces e Bebidas", 0.2,
         "Doce encantado da Dedosdemel que recupera o ânimo e traz um cartão de bruxo famoso.",
         comercio="Dedosdemel / Três Vassouras", peso=0.1),
    item("cerveja_amanteigada", "Cerveja Amanteigada (garrafa)", "Doces e Bebidas", 0.2,
         "Bebida espumante e quentinha servida no Três Vassouras (+1 de circunstância contra o frio por 1 hora).",
         comercio="Dedosdemel / Três Vassouras", peso=0.5),
    item("coruja_correio", "Coruja de estimação", "Animais de estimação", 15,
         "Entrega cartas e encomendas em qualquer lugar do país.",
         comercio="Empório das Corujas", peso=1.0),
    item("gato_escolar", "Gato ou amasso de estimação", "Animais de estimação", 10,
         "Companheiro atento aos arredores da escola e ótimo para farejar impostores.",
         comercio="Empório das Corujas", peso=3.5),
]

gravar("equipment.json", EQUIPAMENTOS)


# ---------------------------------------------------------------- powers.json (56 feitiços + dons)

VARINHA = "Varinha"
VARINHA_ATK = "Combate à Distância: Varinha"


def magia(id_, nome, categoria, catalogo, descricao, arranjo=VARINHA, graduacao=None, graduacao_np=None,
          estatistica=None, pericia=None, ano_minimo=1, so_npc=False, tags=(), **extras):
    dados = {
        "id": id_,
        "nome": nome,
        "categoria": categoria,
        "catalogo": catalogo,
        "descricao": descricao,
        "ano_minimo": ano_minimo,
        "tags": list(tags),
    }
    for chave, valor in (
        ("arranjo", arranjo),
        ("graduacao", graduacao),
        ("graduacao_np", graduacao_np),
        ("estatistica", estatistica),
        ("pericia", pericia),
    ):
        if valor is not None:
            dados[chave] = valor
    if so_npc:
        dados["so_npc"] = True
    dados.update(extras)
    return dados


FEITICOS = [
    # ---- Ano 1 (Feitiços iniciais)
    magia("lumus", "Lumus", "utilidade", "de_transformacao__dedo_de_chave",
          "Acende um ponto de luz branca na ponta da varinha. (1º ano)",
          graduacao=1, estatistica="Ambiente 1 (Luz na ponta da varinha)", ano_minimo=1, tags=["utilidade", "luz"]),
    magia("nox", "Nox", "utilidade", "de_transformacao__dedo_de_chave",
          "Apaga a luz produzida por Lumus ou reduz a iluminação imediata. (1º ano)",
          graduacao=1, estatistica="Ambiente 1 (Apagar luz)", ano_minimo=1, tags=["utilidade"]),
    magia("wingardium_leviosa", "Wingardium Leviosa", "encantamento", "cineticos__telecinesia",
          "Faz objetos levitarem e se moverem suavemente pelo ar. (1º ano)",
          graduacao_np=-1, estatistica="Mover Objetos (telecinesia mágica)", ano_minimo=1,
          tags=["utilidade", "telecinesia"]),
    magia("alohomora", "Alohomora", "encantamento", "de_transformacao__dedo_de_chave",
          "Destranca portas e baús fechados com chaves ou feitiços simples. (1º ano)",
          graduacao=1, estatistica="Característica 1 (+10 para abrir trancas)", ano_minimo=1,
          tags=["utilidade", "exploracao"]),
    magia("colloportus", "Colloportus", "encantamento", "aquaticos__parede_de_agua",
          "Tranca e sela uma porta magicamente contra abertura comum. (1º ano)",
          graduacao=2, estatistica="Criar 2 (Selo mágico de porta)", ano_minimo=1,
          tags=["utilidade", "protecao"]),
    magia("reparo", "Reparo", "encantamento", "de_transformacao__cura_metamorfica",
          "Conserta objetos quebrados, restaurando peças partidas. (1º ano)",
          graduacao=2, estatistica="Transformar/Consertar objetos quebrados 2", ano_minimo=1,
          tags=["utilidade"]),
    magia("pericullum", "Pericullum", "utilidade", "magicos__fantasmas_de_phoros_2",
          "Lança centelhas vermelhas para o céu como sinal de socorro. (1º ano)",
          graduacao=1, estatistica="Ilusão Visual 1 (Sinalizador de centelhas vermelhas)",
          ano_minimo=1, tags=["utilidade", "luz"]),
    magia("incendio", "Incendio", "combate", "flamejantes__explosao_de_fogo",
          "Produz chamas da ponta da varinha para acender tochas ou queimar obstáculos. (1º ano)",
          graduacao_np=0, estatistica="Dano à Distância (fogo)", pericia=VARINHA_ATK,
          ano_minimo=1, tags=["combate", "fogo"]),
    magia("rictusempra", "Rictusempra", "duelo", "magicos__algemas_brilhantes_de_sirrion",
          "Feitiço das cócegas que desestabiliza e derruba o oponente rindo. (1º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Vontade; tonto, atordoado)",
          pericia=VARINHA_ATK, ano_minimo=1, tags=["duelo", "controle"]),
    magia("tarantallegra", "Tarantallegra", "duelo", "magicos__algemas_brilhantes_de_sirrion",
          "Faz as pernas do oponente dançarem sem parar. (1º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Esquiva; impedido, imóvel)",
          pericia=VARINHA_ATK, ano_minimo=1, tags=["duelo", "controle"]),
    magia("petrificus_totalus", "Petrificus Totalus", "duelo", "animais__teia",
          "Petrifica o alvo, deixando o corpo rígido com os braços colados. (1º ano)",
          graduacao_np=-1, estatistica="Aflição Cumulativa à Distância (Esquiva; impedido e vulnerável, indefeso e imóvel)",
          pericia=VARINHA_ATK, ano_minimo=1, tags=["duelo", "controle"]),
    magia("trip", "Trip (Azaração de Tropeço)", "duelo", "climaticos__rajada_ventosa",
          "Faz o alvo tropeçar e cair no chão. (1º ano)",
          graduacao_np=0, estatistica="Mover Objetos, Limitado a Derrubar",
          pericia=VARINHA_ATK, ano_minimo=1, tags=["duelo", "controle"]),

    # ---- Ano 2
    magia("expelliarmus", "Expelliarmus", "duelo", "cineticos__rajada_cinetica",
          "Feitiço de desarmamento clássico: arranca a varinha ou objeto das mãos do alvo. (2º ano)",
          graduacao_np=0, estatistica="Dano à Distância / Desarmar (força cinética)",
          pericia=VARINHA_ATK, ano_minimo=2, tags=["duelo", "combate"]),
    magia("aparecium", "Aparecium", "utilidade", "sombrios__visao_no_escuro",
          "Faz tinta oculta, mensagens secretas ou inscrições invisíveis aparecerem. (2º ano)",
          graduacao=2, estatistica="Sentidos 2 (Revelar escrita e tinta invisível)", ano_minimo=2,
          tags=["utilidade", "investigacao"]),
    magia("aranea_exumai", "Aranea Exumai", "combate", "cineticos__explosao_cinetica",
          "Rajada de impacto para repelir aranhas e criaturas rastejantes. (2º ano)",
          graduacao_np=-1, estatistica="Dano de Explosão em Área (cinética)", ano_minimo=2,
          tags=["combate", "area"]),
    magia("engorgio", "Engorgio", "transfiguracao", "de_tamanho_massa__aumento_de_densidade",
          "Faz o objeto ou criatura alvo crescer de tamanho. (2º ano)",
          graduacao=2, estatistica="Crescimento 2 (Afeta Outros)", ano_minimo=2, tags=["transfiguracao"]),
    magia("reducio", "Reducio", "transfiguracao", "de_tamanho_massa__raio_encolhedor",
          "Reduz o tamanho do objeto ou criatura atingida. (2º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Encolhimento)", pericia=VARINHA_ATK,
          ano_minimo=2, tags=["transfiguracao"]),
    magia("diminuendo", "Diminuendo", "transfiguracao", "de_tamanho_massa__raio_encolhedor",
          "Diminui rapidamente o tamanho de um objeto selecionado. (2º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Reduzir objeto)", pericia=VARINHA_ATK,
          ano_minimo=2, tags=["transfiguracao"]),
    magia("finite_incantatem", "Finite Incantatem", "defesa", "elementais__reacao_neutralizante",
          "Encerra o efeito de um feitiço contínuo lançado em algo ou alguém. (2º ano)",
          graduacao_np=-1, custo_por_graduacao=2, estatistica="Nulificar Magia à Distância, Simultâneo",
          pericia=VARINHA_ATK, ano_minimo=2, tags=["defesa", "utilidade"]),
    magia("cara_de_lesma", "Cara-de-Lesma", "duelo", "magicos__algemas_brilhantes_de_sirrion",
          "Azaração que faz a vítima vomitar lesmas sem parar. (2º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Fortitude; tonto, atordoado)",
          pericia=VARINHA_ATK, ano_minimo=2, tags=["duelo"]),
    magia("travaligua", "Travalíngua", "duelo", "cineticos__cola_por_atrito_2",
          "Cola a língua da vítima no céu da boca, impedindo falas e feitiços verbais. (2º ano)",
          graduacao_np=0, estatistica="Aflição à Percepção (Esquiva; impede fala)",
          pericia=VARINHA_ATK, ano_minimo=2, tags=["duelo", "controle"]),
    magia("mobilicorpus", "Mobilicorpus", "encantamento", "cineticos__telecinesia",
          "Levita e move corpos inconscientes ou imóveis no ar. (2º ano)",
          graduacao_np=-1, estatistica="Mover Objetos (corpos)", ano_minimo=2, tags=["utilidade"]),
    magia("sonorus", "Sonorus", "utilidade", "ilusorios__mimetismo_vocal",
          "Aumenta magicamente o volume da voz como um megafone. (2º ano)",
          graduacao=2, estatistica="Ilusão Auditiva 2 (amplificar voz)", ano_minimo=2, tags=["utilidade"]),
    magia("quietus", "Quietus", "utilidade", "ilusorios__mimetismo_vocal",
          "Faz a voz amplificada por Sonorus voltar ao volume normal. (2º ano)",
          graduacao=1, estatistica="Controle Vocal 1 (reduzir som)", ano_minimo=2, tags=["utilidade"]),

    # ---- Ano 3
    magia("aresto_momentum", "Aresto Momentum", "defesa", "cineticos__rebote_cinetico",
          "Desacelera e para um objeto ou pessoa em queda antes do impacto. (3º ano)",
          graduacao=1, estatistica="Movimento 1 (Queda Segura)", ano_minimo=3, tags=["defesa", "movimento"]),
    magia("immobilus", "Immobilus", "controle", "climaticos__frio_artico",
          "Paralisa o movimento de criaturas pequenas ou alvos no ar. (3º ano)",
          graduacao_np=-1, estatistica="Aflição Cumulativa à Distância (Esquiva; impedido, imóvel)",
          pericia=VARINHA_ATK, ano_minimo=3, tags=["controle", "duelo"]),
    magia("ridikkulus", "Riddikulus", "defesa", "magicos__censura_de_lamal",
          "Transforma um bicho-papão em algo engraçado, anulando seu terror. (3º ano)",
          graduacao_np=0, estatistica="Aflição em Área (Vontade; contra medos e bichos-papões)",
          ano_minimo=3, tags=["defesa", "controle"]),
    magia("expecto_patronum", "Expecto Patronum", "defesa", "magicos__sinal_de_modrossus_3",
          "Conjura um guardião prateado de energia positiva que repele Dementadores e envia mensagens. (3º ano)",
          graduacao_np=0, estatistica="Aflição em Área (Vontade; repele criaturas das trevas)",
          ano_minimo=3, tags=["defesa", "luz"]),
    magia("glacius", "Glacius", "combate", "congelantes__rajada_de_gelo",
          "Congela água, objetos ou criaturas atingidas pelo feixe gélido. (3º ano)",
          graduacao_np=0, estatistica="Dano à Distância (gelo)", pericia=VARINHA_ATK,
          ano_minimo=3, tags=["combate", "gelo"]),
    magia("bomba_bombarda", "Bombarda", "combate", "flamejantes__bola_de_fogo",
          "Causa uma explosão capaz de arrombar paredes ou abrir buracos. (3º ano)",
          graduacao_np=-1, estatistica="Dano à Distância, Área Explosão (impacto)",
          ano_minimo=3, tags=["combate", "area"]),
    magia("reducto", "Reducto", "combate", "cineticos__rajada_cinetica",
          "Desintegra ou estilhaça objetos sólidos que estejam no caminho. (3º ano)",
          graduacao_np=0, estatistica="Dano à Distância (desintegração física)", pericia=VARINHA_ATK,
          ano_minimo=3, tags=["combate"]),
    magia("evanesco", "Evanesco", "transfiguracao", "de_transformacao__forma_maleavel",
          "Faz objetos pequenos desaparecerem por completo. (3º ano)",
          graduacao=1, estatistica="Desaparecer objetos pequenos", ano_minimo=3, tags=["transfiguracao"]),

    # ---- Ano 4
    magia("accio", "Accio", "encantamento", "cineticos__psicocinese_2",
          "Atrai o objeto desejado à distância até a mão do conjurador. (4º ano)",
          graduacao_np=-1, estatistica="Mover Objetos à Percepção (atrair)", ano_minimo=4,
          tags=["utilidade", "telecinesia"]),
    magia("depulso", "Depulso", "duelo", "climaticos__rajada_ventosa",
          "Arremessa objetos ou oponentes para longe com um empurrão mágico. (4º ano)",
          graduacao_np=0, estatistica="Mover Objetos, Empurrar para longe", pericia=VARINHA_ATK,
          ano_minimo=4, tags=["duelo", "telecinesia"]),
    magia("ascendio", "Ascendio", "movimento", "de_transformacao__bola_saltitante",
          "Lança o próprio conjurador imediatamente para cima (ou para fora da água). (4º ano)",
          graduacao_np=0, estatistica="Salto (propulsão vertical)", ano_minimo=4, tags=["movimento"]),
    magia("aguamenti", "Aguamenti", "encantamento", "aquaticos__modelagem_de_agua_2",
          "Conjura um jato de água limpa da ponta da varinha. (4º ano)",
          graduacao_np=-1, estatistica="Criar Água / Jato d'água", ano_minimo=4, tags=["utilidade", "agua"]),
    magia("estupeca", "Estupefaça", "duelo", "cineticos__rajada_cinetica",
          "Raio vermelho de atordoamento clássico dos duelos: derruba e faz desmaiar. (4º ano)",
          graduacao_np=0, estatistica="Dano à Distância / Atordoamento (força mágica)",
          pericia=VARINHA_ATK, ano_minimo=4, tags=["duelo", "combate"]),
    magia("incarcerous", "Incarcerous", "duelo", "animais__teia",
          "Conjura cordas grossas que se enrolam e prendem o corpo do alvo. (4º ano)",
          graduacao_np=-1, estatistica="Aflição Cumulativa à Distância (Esquiva; impedido, imóvel)",
          pericia=VARINHA_ATK, ano_minimo=4, tags=["duelo", "controle"]),
    magia("avis", "Avis", "transfiguracao", "animais__criar_quimera",
          "Conjura um pequeno bando de pássaros da ponta da varinha. (4º ano)",
          graduacao=2, estatistica="Invocar Pássaros 2", ano_minimo=4, tags=["transfiguracao"]),
    magia("oppugno", "Oppugno", "duelo", "animais__companheiro_animal",
          "Faz objetos ou pequenas criaturas conjuradas atacarem alguém. (4º ano)",
          graduacao_np=-1, estatistica="Invocar/Comandar Ataque", ano_minimo=4, tags=["duelo"]),

    # ---- Ano 5
    magia("salvio_hexia", "Salvio Hexia / Protego", "defesa", "cineticos__deflexao_cinetica",
          "Cria um campo protetor que deflete feitiços e protege o bruxo ou área. (5º ano)",
          graduacao_np=0, estatistica="Deflexão Mágica", ano_minimo=5, tags=["defesa", "duelo"]),
    magia("cave_inimicum", "Cave Inimicum", "defesa", "aquaticos__parede_de_agua",
          "Ergue uma barreira protetora invisível em torno de um acampamento ou sala. (5º ano)",
          graduacao_np=0, estatistica="Criar Barreira Protetora", ano_minimo=5, tags=["defesa", "utilidade"]),
    magia("confundus", "Confundus", "mental", "mentais__controle_mental",
          "Confunde a mente da vítima, deixando-a desorientada ou sugestionável. (5º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Vontade; tonto, atordoado)",
          pericia=VARINHA_ATK, ano_minimo=5, tags=["controle", "mental"]),
    magia("episkey", "Episkey", "cura", "vitais__cura",
          "Cura pequenos machucados, narizes quebrados e cortes recentes. (5º ano)",
          graduacao_np=-1, estatistica="Cura Mágica", ano_minimo=5, tags=["cura"]),
    magia("braquium_remendo", "Braquium Remendo", "cura", "vitais__cura",
          "Emenda ossos quebrados do braço ou membros (com cuidado na pronúncia). (5º ano)",
          graduacao_np=0, estatistica="Cura de Ossos", ano_minimo=5, tags=["cura"]),
    magia("anapneo", "Anapneo", "cura", "vitais__cura",
          "Desobstrui imediatamente a traqueia e as vias respiratórias do alvo. (5º ano)",
          graduacao=2, estatistica="Cura 2 (desobstrução)", ano_minimo=5, tags=["cura"]),
    magia("erecto", "Erecto", "encantamento", "cineticos__construcoes_de_forca",
          "Monta tendas, estruturas ou andaimes dobrados num piscar de olhos. (5º ano)",
          graduacao=3, estatistica="Criar Estruturas 3", ano_minimo=5, tags=["utilidade"]),

    # ---- Ano 6 e 7 (Avançados)
    magia("homenum_revelio", "Homenum Revelio", "investigacao", "sensoriais__leitura_de_aura_4",
          "Revela a presença humana oculta num cômodo ou edifício próximo. (6º ano)",
          graduacao=3, estatistica="Sentidos 3 (Detectar Humanos à Distância)", ano_minimo=6,
          tags=["investigacao", "utilidade"]),
    magia("obliviate", "Obliviate", "mental", "magicos__nevoas_do_modrossus_2",
          "Altera ou apaga memórias específicas da vítima. (6º ano)",
          graduacao_np=-1, estatistica="Aflição à Distância (Vontade; apaga memórias)",
          pericia=VARINHA_ATK, ano_minimo=6, tags=["mental", "controle"]),
    magia("avifors", "Avifors", "transfiguracao", "de_transformacao__transformacao_banal",
          "Transfigura um objeto pequeno ou alvo em um pássaro. (6º ano)",
          graduacao_np=-1, estatistica="Aflição Cumulativa à Distância (Vontade; transformado)",
          pericia=VARINHA_ATK, ano_minimo=6, tags=["transfiguracao"]),
    magia("pullus", "Pullus", "transfiguracao", "de_transformacao__transformacao_banal",
          "Transfigura o alvo em uma galinha comum. (6º ano)",
          graduacao_np=-1, estatistica="Aflição Cumulativa à Distância (Vontade; transformado)",
          pericia=VARINHA_ATK, ano_minimo=6, tags=["transfiguracao"]),
    magia("homorfo", "Homorfo", "transfiguracao", "elementais__reacao_neutralizante",
          "Força um Animago ou criatura/objeto transfigurado a voltar à forma original. (7º ano)",
          graduacao_np=-1, custo_por_graduacao=2, estatistica="Nulificar Transfiguração à Distância",
          pericia=VARINHA_ATK, ano_minimo=7, tags=["transfiguracao", "defesa"]),

    # ---- Feitiços Proibidos / Artes das Trevas (NPCs e vilões)
    magia("avada_kedavra", "Avada Kedavra", "proibido", "fatais__maldicao_da_morte",
          "[Proibido] Maldição da Morte: raio verde que mata instantaneamente se não for esquivado.",
          graduacao_np=0, estatistica="Aflição Letal à Percepção (Vontade/Fortitude; moribundo)",
          pericia=VARINHA_ATK, ano_minimo=7, so_npc=True, tags=["proibido", "letal"]),
    magia("crucio", "Crucio", "proibido", "fatais__visao_mortal",
          "[Proibido] Maldição Cruciatus: causa dor física insuportável sem deixar marcas.",
          graduacao_np=0, estatistica="Aflição Cumulativa à Percepção (Vontade; tonto, atordoado, incapacitado)",
          pericia=VARINHA_ATK, ano_minimo=7, so_npc=True, tags=["proibido"]),
    magia("imperio", "Imperio", "proibido", "mentais__controle_mental",
          "[Proibido] Maldição Imperius: coloca a vítima sob controle total da vontade do conjurador.",
          graduacao_np=0, estatistica="Aflição à Percepção (Vontade; transe, compelido, controlado)",
          pericia=VARINHA_ATK, ano_minimo=7, so_npc=True, tags=["proibido", "mental"]),
    magia("morsmordre", "Morsmordre", "proibido", "magicos__fantasmas_de_phoros_2",
          "[Proibido] Conjura a Marca Negra nos céus como sinal dos comensais.",
          graduacao=3, estatistica="Ilusão / Sinal nos céus 3", ano_minimo=7, so_npc=True,
          tags=["proibido"]),

    # ---- Dons raros fora da varinha (opcionais / adultos)
    magia("aparatacao", "Aparatação", "dom", "de_teleporte__teleporte",
          "Teleporte instantâneo com estalo sonoro (exige licença a partir do 6º/7º ano).",
          arranjo=None, graduacao=4, estatistica="Teleporte 4", ano_minimo=6, tags=["movimento"]),
]

gravar("powers.json", FEITICOS)


# ---------------------------------------------------------------- archetypes.json & modules.json (NPCs)

NPC_ARQUETIPOS = [
    {
        "id": "estudante_rival",
        "nome": "Estudante Rival",
        "nomes": "humano",
        "capanga": True,
        "np_maximo": 6,
        "descricao": "Aluno de outra Casa pronto para duelos nos corredores ou disputas no campo.",
        "prioridades": [
            "pericia:Combate à Distância: Varinha",
            "defesa:Esquiva",
            "defesa:Vontade",
            "habilidade:Des",
            "defesa:Fortitude",
            "pericia:Percepção",
            "habilidade:Vig",
        ],
        "faixas": [
            {
                "np": 2,
                "nome": "Rival do 2º ano",
                "fonte": "Escola de Magia [Casa]",
                "status_dados": "validado",
                "observacao": "Estudante com varinha e feitiços básicos de duelo.",
                "ficha": {
                    "habilidades": {"For": 0, "Vig": 1, "Agi": 1, "Des": 1, "Lut": 0, "Int": 1, "Pro": 1, "Pre": 1},
                    "defesas_compradas": {"Esquiva": 1, "Aparar": 1, "Vontade": 1, "Fortitude": 1},
                    "pericias": {"Combate à Distância: Varinha": 1, "Percepção": 2, "Enganação": 2},
                    "vantagens": {"Iniciativa Aprimorada": 1, "Equipamento": 1},
                    "equipamento": ["varinha_padrao", "uniforme_escolar"],
                    "poderes": {
                        "expelliarmus": {"do_genero": "expelliarmus"},
                        "lumus": {"do_genero": "lumus"},
                    },
                },
            }
        ],
    },
    {
        "id": "monitor_escolar",
        "nome": "Monitor da Escola",
        "nomes": "humano",
        "capanga": True,
        "np_maximo": 7,
        "descricao": "Aluno veterano encarregado de vigiar os corredores após o toque de recolher e separar brigas.",
        "prioridades": [
            "pericia:Percepção",
            "pericia:Intuição",
            "pericia:Combate à Distância: Varinha",
            "defesa:Vontade",
            "defesa:Esquiva",
            "habilidade:Int",
            "defesa:Fortitude",
        ],
        "faixas": [
            {
                "np": 4,
                "nome": "Monitor do 5º ano",
                "fonte": "Escola de Magia [Casa]",
                "status_dados": "validado",
                "observacao": "Veterano atento com feitiços de contenção e proteção.",
                "ficha": {
                    "habilidades": {"For": 0, "Vig": 1, "Agi": 1, "Des": 2, "Lut": 1, "Int": 2, "Pro": 2, "Pre": 1},
                    "defesas_compradas": {"Esquiva": 3, "Aparar": 2, "Vontade": 3, "Fortitude": 2},
                    "pericias": {
                        "Combate à Distância: Varinha": 2,
                        "Percepção": 4,
                        "Intuição": 4,
                        "Especialidade: Teoria Mágica": 4,
                    },
                    "vantagens": {"Ritualista": 1, "Equipamento": 1},
                    "equipamento": ["varinha_padrao", "uniforme_escolar"],
                    "poderes": {
                        "petrificus_totalus": {"do_genero": "petrificus_totalus"},
                        "salvio_hexia": {"do_genero": "salvio_hexia"},
                        "lumus": {"do_genero": "lumus"},
                    },
                },
            }
        ],
    },
    {
        "id": "bruxo_das_trevas",
        "nome": "Bruxo das Trevas",
        "nomes": "humano",
        "capanga": False,
        "np_maximo": 10,
        "descricao": "Seguidor das Artes das Trevas versado em maldições e duelos implacáveis.",
        "prioridades": [
            "pericia:Combate à Distância: Varinha",
            "defesa:Esquiva",
            "defesa:Vontade",
            "habilidade:Des",
            "defesa:Fortitude",
            "pericia:Intimidação",
            "habilidade:Vig",
        ],
        "faixas": [
            {
                "np": 6,
                "nome": "Infiltrado das Trevas",
                "fonte": "Escola de Magia [Casa]",
                "status_dados": "validado",
                "observacao": "Bruxo adulto com feitiços de ataque, dor e defesa.",
                "ficha": {
                    "habilidades": {"For": 0, "Vig": 2, "Agi": 2, "Des": 2, "Lut": 1, "Int": 2, "Pro": 2, "Pre": 2},
                    "defesas_compradas": {"Esquiva": 4, "Aparar": 3, "Fortitude": 3, "Vontade": 4},
                    "pericias": {
                        "Combate à Distância: Varinha": 3,
                        "Furtividade": 4,
                        "Intimidação": 4,
                        "Especialidade: Artes das Trevas": 4,
                    },
                    "vantagens": {"Iniciativa Aprimorada": 1, "Destemido": 1, "Equipamento": 1},
                    "equipamento": ["varinha_duelo"],
                    "poderes": {
                        "estupeca": {"do_genero": "estupeca"},
                        "crucio": {"do_genero": "crucio"},
                        "salvio_hexia": {"do_genero": "salvio_hexia"},
                    },
                },
            }
        ],
    },
    {
        "id": "auror_patrulha",
        "nome": "Auror do Ministério",
        "nomes": "humano",
        "capanga": False,
        "np_maximo": 10,
        "descricao": "Investigador e duelista oficial destacado para proteger a escola ou capturar fugitivos.",
        "prioridades": [
            "pericia:Combate à Distância: Varinha",
            "defesa:Vontade",
            "defesa:Esquiva",
            "pericia:Investigação",
            "pericia:Percepção",
            "defesa:Fortitude",
            "habilidade:Des",
        ],
        "faixas": [
            {
                "np": 7,
                "nome": "Auror de Campo",
                "fonte": "Escola de Magia [Casa]",
                "status_dados": "validado",
                "observacao": "Bruxo treinado pelo Ministério com Patrono e Aparatação.",
                "ficha": {
                    "habilidades": {"For": 1, "Vig": 2, "Agi": 2, "Des": 3, "Lut": 2, "Int": 2, "Pro": 3, "Pre": 1},
                    "defesas_compradas": {"Esquiva": 4, "Aparar": 3, "Fortitude": 3, "Vontade": 4},
                    "pericias": {
                        "Combate à Distância: Varinha": 3,
                        "Investigação": 6,
                        "Percepção": 6,
                        "Intuição": 4,
                        "Especialidade: Artes das Trevas": 4,
                    },
                    "vantagens": {"Iniciativa Aprimorada": 1, "Destemido": 1, "Rolamento Defensivo": 1, "Equipamento": 1},
                    "equipamento": ["varinha_duelo"],
                    "poderes": {
                        "estupeca": {"do_genero": "estupeca"},
                        "expelliarmus": {"do_genero": "expelliarmus"},
                        "expecto_patronum": {"do_genero": "expecto_patronum"},
                        "salvio_hexia": {"do_genero": "salvio_hexia"},
                        "aparatacao": {"do_genero": "aparatacao"},
                    },
                },
            }
        ],
    },
]

gravar("archetypes.json", NPC_ARQUETIPOS)

NPC_MODULOS = [
    {
        "id": "duelista_treinado",
        "nome": "Reflexos de Duelo",
        "epiteto": "o Duelista",
        "descricao": "Saca a varinha primeiro e mantém postura defensiva.",
        "tatica": "Tenta desarmar ou atordoar o oponente logo no primeiro turno.",
        "tags": ["combate", "duelo"],
        "estilos": ["combate", "tematico"],
        "arquetipos": ["estudante_rival", "monitor_escolar", "bruxo_das_trevas", "auror_patrulha"],
        "status_dados": "validado",
        "papel": "ambos",
        "adiciona": {
            "vantagens": {"Ataque Acurado": 1, "Ataque Defensivo": 1},
        },
    },
    {
        "id": "batedor_vassoura",
        "nome": "Voador Ágil",
        "epiteto": "dos Céus",
        "descricao": "Acostumado a manobras em alta velocidade na vassoura.",
        "tatica": "Mantém distância em voo e ataca de cima.",
        "tags": ["movimento"],
        "estilos": ["utilidade", "tematico"],
        "arquetipos": ["estudante_rival", "monitor_escolar", "bruxo_das_trevas", "auror_patrulha"],
        "status_dados": "validado",
        "papel": "ambos",
        "adiciona": {
            "pericias": {"Veículos": 2, "Acrobacia": 2},
        },
    },
    {
        "id": "especialista_azaracoes",
        "nome": "Especialista em Azarações",
        "epiteto": "o Azarador",
        "descricao": "Domina feitiços para imobilizar e confundir antes de finalizar o duelo.",
        "tatica": "Usa Incarcerous ou Confundus para isolar o alvo.",
        "tags": ["controle", "combate"],
        "estilos": ["combate", "tematico"],
        "arquetipos": ["estudante_rival", "monitor_escolar", "bruxo_das_trevas", "auror_patrulha"],
        "status_dados": "validado",
        "papel": "ambos",
        "adiciona": {
            "poderes": {
                "incarcerous": {"do_genero": "incarcerous"},
                "confundus": {"do_genero": "confundus"},
            },
        },
    },
]

gravar("modules.json", NPC_MODULOS)


# ---------------------------------------------------------------- player.json (Casas + Arquétipos de PJ)

def raca(id_, nome, descricao, vantagens=None, pericias=None, habilidades=None):
    return {
        "id": id_,
        "nome": nome,
        "descricao": descricao,
        "nomes": "humano",
        "habilidades": habilidades or {},
        "vantagens": vantagens or {},
        "pericias": pericias or {},
        "poderes": [],
    }


CASAS = [
    raca("grifinoria", "Grifinória",
         "Valoriza coragem, ousadia e cavalheirismo. (+Destemido, Atletismo +2)",
         vantagens={"Destemido": 1}, pericias={"Atletismo": 2}),
    raca("corvinal", "Corvinal",
         "Valoriza inteligência, estudo e criatividade. (+Memória Eidética, Investigação +2)",
         vantagens={"Memória Eidética": 1}, pericias={"Investigação": 2}),
    raca("lufa_lufa", "Lufa-Lufa",
         "Valoriza lealdade, paciência e trabalho duro. (+Trabalho em Equipe, Herbologia +2)",
         vantagens={"Trabalho em Equipe": 1}, pericias={"Especialidade: Herbologia": 2}),
    raca("sonserina", "Sonserina",
         "Valoriza ambição, astúcia e liderança. (+Bem Informado, Enganação +2)",
         vantagens={"Bem Informado": 1}, pericias={"Enganação": 2}),
    raca("visitante", "Sem Casa (Adulto / Visitante)",
         "Para bruxos já formados, professores ou visitantes de outras escolas (0 PP).",
         ),
]

FALHA_VARINHA = {
    "id": "varinha_removivel",
    "nome": "Varinha (Removível)",
    "arranjo": VARINHA,
    "custo": -1,
    "descricao": "Sem a varinha o bruxo não consegue conjurar os feitiços do arranjo (pode ser desarmado).",
}


def arq_bruxo(id_, nome, conceito, vantagens_ess, vantagens_opc, prioridades, focos, itens_ess, itens_opc):
    return {
        "id": id_,
        "nome": nome,
        "conceito": conceito,
        "vantagens_essenciais": vantagens_ess,
        "vantagens_opcionais": vantagens_opc,
        "prioridades": prioridades,
        "sugestoes": {
            "motivacoes": ["Amizade", "Conhecimento", "Honra da Casa", "Justiça", "Desvendar Mistérios"],
            "complicacoes": [
                {"nome": "Rivalidade entre Casas", "detalhe": "Um colega vive tentando provocá-lo para um duelo."},
                {"nome": "Laço emocional intenso (Mapa de Relacionamentos)", "detalhe": "Um relacionamento (+3 a +5) entra em perigo na trama."},
                {"nome": "Curiosidade perigosa", "detalhe": "Não resiste a portas trancadas e boatos da floresta."},
            ],
        },
        "focos": focos,
        "implantes": {"essenciais": ["lumus"], "opcionais": []},
        "armas": {"principais": ["varinha_padrao"], "secundarias": []},
        "itens": {"essenciais": itens_ess, "opcionais": itens_opc},
    }


def foco_bruxo(id_, nome, desc, poderes, prioridades_extras=None, vantagens_extras=None, itens_extras=None):
    return {
        "id": id_,
        "nome": nome,
        "descricao": desc,
        "implantes": poderes[:2],
        "implantes_opcionais": poderes[2:],
        "falhas": [FALHA_VARINHA],
        "vantagens": vantagens_extras or [],
        "prioridades": prioridades_extras or [],
        "armas": [],
        "itens": itens_extras or [],
    }


ARQUETIPOS_PJ = [
    arq_bruxo(
        "estudante", "Estudante",
        "Aluno da escola de magia (recomendado NP 2 no 1º-2º ano até NP 6 no 7º ano).",
        ["Ritualista"],
        ["Sorte", "Rolamento Defensivo", "Iniciativa Aprimorada", "Trabalho em Equipe"],
        [
            "pericia:Combate à Distância: Varinha", "defesa:Esquiva", "defesa:Vontade",
            "habilidade:Int", "habilidade:Des", "pericia:Percepção",
            "pericia:Especialidade: Teoria Mágica", "defesa:Fortitude",
        ],
        [
            foco_bruxo(
                "duelista", "Duelista",
                "Focado em Defesa contra as Artes das Trevas, reflexos rápidos e feitiços de duelo.",
                ["expelliarmus", "estupeca", "petrificus_totalus", "salvio_hexia", "lumus"],
                ["pericia:Combate à Distância: Varinha", "habilidade:Des", "defesa:Esquiva"],
                ["Iniciativa Aprimorada", "Ataque Acurado"],
            ),
            foco_bruxo(
                "estudioso", "Estudioso",
                "Brilha em Feitiços, Transfiguração e Teoria Mágica, com repertório variado.",
                ["wingardium_leviosa", "lumus", "reparo", "alohomora", "finite_incantatem", "aparecium"],
                ["habilidade:Int", "pericia:Especialidade: Teoria Mágica", "defesa:Vontade"],
                ["Memória Eidética"],
                ["livros_ano"],
            ),
            foco_bruxo(
                "encrenqueiro", "Encrenqueiro / Explorador",
                "Especialista em passagens secretas, toque de recolher e pegadinhas mágicas.",
                ["alohomora", "lumus", "nox", "rictusempra", "tarantallegra", "confundus"],
                ["pericia:Furtividade", "pericia:Investigação", "habilidade:Agi"],
                ["Sorte"],
                ["orelha_extensivel"],
            ),
            foco_bruxo(
                "herbologista", "Herbologista / Curandeiro",
                "Cuida de estufas, poções restauradoras e primeiros socorros mágicos.",
                ["aguamenti", "episkey", "braquium_remendo", "lumus", "incendio"],
                ["pericia:Especialidade: Herbologia", "pericia:Especialidade: Poções", "pericia:Tratamento"],
                [],
                ["kit_pocoes", "pocao_cura"],
            ),
            foco_bruxo(
                "quadribol", "Jogador de Quadribol",
                "Ágil na vassoura, com ótimos reflexos para evitar balaços e mergulhos.",
                ["aresto_momentum", "ascendio", "accio", "expelliarmus", "lumus"],
                ["pericia:Veículos", "pericia:Atletismo", "pericia:Acrobacia", "habilidade:Agi"],
                ["Iniciativa Aprimorada"],
                ["vassoura_escolar"],
            ),
        ],
        ["varinha_padrao", "uniforme_escolar"],
        ["kit_estudante", "livros_ano", "caldeirao_estanho", "coruja_correio"],
    ),
    arq_bruxo(
        "bruxo_formado", "Bruxo formado",
        "Adulto graduado: auror, curandeiro ou pesquisador (recomendado NP 7 a 10).",
        ["Ritualista", "Iniciativa Aprimorada"],
        ["Sorte", "Rolamento Defensivo", "Bem Informado", "Destemido"],
        [
            "pericia:Combate à Distância: Varinha", "defesa:Esquiva", "defesa:Vontade",
            "habilidade:Des", "habilidade:Int", "pericia:Investigação", "defesa:Fortitude",
        ],
        [
            foco_bruxo(
                "auror", "Auror",
                "Investigador e duelista de elite contra as Artes das Trevas.",
                ["estupeca", "expelliarmus", "expecto_patronum", "salvio_hexia", "homenum_revelio", "aparatacao"],
                ["pericia:Combate à Distância: Varinha", "pericia:Investigação", "pericia:Especialidade: Artes das Trevas"],
                ["Destemido", "Ataque Acurado"],
                ["estojo_varinha"],
            ),
            foco_bruxo(
                "curandeiro", "Curandeiro",
                "Especialista em feitiços médicos, poções complexas e remoção de azarações.",
                ["episkey", "braquium_remendo", "anapneo", "finite_incantatem", "salvio_hexia", "aparatacao"],
                ["pericia:Tratamento", "pericia:Especialidade: Poções", "habilidade:Int"],
                [],
                ["pocao_cura", "antidoto_comum"],
            ),
            foco_bruxo(
                "pesquisador", "Professor / Pesquisador",
                "Mestre de teoria mágica, encantamentos antigos e proteção do castelo.",
                ["salvio_hexia", "cave_inimicum", "finite_incantatem", "reparo", "expecto_patronum", "aparatacao"],
                ["habilidade:Int", "pericia:Especialidade: Teoria Mágica", "defesa:Vontade"],
                ["Memória Eidética"],
                ["livros_ano"],
            ),
        ],
        ["varinha_padrao"],
        ["pocao_cura", "bisbilhotoscopio", "vassoura_passeio"],
    ),
]

gravar("player.json", {
    "_fonte": "Casas inspiradas em Hogwarts como pacotes de base (2 PP), deixando os estilos de estudante livres.",
    "riqueza": [
        {"id": "bolsista", "nome": "Bolsista / Família humilde (Riqueza 4)", "riqueza": 4, "dinheiro": 30,
         "beneficio": 0, "ajuste_de_pontos": 1,
         "descricao": "Usa livros de segunda mão e vestes reformadas. Devolve 1 PP."},
        {"id": "comum", "nome": "Família bruxa comum (Riqueza 8)", "riqueza": 8, "dinheiro": 80,
         "beneficio": 0, "ajuste_de_pontos": 0,
         "descricao": "Padrão: cobre uniforme, varinha, caldeirão e livros do ano."},
        {"id": "abastada", "nome": "Família tradicional (Benefício: Riqueza 1)", "riqueza": 12, "dinheiro": 200,
         "beneficio": 1, "ajuste_de_pontos": 0,
         "descricao": "Custa 1 PP. Dá para comprar vassoura de corrida e poções extras."},
        {"id": "puro_sangue_rico", "nome": "Linhagem muito rica (Benefício: Riqueza 2)", "riqueza": 16, "dinheiro": 600,
         "beneficio": 2, "ajuste_de_pontos": 0,
         "descricao": "Custa 2 PP. Acesso fácil a itens raros e equipamentos de ponta."},
    ],
    "racas": CASAS,
    "arquetipos": ARQUETIPOS_PJ,
})


# ---------------------------------------------------------------- names.json & complications.json

gravar("names.json", {
    "humano": {
        "nomes": [
            "Arthur", "Cedric", "Neville", "Oliver", "Colin", "Seamus", "Dean", "Percy",
            "Gideon", "Fabian", "Teddy", "Albus", "Scorpius", "Hugo", "Sebastian", "Garreth",
            "Hermione", "Luna", "Gina", "Padma", "Parvati", "Cho", "Hannah", "Susan",
            "Nymphadora", "Lily", "Angelina", "Katie", "Lavender", "Poppy", "Imelda", "Natsai",
        ],
        "sobrenomes": [
            "Abbott", "Bones", "Boot", "Brown", "Chang", "Clearwater", "Creevey", "Diggory",
            "Finch-Fletchley", "Finnigan", "Goldstein", "Jordan", "Longbottom", "Lovegood",
            "Macmillan", "Patil", "Spinnet", "Thomas", "Weasley", "Wood", "Sallow", "Ominis",
        ],
    },
})

gravar("complications.json", {
    "motivacoes": [
        {"id": "amizade", "nome": "Amizade", "exemplo": "Protege os colegas e nunca abandona um amigo em apuros."},
        {"id": "conhecimento", "nome": "Conhecimento", "exemplo": "Busca dominar feitiços raros e segredos da magia."},
        {"id": "honra_casa", "nome": "Honra da Casa", "exemplo": "Quer trazer orgulho e pontos para sua Casa."},
        {"id": "justica", "nome": "Justiça", "exemplo": "Enfrenta abusos, preconceitos e ameaças das Artes das Trevas."},
        {"id": "misterios", "nome": "Desvendar Mistérios", "exemplo": "Não descansa até descobrir o que está por trás dos boatos do castelo."},
    ],
    "complicacoes": [
        {"id": "rival_casa", "nome": "Rivalidade entre Casas",
         "exemplo": "Um colega de outra Casa sempre tenta sabotá-lo ou provocá-lo para um duelo."},
        {"id": "segredo_corredor", "nome": "Curiosidade perigosa",
         "exemplo": "Não resiste a investigar portas trancadas, boatos da floresta ou livros restritos."},
        {"id": "varinha_temperamental", "nome": "Varinha temperamental",
         "exemplo": "Sob estresse extremo, a varinha às vezes solta faíscas ou atrasa o efeito."},
        {"id": "detencao_pendente", "nome": "Na mira da monitoria",
         "exemplo": "Professores e monitores vigiam seus passos após uma infração anterior."},
        {"id": "laco_profundo", "nome": "Laço emocional intenso (Mapa de Relacionamentos)",
         "exemplo": "Um relacionamento (+3 a +5) que coloca um amigo, familiar ou rival em perigo no meio da trama."},
        {"id": "fobia_criatura", "nome": "Medo de criatura mágica",
         "exemplo": "Paralisa ou hesita diante de aranhas gigantes, dementadores ou bichos-papões."},
        {"id": "honra_da_casa", "nome": "Orgulho da Casa",
         "exemplo": "Recusa-se a recuar se isso custar pontos da Casa ou parecer covardia."},
        {"id": "origem_trouxa", "nome": "Segredo sobre o mundo comum",
         "exemplo": "Precisa equilibrar deveres escolares com a família que desconhece ou teme a magia."},
    ],
})

print("Arquivos básicos de escola_de_magia gravados em", PASTA)
