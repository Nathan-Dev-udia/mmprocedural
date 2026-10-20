"""Geração de fichas de personagem de jogador (PJ).

Diferenças em relação aos NPCs (livro básico, cap. 2):
- o personagem tem exatamente 15 PP por NP para gastar (mais o ajuste da Riqueza);
- precisa de pelo menos duas complicações, uma delas a Motivação;
- no faroeste, o equipamento é pago em dólares (regra de equipamento gratuito do Guia do Mestre);
  em gêneros com "equipamento": "pontos" (cyberpunk), é pago com a vantagem Equipamento
  (5 pontos de equipamento por graduação, livro básico cap. 7);
- gêneros com poderes do gênero (powers.json) dão implantes/poderes ao arquétipo, sorteados ou escolhidos.

Armas, itens e vantagens podem ser escolhidos pelo jogador ("manual") ou sorteados ("auto")
a partir das listas do arquétipo e do foco.

Fluxo: vantagens -> compras com o dinheiro inicial -> distribuição dos pontos restantes por
prioridade (escalar.py) até fechar o orçamento.
"""

import copy
import math
import random

from . import escalar
from . import formatter
from . import rules
from . import validator
from .generator import GeneratorError

OPCOES_DE_VALIDACAO = {"equipamento_gratuito": True}

# Vantagens que o gerador de PJ não oferece: o equipamento é pago em dólares, e capangas/parceiros
# exigem fichas próprias.
VANTAGENS_FORA_DO_PJ = {"Equipamento", "Capanga", "Parceiro", "Benefício"}

# Perícias úteis a qualquer personagem do Oeste, usadas só para fechar o orçamento.
PERICIAS_DE_RESERVA = ["Percepção", "Atletismo", "Intuição", "Furtividade", "Acrobacia", "Persuasão",
                       "Enganação", "Intimidação", "Investigação", "Especialidade: Cavalgar"]


def _arquetipo(dados, arquetipo_id):
    arquetipo = dados["jogador"]["arquetipos"].get(arquetipo_id)
    if arquetipo is None:
        raise GeneratorError(f"Arquétipo de jogador '{arquetipo_id}' não existe.")
    return arquetipo


def catalogo_do_jogador(dados):
    """Itens que um PJ pode comprar: tudo que tem categoria no catálogo."""
    return [item for item in dados["equipamentos"].values() if item.get("categoria")]


def vantagens_do_jogador(dados):
    """Vantagens que fazem sentido numa ficha de PJ (no faroeste, só as que combinam com o gênero)."""
    faroeste = dados["genero"]["id"] == "faroeste"
    return [v for v in dados["vantagens_detalhes"]
            if v["nome"] not in VANTAGENS_FORA_DO_PJ and not (faroeste and v.get("faroeste") == "Não combina")]


def equipamento_em_pontos(dados):
    """True se o gênero paga o equipamento com a vantagem Equipamento em vez de dinheiro."""
    return dados["configuracoes"].get("equipamento", "dinheiro") == "pontos"


def opcoes_de_validacao(dados):
    return {} if equipamento_em_pontos(dados) else dict(OPCOES_DE_VALIDACAO)


def moeda(dados):
    return dados["configuracoes"].get("moeda", "$")


def implantes_em_dinheiro(dados):
    """True se os implantes também custam dinheiro (o preço do cyberware), além dos PP do poder."""
    return bool(dados["configuracoes"].get("implantes_em_dinheiro")) and not equipamento_em_pontos(dados)


def preco_do_implante(dados, implante_id):
    if not implantes_em_dinheiro(dados):
        return 0
    return dados["poderes_do_genero"][implante_id].get("preco") or 0


def implantes_do_jogador(dados):
    """Poderes do gênero (implantes no cyberpunk) que um PJ pode escolher."""
    return list(dados.get("poderes_do_genero", {}).values())


# ---------------------------------------------------------------- complicações

