"""Módulo e ferramenta de tradução automática de fichas de M&M 3e (Marvel e DC).

Converte termos técnicos em inglês (efeitos de poderes, modificadores/extras/falhas,
condições de aflição, vantagens, perícias, sentidos, equipamentos e defesas) para
o português canônico do livro básico oficial.
"""

import argparse
import glob
import json
import re
from pathlib import Path

# Dicionários ordenados por tamanho decrescente para evitar substituições parciais
PODERES_EFEITOS = {
    "Enhanced Strength": "Força Aprimorada",
    "Enhanced Stamina": "Vigor Aprimorado",
    "Enhanced Agility": "Agilidade Aprimorada",
    "Enhanced Dexterity": "Destreza Aprimorada",
    "Enhanced Fighting": "Luta Aprimorada",
    "Enhanced Intellect": "Intelecto Aprimorado",
    "Enhanced Awareness": "Prontidão Aprimorada",
    "Enhanced Presence": "Presença Aprimorada",
    "Enhanced Trait": "Característica Aprimorada",
    "Impervious Toughness": "Resistência Impenetrável",
    "Super-Senses": "Super-Sentidos",
    "Super Senses": "Super-Sentidos",
    "Mind Reading": "Leitura Mental",
    "Mind Control": "Controle Mental",
    "Mental Blast": "Rajada Mental",
    "Move Object": "Mover Objetos",
    "Force Field": "Campo de Força",
    "Probability Control": "Controle de Probabilidade",
    "Luck Control": "Controle de Sorte",
    "Ranged Damage": "Dano à Distância",
    "Ranged Affliction": "Aflição à Distância",
    "Close Damage": "Dano Corpo a Corpo",
    "Close Affliction": "Aflição Corpo a Corpo",
    "Damage": "Dano",
    "Affliction": "Aflição",
    "Weaken": "Enfraquecer",
    "Nullify": "Nulificar",
    "Protection": "Proteção",
    "Impervious": "Impenetrável",
    "Immunity": "Imunidade",
    "Flight": "Voo",
    "Speed": "Velocidade",
    "Quickness": "Rapidez",
    "Leaping": "Salto",
    "Swimming": "Natação",
    "Burrowing": "Escavação",
    "Teleport": "Teleporte",
    "Movement": "Movimento",
    "Insubstantial": "Intangibilidade",
    "Concealment": "Camuflagem",
    "Strike": "Golpe",
    "Blast": "Raio",
    "Illusion": "Ilusão",
    "Create": "Criar Objetos",
    "Deflect": "Deflexão",
    "Healing": "Cura",
    "Regeneration": "Regeneração",
    "Immortality": "Imortalidade",
    "Morph": "Metamorfose",
    "Shapeshift": "Mudar de Forma",
    "Variable": "Variável",
    "Senses": "Sentidos",
    "Comprehend": "Compreender",
    "Communication": "Comunicação",
    "Feature": "Característica",
    "Shrinking": "Encolhimento",
    "Growth": "Crescimento",
    "Dazzle": "Ofuscar",
    "Elongation": "Alongamento",
    "Telepathy": "Telepatia",
    "Mimic": "Mimetismo",
    "Snare": "Aprisionar",
    "Device": "Dispositivo",
}

# Tradução específica para os 10 poderes da Marvel que não tinham nome_pt
NOMES_PODERES_MARVEL = {
    "Adhesive X Blaster": "Lançador de Adesivo X",
    "Star-Spangled Shield": "Escudo Estrelado",
    "Harness": "Tentáculos Mecânicos",
    "Probability Control": "Controle de Probabilidade",
    "Concealment": "Camuflagem nas Sombras",
    "Dazzle": "Clarão Cegante",
    "Shrinking 4": "Encolhimento",
    "Death Dust": "Pó da Morte",
    "Mimic (All Powers at Once) 10": "Mimetismo de Poderes",
    "Shocker Suit": "Traje de Choque",
}

