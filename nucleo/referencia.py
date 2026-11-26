"""Referência do personagem: explica o que ele tem, para a mesa não precisar abrir o livro.

Monta, a partir de uma ficha pronta, as seções que vão numa página à parte no PDF, no DOCX e no TXT:

- Vantagens: o que cada uma faz (dados/comum/vantagens.json);
- Poderes (magias, sinais, implantes, traços raciais): o que faz, o teste que o alvo faz, o custo e quanto
  custa subir uma graduação, e como funciona o arranjo;
- Equipamento: estatística, descrição e qualidades de cada item;
- Termos de regra: os efeitos, modificadores e condições que aparecem nas linhas acima.

O resultado é neutro de formato: {"titulo", "subtitulo", "secoes": [{"titulo", "nota", "itens": [...]}]},
cada item com "nome", "etiqueta" (linha curta ao lado do nome) e "linhas" (parágrafos). Os exportadores só
desenham. Nada aqui muda a ficha.
"""

import re

from . import poderes as poderes_mod
from . import rules

# Efeitos-base do catálogo de poderes: o que fazem, em poucas linhas (livro básico, cap. 6).
EFEITOS = {
    "Dano": "Ataque. O alvo faz um teste de Resistência (CD 15 + graduação). Se falhar, fica ferido (–1 "
            "cumulativo nas próximas Resistências); falhas maiores deixam tonto, abatido e, por fim, incapacitado "
            "(tabela de Dano do Escudo do Mestre).",
    "Aflição": "Ataque. O alvo resiste com a defesa indicada (CD 10 + graduação). Com 1 grau de falha sofre a "
               "1ª condição da lista, com 2 graus a 2ª e com 3 graus a 3ª. No fim de cada turno ele repete o teste "
               "para se livrar das condições de 1º e 2º grau; a de 3º grau só passa com um minuto de recuperação "
               "ou ajuda (Tratamento).",
    "Enfraquecer": "Ataque. O alvo resiste (CD 10 + graduação) e perde 1 ponto do traço afetado por grau de "
                   "falha. Os pontos voltam à razão de 1 por rodada.",
    "Pasmar": "Ataque. O alvo resiste com Fortitude (CD 10 + graduação) ou fica tonto e, com falhas maiores, "
              "atordoado.",
    "Armadilha": "Ataque. Prende o alvo: quem falha na Esquiva (CD 10 + graduação) fica impedido e vulnerável, "
                 "e com mais falhas, indefeso e imóvel. Escapar exige Força ou Acrobacia contra a mesma CD.",
    "Nulificar": "Desliga outro poder ou magia: teste oposto da sua graduação contra a graduação do efeito (ou a "
                 "Vontade de quem o usa).",
    "Proteção": "+1 na Resistência por graduação. Não soma com a Proteção de armadura: vale a maior.",
    "Defesa Aumentada": "Soma a graduação à defesa indicada (já incluída nos valores da ficha).",
    "Esquiva Aumentada": "Soma a graduação à Esquiva (já incluída nos valores da ficha).",
    "Vontade Aumentada": "Soma a graduação à Vontade (já incluída nos valores da ficha).",
    "Aumento de Força": "Soma a graduação à Força (já incluída nos valores da ficha).",
    "Aumento de Vantagem": "Concede as vantagens listadas, uma por graduação.",
    "Característica": "Um bônus ou benefício especial, descrito na própria linha do poder.",
    "Sentidos": "Sentidos especiais (ver no escuro, faro, sentir magia...). Cada graduação compra um benefício; "
                "os comprados estão na linha do poder.",
    "Cura": "Ação padrão, por toque. Role d20 + graduação contra CD 10: cada grau de sucesso remove uma condição "
            "de dano (a pior primeiro) ou um –1 de ferimento. Usar de novo no mesmo alvo fica mais difícil.",
    "Regeneração": "Recupera ferimentos sozinho, sem descanso: quanto maior a graduação, mais rápido.",
    "Imunidade": "Ignora o que está listado (venenos, doenças, medo...). \"Limitada a meio efeito\": só reduz pela "
                 "metade.",
    "Ilusão": "Cria imagens falsas para os sentidos indicados. Quem desconfia faz um teste de Vontade (CD 10 + "
              "graduação) para perceber a farsa.",
    "Camuflagem": "Fica difícil de perceber pelo sentido indicado; ataques contra você sofrem a penalidade de "
                  "camuflagem.",
    "Mover Objetos": "Move objetos à distância, como se tivesse Força igual à graduação. Não causa dano por si só.",
    "Criar": "Cria objetos sólidos com volume e Resistência iguais à graduação; duram enquanto mantidos.",
    "Invocar": "Convoca um aliado (capanga) de até 15 PP por graduação. Ele age no seu turno e obedece a você.",
    "Teleporte": "Ação de movimento: some e reaparece num lugar que consiga perceber, até a distância da "
                 "graduação.",
    "Movimento": "Modos especiais de se mover (andar em paredes, sem deixar rastro, em terreno difícil...).",
    "Voo": "Voa; a graduação do poder é a graduação de velocidade.",
    "Salto": "Saltos bem maiores que o normal; a graduação diz a distância.",
    "Compreender": "Entende idiomas, animais, espíritos ou máquinas, conforme o descritor.",
    "Comunicação": "Fala à distância com quem escolher (telepatia, sussurros mágicos, rádio).",
    "Sentido Remoto": "Percebe um lugar distante como se estivesse lá (vidência, escuta).",
    "Leitura Mental": "Teste oposto contra a Vontade do alvo; cada grau de sucesso revela pensamentos mais fundos.",
    "Morfar": "Muda de aparência; +20 em Enganação para se disfarçar.",
    "Crescimento": "Fica maior: mais Força e Vigor, porém mais fácil de acertar e de ver.",
    "Intangibilidade": "Fica incorpóreo em parte ou por inteiro: atravessa objetos e, nas graduações altas, ignora "
                       "ataques físicos.",
    "Deflexão": "Desvia ataques à distância dirigidos a você ou a aliados próximos, como um Aparar à distância.",
}

