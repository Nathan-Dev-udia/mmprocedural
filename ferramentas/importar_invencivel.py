"""Importador de fichas de Invencível a partir de dados/livros/invencivel.md.

Gera os JSONs em dados/generos/herois/invencivel/ no formato comum de heróis.
"""

import json
import re
from pathlib import Path

RAIZ = Path(__file__).parent.parent
MD_FILE = RAIZ / "dados" / "livros" / "invencivel.md"
DEST_DIR = RAIZ / "dados" / "generos" / "herois" / "invencivel"


SLUGS_E_NOMES = [
    {
        "slug": "mark_grayson",
        "nome": "Mark Grayson",
        "nome_pt": "Invencível",
        "np": 10,
        "pp": 150,
    },
    {
        "slug": "rex_splode",
        "nome": "Rex Explode",
        "nome_pt": "Rex Splode",
        "np": 10,
        "pp": 135,
    },
    {
        "slug": "menina_monstro",
        "nome": "Menina Monstro",
        "nome_pt": "Monster Girl",
        "np": 10,
        "pp": 113,
    },
    {
        "slug": "allen_o_alien",
        "nome": "Allen o Alien",
        "nome_pt": "Allen the Alien",
        "np": 12,
        "pp": 225,
    },
    {
        "slug": "omni_man",
        "nome": "Omni-Man",
        "nome_pt": "Omni-Man (Nolan Grayson)",
        "np": 14,
        "pp": 232,
    },
    {
        "slug": "robo_drone_humanoide",
        "nome": "Robô (drone humanoide)",
        "nome_pt": "Robô (Drone Humanoide)",
        "np": 10,
        "pp": 131,
    },
    {
        "slug": "robo_drone_gigante",
        "nome": "Robô (Drone gigante)",
        "nome_pt": "Robô (Drone Gigante)",
        "np": 11,
        "pp": 145,
    },
    {
        "slug": "irmaos_mauler",
        "nome": "Os Irmãos Mauler",
        "nome_pt": "Gêmeos Mauler",
        "np": 8,
        "pp": 120,
    },
    {
        "slug": "o_imortal",
        "nome": "O Imortal",
        "nome_pt": "The Immortal",
        "np": 10,
        "pp": 165,
    },
    {
        "slug": "eve_atomica",
        "nome": "Eve Atômica",
        "nome_pt": "Atom Eve",
        "np": 10,
        "pp": 138,
    },
    {
        "slug": "battle_beast",
        "nome": "Battle Beast",
        "nome_pt": "Battle Beast",
        "np": 15,
        "pp": 215,
    },
    {
        "slug": "kratos",
        "nome": "Kratos",
        "nome_pt": "Kratos (Fantasma de Esparta)",
        "np": 12,
        "pp": 180,
        "categoria": "outros",
    },
]


def separar_secoes(bloco):
    sections = {}
    current_sec = "HEADER"
    current_lines = []

    sec_names = {
        "HABILIDADES": "habilidades",
        "DEFESAS": "defesas",
        "PERÍCIAS": "pericias",
        "PERICIAS": "pericias",
        "VANTAGENS": "vantagens",
        "PODERES": "poderes",
        "OFENSIVA": "ofensiva",
        "COMPLICAÇÕES": "complicacoes",
        "COMPLICACOES": "complicacoes",
        "NOTAS": "notas",
    }

    for line in bloco.splitlines():
        l_strip = line.strip()
        if "Habilidades" in l_strip and "=" in l_strip and ("pontos" in l_strip.lower() or "pts" in l_strip.lower()):
            sections[current_sec] = current_lines
            current_sec = "CUSTOS"
            current_lines = [line]
            continue

        m = re.match(r"^\s*(?:\*\*)?(?:###\s*)?(HABILIDADES|DEFESAS|PER[IÍ]CIAS|VANTAGENS|PODERES|OFENSIVA|COMPLICA[CÇ][OÕ]ES|NOTAS)(?:[^\n:]*)?(?:\*\*)?:?", l_strip, re.IGNORECASE)
        if m:
            sections[current_sec] = current_lines
            sec_key = sec_names[m.group(1).upper()]
            current_sec = sec_key
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_sec] = current_lines
    return sections


def parse_habilidades(linhas):
    habs = {}
    texto = "\n".join(linhas)
    for m in re.finditer(r"(For[çc]a|Vigor|Agilidade|Destreza|Luta|Intelecto|Prontid[ãa]o|Presen[çc]a)\s+([-\d/]+|\\-)", texto, re.IGNORECASE):
        nome = m.group(1).lower()
        val = m.group(2).replace(r"\-", "-").strip()
        sigla = {"força": "For", "vigor": "Vig", "agilidade": "Agi", "destreza": "Des",
                 "luta": "Lut", "intelecto": "Int", "prontidão": "Pro", "presença": "Pre"}.get(nome, nome[:3].capitalize())
        try:
            habs[sigla] = int(val)
        except ValueError:
            habs[sigla] = val
    return habs


