"""Geração de NPCs: escolhe a ficha-base, sorteia módulos e aplica à ficha.

Fluxo de um NPC:
 1. escolhe a faixa (ficha-base) do arquétipo para o NP pedido;
 2. filtra os módulos do arquétipo que aceitam esse NP;
 3. sorteia uma combinação conforme o estilo de variação;
 4. aplica os módulos à ficha-base;
 5. pede ao validador para conferir os limites do NP;
 6. se a combinação não servir, tenta outra (com um número máximo de tentativas).

O sorteio usa um random.Random recebido de fora, para os testes serem reproduzíveis.
"""

import copy
import random
from collections import Counter

from . import escalar
from . import rules
from . import validator

SECOES_NUMERICAS = ("habilidades", "defesas_compradas", "pericias", "vantagens")


class GeneratorError(Exception):
    """Pedido inválido: arquétipo, NP, estilo ou quantidade que não existem ou não servem."""


class ModuloInaplicavel(Exception):
    """O módulo não pode ser aplicado a esta ficha (ex.: substituir um item que ela não tem)."""


# ---------------------------------------------------------------- consultas

def nps_disponiveis(dados, arquetipo):
    """NPs que o arquétipo aceita: do NP da menor ficha-base até o np_maximo do arquétipo."""
    menor = min(faixa["np"] for faixa in arquetipo["faixas"])
    return [np for np in dados["configuracoes"]["nps_disponiveis"] if menor <= np <= arquetipo["np_maximo"]]


def faixa_para_np(arquetipo, np):
    """A ficha-base de maior NP que ainda cabe no NP pedido."""
    cabem = [faixa for faixa in arquetipo["faixas"] if faixa["np"] <= np]
    return max(cabem, key=lambda faixa: faixa["np"]) if cabem else None


def modulos_candidatos(dados, arquetipo_id, np):
    """Módulos do arquétipo cujos requisitos de NP aceitam o NP pedido."""
    candidatos = []
    for mod in dados["modulos"].values():
        requisitos = mod.get("requisitos", {})
        if arquetipo_id not in mod["arquetipos"]:
            continue
        if np < requisitos.get("np_min", 0) or np > requisitos.get("np_max", 99):
            continue
        candidatos.append(mod)
    return candidatos


def compativeis(mod_a, mod_b):
    """Dois módulos podem andar juntos se nenhum dos dois declara o outro como incompatível."""
    return (mod_b["id"] not in mod_a.get("incompativel_com", [])
            and mod_a["id"] not in mod_b.get("incompativel_com", []))


# ---------------------------------------------------------------- aplicação

def aplicar_modulos(ficha_base, modulos):
    """Devolve uma cópia da ficha-base com os módulos aplicados, na ordem: remove, substitui, adiciona."""
    ficha = copy.deepcopy(ficha_base)
    for secao in SECOES_NUMERICAS:
        ficha.setdefault(secao, {})
    ficha.setdefault("equipamento", [])
    ficha.setdefault("poderes", {})
    ficha.setdefault("fontes", [])

    for mod in modulos:
        for secao, nomes in mod.get("remove", {}).items():
            for nome in nomes:
                if secao == "equipamento":
                    ficha["equipamento"] = [i for i in ficha["equipamento"] if i != nome]
                else:
                    ficha[secao].pop(nome, None)

        substitui = mod.get("substitui", {})
        for antigo, novo in substitui.get("equipamento", {}).items():
            if antigo not in ficha["equipamento"]:
                raise ModuloInaplicavel(f"{mod['nome']}: a ficha não tem '{antigo}' para substituir.")
            ficha["equipamento"] = [novo if i == antigo else i for i in ficha["equipamento"]]
        for poder_id, novo in substitui.get("poderes", {}).items():
            if poder_id not in ficha["poderes"]:
                raise ModuloInaplicavel(f"{mod['nome']}: a ficha não tem o poder '{poder_id}' para substituir.")
            ficha["poderes"][poder_id] = copy.deepcopy(novo)

        adiciona = mod.get("adiciona", {})
        for secao in SECOES_NUMERICAS:
            for nome, delta in adiciona.get(secao, {}).items():
                novo_valor = ficha[secao].get(nome, 0) + delta
                if novo_valor == 0 and secao != "habilidades":
                    ficha[secao].pop(nome, None)
                else:
                    ficha[secao][nome] = novo_valor
        for item in adiciona.get("equipamento", []):
            if item not in ficha["equipamento"]:
                ficha["equipamento"].append(item)
        for poder_id, poder in adiciona.get("poderes", {}).items():
            ficha["poderes"][poder_id] = copy.deepcopy(poder)

        ficha["fontes"].append({"nome": f"Módulo {mod['nome']}", "status_dados": mod["status_dados"]})
    return ficha


