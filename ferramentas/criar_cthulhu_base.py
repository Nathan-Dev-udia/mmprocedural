"""Gera os arquivos básicos do gênero Chamado de Cthulhu (anos 1920): gênero, equipamento,
ocupações (arquétipos), NPCs, nomes, complicações e módulos.

Uso: python ferramentas/criar_cthulhu_base.py
"""

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "dados" / "generos" / "cthulhu"
PASTA.mkdir(parents=True, exist_ok=True)


def gravar(nome, conteudo):
    caminho = PASTA / nome
    caminho.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gravado {caminho}")


# ---------------------------------------------------------------- genero.json

gravar("genero.json", {
    "id": "cthulhu",
    "nome": "Chamado de Cthulhu",
    "descricao": "Horror cósmico e investigação nos anos 1920: investigadores comuns, mistérios arcanos e os horrores indescritíveis do Mythos de Cthulhu.",
    "perfis_de_poder": [],
    "configuracoes": {
        "rotulo_poderes": "Feitiços arcanos",
        "rotulo_arquetipo": "Ocupação",
        "rotulo_foco": "Especialidade",
        "equipamento": "dinheiro",
        "moeda": "$",
        "np_padrao_jogador": 3,
        "nps_disponiveis": [1, 2, 3, 4, 5],
        "nps_jogador": [1, 2, 3, 4, 5],
        "sanidade": True,
        "itens_basicos": [],
        "prioridades_gerais": [
            "defesa:Vontade",
            "defesa:Esquiva",
            "defesa:Aparar",
            "defesa:Fortitude",
            "pericia:Percepção",
            "pericia:Intuição",
            "pericia:Investigação",
            "vantagem:Rolamento Defensivo",
            "habilidade:Int",
            "habilidade:Vig"
        ]
    }
})


# ---------------------------------------------------------------- equipment.json

def arma(id_item, nome, custo, tipo_atk, efeito, pericia, critico, preco, categoria, comercio,
         peso=1.0, tiros=None, municao=None, soma_forca=False, alcance_tipo="distancia", notas=""):
    d = {
        "id": id_item,
        "nome": nome,
        "custo": custo,
        "ataque": {
            "tipo": tipo_atk,
            "efeito": efeito,
            "pericia": pericia,
            "critico": critico
        },
        "preco": preco,
        "categoria": categoria,
        "comercio": comercio,
        "peso": peso,
        "notas": notas
    }
    if soma_forca:
        d["ataque"]["soma_forca"] = True
    if tiros:
        d["tiros"] = tiros
    if municao:
        d["municao"] = municao
    return d


def item(id_item, nome, custo, preco, categoria, comercio, peso=0.5, descricao="", protecao=None, velocidade=None, carga=None):
    d = {
        "id": id_item,
        "nome": nome,
        "custo": custo,
        "preco": preco,
        "categoria": categoria,
        "comercio": comercio,
        "peso": peso,
        "descricao": descricao
    }
    if protecao is not None:
        d["protecao"] = protecao
    if velocidade is not None:
        d["velocidade"] = velocidade
    if carga is not None:
        d["carga"] = carga
    return d