# Modificadores e termos que aparecem na estatística dos poderes. Chave: trecho procurado (minúsculo).
MODIFICADORES = [
    ("área", "Área", "Não há teste de ataque: todos na área resistem ao efeito. Quem passar num teste de Esquiva "
                     "(CD 10 + graduação) sofre só metade da graduação."),
    ("cone", "Cone", "Área em forma de leque que sai de você."),
    ("explosão", "Explosão", "Área circular em volta de um ponto escolhido."),
    ("linha", "Linha", "Área em linha reta a partir de você."),
    ("nuvem", "Nuvem", "Área que continua afetando quem entra nela por mais uma rodada."),
    ("distância de percepção", "Percepção", "Acerta sozinho qualquer alvo que você consiga perceber: não há teste de ataque, só o "
                               "de resistência do alvo."),
    ("sustentado", "Sustentado", "Dura enquanto você gastar uma ação livre por turno para mantê-lo; acaba se ficar "
                                 "atordoado ou inconsciente."),
    ("concentração", "Concentração", "Precisa de uma ação padrão por turno para continuar."),
    ("contínuo", "Contínuo", "Dura até você desligar, sem gastar ação."),
    ("grau limitado", "Grau limitado", "A Aflição para no 2º grau de falha: a 3ª condição não acontece."),
    ("depende de visão", "Depende de visão", "O alvo precisa ver você ou o efeito; de olhos fechados ou no escuro, "
                                             "não funciona."),
    ("multiataque", "Multiataque", "Um só ataque pode acertar vários alvos, ou o mesmo alvo várias vezes "
                                   "(a CD sobe com os graus de sucesso)."),
    ("cumulativo", "Cumulativo", "As falhas se somam de um ataque para o outro."),
    ("penetrante", "Penetrante", "Atravessa parte da Proteção impenetrável do alvo."),
    ("seletivo", "Seletivo", "Você escolhe quem, na área, é afetado."),
    ("limitad", "Limitado", "Só funciona na situação indicada (por isso custa menos)."),
]

