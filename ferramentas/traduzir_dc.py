"""Script para gerar fichas traduzidas da DC em dados/generos/herois/traducoes/dc/

Converte as fichas publicadas em inglês do DC Adventures para a estrutura canônica
em português usada pelo sistema (aproveitada na tela e nos PDFs).
"""

import argparse
import json
import re
from pathlib import Path
import sys

# Importar o motor de termos do tradutor de heróis
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nucleo.herois import _dividir_por_custo
from nucleo import rules
from ferramentas import tradutor_herois as t

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DC = RAIZ / "dados" / "generos" / "herois" / "dc"
PASTA_TRADUCOES = RAIZ / "dados" / "generos" / "herois" / "traducoes" / "dc"

HABILIDADES_MAP = {
    "STR": "For", "STA": "Vig", "AGL": "Agi", "DEX": "Des",
    "FGT": "Lut", "INT": "Int", "AWE": "Pro", "PRE": "Pre"
}

NOMES_DC_PT = {
    "the_joker": "Coringa",
    "lex_luthor": "Lex Luthor",
    "darkseid": "Darkseid",
    "nightwing": "Asa Noturna (Dick Grayson)",
    "robin": "Robin (Damian Wayne)",
    "red_robin": "Robin Vermelho (Tim Drake)",
    "catwoman": "Mulher-Gato (Selina Kyle)",
    "deathstroke_the_terminator": "Exterminador (Slade Wilson)",
    "sinestro": "Sinestro",
    "harley_quinn": "Arlequina (Harleen Quinzel)",
    "black_adam": "Adão Negro",
    "raven": "Ravena",
    "starfire": "Estelar",
    "cyborg": "Ciborgue (Victor Stone)",
    "beast_boy": "Mutano (Garfield Logan)",
    "poison_ivy": "Hera Venenosa (Pamela Isley)",
    "the_riddler": "Charada (Edward Nigma)",
    "two_face": "Duas-Caras (Harvey Dent)",
    "bane": "Bane",
    "scarecrow": "Espantalho (Jonathan Crane)",
    "brainiac": "Brainiac",
    "bizarro": "Bizarro",
    "general_zod": "General Zod",
    "supergirl": "Supergirl (Kara Zor-El)",
    "captain_marvel": "Shazam (Capitão Marvel)",
    "captain_cold": "Capitão Frio (Leonard Snart)",
    "black_canary_dinah_laurel_lance": "Canário Negro (Dinah Laurel Lance)",
    "zatanna": "Zatanna Zatara",
    "hawkgirl": "Mulher-Gavião (Kendra Saunders)",
    "hawkman": "Gavião Negro (Carter Hall)",
    "the_penguin": "Pinguim (Oswald Cobblepot)",
    "solomon_grundy": "Solomon Grundy",
    "ras_al_ghul": "Ra's al Ghul",
    "black_manta": "Arraia Negra",
    "blue_beetle_jaime_reyes": "Besouro Azul (Jaime Reyes)",
    "booster_gold": "Gladiador Dourado (Michael Jon Carter)",
    "cheetah": "Mulher-Leopardo (Barbara Ann Minerva)",
    "batgirl_barbara_gordon": "Batgirl (Barbara Gordon)",
    "batwoman": "Batwoman (Kate Kane)",
    "huntress": "Caçadora (Helena Bertinelli)",
    "swamp_thing": "Monstro do Pântano",
    "the_spectre": "Espectro",
    "john_constantine": "John Constantine",
}

# Fichas que NUNCA devem ser sobrescritas (preservar traduções manuais ou exigidas em testes de fallback raw)
FICHAS_PROTEGIDAS = {
    # Traduções manuais canônicas originais:
    "aquaman", "batman", "green_arrow_oliver_queen", "green_lantern_hal_jordan",
    "the_flash_barry_allen", "martian_manhunter", "superman", "wonder_woman",
    # Fichas usadas para testar o parser/fallback de texto original em inglês:
    "adam_strange", "captain_comet", "blockbuster_roland_desmond", "dwarfstar"
}