SENTIDOS = {
    "Microscopic Vision": "Visão Microscópica",
    "Low-Light Vision": "Visão na Penumbra",
    "Low-light Vision": "Visão na Penumbra",
    "Extended Vision": "Visão Estendida",
    "Extended Hearing": "Audição Estendida",
    "Danger Sense": "Sentido de Perigo",
    "Direction Sense": "Noção de Direção",
    "Distance Sense": "Noção de Distância",
    "Time Sense": "Noção do Tempo",
    "Darkvision": "Visão no Escuro",
    "Infravision": "Infravisão",
    "Ultravision": "Ultravisão",
    "Ultra-Hearing": "Ultra-Audição",
    "Tremorsense": "Sentido Sísmico",
    "Radio": "Rádio",
    "Accurate": "Preciso",
    "Acute": "Aguçado",
    "Analytical": "Analítico",
    "Radius": "Raio",
    "Ranged": "À Distância",
}

CONDIÇÕES_AFLICAO = {
    "Dazed": "Tonto",
    "Stunned": "Atordoado",
    "Incapacitated": "Incapacitado",
    "Hindered": "Impedido",
    "Immobile": "Imóvel",
    "Paralyzed": "Paralisado",
    "Vulnerable": "Vulnerável",
    "Defenseless": "Indefeso",
    "Compelled": "Compelido",
    "Controlled": "Controlado",
    "Transformed": "Transformado",
    "Asleep": "Adormecido",
    "Blind": "Cego",
    "Deaf": "Surdo",
    "Fatigued": "Fatigado",
    "Exhausted": "Exausto",
    "Dying": "Moribundo",
}

MODIFICADORES = {
    "Perception Range": "Alcance de Percepção",
    "Increased Range": "Alcance Aumentado",
    "Alternate Resistance": "Resistência Alternativa",
    "Concentration Duration": "Duração de Concentração",
    "Easily Removable": "Facilmente Removível",
    "Easily removable": "Facilmente Removível",
    "Shapeable Area": "Área Moldável",
    "Cylinder Area": "Área Cilíndrica",
    "Burst Area": "Área de Explosão",
    "Cloud Area": "Área de Nuvem",
    "Cone Area": "Área de Cone",
    "Line Area": "Área de Linha",
    "Variable Descriptor": "Descritor Variável",
    "Affects Insubstantial": "Afeta Intangível",
    "Sense-Dependent": "Dependente de Sentidos",
    "Check Required": "Exige Teste",
    "Free Action": "Ação Livre",
    "Move Action": "Ação de Movimento",
    "Standard Action": "Ação Padrão",
    "Secondary Effect": "Efeito Secundário",
    "Side Effect": "Efeito Colateral",
    "Grab-based": "Baseado em Agarrar",
    "Alternate Effect": "Efeito Alternativo",
    "Dynamic Alternate Effect": "Efeito Alternativo Dinâmico",
    "Selective": "Seletivo",
    "Multiattack": "Multiataque",
    "Penetrating": "Penetrante",
    "Precise": "Preciso",
    "Subtle": "Sutil",
    "Insidious": "Insidioso",
    "Triggered": "Gatilho",
    "Contagious": "Contagioso",
    "Cumulative": "Cumulativo",
    "Progressive": "Progressivo",
    "Continuous": "Contínuo",
    "Sustained": "Sustentado",
    "Reaction": "Reação",
    "Concentration": "Concentração",
    "Limited": "Limitado",
    "Removable": "Removível",
    "removable": "removível",
    "Array": "Arranjo",
    "Limited to Two Degrees": "Limitado a Dois Graus",
    "Limited to": "Limitado a",
    "Distracting": "Distrativo",
    "Fades": "Dissipação",
    "Tiring": "Cansativo",
    "Unreliable": "Não Confiável",
    "Activation": "Ativação",
    "Quirk": "Peculiaridade",
    "Resistible": "Resistível",
    "Noticeable": "Perceptível",
    "Innate": "Inato",
    "Permanent": "Permanente",
    "Feedback": "Retroalimentação",
    "Dimensional": "Dimensional",
    "Split": "Dividido",
    "Homing": "Teleguiado",
    "Reversible": "Reversível",
    "Ricochet": "Ricochete",
    "Ranged": "À Distância",
    "Close": "Corpo a Corpo",
}

