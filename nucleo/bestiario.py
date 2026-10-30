"""Catálogo do Bestiário (dados/bestiario): fichas prontas de criaturas, feras e monstros por gênero.

Organiza as criaturas em gêneros (Fantasia, etc.), famílias (ex.: Goblin, Lobo, Esqueleto) e variantes
(ex.: Saqueador, Guerreiro, De Areia, Elétrico), com suporte a filtros por gênero, família, tipo, papel de
combate (Lacaio, Soldado, Bruto, Emboscador, Conjurador, Chefe) e faixa de NP, busca em tempo real e geração de PDF.
"""

import copy
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from . import rules


PASTA = Path(__file__).parent.parent / "dados" / "bestiario"

NOMES_DOS_GENEROS = {
    "fantasia": "Fantasia",
    "faroeste": "Faroeste",
    "cyberpunk": "Cyberpunk",
}


def papeis_de(papel):
    """'Bruto / Guardião (Solo)' -> ['Bruto', 'Guardião']: cada parte do papel vale como filtro."""
    return [parte.strip() for parte in re.sub(r"\(.*?\)", "", papel or "").split("/") if parte.strip()]


def e_chefe_pelo_papel(papel):
    """Fichas sem o campo "chefe": o papel decide ("Chefe / Líder", "Bruto (Solo)", "Líder / Soldado")."""
    return "Solo" in (papel or "") or any(p in ("Chefe", "Líder") for p in papeis_de(papel))


@lru_cache(maxsize=1)
def _catalogo():
    """Retorna {id: (caminho, resumo)} de todas as criaturas cadastradas."""
    catalogo = {}
    if not PASTA.is_dir():
        return catalogo

    # 1. Carrega todas as criaturas
    por_familia = defaultdict(list)
    dados_carregados = {}

    for caminho in sorted(PASTA.glob("*/*/*.json")):
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            genero = dados.get("genero") or caminho.parent.parent.name
            categoria = caminho.parent.name
            criatura_id = f"{genero}/{categoria}/{caminho.stem}"
            familia = dados.get("familia") or dados.get("subtipo") or dados.get("nome", caminho.stem)
            variante = dados.get("variante") or dados.get("nome", caminho.stem)
            padrao = bool(dados.get("padrao", False))
            chefe = bool(dados.get("chefe", e_chefe_pelo_papel(dados.get("papel", ""))))

            ficha = dados.get("ficha", {})
            termos = (
                [genero, NOMES_DOS_GENEROS.get(genero, genero), dados.get("tipo", ""),
                 dados.get("subtipo", ""), familia, variante, dados.get("papel", ""), dados.get("tamanho", "")]
                + dados.get("ambientes", [])
                + [p.get("nome", "") for p in ficha.get("poderes", [])]
                + [a.get("nome", "") for a in ficha.get("ataques", [])]
                + list(ficha.get("vantagens", []))
                + dados.get("complicacoes", [])
                + (["chefe"] if chefe else [])
            )

            resumo = {
                "id": criatura_id,
                "genero": genero,
                "genero_nome": NOMES_DOS_GENEROS.get(genero, genero.capitalize()),
                "categoria": categoria,
                "familia": familia,
                "variante": variante,
                "padrao": padrao,
                "nome": dados.get("nome", caminho.stem),
                "tipo": dados.get("tipo", "Monstro"),
                "subtipo": dados.get("subtipo", ""),
                "papel": dados.get("papel", "Monstro"),
                "papeis": papeis_de(dados.get("papel", "Monstro")),
                "chefe": chefe,
                "tamanho": dados.get("tamanho", "Médio"),
                "np": dados.get("nivel_poder", 1),
                "ambientes": dados.get("ambientes", []),
                "descricao": dados.get("descricao", ""),
                "termos": [t for t in termos if t],
            }

            dados_carregados[criatura_id] = (caminho, resumo)
            por_familia[(genero, familia)].append(resumo)
        except (json.JSONDecodeError, OSError):
            continue

    # 2. Vincula a lista de variantes em cada resumo
    for criatura_id, (caminho, resumo) in dados_carregados.items():
        genero = resumo["genero"]
        familia = resumo["familia"]
        parentes = por_familia.get((genero, familia), [])
        
        # Ordena variantes por NP e nome
        parentes_ordenados = sorted(parentes, key=lambda p: (p["np"], p["nome"]))
        resumo["total_variantes"] = len(parentes_ordenados)
        resumo["variantes"] = [
            {
                "id": p["id"],
                "nome": p["nome"],
                "variante": p["variante"],
                "np": p["np"],
                "papel": p["papel"],
                "padrao": p["padrao"],
                "chefe": p["chefe"],
            }
            for p in parentes_ordenados
        ]
        catalogo[criatura_id] = (caminho, resumo)

    return dict(sorted(catalogo.items(), key=lambda par: (
        par[1][1]["genero"],
        par[1][1]["tipo"],
        par[1][1]["familia"],
        0 if par[1][1]["padrao"] else 1,
        par[1][1]["np"],
        par[1][1]["nome"]
    )))


