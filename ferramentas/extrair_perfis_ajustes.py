import re

SINONIMOS = {
    "Invocação": "Invocar", "Membros Extra": "Membros Extras", "Sentido": "Sentidos", "Drenar": "Enfraquecer",
    "Força Aprimorada": "Força Aumentada", "Caraterística Aumentada": "Característica Aumentada",
    "Característica Aumentada": "Característica Aumentada", "Detectar": "Sentidos", "Detecção": "Sentidos",
    "Concentração": "Camuflagem", "Aumento de Vontade": "Vontade Aumentada", "Aprimorada": "Característica Aumentada",
    "Aprimorado": "Característica Aumentada", "Vôo": "Voo", "Intangível": "Intangibilidade",
    "Mover Objeto": "Mover Objetos", "Transformação": "Transformar", "Sentidos Remotos": "Sentido Remoto",
    "Características": "Característica",
}
MODIFICADOR_DE_OUTRO = re.compile(r"(aplicad[oa] (?:a|ao|à)|^adicion(?:ar|e)\b|^modificador\b|no poder anterior|ao efeito de)", re.I)


def ler_custo(t):
    t = t.strip().rstrip(".").replace("–", "-")
    custo = {"texto": t, "fixo": None, "por_graduacao": None, "opcoes": None}
    m = re.match(r"^(-?\d+) pontos? \+ ?(-?\d+)(?: pontos?)? por gradua", t)
    if m:
        custo.update(fixo=int(m.group(1)), por_graduacao=int(m.group(2)))
        return custo
    m = re.match(r"^(\d+) pontos? (?:por|para) (\d+) gradua", t)
    if m:
        custo.update(por_graduacao=round(int(m.group(1)) / int(m.group(2)), 3))
        return custo
    m = re.match(r"^(-?\d+) pontos? (?:por )?gradua", t)
    if m:
        custo.update(por_graduacao=int(m.group(1)))
        return custo
    m = re.match(r"^(-?\d+) pontos?$", t)
    if m:
        custo.update(fixo=int(m.group(1)))
        return custo
    m = re.match(r"^([\d, ]+(?: ou \d+)) pontos?( por gradua)?", t)
    if m:
        valores = [int(x) for x in re.findall(r"\d+", m.group(1))]
        custo["opcoes"] = valores
        custo["opcoes_por_graduacao"] = bool(m.group(2))
    return custo


def efeito_base(texto, efeitos):
    for nome in efeitos + sorted(SINONIMOS, key=len, reverse=True):
        if re.search(rf"(^|\s){re.escape(nome)}(\s|$|,|\(|\d)", texto, re.I):
            return SINONIMOS.get(nome, nome)
    return None
