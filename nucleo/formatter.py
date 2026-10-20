"""Transforma um NPC gerado em textos prontos para exibir ou copiar.

Nada aqui calcula regra: tudo vem do relatório do validador.
"""

from . import poderes as poderes_mod
from . import rules

NOMES_DE_HABILIDADE = {"For": "FOR", "Vig": "VIG", "Agi": "AGI", "Des": "DES",
                       "Lut": "LUT", "Int": "INT", "Pro": "PRO", "Pre": "PRE"}

NOMES_DE_SECAO = {"habilidades": "Habilidades", "defesas": "Defesas", "pericias": "Perícias",
                  "vantagens": "Vantagens", "poderes": "Poderes"}


def _sinal(valor):
    return f"{valor:+d}"


def _metros(valor):
    texto = f"{valor:.1f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def nome_curto(nome):
    """'Revólver leve (Colt Navy)' -> 'Revólver leve', para caber na linha de ataque."""
    return nome.split(" (")[0]


def detalhes_do_ataque(ataque):
    if ataque["tipo"] == "area":
        return f"Área; Esquiva CD {ataque['cd_esquiva']} sofre metade"
    if ataque["tipo"] == "percepcao":
        return f"Percepção (sem teste de ataque); {ataque['resistido_por']} CD {ataque['cd_resistencia']}"
    critico = f"crít. {ataque['critico']}–20" if ataque["critico"] < 20 else "crít. 20"
    resistido = ataque.get("resistido_por", "Resistência")
    resistencia = f"{'Resist.' if resistido == 'Resistência' else resistido} CD {ataque['cd_resistencia']}"
    if ataque.get("efeito_nome", "Dano") != "Dano":
        critico = f"{ataque['efeito_nome']} {ataque['dano']}, {critico}"
    if ataque["tipo"] == "distancia":
        d = ataque["dano"]
        return f"{_metros(d * 7.5)}/{_metros(d * 15)}/{_metros(d * 30)} m, {critico}, {resistencia}"
    return f"Corpo a corpo, {critico}, {resistencia}"


def texto_ataque(ataque):
    efeito_area = ataque.get("efeito_nome", "Dano")
    if ataque["tipo"] == "area":
        return f"{ataque['nome']} ({efeito_area} {ataque['dano']} em área, Esquiva CD {ataque['cd_esquiva']})"
    if ataque["tipo"] == "percepcao":
        return (f"{ataque['nome']} ({efeito_area} {ataque['dano']} à percepção, "
                f"{ataque['resistido_por']} CD {ataque['cd_resistencia']})")
    alcance = " à distância" if ataque["tipo"] == "distancia" else ""
    critico = f", crítico {ataque['critico']}–20" if ataque.get("critico") and ataque["critico"] < 20 else ""
    efeito = ataque.get("efeito_nome", "Dano")
    cd = "" if efeito == "Dano" else f", {ataque['resistido_por']} CD {ataque['cd_resistencia']}"
    multi = ", Multiataque" if ataque.get("multiataque") else ""
    return f"{ataque['nome']} {_sinal(ataque['bonus'])} ({efeito} {ataque['dano']}{alcance}{multi}{critico}{cd})"


def texto_do_poder(poder, papel=None):
    """Nome do poder, com a posição no arranjo quando ele faz parte de um."""
    if papel == "principal":
        return f"{poder['nome']} — Arranjo {poder['arranjo']}: efeito principal"
    if papel == "alternativo":
        return f"{poder['nome']} — Arranjo {poder['arranjo']}: efeito alternativo (1 PP)"
    return poder["nome"]


