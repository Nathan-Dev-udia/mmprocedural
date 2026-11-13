"""Escudo do Mestre: tabelas de consulta rápida por gênero (dados/escudo/<gênero>.json).

O JSON traz as abas e os blocos escritos à mão (tabelas, listas e fórmulas). Os blocos {"tipo": "gerado"} são
calculados aqui, a partir da Tabela de Medidas e do catálogo de equipamento do gênero, para os números do escudo
nunca ficarem diferentes dos do gerador: queda, tempo de viagem, montarias, carga e a própria tabela de medidas.
A página do site e o PDF (nucleo/escudo_pdf.py) leem o mesmo resultado de `montar`.
"""

import json
import re
from pathlib import Path

from . import formatter, medidas

PASTA = Path(__file__).parent.parent / "dados" / "escudo"
TIPOS_DE_BLOCO = {"tabela", "lista", "formulas", "gerado"}

# Distâncias da tabela de tempo de viagem, em km.
DISTANCIAS_DE_VIAGEM = [4, 8, 15, 30, 60, 120, 250]
# Meios de transporte da tabela de tempo: (rótulo, id do item no catálogo com a Velocidade; None = a pé; um número é
# a própria graduação, para gêneros cujo catálogo não tem o veículo, como o metrô e os carros do cyberpunk).
MEIOS_DE_VIAGEM = [("A pé", None), ("Carroça", "carroca"), ("Pônei ou mula", "ponei"),
                   ("Cavalo a galope", "cavalo_montaria")]
MEIOS_DE_VIAGEM_POR_GENERO = {
    "fantasia": MEIOS_DE_VIAGEM,
    "faroeste": [("A pé", None), ("Carroção Conestoga", "carrocao_conestoga"),
                 ("Buckboard", "buckboard"), ("Cavalo a galope", "cavalo")],
    "cthulhu": [("A pé", None), ("Ford Modelo T", "ford_modelo_t"),
                ("Packard de Luxo", "packard_luxo"), ("Motocicleta", "motocicleta")],
    # Livro do Mestre do cyberpunk, seções 10.9 e 16.1.
    "cyberpunk": [("A pé", None), ("Metrô ou ônibus", 3), ("Carro compacto ou moto", 5),
                  ("Carro esportivo ou AV-4", 6), ("Superbike ou supercarro", 7)],
    "escola_de_magia": [("A pé", None), ("Vassoura escolar", "vassoura_escolar"),
                        ("Vassoura de passeio", "vassoura_passeio"), ("Vassoura de corrida", "vassoura_corrida")],
}
KM_POR_DIA_EM_RITMO_NORMAL = 38
KM_POR_HORA_EM_RITMO_NORMAL = 5
ALTURAS_DE_QUEDA = [2, 4, 8, 15, 30, 60, 120, 250, 500]
FORCAS_DA_CARGA = range(-1, 6)
CATEGORIAS_DE_MONTARIA = {"Montaria", "Veículos", "Transporte", "Vassouras"}
# Notas que mudam com o gênero (sem cavalos nem sela nos anos 1920).
NOTA_DO_TEMPO_DE_VIAGEM = {
    "cthulhu": "Tempo = distância – velocidade. A velocidade máxima não se sustenta: para viagens longas de "
               "automóvel, conte paradas para gasolina, pneus furados e estradas de terra; a pé, use o ritmo normal.",
    "cyberpunk": "Tempo = distância – velocidade. No trânsito de Night City, some +2 graduações de tempo; nas "
                 "estradas da Zona de Combate, o mestre decide se dá para andar na velocidade máxima.",
    "escola_de_magia": "Tempo = distância – velocidade. Em vassouras, o vento, a chuva e a altitude podem impor "
                       "testes de Veículos (Voo); Aresto Momentum anula dano de queda.",
}
NOTA_DAS_MONTARIAS = {
    "cthulhu": "O porta-malas e o banco de trás levam a bagagem, que não conta na carga de quem dirige.",
    "escola_de_magia": "A vassoura carrega o bruxo e sua mochila escolar; carga pesada reduz a manobrabilidade em voo.",
}
TITULO_DAS_MONTARIAS = {"cthulhu": "Veículos", "escola_de_magia": "Vassouras"}
LOCAL_DA_QUEDA = {"cthulhu": "de um prédio urbano", "faroeste": "do saloon",
                  "cyberpunk": "do bloco de contêineres", "escola_de_magia": "da torre de astronomia"}