equipamentos = [
    # Armas de fogo
    arma("revolver_38", "Revólver .38 Special", 6, "distancia", 3, "Combate à Distância: Pistolas", 20, 25, "Arma de fogo", "Armeiro", peso=1.0, tiros=6, municao="municao_38"),
    arma("pistola_colt_45", "Pistola Colt .45 M1911", 8, "distancia", 4, "Combate à Distância: Pistolas", 20, 35, "Arma de fogo", "Armeiro", peso=1.2, tiros=7, municao="municao_45"),
    arma("pistola_bolso_32", "Pistola de bolso .32", 4, "distancia", 2, "Combate à Distância: Pistolas", 20, 15, "Arma de fogo", "Armeiro", peso=0.4, tiros=6, municao="municao_32"),
    arma("rifle_ferrolho_30_06", "Rifle de ferrolho Springfield .30-06", 10, "distancia", 5, "Combate à Distância: Rifles", 20, 45, "Arma de fogo", "Armeiro", peso=4.0, tiros=5, municao="municao_rifle"),
    arma("escopeta_12", "Escopeta calibre 12", 10, "distancia", 5, "Combate à Distância: Escopetas", 20, 40, "Arma de fogo", "Armeiro", peso=3.5, tiros=2, municao="cartuchos_12"),
    arma("submetralhadora_thompson", "Submetralhadora Thompson .45", 12, "distancia", 4, "Combate à Distância: Submetralhadoras", 20, 200, "Arma de fogo", "Mercado negro", peso=5.0, tiros=50, municao="tambor_thompson", notas="Multiataque"),

    # Armas brancas
    arma("faca_bowie", "Faca Bowie", 2, "corpo", 1, "Combate Corpo-a-Corpo: Facas", 19, 3, "Arma branca", "Armeiro", peso=0.5, soma_forca=True),
    arma("cassetete", "Cassetete policial", 2, "corpo", 1, "Combate Corpo-a-Corpo: Bastões", 20, 2, "Arma branca", "Armeiro", peso=0.5, soma_forca=True),
    arma("soqueira", "Soqueira de bronze", 1, "corpo", 1, "Combate Corpo-a-Corpo: Briga", 20, 1, "Arma branca", "Armeiro", peso=0.3, soma_forca=True),
    arma("porrete", "Porrete de madeira", 2, "corpo", 2, "Combate Corpo-a-Corpo: Bastões", 20, 2, "Arma branca", "Loja de ferragens", peso=1.0, soma_forca=True),
    arma("pe_de_cabra", "Pé de cabra de ferro", 2, "corpo", 2, "Combate Corpo-a-Corpo: Bastões", 20, 2, "Arma branca", "Loja de ferragens", peso=2.0, soma_forca=True),

    # Explosivos
    arma("dinamite", "Dinamite (banana com estopim)", 10, "area", 5, "Combate à Distância: Arremesso", 20, 3, "Explosivo", "Loja de ferragens", peso=0.5, notas="Área de explosão"),

    # Munição
    item("municao_38", "Munição .38 Special (50 balas)", 1, 2, "Munição", "Armeiro", peso=1.0),
    item("municao_45", "Munição .45 ACP (50 balas)", 1, 3, "Munição", "Armeiro", peso=1.5),
    item("municao_32", "Munição .32 ACP (50 balas)", 1, 2, "Munição", "Armeiro", peso=0.8),
    item("municao_rifle", "Munição de rifle .30-06 (20 balas)", 1, 2, "Munição", "Armeiro", peso=1.0),
    item("cartuchos_12", "Cartuchos calibre 12 (25 cartuchos)", 1, 2, "Munição", "Armeiro", peso=1.0),
    item("tambor_thompson", "Tambor com 50 balas para Thompson", 2, 10, "Munição", "Mercado negro", peso=2.5),

    # Veículos
    item("ford_modelo_t", "Automóvel Ford Modelo T", 8, 300, "Veículos", "Concessionária", peso=750, velocidade=4, carga=400, descricao="Velocidade 4 (60 km/h), transporte popular dos anos 20."),
    item("packard_luxo", "Automóvel de Luxo Packard", 10, 2500, "Veículos", "Concessionária", peso=1500, velocidade=5, carga=500, descricao="Velocidade 5 (120 km/h), potente e confortável."),
    item("motocicleta", "Motocicleta com sidecar", 9, 200, "Veículos", "Concessionária", peso=250, velocidade=5, carga=150, descricao="Velocidade 5 (120 km/h), ágil em ruas e trilhas."),

    # Equipamento investigativo
    item("lanterna_eletrica", "Lanterna elétrica a pilha", 1, 2, "Equipamento geral", "Loja de ferragens", peso=0.5, descricao="Ilumina 9 m de raio."),
    item("camera_fotografica", "Câmera fotográfica com tripé e placas", 2, 20, "Equipamento geral", "Loja de departamentos", peso=3.0, descricao="Registra imagens e evidências."),
    item("maleta_medica", "Maleta médica", 2, 25, "Equipamento geral", "Farmácia", peso=3.5, descricao="Instrumentos cirúrgicos e remédios essenciais para Tratamento."),
    item("gazuas", "Ferramentas de chaveiro (gazuas)", 1, 10, "Equipamento geral", "Mercado negro", peso=0.5, descricao="Ferramentas para abrir fechaduras."),
    item("binoculos", "Binóculos prismáticos", 1, 15, "Equipamento geral", "Loja de departamentos", peso=1.0, descricao="Visão ampliada à distância."),
    item("maquina_escrever", "Máquina de escrever portátil", 1, 30, "Equipamento geral", "Loja de departamentos", peso=5.0, descricao="Redação de artigos e relatórios."),
    item("caderno_caneta", "Caderno de notas e caneta-tinteiro", 0, 1, "Equipamento geral", "Loja de departamentos", peso=0.3, descricao="Anotações de pistas e nomes."),
    item("relogio_bolso", "Relógio de bolso", 0, 5, "Equipamento geral", "Loja de departamentos", peso=0.2),
    item("lupa", "Lupa de aumento", 0, 2, "Equipamento geral", "Loja de departamentos", peso=0.2, descricao="Examina pistas minuciosas."),
    item("cantil", "Cantil de metal com água", 0, 1, "Equipamento geral", "Loja de departamentos", peso=1.5),
    item("isqueiro_cigarros", "Isqueiro e maço de cigarros", 0, 0.5, "Equipamento geral", "Tabacaria", peso=0.1),
    item("gravador_fonografo", "Fonógrafo portátil de cilindros", 2, 35, "Equipamento geral", "Loja de departamentos", peso=6.0, descricao="Grava áudio em cilindros de cera."),
    item("corda_15m", "Corda de cânhamo (15 m)", 1, 2, "Equipamento geral", "Loja de ferragens", peso=3.0),
    item("mochila_couro", "Mala ou pasta executiva de couro", 1, 5, "Equipamento geral", "Loja de departamentos", peso=1.5),
    item("kit_quimica", "Maleta de reagentes químicos", 2, 30, "Equipamento geral", "Farmácia", peso=4.0, descricao="Testes e análises laboratoriais."),

    # Roupas
    item("terno_tres_pecas", "Terno de três peças", 0, 20, "Roupas", "Alfaiataria", peso=2.0),
    item("sobretudo_pesado", "Sobretudo pesado de lã", 1, 25, "Roupas", "Alfaiataria", peso=2.5, protecao=1, descricao="Proteção 1 contra frio e arranhões."),
    item("chapeu_fedora", "Chapéu fedora", 0, 5, "Roupas", "Alfaiataria", peso=0.2),
    item("vestido_melindrosa", "Vestido melindrosa anos 20", 0, 15, "Roupas", "Alfaiataria", peso=1.0),
    item("botas_pesadas", "Botas de couro resistentes", 0, 8, "Roupas", "Alfaiataria", peso=1.5),

    # Serviços e Viagem
    item("passagem_trem", "Passagem de trem (por 50 km)", 0, 1.5, "Serviços", "Estação ferroviária", peso=0),
    item("passagem_navio", "Passagem em transatlântico a vapor", 0, 100, "Serviços", "Porto", peso=0),
    item("telegrama", "Telegrama Western Union (por palavra)", 0, 0.05, "Serviços", "Telégrafo", peso=0),
    item("telefonema", "Telefonema interurbano", 0, 5, "Serviços", "Central telefônica", peso=0),
    item("consulta_medica", "Consulta médica", 0, 3, "Serviços", "Consultório médico", peso=0),
    item("hotel_quarto", "Diária de hotel de padrão médio", 0, 2.5, "Serviços", "Hotel", peso=0),
    item("refeicao_restaurante", "Refeição completa em restaurante", 0, 0.5, "Serviços", "Restaurante", peso=0),
]