def exibicao(npc):
    """Campos já formatados que a página mostra no cartão."""
    rel = npc["validacao"]
    val = rel["valores"]
    ficha = npc["ficha"]

    habilidades = ", ".join(f"{NOMES_DE_HABILIDADE[h]} {val['habilidades'][h]}" for h in rules.HABILIDADES)
    pericias = [f"{nome} {p['graduacoes']} ({_sinal(p['total'])})"
                for nome, p in sorted(val["pericias"].items())]
    vantagens = [nome if grad == 1 and nome != rules.VANTAGEM_EQUIPAMENTO else f"{nome} {grad}"
                 for nome, grad in sorted(ficha.get("vantagens", {}).items())]
    poderes = [texto_do_poder(p, papel) for _, p, papel in poderes_mod.em_ordem_de_exibicao(ficha.get("poderes", {}))]
    d = val["defesas"]
    resistencia = str(d["Resistência"])
    if val.get("resistencia_plena", d["Resistência"]) != d["Resistência"]:
        resistencia += f"/{val['resistencia_plena']} (a primeira só contra ataques {', '.join(val['protecao_limitada_a'])})"
    defesas = (f"Esquiva {d['Esquiva']}, Aparar {d['Aparar']}, Fortitude {d['Fortitude']}, "
               f"Resistência {resistencia}, Vontade {d['Vontade']}")
    ataques = [texto_ataque(a) for a in val["ataques"]]

    partes = []
    for secao, valor in rel["custos"].items():
        rotulo = npc.get("rotulo_poderes", NOMES_DE_SECAO[secao]) if secao == "poderes" else NOMES_DE_SECAO[secao]
        if valor is None:
            partes.append(f"{rotulo} ?")
        elif rel["origem_dos_custos"][secao] == "informado":
            partes.append(f"{rotulo} {valor} (informado)")
        else:
            partes.append(f"{rotulo} {valor}")
    total = rel["total_pp"] if rel["total_pp"] is not None else "?"
    totais = " + ".join(partes) + f" = {total} PP"
    if rel.get("orcamento") is not None:
        totais += f" (orçamento {rel['orcamento']} PP)"

    pe = val["pontos_equipamento"]
    if pe.get("gratuito"):
        texto_pe = "Equipamento pago em dólares (não usa pontos de poder)"
    else:
        texto_pe = f"{pe['usados']} de {pe['disponiveis']} pontos de equipamento"
    return {
        "habilidades": habilidades,
        "pericias": pericias,
        "vantagens": vantagens,
        "poderes": poderes,
        "equipamento": val["itens"],
        "pontos_equipamento": texto_pe,
        "iniciativa": _sinal(val["iniciativa"]),
        "ataques": ataques,
        "defesas": defesas,
        "totais": totais,
        "complicacoes": [texto_complicacao(c) for c in npc.get("complicacoes", [])],
        "dinheiro": texto_dinheiro(npc["dinheiro"]) if npc.get("dinheiro") else "",
        "de_fora": texto_de_fora(npc),
    }


def texto_de_fora(npc):
    """O que o PJ queria (ou sorteou) mas não coube no NP: armas pagas em pontos e implantes."""
    partes = []
    pe = npc.get("pontos_de_equipamento") or {}
    if pe.get("fora_do_np"):
        partes.append("Armas que não cabem no NP: " + ", ".join(pe["fora_do_np"]))
    implantes = npc.get("implantes") or {}
    if implantes.get("fora"):
        partes.append(f"{npc.get('rotulo_poderes', 'Poderes')} que não cabem no NP: " + "; ".join(implantes["fora"]))
    return ". ".join(partes) + "." if partes else ""


def texto_complicacao(complicacao):
    rotulo = "Motivação" if complicacao["categoria"] == "motivacao" else complicacao["nome"]
    nome = f"{rotulo} ({complicacao['nome']})" if complicacao["categoria"] == "motivacao" else rotulo
    return f"{nome}: {complicacao['detalhe']}" if complicacao.get("detalhe") else nome


def dolares(valor, moeda="$"):
    """$1.234,50 (faroeste), 2.550eb (cyberpunk) ou 15 po (fantasia): moeda com letras vai depois."""
    numero = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".").replace(",00", "")
    if moeda == "eb":
        return numero + moeda
    return f"{numero} {moeda}" if moeda[:1].isalpha() else moeda + numero