def generos_com_escudo():
    return sorted(p.stem for p in PASTA.glob("*.json"))


def _ler(genero_id):
    caminho = PASTA / f"{genero_id}.json"
    if not caminho.is_file():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def conferir(escudo):
    """Lista de problemas na estrutura do escudo (vazia se estiver tudo certo)."""
    erros = []
    ids = set()
    for aba in escudo.get("abas", []):
        if not aba.get("id") or not aba.get("nome"):
            erros.append("Aba sem id ou nome.")
        if aba.get("id") in ids:
            erros.append(f"Aba repetida: {aba['id']}.")
        ids.add(aba.get("id"))
        for bloco in aba.get("blocos", []):
            tipo = bloco.get("tipo")
            if tipo not in TIPOS_DE_BLOCO:
                erros.append(f"Aba {aba.get('id')}: tipo de bloco desconhecido '{tipo}'.")
            elif tipo == "gerado" and bloco.get("fonte") not in GERADORES and bloco.get("fonte") not in LETAIS:
                erros.append(f"Aba {aba.get('id')}: bloco gerado sem fonte conhecida ('{bloco.get('fonte')}').")
            elif tipo == "tabela":
                largura = len(bloco.get("colunas", []))
                for linha in bloco.get("linhas", []):
                    if len(linha) != largura:
                        erros.append(f"Aba {aba.get('id')}, tabela '{bloco.get('titulo')}': linha com "
                                     f"{len(linha)} colunas em vez de {largura}: {linha[:1]}.")
            elif tipo in ("lista", "formulas") and not bloco.get("itens"):
                erros.append(f"Aba {aba.get('id')}: lista '{bloco.get('titulo')}' vazia.")
    return erros


# ---------------------------------------------------------------- blocos gerados

def _numero(valor):
    return f"{valor:g}".replace(".", ",")


def _no_ritmo_normal(km):
    """"1 hora", "6 horas", "1,5 dia": quanto um grupo leva no ritmo normal (5 km/h, 38 km por dia)."""
    if km < KM_POR_DIA_EM_RITMO_NORMAL:
        horas = max(1, round(km / KM_POR_HORA_EM_RITMO_NORMAL))
        return f"{horas} hora" + ("s" if horas > 1 else "")
    dias = round(km / KM_POR_DIA_EM_RITMO_NORMAL * 2) / 2
    return f"{_numero(dias)} dia" + ("s" if dias >= 2 else "")


def _tempo_de_viagem(catalogo, dados=None, genero_id="fantasia"):
    genero = genero_id or (dados or {}).get("genero", {}).get("id", "fantasia")
    meios = MEIOS_DE_VIAGEM_POR_GENERO.get(genero, MEIOS_DE_VIAGEM)
    velocidades = [(rotulo, 0 if item_id is None else item_id if isinstance(item_id, int)
                    else catalogo[item_id]["velocidade"]) for rotulo, item_id in meios]
    colunas = (["Distância"] + [f"{rotulo} (Vel. {vel})" for rotulo, vel in velocidades]
               + [f"Ritmo normal ({KM_POR_DIA_EM_RITMO_NORMAL} km/dia)"])
    linhas = []
    for km in DISTANCIAS_DE_VIAGEM:
        graduacao = medidas.graduacao_de_distancia(km * 1000)
        linhas.append([f"{km} km (dist. {graduacao})"]
                      + [medidas.tempo(graduacao - vel) for _, vel in velocidades]
                      + [_no_ritmo_normal(km)])
    return {"tipo": "tabela", "titulo": "Tempo de viagem (velocidade máxima contínua)", "colunas": colunas,
            "linhas": linhas,
            "nota": NOTA_DO_TEMPO_DE_VIAGEM.get(
                genero, "Tempo = distância – velocidade. A velocidade máxima não se sustenta: para vários dias, use o "
                        "ritmo normal; para o galope, veja Forçar a montaria.")}