def normalizar_texto_dc(texto):
    """Corrige falhas de kerning / drop capitals frequentes nos Volumes 1 e 2."""
    if not texto:
        return ""
    subs = [
        (r"\bo\s+ffen\s*S\s*e\b|\bf\s*f\s*e\s*n\s*S\s*e(?:\s+o)?\b", "Offense"),
        (r"\bense:", "Offense:"),
        (r"\bd\s+efen\s*S\s*e\b|\be\s*f\s*e\s*n\s*S\s*e(?:\s+d)?\b", "Defense"),
        (r"\befense:", "Defense:"),
        (r"\bo\s+ff\b", ""),
        (r"\bPo\s*er\s*Point(?:\s*W\s*S)?\b|\bW\s*S\s*Po\s*er\s*Point\b", "Power Points"),
        (r"\bi\s*n\s*i\s*t\s*i\s*a\s*t\s*i\s*v\s*e\b", "Initiative"),
        (r"\bd\s*o\s*d\s*g\s*e\b", "Dodge"),
        (r"\bf\s*o\s*r\s*t\s*i\s*t\s*u\s*d\s*e\b", "Fortitude"),
        (r"\bp\s*a\s*r\s*r\s*y\b", "Parry"),
        (r"\bt\s*o\s*u\s*g\s*h\s*n\s*e\s*s\s*s\b", "Toughness"),
        (r"\bw\s*i\s*l\s*l\b", "Will"),
        (r"\bd\s+amage\b", "Damage"),
        (r"\ba\s+ffliction\b", "Affliction"),
        (r"\bc\s+lose\b", "Close"),
        (r"\br\s+anged\b", "Ranged"),
        (r"\bp\s+erception\b", "Perception"),
        (r"\bligh\s+t\b", "light"),
        (r"\ba\s*b\s*i\s*l\s*i\s*t\s*i\s*e\s*s\b", "Abilities"),
        (r"\bs\s*k\s*i\s*l\s*l\s*s\b", "Skills"),
        (r"\bp\s*o\s*w\s*e\s*r\s*s\b", "Powers"),
        (r"\bd\s*e\s*f\s*e\s*n\s*s\s*e\s*s\b", "Defenses"),
        (r"\ba\s*d\s*v\s*a\s*n\s*t\s*a\s*g\s*e\s*s\b", "Advantages"),
        (r"\bt\s*o\s*t\s*a\s*l\b", "Total"),
    ]
    for padrao, sub in subs:
        texto = re.sub(padrao, sub, texto, flags=re.IGNORECASE)
    # Remove espaços espúrios após sinal de + ou - antes de dígitos (ex: "+ 10" -> "+10")
    texto = re.sub(r"(?<!\d\s)([+-])\s+(\d)", r"\1\2", texto)
    # Normaliza travessões curtos (–, −) antes de dígitos para hífen ASCII
    texto = re.sub(r"[–−](\d)", r"-\1", texto)
    texto = re.sub(r"\s{2,}", " ", texto).strip()
    return texto


def _extrair_bloco_secao(texto, inicio_regex, fim_regex=None):
    """Recorta o trecho de texto a partir de um cabeçalho vazado até o próximo cabeçalho."""
    if not texto:
        return ""
    m = re.search(inicio_regex, texto, re.IGNORECASE)
    if not m:
        return ""
    recorte = texto[m.start():]
    if fim_regex:
        m_fim = re.search(fim_regex, recorte[len(m.group(0)):], re.IGNORECASE)
        if m_fim:
            recorte = recorte[: len(m.group(0)) + m_fim.start()]
    return recorte


def extrair_habilidades(ficha_pub):
    res = {}
    for k, v in ficha_pub.get("habilidades", {}).items():
        v_str = str(v).strip()
        # Se é traço (habilidade ausente, ex: robôs/construtos sem Vigor)
        if re.search(r"^[–—−-]+$", v_str) or v_str in ("", "None"):
            res[HABILIDADES_MAP.get(k, k)] = "—"
        else:
            m = re.search(r"-?\d+", v_str.translate(str.maketrans("–—−", "---")).split("/")[0])
            res[HABILIDADES_MAP.get(k, k)] = int(m.group()) if m else 0
    return res


