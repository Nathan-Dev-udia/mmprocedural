"""Preços do Cyberpunk RED (livro básico traduzido, em referencias/cyber) para o gênero cyberpunk.

- Põe `preco` (eurobucks), `categoria_de_preco` e `fonte_preco` em cada item de equipment.json e
  cada implante de powers.json. Itens sem equivalente no RED recebem o preço típico da categoria e
  `preco_estimado: true`.
- Acrescenta itens dos kits iniciais dos Papéis do RED (munição, granadas, ferramentas...).
- Os valores em PP/pontos de equipamento (regras de M&M) não mudam.

Rode de novo sempre que mexer nos preços: python ferramentas/precos_cyberpunk_red.py
"""

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "dados" / "generos" / "cyberpunk"

# Categorias de preço do RED ("Compra e Venda", p. 385).
CATEGORIAS = {10: "Barato", 20: "Quotidiano", 50: "Oneroso", 100: "Premium", 500: "Caro",
              1000: "Muito Caro", 5000: "Luxuoso", 10000: "Super Luxuoso"}

ARMAS = "Cyberpunk RED, tabelas de armas (p. 92–95)"
ARMADURAS = "Cyberpunk RED, tabela de armaduras (p. 97)"
EQUIPAMENTOS = "Cyberpunk RED, tabela de equipamentos (p. 100–101)"
MUNICAO = "Cyberpunk RED, munição (p. 94 e 345–347)"
CYBERWARE = "Cyberpunk RED, cyberware (p. 111–116)"

# id: (preço, fonte, nome novo ou None). fonte None = estimado pela categoria.
PRECOS_DE_ITENS = {
    "pistola_apoio": (50, ARMAS + ": Pistola Média", "Pistola média"),
    "pistola_leve": (100, ARMAS + ": Pistola Pesada", "Pistola pesada"),
    "pistola_pesada": (100, ARMAS + ": Pistola Muito Pesada", "Pistola muito pesada"),
    # A submetralhadora do livro básico (Dano 4) corresponde à SMG pesada do RED; a SMG comum é o item "smg".
    "submetralhadora": (100, ARMAS + ": SMG Pesada", "SMG pesada"),
    "fuzil_assalto": (500, ARMAS + ": Rifle de Assalto", None),
    "fuzil_precisao": (500, ARMAS + ": Rifle Sniper", None),
    "escopeta": (500, ARMAS + ": Espingarda", None),
    "pistola_energia": (1000, None, None),
    "fuzil_energia": (5000, None, None),
    "pistola_taser": (100, ARMAS + ": Pistola Atordoante (exótica)", None),
    "metralhadora": (1000, None, None),
    "lanca_granadas": (500, ARMAS + ": Lança-Granadas", None),
    "granada_fragmentacao": (100, MUNICAO + ": granada anti-blindagem", None),
    "granada_atordoante": (100, MUNICAO + ": granada flashbang", None),
    "explosivo_plastico": (500, None, None),
    "faca": (50, ARMAS + ": Arma Branca Leve", None),
    "laminas_retrateis": (500, CYBERWARE + ": Estripadores/Wolvers", None),
    "katana": (100, ARMAS + ": Arma Branca Pesada", None),
    "tonfa": (50, ARMAS + ": Arma Branca Média", None),
    "soqueira": (50, ARMAS + ": Arma Branca Leve", None),
    "bastao_choque": (100, ARMAS + ": Bastão Atordoante (exótica)", None),
    # Armaduras vestidas: no RED, corpo e cabeça são compradas separadas (p. 96); o preço é das duas peças,
    # como no kit dos Papéis (corpo + cabeça em blindagem leve).
    "jaqueta_couro": (40, ARMADURAS + ": Couro (SP4), corpo e cabeça (20eb cada)", None),
    "colete_oculto": (100, ARMADURAS + ": Kevlar® (SP7), corpo e cabeça (50eb cada)", "Roupa de Kevlar"),
    "colete_balistico": (200, ARMADURAS + ": Blindagem Leve (SP11), corpo e cabeça (100eb cada)",
                         "Blindagem leve (corpo e cabeça)"),
    # A armadura do Soldado do livro básico (Proteção 3) não tem equivalente no RED: fica entre o Kevlar
    # (Proteção 2) e a blindagem leve (Proteção 4). A flak do RED virou o item armadura_flak.
    "armadura_tatica": (200, None, "Armadura militar"),
    "celular": (50, EQUIPAMENTOS + ": Celular Descartável", "Celular descartável"),
    "smartphone": (100, EQUIPAMENTOS + ": Agente", "Agente (smartphone com IA)"),
    "comunicador": (100, EQUIPAMENTOS + ": Rádio Comunicador", "Rádio comunicador"),
    "computador": (500, EQUIPAMENTOS + ": Cyberdeck", "Cyberdeck"),
    "gravador": (100, EQUIPAMENTOS + ": Gravador de Áudio", None),
    "camera": (100, EQUIPAMENTOS + ": Câmera de Vídeo", "Câmera de vídeo"),
    "binoculos": (50, EQUIPAMENTOS + ": Binóculos", None),
    "oculos_visao_noturna": (1000, EQUIPAMENTOS + ": Óculos Inteligentes (500eb) + opção de cyberolho "
                             "Luz Baixa/Infravermelho/UV (500eb)", None),
    "microfone_parabolico": (500, None, None),
    "rastreador": (500, EQUIPAMENTOS + ": Localizador", "Localizador"),
    "gazua_automatica": (20, EQUIPAMENTOS + ": Ferramenta de Arrombamento", "Ferramenta de arrombamento"),
    "algemas": (50, EQUIPAMENTOS + ": Algemas", None),
    "mascara_gas": (20, EQUIPAMENTOS + ": Máscara de Gás", None),
    "multiferramenta": (100, EQUIPAMENTOS + ": Techtool", "Techtool (multiferramenta)"),
    "kit_medico": (100, EQUIPAMENTOS + ": Bolsa Medtech", "Bolsa Medtech"),
    "lanterna": (20, EQUIPAMENTOS + ": Lanterna", None),
    "gps": (50, None, None),
}

