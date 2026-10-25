"""Gera a ficha editável em PDF de uma criatura do Bestiário (dados/generos/bestiario)."""

import json
import textwrap
import unicodedata
from pathlib import Path

from . import bestiario, pdf_export, rules
from .pdf_export import CAMPO_DA_HABILIDADE, LINHAS, LINHAS_ESPECIALIZADAS, PREFIXO_DA_PERICIA, _preencher_linhas


def _compativel_com_a_fonte(texto):
    """A fonte do PDF só aceita Latin-1/Windows-1252: troca ≤, ≥ e descarta caracteres sem mapa."""
    texto = str(texto or "").replace("≤", "<=").replace("≥", ">=").replace("→", "->")
    return "".join(c if c.encode("cp1252", "ignore") else
                   unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode() for c in texto)


def campos_da_criatura(criatura_id):
    """Mapeia os campos da criatura para o formulário da ficha editável PDF."""
    entrada = bestiario._catalogo().get(criatura_id)
    if entrada is None:
        return None
    caminho, resumo = entrada
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    f = dados.get("ficha", {})
    hab = f.get("habilidades", {})

    campos = {
        "Herói": dados.get("nome", ""),
        "Identidade": f"{dados.get('tipo', '')} ({dados.get('papel', '')})",
        "Gênero": "Fantasia / Bestiário",
        "Idade": "",
        "Altura": dados.get("tamanho", "Médio"),
        "Peso": "",
        "Olhos": "",
        "Cabelos": "",
        "NP": str(dados.get("nivel_poder", "")),
        "Total": "",
        "Jogador": "Mestre (NPC)",
    }

    # Habilidades
    for sigla, campo in CAMPO_DA_HABILIDADE.items():
        v = hab.get(sigla, 0)
        campos[campo] = str(v) if v is not None else "—"

    # Defesas
    defs = f.get("defesas", {})
    pares = [
        ("Esquiva", "Agi", "Agi"),
        ("Aparar", "Lut", "Lut"),
        ("Fortitude", "Vig", "Vig"),
        ("Vontade", "Pro", "Pro"),
    ]
    for d_nome, h_sigla, campo_def in pares:
        total = defs.get(d_nome)
        if total is not None:
            base = hab.get(h_sigla, 0) or 0
            comprada = max(0, total - base)
            campos[f"{campo_def}Hab"] = str(base)
            campos[f"{campo_def}Def"] = str(comprada) if comprada else ""
            campos[f"{campo_def}Total"] = str(total)
            campos[campo_def] = str(total)

    if "Resistencia" in defs:
        campos["Resistência"] = str(defs["Resistencia"])
    elif "Resistência" in defs:
        campos["Resistência"] = str(defs["Resistência"])

    # Ataques
    notas = []
    ataques = f.get("ataques", [])
    for n, atk in enumerate(ataques[:LINHAS["ataques"]], start=1):
        nome = atk.get("nome", "")
        bonus = atk.get("bonus", 0)
        dano = atk.get("dano", 0)
        desc = atk.get("descricao", "")
        crit = atk.get("critico", 20)
        campos[f"Ataque {n}"] = f"{nome} {bonus:+d}" if isinstance(bonus, int) else nome
        campos[f"Dano {n}"] = str(dano)
        crit_txt = f"Crítico {crit}-20" if crit and crit < 20 else ""
        campos[f"Descrição {n}"] = f"{crit_txt}; {desc}".strip("; ") if (crit_txt or desc) else ""

    for atk in ataques[LINHAS["ataques"]:]:
        notas.append(f"Ataque: {atk.get('nome')} {atk.get('bonus', 0):+d}, Dano {atk.get('dano', 0)}")

    # Perícias
    pericias = f.get("pericias", {})
    usadas = {chave: 0 for chave in LINHAS_ESPECIALIZADAS}
    for nome, grad in sorted(pericias.items()):
        sigla = rules.habilidade_da_pericia(nome)
        base = rules.nome_base(nome)
        h_val = hab.get(sigla, 0) or 0
        total = h_val + grad
        if base in PREFIXO_DA_PERICIA:
            prefixo = PREFIXO_DA_PERICIA[base]
            campos[f"{prefixo}Hab"] = str(h_val)
            campos[f"{prefixo}Per"] = str(grad)
            campos[f"{prefixo}Total"] = str(total)
        elif base in LINHAS_ESPECIALIZADAS:
            campo_nome, prefixo, sufixo_outros, maximo = LINHAS_ESPECIALIZADAS[base]
            if usadas[base] < maximo:
                usadas[base] += 1
                n = usadas[base]
                campos[campo_nome.format(n=n)] = nome.split(":", 1)[1].strip() if ":" in nome else ""
                campos[f"{prefixo}Hab {n}"] = str(h_val)
                campos[f"{prefixo}Per {n}"] = str(grad)
                campos[f"{prefixo}Total {n}"] = str(total)
            else:
                notas.append(f"Perícia: {nome} {grad} ({total:+d})")

    # Vantagens
    _preencher_linhas(campos, "Vantagens {n}", f.get("vantagens", []), LINHAS["vantagens"])

    # Equipamento
    linhas_equip = []
    for item in f.get("equipamento", []):
        linhas_equip += textwrap.wrap(item, width=50, subsequent_indent="  ", break_long_words=False)
    _preencher_linhas(campos, "Equipamento {n}", linhas_equip, LINHAS["equipamento"])

    # Poderes
    linhas_poderes = []
    for p in f.get("poderes", []):
        nome = p.get("nome", "")
        cons = p.get("construcao", p.get("efeito", ""))
        texto = f"{nome}: {cons}" if nome and cons else (nome or cons)
        linhas_poderes += textwrap.wrap(texto, width=62, subsequent_indent="  ", break_long_words=False)
    _preencher_linhas(campos, "Poderes e Dispositivos {n}", linhas_poderes, LINHAS["poderes"])

    # Notas & Táticas
    condicoes = [f"Bestiário Fantasia — Fonte: {dados.get('fonte', '')}"]
    if dados.get("descricao"):
        condicoes.append(f"Descrição: {dados['descricao']}")
    if dados.get("tatica"):
        condicoes.append(f"Tática: {dados['tatica']}")
    if dados.get("ambientes"):
        condicoes.append(f"Ambientes: {', '.join(dados['ambientes'])}")

    campos["Notas & Condições"] = "\n\n".join(condicoes + notas)

    return {k: _compativel_com_a_fonte(v) for k, v in campos.items()}


def gerar_pdf(caminho_modelo, criatura_id):
    """Gera os bytes do PDF preenchido da criatura."""
    campos = campos_da_criatura(criatura_id)
    if campos is None:
        return None
    return pdf_export.preencher_modelo(caminho_modelo, campos)