gravar("equipment.json", equipamentos)


# ---------------------------------------------------------------- complications.json

complications_data = {
    "_fonte": "Chamado de Cthulhu 7ª edição (regras de Sanidade, fobias e manias) adaptado para Mutantes & Malfeitores 3ª edição.",
    "motivacoes": [
        {"nome": "Justiça", "exemplo": "Ver os inocentes protegidos e a verdade revelada."},
        {"nome": "Conhecimento", "exemplo": "A busca implacável pela verdade cósmica e mistérios proibidos."},
        {"nome": "Dever Profissional", "exemplo": "Cumprir seu trabalho como detetive, jornalista, médico ou policial."},
        {"nome": "Proteção de Inocentes", "exemplo": "Salvar entes queridos e inocentes dos horrores das sombras."},
        {"nome": "Curiosidade Macabra", "exemplo": "Fascinado pelo bizarro e pelo inexplicável."},
        {"nome": "Vingança", "exemplo": "Destruir a criatura ou culto que arruinou sua família ou sanidade."}
    ],
    "complicacoes": [
        {"nome": "Fobia", "exemplo": "Pavor paralisante de escuridão, insetos, alturas ou corpos mortos."},
        {"nome": "Mania", "exemplo": "Compulsões neuróticas: lavagem constante, grafomania, higiene obsessiva."},
        {"nome": "Pesadelos", "exemplo": "Sonhos perturbadores com geometrias estranhas e cidades submersas."},
        {"nome": "Paranoia", "exemplo": "Desconfiança doentia de qualquer pessoa ou autoridade."},
        {"nome": "Trauma da Grande Guerra", "exemplo": "Sequelas de choque de trincheira e pânico de explosões."},
        {"nome": "Lei Seca", "exemplo": "Vício secreto em bebidas ilegais ou dívidas com mafiosos."},
        {"nome": "Inimigo", "exemplo": "Perseguido por um culto implacável do Mythos."},
        {"nome": "Segredo de Família", "exemplo": "Ancestrais ligados a rituais arcanos ou sangue maculado."},
        {"nome": "Obsessão", "exemplo": "Compelido a desvendar qualquer enigma proibido."},
        {"nome": "Honra", "exemplo": "Código profissional ético rígido que nunca transgride."},
        {"nome": "Ceticismo Fanático", "exemplo": "Recusa veemente em aceitar o inexplicável até ser tarde demais."}
    ]
}

gravar("complications.json", complications_data)


# ---------------------------------------------------------------- names.json

names = {
    "humano": {
        "nomes": [
            "Harvey", "Edward", "Thomas", "Francis", "Walter", "Arthur", "Charles", "William",
            "Henry", "George", "Albert", "Richard", "Robert", "Joseph", "Samuel", "Evelyn",
            "Eleanor", "Dorothy", "Beatrice", "Clara", "Margaret", "Ruth", "Florence", "Alice",
            "Grace", "Helen", "Lillian", "Marion", "Virginia", "Mildred"
        ],
        "sobrenomes": [
            "Walters", "Armitage", "Pickman", "Marsh", "West", "Dexter", "Gilman", "Gardner",
            "Danforth", "Blackwood", "Peabody", "Derby", "Carter", "Whateley", "Atwood", "Phillips",
            "O'Malley", "Sullivan", "Rossi", "Moretti", "Müller", "Schneider", "Goldberg", "Vance"
        ],
        "apelidos": [
            "Professor", "Doutor", "Gato", "Sombra", "Olho de Águia", "Raposa", "Doc", "Capitão"
        ]
    }
}

gravar("names.json", names)


# ---------------------------------------------------------------- archetypes.json (NPCs)