VANTAGENS = {
    "Accurate Attack": "Ataque Preciso",
    "Agile Feint": "Finta Ágil",
    "All-out Attack": "Ataque Imprudente",
    "All-Out Attack": "Ataque Imprudente",
    "Animal Empathy": "Empatia com Animais",
    "Artificer": "Artífice",
    "Assessment": "Avaliação",
    "Attractive": "Atraente",
    "Benefit": "Benefício",
    "Chokehold": "Estrangular",
    "Close Attack": "Ataque Corpo-a-Corpo",
    "Connected": "Conectado",
    "Contacts": "Contatos",
    "Daze": "Tontear",
    "Defensive Attack": "Ataque Defensivo",
    "Defensive Roll": "Rolamento Defensivo",
    "Diehard": "Duro de Matar",
    "Eidetic Memory": "Memória Eidética",
    "Equipment": "Equipamento",
    "Extraordinary Effort": "Esforço Extraordinário",
    "Fascinate": "Fascinar",
    "Fast Grab": "Agarrar Rápido",
    "Favored Environment": "Ambiente Favorito",
    "Favored Foe": "Inimigo Favorito",
    "Fearless": "Destemido",
    "Grabbing Finesse": "Agarrar com Destreza",
    "Great Endurance": "Grande Vigor",
    "Hide in Plain Sight": "Esconder-se a Plena Vista",
    "Improved Aim": "Mira Aprimorada",
    "Improved Critical": "Crítico Aprimorado",
    "Improved Defense": "Defesa Aprimorada",
    "Improved Disarm": "Desarmar Aprimorado",
    "Improved Grab": "Agarrar Aprimorado",
    "Improved Hold": "Imobilizar Aprimorado",
    "Improved Initiative": "Iniciativa Aprimorada",
    "Improved Smash": "Quebrar Aprimorado",
    "Improved Trip": "Derrubar Aprimorado",
    "Improvised Tools": "Ferramentas Improvisadas",
    "Improvised Weapon": "Arma Improvisada",
    "Inspire": "Inspirar",
    "Instant Up": "Levantar Rápido",
    "Interpose": "Interpor-se",
    "Inventor": "Inventor",
    "Jack-of-all-trades": "Pau pra Toda Obra",
    "Leadership": "Liderança",
    "Luck": "Sorte",
    "Minion": "Capanga",
    "Move-by Action": "Ação em Movimento",
    "Power Attack": "Ataque Poderoso",
    "Prone Fighting": "Luta Caída",
    "Quick Draw": "Saque Rápido",
    "Ranged Attack": "Ataque à Distância",
    "Redirect": "Redirecionar",
    "Ritualist": "Ritualista",
    "Second Chance": "Segunda Chance",
    "Seize Initiative": "Tomar a Iniciativa",
    "Set-up": "Preparar",
    "Sidekick": "Parceiro",
    "Skill Mastery": "Maestria em Perícia",
    "Startle": "Assustar",
    "Takedown": "Derrubar em Sequência",
    "Taunt": "Provocar",
    "Teamwork": "Trabalho em Equipe",
    "Throwing Mastery": "Maestria em Arremesso",
    "Tracking": "Rastrear",
    "Trance": "Transe",
    "Ultimate Effort": "Esforço Supremo",
    "Uncanny Dodge": "Esquiva Fabulosa",
    "Weapon Bind": "Prender Arma",
    "Weapon Break": "Quebrar Arma",
    "Well-informed": "Bem-Informado",
    "Well-Informed": "Bem-Informado",
    "Sneak Attack": "Ataque Furtivo",
}

