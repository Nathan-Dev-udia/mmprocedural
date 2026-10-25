"""Preenche a ficha editável (PDF) com uma ficha pronta de herói conhecido (dados/generos/herois).

Diferente do NPC gerado, a ficha publicada não passa pelo validador: os números dos livros vão para a ficha como estão
e a diferença entre o total e a base (habilidade + graduações) cai em "Outros". As da Marvel já vêm em campos
separados; as da DC, em texto corrido em inglês, que é separado aqui. Nomes de poderes e vantagens ficam como no livro.
"""

import json
import re
import textwrap
import unicodedata

from . import herois, pdf_export, rules
from .pdf_export import CAMPO_DA_HABILIDADE, LINHAS, LINHAS_ESPECIALIZADAS, PREFIXO_DA_PERICIA, _preencher_linhas

TRADUCAO_DE_PERICIAS_DC = {
    "Acrobatics": "Acrobacia", "Athletics": "Atletismo", "Deception": "Enganação", "Stealth": "Furtividade",
    "Intimidation": "Intimidação", "Insight": "Intuição", "Investigation": "Investigação",
    "Perception": "Percepção", "Persuasion": "Persuasão", "Sleight of Hand": "Prestidigitação",
    "Technology": "Tecnologia", "Treatment": "Tratamento", "Vehicles": "Veículos",
    "Close Combat": "Combate Corpo-a-Corpo", "Ranged Combat": "Combate à Distância", "Expertise": "Especialidade",
}
DEFESAS_DC = {"Dodge": "Esquiva", "Parry": "Aparar", "Fortitude": "Fortitude", "Toughness": "Resistência",
              "Will": "Vontade"}
CUSTOS_DC = {"Abilities": "Habilidades", "Powers": "Poderes", "Advantages": "Vantagens", "Skills": "Perícias",
             "Defenses": "Defesas"}
CUSTOS_MARVEL = {"habilidades_base": "Habilidades", "habilidades": "Habilidades", "poderes": "Poderes", "vantagens": "Vantagens",
                 "pericias": "Perícias", "defesas": "Defesas"}
SINAL_MENOS = str.maketrans("–—−", "---")