def _montarias(catalogo, dados=None, genero_id="fantasia"):
    moeda = (dados or {}).get("configuracoes", {}).get("moeda", "po")
    itens = sorted((i for i in catalogo.values()
                    if i.get("categoria") in CATEGORIAS_DE_MONTARIA and i.get("velocidade") is not None),
                   key=lambda i: (-i["velocidade"], i.get("preco") or 0))
    linhas = [[i["nome"], str(i["velocidade"]).replace("-", "–"), f"{_numero(medidas.km_por_hora(i['velocidade']))} km/h",
               f"{i['carga']} kg" if i.get("carga") else "—", formatter.dolares(i["preco"], moeda) if i.get("preco") else "—"]
              for i in itens]
    titulo = TITULO_DAS_MONTARIAS.get(genero_id, "Montarias e veículos")
    return {"tipo": "tabela", "titulo": titulo, "linhas": linhas,
            "colunas": ["Montaria ou veículo" if titulo != "Veículos" else "Veículo", "Velocidade", "Máxima",
                        "Carga", "Preço"],
            "nota": NOTA_DAS_MONTARIAS.get(genero_id, "Sela e alforjes vão no animal e não contam na carga de quem "
                                                      "monta.")}


def _carga(_catalogo, _dados=None, _genero_id="fantasia"):
    linhas = []
    for forca in FORCAS_DA_CARGA:
        linhas.append([f"{forca:+d}".replace("+0", "0").replace("-", "–"), medidas.massa(forca - 1),
                       medidas.massa(forca)])
    return {"tipo": "tabela", "titulo": "Carga [Casa]", "colunas": ["Força", "Carga leve até", "Carga máxima"],
            "linhas": linhas,
            "nota": "Leve (até a massa da Força – 1): sem penalidade. Pesada (até a massa da Força): –1 de Velocidade. "
                    "Acima: sobrecarregado (impedido)."}


def _queda(_catalogo, _dados=None, genero_id="fantasia"):
    linhas = []
    for metros in ALTURAS_DE_QUEDA:
        graduacao = medidas.graduacao_de_distancia(metros)
        dano = medidas.dano_de_queda(metros)
        linhas.append([f"até {_numero(metros)} m", str(graduacao).replace("-", "–"),
                       f"Dano {dano}" if dano else "sem dano", f"CD {15 + dano}" if dano else "—"])
    linhas.append([f"mais de {ALTURAS_DE_QUEDA[-1]} m", "—", "Dano 16 (máximo)", "CD 31"])
    local = LOCAL_DA_QUEDA.get(genero_id, "da taverna")
    return {"tipo": "tabela", "titulo": "Queda", "colunas": ["Altura", "Distância", "Dano", "Resistência"],
            "linhas": linhas,
            "nota": f"Dano 4 + o dobro da graduação de distância, no máximo 16. Do segundo andar {local} (4 m): "
                    "Dano 2. Cair do veículo em baixa velocidade não machuca; em alta velocidade, Dano 2 ou mais [Casa]."}


def _medidas(_catalogo, _dados=None, _genero_id="fantasia"):
    linhas = [[str(g).replace("-", "–"), m["massa"], m["tempo"], m["distancia"]]
              for g, m in medidas.tabela().items() if g <= 20]
    return {"tipo": "tabela", "titulo": "Tabela de medidas", "colunas": ["Grad.", "Massa", "Tempo", "Distância"],
            "linhas": linhas, "nota": "Cada graduação dobra a anterior. Um valor pertence à menor graduação que o alcança.",
            "larga": True}


GERADORES = {"tempo_de_viagem": _tempo_de_viagem, "montarias": _montarias, "carga": _carga, "queda": _queda,
             "medidas": _medidas}


# ---------------------------------------------------------------- letalidade