PERICIAS = {
    "Acrobatics": "Acrobacia",
    "Athletics": "Atletismo",
    "Close Combat": "Combate Corpo-a-Corpo",
    "Deception": "Enganação",
    "Expertise": "Especialidade",
    "Insight": "Intuição",
    "Intimidation": "Intimidação",
    "Intimidate": "Intimidação",
    "Investigation": "Investigação",
    "Investigate": "Investigação",
    "Perception": "Percepção",
    "Persuasion": "Persuasão",
    "Ranged Combat": "Combate à Distância",
    "Sleight of Hand": "Prestidigitação",
    "Stealth": "Furtividade",
    "Technology": "Tecnologia",
    "Treatment": "Tratamento",
    "Vehicles": "Veículos",
}

DEFESAS = {
    "Dodge": "Esquiva",
    "Parry": "Aparar",
    "Fortitude": "Fortitude",
    "Toughness": "Resistência",
    "Will": "Vontade",
}

HABILIDADES = {
    "Strength": "Força",
    "Stamina": "Vigor",
    "Agility": "Agilidade",
    "Dexterity": "Destreza",
    "Fighting": "Luta",
    "Intellect": "Intelecto",
    "Awareness": "Prontidão",
    "Presence": "Presença",
}

TERMOS_GERAIS = {
    "points": "pontos",
    "point": "ponto",
    "ranks": "graduações",
    "rank": "graduação",
    "Unarmed": "Desarmado",
    "Initiative": "Iniciativa",
    "Close": "corpo a corpo",
    "Ranged": "à distância",
    "Area": "área",
    "Resisted by": "resistido por",
    "DC": "CD",
    "Airborne": "Aéreo",
    "Underwater": "Subaquático",
    "Will saves": "salvamentos de Vontade",
    "Toughness saves": "salvamentos de Resistência",
    "Fortitude saves": "salvamentos de Fortitude",
    "Damage resistance": "Resistência a Dano",
    "Ball and Chain": "Bola e Corrente",
    "Knife Attack": "Ataque com Faca",
    "Shield Bash": "Golpe com Escudo",
    "Aging": "Envelhecimento",
    "Life Support": "Suporte Vital",
    "miles": "milhas",
    "Cold": "Frio",
    "Heat": "Calor",
    "Pressure": "Pressão",
    "Drowning": "Afogamento",
    "Disease": "Doença",
    "Poison": "Veneno",
    "Suffocation": "Sufocamento",
    "Radiation": "Radiação",
    "Vacuum": "Vácuo",
    "Starvation": "Inanição",
    "electricity": "eletricidade",
    "fire": "fogo",
    "mental": "mental",
    "magic": "mágico",
    "plus others": "mais outros",
    "Without Defensive Roll": "sem Rolamento Defensivo",
    "Without Venom": "sem Veneno",
    "Varies based on Shapeshifting": "Varia com Mudar de Forma",
    "Pistol": "Pistola",
    "Rifle": "Rifle",
    "Sword": "Espada",
    "Shield": "Escudo",
    "Tommy Gun": "Metralhadora Tommy",
    "Bio-Shell Strikes": "Golpes de Bio-Carapaça",
    "Mental Blast": "Rajada Mental",
    "Optic Blasters": "Disparadores Ópticos",
    "Mini-Torpedoes": "Minitorpedos",
    "Grapple-Wire": "Cabo de Gancho",
    "Electric Shock": "Choque Elétrico",
    "Twin Blades": "Lâminas Gêmeas",
    "Lapel Flower": "Flor de Lapela",
    "Joker Venom": "Veneno do Coringa",
    "Squirting Acid": "Ácido Espirrado",
    "Joy Buzzer": "Campainha Elétrica",
    "Marbles": "Bolinhas de Gude",
    "Batarang": "Batarangue",
    "Batarangs": "Batarangues",
    "Immortal": "Imortal",
    "Omega Effect": "Efeito Ômega",
    "Destruction": "Destruição",
    "Pain": "Dor",
    "Transportation": "Transporte",
}

