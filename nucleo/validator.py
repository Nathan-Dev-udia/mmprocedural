"""Validação mecânica de fichas de M&M 3e.

O validador recebe uma ficha já montada (base + módulos) e devolve um relatório:
valores calculados, custos em pontos de poder, limites do NP e o status.
Ele não sorteia nada e não altera a ficha.

Formato da ficha (dicionário):
    habilidades         {"For": 3, ...}           graduações compradas
    defesas_compradas   {"Esquiva": 1, ...}       graduações acima da habilidade
    pericias            {"Atletismo": 4, ...}     graduações
    vantagens           {"Saque Rápido": 1, ...}  graduações
    poderes             {id: {"nome", "custo_informado", "ajustes"}}
    equipamento         [ids do catálogo de equipamento]
    ataques_naturais    [{"nome", "tipo", "pericia", "efeito", "soma_forca", "critico"}]
    ataque_desarmado    True/False
    fontes              [{"nome", "status_dados"}]  de onde vieram os dados
"""

import math

from . import poderes as poderes_mod
from . import rules

STATUS = {
    "invalida": "Inválida",
    "conceitual": "Conceitual",
    "parcial": "Custos parciais",
    "calculada": "Custos calculados",
    "validada": "Validada (regras implementadas)",
}


def _ajustes_de_poder(ficha, ativo=None):
    """Soma os ajustes que poderes fazem em habilidades e defesas.

    Num arranjo só um efeito funciona por vez (livro básico, cap. 6): vale o principal, ou `ativo` (o id de um
    efeito alternativo) no lugar do principal do arranjo dele. Ex.: o Quen (escudo) é alternativo do Igni, então a
    Proteção dele não entra na ficha de sempre, só na conferência "com Quen ativo".
    """
    poderes = ficha.get("poderes", {})
    papeis = poderes_mod.papeis_no_arranjo(poderes)
    arranjo_do_ativo = poderes[ativo].get("arranjo") if ativo in poderes else None
    total = {}
    for poder_id, poder in poderes.items():
        papel = papeis.get(poder_id)
        if papel == "alternativo" and poder_id != ativo:
            continue
        if papel == "principal" and arranjo_do_ativo == poder.get("arranjo"):
            continue
        for chave, valor in poder.get("ajustes", {}).items():
            total[chave] = total.get(chave, 0) + valor
    return total


def _com_quantidade(nome, quantidade):
    """'Rações de viagem (5 dias)', 3 -> 'Rações de viagem (5 dias) ×3'."""
    return f"{nome} ×{quantidade}" if quantidade > 1 else nome