def texto_dinheiro(dinheiro):
    moeda = dinheiro.get("moeda", "$")
    texto = (f"{dinheiro['condicao']}: {dolares(dinheiro['inicial'], moeda)} iniciais, "
             f"{dolares(dinheiro['gasto'], moeda)} gastos, sobram {dolares(dinheiro['restante'], moeda)}")
    implantes = [c for c in dinheiro["compras"] if c.get("implante")]
    if implantes:
        texto += ("; cyberware: " + ", ".join(f"{c['nome']} ({dolares(c['preco'], moeda)})" for c in implantes))
    if dinheiro.get("subiu_de"):
        texto += (f". A condição financeira subiu de {dinheiro['subiu_de']} para pagar os itens "
                  f"(+{dinheiro['pontos_da_riqueza']} PP em Benefício: Riqueza)")
    if dinheiro.get("divida"):
        texto += f". DÍVIDA de {dolares(dinheiro['divida'], moeda)}: combine com o mestre (boa complicação)"
    a_combinar = [c["nome"] for c in dinheiro["compras"] if c["preco"] is None]
    if a_combinar:
        texto += f". Sem preço na tabela (combine com o mestre): {', '.join(a_combinar)}"
    if dinheiro.get("sem_dinheiro"):
        texto += f". Não coube no dinheiro: {', '.join(dinheiro['sem_dinheiro'])}"
    if dinheiro.get("fora_do_np"):
        texto += f". Não cabe no NP: {', '.join(dinheiro['fora_do_np'])}"
    return texto + "."


def texto(npc):
    """Bloco de texto no estilo das fichas do livro, para copiar e colar."""
    e = exibicao(npc)
    rel = npc["validacao"]
    modulos = ", ".join(f"{m['nome']} ({m['papel']})" for m in npc["modulos"])
    if npc.get("tipo") == "jogador":
        raca = f"{npc['raca']['nome']} · " if npc.get("raca") else ""
        cabecalho = [f"{raca}{npc['arquetipo']['nome']} · personagem de jogador · NP {npc['np_pretendido']}",
                     "Foco: " + ", ".join(m["nome"] for m in npc["modulos"])]
    else:
        cabecalho = [f"{npc['arquetipo']['nome']} · ficha-base {npc['faixa']['nome']} · NP pretendido "
                     f"{npc['np_pretendido']} (NP estimado pelos valores: {rel['np_efetivo']})",
                     f"Módulos: {modulos}"]
    linhas = [
        f"{npc['nome']}" + (f" (jogador: {npc['jogador']})" if npc.get("jogador") else ""),
        *cabecalho,
        "",
        e["habilidades"] + ".",
        "Perícias: " + ", ".join(e["pericias"]) + ".",
        "Vantagens: " + (", ".join(e["vantagens"]) or "nenhuma") + ".",
    ]
    if e["poderes"]:
        linhas.append(f"{npc.get('rotulo_poderes', 'Poderes')}: " + ", ".join(e["poderes"]) + ".")
    if e["equipamento"]:
        linhas.append("Equipamento: " + ", ".join(e["equipamento"]) + ".")
    if e["dinheiro"]:
        linhas.append(f"Dinheiro: {e['dinheiro']}")
    if e["de_fora"]:
        linhas.append(f"Ficou de fora: {e['de_fora']}")
    linhas += [
        f"Ataque: Inic {e['iniciativa']}, " + ", ".join(e["ataques"]) + ".",
        f"Defesa: {e['defesas']}.",
        f"Totais: {e['totais']}.",
    ]
    if npc["capanga"]:
        linhas.append("Capanga: não faz críticos contra quem não é capanga; qualquer falha num salvamento "
                      "aplica o pior resultado.")
    if e["complicacoes"]:
        linhas += ["Complicações: " + "; ".join(c.rstrip(".") for c in e["complicacoes"]) + "."]
    linhas += ["", f"Tática: {npc['tatica']}", f"Status: {rel['status_rotulo']}"]
    linhas += [f"Pendente: {p}" for p in rel["pendencias"]]
    linhas += [f"Aviso: {a}" for a in rel["avisos"]]
    return "\n".join(linhas)
