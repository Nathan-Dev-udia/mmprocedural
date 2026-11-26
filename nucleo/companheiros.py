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


def ficha(companheiro):
    """Converte o JSON do companheiro na ficha que o validador entende."""
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
        "equipamento": [],
        "ataques_naturais": [dict(a) for a in base.get("ataques_naturais", [])],
        "fontes": [{"nome": companheiro["fonte"], "status_dados": "livro"}],
    }


def relatorio(companheiro):
    """Relatório do validador (valores, custos, limites) no NP do companheiro."""
    return validator.validar(ficha(companheiro), companheiro["nivel_poder"], {})


def graduacao_da_vantagem(total_pp, vantagem):
    """Graduações de Parceiro ou Capanga para ter um companheiro de total_pp pontos (arredonda para cima)."""
    return max(1, math.ceil(total_pp / PONTOS_POR_GRADUACAO[vantagem]))


def custo_para_o_heroi(companheiro):
    """{"total": PP de ficha do pet, "parceiro": PP do herói, "capanga": PP do herói}."""
    total = relatorio(companheiro)["total_pp"]
    return {"total": total, "parceiro": graduacao_da_vantagem(total, "parceiro"),
            "capanga": graduacao_da_vantagem(total, "capanga")}