# Quão fácil é morrer: as tabelas de dano, Aflição e recuperação mudam; a ficha não.
LETALIDADES = {"heroica": "Heroica", "equilibrada": "Equilibrada", "mortal": "Mortal"}
DESCRICAO_DA_LETALIDADE = {
    "heroica": "Livro básico puro: ninguém morre de um golpe só.",
    "equilibrada": "Tiros e lâminas deixam marca, mas só morre quem já está caído e é atingido de novo [Casa].",
    "mortal": "Dano letal do Guia do Mestre: o 4º grau já deixa moribundo.",
}
CURA_PADRAO = {
    "heroica": "**Recuperação (livro básico):** 1 condição de dano por minuto de descanso, da pior para a melhor; "
               "a fadiga some com 1 hora.",
    "equilibrada": "**Recuperação [Casa]:** 1 condição de dano por hora de descanso, da pior para a melhor (cada –1 "
                  "de ferido é uma condição). Tratamento de longo prazo reduz uma graduação de tempo.",
    "mortal": "**Recuperação lenta [Casa]:** 1 condição de dano por dia de descanso, da pior para a melhor. "
              "Tratamento de longo prazo reduz uma graduação de tempo.",
}
NOTA_DA_AFLICAO = ("O efeito define uma condição para cada grau; graus mais altos substituem os mais baixos. No fim de "
                   "cada turno, o alvo faz um salvamento para tirar as condições de 1º e 2º grau; as de 3º grau exigem "
                   "um minuto ou ajuda (Tratamento CD 10 + graduação).")


def letalidade_padrao(escudo):
    return (escudo.get("letalidade") or {}).get("padrao", "equilibrada")


def _dano(config, modo):
    if modo == "heroica":
        return {"tipo": "tabela", "titulo": "Dano", "colunas": ["Grau de falha", "Efeito (todos os ataques)"],
                "linhas": [
                    ["Sucesso", "Sem efeito."],
                    ["1º grau (1 a 5)", "–1 nos próximos salvamentos de Resistência (cumulativo)."],
                    ["2º grau (6 a 10)", "–1 e tonto até o fim do próximo turno."],
                    ["3º grau (11 a 15)", "–1 e abatido (tonto e impedido). Se já estava abatido, aplique o 4º grau."],
                    ["4º grau (16 ou mais)", "Incapacitado."],
                ],
                "nota": "**Letalidade heroica (livro básico).** Salvamento: d20 + Resistência contra 15 + Dano. "
                        "Incapacitado que falha de novo fica moribundo; moribundo que falha morre. Para matar de "
                        "propósito, use a manobra Ataque Final."}
    mortal = modo == "mortal"
    lesao = config.get("lesao_critica")
    terceiro = ("Ferido, abatido e desabilitado (–5 em todos os testes)." if mortal
                else "Ferido e abatido (tonto e impedido).")
    quarto = "Incapacitado e moribundo." if mortal else "Incapacitado."
    if lesao and mortal:
        terceiro += " Rola uma lesão crítica."
    if lesao:
        quarto += " Rola uma lesão crítica."
    if mortal:
        nota = ("**Letalidade mortal (Guia do Mestre).** Salvamento: d20 + Resistência contra 15 + Dano. O 4º grau "
                "letal deixa moribundo na hora; moribundo que falha morre. Opcional: cinco ou mais graus de falha "
                "contra dano letal matam na hora.")
    else:
        nota = ("**Letalidade equilibrada [Casa].** Salvamento: d20 + Resistência contra 15 + Dano. O –1 de ferido não "
                "some sozinho: só com descanso. Incapacitado que falha de novo fica moribundo; moribundo que falha "
                "morre.")
    return {"tipo": "tabela", "titulo": "Dano",
            "colunas": ["Grau de falha", f"Padrão ({config.get('ataques_padrao', 'socos e golpes sem arma')})",
                        f"Letal ({config.get('ataques_letais', 'armas')})"],
            "linhas": [
                ["Sucesso", "Sem efeito.", "Sem efeito."],
                ["1º grau (1 a 5)", "–1 nos próximos salvamentos de Resistência (cumulativo).",
                 "Ferido: –1 na Resistência (cumulativo)."],
                ["2º grau (6 a 10)", "–1 e tonto até o fim do próximo turno.",
                 "Ferido e tonto até o fim do próximo turno."],
                ["3º grau (11 a 15)", "–1 e abatido (tonto e impedido). Se já estava abatido, aplique o 4º grau.",
                 terceiro],
                ["4º grau (16 ou mais)", "Incapacitado.", quarto],
            ],
            "nota": nota}