# Condições (livro básico, cap. 8). Chave: trecho procurado (minúsculo).
CONDICOES = [
    ("prejudicado", "Prejudicado", "–2 em todos os testes (ou nos indicados)."),
    ("desabilitado", "Desabilitado", "–5 em todos os testes (ou nos indicados)."),
    ("tonto", "Tonto", "Só ações livres e uma ação padrão por turno."),
    ("atordoado", "Atordoado", "Não faz nenhuma ação, nem livre."),
    ("impedido", "Impedido", "Move-se à metade da velocidade."),
    ("imóvel", "Imóvel", "Não sai do lugar."),
    ("vulnerável", "Vulnerável", "Esquiva e Aparar pela metade."),
    ("indefeso", "Indefeso", "Esquiva e Aparar 0; um ataque que acerte vira crítico."),
    ("desatento", "Desatento", "Não percebe o ambiente nem age com base nele."),
    ("fatigado", "Fatigado", "Impedido; passa com 1 hora de descanso."),
    ("exausto", "Exausto", "Prejudicado e impedido; passa com 1 hora de descanso em lugar confortável."),
    ("transe", "Em transe", "Fica parado, só observando; qualquer ameaça óbvia encerra o transe."),
    ("compelido", "Compelido", "Quem o controla escolhe uma ação padrão dele por turno."),
    ("controlado", "Controlado", "Quem o controla escolhe todas as ações dele."),
    ("abatido", "Abatido", "Tonto e impedido."),
    ("caído", "Caído", "Impedido; –5 nos ataques corpo a corpo; atacantes têm +5 corpo a corpo e –5 à distância. "
                       "Levantar é ação de movimento."),
    ("cego", "Cego", "Impedido, vulnerável e sem ver nada: tudo tem camuflagem total contra ele."),
    ("paralisado", "Paralisado", "Indefeso, imóvel e fisicamente atordoado; ainda percebe o que acontece."),
    ("incapacitado", "Incapacitado", "Indefeso, atordoado e desatento; normalmente caído."),
]

# Qualidades escritas nas notas das armas (as do Gadget Guide ficam em rules.QUALIDADES_DE_ARMA).
QUALIDADES_DAS_NOTAS = {
    "Versátil": "Com as duas mãos, o mestre pode dar +1 de Dano como façanha.",
}

NOMES_DAS_DEFESAS_ATIVAS = "Esquiva e Aparar"


def _sem_detalhe(nome):
    """'Ambiente Favorito (deserto)' -> 'Ambiente Favorito'."""
    return nome.split(" (")[0].strip()


def _sinal(valor):
    return f"{valor:+d}"


# ---------------------------------------------------------------- vantagens

def _secao_vantagens(npc, dados):
    detalhes = {v["nome"]: v for v in dados.get("vantagens_detalhes", [])}
    itens = []
    for nome, graduacao in sorted(npc["ficha"].get("vantagens", {}).items()):
        if nome == rules.VANTAGEM_EQUIPAMENTO:
            continue
        info = detalhes.get(nome) or detalhes.get(_sem_detalhe(nome)) or {}
        rotulo = nome if graduacao == 1 else f"{nome} {graduacao}"
        etiqueta = " · ".join(p for p in (info.get("tipo"), f"{graduacao} PP") if p)
        itens.append({"nome": rotulo, "etiqueta": etiqueta,
                      "linhas": [info.get("efeito") or "Veja o livro básico, cap. 5."]})
    if not itens:
        return None
    return {"titulo": "Vantagens", "nota": "Cada graduação de vantagem custa 1 PP.", "itens": itens}


# ---------------------------------------------------------------- poderes

def _ataques_por_nome(relatorio):
    if not relatorio:
        return {}
    return {a["nome"]: a for a in relatorio.get("valores", {}).get("ataques", [])}


def _linha_do_teste(ataque):
    """'Teste do alvo: ...' de um ataque já validado (CDs e bônus prontos)."""
    efeito = ataque.get("efeito_nome", "Dano")
    resistido = ataque.get("resistido_por") or "Resistência"
    cd = ataque.get("cd_resistencia")
    if ataque["tipo"] == "area":
        return (f"Em área, sem teste de ataque. Esquiva CD {ataque['cd_esquiva']} para sofrer metade; depois "
                f"{resistido} CD {cd} contra {efeito} {ataque['dano']}.")
    if ataque["tipo"] == "percepcao":
        return f"Acerta sozinho quem você percebe. O alvo resiste com {resistido} CD {cd} ({efeito} {ataque['dano']})."
    alcance, defesa = ("à distância", "Esquiva") if ataque["tipo"] == "distancia" else ("corpo a corpo", "Aparar")
    critico = f"; crítico {ataque['critico']}–20" if ataque.get("critico") and ataque["critico"] < 20 else ""
    bonus = "" if ataque.get("bonus") is None else f"ataque {_sinal(ataque['bonus'])} "
    pericia = f" (perícia {ataque['pericia']})" if ataque.get("pericia") else ""
    return (f"Ataque {alcance}: {bonus}contra {defesa} do alvo{pericia}{critico}. Se acertar, o alvo faz "
            f"{resistido} CD {cd} contra {efeito} {ataque['dano']}.")