archetypes = [
    {
        "id": "cultista",
        "nome": "Cultista do Mythos",
        "nomes": "humano",
        "capanga": True,
        "np_maximo": 4,
        "descricao": "Fanático corrompido pelas promessas de entidades cósmicas. Usa túnica cerimonial e ataca com fúria cega.",
        "faixas": [
            {
                "np": 2,
                "nome": "Iniciado do Culto",
                "fonte": "Chamado de Cthulhu / M&M",
                "status_dados": "validado",
                "observacao": "Fanático de apoio armado de adaga ritual.",
                "ficha": {
                    "habilidades": {"For": 1, "Vig": 1, "Agi": 1, "Des": 0, "Lut": 1, "Int": 0, "Pro": 0, "Pre": 0},
                    "defesas_compradas": {"Esquiva": 1, "Fortitude": 1, "Vontade": 1},
                    "pericias": {"Combate Corpo-a-Corpo: Facas": 1, "Furtividade": 2, "Enganação": 2},
                    "vantagens": {"Destemido": 1, "Equipamento": 1},
                    "equipamento": ["faca_bowie"]
                }
            }
        ]
    },
    {
        "id": "policial_ronda",
        "nome": "Policial de Ronda",
        "nomes": "humano",
        "capanga": True,
        "np_maximo": 5,
        "descricao": "Guarda fardado de patrulha urbana na cidade dos anos 20.",
        "faixas": [
            {
                "np": 3,
                "nome": "Guarda de Rua",
                "fonte": "Chamado de Cthulhu / M&M",
                "status_dados": "validado",
                "observacao": "Equipado com cassetete e revólver regulamentar.",
                "ficha": {
                    "habilidades": {"For": 1, "Vig": 1, "Agi": 1, "Des": 1, "Lut": 1, "Int": 0, "Pro": 1, "Pre": 0},
                    "defesas_compradas": {"Esquiva": 1, "Aparar": 1, "Fortitude": 1, "Vontade": 1},
                    "pericias": {"Combate à Distância: Pistolas": 2, "Percepção": 2, "Intimidação": 2},
                    "vantagens": {"Iniciativa Aprimorada": 1, "Equipamento": 2},
                    "equipamento": ["revolver_38", "cassetete"]
                }
            }
        ]
    }
]

gravar("archetypes.json", archetypes)


# ---------------------------------------------------------------- modules.json (para NPCs)

modules = [
    {
        "id": "fanatico_com_punhal",
        "nome": "Fanático com Punhal",
        "epiteto": "o Fanático",
        "descricao": "Ataca em transe religioso sem hesitar diante do perigo.",
        "tatica": "Avança diretamente contra o alvo mais próximo com a faca em punho.",
        "tags": ["combate", "corpo-a-corpo"],
        "estilos": ["combate", "tematico"],
        "arquetipos": ["cultista"],
        "status_dados": "validado",
        "papel": "ambos",
        "adiciona": {
            "pericias": {"Intimidação": 2},
            "vantagens": {"Ataque Poderoso": 1}
        }
    },
    {
        "id": "cultista_ocultista",
        "nome": "Iniciado no Oculto",
        "epiteto": "o Conjurador",
        "descricao": "Conhece símbolos blasfemos e passagens secretas do templo.",
        "tatica": "Usa fumaça e dissimulação para escapar ou preparar emboscadas.",
        "tags": ["utilidade", "ocultismo"],
        "estilos": ["utilidade", "tematico"],
        "arquetipos": ["cultista"],
        "status_dados": "validado",
        "papel": "ambos",
        "adiciona": {
            "pericias": {"Especialidade: Ocultismo": 2, "Enganação": 2}
        }
    },
    {
        "id": "tira_veterano",
        "nome": "Tira Veterano",
        "epiteto": "o Veterano",
        "descricao": "Endurecido por anos de ronda noturna nos becos da metrópole.",
        "tatica": "Busca cobertura e mantém os olhos bem abertos para emboscadas.",
        "tags": ["combate", "defesa"],
        "estilos": ["combate", "tematico"],
        "arquetipos": ["policial_ronda"],
        "status_dados": "validado",
        "papel": "ambos",
        "adiciona": {
            "pericias": {"Investigação": 2},
            "vantagens": {"Rolamento Defensivo": 1}
        }
    },
    {
        "id": "guarda_escopeta",
        "nome": "Guarda com Escopeta",
        "epiteto": "o Guarda de Choque",
        "descricao": "Armado com escopeta de repetição pesada para conter distúrbios graves.",
        "tatica": "Dispara tiros espalhados para dispersar turbas e cultistas fanáticos.",
        "tags": ["combate", "distancia"],
        "estilos": ["combate", "tematico"],
        "arquetipos": ["policial_ronda"],
        "status_dados": "validado",
        "papel": "ambos",
        "substitui": {
            "equipamento": {"revolver_38": "escopeta_12"}
        },
        "adiciona": {
            "pericias": {"Atletismo": 2},
            "vantagens": {"Equipamento": 1}
        }
    }
]

gravar("modules.json", modules)


# ---------------------------------------------------------------- player.json (Ocupações dos Investigadores)

def arq_investigador(id_arq, nome, conceito, vantagens_ess, vantagens_opc, prioridades, focos, armas, itens):
    return {
        "id": id_arq,
        "nome": nome,
        "conceito": conceito,
        "vantagens_essenciais": vantagens_ess,
        "vantagens_opcionais": vantagens_opc,
        "prioridades": prioridades,
        "sugestoes": {
            "motivacoes": ["Justiça", "Conhecimento", "Curiosidade Macabra", "Proteção de Inocentes", "Dever Profissional"],
            "complicacoes": [
                {"nome": "Fobia", "detalhe": "Pavor paralisante de escuridão ou espaços fechados."},
                {"nome": "Mania", "detalhe": "Registrar obsessivamente tudo o que vê em anotações cifradas."},
                {"nome": "Paranoia", "detalhe": "Desconfia que figuras nas sombras o estão seguindo."},
                {"nome": "Obsessão", "detalhe": "Não consegue abandonar um enigma ou manuscrito proibido."}
            ]
        },
        "focos": focos,
        "armas": armas,
        "itens": itens
    }