EQUIPAMENTO_TERMOS = {
    "Damage": "Dano",
    "Toughness": "Resistência",
    "Protection": "Proteção",
    "Autofire": "Multiataque",
    "Auto-Fire": "Multiataque",
    "Mighty": "Baseado em Força",
    "Improved Critical": "Crítico Aprimorado",
    "Subtle": "Sutil",
    "EP": "PE",
    "Crit": "Crítico",
}


def _substituir_mapa(texto, mapa):
    """Substitui termos inteiros baseando-se em limites de palavras e regex."""
    if not texto:
        return texto
    for k in sorted(mapa.keys(), key=len, reverse=True):
        v = mapa[k]
        padrao = r"\b" + re.escape(k) + r"\b"
        texto = re.sub(padrao, v, texto, flags=re.IGNORECASE)
    return texto


def traduzir_construcao(texto):
    """Traduz fórmulas mecânicas de poderes e efeitos (ex: construcao_3e)."""
    if not texto:
        return texto
    
    texto = _substituir_mapa(texto, PODERES_EFEITOS)
    texto = _substituir_mapa(texto, SENTIDOS)
    texto = _substituir_mapa(texto, CONDIÇÕES_AFLICAO)
    texto = _substituir_mapa(texto, MODIFICADORES)
    texto = _substituir_mapa(texto, DEFESAS)
    texto = _substituir_mapa(texto, HABILIDADES)
    texto = _substituir_mapa(texto, TERMOS_GERAIS)
    
    # Ajustar ranks numéricos e MPH para km/h
    texto = re.sub(r"(\d+)\s*MPH\b", lambda m: f"{int(int(m.group(1)) * 1.6)} km/h", texto, flags=re.IGNORECASE)
    return texto


def traduzir_vantagem(nome):
    """Traduz o nome de uma vantagem (ex: 'Uncanny Dodge', 'Daze (Deception)')."""
    if not nome:
        return nome
    
    m = re.match(r"^([^(]+)\((.+)\)(.*)$", nome)
    if m:
        base, dentro, resto = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        base_pt = VANTAGENS.get(base, base)
        dentro_pt = PERICIAS.get(dentro, dentro)
        dentro_pt = SENTIDOS.get(dentro_pt, dentro_pt)
        dentro_pt = DEFESAS.get(dentro_pt, dentro_pt)
        dentro_pt = _substituir_mapa(dentro_pt, TERMOS_GERAIS)
        res = f"{base_pt} ({dentro_pt})"
        if resto:
            res += f" {resto}"
        return res
    
    m_num = re.match(r"^(.+?)\s+(\d+)$", nome)
    if m_num:
        base, num = m_num.group(1).strip(), m_num.group(2)
        base_pt = VANTAGENS.get(base, base)
        return f"{base_pt} {num}"
        
    return VANTAGENS.get(nome, nome)


def traduzir_pericia(nome):
    """Traduz nome de perícia (ex: 'Close Combat: Unarmed' -> 'Combate Corpo a Corpo: Desarmado')."""
    if not nome:
        return nome
    for k, v in PERICIAS.items():
        if nome.startswith(k):
            resto = nome[len(k):]
            for gk, gv in TERMOS_GERAIS.items():
                resto = re.sub(r"\b" + re.escape(gk) + r"\b", gv, resto, flags=re.IGNORECASE)
            return f"{v}{resto}"
    return nome


def traduzir_equipamento(texto):
    """Traduz termos comuns em equipamentos (ex: '+3 Damage; Mighty; 2 EP')."""
    if not texto:
        return texto
    return _substituir_mapa(texto, EQUIPAMENTO_TERMOS)


