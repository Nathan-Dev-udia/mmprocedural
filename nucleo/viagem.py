"""Rolagem de eventos de viagem (dados/viagem): clima, se algo acontece, tipo, evento, criatura e intensidade.

Cada gênero é uma categoria: um arquivo dados/viagem/<genero>.json com as mesmas tabelas (hoje só a
fantasia medieval, igual à planilha dados/viagem/fantasia.xlsx). Cada rolagem pode vir
do jogador (dado físico) ou ser sorteada aqui; o resultado lista só as etapas que de fato foram roladas.
"""

import json
import random
from functools import lru_cache
from pathlib import Path

PASTA = Path(__file__).parent.parent / "dados" / "viagem"

# Etapas na ordem em que são roladas: (chave, nome na tela, faces do dado).
DADOS = {
    "clima": ("Clima", 100),
    "mudanca_clima": ("Clima muda?", 6),
    "evento": ("Acontece algo?", 20),
    "tipo": ("Tipo de evento", 100),
    "qual": ("Qual evento", 6),
    "criatura": ("Criatura", 100),
    "intensidade": ("Intensidade", 6),
}
PISTA = "Pista / presságio"
INTENSIDADE_DE_COMBATE = 3  # de "Encontro menor" para cima a criatura chega a lutar


@lru_cache(maxsize=1)
def _arquivos():
    return {caminho.stem: caminho for caminho in sorted(PASTA.glob("*.json"))}


def categorias():
    """Categorias disponíveis, uma por gênero que tem tabelas."""
    return [{"id": c, "nome": tabelas(c)["nome"], "descricao": tabelas(c)["descricao"]} for c in _arquivos()]


@lru_cache(maxsize=None)
def tabelas(categoria):
    caminho = _arquivos().get(categoria)
    if caminho is None:
        raise ValueError(f"Categoria de rolagem desconhecida: {categoria!r}.")
    return json.loads(caminho.read_text(encoding="utf-8"))


def opcoes(categoria):
    """O que a tela precisa para montar os campos da situação."""
    t = tabelas(categoria)
    return {
        "id": categoria,
        "nome": t["nome"],
        "descricao": t["descricao"],
        "areas": [{"id": a["id"], "descricao": f'{a["quando"]}. Evento com d20 ≥ {a["limiar"]}; {a["np"]}.'}
                  for a in t["areas"]],
        "periodos": [{"id": p["id"], "descricao": f'{p["horario"]}. {p["notas"]}'} for p in t["periodos"]],
        "estacoes": [{"id": e, "descricao": "Define a tabela de clima."} for e in t["estacoes"]],
        "terrenos": [{"id": x["id"], "descricao": x["inclui"]} for x in t["terrenos"]],
        "situacoes": [{"id": s["id"], "descricao": s["descricao"]} for s in t["situacoes"]],
        "climas": [c["nome"] for c in t["climas"]],
    }


def _por_id(lista, valor, campo, chave="id"):
    for item in lista:
        if item[chave] == valor:
            return item
    raise ValueError(f"{campo} desconhecido: {valor!r}.")


def _sinal(n):
    return f"+{n}" if n >= 0 else str(n)


def _escolher(itens, pesos, d100):
    """Escolhe proporcionalmente ao peso: o d100 vira uma fração do peso total."""
    alvo = d100 / 100 * sum(pesos)
    acumulado = 0
    for item, peso in zip(itens, pesos):
        acumulado += peso
        if peso > 0 and acumulado >= alvo - 1e-9:
            return item
    return next(i for i, p in zip(reversed(itens), reversed(pesos)) if p > 0)


def _faixa(itens, pesos, escolhido):
    """Faixa do d100 que corresponde ao item, quando os pesos somam 100 (ex.: "39–50")."""
    inicio = 1
    for item, peso in zip(itens, pesos):
        if item is escolhido:
            return f"{inicio}–{inicio + peso - 1}"
        inicio += peso
    return ""


def peso_da_criatura(t, criatura, area, periodo, terreno):
    fator_terreno = 1 if ("Qualquer" in criatura["terrenos"] or terreno in criatura["terrenos"]) else t["fator_fora_do_terreno"]
    return criatura["pesos"][area] * t["atividade"][criatura["atividade"]][periodo] * fator_terreno