def foco_item(id_foco, nome, desc, prioridades_extras=None, vantagens_extras=None, armas_extras=None, itens_extras=None):
    return {
        "id": id_foco,
        "nome": nome,
        "descricao": desc,
        "vantagens": vantagens_extras or [],
        "prioridades": prioridades_extras or [],
        "armas": armas_extras or [],
        "itens": itens_extras or []
    }


arquetipos_jogador = [
    # 1. Professor
    arq_investigador(
        "professor", "Professor Universitário",
        "Erudito e pesquisador acadêmico da Universidade Miskatonic, acostumado a arquivos, línguas mortas e bibliotecas empoeiradas.",
        ["Bem Informado", "Memória Eidética"],
        ["Contatos", "Idiomas", "Fascinar"],
        ["habilidade:Int", "pericia:Investigação", "pericia:Especialidade: História", "defesa:Vontade", "habilidade:Pro", "pericia:Percepção", "habilidade:Vig", "defesa:Esquiva"],
        [
            foco_item("historiador", "Historiador", "Pesquisa manuscritos e genealogias antigas.", ["pericia:Especialidade: História"]),
            foco_item("arqueologo", "Arqueólogo", "Explorador de ruínas e tumbas antigas.", ["pericia:Especialidade: Arqueologia", "pericia:Atletismo"], itens_extras=["lanterna_eletrica"]),
            foco_item("antropologo", "Antropólogo", "Estudioso de costumes tribais e cultos folclóricos.", ["pericia:Especialidade: Antropologia"]),
            foco_item("linguista", "Linguista", "Tradutor de inscrições rúnicas e hieróglifos arcanos.", ["pericia:Especialidade: Línguas Antigas"], vantagens_extras=["Idiomas"])
        ],
        {"principais": ["revolver_38", "pistola_bolso_32"], "secundarias": ["cassetete", "faca_bowie"]},
        {"essenciais": ["caderno_caneta", "relogio_bolso"], "opcionais": ["lupa", "lanterna_eletrica", "mochila_couro"]}
    ),

    # 2. Detetive Particular
    arq_investigador(
        "detetive", "Detetive Particular",
        "Investigador contratado para solucionar desaparecimentos bizarros, homicídios insolúveis e casos que a polícia arquivou.",
        ["Contatos", "Iniciativa Aprimorada"],
        ["Saque Rápido", "Tolerância Maior", "Duro de Matar"],
        ["habilidade:Des", "pericia:Investigação", "pericia:Combate à Distância: Pistolas", "defesa:Esquiva", "habilidade:Int", "pericia:Percepção", "habilidade:Vig", "defesa:Vontade"],
        [
            foco_item("ex_policial", "Ex-Policial", "Endurecido pelas ruas, intimidador e rápido no gatilho.", ["pericia:Intimidação"], vantagens_extras=["Iniciativa Aprimorada"]),
            foco_item("pinkerton", "Agente Pinkerton", "Perito em rastreio, campanas e infiltração discreta.", ["pericia:Furtividade"], itens_extras=["binoculos"])
        ],
        {"principais": ["revolver_38", "pistola_colt_45"], "secundarias": ["soqueira", "cassetete"]},
        {"essenciais": ["gazuas", "lanterna_eletrica", "caderno_caneta"], "opcionais": ["sobretudo_pesado", "camera_fotografica"]}
    ),

    # 3. Médico
    arq_investigador(
        "medico", "Médico",
        "Profissional da medicina confrontado por ferimentos inexplicáveis, patologias cósmicas e a fragilidade do corpo humano.",
        ["Maestria em Perícia"],
        ["Tolerância Maior", "Contatos", "Destemido"],
        ["habilidade:Int", "pericia:Tratamento", "pericia:Especialidade: Medicina", "defesa:Vontade", "habilidade:Pro", "pericia:Intuição", "habilidade:Vig", "defesa:Esquiva"],
        [
            foco_item("clinico", "Clínico Geral", "Especialista em diagnósticos rápidos e primeiros socorros.", ["pericia:Tratamento"]),
            foco_item("cirurgiao", "Cirurgião", "Mão firme e precisão cirúrgica sob extrema pressão.", ["pericia:Tratamento", "habilidade:Des"]),
            foco_item("legista", "Médico Legista", "Examina autópsias e causas de mortes grotescas.", ["pericia:Investigação"]),
            foco_item("psiquiatra", "Psiquiatra", "Trata traumas e crises agudas de histeria ou terror.", ["pericia:Especialidade: Psicanálise"], vantagens_extras=["Destemido"])
        ],
        {"principais": ["pistola_bolso_32", "revolver_38"], "secundarias": ["faca_bowie"]},
        {"essenciais": ["maleta_medica", "relogio_bolso"], "opcionais": ["lanterna_eletrica", "mochila_couro"]}
    ),

    # 4. Jornalista
    arq_investigador(
        "jornalista", "Jornalista",
        "Repórter investigativo incansável atrás de manchetes sensacionalistas, sociedades secretas e conspirações urbanas.",
        ["Contatos", "Bem Relacionado"],
        ["Fascinar", "Bem Informado", "Iniciativa Aprimorada"],
        ["habilidade:Int", "pericia:Investigação", "pericia:Enganação", "pericia:Percepção", "defesa:Esquiva", "habilidade:Pre", "defesa:Vontade", "habilidade:Vig"],
        [
            foco_item("reporter_policial", "Repórter Policial", "Fontes no necrotério e informantes no submundo.", ["pericia:Intuição"]),
            foco_item("fotografo", "Fotógrafo", "Registra em filme as evidências do indescritível.", ["pericia:Especialidade: Fotografia"], itens_extras=["camera_fotografica"]),
            foco_item("colunista", "Colunista Social", "Transita em festas da elite ouvindo confidências indiscretas.", ["pericia:Persuasão"])
        ],
        {"principais": ["revolver_38", "pistola_bolso_32"], "secundarias": ["cassetete"]},
        {"essenciais": ["caderno_caneta", "relogio_bolso"], "opcionais": ["camera_fotografica", "maquina_escrever", "lanterna_eletrica"]}
    ),

    # 5. Antiquário
    arq_investigador(
        "antiquario", "Antiquário",
        "Negociante de peças raras, estatuetas macabras de basalto e relíquias de procedência duvidosa.",
        ["Avaliação", "Bem Informado"],
        ["Contatos", "Idiomas", "Atraente"],
        ["habilidade:Int", "pericia:Especialidade: Antiguidades", "pericia:Percepção", "defesa:Vontade", "habilidade:Pro", "pericia:Persuasão", "habilidade:Vig", "defesa:Esquiva"],
        [
            foco_item("colecionador", "Colecionador Ocultista", "Reconhece artefatos e grimórios do Mythos.", ["pericia:Especialidade: Ocultismo"]),
            foco_item("avaliador", "Avaliador Comercial", "Perito em discernir ouro antigo de falsificações.", ["pericia:Especialidade: Antiguidades"]),
            foco_item("cacador_reliquias", "Caçador de Relíquias", "Viaja a sítios isolados em busca de peças exóticas.", ["pericia:Atletismo"])
        ],
        {"principais": ["revolver_38", "pistola_bolso_32"], "secundarias": ["faca_bowie", "porrete"]},
        {"essenciais": ["lupa", "lanterna_eletrica"], "opcionais": ["mochila_couro", "caderno_caneta"]}
    ),

    # 6. Veterano de Guerra
    arq_investigador(
        "veterano", "Veterano de Guerra",
        "Ex-soldado da Primeira Guerra Mundial, familiarizado com bombardeios, morticínio e a fragilidade da vida.",
        ["Duro de Matar", "Tolerância Maior"],
        ["Iniciativa Aprimorada", "Ataque Poderoso", "Rolamento Defensivo"],
        ["habilidade:Vig", "pericia:Combate à Distância: Rifles", "defesa:Fortitude", "habilidade:Des", "defesa:Esquiva", "pericia:Atletismo", "defesa:Vontade", "pericia:Percepção"],
        [
            foco_item("infantaria", "Soldado de Infantaria", "Disciplinado e resistente a marchas e intempéries.", ["pericia:Atletismo"]),
            foco_item("sapador", "Sapador", "Especialista em demolições, trincheiras e explosivos.", ["pericia:Tecnologia"], armas_extras=["dinamite"]),
            foco_item("atirador_elite", "Atirador de Elite", "Calmo sob pressão, letal a centenas de metros.", ["pericia:Combate à Distância: Rifles"], vantagens_extras=["Mira Aprimorada"])
        ],
        {"principais": ["rifle_ferrolho_30_06", "escopeta_12", "pistola_colt_45"], "secundarias": ["faca_bowie", "cassetete"]},
        {"essenciais": ["botas_pesadas", "sobretudo_pesado", "cantil"], "opcionais": ["lanterna_eletrica", "binoculos"]}
    ),

    # 7. Policial
    arq_investigador(
        "policial", "Oficial de Polícia",
        "Homem da lei juramentado, habituado a interrogatórios, rondas perigosas e a conter a violência urbana.",
        ["Benefício (Autoridade Policial)", "Iniciativa Aprimorada"],
        ["Derrubar Aprimorado", "Duro de Matar", "Desarmar Aprimorado"],
        ["habilidade:Vig", "pericia:Combate à Distância: Pistolas", "pericia:Percepção", "defesa:Esquiva", "habilidade:Lut", "pericia:Intimidação", "defesa:Aparar", "defesa:Fortitude"],
        [
            foco_item("patrulheiro", "Patrulheiro de Rua", "Conhece as ruas da cidade e aborda suspeitos com agilidade.", ["pericia:Atletismo"]),
            foco_item("inspetor", "Inspetor de Homicídios", "Dedicado a pistas forenses, depoimentos e interrogatórios.", ["pericia:Investigação"])
        ],
        {"principais": ["revolver_38", "escopeta_12"], "secundarias": ["cassetete"]},
        {"essenciais": ["cassetete", "lanterna_eletrica"], "opcionais": ["caderno_caneta", "relogio_bolso"]}
    ),

    # 8. Bibliotecário
    arq_investigador(
        "bibliotecario", "Bibliotecário",
        "Guardião silencioso de coleções raras, jornais microfilmados e livros cuja leitura jamais deveria ser permitida.",
        ["Memória Eidética", "Bem Informado"],
        ["Idiomas", "Fascinar", "Contatos"],
        ["habilidade:Int", "pericia:Investigação", "defesa:Vontade", "pericia:Percepção", "habilidade:Pro", "pericia:Especialidade: Línguas Antigas", "habilidade:Vig", "defesa:Esquiva"],
        [
            foco_item("arquivista", "Arquivista", "Encontra qualquer registro ou documento em minutos.", ["pericia:Investigação"]),
            foco_item("obras_raras", "Curador de Obras Raras", "Conhece os títulos proibidos do Mythos e seus riscos.", ["pericia:Especialidade: Ocultismo"])
        ],
        {"principais": ["pistola_bolso_32"], "secundarias": ["faca_bowie"]},
        {"essenciais": ["caderno_caneta", "lupa"], "opcionais": ["lanterna_eletrica", "mochila_couro"]}
    ),

    # 9. Diletante
    arq_investigador(
        "diletante", "Diletante",
        "Herdeiro afortunado com muito dinheiro e curiosidade mórbida por clubes secretos e expedições exóticas.",
        ["Benefício (Riqueza)", "Contatos"],
        ["Atraente", "Bem Relacionado", "Fascinar"],
        ["habilidade:Pre", "pericia:Persuasão", "defesa:Esquiva", "habilidade:Int", "pericia:Veículos", "pericia:Percepção", "habilidade:Agi", "defesa:Vontade"],
        [
            foco_item("herdeiro", "Alta Sociedade", "Influência nas altas rodas políticas e financeiras.", ["pericia:Persuasão"]),
            foco_item("aventureiro", "Aventureiro Esportivo", "Pilota carros de corrida e financia safáris misteriosos.", ["pericia:Veículos", "pericia:Atletismo"])
        ],
        {"principais": ["revolver_38", "pistola_colt_45", "escopeta_12"], "secundarias": ["faca_bowie"]},
        {"essenciais": ["terno_tres_pecas", "relogio_bolso", "isqueiro_cigarros"], "opcionais": ["camera_fotografica", "binoculos"]}
    ),

    # 10. Membro do Clero
    arq_investigador(
        "clero", "Membro do Clero",
        "Sacerdote ou pastor confrontado com horrores cósmicos que desafiam todas as escrituras sagradas da humanidade.",
        ["Inspirar", "Destemido"],
        ["Bem Informado", "Idiomas", "Liderança"],
        ["habilidade:Pro", "defesa:Vontade", "pericia:Especialidade: Teologia", "pericia:Persuasão", "habilidade:Int", "pericia:Intuição", "habilidade:Vig", "defesa:Fortitude"],
        [
            foco_item("padre", "Padre Erudito", "Instruído em latim e no combate ao oculto e herético.", ["pericia:Especialidade: Teologia", "pericia:Especialidade: Ocultismo"]),
            foco_item("pastor", "Pregador de Comunidade", "Voz poderosa que ampara fiéis atormentados pelo medo.", ["pericia:Persuasão"])
        ],
        {"principais": ["pistola_bolso_32", "revolver_38"], "secundarias": ["cassetete"]},
        {"essenciais": ["caderno_caneta", "relogio_bolso"], "opcionais": ["lanterna_eletrica", "mochila_couro"]}
    ),

    # 11. Escritor
    arq_investigador(
        "escritor", "Escritor",
        "Autor de contos macabros e histórias policiais para revistas pulp, cujos pesadelos começam a se manifestar na vigília.",
        ["Fascinar", "Memória Eidética"],
        ["Contatos", "Bem Informado", "Idiomas"],
        ["habilidade:Int", "pericia:Especialidade: Literatura", "defesa:Vontade", "pericia:Percepção", "habilidade:Pro", "pericia:Intuição", "habilidade:Vig", "defesa:Esquiva"],
        [
            foco_item("romancista", "Romancista Policial", "Trama teorias dedutivas afiadas.", ["pericia:Investigação"]),
            foco_item("poeta_gotico", "Poeta Gótico", "Fascinado pelo grotesco, cemitérios e lendas esquecidas.", ["pericia:Especialidade: Ocultismo"])
        ],
        {"principais": ["pistola_bolso_32", "revolver_38"], "secundarias": ["faca_bowie"]},
        {"essenciais": ["maquina_escrever", "caderno_caneta"], "opcionais": ["relogio_bolso", "isqueiro_cigarros"]}
    ),

    # 12. Parapsicólogo
    arq_investigador(
        "parapsicologo", "Parapsicólogo",
        "Pesquisador acadêmico ou independente devotado ao registro científico de aparições, telepatia e sessões espíritas.",
        ["Bem Informado", "Artífice"],
        ["Destemido", "Contatos", "Transe"],
        ["habilidade:Int", "pericia:Especialidade: Ocultismo", "pericia:Investigação", "defesa:Vontade", "pericia:Percepção", "habilidade:Pro", "defesa:Esquiva", "habilidade:Vig"],
        [
            foco_item("pesquisador_psiquico", "Pesquisador Psíquico", "Registra evidências com gravações e instrumentos de precisão.", ["pericia:Especialidade: Ocultismo"], itens_extras=["gravador_fonografo"]),
            foco_item("desmistificador", "Desmistificador de Médiuns", "Revela truques de charlatães e mecanismos secretos.", ["pericia:Enganação", "pericia:Tecnologia"])
        ],
        {"principais": ["revolver_38", "pistola_bolso_32"], "secundarias": ["faca_bowie"]},
        {"essenciais": ["camera_fotografica", "lanterna_eletrica"], "opcionais": ["lupa", "caderno_caneta"]}
    ),

    # 13. Enfermeira
    arq_investigador(
        "enfermeira", "Enfermeira",
        "Profissional obstinada de hospitais e ambulatórios, acostumada a tratar infecções bizarras e delírios febris.",
        ["Tolerância Maior", "Duro de Matar"],
        ["Trabalho em Equipe", "Contatos", "Inspirar"],
        ["habilidade:Pro", "pericia:Tratamento", "pericia:Intuição", "defesa:Vontade", "pericia:Percepção", "habilidade:Vig", "defesa:Fortitude", "defesa:Esquiva"],
        [
            foco_item("hospitalar", "Enfermeira de Hospital", "Administra medicamentos, sedativos e cuidados intensivos.", ["pericia:Tratamento"]),
            foco_item("veterana_guerra", "Enfermeira da Grande Guerra", "Resiliente sob fogo cruzado e acostumada ao caos.", ["pericia:Atletismo", "defesa:Fortitude"])
        ],
        {"principais": ["pistola_bolso_32"], "secundarias": ["faca_bowie"]},
        {"essenciais": ["maleta_medica", "lanterna_eletrica"], "opcionais": ["relogio_bolso", "cantil"]}
    ),

    # 14. Advogado
    arq_investigador(
        "advogado", "Advogado",
        "Causídico eloquente e perspicaz, acostumado a disputas jurídicas, testamentos de famílias abastadas e contratos arcanos.",
        ["Bem Relacionado", "Contatos"],
        ["Fascinar", "Bem Informado", "Zombar"],
        ["habilidade:Int", "pericia:Especialidade: Direito", "pericia:Persuasão", "defesa:Vontade", "habilidade:Pre", "pericia:Intuição", "defesa:Esquiva", "habilidade:Vig"],
        [
            foco_item("criminalista", "Criminalista", "Defende clientes acusados de crimes bizarros.", ["pericia:Intimidação"]),
            foco_item("civil", "Direito Civil e Sucessões", "Desvenda testamentos, propriedades confiscadas e cláusulas ocultas.", ["pericia:Investigação"])
        ],
        {"principais": ["pistola_bolso_32", "revolver_38"], "secundarias": ["cassetete"]},
        {"essenciais": ["mochila_couro", "caderno_caneta"], "opcionais": ["terno_tres_pecas", "relogio_bolso"]}
    ),

    # 15. Criminoso
    arq_investigador(
        "criminoso", "Criminoso",
        "Operador do submundo da Lei Seca, perito em burlar a vigilância policial, arrombar trancas e transportar cargas ilícitas.",
        ["Contatos", "Esconder-se à Plena Vista"],
        ["Saque Rápido", "Iniciativa Aprimorada", "Duro de Matar"],
        ["habilidade:Agi", "pericia:Furtividade", "pericia:Combate à Distância: Pistolas", "defesa:Esquiva", "pericia:Prestidigitação", "pericia:Enganação", "habilidade:Des", "habilidade:Vig"],
        [
            foco_item("contrabandista", "Contrabandista da Lei Seca", "Pilota caminhões velozes e foge de patrulhas.", ["pericia:Veículos"]),
            foco_item("arrombador", "Ladrão de Cofres", "Abre cofres e fechaduras no escuro.", ["pericia:Tecnologia"], armas_extras=["dinamite"])
        ],
        {"principais": ["revolver_38", "pistola_colt_45", "submetralhadora_thompson"], "secundarias": ["soqueira", "faca_bowie"]},
        {"essenciais": ["gazuas", "lanterna_eletrica"], "opcionais": ["pe_de_cabra", "mochila_couro"]}
    )
]