# ---------------------------------------------------------------- escalada até o NP

def prioridades_do_modulo(mod, equipamentos):
    """Prioridades explícitas do módulo ou, se não houver, o que ele acrescenta (na ordem do cadastro)."""
    if "prioridades" in mod:
        return [escalar.ler_passo(p) for p in mod["prioridades"]]
    adiciona = mod.get("adiciona", {})
    passos = [{"tipo": "pericia", "nome": n} for n in adiciona.get("pericias", {})]
    passos += [{"tipo": "defesa", "nome": n} for n in adiciona.get("defesas_compradas", {})]
    passos += [{"tipo": "vantagem", "nome": n} for n in adiciona.get("vantagens", {})
               if rules.nome_base(n) in rules.VANTAGENS_ESCALAVEIS]
    itens = list(adiciona.get("equipamento", [])) + list(mod.get("substitui", {}).get("equipamento", {}).values())
    for item in itens:
        pericia = equipamentos[item].get("ataque", {}).get("pericia")
        if pericia:
            passos.append({"tipo": "pericia", "nome": pericia})
    return passos


def prioridades_do_npc(dados, arquetipo, modulos):
    passos = []
    for mod in modulos:
        passos += prioridades_do_modulo(mod, dados["equipamentos"])
    passos += [escalar.ler_passo(p) for p in arquetipo.get("prioridades", [])]
    passos += [escalar.ler_passo(p) for p in dados["configuracoes"].get("prioridades_gerais", [])]
    return escalar.sem_repetidos(passos)


def escalar_npc(dados, arquetipo, modulos, ficha, np, rng):
    """Sobe a ficha até uma fração sorteada dos tetos do NP (opção A)."""
    faixa = dados["configuracoes"].get("escala_npc", {"minimo": 0.7, "maximo": 1.0})
    alvo = rng.uniform(faixa["minimo"], faixa["maximo"])
    passos = prioridades_do_npc(dados, arquetipo, modulos)
    return escalar.subir(
        ficha, np, passos, dados["equipamentos"], rng,
        objetivo=lambda _ficha, relatorio: escalar.progresso(relatorio, passos, np) >= alvo,
        habilidade_maxima=arquetipo.get("habilidade_maxima", rules.HABILIDADE_MAXIMA_HUMANA),
    ), alvo


# ---------------------------------------------------------------- sorteio

def _peso(mod, estilo):
    if estilo["modo"] == "preferencia" and estilo["id"] in mod["estilos"]:
        return estilo.get("peso_preferido", 1)
    return 1


def _escolher(rng, opcoes, estilo):
    return rng.choices(opcoes, weights=[_peso(m, estilo) for m in opcoes], k=1)[0]


def tipos_do_arquetipo(dados, arquetipo_id, np):
    """Módulos que podem ser o principal (o "tipo" do NPC, ex.: Dragão azul) nesse NP."""
    return [m for m in modulos_candidatos(dados, arquetipo_id, np) if m.get("papel", "ambos") in ("principal", "ambos")]


def sortear_combinacao(rng, candidatos, estilo, max_extras, principais_evitar=frozenset(), tipo=None):
    """Escolhe o módulo principal e, talvez, um extra compatível. Devolve uma lista de módulos.

    tipo: id do módulo principal escolhido pelo usuário; só o extra é sorteado.
    """
    principais = [m for m in candidatos if m.get("papel", "ambos") in ("principal", "ambos")]
    if tipo:
        principais = [m for m in principais if m["id"] == tipo]
    elif estilo["modo"] == "tematico":
        principais = [m for m in principais if "tematico" in m["estilos"]]
        ineditos = [m for m in principais if m["id"] not in principais_evitar]
        principais = ineditos or principais
    if not principais:
        return []

    principal = _escolher(rng, principais, estilo)
    escolhidos = [principal]
    if max_extras > 0 and rng.random() < estilo.get("chance_extra", 0):
        extras = [m for m in candidatos
                  if m["id"] != principal["id"]
                  and m.get("papel", "ambos") in ("extra", "ambos")
                  and compativeis(principal, m)]
        if extras:
            escolhidos.append(_escolher(rng, extras, estilo))
    return escolhidos