def rolar(categoria, situacao, dados=None, clima_atual=None, combate_hoje=False, rng=None):
    """Rola um período de viagem nas tabelas da categoria (gênero).

    situacao: {"area", "periodo", "estacao", "terreno", "situacao"} com os ids das tabelas.
    dados: valores dos dados físicos, por etapa (chaves de DADOS); o que faltar é sorteado.
    clima_atual: nome do clima do período anterior. Sem ele, rola o clima do dia (d100);
        com ele, rola 1d6 e só troca o clima no 6.
    combate_hoje: já houve combate neste dia de viagem (regra de ritmo: no máximo 1 por dia).
    """
    t = tabelas(categoria)
    rng = rng or random.Random()
    dados = dados or {}
    area = _por_id(t["areas"], situacao.get("area"), "Área")
    periodo = _por_id(t["periodos"], situacao.get("periodo"), "Período")
    estacao = situacao.get("estacao")
    if estacao not in t["estacoes"]:
        raise ValueError(f"Estação desconhecida: {estacao!r}.")
    terreno = _por_id(t["terrenos"], situacao.get("terreno"), "Terreno")["id"]
    grupo = _por_id(t["situacoes"], situacao.get("situacao"), "Situação do grupo")
    etapas = []

    def dado(chave):
        nome, faces = DADOS[chave]
        valor = dados.get(chave)
        if valor in (None, ""):
            return rng.randint(1, faces), False
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{nome}: o d{faces} precisa ser um número.") from None
        if not 1 <= valor <= faces:
            raise ValueError(f"{nome}: o d{faces} vai de 1 a {faces} (veio {valor}).")
        return valor, True

    def etapa(chave, valor, informado, resultado, detalhe):
        nome, faces = DADOS[chave]
        etapas.append({"id": chave, "etapa": nome, "dado": f"d{faces}", "valor": valor, "informado": informado,
                       "resultado": resultado, "detalhe": detalhe})

    # 1. Clima: d100 no começo do dia; nos outros períodos, 1d6 e só muda no 6.
    climas = t["climas"]
    pesos_clima = [c["pesos"][estacao] for c in climas]
    clima = next((c for c in climas if c["nome"] == clima_atual), None)
    if clima is not None:
        valor, informado = dado("mudanca_clima")
        muda = valor == 6
        etapa("mudanca_clima", valor, informado, "Muda" if muda else f"Continua: {clima['nome']}",
              "No 6 o clima muda e rola de novo no d100.")
        if muda:
            clima = None
    if clima is None:
        valor, informado = dado("clima")
        clima = _escolher(climas, pesos_clima, valor)
        etapa("clima", valor, informado, clima["nome"],
              f'{_faixa(climas, pesos_clima, clima)} no {estacao.lower()}. {clima["viagem"]}')

    # 2. Acontece algo?
    valor, informado = dado("evento")
    mods = periodo["mod_evento"] + grupo["mod_evento"] + clima["mod_evento"]
    total = valor + mods
    acontece = total >= area["limiar"]
    partes = [f'{periodo["id"].lower()} {_sinal(periodo["mod_evento"])}']
    if grupo["mod_evento"]:
        partes.append(f'{grupo["id"].lower()} {_sinal(grupo["mod_evento"])}')
    if clima["mod_evento"]:
        partes.append(f'{clima["nome"].lower()} {_sinal(clima["mod_evento"])}')
    etapa("evento", valor, informado, "Sim, algo acontece" if acontece else "Nada acontece",
          f'{valor} {_sinal(mods)} ({", ".join(partes)}) = {total}; precisa de {area["limiar"]}+ na área {area["id"]}.')

    resultado = {"clima": {"nome": clima["nome"], "viagem": clima["viagem"], "regra": clima["regra"]},
                 "acontece": acontece, "tipo": None, "evento": None, "criatura": None, "intensidade": None,
                 "combate": False, "avisos": []}

    if acontece:
        # 3. Tipo de evento: d100 + mods, limitado a 1–100.
        valor, informado = dado("tipo")
        mods = periodo["mod_tipo"] + clima["mod_tipo"]
        ajustado = max(1, min(100, valor + mods))
        pesos_tipo = [x["pesos"][area["id"]] for x in t["tipos"]]
        tipo = _escolher(t["tipos"], pesos_tipo, ajustado)
        conta = f'{valor} {_sinal(mods)} = {ajustado}; ' if mods else ""
        etapa("tipo", valor, informado, tipo["nome"],
              f'{conta}{_faixa(t["tipos"], pesos_tipo, tipo)} na área {area["id"]}.')
        resultado["tipo"] = tipo["nome"]

        # 4. Qual evento: d6 dentro do tipo.
        valor, informado = dado("qual")
        evento = t["eventos"][tipo["nome"]][valor - 1]
        etapa("qual", valor, informado, evento["nome"], evento["descricao"])
        resultado["evento"] = evento

        # 5. Criatura: só da categoria do tipo, pesada por área, período e terreno.
        if tipo["categoria"]:
            valor, informado = dado("criatura")
            candidatas = [c for c in t["criaturas"] if c["categoria"] == tipo["categoria"]]
            pesos = [peso_da_criatura(t, c, area["id"], periodo["id"], terreno) for c in candidatas]
            criatura = _escolher(candidatas, pesos, valor)
            chance = round(100 * pesos[candidatas.index(criatura)] / sum(pesos))
            etapa("criatura", valor, informado, criatura["nome"],
                  f'NP {criatura["np"]} · {criatura["grupo"]} · {chance}% de chance entre os {tipo["categoria"].lower()}s nesta situação.')
            resultado["criatura"] = criatura

            # 6. Intensidade: d6 + mod. da área (só quando a criatura aparece).
            if tipo["nome"] != PISTA:
                valor, informado = dado("intensidade")
                total = max(1, min(len(t["intensidade"]), valor + area["mod_intensidade"]))
                intensidade = t["intensidade"][total - 1]
                etapa("intensidade", valor, informado, intensidade["nome"],
                      f'{valor} {_sinal(area["mod_intensidade"])} (área {area["id"]}) = {total}. {intensidade["descricao"]}')
                resultado["intensidade"] = intensidade
                resultado["combate"] = total >= INTENSIDADE_DE_COMBATE
                if resultado["combate"] and combate_hoje:
                    resultado["avisos"].append("Já houve um combate hoje. Pela regra de ritmo, troque este por pressão, "
                                               "perseguição ou um sinal da criatura.")

    resultado["etapas"] = etapas
    resultado["narrar"] = _para_narrar(resultado)
    return resultado