def calcular(ficha, catalogo_equipamento, ativo=None):
    """Calcula os valores finais da ficha (o que vai impresso no cartão).

    ativo: id de um efeito alternativo de arranjo para calcular a ficha com ele ligado.
    """
    ajustes = _ajustes_de_poder(ficha, ativo)
    vantagens = ficha.get("vantagens", {})
    pericias = ficha.get("pericias", {})

    hab = {h: ficha["habilidades"].get(h, 0) + ajustes.get(h, 0) for h in rules.HABILIDADES}

    defesas = {}
    for defesa, habilidade in rules.DEFESAS_COMPRAVEIS.items():
        defesas[defesa] = (hab[habilidade]
                           + ficha.get("defesas_compradas", {}).get(defesa, 0)
                           + ajustes.get(defesa, 0))

    itens = [catalogo_equipamento[i] for i in ficha.get("equipamento", [])]
    # Livro básico, cap. 7: escudos dão bônus às defesas ativas (Esquiva e Aparar); vale o maior escudo.
    escudo = max([item.get("defesas_ativas", 0) for item in itens], default=0)
    defesas["Esquiva"] += escudo
    defesas["Aparar"] += escudo
    # Livro básico, cap. 7: bônus de armadura não se somam a outros bônus de Proteção; vale o maior.
    # Coletes à prova de balas são Proteção Limitada a ataques balísticos ("Res 6/2" no livro):
    # contam contra tiros, mas não contra golpes corpo a corpo.
    protecao = max([item.get("protecao", 0) for item in itens], default=0)
    protecao_plena = max([item.get("protecao", 0) for item in itens if not item.get("limitada_a")], default=0)
    fontes_de_protecao = [
        item["nome"] for item in itens
        if item.get("protecao") == protecao and protecao > 0
    ]
    protecao_de_poder = ajustes.get("Proteção", 0)
    base_de_resistencia = (hab["Vig"] + vantagens.get(rules.VANTAGEM_RESISTENCIA, 0)
                           + ajustes.get("Resistência", 0))
    defesas["Resistência"] = base_de_resistencia + max(protecao, protecao_de_poder)
    resistencia_plena = base_de_resistencia + max(protecao_plena, protecao_de_poder)
    limitadas = sorted({item["limitada_a"] for item in itens if item.get("limitada_a") and item.get("protecao")})

    iniciativa = hab["Agi"] + rules.INICIATIVA_POR_GRADUACAO * vantagens.get(rules.VANTAGEM_INICIATIVA, 0)

    pericias_totais = {}
    for nome, graduacoes in pericias.items():
        pericias_totais[nome] = {"graduacoes": graduacoes,
                                 "total": hab[rules.habilidade_da_pericia(nome)] + graduacoes}

    ataques = []
    fontes_de_ataque = list(ficha.get("ataques_naturais", []))
    if ficha.get("ataque_desarmado"):
        fontes_de_ataque.insert(0, {"nome": "Desarmado", "tipo": "corpo", "efeito": 0, "soma_forca": True,
                                    "pericia": "Combate Corpo-a-Corpo: Briga", "critico": 20})
    fontes_de_ataque += [item["ataque"] | {"nome": item["nome"]} for item in itens if "ataque" in item]
    fontes_de_ataque += [p["ataque"] | {"nome": p.get("nome_curto", p["nome"])}
                         for p in ficha.get("poderes", {}).values() if "ataque" in p]

    for atq in fontes_de_ataque:
        dano = atq["efeito"] + (hab["For"] if atq.get("soma_forca") else 0)
        efeito = atq.get("efeito_nome", "Dano")
        base_da_cd = 15 if efeito == "Dano" else 10
        if atq["tipo"] == "area":
            ataques.append({"nome": atq["nome"], "tipo": "area", "bonus": None, "dano": dano,
                            "efeito_nome": efeito, "cd_esquiva": 10 + dano,
                            "resistido_por": atq.get("resistido_por", "Resistência"),
                            "cd_resistencia": base_da_cd + dano, "critico": None})
            continue
        if atq["tipo"] == "percepcao":
            # Alcance percepção: acerta sem teste de ataque; o efeito é limitado ao NP (como área).
            ataques.append({"nome": atq["nome"], "tipo": "percepcao", "bonus": None, "dano": dano,
                            "efeito_nome": efeito, "resistido_por": atq.get("resistido_por", "Vontade"),
                            "cd_resistencia": base_da_cd + dano, "critico": None})
            continue
        bonus = (hab[rules.HABILIDADE_DE_ATAQUE[atq["tipo"]]]
                 + pericias.get(atq.get("pericia"), 0)
                 + vantagens.get(rules.VANTAGEM_ATAQUE[atq["tipo"]], 0))
        # Dano é resistido com CD 15 + graduação; outros efeitos (Armadilha do laço), com CD 10 + graduação.
        ataques.append({"nome": atq["nome"], "tipo": atq["tipo"], "bonus": bonus, "dano": dano,
                        "multiataque": bool(atq.get("multiataque")),
                        "pericia": atq.get("pericia"), "soma_forca": bool(atq.get("soma_forca")),
                        "efeito_nome": efeito, "resistido_por": atq.get("resistido_por", "Resistência"),
                        "cd_resistencia": base_da_cd + dano, "critico": atq.get("critico", 20)})

    pontos_equipamento = {
        "usados": sum(item["custo"] * ficha.get("quantidades", {}).get(i, 1)
                      for item, i in zip(itens, ficha.get("equipamento", [])) if item.get("custo") is not None),
        "disponiveis": rules.PONTOS_DE_EQUIPAMENTO_POR_GRADUACAO * vantagens.get(rules.VANTAGEM_EQUIPAMENTO, 0),
        "itens_sem_custo": [item["nome"] for item in itens if item.get("custo") is None],
    }

    return {
        "habilidades": hab,
        "defesas": defesas,
        "iniciativa": iniciativa,
        "pericias": pericias_totais,
        "ataques": ataques,
        "pontos_equipamento": pontos_equipamento,
        "itens": [_com_quantidade(item["nome"], ficha.get("quantidades", {}).get(i, 1))
                  for item, i in zip(itens, ficha.get("equipamento", []))],
        "protecao": protecao,
        "fontes_de_protecao": fontes_de_protecao,
        "protecao_de_poder": protecao_de_poder,
        # Resistência sem as proteções limitadas (ex.: contra golpes, quando o colete só para balas).
        "resistencia_plena": resistencia_plena,
        "protecao_limitada_a": limitadas,
    }