def extrair_defesas(def_texto, textos_extras=None):
    candidatos = [normalizar_texto_dc(def_texto)] if def_texto else []
    for ex in (textos_extras or []):
        if ex:
            norm = normalizar_texto_dc(ex)
            bloco = _extrair_bloco_secao(norm, r"\bDefense(?:s)?\b", r"\bPower Points\b")
            candidatos.append(bloco or norm)

    defesas = {}
    txt_principal = candidatos[0] if candidatos else ""
    for txt in candidatos:
        if len(defesas) >= 5:
            break
        for m in re.finditer(r"\b(Dodge|Parry|Fortitude|Toughness|Will)\s+([+-]?\d+|Immune|[—–\-])", txt, re.IGNORECASE):
            nome_d = t.DEFESAS.get(m.group(1).capitalize(), m.group(1).capitalize())
            if nome_d in defesas:
                continue
            val = m.group(2)
            if re.match(r"^[+-]?\d+$", val):
                defesas[nome_d] = int(val)
            else:
                defesas[nome_d] = None
        if len(defesas) >= 3:
            if not txt_principal:
                txt_principal = txt
            break

    obs_defesas = ""
    if txt_principal:
        txt_sem_pp = re.split(r"\bPower Points\b", txt_principal, maxsplit=1, flags=re.IGNORECASE)[0]
        obs_m = re.search(r"(\*+[^*].*)$", txt_sem_pp)
        if obs_m:
            obs_defesas = t.traduzir_construcao(obs_m.group(1).strip())
    return defesas, obs_defesas


def extrair_custos(custos_texto, total_pub, textos_extras=None):
    candidatos = []
    if custos_texto:
        candidatos.append(normalizar_texto_dc(custos_texto))
    for ex in (textos_extras or []):
        if ex:
            norm = normalizar_texto_dc(ex)
            bloco = _extrair_bloco_secao(norm, r"\b(?:Power Points|Abilities)\b")
            if bloco:
                candidatos.append(bloco)

    custos = {}
    total = total_pub
    for txt in candidatos:
        for m in re.finditer(r"\b(Abilities|Skills|Powers|Defenses|Advantages)\s+(-?\d+)", txt, re.IGNORECASE):
            cat_pt = {
                "Abilities": "Habilidades", "Skills": "Perícias", "Powers": "Poderes",
                "Defenses": "Defesas", "Advantages": "Vantagens"
            }.get(m.group(1).capitalize(), m.group(1).capitalize())
            custos.setdefault(cat_pt, int(m.group(2)))
        if not total:
            m_tot = re.search(r"\bTotal\s+(-?\d+)|=\s*(-?\d+)", txt, re.IGNORECASE)
            if m_tot:
                total = int(m_tot.group(1) or m_tot.group(2))
        if len(custos) == 5 and total:
            break

    if not total and len(custos) == 5:
        total = sum(custos.values())
    return custos, total


def extrair_vantagens(vantagens_texto):
    if not vantagens_texto:
        return []
    txt = normalizar_texto_dc(vantagens_texto)
    itens = [v.strip().rstrip(",") for v in re.split(r",\s*(?![^()]*\))", txt) if v.strip().rstrip(",")]
    return [t.traduzir_vantagem(v) for v in itens]


def extrair_pericias(per_texto):
    if not per_texto:
        return []
    txt = normalizar_texto_dc(per_texto)
    # Rejuntar quebras com hífen (ex: Technol- ogy, Ornitholo - gy)
    txt = re.sub(r"([A-Za-z]{3,})-\s+([a-z]{2,})", r"\1\2", txt)
    txt = re.sub(r"Expertise\s*\([A-Z]+\):", "Expertise:", txt)
    txt = re.sub(r"\bRange(?:d\s+Attack)?\s+Combat\b", "Ranged Combat", txt, flags=re.I)
    txt = re.sub(r"\bRanged\s+Attack:", "Ranged Combat:", txt, flags=re.I)
    txt = re.sub(r"\bExpert:", "Expertise:", txt, flags=re.I)
    txt = re.sub(r"\bPerceptions\b", "Perception", txt, flags=re.I)

    pericias = []
    bloco = re.split(r"\b(?:Offense|Defense|Initiative|Some of|Notes?:)\b", txt, maxsplit=1, flags=re.I)[0]
    for part in re.finditer(r"([A-Za-z0-9\s:\-&()/'\"]+?)\s+(\d+)\s*\(\+?(-?\d+)(?:/[^)]+)?\)", bloco):
        nome_bruto = part.group(1).strip()
        nome_bruto = re.sub(r"^[0-9*),;.\s\-]+", "", nome_bruto)
        nome_bruto = re.sub(r"^\([^)]*\)\s*", "", nome_bruto)
        nome_bruto = re.sub(r"^[0-9*),;.\s\-]+", "", nome_bruto)
        if not nome_bruto:
            continue
        nome_p_pt = t.traduzir_pericia(nome_bruto)
        base = rules.nome_base(nome_p_pt)
        if base == "Combate Corpo a Corpo":
            base = "Combate Corpo-a-Corpo"
            nome_p_pt = nome_p_pt.replace("Combate Corpo a Corpo", "Combate Corpo-a-Corpo")
        if base not in rules.PERICIAS:
            nome_p_pt = f"Especialidade: {nome_p_pt}"
        pericias.append({
            "nome": nome_p_pt,
            "graduacoes": int(part.group(2)),
            "total": int(part.group(3))
        })
    return pericias


