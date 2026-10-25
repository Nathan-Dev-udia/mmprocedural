"""Catálogo de heróis conhecidos (dados/generos/herois): fichas prontas da Marvel e da DC, só para consulta e download.

As fichas chegam em dois formatos: as da Marvel são conversões da 2ª para a 3ª edição, já em campos separados
(habilidades, defesas, poderes com a construção em 3e, notas de conversão); as da DC foram extraídas dos livros DC
Adventures e guardam o texto publicado, em inglês. Este módulo põe as duas num formato comum para a tela (resumo para a
lista e seções para a ficha) sem mexer nos arquivos.
"""

import json
import re
from functools import lru_cache
from pathlib import Path


PASTA = Path(__file__).parent.parent / "dados" / "generos" / "herois"

EDITORAS = {"marvel": "Marvel", "dc": "DC"}

FONTE_DA_EDITORA = {"marvel": "Marvel Files (M&M 2ª edição), convertida para a 3ª edição",
                    "dc": "DC Adventures: Heroes and Villains (M&M 3ª edição)"}

VOLUMES_DC = {"volume1": "Vol. I", "volume2": "Vol. II"}

# Abreviações das habilidades nos livros em inglês da DC → as do projeto.
HABILIDADES_DC = {"STR": "For", "STA": "Vig", "AGL": "Agi", "DEX": "Des", "FGT": "Lut", "INT": "Int", "AWE": "Pro",
                  "PRE": "Pre"}

TITULOS_DC = {"poderes": "Poderes", "equipamento": "Equipamento", "vantagens": "Vantagens", "pericias": "Perícias",
              "ataques": "Ataques", "defesas": "Defesas", "pontos_poder": "Pontos de poder",
              "complicacoes": "Complicações"}

# "Flight 7 (250 MPH) • 11 points Rannian Eyes: ..." → um poder por item, com o custo no fim.
_CUSTO_DC = re.compile(r"\s*•\s*(-?\d+)\s*points?\b\s*", re.IGNORECASE)


def _dividir_por_custo(texto):
    partes = _CUSTO_DC.split(texto)
    itens = []
    for i in range(0, len(partes) - 1, 2):
        if partes[i].strip():
            itens.append(f"{partes[i].strip()} ({partes[i + 1]} PP)")
    if len(partes) % 2 and partes[-1].strip():
        itens.append(partes[-1].strip())
    return itens or [texto]


def _nomes_dos_poderes_dc(texto):
    return [item.split(":")[0].strip() for item in _dividir_por_custo(texto) if ":" in item]


def _resumo_marvel(caminho, dados):
    return {"id": f"marvel/{caminho.stem}", "editora": "marvel", "nome": dados["nome"],
            "nome_pt": dados.get("nome_pt") if dados.get("nome_pt") != dados["nome"] else "",
            "np": dados.get("nivel_poder"), "pp": dados.get("pontos_poder_origem"), "pp_rotulo": "PP na 2ª edição",
            "volume": "", "termos": [t for p in dados["ficha"].get("poderes", []) for t in (p.get("nome"), p.get("nome_pt")) if t]}


def _resumo_dc(caminho, dados):
    return {"id": f"dc/{caminho.parent.name}/{caminho.stem}", "editora": "dc", "nome": dados["nome"],
            "nome_pt": dados.get("nome_pt") if dados.get("nome_pt") != dados["nome"] else "",
            "np": dados.get("nivel_poder"), "pp": dados.get("pontos_poder_publicados"), "pp_rotulo": "PP",
            "volume": VOLUMES_DC.get(caminho.parent.name, caminho.parent.name),
            # A página distingue versões do mesmo personagem (Tempest na p. 24 e na p. 185 do Vol. I).
            "pagina": dados.get("fonte", {}).get("pagina_pdf"),
            "termos": _nomes_dos_poderes_dc(dados["ficha_publicada"].get("poderes", ""))}