def _limite_do_np(ataque, np):
    if ataque["tipo"] in ("area", "percepcao"):
        return f"Limite do NP {np}: graduação até {np}."
    if ataque.get("bonus") is None:
        return ""
    soma = ataque["bonus"] + ataque["dano"]
    return f"Limite do NP {np}: ataque + graduação até {2 * np} (hoje {soma})."


def _custo_de_subir(poder, dados, poder_id):
    """Quanto custa subir 1 graduação, pelo custo do catálogo (None se o poder não tem custo por graduação)."""
    item = dados.get("poderes", {}).get(poder.get("catalogo") or "")
    graduacao = poder.get("graduacao")
    if not item or not graduacao:
        return None
    entrada = dados.get("poderes_do_genero", {}).get(poder_id, {})
    por_graduacao = entrada.get("custo_por_graduacao") or item["custo"].get("por_graduacao")
    if not por_graduacao:
        return None
    if por_graduacao < 1:
        passo = round(1 / por_graduacao)
        return f"1 PP a cada {passo} graduações"
    try:
        delta = (poderes_mod.custo(item, graduacao + 1, entrada.get("custo_por_graduacao"))
                 - poderes_mod.custo(item, graduacao, entrada.get("custo_por_graduacao")))
    except poderes_mod.PoderInvalido:
        return None
    return f"+{delta} PP por graduação"


def _custo_cheio(poder, dados, poder_id):
    """Quanto o poder custaria fora do arranjo (None se não der para calcular)."""
    item = dados.get("poderes", {}).get(poder.get("catalogo") or "")
    if not item:
        return None
    entrada = dados.get("poderes_do_genero", {}).get(poder_id, {})
    try:
        return poderes_mod.custo(item, poder.get("graduacao"), entrada.get("custo_por_graduacao"))
    except poderes_mod.PoderInvalido:
        return None


def _estatistica(poder):
    """O que está entre os parênteses do nome: 'Igni 7 (Dano, Área Cone (chama arcana))' -> 'Dano, Área ...'."""
    nome = poder.get("nome", "")
    curto = poder.get("nome_curto", "")
    if curto and nome.startswith(curto + " (") and nome.endswith(")"):
        return nome[len(curto) + 2:-1]
    if " (" in nome and nome.endswith(")"):
        return nome[nome.index(" (") + 2:-1]
    return ""


def _secao_poderes(npc, dados, relatorio):
    poderes = npc["ficha"].get("poderes", {})
    if not poderes:
        return None, []
    ataques = _ataques_por_nome(relatorio)
    np = int(npc.get("np_pretendido") or 0)
    custos_dos_principais = {}
    itens = []
    for poder_id, poder, papel in poderes_mod.em_ordem_de_exibicao(poderes):
        if papel == "principal":
            custos_dos_principais[poder["arranjo"]] = poder.get("custo_informado")
    arranjos = {}
    for poder_id, poder, papel in poderes_mod.em_ordem_de_exibicao(poderes):
        rotulo = poder.get("nome_curto") or _sem_detalhe(poder["nome"])
        custo = poder.get("custo_informado")
        partes_etiqueta = []
        if papel == "alternativo":
            partes_etiqueta.append(f"1 PP (alternativo de {poder['arranjo']})")
        elif custo is not None:
            partes_etiqueta.append(f"{custo} PP" + (f" (principal de {poder['arranjo']})" if papel else ""))
        linhas = []
        if poder.get("descricao"):
            linhas.append(poder["descricao"])
        estatistica = _estatistica(poder)
        if estatistica:
            linhas.append(f"Na regra: {estatistica}.")
        if poder.get("ajustes"):
            bonus = ", ".join(f"{traco} {_sinal(valor)}" for traco, valor in poder["ajustes"].items())
            linhas.append(f"Já somado na ficha: {bonus}.")
        if poder.get("ajustes_limitados"):
            bonus = ", ".join(f"{traco} {_sinal(valor)}" for traco, valor in poder["ajustes_limitados"].items())
            linhas.append(f"Só na situação descrita: {bonus} (não está somado na ficha).")
        ataque = ataques.get(_sem_detalhe(rotulo)) or ataques.get(re.sub(r"\s+\d+$", "", rotulo))
        if ataque:
            linhas.append(_linha_do_teste(ataque))
            limite = _limite_do_np(ataque, np)
            if limite:
                linhas.append(limite)
        subir = _custo_de_subir(poder, dados, poder_id)
        if papel == "alternativo":
            teto = custos_dos_principais.get(poder["arranjo"])
            sozinho = _custo_cheio(poder, dados, poder_id)
            conta = f"sozinho custaria {sozinho} PP" + (f" ({subir})" if subir else "") + "; " if sozinho else ""
            linhas.append(f"Subir de graduação: {conta}sobe de graça enquanto não passar do custo do principal "
                          f"({teto} PP). Acima disso, suba o principal primeiro.")
        elif subir:
            extra = " (os alternativos do arranjo podem subir junto, sem custo)" if papel == "principal" else ""
            linhas.append(f"Subir de graduação: {subir}{extra}.")
        elif custo is not None and not poder.get("graduacao"):
            linhas.append("Custo fixo: não tem graduações para subir.")
        if poder.get("arranjo"):
            arranjos.setdefault(poder["arranjo"], []).append(rotulo)
        itens.append({"nome": rotulo, "etiqueta": " · ".join(partes_etiqueta), "linhas": linhas})
    nota = ""
    if arranjos:
        nota = ("Arranjo: os poderes do mesmo arranjo são usados um de cada vez; trocar de efeito é uma ação livre, "
                "uma vez por turno. O mais caro é o principal e paga o custo cheio; cada alternativo custa 1 PP e "
                "não pode custar mais que o principal. Arranjos desta ficha: "
                + "; ".join(f"{nome}: {', '.join(membros)}" for nome, membros in arranjos.items()) + ".")
    titulo = npc.get("rotulo_poderes") or "Poderes"
    textos = [poder.get("nome", "") for poder in poderes.values()]
    return {"titulo": titulo, "nota": nota, "itens": itens}, textos


