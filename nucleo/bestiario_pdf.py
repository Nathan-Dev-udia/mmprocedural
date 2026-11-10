"""Gera a ficha editável em PDF de uma criatura do Bestiário (dados/generos/bestiario)."""

import re
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


def campos_da_criatura(criatura_id, nome=None, np=None):
    """Mapeia os campos da criatura para o formulário da ficha editável PDF.

    `nome` troca o nome da ficha (ex.: "Carniçal 2" quando o mestre baixa várias cópias); `np` leva a criatura
    a outro NP (bestiario.no_np).
    """
    resultado = _campos_e_formulas(criatura_id, nome, np)
    return None if resultado is None else resultado[0]


def _campos_e_formulas(criatura_id, nome=None, np=None):
    """(campos, fórmulas a acrescentar no PDF) da criatura; None se ela não existir."""
    dados, resumo = bestiario.carregar(criatura_id, np)
    if dados is None:
        return None
    f = dados.get("ficha", {})
    hab = f.get("habilidades", {})

    genero_nome = resumo.get("genero_nome", "Bestiário") if resumo else "Bestiário"
    campos = {
        "Herói": nome or dados.get("nome", ""),
        "Identidade": f"{dados.get('tipo', '')} ({dados.get('papel', '')})",
        "Gênero": f"{genero_nome} / Bestiário",
        "Idade": "",
        "Altura": dados.get("tamanho", "Médio"),
        "Peso": "",
        "Olhos": "",
        "Cabelos": "",
        "Nível de Poder": str(dados.get("nivel_poder", "")),
        "Total": "",
        "Jogador": "Mestre (NPC)",
    }

    # Habilidades
    for sigla, campo in CAMPO_DA_HABILIDADE.items():
        v = hab.get(sigla, 0)
        campos[campo] = str(v) if v is not None else "—"

    # Defesas: habilidade + graduações (o que passa da habilidade) + outros (o que fica abaixo dela, como o
    # Crescimento tirando Esquiva e Aparar), para as fórmulas do PDF fecharem com o total da ficha.
    defs = f.get("defesas", {})
    for defesa, sigla in rules.DEFESAS_COMPRAVEIS.items():
        total = defs.get(defesa)
        if isinstance(total, str):
            # Defesa que a criatura não tem (Fortitude de morto-vivo sem Vigor): "Imune".
            campos[defesa] = total
        elif total is not None:
            diferenca = total - (hab.get(sigla) or 0)
            campos[f"Grad.{defesa}"] = str(max(diferenca, 0))
            campos[f"{defesa} Outros"] = str(min(diferenca, 0)) if diferenca < 0 else ""
            campos[defesa] = str(total)
    resistencia = defs.get("Resistencia", defs.get("Resistência"))
    if isinstance(resistencia, int):
        outros = resistencia - (hab.get("Vig") or 0)
        campos["Resistência Outros"] = str(outros) if outros else ""
        campos["Resistência"] = str(resistencia)
    elif resistencia is not None:
        campos["Resistência"] = str(resistencia)

    # Iniciativa: Agilidade + 4 por graduação de Iniciativa Aprimorada
    iniciativa = None
    if isinstance(hab.get("Agi"), int):
        graduacoes = 0
        for vantagem in f.get("vantagens", []):
            achou = re.fullmatch(rf"{rules.VANTAGEM_INICIATIVA}\s*(\d+)?", vantagem.strip())
            if achou:
                graduacoes += int(achou.group(1) or 1)
        iniciativa = hab["Agi"] + rules.INICIATIVA_POR_GRADUACAO * graduacoes
        campos["Iniciativa"] = f"{iniciativa:+d}"

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
    # A criatura não tem custo em PP: o Total fica em branco (a fórmula do modelo somaria só uma parte).
    formulas = {**pdf_export.formula_da_iniciativa(iniciativa, hab.get("Agi")), "Total": pdf_export.MANTER_O_VALOR}
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
                formulas.update(pdf_export.formula_da_linha_de_pericia(base, n, sigla))
            else:
                notas.append(f"Perícia: {nome} {grad} ({total:+d})")
    campos["Perícias Total"] = str(sum(pericias.values()))

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

    # Complicações
    linhas_complicacoes = []
    for complicacao in dados.get("complicacoes", []):
        linhas_complicacoes += textwrap.wrap(complicacao, width=62, subsequent_indent="  ", break_long_words=False)
    _preencher_linhas(campos, "Complicações {n}", linhas_complicacoes, LINHAS["complicacoes"])

    # Notas & Táticas
    condicoes = [f"Bestiário Fantasia — Fonte: {dados.get('fonte', '')}"]
    if dados.get("aviso_de_escala"):
        condicoes.append(dados["aviso_de_escala"])
    if dados.get("descricao"):
        condicoes.append(f"Descrição: {dados['descricao']}")
    if dados.get("tatica"):
        condicoes.append(f"Tática: {dados['tatica']}")
    if dados.get("ambientes"):
        condicoes.append(f"Ambientes: {', '.join(dados['ambientes'])}")

    campos["Notas & Condições"] = "\n\n".join(condicoes + notas)

    return {k: _compativel_com_a_fonte(v) for k, v in campos.items()}, formulas


def gerar_pdf(caminho_modelo, criatura_id, nome=None, np=None):
    """Gera os bytes do PDF preenchido da criatura."""
    resultado = _campos_e_formulas(criatura_id, nome, np)
    if resultado is None:
        return None
    campos, formulas = resultado
    dados, _ = bestiario.carregar(criatura_id, np)
    caminho_img = bestiario.arquivo_de_imagem(criatura_id, dados)
    return pdf_export.preencher_modelo(caminho_modelo, campos, caminho_imagem=caminho_img, formulas=formulas)