# Itens novos: kits iniciais dos Papéis do RED (p. 98 e 103). Custo em pontos de equipamento de M&M.
ITENS_NOVOS = [
    {"id": "smg", "nome": "SMG", "categoria": "Arma de fogo", "custo": 9,
     "ataque": {"tipo": "distancia", "efeito": 3, "critico": 20, "pericia": "Combate à Distância: Submetralhadoras",
                "multiataque": True},
     "notas": "Multiataque", "municao": "municao_pistola", "preco": 100, "fonte_preco": ARMAS + ": SMG",
     "fonte": "Dano 3 à distância com Multiataque (submetralhadora do livro básico, cap. 7, um grau abaixo)"},
    {"id": "armadura_flak", "nome": "Armadura flak (corpo e cabeça)", "categoria": "Armadura", "custo": 3,
     "protecao": 5, "limitada_a": "balísticos",
     "descricao": "Proteção 5 contra ataques balísticos. Pesada: no RED dá –4 em REF, DEX e MOVE "
                  "(regra opcional no guia do mestre, seção 5.8).",
     "preco": 1000, "fonte_preco": ARMADURAS + ": Flak (SP15), corpo e cabeça (500eb cada)",
     "fonte": "Proteção Limitada a balísticos: 5 graduações a meio ponto = 3 pontos"},
    {"id": "moto_do_cla", "nome": "Moto estradeira do clã (emprestada)", "categoria": "Veículo", "custo": 10,
     "descricao": "Motocicleta: tamanho Médio, Força 1, Velocidade 6, Defesa 10, Resistência 8. "
                  "Emprestada pela família; não é do personagem.",
     "preco": 0, "categoria_de_preco": "Emprestado",
     "fonte_preco": "Cyberpunk RED, Habilidade de Papel Moto do Nômade (p. 165): a família empresta o veículo. "
                    "Comprada, uma moto estradeira custa 20.000eb (p. 190)",
     "fonte": "Livro básico, cap. 7 (veículos: motocicleta, 10 pontos)"},
    {"id": "arco", "nome": "Arco ou besta", "categoria": "Arma de disparo", "custo": 6,
     "ataque": {"tipo": "distancia", "efeito": 3, "critico": 20, "pericia": "Combate à Distância: Arcos"},
     "preco": 100, "fonte_preco": ARMAS + ": Arco & Besta", "fonte": "Livro básico, cap. 7 (arco)"},
    {"id": "traje_corporal", "nome": "Traje corporal (bodyweight)", "categoria": "Armadura", "custo": 3, "protecao": 3,
     "notas": "Discreto; guarda o cyberdeck", "preco": 1000, "fonte_preco": ARMADURAS + ": Traje Corporal (SP11)",
     "fonte": "Proteção 3 contra qualquer ataque (sem limitação)"},
    {"id": "escudo_balistico", "nome": "Escudo balístico", "categoria": "Armadura", "custo": 2,
     "notas": "+2 em Esquiva e Aparar enquanto empunhado (bônus de cobertura; não entra no cálculo da ficha)",
     "preco": 100, "fonte_preco": ARMADURAS + ": Escudo Balístico",
     "fonte": "Livro básico, cap. 7 (escudo médio: +2 em Esquiva e Aparar)"},
    {"id": "municao_pistola", "nome": "Munição de pistola/SMG (50 tiros)", "categoria": "Munição", "custo": 0,
     "preco": 50, "fonte_preco": MUNICAO + ": munição básica, 10eb por 10"},
    {"id": "municao_rifle", "nome": "Munição de rifle (50 tiros)", "categoria": "Munição", "custo": 0,
     "preco": 50, "fonte_preco": MUNICAO + ": munição básica, 10eb por 10"},
    {"id": "municao_espingarda", "nome": "Cartuchos de espingarda (50)", "categoria": "Munição", "custo": 0,
     "preco": 50, "fonte_preco": MUNICAO + ": munição básica, 10eb por 10"},
    {"id": "granada_fumaca", "nome": "Granada de fumaça", "categoria": "Explosivo", "custo": 1,
     "notas": "Nuvem de fumaça de 10 m: camuflagem visual na área", "preco": 50, "fonte_preco": MUNICAO + ": fumaça"},
    {"id": "granada_gas", "nome": "Granada de gás lacrimogêneo", "categoria": "Explosivo", "custo": 1,
     "notas": "Quem respira sem proteção fica tonto (combine o efeito com o mestre)", "preco": 50,
     "fonte_preco": MUNICAO + ": gás lacrimogêneo"},
    {"id": "granada_emp", "nome": "Granada EMP", "categoria": "Explosivo", "custo": 1,
     "notas": "Desliga eletrônicos e implantes por 1 minuto (combine com o mestre)", "preco": 500,
     "fonte_preco": MUNICAO + ": EMP"},
    {"id": "computador_portatil", "nome": "Computador portátil", "categoria": "Eletrônicos", "custo": 1,
     "descricao": "+2 em Investigação para pesquisas.", "preco": 50, "fonte_preco": EQUIPAMENTOS + ": Computador"},
    {"id": "oculos_virtuais", "nome": "Óculos virtuais", "categoria": "Eletrônicos", "custo": 1,
     "descricao": "Mostra o ciberespaço sobre o mundo real.", "preco": 100, "fonte_preco": EQUIPAMENTOS + ": Óculos Virtuais"},
    {"id": "codificador", "nome": "Codificador/decodificador", "categoria": "Eletrônicos", "custo": 1,
     "descricao": "Protege as comunicações.", "preco": 500, "fonte_preco": EQUIPAMENTOS + ": Codificador/Decodificador"},
    {"id": "detector_escutas", "nome": "Detector de escutas", "categoria": "Vigilância", "custo": 1,
     "descricao": "+5 para achar grampos e escutas.", "preco": 500, "fonte_preco": EQUIPAMENTOS + ": Detector de Escutas"},
    {"id": "radio_scanner", "nome": "Rádio scanner / tocador de música", "categoria": "Eletrônicos", "custo": 1,
     "preco": 50, "fonte_preco": EQUIPAMENTOS + ": Radio Scanner/Music Player"},
    {"id": "techscanner", "nome": "Techscanner", "categoria": "Equipamento geral", "custo": 1,
     "descricao": "+2 em Tecnologia para diagnosticar defeitos.", "preco": 1000, "fonte_preco": EQUIPAMENTOS + ": Techscanner"},
    {"id": "bolsa_tech", "nome": "Bolsa Tech", "categoria": "Equipamento geral", "custo": 1,
     "descricao": "Ferramentas para consertar coisas (evita a penalidade de trabalhar sem ferramentas).",
     "preco": 500, "fonte_preco": EQUIPAMENTOS + ": Bolsa Tech"},
    {"id": "scanner_medico", "nome": "Escâner médico", "categoria": "Equipamento geral", "custo": 1,
     "descricao": "+2 em Tratamento para diagnóstico.", "preco": 1000, "fonte_preco": EQUIPAMENTOS + ": Escâner Médico"},
    {"id": "airhypo", "nome": "Airhypo", "categoria": "Equipamento geral", "custo": 1,
     "descricao": "Injeção sem agulha: aplica remédio ou droga com um toque.", "preco": 50, "fonte_preco": EQUIPAMENTOS + ": Airhypo"},
    {"id": "arma_gancho", "nome": "Arma de gancho", "categoria": "Equipamento geral", "custo": 1,
     "descricao": "Dispara um gancho com 30 m de cabo.", "preco": 100, "fonte_preco": EQUIPAMENTOS + ": Arma de Gancho"},
    {"id": "corda", "nome": "Corda (60 m)", "categoria": "Equipamento geral", "custo": 1, "preco": 20,
     "fonte_preco": EQUIPAMENTOS + ": Corda"},
    {"id": "fita_adesiva", "nome": "Fita adesiva", "categoria": "Equipamento geral", "custo": 0, "preco": 20,
     "fonte_preco": EQUIPAMENTOS + ": Fita Adesiva"},
    {"id": "sinalizador", "nome": "Sinalizadores (6)", "categoria": "Equipamento geral", "custo": 0, "preco": 60,
     "fonte_preco": EQUIPAMENTOS + ": Sinalizador (10eb cada)"},
    {"id": "equipamento_camping", "nome": "Barraca e equipamento de camping", "categoria": "Equipamento geral",
     "custo": 1, "preco": 50, "fonte_preco": EQUIPAMENTOS + ": Tenda e Equipamentos de Camping"},
    {"id": "cama_inflavel", "nome": "Cama inflável e saco de dormir", "categoria": "Equipamento geral", "custo": 0,
     "preco": 20, "fonte_preco": EQUIPAMENTOS + ": Cama Inflável & Saco de Dormir"},
    {"id": "guitarra", "nome": "Guitarra elétrica (ou outro instrumento)", "categoria": "Equipamento geral", "custo": 1,
     "descricao": "Instrumento de qualidade: +2 em Especialidade: Música.", "preco": 500,
     "fonte_preco": EQUIPAMENTOS + ": Guitarra Elétrica/Outro Instrumento"},
    {"id": "amplificador", "nome": "Amplificador de bolso", "categoria": "Equipamento geral", "custo": 0, "preco": 50,
     "fonte_preco": EQUIPAMENTOS + ": Amplificador de Bolso"},
]