def limpar_cache():
    _catalogo.cache_clear()


def lista(genero=None):
    """Lista de resumos de criaturas (filtrando opcionalmente por gênero)."""
    todas = [resumo for _, resumo in _catalogo().values()]
    if genero and genero != "todos":
        return [r for r in todas if r["genero"] == genero]
    return todas


def generos():
    """Gêneros disponíveis no bestiário com as contagens."""
    todas = lista()
    contagem = {}
    for r in todas:
        g = r["genero"]
        contagem[g] = contagem.get(g, 0) + 1
    itens = [{"id": g, "nome": NOMES_DOS_GENEROS.get(g, g.capitalize()), "quantidade": c}
             for g, c in sorted(contagem.items())]
    return [{"id": "todos", "nome": "Todos os gêneros", "quantidade": len(todas)}] + itens


def tipos(genero=None):
    """Tipos de criaturas e contagem (filtrando opcionalmente por gênero)."""
    contagem = {}
    for r in lista(genero):
        t = r["tipo"]
        contagem[t] = contagem.get(t, 0) + 1
    return [{"id": t, "nome": t, "quantidade": c} for t, c in sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))]


def familias(genero=None):
    """Famílias de criaturas (ex.: Goblin, Hobgoblin, Lobo, Dragão)."""
    contagem = {}
    for r in lista(genero):
        f = r["familia"]
        contagem[f] = contagem.get(f, 0) + 1
    return [{"id": f, "nome": f, "quantidade": c} for f, c in sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))]


def papeis(genero=None):
    """Papéis de combate e contagem (filtrando opcionalmente por gênero). "Bruto / Chefe" conta nos dois."""
    contagem = {}
    for r in lista(genero):
        for p in r["papeis"]:
            contagem[p] = contagem.get(p, 0) + 1
    return [{"id": p, "nome": p, "quantidade": c} for p, c in sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))]


def faixas_np(genero=None):
    """Faixas de NP com contagem de criaturas."""
    faixas = [
        {"id": "todos", "nome": "Todos os NPs", "min": 0, "max": 99},
        {"id": "1-3", "nome": "NP 1–3 (Lacaios / Fracos)", "min": 1, "max": 3},
        {"id": "4-6", "nome": "NP 4–6 (Médios / Soldados)", "min": 4, "max": 6},
        {"id": "7-9", "nome": "NP 7–9 (Fortes / Bruxas)", "min": 7, "max": 9},
        {"id": "10+", "nome": "NP 10+ (Chefes / Dragões)", "min": 10, "max": 99},
    ]
    todas = lista(genero)
    for f in faixas:
        f["quantidade"] = sum(1 for r in todas if f["min"] <= (r.get("np") or 0) <= f["max"])
    return faixas


def chefes(genero=None):
    """Quantas criaturas servem de chefe (luta principal da sessão)."""
    return sum(1 for r in lista(genero) if r["chefe"])


def texto_das_pericias(ficha_da_criatura):
    """'Furtividade 6 (+8)': graduações e total (habilidade + graduações), como nas fichas de NPC."""
    habilidades = ficha_da_criatura.get("habilidades", {})
    textos = []
    for nome, graduacoes in ficha_da_criatura.get("pericias", {}).items():
        sigla = rules.habilidade_da_pericia(nome)
        if not isinstance(graduacoes, int) or sigla is None:
            textos.append(f"{nome} {graduacoes}")
            continue
        total = (habilidades.get(sigla) or 0) + graduacoes
        textos.append(f"{nome} {graduacoes} ({total:+d})")
    return textos