def parse_defesas(linhas):
    defesas = {}
    texto = "\n".join(linhas)
    for d in ["Esquiva", "Aparar", "Resistência", "Fortitude", "Vontade"]:
        padrao = rf"{d}[^\n,;]*?(\*?IMUNE\*?|\+?\d+/\+?\d+\s*\(\+?\d+\)|\+?\d+\s*\(\+?\d+\)|\+?\d+/\+?\d+|\+?\d+)"
        m = re.search(padrao, texto, re.IGNORECASE)
        if m:
            v = m.group(1).strip()
            total_m = re.search(r"\((\+?\d+)\)", v)
            if total_m:
                defesas[d] = int(total_m.group(1))
            elif "IMUNE" in v.upper():
                defesas[d] = "Imune"
            elif "/" in v:
                p = re.findall(r"\d+", v)
                defesas[d] = int(p[0]) if p else v
            else:
                p = re.search(r"-?\d+", v)
                defesas[d] = int(p.group()) if p else v
    return defesas


def parse_pericias(linhas):
    texto = " ".join(l.strip() for l in linhas if l.strip())
    texto = re.sub(r"^\*\s*", "", texto).strip()
    itens = [p.strip() for p in re.split(r",\s*(?![^()]*\))", texto) if p.strip()]
    pericias_dict = {}
    lista = []
    for item in itens:
        item_limpo = item.rstrip(".")
        lista.append(item_limpo)
        m = re.search(r"^(.*?)\s+(\d+)\s*\((.*?)\)$", item_limpo)
        if m:
            nome = m.group(1).strip()
            grad = int(m.group(2))
            pericias_dict[nome] = grad
        else:
            m2 = re.search(r"^(.*?)\s+(\d+)$", item_limpo)
            if m2:
                pericias_dict[m2.group(1).strip()] = int(m2.group(2))
    return lista, pericias_dict


def parse_vantagens(linhas):
    texto = " ".join(l.strip() for l in linhas if l.strip())
    texto = re.sub(r"^\*\s*", "", texto).strip()
    itens = [p.strip().rstrip(".") for p in re.split(r",\s*(?![^()]*\))", texto) if p.strip()]
    return [i for i in itens if i]


def parse_poderes(linhas):
    poderes = []
    for l in linhas:
        l_strip = l.strip()
        if not l_strip:
            continue
        indent = len(l) - len(l.lstrip())
        texto_linha = re.sub(r"^[-*]\s*", "", l_strip).strip()
        # Se for sub-poder (indentado)
        if indent >= 2:
            poderes.append(f"• {texto_linha}")
        else:
            poderes.append(texto_linha)
    return poderes


def parse_ofensiva(linhas):
    iniciativa = 0
    ataques = []
    modo_atual = "Corpo a corpo"
    for l in linhas:
        l_strip = l.strip()
        if not l_strip:
            continue
        m_ini = re.search(r"Iniciativa\s*\\?\+?(-?\d+)", l_strip, re.IGNORECASE)
        if m_ini:
            iniciativa = int(m_ini.group(1))
            continue
        if re.search(r"Corpo-a-corpo", l_strip, re.IGNORECASE):
            modo_atual = "Corpo a corpo"
            continue
        if re.search(r"[ÀA]\s*Dist[âa]ncia", l_strip, re.IGNORECASE):
            modo_atual = "À distância"
            continue
        if re.search(r"Áreas|Especial", l_strip, re.IGNORECASE):
            modo_atual = "Área"
            continue
        # Ataque
        m_atq = re.search(r"^[-*]\s*(.*?)\s*\\?\+(\d+)[,\s]+(.*)$", l_strip)
        if m_atq:
            nome = m_atq.group(1).strip()
            bonus = int(m_atq.group(2))
            desc = m_atq.group(3).strip()
            # tenta pegar dano
            m_dano = re.search(r"dano[^\d]*(\d+)", desc, re.IGNORECASE)
            dano = int(m_dano.group(1)) if m_dano else ""
            ataques.append({
                "nome": nome,
                "bonus": bonus,
                "alcance": modo_atual,
                "dano": dano,
                "descricao": desc,
            })
        elif l_strip.startswith(("-", "*")):
            desc = re.sub(r"^[-*]\s*", "", l_strip).strip()
            if ":" in desc:
                nome, _, resto = desc.partition(":")
                ataques.append({
                    "nome": nome.strip(),
                    "bonus": None,
                    "alcance": modo_atual,
                    "dano": "",
                    "descricao": resto.strip(),
                })
    return iniciativa, ataques