ITENS_REMOVIDOS = {"smg_pesada"}

# Munição de cada arma de fogo.
MUNICAO_DAS_ARMAS = {
    "pistola_apoio": "municao_pistola", "pistola_leve": "municao_pistola", "pistola_pesada": "municao_pistola",
    "submetralhadora": "municao_pistola", "fuzil_assalto": "municao_rifle", "fuzil_precisao": "municao_rifle",
    "metralhadora": "municao_rifle", "escopeta": "municao_espingarda", "smg": "municao_pistola",
}

# Implantes: preço do cyberware equivalente no RED (instalação inclusa, p. 110).
PRECOS_DE_IMPLANTES = {
    "blindagem_subdermica": (500, CYBERWARE + ": Malha Subdérmica"),
    "placas_dermicas": (1000, CYBERWARE + ": Armadura Subdérmica"),
    "braco_cibernetico": (500, CYBERWARE + ": Cyberbraço"),
    "olhos_ciberneticos": (1200, CYBERWARE + ": 2 Cyberolhos (100eb cada) + Luz Baixa/Infravermelho/UV (500eb por olho)"),
    "audicao_amplificada": (600, CYBERWARE + ": Conjunto de Cyberáudio (500eb) + Audição Amplificada (100eb)"),
    "radar_subcutaneo": (1000, CYBERWARE + ": Radar/Sonar Implantado"),
    "scanner_raio_x": (1000, None),
    "alerta_de_combate": (500, None),
    "interface_neural": (1000, CYBERWARE + ": Link Neural (500eb) + Plugs de Interface (500eb)"),
    "radio_implantado": (600, CYBERWARE + ": Conjunto de Cyberáudio (500eb) + Rádio Comunicador (100eb)"),
    "acesso_a_cameras": (1000, None),
    "reflexos_turbinados": (1000, CYBERWARE + ": Link Neural (500eb) + Sandevistan (500eb)"),
    "nanorreparo": (500, CYBERWARE + ": Anticorpos Reforçados"),
    "pernas_hidraulicas": (1200, CYBERWARE + ": 2 Cyberpernas (100eb cada) + Salto Aprimorado (500eb por perna)"),
    "firewall_cortical": (500, None),
    "filtros_sinteticos": (1200, CYBERWARE + ": Filtros Nasais (100eb) + Suprimento de Oxigênio (1.000eb) + Aglutinador de Toxina (100eb)"),
    "camuflagem_optica": (5000, None),
    "braco_canhao": (1000, CYBERWARE + ": Cyberbraço (500eb) + Arma a Distância Embutida (500eb)"),
    "metralhadora_embutida": (1000, CYBERWARE + ": Cyberbraço (500eb) + Arma a Distância Embutida (500eb)"),
    "taser_implantado": (1000, CYBERWARE + ": Cyberbraço (500eb) + Arma a Distância Embutida (500eb)"),
    "pulso_eletromagnetico": (1000, None),
}