def _parse_ataques_texto(txt):
    ini_m = re.search(r"Initiative\s*\+?(-?\d+)", txt, re.IGNORECASE)
    iniciativa = int(ini_m.group(1)) if ini_m else 0
    resto = re.sub(r"^\s*Offense\s*:?\s*", "", txt, flags=re.IGNORECASE)
    resto = re.sub(r"\bDefense\b.*$", "", resto, flags=re.IGNORECASE)
    resto = re.sub(r"Initiative\s*\+?(-?\d+)[,.]?", "", resto, flags=re.IGNORECASE).strip()
    if not resto:
        return iniciativa, []

    ataques = []
    # Caso 1: ataques com parênteses: "Ataque +X (Alcance, Dano), Outro — (Alcance, Dano)"
    if "(" in resto and ")" in resto and not re.search(r"(?:Close|Ranged)\s*,\s*Damage\s+\d+\s+[A-Z]", resto):
        partes = re.split(r"(?<=\))\s*,\s*", resto)
        for p in partes:
            p = p.strip().rstrip(",")
            if not p:
                continue
            m_paren = re.match(r"^(.+?)(?:\s*(?:(\+?-?\d+)|[—]))?\s*\(([^)]+)\)$", p)
            if m_paren:
                nome = m_paren.group(1).strip(" —-")
                bonus = int(m_paren.group(2)) if m_paren.group(2) else None
                detalhes = [d.strip() for d in m_paren.group(3).split(",")]
                alcance = ""
                if detalhes and detalhes[0].lower() in ("close", "ranged", "perception", "perception range"):
                    alc_raw = detalhes.pop(0).lower()
                    alcance = "Corpo a corpo" if "close" in alc_raw else ("À distância" if "ranged" in alc_raw else "Percepção")
                dano = ", ".join(detalhes)
                ataques.append({
                    "nome": t.traduzir_construcao(nome),
                    "bonus": bonus,
                    "alcance": alcance,
                    "dano": t.traduzir_construcao(dano)
                })
        if ataques:
            return iniciativa, ataques

    # Caso 2: formato padrão sem parênteses externos (incluindo ataques de área/percepção com —)
    resto = re.sub(
        r"(plus\s+others|others|\d+|\))\s+([A-Z][A-Za-z0-9'’\-/]*(?:\s+[A-Z0-9][A-Za-z0-9'’\-/]*){0,4})\s*(\+\d+|—)",
        r"\1 /// \2 \3",
        resto,
    )
    blocos = [b.strip() for b in resto.split("///") if b.strip()]

    for bloco in blocos:
        m = re.match(
            r"^([A-Za-z0-9\s\-_/'’]+?)\s*(?:(\+\d+)|—)\*?\s*(?:(Close|Ranged|Perception\s+Range(?:d)?)\s*,?\s*)?(.*)$",
            bloco,
            re.I,
        )
        if m:
            nome = m.group(1).strip()
            bonus = int(m.group(2)) if m.group(2) else None
            alc_raw = (m.group(3) or "").lower()
            alcance = (
                "Corpo a corpo" if "close" in alc_raw
                else ("À distância" if "ranged" in alc_raw and "perception" not in alc_raw
                      else ("Percepção" if "perception" in alc_raw else ""))
            )
            dano = m.group(4).strip().rstrip(" ,.")
            if not alcance:
                if re.match(r"^(Close|Corpo a corpo)\b", dano, re.I):
                    alcance = "Corpo a corpo"
                    dano = re.sub(r"^(Close|Corpo a corpo)\s*,?\s*", "", dano, flags=re.I)
                elif re.match(r"^(Ranged|À distância)\b", dano, re.I):
                    alcance = "À distância"
                    dano = re.sub(r"^(Ranged|À distância)\s*,?\s*", "", dano, flags=re.I)
                elif re.match(r"^(Perception\s+Range(?:d)?|Alcance de Percepção)\b", dano, re.I):
                    alcance = "Percepção"
                    dano = re.sub(r"^(Perception\s+Range(?:d)?|Alcance de Percepção)\s*,?\s*", "", dano, flags=re.I)
            ataques.append({
                "nome": t.traduzir_construcao(nome),
                "bonus": bonus,
                "alcance": alcance,
                "dano": t.traduzir_construcao(dano)
            })

    return iniciativa, ataques