def traduzir_ficha_marvel(dados):
    """Traduz os campos de uma ficha da Marvel (JSON)."""
    ficha = dados.get("ficha", {})
    
    # 1. Poderes
    for p in ficha.get("poderes", []):
        nome = p.get("nome", "")
        nome_pt = p.get("nome_pt", "")
        if not nome_pt or nome_pt == nome:
            trad = NOMES_PODERES_MARVEL.get(nome) or PODERES_EFEITOS.get(nome) or SENTIDOS.get(nome)
            if trad:
                p["nome_pt"] = trad
        if "construcao_3e" in p:
            p["construcao_3e"] = traduzir_construcao(p["construcao_3e"])
            
    # 2. Vantagens
    novas_vantagens = []
    for v in ficha.get("vantagens", []):
        novas_vantagens.append(traduzir_vantagem(v))
    ficha["vantagens"] = novas_vantagens
    
    # 3. Perícias
    pericias = ficha.get("pericias", {})
    if isinstance(pericias, dict):
        novas_pericias = {}
        for k, val in pericias.items():
            novas_pericias[traduzir_pericia(k)] = val
        ficha["pericias"] = novas_pericias

    # 4. Equipamento
    if "equipamento" in ficha and isinstance(ficha["equipamento"], list):
        ficha["equipamento"] = [traduzir_equipamento(eq) for eq in ficha["equipamento"]]
        
    return dados


def traduzir_ficha_dc_publicada(ficha_pub):
    """Traduz os blocos de texto publicados das fichas da DC."""
    res = dict(ficha_pub)
    
    if "defesas" in res:
        res["defesas"] = _substituir_mapa(res["defesas"], DEFESAS)
        res["defesas"] = res["defesas"].replace("Without Defensive Roll", "sem Rolamento Defensivo")
        
    if "pericias" in res:
        itens = [p.strip() for p in res["pericias"].split(",")]
        novos = [_substituir_mapa(it, PERICIAS) for it in itens]
        res["pericias"] = ", ".join(novos)
        
    if "vantagens" in res:
        itens = [v.strip() for v in res["vantagens"].split(",")]
        novos = [traduzir_vantagem(v) for v in itens]
        res["vantagens"] = ", ".join(novos)
        
    if "poderes" in res:
        res["poderes"] = traduzir_construcao(res["poderes"])
        
    if "ataques" in res:
        res["ataques"] = _substituir_mapa(res["ataques"], TERMOS_GERAIS)
        res["ataques"] = _substituir_mapa(res["ataques"], PODERES_EFEITOS)
        
    return res


def aplicar_traducao_marvel(raiz_projeto=None):
    """Aplica a tradução nos 116 arquivos da Marvel salvando os arquivos no disco."""
    raiz = Path(raiz_projeto) if raiz_projeto else Path(__file__).resolve().parent.parent
    pasta_marvel = raiz / "dados" / "generos" / "herois" / "marvel"
    arquivos = list(pasta_marvel.glob("*.json"))
    total_modificados = 0

    for arq in arquivos:
        original = json.loads(arq.read_text(encoding="utf-8"))
        copia = json.loads(json.dumps(original))
        traduzido = traduzir_ficha_marvel(copia)
        
        str_orig = json.dumps(original, ensure_ascii=False, indent=2)
        str_trad = json.dumps(traduzido, ensure_ascii=False, indent=2)
        if str_orig != str_trad:
            arq.write_text(str_trad + "\n", encoding="utf-8")
            total_modificados += 1

    print(f"Tradução da Marvel concluída: {total_modificados} de {len(arquivos)} arquivos atualizados.")
    return total_modificados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tradutor de fichas de heróis de M&M 3e.")
    parser.add_argument("--marvel", action="store_true", help="Aplica tradução nos arquivos da Marvel")
    args = parser.parse_args()

    if args.marvel:
        aplicar_traducao_marvel()
    else:
        print("Use --marvel para aplicar a tradução aos arquivos da Marvel.")