def _gerar_nome(dados, arquetipo, estilo, principal, rng, nomes_usados):
    lista = dados["nomes"][arquetipo["nomes"]]
    nome = ""
    for _ in range(20):
        nome = rng.choice(lista["nomes"])
        if "sobrenomes" in lista:
            sobrenome = rng.choice(lista["sobrenomes"])
            if lista.get("apelidos") and rng.random() < 0.3:
                nome = f'{nome} "{rng.choice(lista["apelidos"])}" {sobrenome}'
            else:
                nome = f"{nome} {sobrenome}"
        if estilo["modo"] == "tematico" and principal.get("epiteto"):
            nome = f"{nome}, {principal['epiteto']}"
        if nome not in nomes_usados:
            break
    nomes_usados.add(nome)
    return nome


def _conferir_parametros(dados, arquetipo_id, np, estilo_id):
    arquetipo = dados["arquetipos"].get(arquetipo_id)
    if arquetipo is None:
        raise GeneratorError(f"Arquétipo '{arquetipo_id}' não existe.")
    estilo = dados["estilos"].get(estilo_id)
    if estilo is None:
        raise GeneratorError(f"Estilo de variação '{estilo_id}' não existe.")
    if np not in nps_disponiveis(dados, arquetipo):
        raise GeneratorError(f"O arquétipo {arquetipo['nome']} não aceita o NP {np}. "
                             f"NPs disponíveis: {nps_disponiveis(dados, arquetipo)}.")
    return arquetipo, estilo, faixa_para_np(arquetipo, np)


def _conferir_tipo(dados, arquetipo, np, tipo):
    if tipo and tipo not in {m["id"] for m in tipos_do_arquetipo(dados, arquetipo["id"], np)}:
        raise GeneratorError(f"O tipo '{tipo}' não existe para {arquetipo['nome']} no NP {np}.")