def parse_custos(linhas):
    texto = " ".join(linhas)
    custos = {}
    total = None
    m = re.search(r"Habilidades\s*(\d+).*?Defesas\s*(\d+).*?Per[íi]cias\s*(\d+).*?Vantagens\s*(\d+).*?Poderes\s*(\d+).*?=\s*(\d+)", texto, re.IGNORECASE)
    if m:
        custos = {
            "Habilidades": int(m.group(1)),
            "Defesas": int(m.group(2)),
            "Perícias": int(m.group(3)),
            "Vantagens": int(m.group(4)),
            "Poderes": int(m.group(5)),
        }
        total = int(m.group(6))
    else:
        m2 = re.search(r"Habilidades\s*(\d+).*?Vantagens\s*(\d+).*?Per[íi]cias\s*(\d+).*?Poderes\s*(\d+).*?Defesas\s*(\d+).*?=\s*(\d+)", texto, re.IGNORECASE)
        if m2:
            custos = {
                "Habilidades": int(m2.group(1)),
                "Vantagens": int(m2.group(2)),
                "Perícias": int(m2.group(3)),
                "Poderes": int(m2.group(4)),
                "Defesas": int(m2.group(5)),
            }
            total = int(m2.group(6))
    return custos, total


def parse_complicacoes(linhas):
    comps = []
    comp_atual = None
    for l in linhas:
        l_strip = l.strip()
        if not l_strip:
            continue
        m = re.search(r"^[-*]\s*\*\*(.*?)\*\*:\s*(.*)$", l_strip)
        if m:
            if comp_atual:
                comps.append(comp_atual)
            comp_atual = {"titulo": m.group(1).strip(), "texto": m.group(2).strip()}
        elif comp_atual:
            comp_atual["texto"] += " " + l_strip
        else:
            m2 = re.search(r"^[-*]\s*\*\*(.*?)\*\*$", l_strip)
            if m2:
                comps.append({"titulo": m2.group(1).strip(), "texto": ""})
            elif l_strip.startswith(("-", "*")):
                comps.append({"titulo": l_strip.lstrip("-* ").strip(), "texto": ""})
    if comp_atual:
        comps.append(comp_atual)
    return comps


def processar_bloco(bloco, meta):
    secoes = separar_secoes(bloco)

    habs = parse_habilidades(secoes.get("habilidades", []))
    defesas = parse_defesas(secoes.get("defesas", []))
    pericias_lista, pericias_dict = parse_pericias(secoes.get("pericias", []))
    vantagens = parse_vantagens(secoes.get("vantagens", []))
    poderes = parse_poderes(secoes.get("poderes", []))
    iniciativa, ataques = parse_ofensiva(secoes.get("ofensiva", []))
    custos, total_pontos = parse_custos(secoes.get("CUSTOS", []))
    complicacoes = parse_complicacoes(secoes.get("complicacoes", []))

    notas_linhas = secoes.get("notas", [])
    notas = ["\n".join(notas_linhas).strip()] if notas_linhas else []

    dados = {
        "nome": meta["nome"],
        "nome_pt": meta["nome_pt"],
        "nivel_poder": meta["np"],
        "pontos_poder": total_pontos or meta["pp"],
        "universo": meta.get("categoria", "invencivel"),
        "fonte": {
            "arquivo": "dados/livros/invencivel.md",
        },
        "ficha": {
            "habilidades": habs,
            "defesas": defesas,
            "pericias": pericias_dict,
            "pericias_detalhes": pericias_lista,
            "vantagens": vantagens,
            "poderes": poderes,
            "equipamento": [],
            "iniciativa": iniciativa,
            "ataques": ataques,
            "custos": custos,
            "total": total_pontos or meta["pp"],
            "complicacoes": complicacoes,
            "notas": notas,
        }
    }
    return dados


def importar():
    with open(MD_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # remove imagem base64
    text = re.sub(r"\[image1\]:\s*<data:image/.*?>", "", text, flags=re.DOTALL)
    blocks = re.split(r"\n(?=#\s+|###\s+\*\*KRATOS)", text)

    # Limpa kratos de invencivel se existir
    kratos_antigo = DEST_DIR / "kratos.json"
    if kratos_antigo.is_file():
        kratos_antigo.unlink()

    importados = []
    for i, b in enumerate(blocks):
        b = b.strip()
        if not b or i >= len(SLUGS_E_NOMES):
            continue
        meta = SLUGS_E_NOMES[i]
        categoria = meta.get("categoria", "invencivel")
        pasta_destino = RAIZ / "dados" / "generos" / "herois" / categoria
        pasta_destino.mkdir(parents=True, exist_ok=True)

        dados = processar_bloco(b, meta)
        arquivo_json = pasta_destino / f"{meta['slug']}.json"
        with open(arquivo_json, "w", encoding="utf-8") as f_out:
            json.dump(dados, f_out, ensure_ascii=False, indent=2)
        importados.append(f"{categoria}/{meta['slug']}")
        print(f"Salvo: {arquivo_json.name} ({dados['nome']}) em {categoria}/")

    print(f"Total importados: {len(importados)}")


if __name__ == "__main__":
    importar()