def _aflicao(config, modo):
    linhas = [
        ["1º grau (falha por 1 a 5)", "Tonto, em transe, fatigado, impedido, prejudicado ou vulnerável"],
        ["2º grau (falha por 6 a 10)", "Atordoado, caído, compelido, desabilitado, exausto, imóvel ou vulnerável"],
        ["3º grau (falha por 11 a 15)", "Adormecido, controlado, desatento, incapacitado, paralisado ou transformado"],
    ]
    if modo == "mortal" and config.get("aflicao_quarto_grau"):
        linhas.append(["4º grau [Casa] (16 ou mais)", config["aflicao_quarto_grau"]])
    colunas = ["Grau de falha", "Condições possíveis"]
    exemplos = config.get("aflicao_exemplos")
    if exemplos:
        colunas.append("Exemplos")
        linhas = [linha + [exemplos.get(str(i + 1), "—")] for i, linha in enumerate(linhas)]
    nota = f"{NOTA_DA_AFLICAO} {config.get('aflicao_nota', '')}".strip()
    return {"tipo": "tabela", "titulo": "Aflição: condição por grau de falha", "colunas": colunas, "linhas": linhas,
            "nota": nota}


def _recuperacao(config, modo):
    if modo == "mortal":
        como = ("**Moribundo:** o 4º grau de dano letal deixa moribundo na hora. Fortitude CD 15 na hora e a cada "
                "rodada: dois graus de sucesso estabilizam, três graus de falha somados matam.")
    else:
        como = ("**Moribundo:** quem já está incapacitado e falha de novo num salvamento contra dano fica moribundo. "
                "Fortitude CD 15 na hora e a cada rodada: dois graus de sucesso estabilizam, três graus de falha "
                "somados matam.")
    cura = (config.get("cura") or {}).get(modo, CURA_PADRAO[modo])
    itens = [como, "**Estabilizar:** Tratamento CD 15 (ação padrão). A vantagem Duro de Matar estabiliza sozinha.",
             cura, "**Ponto heroico:** remove tonto, atordoado ou fatigado na hora, sem gastar ação."]
    return {"tipo": "lista", "titulo": "Moribundo e recuperação", "itens": itens + config.get("recuperacao_extras", [])}


LETAIS = {"dano": _dano, "aflicao": _aflicao, "recuperacao": _recuperacao}


def montar(genero_id, dados=None, letalidade=None):
    """O escudo do gênero com os blocos gerados já calculados; None se o gênero não tiver escudo.

    `dados` é o gênero carregado (data_loader.carregar_genero), de onde sai o catálogo de equipamento.
    `letalidade`: "heroica", "equilibrada" ou "mortal" (sem pedido, a padrão do gênero). "todas" monta os três
    modos de cada bloco de letalidade, marcados com "letalidade", para a página trocar sem recarregar.
    """
    escudo = _ler(genero_id)
    if escudo is None:
        return None
    catalogo = (dados or {}).get("equipamentos", {})
    config = escudo.get("letalidade") or {}
    padrao = letalidade_padrao(escudo)
    todas = letalidade == "todas"
    modo = letalidade if letalidade in LETALIDADES else padrao
    for aba in escudo["abas"]:
        blocos = []
        for b in aba["blocos"]:
            if b["tipo"] == "gerado" and b["fonte"] in LETAIS:
                for m in (LETALIDADES if todas else [modo]):
                    bloco = LETAIS[b["fonte"]](config, m)
                    blocos.append(dict(bloco, letalidade=m) if todas else bloco)
            elif b["tipo"] == "gerado":
                blocos.append(GERADORES[b["fonte"]](catalogo, dados, genero_id))
            else:
                blocos.append(b)
        aba["blocos"] = blocos
    escudo["letalidade_atual"] = modo
    escudo["letalidades"] = [{"id": m, "nome": nome, "descricao": DESCRICAO_DA_LETALIDADE[m]}
                             for m, nome in LETALIDADES.items()]
    if not todas:
        escudo["titulo"] = f"{escudo['titulo']} · Letalidade {LETALIDADES[modo].lower()}"
    return escudo


# ---------------------------------------------------------------- texto

_NEGRITO = re.compile(r"\*\*(.+?)\*\*")


def partes_do_texto(texto):
    """[(trecho, negrito?)] de um texto com **negrito**, para a página e o PDF montarem cada um do seu jeito."""
    partes, inicio = [], 0
    for m in _NEGRITO.finditer(texto):
        if m.start() > inicio:
            partes.append((texto[inicio:m.start()], False))
        partes.append((m.group(1), True))
        inicio = m.end()
    if inicio < len(texto):
        partes.append((texto[inicio:], False))
    return partes