@lru_cache(maxsize=1)
def _catalogo():
    """{id: (caminho, resumo)} de todas as fichas, em ordem alfabética dentro de cada editora."""
    fichas = {}
    for caminho in sorted((PASTA / "marvel").glob("*.json")):
        fichas[f"marvel/{caminho.stem}"] = caminho
    for caminho in sorted((PASTA / "dc").glob("*/*.json")):
        fichas[f"dc/{caminho.parent.name}/{caminho.stem}"] = caminho
    catalogo = {}
    for ficha_id, caminho in fichas.items():
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        resumo = (_resumo_marvel if ficha_id.startswith("marvel/") else _resumo_dc)(caminho, dados)
        catalogo[ficha_id] = (caminho, resumo)
    return dict(sorted(catalogo.items(), key=lambda par: (par[1][1]["editora"], par[1][1]["nome"].lower())))


def lista():
    """Resumos de todas as fichas (para a lista e a busca da tela)."""
    return [resumo for _, resumo in _catalogo().values()]


def _texto_de(valor):
    if isinstance(valor, dict):
        return ", ".join(f"{k} {v}" for k, v in valor.items())
    if isinstance(valor, list):
        return "; ".join(_texto_de(v) for v in valor)
    return str(valor)


def _secoes_marvel(dados):
    ficha = dados["ficha"]
    poderes = [f"{p.get('nome_pt') or p['nome']}: {p.get('construcao_3e', '')}".strip() for p in ficha.get("poderes", [])]
    ataques = [f"{a['nome']} {a['bonus']:+d}, Dano {a['dano']}" if isinstance(a.get("bonus"), int)
               else _texto_de(a) for a in ficha.get("ataques", [])]
    secoes = [("Defesas", [_texto_de(ficha.get("defesas", {}))]),
              ("Ataques", ataques),
              ("Perícias", [f"{nome} {valor}" for nome, valor in ficha.get("pericias", {}).items()]),
              ("Vantagens", ficha.get("vantagens", [])),
              ("Poderes", poderes),
              ("Equipamento", ficha.get("equipamento", [])),
              ("Complicações", ficha.get("complicacoes", []))]
    for forma in ficha.get("formas_alternativas", []):
        secoes.append((f"Forma alternativa: {forma.get('nome', '')}",
                       [f"{campo}: {_texto_de(valor)}" for campo, valor in forma.items() if campo != "nome"]))
    if ficha.get("habilidades_base"):
        secoes.append(("Habilidades base", [_texto_de(ficha["habilidades_base"])]))
    secoes.append(("Notas de conversão", dados.get("notas_conversao", [])))
    return secoes


def _secoes_dc(dados):
    ficha = dados["ficha_publicada"]
    secoes = []
    for campo, titulo in TITULOS_DC.items():
        if ficha.get(campo):
            texto = ficha[campo]
            itens = _dividir_por_custo(texto) if campo in ("poderes", "equipamento") else [texto]
            secoes.append((titulo, itens))
    return secoes


def ficha(ficha_id):
    """Resumo, habilidades e seções de uma ficha, prontos para a tela; None se o id não existir."""
    entrada = _catalogo().get(ficha_id)
    if not entrada:
        return None
    arquivo, resumo = entrada
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    if resumo["editora"] == "marvel":
        habilidades = dados["ficha"].get("habilidades", {})
        secoes = _secoes_marvel(dados)
        pagina = dados.get("fonte", {}).get("pagina")
        status = "Conversão com ajustes de NP" if dados.get("status_conversao") == "convertida_com_ajustes_de_np" \
            else "Conversão"
    else:
        habilidades = {HABILIDADES_DC.get(k, k): v for k, v in dados["ficha_publicada"].get("habilidades", {}).items()}
        secoes = _secoes_dc(dados)
        pagina = dados.get("fonte", {}).get("pagina_pdf")
        status = "Ficha publicada (texto original em inglês)"
    fonte = FONTE_DA_EDITORA[resumo["editora"]] + (f", {resumo['volume']}" if resumo["volume"] else "") + \
        (f", p. {pagina} do PDF" if pagina else "")
    return {**resumo, "habilidades": habilidades, "fonte": fonte, "status": status,
            "secoes": [{"titulo": titulo, "itens": [str(i) for i in itens if str(i).strip()]}
                       for titulo, itens in secoes if itens]}