# ---------------------------------------------------------------- equipamento

def _estatistica_do_item(item, ataque_validado):
    partes = []
    ataque = item.get("ataque")
    if ataque_validado:
        partes.append(_linha_do_teste(ataque_validado))
    elif ataque:
        efeito = ataque.get("efeito_nome", "Dano")
        forca = " + Força" if ataque.get("soma_forca") else ""
        partes.append(f"{efeito} {ataque['efeito']}{forca}"
                      + (f" ({ataque['descritor']})" if ataque.get("descritor") else "")
                      + (f"; crítico {ataque['critico']}–20" if ataque.get("critico", 20) < 20 else "") + ".")
    if ataque and ataque.get("soma_forca") and ataque_validado:
        partes.append(f"O dano já inclui a sua Força (a arma sozinha é Dano {ataque['efeito']}).")
    if item.get("protecao"):
        limitada = f" (só {item['limitada_a']})" if item.get("limitada_a") else ""
        partes.append(f"Proteção +{item['protecao']}{limitada} na Resistência; não soma com outra Proteção, vale "
                      f"a maior.")
    if item.get("defesas_ativas"):
        partes.append(f"+{item['defesas_ativas']} em {NOMES_DAS_DEFESAS_ATIVAS}.")
    return partes


def _secao_equipamento(npc, dados, relatorio):
    catalogo = dados.get("equipamentos", {})
    quantidades = npc["ficha"].get("quantidades", {})
    ataques = _ataques_por_nome(relatorio)
    itens, qualidades, textos = [], set(), []
    for item_id in dict.fromkeys(npc["ficha"].get("equipamento", [])):
        item = catalogo.get(item_id)
        if not item or item.get("kit"):
            continue   # os kits já vêm abertos: cada peça aparece sozinha
        linhas = _estatistica_do_item(item, ataques.get(item["nome"]) or ataques.get(_sem_detalhe(item["nome"])))
        if item.get("descricao") and not (item.get("protecao") and item["descricao"].startswith("Proteção")):
            linhas.append(item["descricao"])
        if item.get("notas"):
            linhas.append(item["notas"].rstrip(".") + ".")
        if not linhas:
            continue
        for qualidade in (item.get("ataque") or {}).get("qualidades", []):
            qualidades.add(qualidade)
        for qualidade in QUALIDADES_DAS_NOTAS:
            if qualidade.lower() in (item.get("notas") or "").lower():
                qualidades.add(qualidade)
        quantidade = quantidades.get(item_id, 1)
        nome = item["nome"] + (f" ×{quantidade}" if quantidade and quantidade > 1 else "")
        itens.append({"nome": nome, "etiqueta": item.get("categoria", ""), "linhas": linhas})
        textos.append(" ".join(linhas))
    if not itens:
        return None, set(), []
    return {"titulo": "Equipamento", "nota": "", "itens": itens}, qualidades, textos