def sortear_complicacoes(dados, arquetipo_id, rng):
    """Uma motivação e duas complicações coerentes com o arquétipo (às vezes uma surpresa da lista geral)."""
    arquetipo = _arquetipo(dados, arquetipo_id)
    sugestoes = arquetipo["sugestoes"]
    escolhidas = [{"categoria": "motivacao", "nome": rng.choice(sugestoes["motivacoes"]), "detalhe": ""}]
    outras = rng.sample(sugestoes["complicacoes"], k=min(2, len(sugestoes["complicacoes"])))
    if rng.random() < 0.3:
        surpresa = rng.choice(dados["complicacoes"]["complicacoes"])
        if surpresa["nome"] not in {c["nome"] for c in outras}:
            outras[-1] = {"nome": surpresa["nome"], "detalhe": surpresa["exemplo"]}
    escolhidas += [{"categoria": "complicacao", "nome": c["nome"], "detalhe": c["detalhe"]} for c in outras]
    return escolhidas


def _conferir_complicacoes(complicacoes):
    if not isinstance(complicacoes, list):
        raise GeneratorError("As complicações precisam vir como uma lista.")
    motivacoes = [c for c in complicacoes if c.get("categoria") == "motivacao" and c.get("nome")]
    validas = [c for c in complicacoes if c.get("nome")]
    if not motivacoes:
        raise GeneratorError("Escolha uma Motivação: todo personagem precisa de uma.")
    if len(validas) < 2:
        raise GeneratorError("Escolha pelo menos duas complicações no total (a Motivação conta como uma).")
    return [{"categoria": c.get("categoria", "complicacao"), "nome": str(c["nome"]),
             "detalhe": str(c.get("detalhe", "")).strip()} for c in validas]


# ---------------------------------------------------------------- vantagens

def _vantagens_automaticas(arquetipo, foco, rng):
    """Essenciais do arquétipo e do foco, mais 0 a 2 opcionais do arquétipo."""
    vantagens = {nome: 1 for nome in arquetipo["vantagens_essenciais"] + foco.get("vantagens", [])}
    opcionais = [v for v in arquetipo["vantagens_opcionais"] if v not in vantagens]
    for nome in rng.sample(opcionais, k=min(len(opcionais), rng.randint(0, 2))):
        vantagens[nome] = 1
    return vantagens


def _vantagens_escolhidas(dados, nomes, orcamento):
    if not isinstance(nomes, list):
        raise GeneratorError("As vantagens escolhidas precisam vir como uma lista.")
    vantagens = {}
    for nome in nomes:
        nome = str(nome).strip()
        if rules.nome_base(nome) not in dados["vantagens"]:
            raise GeneratorError(f"Vantagem desconhecida: '{nome}'.")
        vantagens[nome] = 1
    if len(vantagens) > orcamento:
        raise GeneratorError(f"As vantagens escolhidas custam {len(vantagens)} PP, mais que o orçamento de {orcamento} PP.")
    return vantagens


# ---------------------------------------------------------------- equipamento

def _cabe_no_np(item, np, vantagens):
    """Uma arma cabe no NP se o efeito, somado só ao bônus das vantagens de ataque, não passa do limite."""
    ataque = item.get("ataque")
    if not ataque:
        return True
    teto = rules.limites_do_np(np)
    if ataque["tipo"] == "area":
        return ataque["efeito"] <= teto["efeito_sem_ataque"]
    bonus = vantagens.get(rules.VANTAGEM_ATAQUE[ataque["tipo"]], 0)
    return bonus + ataque["efeito"] <= teto["ataque_mais_efeito"]


def _equipamento_automatico(dados, arquetipo, foco, np, vantagens, rng):
    """Lista de compras coerente com o arquétipo e o foco, na ordem de prioridade."""
    catalogo = dados["equipamentos"]
    cabe = [i for i in arquetipo["armas"]["principais"] if _cabe_no_np(catalogo[i], np, vantagens)]
    lista = []
    armas_do_foco = [i for i in foco.get("armas", []) if _cabe_no_np(catalogo[i], np, vantagens)]
    if armas_do_foco:
        lista.append(rng.choice(armas_do_foco))
    # Se o foco já deu uma arma do mesmo tipo (ex.: um rifle de precisão), não compra outra principal igual.
    pericias_do_foco = {catalogo[i].get("ataque", {}).get("pericia") for i in lista}
    cabe = [i for i in cabe if catalogo[i]["ataque"]["pericia"] not in pericias_do_foco]
    if cabe:
        lista.append(rng.choice(cabe))
    secundarias = [i for i in arquetipo["armas"]["secundarias"]
                   if i not in lista and _cabe_no_np(catalogo[i], np, vantagens)]
    secundaria = rng.choice(secundarias) if secundarias and rng.random() < 0.6 else None
    armas = lista + ([secundaria] if secundaria else [])
    municoes = []
    for arma in armas:
        municao = catalogo[arma].get("municao")
        if municao and municao not in municoes:
            municoes.append(municao)
    opcionais = rng.sample(arquetipo["itens"]["opcionais"], k=min(len(arquetipo["itens"]["opcionais"]),
                                                                    rng.randint(1, 3)))
    ordem = (lista + municoes + arquetipo["itens"]["essenciais"] + foco.get("itens", [])
             + ([secundaria] if secundaria else []) + opcionais)
    sem_repetir = []
    for item in ordem:
        if item not in sem_repetir:
            sem_repetir.append(item)
    return sem_repetir