def _texto_de(valor):
    if isinstance(valor, dict):
        return ", ".join(f"{k} {'—' if v is None else v}" for k, v in valor.items())
    if isinstance(valor, list):
        return "; ".join(_texto_de(v) for v in valor)
    return str(valor)


# ------------------------------------------------------------------ escala de NP

NP_MINIMO, NP_MAXIMO = 1, 20

# Habilidades que acompanham o NP: combate, defesas ativas, Resistência e Vontade. Intelecto e Presença ficam.
HABILIDADES_QUE_ESCALAM = ("For", "Vig", "Agi", "Des", "Lut", "Pro")
DEFESAS_QUE_ESCALAM = ("Esquiva", "Aparar", "Fortitude", "Vontade", "Resistencia", "Resistência")
# Graduações de efeito que entram nos limites do NP (ataque + efeito, área até o NP) e as CDs escritas no texto.
_EFEITO = re.compile(r"\b(Dano|Aflição|Enfraquecer \w+|Anular|CD|DC) (\d+)")
_PROTECAO = re.compile(r"\bProteção (\d+)")


def _sem_vigor(habilidades):
    """Mortos-vivos e construtos: Vigor ausente (null, ou -5 nas fichas antigas)."""
    return habilidades.get("Vig") in (None, -5)


def _mudar_graduacoes(texto, delta):
    return _EFEITO.sub(lambda m: f"{m.group(1)} {max(1, int(m.group(2)) + delta)}", texto)


def no_np(dados, np):
    """Cópia da criatura levada a outro NP, sem mexer no arquivo.

    Cada NP a mais (ou a menos) vale +1 (–1) em Força, Vigor, Agilidade, Destreza, Luta e Prontidão, nas defesas,
    nos bônus de ataque e nas graduações de Dano, Aflição, Enfraquecer e Anular (e nas CDs do texto). Assim os
    limites do NP (ataque + efeito, defesa + Resistência, Fortitude + Vontade: 2 × NP) andam junto com ele.
    Sem Vigor, a Resistência vem da Proteção, que sobe no lugar dele. As perícias guardam as graduações; o total
    acompanha a habilidade.
    """
    padrao = dados.get("nivel_poder", 1)
    np = max(NP_MINIMO, min(int(np), NP_MAXIMO))
    delta = np - padrao
    escalada = copy.deepcopy(dados)
    if delta == 0:
        return escalada
    f = escalada.setdefault("ficha", {})
    hab = f.setdefault("habilidades", {})
    sem_vigor = _sem_vigor(hab)

    for sigla in HABILIDADES_QUE_ESCALAM:
        valor = hab.get(sigla)
        if not isinstance(valor, int) or valor == -5:
            continue  # habilidade ausente continua ausente
        hab[sigla] = max(-5, valor + delta)

    defesas = f.setdefault("defesas", {})
    for nome in DEFESAS_QUE_ESCALAM:
        valor = defesas.get(nome)
        if not isinstance(valor, int) or (nome == "Fortitude" and sem_vigor):
            continue  # "Imune", ou a Fortitude de quem não tem Vigor
        defesas[nome] = max(0, valor + delta)

    for ataque in f.get("ataques", []):
        if isinstance(ataque.get("bonus"), int) and ataque["bonus"]:
            ataque["bonus"] = max(0, ataque["bonus"] + delta)
        if isinstance(ataque.get("dano"), int) and ataque["dano"]:
            ataque["dano"] = max(1, ataque["dano"] + delta)
        if ataque.get("descricao"):
            ataque["descricao"] = _mudar_graduacoes(ataque["descricao"], delta)

    protecao_ajustada = not sem_vigor
    for poder in f.get("poderes", []):
        chave = "construcao" if "construcao" in poder else "efeito"
        texto = _mudar_graduacoes(poder.get(chave, ""), delta)
        if not protecao_ajustada and _PROTECAO.search(texto):
            texto = _PROTECAO.sub(lambda m: f"Proteção {max(0, int(m.group(1)) + delta)}", texto, count=1)
            protecao_ajustada = True
        poder[chave] = texto

    escalada["nivel_poder"] = np
    escalada["np_padrao"] = padrao
    escalada["aviso_de_escala"] = (
        f"Ficha levada do NP {padrao} (padrão) ao NP {np} pelo gerador: {delta:+d} em Força, Vigor, Agilidade, "
        f"Destreza, Luta e Prontidão, nas defesas, nos ataques e nas graduações dos efeitos. "
        f"As perícias guardam as graduações.")
    return escalada


