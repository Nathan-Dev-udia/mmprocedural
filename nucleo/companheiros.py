"""Companheiros (pets): fichas de animais que um personagem pode ter.

Cada companheiro é um JSON em dados/comum/companheiros/, no formato de ficha que o validador entende
(habilidades base, defesas compradas, graduações de perícia, poderes com custo). Assim o programa calcula os
valores, o custo em PP e os limites do NP, em vez de copiar os números de um livro.

O bloco "livro" de cada arquivo guarda os valores impressos na fonte (Guia do Mestre de Jogo), para o teste
conferir a conta.

Tamanho (livro básico, efeitos Crescimento e Encolhimento): as habilidades de "ficha.habilidades" são as base;
os efeitos do tamanho entram como ajustes do poder, calculados aqui.
"""

import json
import math
from functools import lru_cache
from pathlib import Path

from . import validator

PASTA = Path(__file__).resolve().parent.parent / "dados" / "comum" / "companheiros"

# Livro básico, vantagens Parceiro (p. 85) e Capanga (p. 81): PP de ficha por graduação da vantagem.
PONTOS_POR_GRADUACAO = {"parceiro": 5, "capanga": 15}


def efeitos_de_tamanho(efeito, graduacao):
    """Ajustes de Crescimento ou Encolhimento (livro básico), para o validador.

    Crescimento: +1 For e Vig por graduação; –1 Esquiva e Aparar a cada 2 (arredondado para cima);
    +1 Intimidação a cada 2; –1 Furtividade por graduação.
    Encolhimento: –1 For a cada 4 graduações; +1 Esquiva e Aparar a cada 2 (arredondado para baixo);
    –1 Intimidação a cada 2; +1 Furtividade por graduação.
    Devolve (ajustes, circunstancias).
    """
    if efeito == "Crescimento":
        defesa = -math.ceil(graduacao / 2)
        ajustes = {"For": graduacao, "Vig": graduacao, "Esquiva": defesa, "Aparar": defesa}
        circunstancias = {"Furtividade": -graduacao, "Intimidação": graduacao // 2}
    elif efeito == "Encolhimento":
        defesa = graduacao // 2
        ajustes = {"For": -(graduacao // 4), "Esquiva": defesa, "Aparar": defesa}
        circunstancias = {"Furtividade": graduacao, "Intimidação": -defesa}
    else:
        raise ValueError(f"Efeito de tamanho desconhecido: {efeito}")
    return ({k: v for k, v in ajustes.items() if v}, {k: v for k, v in circunstancias.items() if v})


@lru_cache(maxsize=1)
def _todos():
    companheiros = {}
    for caminho in sorted(PASTA.glob("*.json")):
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        companheiros[dados["id"]] = dados
    return companheiros


def lista(genero=None):
    """Companheiros cadastrados, opcionalmente só os de um gênero."""
    return [c for c in _todos().values() if genero is None or genero in c.get("generos", [])]


def carregar(companheiro_id):
    try:
        return _todos()[companheiro_id]
    except KeyError:
        raise KeyError(f"Companheiro '{companheiro_id}' não existe.") from None


def barda_do_equipamento(ids, catalogo):
    """A barda (armadura da montaria) de maior Proteção entre os itens do dono, ou None."""
    bardas = [catalogo[i] for i in ids if catalogo.get(i, {}).get("protecao_da_montaria")]
    return max(bardas, key=lambda i: i["protecao_da_montaria"], default=None)


def _catalogo_da_barda(barda):
    """Catálogo de um item só, para o validador somar a Proteção da barda na Resistência do animal."""
    return {barda["id"]: {"id": barda["id"], "nome": barda["nome"], "protecao": barda["protecao_da_montaria"]}}


def ficha(companheiro, barda=None):
    """Converte o JSON do companheiro na ficha que o validador entende (com a barda, se o dono tem uma)."""
    base = companheiro["ficha"]
    poderes = {}
    for poder in base.get("poderes", []):
        ajustes, circunstancias = dict(poder.get("ajustes", {})), {}
        if poder.get("tamanho"):
            ajustes, circunstancias = efeitos_de_tamanho(poder["tamanho"]["efeito"], poder["tamanho"]["graduacao"])
        poderes[poder["id"]] = {"nome": poder["nome"], "nome_curto": poder["nome"].split(" (")[0],
                                "custo_informado": poder["custo"], "ajustes": ajustes,
                                "circunstancias": circunstancias}
    return {
        "habilidades": dict(base["habilidades"]),
        "defesas_compradas": dict(base.get("defesas_compradas", {})),
        "pericias": dict(base.get("pericias", {})),
        "vantagens": dict(base.get("vantagens", {})),
        "poderes": poderes,
        "equipamento": [barda["id"]] if barda else [],
        "ataques_naturais": [dict(a) for a in base.get("ataques_naturais", [])],
        "fontes": [{"nome": companheiro["fonte"], "status_dados": "livro"}],
    }


def relatorio(companheiro, barda=None):
    """Relatório do validador (valores, custos, limites) no NP do companheiro."""
    return validator.validar(ficha(companheiro, barda), companheiro["nivel_poder"],
                             _catalogo_da_barda(barda) if barda else {})


def graduacao_da_vantagem(total_pp, vantagem):
    """Graduações de Parceiro ou Capanga para ter um companheiro de total_pp pontos (arredonda para cima)."""
    return max(1, math.ceil(total_pp / PONTOS_POR_GRADUACAO[vantagem]))


def item_de_compra(companheiro, genero_id):
    """Id do item de equipamento que representa a compra deste animal no gênero (None se não se compra lá)."""
    return (companheiro.get("compra") or {}).get(genero_id)


def disponiveis(dados):
    """Companheiros que o jogador pode comprar neste gênero (o item existe no equipamento e tem preço)."""
    genero_id = dados["genero"]["id"]
    catalogo = dados["equipamentos"]
    saida = []
    for c in _todos().values():
        item = catalogo.get(item_de_compra(c, genero_id) or "")
        if item and item.get("preco") is not None:
            saida.append({"id": c["id"], "nome": c["nome"], "np": c["nivel_poder"], "descricao": c["descricao"],
                          "item": item["id"], "preco": item["preco"]})
    return saida


def bloco(companheiro, barda=None):
    """A ficha do companheiro pronta para exibir (PDF, DOCX, TXT e tela), calculada pelo validador.

    barda: item do catálogo (com "protecao_da_montaria") que o dono comprou; soma na Resistência do animal.
    """
    rel = relatorio(companheiro, barda)
    valores = rel["valores"]
    ordem = ["Esquiva", "Aparar", "Fortitude", "Resistência", "Vontade"]
    return {
        "id": companheiro["id"],
        "nome": companheiro["nome"],
        "np": companheiro["nivel_poder"],
        "descricao": companheiro["descricao"],
        "fonte": companheiro["fonte"],
        "habilidades": dict(valores["habilidades"]),
        "defesas": {d: valores["defesas"][d] for d in ordem},
        "iniciativa": valores["iniciativa"],
        # Só as perícias treinadas: o tamanho também muda Furtividade e Intimidação, mas isso já está no total.
        "pericias": [{"nome": n, "graduacoes": p["graduacoes"], "total": p["total"]}
                     for n, p in valores["pericias"].items() if p["graduacoes"]],
        "ataques": [{"nome": a["nome"], "bonus": a["bonus"], "dano": a["dano"], "critico": a["critico"]}
                    for a in valores["ataques"]],
        "poderes": [{"nome": p["nome"], "custo": p["custo"], "explicacao": explicacao_do_poder(p)}
                    for p in companheiro["ficha"].get("poderes", [])],
        "vantagens": [{"nome": v, "explicacao": _efeito_da_vantagem(v)} for v in companheiro["ficha"].get("vantagens", {})],
        "equipamento": ([{"nome": barda["nome"],
                          "explicacao": f"Proteção {barda['protecao_da_montaria']}, já somada na Resistência."}]
                        if barda else []),
        "total_pp": rel["total_pp"],
    }


NOMES_DOS_AJUSTES = {"For": "Força", "Vig": "Vigor"}


def explicacao_do_poder(poder):
    """O que o poder faz na mesa. O tamanho (Crescimento, Encolhimento) se explica pela conta do livro básico."""
    if not poder.get("tamanho"):
        return poder.get("explicacao", "")
    efeito, graduacao = poder["tamanho"]["efeito"], poder["tamanho"]["graduacao"]
    ajustes, circunstancias = efeitos_de_tamanho(efeito, graduacao)
    def lista(valores):
        return ", ".join(f"{NOMES_DOS_AJUSTES.get(k, k)} {v:+d}".replace("-", "–") for k, v in valores.items())
    porte = "Maior" if efeito == "Crescimento" else "Menor"
    texto = f"{porte} que uma pessoa, o tempo todo. Já somado na ficha: {lista(ajustes)}."
    return texto + (f" Perícias: {lista(circunstancias)} (já somado nas perícias que a ficha lista)."
                    if circunstancias else "")


@lru_cache(maxsize=1)
def _vantagens():
    caminho = PASTA.parent / "vantagens.json"
    return {v["nome"]: v for v in json.loads(caminho.read_text(encoding="utf-8"))["vantagens"]}


def _efeito_da_vantagem(nome):
    info = _vantagens().get(nome) or _vantagens().get(nome.split(" (")[0]) or {}
    return info.get("efeito", "Veja o livro básico, cap. 5.")


def critico(ataque):
    """'20' ou '19–20', como a ficha mostra a margem de crítico."""
    return "20" if ataque["critico"] >= 20 else f"{ataque['critico']}–20"


def texto(b, posse=""):
    """O bloco do companheiro em texto simples (para o TXT)."""
    hab = " ".join(f"{h} {v:+d}" for h, v in b["habilidades"].items())
    defesas = ", ".join(f"{d} {v}" for d, v in b["defesas"].items())
    linhas = [f"COMPANHEIRO: {b['nome']} (NP {b['np']}){' · ' + posse if posse else ''}", b["descricao"],
              f"Habilidades: {hab}", f"Defesas: {defesas}; Iniciativa {b['iniciativa']:+d}"]
    if b["pericias"]:
        linhas.append("Perícias: " + ", ".join(f"{p['nome']} {p['total']:+d}" for p in b["pericias"]))
    if b["ataques"]:
        linhas.append("Ataques: " + ", ".join(
            f"{a['nome']} {a['bonus']:+d} (Dano {a['dano']}, crítico {critico(a)})" for a in b["ataques"]))
    for titulo, itens in (("Poderes", b["poderes"]), ("Vantagens", b["vantagens"]),
                          ("Equipamento", b.get("equipamento", []))):
        if itens:
            linhas.append(f"{titulo}:")
            linhas.extend(f"- {i['nome']}: {i['explicacao']}" if i["explicacao"] else f"- {i['nome']}" for i in itens)
    return "\n".join(linhas)


def custo_para_o_heroi(companheiro):
    """{"total": PP de ficha do pet, "parceiro": PP do herói, "capanga": PP do herói}."""
    total = relatorio(companheiro)["total_pp"]
    return {"total": total, "parceiro": graduacao_da_vantagem(total, "parceiro"),
            "capanga": graduacao_da_vantagem(total, "capanga")}