def gerar_npc(dados, arquetipo_id, np, estilo_id, rng,
              combinacoes_usadas=None, principais_usados=None, nomes_usados=None, tipo=None):
    """Gera um NPC. Devolve (npc, None) ou (None, motivo) se nenhuma combinação servir.

    tipo: id do módulo principal (o "tipo" escolhido na tela); sem tipo, o gerador sorteia.
    """
    arquetipo, estilo, faixa = _conferir_parametros(dados, arquetipo_id, np, estilo_id)
    _conferir_tipo(dados, arquetipo, np, tipo)
    combinacoes_usadas = combinacoes_usadas if combinacoes_usadas is not None else set()
    principais_usados = principais_usados if principais_usados is not None else set()
    nomes_usados = nomes_usados if nomes_usados is not None else set()
    config = dados["configuracoes"]

    candidatos = modulos_candidatos(dados, arquetipo_id, np)
    if not candidatos:
        return None, f"Nenhum módulo de {arquetipo['nome']} aceita o NP {np}."

    ficha_base = copy.deepcopy(faixa["ficha"])
    ficha_base["fontes"] = [{"nome": f"Ficha-base {faixa['nome']}", "status_dados": faixa["status_dados"]}]

    tentativas = config["tentativas_maximas"]
    motivos = Counter()
    for tentativa in range(tentativas):
        # Na primeira metade das tentativas, evita repetir o principal e a combinação;
        # na segunda, aceita repetição para não travar quando as opções inéditas não servem.
        primeira_metade = tentativa < tentativas // 2
        evitar = principais_usados if primeira_metade else frozenset()
        modulos = sortear_combinacao(rng, candidatos, estilo, config["modulos_extras_maximos"], evitar, tipo)
        if not modulos:
            return None, f"O estilo {estilo['nome']} não tem módulos para {arquetipo['nome']} no NP {np}."
        chave = frozenset(m["id"] for m in modulos)
        if chave in combinacoes_usadas and primeira_metade:
            motivos["combinação já usada no grupo"] += 1
            continue
        try:
            ficha = aplicar_modulos(ficha_base, modulos)
        except ModuloInaplicavel as erro:
            motivos[str(erro)] += 1
            continue
        relatorio = validator.validar(ficha, np, dados["equipamentos"])
        if relatorio["problemas"]:
            nomes_mods = " + ".join(m["nome"] for m in modulos)
            motivos[f"{nomes_mods}: {relatorio['problemas'][0]}"] += 1
            continue

        ficha, alvo = escalar_npc(dados, arquetipo, modulos, ficha, np, rng)
        relatorio = validator.validar(ficha, np, dados["equipamentos"])

        repetida = chave in combinacoes_usadas
        combinacoes_usadas.add(chave)
        principais_usados.add(modulos[0]["id"])
        npc = {
            "genero": dados["genero"]["id"],
            "rotulo_poderes": dados["configuracoes"].get("rotulo_poderes", "Poderes"),
            "uid": f"{rng.getrandbits(32):08x}",
            "nome": _gerar_nome(dados, arquetipo, estilo, modulos[0], rng, nomes_usados),
            "arquetipo": {"id": arquetipo["id"], "nome": arquetipo["nome"]},
            "capanga": arquetipo.get("capanga", False),
            "np_pretendido": np,
            "faixa": {"np": faixa["np"], "nome": faixa["nome"], "fonte": faixa["fonte"],
                      "observacao": faixa.get("observacao", "")},
            "estilo": {"id": estilo["id"], "nome": estilo["nome"]},
            "modulos": [{"id": m["id"], "nome": m["nome"], "papel": "principal" if i == 0 else "extra",
                         "descricao": m["descricao"], "tatica": m.get("tatica", ""), "tags": m["tags"],
                         "status_dados": m["status_dados"], "fonte": m.get("fonte", "")}
                        for i, m in enumerate(modulos)],
            "combinacao": sorted(chave),
            "repetida": repetida,
            "escala": round(alvo, 2),
            "descricao": " ".join([arquetipo["descricao"]] + [m["descricao"] for m in modulos]),
            "tatica": " ".join(m.get("tatica", "") for m in modulos).strip(),
            "ficha": ficha,
            "validacao": relatorio,
        }
        return npc, None

    mais_comuns = "; ".join(f"{motivo} ({vezes}x)" for motivo, vezes in motivos.most_common(3))
    return None, (f"Não encontrei uma combinação válida em {tentativas} tentativas. "
                  f"Motivos mais comuns: {mais_comuns}.")


def gerar_grupo(dados, arquetipo_id, np, estilo_id, quantidade, rng=None, tipo=None):
    """Gera vários NPCs, evitando repetir combinações de módulos enquanto houver alternativas.

    tipo: todos do mesmo tipo (módulo principal), variando só o extra, a ficha e o nome.
    """
    arquetipo, _, _ = _conferir_parametros(dados, arquetipo_id, np, estilo_id)
    _conferir_tipo(dados, arquetipo, np, tipo)
    maximo = dados["configuracoes"]["quantidade_maxima"]
    if not 1 <= quantidade <= maximo:
        raise GeneratorError(f"A quantidade deve ficar entre 1 e {maximo}.")
    rng = rng or random.Random()

    npcs, avisos = [], []
    usadas, principais, nomes = set(), set(), set()
    for _ in range(quantidade):
        npc, motivo = gerar_npc(dados, arquetipo_id, np, estilo_id, rng, usadas, principais, nomes, tipo)
        if npc is None:
            avisos.append(motivo)
            break
        npcs.append(npc)

    if len(npcs) < quantidade:
        avisos.append(f"Foram gerados {len(npcs)} de {quantidade} NPCs.")
    repetidos = sum(1 for npc in npcs if npc["repetida"])
    if repetidos and not tipo:   # com um tipo escolhido, repetir o principal é o esperado
        avisos.append(f"{repetidos} NPC(s) repetem a combinação de módulos de outro: não há variações "
                      "suficientes para este arquétipo, NP e estilo.")
    return {"npcs": npcs, "avisos": avisos}