def carregar(criatura_id, np=None):
    """(dados, resumo) da criatura, já no NP pedido (None ou o padrão: a ficha como está no arquivo)."""
    entrada = _catalogo().get(criatura_id)
    if not entrada:
        return None, None
    caminho, resumo = entrada
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if np is not None and int(np) != dados.get("nivel_poder"):
        dados = no_np(dados, np)
    return dados, resumo


def ficha(criatura_id, np=None):
    """Retorna os dados completos e seções formatadas de uma criatura para a interface (no NP pedido)."""
    dados, resumo = carregar(criatura_id, np)
    if dados is None:
        return None
    f = dados.get("ficha", {})

    ataques = []
    for a in f.get("ataques", []):
        nome = a.get("nome", "Ataque")
        bonus = a.get("bonus", 0)
        dano = a.get("dano", 0)
        crit = a.get("critico", 20)
        desc = a.get("descricao", "")
        extra_crit = f", Crítico {crit}-20" if crit and crit < 20 else ""
        extra_desc = f" ({desc})" if desc else ""
        sinal = f"{bonus:+d}" if isinstance(bonus, int) else str(bonus)
        ataques.append(f"{nome} {sinal}, Dano {dano}{extra_crit}{extra_desc}")

    poderes = []
    for p in f.get("poderes", []):
        nome = p.get("nome", "")
        cons = p.get("construcao", p.get("efeito", ""))
        poderes.append(f"{nome}: {cons}" if nome and cons else (nome or cons))

    secoes = [
        {"titulo": "Defesas", "itens": [_texto_de(f.get("defesas", {}))]},
        {"titulo": "Ataques", "itens": ataques or ["Nenhum ataque registrado."]},
    ]

    if poderes:
        secoes.append({"titulo": "Poderes & Traços Especiais", "itens": poderes})

    pericias = texto_das_pericias(f)
    if pericias:
        secoes.append({"titulo": "Perícias", "itens": pericias})

    vantagens = f.get("vantagens", [])
    if vantagens:
        secoes.append({"titulo": "Vantagens", "itens": vantagens})

    if dados.get("complicacoes"):
        secoes.append({"titulo": "Complicações", "itens": dados["complicacoes"]})

    equipamento = f.get("equipamento", [])
    if equipamento:
        secoes.append({"titulo": "Equipamento", "itens": equipamento})

    if dados.get("tatica"):
        secoes.append({"titulo": "Táticas de Combate", "itens": [dados["tatica"]]})


    # Lista de variantes com marcador 'atual'
    variantes = [
        {**v, "atual": bool(v["id"] == criatura_id)}
        for v in resumo.get("variantes", [])
    ]

    return {
        "id": criatura_id,
        "genero": resumo["genero"],
        "genero_nome": resumo["genero_nome"],
        "familia": resumo["familia"],
        "variante": resumo["variante"],
        "variantes": variantes,
        "total_variantes": len(variantes),
        "nome": dados.get("nome", resumo["nome"]),
        "tipo": dados.get("tipo", resumo["tipo"]),
        "subtipo": dados.get("subtipo", resumo["subtipo"]),
        "papel": dados.get("papel", resumo["papel"]),
        "chefe": resumo["chefe"],
        "tamanho": dados.get("tamanho", resumo["tamanho"]),
        "np": dados.get("nivel_poder", resumo["np"]),
        "np_padrao": resumo["np"],
        "aviso_de_escala": dados.get("aviso_de_escala", ""),
        "ambientes": dados.get("ambientes", resumo["ambientes"]),
        "descricao": dados.get("descricao", resumo["descricao"]),
        "tatica": dados.get("tatica", ""),
        "habilidades": f.get("habilidades", {}),
        "pericias": pericias,
        "defesas": f.get("defesas", {}),
        "secoes": secoes,
        "fonte": dados.get("fonte", "Guia do Mestre de Jogo / D&D 5e"),
    }
