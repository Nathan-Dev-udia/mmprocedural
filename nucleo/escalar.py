"""Motor que sobe uma ficha passo a passo, respeitando as regras.

Um "passo" é +1 numa característica: uma graduação de habilidade, perícia,
defesa ou vantagem. Os passos vêm de uma lista de prioridades (os primeiros
têm mais chance de ser escolhidos). Depois de cada passo, o validador confere
os limites do NP; se o passo quebrar algum limite, ele é descartado.

Usado de dois jeitos:
- NPC: sobe até a ficha chegar a uma fração dos tetos do NP (ex.: 70% a 100%).
- Personagem de jogador: sobe até gastar exatamente o orçamento de pontos.
"""

import copy

from . import rules
from . import validator

SECAO_DO_TIPO = {"habilidade": "habilidades", "pericia": "pericias",
                 "defesa": "defesas_compradas", "vantagem": "vantagens"}


def ler_passo(texto):
    """'pericia:Combate à Distância: Pistolas' -> {'tipo': 'pericia', 'nome': 'Combate à Distância: Pistolas'}."""
    tipo, _, nome = texto.partition(":")
    return {"tipo": tipo.strip(), "nome": nome.strip()}


def sem_repetidos(passos):
    vistos, saida = set(), []
    for passo in passos:
        chave = (passo["tipo"], passo["nome"])
        if chave not in vistos:
            vistos.add(chave)
            saida.append(passo)
    return saida


def aplicar_passo(ficha, passo):
    nova = copy.deepcopy(ficha)
    secao = nova.setdefault(SECAO_DO_TIPO[passo["tipo"]], {})
    secao[passo["nome"]] = secao.get(passo["nome"], 0) + 1
    return nova