def _para_narrar(r):
    clima = r["clima"]
    linhas = [{"rotulo": "Clima", "texto": f'{clima["nome"]}: {clima["viagem"]}', "regra": clima["regra"]}]
    evento = r["evento"]
    if evento is None:
        linhas.append({"rotulo": "Cena", "texto": "Nada relevante neste período. Descreva a paisagem e o clima e avance a viagem."})
        return linhas
    linhas += [
        {"rotulo": "Cena", "texto": f'{evento["nome"]}: {evento["descricao"]}'},
        {"rotulo": "Opções do jogador", "texto": evento["opcoes"]},
        {"rotulo": "Nota do mestre", "texto": evento["reviravolta"]},
    ]
    criatura = r["criatura"]
    if criatura:
        prefixo = "Quem deixou o sinal: " if r["tipo"] == PISTA else ""
        linhas.append({"rotulo": "Criatura", "texto": f'{prefixo}{criatura["nome"]}. {criatura["nota"]}',
                       "ficha": criatura["ficha_base"], "bestiario_id": criatura["bestiario_id"]})
    if r["tipo"] == PISTA and criatura:
        linhas.append({"rotulo": "Intensidade", "texto": "É só uma pista: a criatura não aparece agora. "
                                                          "Se o grupo seguir o rastro, role a intensidade."})
    elif r["intensidade"]:
        linhas.append({"rotulo": "Intensidade", "texto": f'{r["intensidade"]["nome"]}. {r["intensidade"]["solo"]}'})
    return linhas