def _comprar(dados, itens, dinheiro, obrigatorio=False):
    """Compra os itens na ordem da lista. Itens sem preço entram como 'a combinar'.

    obrigatorio=True (escolha do jogador): se o dinheiro não der, é erro em vez de pular o item.
    """
    compras, restante, sem_dinheiro = [], dinheiro, []
    for item_id in itens:
        item = dados["equipamentos"][item_id]
        preco = item.get("preco")
        if preco is None:
            compras.append({"id": item_id, "nome": item["nome"], "preco": None})
        elif preco <= restante + 1e-9:
            compras.append({"id": item_id, "nome": item["nome"], "preco": preco})
            restante -= preco
        else:
            sem_dinheiro.append(item["nome"])
    if obrigatorio and sem_dinheiro:
        total = sum(dados["equipamentos"][i].get("preco") or 0 for i in itens)
        raise GeneratorError(f"Os itens escolhidos custam {formatter.dolares(total, moeda(dados))}, mas o personagem "
                             f"só tem {formatter.dolares(dinheiro, moeda(dados))}.")
    return compras, round(restante, 2), sem_dinheiro


def custo_em_pontos(riqueza):
    """Quanto uma condição financeira custa em PP (Benefício comprado menos o ponto devolvido pela Riqueza baixa)."""
    return riqueza["beneficio"] - riqueza["ajuste_de_pontos"]


def riqueza_que_paga(dados, atual, total):
    """A condição financeira mais barata, sem descer da atual, cujo dinheiro cobre o total."""
    opcoes = [r for r in dados["jogador"]["riqueza"]
              if r["dinheiro"] >= total and custo_em_pontos(r) >= custo_em_pontos(atual)]
    if not opcoes:
        maior = max(dados["jogador"]["riqueza"], key=lambda r: r["dinheiro"])
        raise GeneratorError(f"Os itens escolhidos custam {formatter.dolares(total, moeda(dados))}, mais que o "
                             f"dinheiro da maior condição financeira ({maior['nome']}: "
                             f"{formatter.dolares(maior['dinheiro'], moeda(dados))}).")
    return min(opcoes, key=lambda r: (custo_em_pontos(r), r["dinheiro"]))


def _tirar_armas_acima_do_np(dados, ficha, compras, troco, np):
    """Remove (e devolve o dinheiro de) armas que já passam do limite do NP só com as vantagens iniciais."""
    fora_do_np = []
    while True:
        relatorio = validator.validar(ficha, np, dados["equipamentos"], OPCOES_DE_VALIDACAO)
        nomes_com_problema = {c["nome"].split(":")[0] for c in relatorio["limites"] if not c["ok"]}
        culpada = next((c for c in compras if c["nome"] in nomes_com_problema), None)
        if culpada is None:
            return compras, troco, fora_do_np
        compras = [c for c in compras if c is not culpada]
        ficha["equipamento"].remove(culpada["id"])
        troco = round(troco + (culpada["preco"] or 0), 2)
        fora_do_np.append(culpada["nome"])


def _sincronizar_equipamento(dados, ficha):
    """Graduação da vantagem Equipamento que cobre os itens da ficha (5 pontos por graduação)."""
    usados = sum(dados["equipamentos"][i].get("custo") or 0 for i in ficha["equipamento"])
    graduacao = math.ceil(usados / rules.PONTOS_DE_EQUIPAMENTO_POR_GRADUACAO)
    if graduacao:
        ficha["vantagens"][rules.VANTAGEM_EQUIPAMENTO] = graduacao
    else:
        ficha["vantagens"].pop(rules.VANTAGEM_EQUIPAMENTO, None)
    return usados, graduacao