def calcular_custos(ficha):
    """Custos em pontos de poder por seção, e de onde vem cada valor."""
    custos = {
        "habilidades": rules.CUSTO_POR_GRADUACAO_HABILIDADE * sum(ficha["habilidades"].values()),
        "defesas": rules.CUSTO_POR_GRADUACAO_DEFESA * sum(ficha.get("defesas_compradas", {}).values()),
        "pericias": rules.custo_pericias(sum(ficha.get("pericias", {}).values())),
        "vantagens": rules.CUSTO_POR_GRADUACAO_VANTAGEM * sum(ficha.get("vantagens", {}).values()),
    }
    origem = {secao: "calculado" for secao in custos}

    poderes = ficha.get("poderes", {})
    if poderes:
        custos["poderes"] = poderes_mod.custo_total(poderes)
        origem["poderes"] = "pendente" if custos["poderes"] is None else "informado"

    total = None if None in custos.values() else sum(custos.values())
    return custos, origem, total


def _checar_defesas(valores, np, sufixo="", extras=None):
    """Somas de defesa contra os tetos do NP. extras: bônus que só valem numa situação (ex.: +2 de Vontade contra
    efeitos mentais), somados às defesas desta conferência."""
    teto = rules.limites_do_np(np)
    d = dict(valores["defesas"])
    resistencia_plena = valores["resistencia_plena"]
    for defesa, bonus in (extras or {}).items():
        d[defesa] = d.get(defesa, 0) + bonus
        if defesa == "Resistência":
            resistencia_plena += bonus
    pares = [("Esquiva + Resistência", d["Esquiva"] + d["Resistência"], teto["esquiva_mais_resistencia"]),
             # Aparar protege contra golpes; usa a Resistência sem proteções limitadas a balísticos.
             ("Aparar + Resistência", d["Aparar"] + resistencia_plena, teto["aparar_mais_resistencia"]),
             ("Fortitude + Vontade", d["Fortitude"] + d["Vontade"], teto["fortitude_mais_vontade"])]
    return [{"nome": nome + sufixo, "valor": valor, "maximo": maximo, "ok": valor <= maximo}
            for nome, valor, maximo in pares
            if not extras or any(defesa in nome for defesa in extras)]


def _checar_situacoes(ficha, catalogo_equipamento, np, valores):
    """Conferências extras de defesa: cada efeito alternativo de arranjo que muda defesas, ligado; e os bônus
    limitados ("ajustes_limitados", ex.: Vontade contra efeitos mentais), somados."""
    checagens = []
    poderes = ficha.get("poderes", {})
    for poder_id, papel in poderes_mod.papeis_no_arranjo(poderes).items():
        if papel == "alternativo" and poderes[poder_id].get("ajustes"):
            com_ele = calcular(ficha, catalogo_equipamento, ativo=poder_id)
            nome = poderes[poder_id].get("nome_curto", poderes[poder_id]["nome"])
            checagens += _checar_defesas(com_ele, np, f" (com {nome} ativo)")
    for poder in poderes.values():
        if poder.get("ajustes_limitados"):
            nome = poder.get("nome_curto", poder["nome"])
            checagens += _checar_defesas(valores, np, f" ({nome})", poder["ajustes_limitados"])
    return checagens


def _checar_limites(valores, np):
    """Compara os valores calculados com os tetos do NP."""
    teto = rules.limites_do_np(np)
    checagens = []

    def checar(nome, valor, maximo):
        checagens.append({"nome": nome, "valor": valor, "maximo": maximo, "ok": valor <= maximo})

    for atq in valores["ataques"]:
        if atq["tipo"] == "area":
            checar(f"{atq['nome']}: efeito em área", atq["dano"], teto["efeito_sem_ataque"])
        elif atq["tipo"] == "percepcao":
            checar(f"{atq['nome']}: efeito de percepção", atq["dano"], teto["efeito_sem_ataque"])
        else:
            checar(f"{atq['nome']}: ataque + dano", atq["bonus"] + atq["dano"], teto["ataque_mais_efeito"])

    checagens += _checar_defesas(valores, np)

    for nome, pericia in valores["pericias"].items():
        checar(f"Perícia {nome}", pericia["total"], teto["pericia"])
    return checagens