# Tetos de graduação que o gerador respeita ao subir vantagens.
# Crítico Aprimorado e Sorte: limites do livro básico. Iniciativa Aprimorada: o livro não limita;
# o teto (NP ÷ 3, mínimo 1) é uma escolha do gerador para não despejar pontos em iniciativa.
TETOS_DE_VANTAGEM = {
    "Crítico Aprimorado": lambda np: 4,
    "Sorte": rules.limite_de_sorte,
    "Iniciativa Aprimorada": lambda np: max(1, np // 3),
}


def _passo_permitido(ficha, passo, habilidade_maxima, np):
    if passo["tipo"] == "habilidade":
        atual = ficha["habilidades"].get(passo["nome"], 0)
        # –5 é como as fichas guardam uma habilidade ausente ("—" no livro, ex.: o Vigor de um esqueleto):
        # ela não sobe.
        return rules.HABILIDADE_MINIMA < atual < habilidade_maxima
    if passo["tipo"] == "vantagem":
        atual = ficha.get("vantagens", {}).get(passo["nome"], 0)
        base = rules.nome_base(passo["nome"])
        if atual and base not in rules.VANTAGENS_ESCALAVEIS:
            return False
        teto = TETOS_DE_VANTAGEM.get(base)
        return teto is None or atual < teto(np)
    return True


def saturacao(passo, relatorio, ficha, np, habilidade_maxima):
    """Quão perto do teto (0 = longe, 1 = no teto) fica o que este passo sobe."""
    teto = rules.limites_do_np(np)
    valores = relatorio["valores"]
    d = valores["defesas"]
    ataques = [a for a in valores["ataques"] if a["bonus"] is not None]

    def sat_ataques(filtro):
        return max([(a["bonus"] + a["dano"]) / teto["ataque_mais_efeito"] for a in ataques if filtro(a)] or [0])

    esq = (d["Esquiva"] + d["Resistência"]) / teto["esquiva_mais_resistencia"]
    apa = (d["Aparar"] + valores["resistencia_plena"]) / teto["aparar_mais_resistencia"]
    fv = (d["Fortitude"] + d["Vontade"]) / teto["fortitude_mais_vontade"]
    tipo, nome = passo["tipo"], passo["nome"]

    if tipo == "pericia":
        pericia = valores["pericias"].get(nome)
        propria = pericia["total"] / teto["pericia"] if pericia else 0
        return max(propria, sat_ataques(lambda a: a["pericia"] == nome))
    if tipo == "defesa":
        return {"Esquiva": esq, "Aparar": apa}.get(nome, fv)
    if tipo == "habilidade":
        propria = ficha["habilidades"].get(nome, 0) / habilidade_maxima
        derivada = {
            "Des": sat_ataques(lambda a: a["tipo"] == "distancia"),
            "Lut": max(apa, sat_ataques(lambda a: a["tipo"] == "corpo")),
            "For": sat_ataques(lambda a: a["soma_forca"]),
            "Agi": esq,
            "Vig": max(esq, apa, fv),
            "Pro": fv,
        }.get(nome, 0)
        return max(propria, derivada)
    base = rules.nome_base(nome)
    atual = ficha.get("vantagens", {}).get(nome, 0)
    if base == "Ataque à Distância":
        return sat_ataques(lambda a: a["tipo"] == "distancia")
    if base == "Ataque Corpo-a-Corpo":
        return sat_ataques(lambda a: a["tipo"] == "corpo")
    if base == "Rolamento Defensivo":
        return max(esq, apa)
    if base in TETOS_DE_VANTAGEM:
        return atual / max(1, TETOS_DE_VANTAGEM[base](np))
    return 0


def _ordem_ponderada(passos, rng, saturacoes):
    """Embaralha dando mais chance aos primeiros da lista e muito menos ao que já está perto do teto.

    A chave de cada passo é random() elevado a um expoente: quanto maior o expoente, menor a chance
    de o passo vir primeiro. O expoente cresce com a posição na lista e explode perto do teto
    (saturação 0,9 multiplica por 100), então chegar ao máximo é possível, mas raro.
    """
    chaves = []
    for i, (passo, sat) in enumerate(zip(passos, saturacoes)):
        expoente = (1 + 0.35 * i) / max(0.03, 1 - sat) ** 2
        chaves.append((rng.random() ** expoente, passo))
    return [passo for _, passo in sorted(chaves, key=lambda par: par[0], reverse=True)]


def progresso(relatorio, passos, np):
    """Quão perto dos tetos do NP a ficha está, de 0 a 1.

    Média entre (a) as defesas e (b) o que for melhor entre o ataque e a perícia principal.
    """
    teto = rules.limites_do_np(np)
    valores = relatorio["valores"]
    d = valores["defesas"]
    defesas = sum([
        (d["Esquiva"] + d["Resistência"]) / teto["esquiva_mais_resistencia"],
        (d["Aparar"] + valores["resistencia_plena"]) / teto["aparar_mais_resistencia"],
        (d["Fortitude"] + d["Vontade"]) / teto["fortitude_mais_vontade"],
    ]) / 3
    ataque = max([(a["bonus"] + a["dano"]) / teto["ataque_mais_efeito"]
                  for a in valores["ataques"] if a["bonus"] is not None] or [0])
    nomes = {p["nome"] for p in passos if p["tipo"] == "pericia"}
    pericia = max([p["total"] / teto["pericia"] for nome, p in valores["pericias"].items() if nome in nomes] or [0])
    return (defesas + max(ataque, pericia)) / 2


def _no_teto(relatorio):
    """Quantos limites do NP estão exatamente no máximo."""
    return sum(1 for c in relatorio["limites"] if c["valor"] >= c["maximo"])


# Chance de aceitar um passo que leva algo exatamente ao teto do NP quando ainda há outras opções.
CHANCE_DE_ATINGIR_O_TETO = 0.01


def subir(ficha, np, passos, catalogo, rng, objetivo, opcoes_validacao=None,
          habilidade_maxima=rules.HABILIDADE_MAXIMA_HUMANA, orcamento=None, max_passos=500):
    """Aplica passos até `objetivo(ficha, relatorio)` ser verdadeiro ou nenhum passo caber.

    `orcamento`: se informado, nenhum passo pode deixar o total de PP acima dele.
    Passos que levam algo ao teto do NP ficam para depois (ou passam com 1% de chance).
    """
    relatorio = validator.validar(ficha, np, catalogo, opcoes_validacao)
    for _ in range(max_passos):
        if objetivo(ficha, relatorio):
            break
        saturacoes = [saturacao(p, relatorio, ficha, np, habilidade_maxima) for p in passos]
        adiados = []
        escolhido = None
        for passo in _ordem_ponderada(passos, rng, saturacoes):
            if not _passo_permitido(ficha, passo, habilidade_maxima, np):
                continue
            nova = aplicar_passo(ficha, passo)
            novo_relatorio = validator.validar(nova, np, catalogo, opcoes_validacao)
            if novo_relatorio["problemas"]:
                continue
            if orcamento is not None and (novo_relatorio["total_pp"] or 0) > orcamento:
                continue
            # Conta qualquer coisa que chegue ao teto com este passo (subir Agilidade, por exemplo,
            # também sobe Furtividade e Acrobacia).
            if (_no_teto(novo_relatorio) > _no_teto(relatorio)
                    and rng.random() >= CHANCE_DE_ATINGIR_O_TETO):
                adiados.append((nova, novo_relatorio))
                continue
            escolhido = (nova, novo_relatorio)
            break
        if escolhido is None and adiados:
            escolhido = adiados[0]   # só sobrou o que vai ao teto
        if escolhido is None:
            break   # nenhum passo coube
        ficha, relatorio = escolhido
    return ficha