def _cortar_equipamento(dados, lista, teto_de_graduacoes):
    """Corta itens do fim da lista (os menos importantes) até a vantagem Equipamento caber no teto."""
    lista = list(lista)
    while lista:
        usados = sum(dados["equipamentos"][i].get("custo") or 0 for i in lista)
        if math.ceil(usados / rules.PONTOS_DE_EQUIPAMENTO_POR_GRADUACAO) <= teto_de_graduacoes:
            break
        lista.pop()
    return lista


def _limites_estourados(dados, ficha, np, opcoes):
    relatorio = validator.validar(ficha, np, dados["equipamentos"], opcoes)
    return [c for c in relatorio["limites"] if not c["ok"]], relatorio


def _tirar_itens_acima_do_np(dados, ficha, np, opcoes):
    """Versão para equipamento em pontos: tira armas que passam do NP e devolve os nomes."""
    fora = []
    while True:
        estourados, _ = _limites_estourados(dados, ficha, np, opcoes)
        nomes = {c["nome"].split(":")[0] for c in estourados}
        culpado = next((i for i in ficha["equipamento"] if dados["equipamentos"][i]["nome"] in nomes), None)
        if culpado is None:
            return fora
        ficha["equipamento"].remove(culpado)
        fora.append(dados["equipamentos"][culpado]["nome"])


def _implantes_automaticos(arquetipo, foco, rng):
    implantes = arquetipo.get("implantes", {})
    lista = list(implantes.get("essenciais", [])) + list(foco.get("implantes", []))
    opcionais = [i for i in implantes.get("opcionais", []) if i not in lista]
    lista += rng.sample(opcionais, k=min(len(opcionais), rng.randint(0, 2)))
    return list(dict.fromkeys(lista))


def _instalar_implantes(dados, ficha, ids, np, opcoes, teto_de_pontos=None, dinheiro=None):
    """Põe os poderes do gênero na ficha, um por um; os que estouram o NP (ou o teto de PP) ficam de fora.

    dinheiro: quanto há para pagar o cyberware (gêneros com implantes_em_dinheiro). No sorteio, o implante
    que não cabe no dinheiro é pulado; na escolha do jogador, fica anotado como de fora.
    Devolve (instalados, fora, compras).
    """
    instalados, fora, compras = [], [], []
    gasto, restante = 0, dinheiro
    for implante_id in ids:
        item = dados["poderes_do_genero"][implante_id]
        poder = copy.deepcopy(item["poder"])
        poder["nome_curto"] = item["nome"]
        poder["descricao"] = item.get("descricao", "")
        preco = preco_do_implante(dados, implante_id)
        if teto_de_pontos is not None and gasto + poder["custo_informado"] > teto_de_pontos:
            continue
        if restante is not None and preco > restante + 1e-9:
            if teto_de_pontos is None:
                fora.append(f"{item['nome']} (custa {formatter.dolares(preco, moeda(dados))}; não coube no dinheiro)")
            continue
        ficha["poderes"][implante_id] = poder
        estourados, _ = _limites_estourados(dados, ficha, np, opcoes)
        if estourados:
            del ficha["poderes"][implante_id]
            fora.append(f"{item['nome']} ({estourados[0]['nome']} passaria de {estourados[0]['maximo']})")
            continue
        gasto += poder["custo_informado"]
        instalados.append(implante_id)
        if preco:
            compras.append({"id": implante_id, "nome": item["nome"], "preco": preco, "implante": True})
            restante -= preco
    return instalados, fora, compras


# ---------------------------------------------------------------- distribuição dos pontos

def _pericias_das_armas(dados, ficha):
    """Perícias de ataque das armas e dos poderes que a ficha carrega (na ordem em que entraram)."""
    ataques = [dados["equipamentos"][i].get("ataque") for i in ficha["equipamento"]]
    ataques += [p.get("ataque") for p in ficha["poderes"].values()]
    return list(dict.fromkeys(a["pericia"] for a in ataques if a and a.get("pericia")))