riquezas_cthulhu = [
    {
        "id": "pobretao",
        "nome": "Pobretão (Crédito 0)",
        "riqueza": 4,
        "dinheiro": 20,
        "beneficio": 0,
        "ajuste_de_pontos": 1,
        "descricao": "Desempregado ou sem teto. Devolve 1 PP no orçamento de criação."
    },
    {
        "id": "pobre",
        "nome": "Pobre (Crédito 1–9)",
        "riqueza": 6,
        "dinheiro": 75,
        "beneficio": 0,
        "ajuste_de_pontos": 0,
        "descricao": "Estudante ou trabalhador braçal com orçamento apertado."
    },
    {
        "id": "classe_media",
        "nome": "Classe média (Crédito 10–49)",
        "riqueza": 8,
        "dinheiro": 250,
        "beneficio": 0,
        "ajuste_de_pontos": 0,
        "descricao": "Padrão: professor, jornalista, detetive ou médico de bairro."
    },
    {
        "id": "abastado",
        "nome": "Abastado (Crédito 50–89)",
        "riqueza": 12,
        "dinheiro": 1000,
        "beneficio": 1,
        "ajuste_de_pontos": 0,
        "descricao": "Médico renomado, advogado sócio ou empresário próspero (1 PP)."
    },
    {
        "id": "rico",
        "nome": "Rico (Crédito 90–98)",
        "riqueza": 24,
        "dinheiro": 10000,
        "beneficio": 4,
        "ajuste_de_pontos": 0,
        "descricao": "Diletante herdeiro ou banqueiro estabelecido (4 PP)."
    },
    {
        "id": "ricaco",
        "nome": "Ricaço (Crédito 99)",
        "riqueza": 32,
        "dinheiro": 50000,
        "beneficio": 6,
        "ajuste_de_pontos": 0,
        "descricao": "Magnata industrial ou financista multimilionário (6 PP)."
    }
]

player_data = {
    "_fonte": "Ocupações do Livro do Jogador de Chamado de Cthulhu 7ª edição, adaptadas como arquétipos de Mutantes & Malfeitores 3ª edição.",
    "riqueza": riquezas_cthulhu,
    "arquetipos": arquetipos_jogador,
    "_equipamento": "Armas e itens de 1920 sorteados pelo orçamento inicial em dólares."
}

gravar("player.json", player_data)

print("Todos os arquivos básicos de Chamado de Cthulhu foram gerados com sucesso!")
