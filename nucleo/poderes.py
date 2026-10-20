"""Poderes vindos do catálogo extraído dos livros (dados/comum/poderes).

Um poder do catálogo tem o custo do livro (fixo e/ou por graduação) e a linha de estatística
interpretada (efeito-base, alcance, área, defesa). Este módulo:

- resolve uma referência {"catalogo": id, "graduacao": n} num poder pronto para a ficha
  (nome, custo, ajustes em habilidades e defesas, ataque);
- busca poderes por perfil, categoria e efeito, para os arquétipos sortearem.

O custo é o informado pelo livro (não é recalculado a partir das regras de modificadores),
por isso as fichas com poderes ficam com status "Custos calculados".

Arranjos (livro básico, cap. 6, Efeitos Alternativos): poderes com o mesmo "arranjo" são usados um
de cada vez. O mais caro é o efeito principal e paga o custo cheio; cada outro custa 1 PP.
"""

import math
import re

# Efeitos que somam graduações a uma habilidade ou defesa (Característica Aumentada e afins).
AJUSTES_POR_EFEITO = {
    "Força Aumentada": "For", "Aumento de Força": "For", "Vigor Aumentado": "Vig",
    "Agilidade Aumentada": "Agi", "Destreza Aumentada": "Des", "Luta Aumentada": "Lut",
    "Intelecto Aumentado": "Int", "Prontidão Aumentada": "Pro", "Presença Aumentada": "Pre",
    "Esquiva Aumentada": "Esquiva", "Aparar Aumentado": "Aparar", "Fortitude Aumentada": "Fortitude",
    "Vontade Aumentada": "Vontade", "Proteção": "Proteção",
    "Aparar Aumentado": "Aparar", "Aumento de Vontade": "Vontade",
}

# Efeitos de ataque e a defesa que resiste por padrão.
EFEITOS_DE_ATAQUE = {"Dano": "Resistência", "Aflição": "Vontade", "Enfraquecer": "Fortitude",
                     "Pasmar": "Fortitude", "Armadilha": "Esquiva", "Nulificar": "Vontade"}

# Efeitos que o gerador ainda não sabe usar com segurança.
EFEITOS_FORA_DA_BUSCA = {"Variável", "Invocar", "Transformar", None}

# Custo de cada efeito alternativo de um arranjo (o livro também tem o Dinâmico, a 2 PP, que o gerador não usa).
CUSTO_DO_EFEITO_ALTERNATIVO = 1


class PoderInvalido(Exception):
    pass


def custo(item, graduacao, por_graduacao=None):
    """Custo em PP: fixo + por graduação × graduação (frações arredondadas para cima).

    por_graduacao substitui o valor lido do livro quando a entrada traz mais de um preço
    (ex.: Defesa Rápida: 1 PP por graduação de uma defesa, 2 PP por graduação de ambas).
    """
    c = dict(item["custo"])
    if por_graduacao is not None:
        c["por_graduacao"] = por_graduacao
    if c.get("fixo") is None:
        # O extrator guardou só a parte por graduação de custos como "3 pontos por graduação + 2 pontos";
        # a parte fixa (os extras e falhas de custo fixo do livro) está no texto.
        fixo = re.search(r"\+\s*(\d+)\s*pontos?\b", c.get("texto") or "")
        if fixo:
            c["fixo"] = int(fixo.group(1))
    if c.get("por_graduacao") is None and c.get("fixo") is None:
        raise PoderInvalido(f"{item['nome']}: o livro não traz um custo simples ({c.get('texto')}).")
    total = (c.get("fixo") or 0) + (c.get("por_graduacao") or 0) * (graduacao or 0)
    return math.ceil(total)


def papeis_no_arranjo(poderes):
    """{id do poder: "principal" | "alternativo"} para os poderes que estão em algum arranjo.

    O principal é o mais caro do arranjo (no empate, o que aparece primeiro).
    """
    papeis, principais = {}, {}
    for poder_id, poder in poderes.items():
        arranjo = poder.get("arranjo")
        if not arranjo:
            continue
        atual = principais.get(arranjo)
        if atual is None or (poder.get("custo_informado") or 0) > (poderes[atual].get("custo_informado") or 0):
            principais[arranjo] = poder_id
    for poder_id, poder in poderes.items():
        if poder.get("arranjo"):
            papeis[poder_id] = "principal" if principais[poder["arranjo"]] == poder_id else "alternativo"
    return papeis


def em_ordem_de_exibicao(poderes):
    """[(id, poder, papel)] com cada arranjo junto: o principal e logo depois os alternativos."""
    papeis = papeis_no_arranjo(poderes)
    saida, arranjos_vistos = [], set()
    for poder_id, poder in poderes.items():
        arranjo = poder.get("arranjo")
        if not arranjo:
            saida.append((poder_id, poder, None))
            continue
        if arranjo in arranjos_vistos:
            continue
        arranjos_vistos.add(arranjo)
        do_arranjo = [(i, p) for i, p in poderes.items() if p.get("arranjo") == arranjo]
        do_arranjo.sort(key=lambda par: papeis[par[0]] != "principal")
        saida += [(i, p, papeis[i]) for i, p in do_arranjo]
    return saida