def _chave(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", sem_acento.lower())


_PERICIA_PELO_NOME = {_chave(nome): nome for nome in rules.PERICIAS}


def _inteiro(texto, padrao=0):
    achado = re.search(r"-?\d+", str(texto).translate(SINAL_MENOS))
    return int(achado.group()) if achado else padrao


def _separar_por_virgula(texto):
    """Separa por vírgulas fora de parênteses."""
    return [p.strip() for p in re.split(r",\s*(?![^()]*\))", texto) if p.strip()]


def _nome_da_pericia(nome):
    """'Intuicao' -> 'Intuição'; 'Expertise: Magic' -> 'Especialidade: Magic'; None se não for perícia."""
    base, _, especialidade = nome.partition(":")
    base = _PERICIA_PELO_NOME.get(_chave(TRADUCAO_DE_PERICIAS_DC.get(base.strip(), base)))
    if base is None:
        return None
    return f"{base}: {especialidade.strip()}" if especialidade.strip() else base


# ---------------------------------------------------------------- leitura dos dois formatos

def _ler_marvel(dados):
    f = dados["ficha"]
    pericias = {}
    for nome, graduacoes in f.get("pericias", {}).items():
        if (limpo := _nome_da_pericia(nome)):
            pericias[limpo] = {"grad": graduacoes, "total": None}
    return {
        "habilidades": {k: _inteiro(v) for k, v in f.get("habilidades", {}).items()},
        "defesas": {"Resistência" if k == "Resistencia" else k: v for k, v in f.get("defesas", {}).items()
                    if isinstance(v, int)},
        "pericias": pericias,
        "ataques": [(a["nome"], a.get("bonus"), a.get("dano"), "") for a in f.get("ataques", [])],
        "vantagens": list(f.get("vantagens", [])),
        "poderes": [f"{p.get('nome_pt') or p['nome']}: {p.get('construcao_3e', '')}".strip() for p in f.get("poderes", [])],
        "equipamento": list(f.get("equipamento", [])), "complicacoes": list(f.get("complicacoes", [])),
        "iniciativa": None,
        "custos": {rotulo: valor for chave, rotulo in CUSTOS_MARVEL.items()
                   if (valor := dados.get("custos_3e", {}).get(chave)) is not None},
        "total": dados.get("pontos_poder_3e"), "notas": list(dados.get("notas_conversao", [])),
        "serie": "Marvel", "np": dados.get("nivel_poder"), "detalhes_complicacoes": "",
    }


# A extração do PDF da DC separa a letra capitular ("d odge 10 f or titude 12"): estas palavras são religadas
# antes de ler os campos de defesas, ataques, perícias e pontos.
_PALAVRAS_DC = ["Dodge", "Parry", "Fortitude", "Toughness", "Will", "Initiative", "Damage", "Close", "Ranged", "Crit",
                "Abilities", "Skills", "Powers", "Defenses", "Advantages", "Total", "Expertise", "Combat",
                *TRADUCAO_DE_PERICIAS_DC]
_RELIGAR = [(re.compile(r"(?<![A-Za-z])" + r"\s+".join(r"\s?".join(palavra) for palavra in nome.split()) + r"(?![a-z])",
                        re.IGNORECASE), nome) for nome in sorted(set(_PALAVRAS_DC), key=len, reverse=True)]


def _religar(texto):
    for padrao, nome in _RELIGAR:
        texto = padrao.sub(nome, texto)
    return texto


def _ataques_dc(texto):
    """Dois formatos: 'Unarmed +11 Close, Damage 11, Crit. 19-20' (Vol. I) e 'Unarmed +8 (Close, Damage 1)'."""
    ataques = []
    for nome, bonus, detalhe in re.findall(r"([A-Za-z][^+,()]*?)\s+\+(\d+)\s*(\([^)]*\)|[^+]*?Damage\s+\d+(?:,\s*Crit\.\s*\d+-\d+)?)",
                                          texto):
        dano = re.search(r"Damage\s+(\d+)", detalhe)
        if not dano:
            continue
        tipo = "À distância" if "Ranged" in detalhe else "Corpo a corpo" if "Close" in detalhe else ""
        critico = re.search(r"Crit\.\s*(\d+-\d+)", detalhe)
        descricao = ", ".join(filter(None, [tipo, f"crítico {critico.group(1)}" if critico else ""]))
        ataques.append((re.sub(r"^Damaging\s+", "", nome.strip()), int(bonus), dano.group(1), descricao))
    return ataques


def _ler_dc(dados):
    f = {k: _religar(v) if k in ("defesas", "ataques", "pericias", "pontos_poder") else v
         for k, v in dados["ficha_publicada"].items()}
    pericias = {}
    for item in _separar_por_virgula(f.get("pericias", "").translate(SINAL_MENOS)):
        achado = re.match(r"^(.*?)\s+(-?\d+)\s*\(([^)]*)\)", item)
        nome = _nome_da_pericia(achado.group(1)) if achado else None
        if nome:
            pericias[nome] = {"grad": int(achado.group(2)), "total": _inteiro(achado.group(3))}
    defesas = {DEFESAS_DC[r]: int(v) for r, v in re.findall(r"(Dodge|Parry|Fortitude|Toughness|Will)\s+(\d+)",
                                                            f.get("defesas", ""))}
    texto_ataques = f.get("ataques", "").translate(SINAL_MENOS)
    iniciativa = re.search(r"Initiative\s+([+-]?\d+)", texto_ataques)
    ataques = _ataques_dc(re.sub(r"Initiative\s+[+-]?\d+[\s,]*", "", texto_ataques))
    texto_custos = f.get("pontos_poder", "")
    custos = {CUSTOS_DC[nome]: int(valor) for nome, valor in re.findall(r"(\w+)\s+(\d+)", texto_custos)
              if nome in CUSTOS_DC}
    total = re.search(r"to\s*tal\s+(\d+)", texto_custos, re.IGNORECASE)
    complicacoes = f.get("complicacoes", "")
    return {
        "habilidades": {herois.HABILIDADES_DC.get(k, k): _inteiro(v) for k, v in f.get("habilidades", {}).items()},
        "defesas": defesas, "pericias": pericias, "ataques": ataques,
        "vantagens": _separar_por_virgula(f.get("vantagens", "")),
        "poderes": herois._dividir_por_custo(f["poderes"]) if f.get("poderes") else [],
        "equipamento": herois._dividir_por_custo(f["equipamento"]) if f.get("equipamento") else [],
        # Só os títulos ("Obsession", "Nemesis"...); o texto completo vai para as notas.
        "complicacoes": [m.group(1) for m in re.finditer(r"(?:^|(?<=[.!?] ))([A-Za-z][\w' /-]{2,30}):", complicacoes)],
        "iniciativa": int(iniciativa.group(1)) if iniciativa else None,
        "custos": custos, "total": int(total.group(1)) if total else dados.get("pontos_poder_publicados"),
        "notas": [f"Ataques (texto do livro): {f['ataques']}"] if f.get("ataques") else [], "serie": "DC", "np": dados.get("nivel_poder"), "detalhes_complicacoes": complicacoes,
    }


# ---------------------------------------------------------------- campos do PDF

def campos_do_heroi(ficha_id):
    """{nome do campo: valor} para preencher o modelo; None se o id não existir."""
    entrada = herois._catalogo().get(ficha_id)
    if entrada is None:
        return None
    caminho, resumo = entrada
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    h = (_ler_marvel if resumo["editora"] == "marvel" else _ler_dc)(dados)
    hab = {k: h["habilidades"].get(k, 0) for k in CAMPO_DA_HABILIDADE}
    campos = {"Herói": dados["nome"], "Series": h["serie"], "Nível de Poder": str(h["np"] or ""),
              "Grupo Afiliado": f"{h['serie']} {resumo['volume']}".strip()}
    for rotulo, valor in h["custos"].items():
        campos[rotulo] = "" if valor is None else str(valor)
    campos["Total"] = "" if h["total"] is None else str(h["total"])

    for sigla, campo in CAMPO_DA_HABILIDADE.items():
        campos[campo] = str(hab[sigla])
    iniciativa = h["iniciativa"]
    if iniciativa is None:
        iniciativa = hab["Agi"] + 4 * sum(_inteiro(v, 1) for v in h["vantagens"]
                                          if _chave(v).startswith(("improvedinitiative", "iniciativaaprimorada")))
    campos["Iniciativa"] = f"{iniciativa:+d}"

    for defesa, sigla in rules.DEFESAS_COMPRAVEIS.items():
        if defesa in h["defesas"]:
            outros = h["defesas"][defesa] - hab[sigla]
            campos[f"Grad.{defesa}"] = "0"
            campos[f"{defesa} Outros"] = str(outros) if outros else ""
            campos[defesa] = str(h["defesas"][defesa])
    if "Resistência" in h["defesas"]:
        outros = h["defesas"]["Resistência"] - hab["Vig"]
        campos["Resistência Outros"] = str(outros) if outros else ""
        campos["Resistência"] = str(h["defesas"]["Resistência"])

    notas = list(h["notas"])
    for n, (nome, bonus, dano, tipo) in enumerate(h["ataques"][:LINHAS["ataques"]], start=1):
        campos[f"Ataque {n}"] = f"{nome} {bonus:+d}" if isinstance(bonus, int) else nome
        campos[f"Dano {n}"] = str(dano)
        campos[f"Descrição {n}"] = tipo
    for nome, bonus, dano, _ in h["ataques"][LINHAS["ataques"]:]:
        notas.append(f"Ataque: {nome} {bonus:+d}, Dano {dano}")

    _preencher_pericias(campos, h["pericias"], hab, notas)
    campos["Perícias Total"] = str(sum(p["grad"] for p in h["pericias"].values()))
    _preencher_linhas(campos, "Vantagens {n}", h["vantagens"], LINHAS["vantagens"])
    linhas_de_equipamento = []
    for item in h["equipamento"]:
        linhas_de_equipamento += textwrap.wrap(item, width=50, subsequent_indent="  ", break_long_words=False)
    _preencher_linhas(campos, "Equipamento {n}", linhas_de_equipamento, LINHAS["equipamento"])
    _preencher_linhas(campos, "Complicações {n}", h["complicacoes"], LINHAS["complicacoes"])
    linhas_de_poderes = []
    for poder in h["poderes"]:
        linhas_de_poderes += textwrap.wrap(poder, width=62, subsequent_indent="  ", break_long_words=False,
                                           break_on_hyphens=False)
    _preencher_linhas(campos, "Poderes e Dispositivos {n}", linhas_de_poderes, LINHAS["poderes"])

    condicoes = [f"Ficha publicada ({herois.FONTE_DA_EDITORA[resumo['editora']]}); valores conforme o livro."]
    if h["detalhes_complicacoes"]:
        condicoes.append(f"Complicações: {h['detalhes_complicacoes']}")
    campos["Notas & Condições"] = "\n".join(condicoes + notas)
    return campos


def _preencher_pericias(campos, pericias, hab, notas):
    usadas = {chave: 0 for chave in LINHAS_ESPECIALIZADAS}
    for nome, p in sorted(pericias.items()):
        sigla = rules.habilidade_da_pericia(nome)
        base = rules.nome_base(nome)
        total = p["total"] if p["total"] is not None else hab[sigla] + p["grad"]
        if base in PREFIXO_DA_PERICIA:
            prefixo = PREFIXO_DA_PERICIA[base]
            outros = total - hab[sigla] - p["grad"]
            campos[f"{prefixo}Hab"] = str(hab[sigla])
            campos[f"{prefixo}Per"] = str(p["grad"])
            campos[f"{prefixo}Outros"] = str(outros) if outros else ""
            campos[f"{prefixo}Total"] = str(total)
            continue
        campo_nome, prefixo, sufixo_outros, maximo = LINHAS_ESPECIALIZADAS[base]
        if usadas[base] == maximo:
            notas.append(f"Perícia: {nome} {p['grad']} ({total:+d})")
            continue
        usadas[base] += 1
        n = usadas[base]
        padrao = hab[pdf_export.HABILIDADE_PADRAO_DA_LINHA[base]]
        outros = total - padrao - p["grad"]
        campos[campo_nome.format(n=n)] = nome.split(":", 1)[1].strip() if ":" in nome else ""
        campos[f"{prefixo}Hab {n}"] = str(padrao)
        campos[f"{prefixo}Per {n}"] = str(p["grad"])
        campos[f"{prefixo}{sufixo_outros} {n}"] = str(outros) if outros else ""
        campos[f"{prefixo}Total {n}"] = str(total)


def _compativel_com_a_fonte(texto):
    """A fonte do PDF só aceita Latin-1/Windows-1252: troca ≤, ≥ e afins e descarta o que não tem equivalente."""
    texto = texto.replace("≤", "<=").replace("≥", ">=").replace("→", "->")
    return "".join(c if c.encode("cp1252", "ignore") else
                   unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode() for c in texto)


def gerar_pdf(caminho_modelo, ficha_id):
    """Bytes do PDF preenchido; None se o id não existir."""
    campos = campos_do_heroi(ficha_id)
    if campos is None:
        return None
    return pdf_export.preencher_modelo(caminho_modelo, {k: _compativel_com_a_fonte(v) for k, v in campos.items()})