def extrair_ataques(ataques_texto, textos_extras=None):
    iniciativa = 0
    ataques = []
    if ataques_texto:
        iniciativa, ataques = _parse_ataques_texto(normalizar_texto_dc(ataques_texto))
    if not ataques:
        for ex in (textos_extras or []):
            if not ex:
                continue
            norm = normalizar_texto_dc(ex)
            bloco = _extrair_bloco_secao(norm, r"\b(?:Offense|Initiative)\b", r"\b(?:Defense|Power Points)\b")
            if bloco:
                ini2, atq2 = _parse_ataques_texto(bloco)
                if atq2:
                    return (ini2 or iniciativa), atq2
                if ini2 and not iniciativa:
                    iniciativa = ini2
    return iniciativa, ataques


def formatar_linhas_poderes(texto, custo_total_poderes=None):
    if not texto or custo_total_poderes == 0:
        return []
    txt = normalizar_texto_dc(texto)
    itens_brutos = _dividir_por_custo(txt)
    linhas = []
    for item in itens_brutos:
        m = re.match(r"^(.*?Array\s*\([^)]+\))\s*•\s*(.*)$", item, re.IGNORECASE)
        if m:
            linhas.append(t.traduzir_construcao(m.group(1).strip()))
            linhas.append("• " + t.traduzir_construcao(m.group(2).strip()))
        else:
            linhas.append(t.traduzir_construcao(item.strip()))
    return linhas


def extrair_complicacoes(comp_texto):
    if not comp_texto:
        return []
    txt = normalizar_texto_dc(comp_texto)
    complicacoes = []
    partes = re.split(r"(?<=[.!?])\s*(?=[A-Z][A-Za-z\s\-]+:)", txt.strip())
    for p in partes:
        if ":" in p:
            tit, texto = p.split(":", 1)
            tit_pt = {
                "Motivation": "Motivação", "Responsibility": "Responsabilidade", "Enemy": "Inimigo",
                "Enemies": "Inimigos", "Madness": "Loucura", "Obsession": "Obsessão", "Relationship": "Relacionamento",
                "Relationships": "Relacionamentos", "Secret Identity": "Identidade Secreta", "Secret": "Segredo",
                "Weakness": "Fraqueza", "Quirk": "Peculiaridade", "Prejudice": "Preconceito", "Temper": "Temperamento",
                "Phobia": "Fobia", "Rivalry": "Rivalidade", "Accident": "Acidente", "Honor": "Honra",
                "Power Loss": "Perda de Poder", "Reputation": "Reputação", "Addiction": "Vício",
                "Disability": "Deficiência", "Hatred": "Ódio", "Greed": "Ganância", "Trademark": "Marca Registrada"
            }.get(tit.strip(), tit.strip())
            complicacoes.append({"titulo": tit_pt, "texto": t.traduzir_construcao(texto.strip())})
        else:
            complicacoes.append({"titulo": "Complicação", "texto": t.traduzir_construcao(p.strip())})
    return complicacoes