def np_efetivo(valores):
    """Estima o NP da ficha pelos valores, como o livro manda fazer com PdMs."""
    candidatos = [0]
    for atq in valores["ataques"]:
        if atq["tipo"] in ("area", "percepcao"):
            candidatos.append(atq["dano"])
        else:
            candidatos.append(math.ceil((atq["bonus"] + atq["dano"]) / 2))
    d = valores["defesas"]
    for par in (d["Esquiva"] + d["Resistência"], d["Aparar"] + valores["resistencia_plena"],
                d["Fortitude"] + d["Vontade"]):
        candidatos.append(math.ceil(par / 2))
    candidatos += [p["total"] - 10 for p in valores["pericias"].values()]
    return max(candidatos)


def validar(ficha, np, catalogo_equipamento, opcoes=None):
    """Gera o relatório completo de validação de uma ficha no NP pedido.

    opcoes (todas opcionais):
        equipamento_gratuito  True: equipamento é pago em dinheiro e não usa a vantagem Equipamento.
        orcamento             total exato de pontos de poder que a ficha deve ter (personagem de jogador).
    """
    opcoes = opcoes or {}
    valores = calcular(ficha, catalogo_equipamento)
    custos, origem, total = calcular_custos(ficha)
    limites = _checar_limites(valores, np) + _checar_situacoes(ficha, catalogo_equipamento, np, valores)

    problemas = [f"{c['nome']} = {c['valor']} passa do limite de {c['maximo']} no NP {np}."
                 for c in limites if not c["ok"]]
    for hab, valor in ficha["habilidades"].items():
        if valor < rules.HABILIDADE_MINIMA:
            problemas.append(f"Habilidade {hab} = {valor} está abaixo de {rules.HABILIDADE_MINIMA}.")
    for secao in ("pericias", "vantagens", "defesas_compradas"):
        for nome, graduacoes in ficha.get(secao, {}).items():
            if graduacoes < 0:
                problemas.append(f"{nome} tem graduação negativa ({graduacoes}).")
    sorte = ficha.get("vantagens", {}).get(rules.VANTAGEM_SORTE, 0)
    if sorte > rules.limite_de_sorte(np):
        problemas.append(f"Sorte {sorte} passa do limite de {rules.limite_de_sorte(np)} (metade do NP {np}).")

    pe = valores["pontos_equipamento"]
    pe["gratuito"] = bool(opcoes.get("equipamento_gratuito"))
    if pe["gratuito"]:
        pe["itens_sem_custo"] = []
    elif pe["usados"] > pe["disponiveis"]:
        problemas.append(f"Equipamento usa {pe['usados']} pontos, mas a vantagem Equipamento só dá "
                         f"{pe['disponiveis']}.")

    orcamento = opcoes.get("orcamento")
    if orcamento is not None and total is not None and total != orcamento:
        problemas.append(f"A ficha soma {total} PP, mas o orçamento do personagem é {orcamento} PP.")

    pendencias, avisos = [], []
    if origem.get("poderes") == "pendente":
        pendencias.append("Há traços naturais sem custo cadastrado; o total de pontos não pode ser calculado.")
    if origem.get("poderes") == "informado":
        avisos.append("O custo dos traços naturais (construídos com efeitos de poder no livro) foi copiado da fonte e não foi recalculado pelo programa.")
    if pe["itens_sem_custo"]:
        pendencias.append("Equipamento sem custo cadastrado: " + ", ".join(pe["itens_sem_custo"]) + ".")
    fontes = ficha.get("fontes", [])
    for fonte in fontes:
        if fonte["status_dados"] == "ilustrativo":
            avisos.append(f"{fonte['nome']}: números ilustrativos, criados para o protótipo (não vêm de livro).")
        elif fonte["status_dados"] == "pendente":
            pendencias.append(f"{fonte['nome']}: dados marcados como pendentes de revisão.")
        elif fonte["status_dados"] == "conceitual":
            pendencias.append(f"{fonte['nome']}: só tem descrição, sem números.")

    if problemas:
        status = "invalida"
    elif any(f["status_dados"] == "conceitual" for f in fontes):
        status = "conceitual"
    elif pendencias:
        status = "parcial"
    elif "informado" in origem.values():
        status = "calculada"
    else:
        status = "validada"

    return {
        "valores": valores,
        "custos": custos,
        "origem_dos_custos": origem,
        "total_pp": total,
        "orcamento": orcamento,
        "limites": limites,
        "np_verificado": np,
        "np_efetivo": np_efetivo(valores),
        "problemas": problemas,
        "pendencias": pendencias,
        "avisos": avisos,
        "status": status,
        "status_rotulo": STATUS[status],
    }