def _passos(dados, arquetipo, foco, vantagens_extras, so_vantagens_escolhidas, vantagens, ficha=None):
    reserva = dados["configuracoes"].get("pericias_de_reserva", PERICIAS_DE_RESERVA)
    passos = [escalar.ler_passo(p) for p in foco.get("prioridades", [])]
    # As armas que o personagem de fato carrega vêm logo depois do foco: não adianta treinar fuzil sem fuzil.
    passos += [{"tipo": "pericia", "nome": p} for p in (_pericias_das_armas(dados, ficha) if ficha else [])][:2]
    passos += [escalar.ler_passo(p) for p in arquetipo["prioridades"]]
    passos += [escalar.ler_passo(p) for p in dados["configuracoes"].get("prioridades_gerais", [])]
    passos += [{"tipo": "vantagem", "nome": v} for v in vantagens_extras]
    passos += [{"tipo": "pericia", "nome": p} for p in reserva]
    if so_vantagens_escolhidas:
        # Com vantagens escolhidas pelo jogador, o gerador só sobe graduações das que ele marcou.
        passos = [p for p in passos if p["tipo"] != "vantagem" or p["nome"] in vantagens]
    return escalar.sem_repetidos(passos)


def gerar_personagem(dados, arquetipo_id, np, foco_id, riqueza_id, complicacoes,
                     nome=None, jogador="", rng=None, equipamento=None, vantagens=None, implantes=None):
    """Gera uma ficha de PJ.

    equipamento: {"modo": "auto"} (padrão) ou {"modo": "manual", "ids": [...], "excesso": "pontos" | "divida"}.
                 Com equipamento em dinheiro, se os itens escolhidos passarem do dinheiro: "pontos" (padrão)
                 sobe a condição financeira comprando Benefício (Riqueza); "divida" gera a ficha com a dívida
                 anotada. Com equipamento em pontos, os itens viram graduações da vantagem Equipamento.
    vantagens:   {"modo": "auto"} (padrão) ou {"modo": "manual", "nomes": [...]}.
    implantes:   {"modo": "auto"} (padrão) ou {"modo": "manual", "ids": [...]} (só em gêneros com powers.json).
    """
    arquetipo = _arquetipo(dados, arquetipo_id)
    config = dados["configuracoes"]
    em_pontos = equipamento_em_pontos(dados)
    if np not in config["nps_jogador"]:
        raise GeneratorError(f"NP {np} não está disponível. Escolha entre {config['nps_jogador']}.")
    foco = next((f for f in arquetipo["focos"] if f["id"] == foco_id), None)
    if foco is None:
        raise GeneratorError(f"O foco '{foco_id}' não existe para {arquetipo['nome']}.")
    riqueza = next((r for r in dados["jogador"]["riqueza"] if r["id"] == riqueza_id), None)
    if riqueza is None and em_pontos:
        riqueza = dados["jogador"]["riqueza"][0]
    if riqueza is None:
        raise GeneratorError(f"Opção de riqueza '{riqueza_id}' não existe.")
    complicacoes = _conferir_complicacoes(complicacoes)
    equipamento = equipamento or {"modo": "auto"}
    vantagens_pedidas = vantagens or {"modo": "auto"}
    implantes_pedidos = implantes or {"modo": "auto"}
    rng = rng or random.Random()
    opcoes = opcoes_de_validacao(dados)
    rotulo = config.get("rotulo_poderes", "Poderes")
    tem_implantes = bool(dados.get("poderes_do_genero"))

    # Equipamento escolhido: confere os itens e, se passar do dinheiro, decide como pagar.
    manual_equipamento = equipamento.get("modo") == "manual"
    riqueza_escolhida, divida = riqueza, 0
    if manual_equipamento:
        ids = [str(i) for i in equipamento.get("ids", [])]
        desconhecidos = [i for i in ids if i not in dados["equipamentos"]
                         or not dados["equipamentos"][i].get("categoria")]
        if desconhecidos:
            raise GeneratorError(f"Itens desconhecidos: {', '.join(desconhecidos)}.")
        total = round(sum(dados["equipamentos"][i].get("preco") or 0 for i in ids), 2)
        if implantes_pedidos.get("modo") == "manual" and tem_implantes:
            total += sum(preco_do_implante(dados, i) for i in implantes_pedidos.get("ids", [])
                         if i in dados["poderes_do_genero"])
        if not em_pontos and total > riqueza["dinheiro"]:
            if equipamento.get("excesso", "pontos") == "divida":
                divida = round(total - riqueza["dinheiro"], 2)
            else:
                riqueza = riqueza_que_paga(dados, riqueza, total)

    orcamento = rules.orcamento_de_jogador(np) + riqueza["ajuste_de_pontos"]

    # Vantagens
    manual_vantagens = vantagens_pedidas.get("modo") == "manual"
    if manual_vantagens:
        vantagens = _vantagens_escolhidas(dados, vantagens_pedidas.get("nomes", []), orcamento - riqueza["beneficio"])
        extras = []
    else:
        vantagens = _vantagens_automaticas(arquetipo, foco, rng)
        extras = [v for v in arquetipo["vantagens_opcionais"] if v not in vantagens]
    if riqueza["beneficio"]:
        vantagens["Benefício (Riqueza)"] = riqueza["beneficio"]
    if rules.VANTAGEM_SORTE in vantagens:
        vantagens[rules.VANTAGEM_SORTE] = min(vantagens[rules.VANTAGEM_SORTE], max(1, rules.limite_de_sorte(np)))

    ficha = {
        "habilidades": {h: 0 for h in rules.HABILIDADES},
        "defesas_compradas": {},
        "pericias": {},
        "vantagens": vantagens,
        "equipamento": [],
        "ataque_desarmado": True,
        "poderes": {},
        "fontes": [],
    }

    # Equipamento
    compras, troco, sem_dinheiro, fora_do_np, pontos_de_equipamento = [], 0, [], [], None
    if em_pontos:
        if manual_equipamento:
            lista = ids
        else:
            # Sorteado: no máximo ~1/6 do orçamento vai para a vantagem Equipamento.
            lista = _equipamento_automatico(dados, arquetipo, foco, np, vantagens, rng)
            lista = _cortar_equipamento(dados, lista, max(1, orcamento // 6))
        ficha["equipamento"] = list(lista)
        fora_do_np = _tirar_itens_acima_do_np(dados, ficha, np, opcoes)
        usados, graduacao = _sincronizar_equipamento(dados, ficha)
        pontos_de_equipamento = {
            "usados": usados, "graduacao": graduacao,
            "disponiveis": graduacao * rules.PONTOS_DE_EQUIPAMENTO_POR_GRADUACAO,
            "itens": [{"id": i, "nome": dados["equipamentos"][i]["nome"], "custo": dados["equipamentos"][i].get("custo")}
                      for i in ficha["equipamento"]],
            "fora_do_np": fora_do_np,
        }
    else:
        if manual_equipamento:
            compras, troco, sem_dinheiro = _comprar(dados, ids, riqueza["dinheiro"] + divida, obrigatorio=True)
        else:
            lista = _equipamento_automatico(dados, arquetipo, foco, np, vantagens, rng)
            compras, troco, sem_dinheiro = _comprar(dados, lista, riqueza["dinheiro"])
        ficha["equipamento"] = [c["id"] for c in compras]
        compras, troco, fora_do_np = _tirar_armas_acima_do_np(dados, ficha, compras, troco, np)

    # Implantes / poderes do gênero (no cyberpunk, pagos também com o dinheiro que sobrou dos itens)
    manual_implantes = implantes_pedidos.get("modo") == "manual"
    instalados, implantes_fora, compras_de_implantes = [], [], []
    caixa = troco if implantes_em_dinheiro(dados) else None
    if tem_implantes:
        if manual_implantes:
            pedidos = list(dict.fromkeys(str(i) for i in implantes_pedidos.get("ids", [])))
            desconhecidos = [i for i in pedidos if i not in dados["poderes_do_genero"]]
            if desconhecidos:
                raise GeneratorError(f"{rotulo} desconhecidos: {', '.join(desconhecidos)}.")
            instalados, implantes_fora, compras_de_implantes = _instalar_implantes(
                dados, ficha, pedidos, np, opcoes, dinheiro=caixa)
        else:
            sorteados = _implantes_automaticos(arquetipo, foco, rng)
            instalados, implantes_fora, compras_de_implantes = _instalar_implantes(
                dados, ficha, sorteados, np, opcoes, teto_de_pontos=max(4, orcamento * 35 // 100), dinheiro=caixa)
    if compras_de_implantes:
        compras = compras + compras_de_implantes
        troco = round(troco - sum(c["preco"] for c in compras_de_implantes), 2)

    inicial = validator.validar(ficha, np, dados["equipamentos"], opcoes)["total_pp"] or 0
    if inicial > orcamento:
        raise GeneratorError(
            f"As escolhas já custam {inicial} PP (vantagens, equipamento e {rotulo.lower()}), mais que o "
            f"orçamento de {orcamento} PP do NP {np}. Tire alguma coisa ou suba o NP.")

    passos = _passos(dados, arquetipo, foco, extras, manual_vantagens, vantagens, ficha)
    ficha = escalar.subir(
        ficha, np, passos, dados["equipamentos"], rng,
        objetivo=lambda _f, relatorio: (relatorio["total_pp"] or 0) >= orcamento,
        opcoes_validacao=opcoes, orcamento=orcamento, max_passos=800,
    )
    regras = dict(opcoes, orcamento=orcamento)
    relatorio = validator.validar(ficha, np, dados["equipamentos"], regras)

    if not nome:
        lista_de_nomes = dados["nomes"]["humano"]
        nome = f"{rng.choice(lista_de_nomes['nomes'])} {rng.choice(lista_de_nomes['sobrenomes'])}"

    if em_pontos:
        dinheiro = None
        observacao_do_equipamento = "Equipamento pago com a vantagem Equipamento (5 pontos por graduação). "
    else:
        # `troco` saiu de dinheiro + dívida; o saldo real é troco - dívida (negativo = ainda devendo).
        saldo = round(troco - divida, 2)
        gasto = round(riqueza["dinheiro"] - saldo, 2)
        dinheiro = {"riqueza": riqueza["riqueza"], "condicao": riqueza["nome"], "inicial": riqueza["dinheiro"],
                    "gasto": gasto, "restante": max(saldo, 0), "compras": compras, "sem_dinheiro": sem_dinheiro,
                    "fora_do_np": fora_do_np, "divida": max(-saldo, 0),
                    "subiu_de": riqueza_escolhida["nome"] if riqueza is not riqueza_escolhida else None,
                    "pontos_da_riqueza": custo_em_pontos(riqueza) - custo_em_pontos(riqueza_escolhida),
                    "moeda": moeda(dados)}
        observacao_do_equipamento = ("Equipamento e cyberware pagos em eurobucks (preços do Cyberpunk RED). "
                                     if implantes_em_dinheiro(dados) else "Equipamento pago em dólares. ")
    observacao = (f"Orçamento de {orcamento} PP (15 × NP {np}"
                  + (f" + {riqueza['ajuste_de_pontos']} pela Riqueza baixa" if riqueza["ajuste_de_pontos"] else "")
                  + "). " + observacao_do_equipamento
                  + f"Armas e itens: {'escolhidos pelo jogador' if manual_equipamento else 'sorteados pelo arquétipo'}. "
                  + f"Vantagens: {'escolhidas pelo jogador' if manual_vantagens else 'sorteadas pelo arquétipo'}.")
    escolhas = {"equipamento": "manual" if manual_equipamento else "auto",
                "vantagens": "manual" if manual_vantagens else "auto"}
    if tem_implantes:
        observacao += f" {rotulo}: {'escolhidos pelo jogador' if manual_implantes else 'sorteados pelo arquétipo'}."
        escolhas["implantes"] = "manual" if manual_implantes else "auto"
    return {
        "genero": dados["genero"]["id"],
        "rotulo_poderes": rotulo,
        "tipo": "jogador",
        "uid": f"{rng.getrandbits(32):08x}",
        "nome": nome,
        "jogador": jogador,
        "arquetipo": {"id": arquetipo["id"], "nome": arquetipo["nome"]},
        "capanga": False,
        "np_pretendido": np,
        "faixa": {"np": np, "nome": arquetipo["nome"],
                  "fonte": "Arquétipo de jogador do gênero; pontos distribuídos pelo gerador",
                  "observacao": observacao},
        "estilo": {"id": foco["id"], "nome": foco["nome"]},
        "modulos": [{"id": foco["id"], "nome": foco["nome"], "papel": "foco", "descricao": foco["descricao"],
                     "tatica": "", "tags": [], "status_dados": "validado", "fonte": "Foco do arquétipo"}],
        "combinacao": [foco["id"]],
        "repetida": False,
        "descricao": f"{arquetipo['conceito']} {foco['descricao']}",
        "tatica": foco["descricao"],
        "complicacoes": complicacoes,
        "dinheiro": dinheiro,
        "pontos_de_equipamento": pontos_de_equipamento,
        "implantes": {"instalados": instalados, "fora": implantes_fora} if tem_implantes else None,
        "escolhas": escolhas,
        "regras_validacao": regras,
        "ficha": ficha,
        "validacao": relatorio,
    }
