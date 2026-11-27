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
# Livro Básico, efeito Invocar (p. 111): a criatura tem 15 PP por graduação.
PONTOS_POR_GRADUACAO_DE_INVOCAR = 15


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


def do_equipamento(ids, genero_id):
    """Os companheiros cujo item de compra está no equipamento (ids), na ordem dos itens e sem repetir.

    É assim que o animal comprado pelo kit ou em "Escolher" também ganha a página dele."""
    por_item = {item_de_compra(c, genero_id): c for c in _todos().values() if item_de_compra(c, genero_id)}
    vistos, saida = set(), []
    for i in ids:
        c = por_item.get(i)
        if c and c["id"] not in vistos:
            vistos.add(c["id"])
            saida.append(c)
    return saida


def barda_do_equipamento(ids, catalogo, companheiro=None):
    """A barda (armadura da montaria) de maior Proteção entre os itens do dono, ou None.

    Com companheiro, só vale para montaria ("montaria": true no JSON): a barda não serve no cão."""
    if companheiro is not None and not companheiro.get("montaria"):
        return None
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


def parceiros(genero_id):
    """Os animais que podem ser Parceiro neste gênero, com o custo em PP do herói (Livro Básico, p. 85-86).

    Não precisam estar à venda: o Parceiro se paga com pontos, não com dinheiro. O lobo do patrulheiro é um."""
    saida = []
    for c in lista(genero_id):
        if c.get("invocado"):
            continue                      # o elemental e os constructos vêm de poderes, não da vantagem
        total = relatorio(c)["total_pp"]
        graduacao = graduacao_da_vantagem(total, "parceiro")
        saida.append({"id": c["id"], "nome": c["nome"], "np": c["nivel_poder"], "descricao": c["descricao"],
                      "total_pp": total, "graduacao": graduacao})
    return saida


def invocado_do_poder(entrada, graduacao, np):
    """A criatura que um poder de Invocar traz (campo "companheiros" do powers.json), ou None.

    Vale a primeira da lista que cabe no NP do dono e nos 15 PP por graduação do Invocar: o Mestre das feras
    tem o lobo (NP 3) e, no NP 2, o cão."""
    teto = PONTOS_POR_GRADUACAO_DE_INVOCAR * (graduacao or 0)
    for companheiro_id in entrada.get("companheiros", []):
        c = carregar(companheiro_id)
        if c["nivel_poder"] <= np and relatorio(c)["total_pp"] <= teto:
            return c
    return None


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


# Como cada forma de ter o bicho funciona na mesa (Livro Básico): vai na ficha, junto da descrição.
REGRAS_POR_TIPO = {
    "comprado": "Animal comprado: é do mestre e obedece ao dono com Comandar (ação de movimento). Não evolui.",
    "parceiro": "Parceiro (vantagem, Livro Básico p. 85): personagem completo, leal ao dono, que costuma comandá-lo "
                "(ação de movimento). Não é capanga e não tem pontos heroicos (o dono pode gastar os dele). Melhora "
                "quando o dono compra mais graduações de Parceiro (+5 PP de ficha cada).",
    "invocado": "Invocado (efeito Invocar, Livro Básico p. 111): aparece ao lado do dono com uma ação padrão e age "
                "na iniciativa dele a partir da rodada seguinte, tonto (só uma ação padrão por rodada). Heroico: não "
                "segue as regras de capanga. Incapacitado, some e só volta recuperado. Dar ordens é ação de movimento.",
}


def bloco(companheiro, barda=None, tipo="comprado"):
    """A ficha do companheiro pronta para exibir (PDF, DOCX, TXT e tela), calculada pelo validador.

    barda: item do catálogo (com "protecao_da_montaria") que o dono comprou; soma na Resistência do animal.
    tipo: "comprado", "parceiro" ou "invocado"; acrescenta a regra de mesa dessa forma de ter o bicho.
    """
    rel = relatorio(companheiro, barda)
    valores = rel["valores"]
    ordem = ["Esquiva", "Aparar", "Fortitude", "Resistência", "Vontade"]
    return {
        "id": companheiro["id"],
        "nome": companheiro["nome"],
        "np": companheiro["nivel_poder"],
        "descricao": companheiro["descricao"],
        "regra": REGRAS_POR_TIPO.get(tipo, ""),
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
              *([b["regra"]] if b.get("regra") else []),
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