def custo_total(poderes):
    """Custo em PP de um conjunto de poderes, com os arranjos já descontados (None se algum não tem custo)."""
    if any(p.get("custo_informado") is None for p in poderes.values()):
        return None
    papeis = papeis_no_arranjo(poderes)
    return sum(CUSTO_DO_EFEITO_ALTERNATIVO if papeis.get(poder_id) == "alternativo" else poder["custo_informado"]
               for poder_id, poder in poderes.items())


def graduacao_no_np(entrada, np):
    """Graduação de um poder do gênero que acompanha o NP ("graduacao_np": ajuste somado ao NP, mínimo 1)."""
    return max(1, np + entrada["graduacao_np"])


def graduacao_padrao(item):
    """Graduação embutida na estatística (ex.: 'Camuflagem 10'), se houver."""
    return item["efeitos"][0].get("graduacao") if item.get("efeitos") else None


def resolver(entrada, catalogo):
    """{"catalogo": id, "graduacao": n, "nome": opcional, "descricao": opcional} -> poder da ficha."""
    item = catalogo.get(entrada["catalogo"])
    if item is None:
        raise PoderInvalido(f"Poder '{entrada['catalogo']}' não está no catálogo deste gênero.")
    efeito = item["efeitos"][0] if item.get("efeitos") else {}
    por_graduacao = item["custo"].get("por_graduacao")
    graduacao = entrada.get("graduacao") or graduacao_padrao(item)
    if por_graduacao and not graduacao:
        raise PoderInvalido(f"{item['nome']}: informe a graduação (o custo é por graduação).")
    nome = entrada.get("nome") or item["nome"]
    rotulo = f"{nome} {graduacao}" if por_graduacao else nome
    if entrada.get("estatistica"):
        # O gênero reescreve a estatística com o descritor dele (ex.: "força mágica" no lugar de "laser").
        nome_completo = f"{rotulo} ({entrada['estatistica']})"
    elif entrada.get("nome"):
        nome_completo = f"{rotulo} ({item['nome']}: {item['estatistica']})"
    else:
        nome_completo = f"{rotulo} ({item['estatistica']})"
    poder = {
        "nome": nome_completo,
        "descricao": entrada.get("descricao", ""),
        "nome_curto": rotulo,
        "custo_informado": custo(item, graduacao, entrada.get("custo_por_graduacao")),
        "ajustes": {},
        "catalogo": item["id"],
        "graduacao": graduacao,
        "fonte": f"{item.get('arquivo', 'catálogo')}: perfil {item['perfil']}, pág. {item.get('pagina_pdf')} do PDF",
    }
    if entrada.get("arranjo"):
        poder["arranjo"] = entrada["arranjo"]
    if entrada.get("ajustes_limitados"):
        # Bônus que só valem numa situação (ex.: Vontade contra efeitos mentais): não entram na ficha de sempre,
        # mas o validador confere os limites do NP com eles.
        poder["ajustes_limitados"] = {defesa: graduacao if valor == "graduacao" else valor
                                      for defesa, valor in entrada["ajustes_limitados"].items()}
    base = efeito.get("efeito_base")
    if base in AJUSTES_POR_EFEITO and graduacao:
        poder["ajustes"][AJUSTES_POR_EFEITO[base]] = graduacao
        # A mesma linha pode aumentar mais de um traço ("Esquiva Aumentada, Aparar Aumentado").
        for nome_do_efeito, traco in AJUSTES_POR_EFEITO.items():
            if nome_do_efeito in item["estatistica"]:
                poder["ajustes"][traco] = graduacao
    if base in EFEITOS_DE_ATAQUE and graduacao:
        alcance = efeito.get("alcance")
        if efeito.get("area"):
            tipo = "area"
        elif alcance == "percepcao":
            tipo = "percepcao"
        elif alcance == "distancia":
            tipo = "distancia"
        else:
            tipo = "corpo"
        ataque = {"tipo": tipo, "efeito": graduacao, "efeito_nome": base,
                  "resistido_por": efeito.get("resistido_por") or EFEITOS_DE_ATAQUE[base], "critico": 20}
        if tipo in ("distancia", "corpo"):
            combate = "Combate à Distância" if tipo == "distancia" else "Combate Corpo-a-Corpo"
            # "pericia" na entrada: várias magias podem usar a mesma perícia (ex.: Combate à Distância: Magia).
            ataque["pericia"] = entrada.get("pericia") or f"{combate}: {nome}"
            ataque["soma_forca"] = tipo == "corpo" and "força" in item["estatistica"].lower()
        if "multi" in item["estatistica"].lower():
            ataque["multiataque"] = True
        poder["ataque"] = ataque
    return poder


def buscar(catalogo, perfis=None, categorias=None, efeitos=None):
    """Poderes do catálogo que o gerador sabe usar, filtrados por perfil, categoria e efeito-base."""
    achados = []
    for item in catalogo.values():
        if item.get("conferir") or item.get("modifica_outro_poder"):
            continue
        base = item["efeitos"][0].get("efeito_base") if item.get("efeitos") else None
        if base in EFEITOS_FORA_DA_BUSCA:
            continue
        if perfis and item["perfil"] not in perfis:
            continue
        if categorias and item["categoria"] not in categorias:
            continue
        if efeitos and base not in efeitos:
            continue
        achados.append(item)
    return achados