def categoria(preco):
    menores = [v for v in CATEGORIAS if v <= preco]
    return CATEGORIAS[max(menores)] if menores else "Barato"


def precificar(item, preco, fonte, rotulo_categoria=None):
    item["preco"] = preco
    item["categoria_de_preco"] = rotulo_categoria or categoria(preco)
    if fonte:
        item["fonte_preco"] = fonte
        item.pop("preco_estimado", None)
    else:
        item["fonte_preco"] = (f"Sem equivalente no Cyberpunk RED: preço típico da categoria "
                               f"{categoria(preco)}, estimado pelo gerador")
        item["preco_estimado"] = True


def main():
    caminho = PASTA / "equipment.json"
    itens = json.loads(caminho.read_text(encoding="utf-8"))
    por_id = {i["id"]: i for i in itens}
    for item_id, (preco, fonte, nome) in PRECOS_DE_ITENS.items():
        item = por_id[item_id]
        if nome:
            item["nome"] = nome
        precificar(item, preco, fonte)
        if item_id in MUNICAO_DAS_ARMAS:
            item["municao"] = MUNICAO_DAS_ARMAS[item_id]
    for novo in ITENS_NOVOS:
        novo = dict(novo)
        novo.setdefault("fonte", "Item comum; custo em pontos de equipamento pelo livro básico, cap. 7")
        fonte_preco = novo.pop("fonte_preco")
        preco = novo.pop("preco")
        rotulo_categoria = novo.pop("categoria_de_preco", None)
        if novo["id"] in por_id:
            por_id[novo["id"]].update(novo)
            alvo = por_id[novo["id"]]
        else:
            itens.append(novo)
            por_id[novo["id"]] = novo
            alvo = novo
        precificar(alvo, preco, fonte_preco, rotulo_categoria)
    # Itens que saíram da tabela (a antiga "SMG pesada" de Dano 5 virou a submetralhadora do livro).
    itens = [i for i in itens if i["id"] not in ITENS_REMOVIDOS]
    sem_preco = [i["id"] for i in itens if "preco" not in i]
    assert not sem_preco, sem_preco
    caminho.write_text(json.dumps(itens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    caminho = PASTA / "powers.json"
    implantes = json.loads(caminho.read_text(encoding="utf-8"))
    for implante in implantes:
        preco, fonte = PRECOS_DE_IMPLANTES[implante["id"]]
        precificar(implante, preco, fonte)
    caminho.write_text(json.dumps(implantes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(itens)} itens e {len(implantes)} implantes com preço.")


if __name__ == "__main__":
    main()