# ---------------------------------------------------------------- termos de regra

def _secao_termos(textos_de_poder, efeitos_base, qualidades, textos_extras):
    itens = []
    for efeito in efeitos_base:
        if efeito in EFEITOS:
            itens.append({"nome": efeito, "etiqueta": "efeito", "linhas": [EFEITOS[efeito]]})
    texto_poderes = " ".join(textos_de_poder).lower()
    sem_grau_limitado = texto_poderes.replace("grau limitado", "")
    for trecho, nome, regra in MODIFICADORES:
        onde = sem_grau_limitado if trecho == "limitad" else texto_poderes
        if re.search(r"\b" + re.escape(trecho), onde):
            itens.append({"nome": nome, "etiqueta": "modificador", "linhas": [regra]})
    for qualidade in sorted(qualidades):
        regra = rules.QUALIDADES_DE_ARMA.get(qualidade) or QUALIDADES_DAS_NOTAS.get(qualidade)
        if regra:
            itens.append({"nome": qualidade, "etiqueta": "qualidade de arma", "linhas": [regra]})
    texto_todo = (texto_poderes + " " + " ".join(textos_extras)).lower()
    for trecho, nome, regra in CONDICOES:
        if re.search(rf"\b{re.escape(trecho)}", texto_todo):
            itens.append({"nome": nome, "etiqueta": "condição", "linhas": [regra]})
    if not itens:
        return None
    return {"titulo": "Termos de regra", "nota": "Os efeitos, modificadores e condições citados acima.",
            "itens": itens}


def _efeitos_base(npc, dados):
    vistos = []
    for poder in npc["ficha"].get("poderes", {}).values():
        item = dados.get("poderes", {}).get(poder.get("catalogo") or "")
        for efeito in (item or {}).get("efeitos", []):
            base = efeito.get("efeito_base")
            if base and base not in vistos:
                vistos.append(base)
    return vistos


# ---------------------------------------------------------------- montagem

def montar(npc, dados, relatorio=None):
    """As seções da referência do personagem (veja o docstring do módulo). Seções vazias ficam de fora."""
    relatorio = relatorio or npc.get("validacao")
    secoes = []
    vantagens = _secao_vantagens(npc, dados)
    if vantagens:
        secoes.append(vantagens)
    poderes, textos_de_poder = _secao_poderes(npc, dados, relatorio)
    if poderes:
        secoes.append(poderes)
    equipamento, qualidades, textos_de_itens = _secao_equipamento(npc, dados, relatorio)
    if equipamento:
        secoes.append(equipamento)
    textos_extras = textos_de_itens + [linha for item in (poderes or {}).get("itens", []) for linha in item["linhas"]]
    termos = _secao_termos(textos_de_poder, _efeitos_base(npc, dados), qualidades, textos_extras)
    if termos:
        secoes.append(termos)
    arquetipo = (npc.get("arquetipo") or {}).get("nome", "")
    raca = (npc.get("raca") or {}).get("nome", "")
    subtitulo = " · ".join(p for p in (raca, arquetipo, f"NP {npc.get('np_pretendido')}") if p)
    return {"titulo": f"Referência: {npc.get('nome', 'Personagem')}", "subtitulo": subtitulo, "secoes": secoes,
            # Campos do cabeçalho da página no PDF (como os da ficha).
            "nome": npc.get("nome", ""), "jogador": npc.get("jogador", ""), "np": npc.get("np_pretendido")}


def texto(referencia):
    """A referência em texto simples (para o TXT)."""
    if not referencia["secoes"]:
        return ""
    linhas = [referencia["titulo"].upper(), referencia["subtitulo"]]
    for secao in referencia["secoes"]:
        linhas += ["", secao["titulo"].upper()]
        if secao.get("nota"):
            linhas.append(secao["nota"])
        for item in secao["itens"]:
            cabecalho = item["nome"] + (f" [{item['etiqueta']}]" if item.get("etiqueta") else "")
            linhas.append(f"- {cabecalho}: " + " ".join(item["linhas"]))
    return "\n".join(linhas)