def converter_ficha_dc(caminho_json):
    caminho = Path(caminho_json)
    pub = json.loads(caminho.read_text(encoding="utf-8"))
    ficha_pub = pub.get("ficha_publicada", {})
    slug = caminho.stem

    nome_pt = NOMES_DC_PT.get(slug, pub.get("nome_pt") or pub.get("nome"))
    pagina_pdf = pub.get("fonte", {}).get("pagina_pdf", 0)
    pagina_livro = max(1, pagina_pdf - 4) if pagina_pdf else 1

    habilidades = extrair_habilidades(ficha_pub)
    extras_ataques = [ficha_pub.get("pericias", ""), ficha_pub.get("defesas", ""), ficha_pub.get("equipamento", "")]
    extras_defesas = [ficha_pub.get("ataques", ""), ficha_pub.get("pericias", ""), ficha_pub.get("pontos_poder", "")]
    extras_custos = [ficha_pub.get("defesas", ""), ficha_pub.get("pericias", ""), ficha_pub.get("ataques", "")]

    defesas, obs_defesas = extrair_defesas(ficha_pub.get("defesas", ""), textos_extras=extras_defesas)
    custos, total_pp = extrair_custos(
        ficha_pub.get("pontos_poder", ""),
        pub.get("pontos_poder_publicados", 0),
        textos_extras=extras_custos,
    )
    vantagens = extrair_vantagens(ficha_pub.get("vantagens", ""))
    pericias = extrair_pericias(ficha_pub.get("pericias", ""))
    iniciativa, ataques = extrair_ataques(ficha_pub.get("ataques", ""), textos_extras=extras_ataques)
    
    custo_pod = custos.get("Poderes")
    poderes = formatar_linhas_poderes(ficha_pub.get("poderes", ""), custo_pod)
    equipamento = formatar_linhas_poderes(ficha_pub.get("equipamento", ""))
    complicacoes = extrair_complicacoes(ficha_pub.get("complicacoes", ""))

    traduzida = {
        "nome_pt": nome_pt,
        "conferida_em": "2026-11-02",
        "pagina_do_livro": pagina_livro,
        "ficha": {
            "habilidades": habilidades,
            "poderes": poderes,
            "equipamento": equipamento,
            "vantagens": vantagens,
            "pericias": pericias,
            "iniciativa": iniciativa,
            "ataques": ataques,
            "defesas": defesas,
            "observacao_defesas": obs_defesas,
            "custos": custos,
            "total": total_pp,
            "complicacoes": complicacoes,
        },
        "notas": [
            f"Ficha adaptada e traduzida automaticamente a partir de {pub.get('fonte', {}).get('arquivo', 'DC Adventures')}."
        ]
    }
    return traduzida


def salvar_traducao(caminho_json, destino_raiz=None, sobrescrever=False):
    caminho = Path(caminho_json)
    vol = caminho.parent.name
    slug = caminho.stem

    if slug in FICHAS_PROTEGIDAS:
        return None

    destino_dir = (destino_raiz or PASTA_TRADUCOES) / vol
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino_arq = destino_dir / f"{slug}.json"

    if destino_arq.is_file() and not sobrescrever:
        return None

    trad = converter_ficha_dc(caminho)
    destino_arq.write_text(json.dumps(trad, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destino_arq


def main():
    parser = argparse.ArgumentParser(description="Traduz fichas da DC para a pasta de traduções.")
    parser.add_argument("--populares", action="store_true", help="Gera tradução para os 43 heróis e vilões mais populares da DC")
    parser.add_argument("--personagem", type=str, help="Gera tradução para um personagem específico (slug)")
    parser.add_argument("--todos", action="store_true", help="Gera tradução para todas as fichas não protegidas")
    parser.add_argument("--sobrescrever", action="store_true", help="Sobrescreve traduções existentes (exceto fichas protegidas)")
    args = parser.parse_args()

    dc_files = {p.stem: p for p in PASTA_DC.glob("volume*/*.json")}

    if args.personagem:
        slug = args.personagem
        if slug not in dc_files:
            print(f"Personagem '{slug}' não encontrado em {PASTA_DC}")
            return
        arq = salvar_traducao(dc_files[slug], sobrescrever=args.sobrescrever)
        if arq:
            print(f"Salvo: {arq}")
        else:
            print(f"Pulado (protegido ou já existente): {slug}")
        return

    if args.populares:
        total = 0
        for slug in NOMES_DC_PT:
            if slug in dc_files:
                arq = salvar_traducao(dc_files[slug], sobrescrever=args.sobrescrever)
                if arq:
                    total += 1
                    print(f"Traduzido [{total}]: {slug} -> {NOMES_DC_PT[slug]}")
                else:
                    print(f"Ignorado (protegido ou existente): {slug}")
        print(f"\nTotal de fichas DC populares geradas: {total}")
        return

    if args.todos:
        total = 0
        for p in sorted(PASTA_DC.glob("volume*/*.json")):
            if p.stem not in FICHAS_PROTEGIDAS:
                arq = salvar_traducao(p, sobrescrever=args.sobrescrever)
                if arq:
                    total += 1
        print(f"\nTotal de fichas DC traduzidas: {total}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
