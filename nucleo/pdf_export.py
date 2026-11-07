"""Preenche a ficha de personagem editável (PDF) com um NPC gerado.

O modelo fica em data/ficha_editavel.pdf. Ele tem campos de formulário com
cálculos automáticos (totais de perícias, defesas e custos). Por isso os
valores são preenchidos de forma coerente com essas fórmulas: se o leitor de
PDF recalcular, os números continuam certos.

Ajustes feitos na cópia gerada (o modelo original não é alterado):
- todos os campos de dados são limpos antes (o modelo veio preenchido);
- a fórmula do total do 2º Combate à Distância é corrigida (ela somava o
  nome da especialização em vez das graduações);
- as fórmulas do custo das perícias e da Resistência Máxima são corrigidas, e a
  ordem de cálculo passa a seguir as dependências (parcelas antes dos totais);
- na ficha gerada, custo das habilidades, Iniciativa, bônus de ataque e dano com
  Força ganham fórmulas: o jogador muda uma habilidade e eles acompanham.
"""

import io
from pathlib import Path
import re
import textwrap

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

from . import formatter
from . import poderes as poderes_mod
from . import rules

# Campos do modelo que funcionam como rótulos e não devem ser apagados.
CAMPOS_ROTULO = {
    "Esquiva Máx", "Esquiva Grad", "Aparar Máx", "Aparar Grad", "Fortitude Máx", "Fortitude Grad",
    "Resistência Máx", "Armadura", "Vontade Máx", "Vontade Grad", "Esquiva Outros1", "Aparar Outros1",
    "Fortitude Outros1", "Resistência Outros1", "Vontade Outros1", "Grad Máx Perícia",
}

CAMPO_DA_HABILIDADE = {"For": "Força", "Vig": "Vigor", "Agi": "Agilidade", "Des": "Destreza",
                       "Lut": "Luta", "Int": "Intelecto", "Pro": "Prontidão", "Pre": "Presença"}

# Perícias sem especialização: prefixo dos campos na ficha (Total, Hab, Per, Outros).
PREFIXO_DA_PERICIA = {"Acrobacia": "Acrob", "Atletismo": "Atle", "Enganação": "Eng", "Furtividade": "Furt",
                      "Intimidação": "Int", "Intuição": "Intuição", "Investigação": "Inv",
                      "Percepção": "Perc", "Persuasão": "Pers", "Prestidigitação": "Prest",
                      "Tecnologia": "Tec", "Tratamento": "Trat", "Veículos": "Veic"}

# Perícias com especialização: (campo do nome, prefixo dos campos, sufixo do campo "Outros", linhas).
LINHAS_ESPECIALIZADAS = {
    "Combate Corpo-a-Corpo": ("CCC {n}", "CCC", "Outro", 3),
    "Combate à Distância": ("CaD {n}", "CaD", "Outros", 3),
    "Especialidade": ("Especialidade {n}", "Esp", "Outros", 4),
}

# A ficha usa a habilidade padrão em cada linha; a diferença vai para "Outros".
HABILIDADE_PADRAO_DA_LINHA = {"Combate Corpo-a-Corpo": "Lut", "Combate à Distância": "Des", "Especialidade": "Int"}

LINHAS = {"ataques": 4, "vantagens": 11, "equipamento": 10, "poderes": 18, "notas": 6, "complicacoes": 11}
LARGURA_DA_LINHA = 95


def _sinal(valor):
    return f"{valor:+d}"


def valores_dos_campos(npc, relatorio, genero_nome):
    """Monta o dicionário {nome do campo: valor} para um NPC já validado."""
    ficha = npc["ficha"]
    val = relatorio["valores"]
    custos = relatorio["custos"]
    campos = {}
    notas_extras = []

    # Cabeçalho e custos
    campos["Herói"] = npc["nome"]
    campos["Jogador"] = npc.get("jogador", "")
    campos["Grupo Afiliado"] = npc["faixa"]["nome"]
    campos["Nível de Poder"] = str(npc["np_pretendido"])
    campos["Series"] = f"{genero_nome} em Mutantes & Malfeitores"
    for secao, campo in (("habilidades", "Habilidades"), ("poderes", "Poderes"), ("vantagens", "Vantagens"),
                         ("pericias", "Perícias"), ("defesas", "Defesas")):
        valor = custos.get(secao, 0)
        campos[campo] = "" if valor is None else str(valor)
    total = relatorio["total_pp"]
    campos["Total"] = "" if total is None else str(total)

    # Habilidades (valores finais, já com os traços naturais aplicados)
    for hab, campo in CAMPO_DA_HABILIDADE.items():
        campos[campo] = str(val["habilidades"][hab])
    campos["Iniciativa"] = _sinal(val["iniciativa"])

    # Defesas: base da habilidade + graduações compradas + outros = total
    compradas = ficha.get("defesas_compradas", {})
    for defesa, hab in rules.DEFESAS_COMPRAVEIS.items():
        grad = compradas.get(defesa, 0)
        outros = val["defesas"][defesa] - val["habilidades"][hab] - grad
        campos[f"Grad.{defesa}"] = str(grad)
        campos[f"{defesa} Outros"] = str(outros) if outros else ""
        campos[defesa] = str(val["defesas"][defesa])
    protecao = val["protecao"]
    campos["Mod de Armadura"] = str(protecao) if protecao else ""
    outros_res = val["defesas"]["Resistência"] - val["habilidades"]["Vig"] - protecao
    campos["Resistência Outros"] = str(outros_res) if outros_res else ""
    campos["Resistência"] = str(val["defesas"]["Resistência"])

    # Ataques
    ataques = formatter.ataques_exibidos(val["ataques"])
    for n, ataque in enumerate(ataques[:LINHAS["ataques"]], start=1):
        bonus = "" if ataque["bonus"] is None else f" {_sinal(ataque['bonus'])}"
        campos[f"Ataque {n}"] = f"{formatter.nome_curto(ataque['nome'])}{bonus}"
        campos[f"Dano {n}"] = str(ataque["dano"])
        campos[f"Descrição {n}"] = formatter.detalhes_do_ataque(ataque)
    for ataque in ataques[LINHAS["ataques"]:]:
        bonus = "" if ataque["bonus"] is None else f" {_sinal(ataque['bonus'])}"
        notas_extras.append(f"Ataque: {ataque['nome']}{bonus}, Dano {ataque['dano']}. {formatter.detalhes_do_ataque(ataque)}")

    # Perícias
    usadas = {chave: 0 for chave in LINHAS_ESPECIALIZADAS}
    for nome, pericia in sorted(val["pericias"].items()):
        hab_da_pericia = rules.habilidade_da_pericia(nome)
        base = rules.nome_base(nome)
        if base in PREFIXO_DA_PERICIA:
            prefixo = PREFIXO_DA_PERICIA[base]
            campos[f"{prefixo}Hab"] = str(val["habilidades"][hab_da_pericia])
            campos[f"{prefixo}Per"] = str(pericia["graduacoes"])
            outros = pericia["total"] - val["habilidades"][hab_da_pericia] - pericia["graduacoes"]
            campos[f"{prefixo}Outros"] = str(outros) if outros else ""
            campos[f"{prefixo}Total"] = str(pericia["total"])
            continue
        campo_nome, prefixo, sufixo_outros, maximo = LINHAS_ESPECIALIZADAS[base]
        if usadas[base] == maximo:
            notas_extras.append(f"Perícia: {nome} {pericia['graduacoes']} ({_sinal(pericia['total'])})")
            continue
        usadas[base] += 1
        n = usadas[base]
        # A coluna Hab mostra a habilidade da própria perícia (a fórmula da linha é trocada em formulas_dos_campos
        # quando não é a padrão), para o total acompanhar se o jogador mudar essa habilidade no PDF.
        campos[campo_nome.format(n=n)] = nome.split(":", 1)[1].strip()
        campos[f"{prefixo}Hab {n}"] = str(val["habilidades"][hab_da_pericia])
        campos[f"{prefixo}Per {n}"] = str(pericia["graduacoes"])
        outros = pericia["total"] - val["habilidades"][hab_da_pericia] - pericia["graduacoes"]
        campos[f"{prefixo}{sufixo_outros} {n}"] = str(outros) if outros else ""
        campos[f"{prefixo}Total {n}"] = str(pericia["total"])
    campos["Perícias Total"] = str(sum(ficha.get("pericias", {}).values()))

    # Vantagens
    vantagens = [nome if grad == 1 and nome != rules.VANTAGEM_EQUIPAMENTO else f"{nome} {grad}"
                 for nome, grad in sorted(ficha.get("vantagens", {}).items())]
    _preencher_linhas(campos, "Vantagens {n}", vantagens, LINHAS["vantagens"])

    # Equipamento
    pe = val["pontos_equipamento"]
    equipamento = list(val["itens"])
    if not npc.get("dinheiro") and pe["disponiveis"]:
        equipamento.append(f"({pe['usados']} de {pe['disponiveis']} pontos de equipamento)")
    if val.get("carga"):
        c = val["carga"]
        p_str = formatter.peso(c["peso_total"])
        l_str = formatter.peso(c["capacidade_leve"])
        m_str = formatter.peso(c["capacidade_maxima"])
        rotulos = {"leve": "Leve", "pesada": "Pesada", "sobrecarregado": "Sobrecarregado"}
        rot = rotulos.get(c["categoria"], "Leve")
        na_montaria = f"; +{formatter.peso(c['na_montaria'])} na montaria" if c.get("na_montaria") else ""
        equipamento.append(f"Carga: {p_str} ({rot} • Leve {l_str}, Máx {m_str}){na_montaria}")
    _preencher_linhas(campos, "Equipamento {n}", equipamento, LINHAS["equipamento"])

    # Complicações
    _preencher_linhas(campos, "Complicações {n}",
                      [formatter.texto_complicacao(c) for c in npc.get("complicacoes", [])], LINHAS["complicacoes"])

    # Poderes (traços naturais de animais, implantes, feitiços...), com efeitos e posição nos arranjos.
    rotulo = npc.get("rotulo_poderes", "Poderes")
    tracos = []
    for _, poder, papel in poderes_mod.em_ordem_de_exibicao(ficha.get("poderes", {})):
        texto = f"{rotulo}: {formatter.texto_do_poder(poder, papel)}"
        tracos.extend(textwrap.wrap(texto, width=62, subsequent_indent="  ", break_long_words=False,
                                    break_on_hyphens=False))
    _preencher_linhas(campos, "Poderes e Dispositivos {n}", tracos, LINHAS["poderes"])

    # Notas & Condições (página 1): regras de jogo do NPC
    condicoes = []
    if npc["capanga"]:
        condicoes.append("Capanga: não faz críticos contra quem não é capanga; qualquer falha num "
                         "salvamento aplica o pior resultado.")
    if npc.get("dinheiro"):
        dinheiro = npc["dinheiro"]
        moeda = dinheiro.get("moeda", "$")
        resumo = (f"Dinheiro: {formatter.dolares(dinheiro['inicial'], moeda)} iniciais; "
                  f"{formatter.dolares(dinheiro['gasto'], moeda)} gastos; sobram "
                  f"{formatter.dolares(dinheiro['restante'], moeda)}.")
        if dinheiro.get("divida"):
            resumo += f" Dívida: {formatter.dolares(dinheiro['divida'], moeda)}."
        condicoes.append(resumo)
    san = npc.get("sanidade") or ficha.get("sanidade")
    if san:
        condicoes.append(f"Sanidade: {san['atual']} (máx. {san['maxima']}; inicial {san['inicial']})")
    detalhe_protecao = formatter.detalhe_protecao(val)
    if detalhe_protecao:
        condicoes.append(f"Armadura: {detalhe_protecao}; já incluída na Resistência.")
    condicoes.append(f"Tática: {npc['tatica']}")
    condicoes += notas_extras
    campos["Notas & Condições"] = "\n".join(condicoes)

    # Notas (página 2): descrição, módulos, origem e status
    modulos = ", ".join(f"{m['nome']} ({m['papel']})" for m in npc["modulos"])
    notas = textwrap.wrap(npc["descricao"], LARGURA_DA_LINHA)
    notas += textwrap.wrap(f"{npc['arquetipo']['nome']}. Módulos: {modulos}. "
                           f"Ficha-base: {npc['faixa']['fonte']}.", LARGURA_DA_LINHA)
    notas += textwrap.wrap(f"Status: {relatorio['status_rotulo']}. NP estimado pelos valores: "
                           f"{relatorio['np_efetivo']}.", LARGURA_DA_LINHA)
    _preencher_linhas(campos, "Notas {n}", notas[:LINHAS["notas"]], LINHAS["notas"])
    if len(notas) > LINHAS["notas"]:
        campos["Notes 7"] = " ".join(notas[LINHAS["notas"]:])[:LARGURA_DA_LINHA]
    return campos


def _preencher_linhas(campos, modelo, itens, maximo):
    """Coloca um item por linha; o que sobrar vai junto na última linha."""
    if len(itens) > maximo:
        itens = itens[:maximo - 1] + ["; ".join(itens[maximo - 1:])]
    for n, item in enumerate(itens, start=1):
        campos[modelo.format(n=n)] = item


def _corrigir_formula_do_combate_a_distancia(writer):
    for pagina in writer.pages:
        for anotacao in pagina.get("/Annots", []):
            anotacao = anotacao.get_object()
            if anotacao.get("/T") != "CaDTotal 2" or "/AA" not in anotacao:
                continue
            acao = anotacao["/AA"]["/C"].get_object()
            js = acao["/JS"]
            texto = js.get_object().get_data().decode("latin-1") if hasattr(js.get_object(), "get_data") else str(js)
            acao[NameObject("/JS")] = TextStringObject(texto.replace('"CaD 2"', '"CaDPer 2"'))


# Fórmulas do modelo que precisam de conserto, para todas as fichas (NPC, PJ, herói, criatura):
# - o custo das perícias é 1 PP a cada 2 graduações, arredondado para cima (como o gerador conta);
# - a Resistência Máxima comparava os textos "Esquiva" e "Aparar", não os valores.
FORMULAS_CORRIGIDAS = {
    "Perícias": 'event.value = Math.ceil(AFMakeNumber(getField("Perícias Total").value) / 2);',
    "Resistência Máxima": ('var e = AFMakeNumber(getField("Esquiva").value), a = AFMakeNumber(getField("Aparar").value);'
                           ' event.value = 2 * AFMakeNumber(getField("Nível de Poder").value) - Math.max(e, a);'),
}


def _js_numero(campo):
    return f'AFMakeNumber(getField("{campo}").value)'


def _js_so_quando_mudar(campos, calculo):
    """Recalcula só quando o jogador muda um dos campos dados; com qualquer outra mudança, o campo fica como está
    (o jogador pode trocar a arma ou o texto à mão sem a fórmula apagar)."""
    lista = ", ".join(f'"{c}"' for c in campos)
    return (f"var origem = event.source ? event.source.name : \"\"; "
            f"if ([{lista}].indexOf(origem) >= 0) {{ {calculo} }} else {{ event.value = event.target.value; }}")


def _js_descricao(ataque, campo_dano):
    """A descrição do ataque com a CD (e o alcance, à distância) tirados do campo de Dano."""
    d = _js_numero(campo_dano)
    base = 15 if ataque.get("efeito_nome", "Dano") == "Dano" else 10
    critico = f"crít. {ataque['critico']}–20" if ataque["critico"] < 20 else "crít. 20"
    resistido = ataque.get("resistido_por", "Resistência")
    rotulo = "Resist." if resistido == "Resistência" else resistido
    extras = formatter._descritor_e_qualidades(ataque)
    efeito = "" if ataque.get("efeito_nome", "Dano") == "Dano" else f'"{ataque["efeito_nome"]} " + d + ", " + '
    fim = f'"{critico}, {rotulo} CD " + ({base} + d) + "{extras}"'
    if ataque["tipo"] == "distancia":
        metros = 'function m(x) { return x.toFixed(1).replace(/\\.?0+$/, "").replace(".", ","); } '
        return (f"var d = {d}; {metros}event.value = m(d * 7.5) + \"/\" + m(d * 15) + \"/\" + m(d * 30) + \" m, \" + "
                f"{efeito}{fim};")
    return f'var d = {d}; event.value = "Corpo a corpo, " + {efeito}{fim};'


# Para um campo calculado cujo valor não sai da fórmula do modelo (Fortitude "Imune" de quem não tem Vigor, o custo
# de Defesas de uma ficha publicada que não separa as graduações): o leitor deixa o valor como está.
MANTER_O_VALOR = "event.value = event.target.value;"


def formula_do_custo_das_habilidades(custo, hab):
    """{"Habilidades": js}: 2 PP por graduação, mais o que a ficha já trazia de diferente (traços de raça...)."""
    if custo is None or not all(isinstance(v, int) for v in hab.values()):
        return {}
    soma = " + ".join(_js_numero(c) for c in CAMPO_DA_HABILIDADE.values())
    return {"Habilidades": f"event.value = 2 * ({soma}) + ({custo - 2 * sum(hab.values())});"}


def formula_da_iniciativa(iniciativa, agilidade):
    """{"Iniciativa": js}: Agilidade mais o que vem das vantagens (só recalcula quando a Agilidade muda)."""
    if not isinstance(iniciativa, int) or not isinstance(agilidade, int):
        return {}
    return {"Iniciativa": _js_so_quando_mudar(
        ["Agilidade"], f'var n = {_js_numero("Agilidade")} + ({iniciativa - agilidade}); '
                       f'event.value = (n >= 0 ? "+" : "") + n;')}


def formula_da_linha_de_pericia(base, n, sigla):
    """{campo Hab da linha: js} quando a perícia especializada usa outra habilidade que não a padrão da linha
    (a ficha soma Luta, Destreza ou Intelecto; Especialidade: Cavalgar usa Agilidade)."""
    if sigla == HABILIDADE_PADRAO_DA_LINHA[base]:
        return {}
    return {f"{LINHAS_ESPECIALIZADAS[base][1]}Hab {n}": f"event.value = {_js_numero(CAMPO_DA_HABILIDADE[sigla])};"}


def formulas_dos_campos(npc, relatorio):
    """{campo: JavaScript de cálculo} dos campos que o modelo não calcula e que dependem das habilidades.

    Os números que não vêm das habilidades (graduações, vantagens, a arma) entram como uma constante na fórmula:
    se o jogador trocar Força ou Agilidade no PDF, o custo, a Iniciativa, o ataque e o dano acompanham.
    """
    val = relatorio["valores"]
    hab = val["habilidades"]
    formulas = {**formula_do_custo_das_habilidades(relatorio["custos"].get("habilidades"), hab),
                **formula_da_iniciativa(val["iniciativa"], hab.get("Agi"))}

    for n, ataque in enumerate(formatter.ataques_exibidos(val["ataques"])[:LINHAS["ataques"]], start=1):
        if ataque["bonus"] is not None and ataque["tipo"] in rules.HABILIDADE_DE_ATAQUE:
            sigla = rules.HABILIDADE_DE_ATAQUE[ataque["tipo"]]
            campo = CAMPO_DA_HABILIDADE[sigla]
            k = ataque["bonus"] - hab[sigla]
            nome = formatter.nome_curto(ataque["nome"]).replace("\\", "\\\\").replace('"', '\\"')
            formulas[f"Ataque {n}"] = _js_so_quando_mudar(
                [campo], f'var b = {_js_numero(campo)} + ({k}); event.value = "{nome} " + (b >= 0 ? "+" : "") + b;')
        if ataque.get("soma_forca") and hab.get("For") is not None:
            k = ataque["dano"] - hab["For"]
            formulas[f"Dano {n}"] = _js_so_quando_mudar(["Força"], f'event.value = {_js_numero("Força")} + ({k});')
            if ataque["tipo"] in ("corpo", "distancia"):
                formulas[f"Descrição {n}"] = _js_so_quando_mudar(["Força"], _js_descricao(ataque, f"Dano {n}"))

    # Linhas de perícia especializada cuja habilidade não é a padrão da linha (Combate à Distância: Arremesso...)
    usadas = {chave: 0 for chave in LINHAS_ESPECIALIZADAS}
    for nome in sorted(val["pericias"]):
        base = rules.nome_base(nome)
        if base not in LINHAS_ESPECIALIZADAS:
            continue
        _, prefixo, _, maximo = LINHAS_ESPECIALIZADAS[base]
        if usadas[base] == maximo:
            continue
        usadas[base] += 1
        formulas.update(formula_da_linha_de_pericia(base, usadas[base], rules.habilidade_da_pericia(nome)))
    return formulas


def _campos_do_formulario(writer):
    """{nome: referência} dos campos do formulário (o campo é o pai do widget quando o widget não tem nome)."""
    campos = {}
    for pagina in writer.pages:
        for ref in pagina.get("/Annots", []):
            anotacao = ref.get_object()
            if "/T" in anotacao:
                campos.setdefault(str(anotacao["/T"]), ref.indirect_reference if hasattr(ref, "indirect_reference")
                                  and ref.indirect_reference else ref)
            elif "/Parent" in anotacao:
                pai = anotacao.raw_get("/Parent")
                campos.setdefault(str(pai.get_object().get("/T")), pai)
    return campos


def _texto_do_js(acao):
    js = acao.get_object()["/JS"].get_object()
    return js.get_data().decode("latin-1") if hasattr(js, "get_data") else str(js)


def _formulas_que_mantem_texto(writer, campos):
    """Campo calculado preenchido com texto ("Imune", "—"): a soma do modelo o trocaria por um número."""
    formulas = {}
    for nome, ref in _campos_do_formulario(writer).items():
        acoes = ref.get_object().get("/AA")
        valor = str(campos.get(nome, "")).strip().lstrip("+-")
        if acoes is not None and "/C" in acoes.get_object() and valor and not valor.isdigit():
            formulas[nome] = MANTER_O_VALOR
    return formulas


def _aplicar_formulas(writer, formulas):
    """Grava as fórmulas nos campos e refaz a ordem de cálculo (/CO) pelas dependências.

    O modelo calculava alguns totais antes das parcelas (AcrobTotal antes de AcrobHab, Total antes de Habilidades):
    o leitor de PDF roda a lista uma vez por mudança, então esses totais ficavam um passo atrasados.
    """
    campos = _campos_do_formulario(writer)
    for nome, js in formulas.items():
        if nome not in campos:
            continue
        campo = campos[nome].get_object()
        acoes = campo.get("/AA")
        if acoes is None:
            acoes = DictionaryObject()
            campo[NameObject("/AA")] = acoes
        acoes = acoes.get_object()
        acoes[NameObject("/C")] = DictionaryObject({NameObject("/S"): NameObject("/JavaScript"),
                                                    NameObject("/JS"): TextStringObject(js)})

    formulario = writer._root_object["/AcroForm"]
    antiga = [str(ref.get_object().get("/T")) for ref in formulario.get("/CO", [])]
    calculos = {}
    for nome, ref in campos.items():
        acoes = ref.get_object().get("/AA")
        if acoes is not None and "/C" in acoes.get_object():
            calculos[nome] = _texto_do_js(acoes.get_object()["/C"])
    ordem_original = {nome: i for i, nome in enumerate(antiga)}
    nomes = sorted(calculos, key=lambda nome: ordem_original.get(nome, len(antiga)))
    depende = {nome: {d for d in re.findall(r'"([^"]+)"', js) if d in calculos and d != nome}
               for nome, js in calculos.items()}
    ordem, feitos = [], set()
    while len(ordem) < len(nomes):
        prontos = [n for n in nomes if n not in feitos and depende[n] <= feitos]
        proximo = prontos[0] if prontos else next(n for n in nomes if n not in feitos)   # ciclo: segue a ordem
        ordem.append(proximo)
        feitos.add(proximo)
    formulario[NameObject("/CO")] = ArrayObject(campos[nome] for nome in ordem)


def gerar_pdf(caminho_modelo, npc, relatorio, genero_nome):
    """Devolve os bytes de um PDF preenchido com o NPC."""
    return preencher_modelo(caminho_modelo, valores_dos_campos(npc, relatorio, genero_nome),
                            formulas=formulas_dos_campos(npc, relatorio))


def _inserir_imagem_do_personagem(writer, caminho_imagem):
    """Insere a imagem no quadro 'Desenho do Personagem' na página 1 da ficha PDF."""
    try:
        from PIL import Image
        import pypdf

        img = Image.open(caminho_imagem)
        img_w, img_h = img.size
        if not img_w or not img_h or not len(writer.pages):
            return

        # Coordenadas do campo "Desenho do Personagem" no modelo original (pt):
        x0, y0, x1, y1 = 400.814, 26.6932, 583.434, 319.725
        box_w = x1 - x0
        box_h = y1 - y0

        scale = min(box_w / img_w, box_h / img_h)
        final_w = img_w * scale
        final_h = img_h * scale
        offset_x = (box_w - final_w) / 2
        offset_y = (box_h - final_h) / 2

        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PDF")
        buf.seek(0)

        img_reader = pypdf.PdfReader(buf)
        img_xobj_ref = img_reader.pages[0]["/Resources"]["/XObject"]["/image"]

        # 1. Configura o botão do formulário "Desenho do Personagem" com a imagem como aparência (/AP /N)
        for a in writer.pages[0].get("/Annots", []):
            annot_obj = a.get_object()
            if annot_obj.get("/T") == "Desenho do Personagem":
                # Remove o fundo branco opaco (/BG) que cobria a imagem
                mk = annot_obj.get("/MK")
                if mk:
                    mk_obj = mk.get_object()
                    if "/BG" in mk_obj:
                        del mk_obj[NameObject("/BG")]
                    mk_obj[NameObject("/TP")] = pypdf.generic.NumberObject(1)

                # Cria o Form XObject com a imagem desenhada nas dimensões exatas do botão
                stream_content = (
                    f"q\n0 0 {box_w:.3f} {box_h:.3f} re\nW\nn\n"
                    f"q\n{final_w:.3f} 0 0 {final_h:.3f} {offset_x:.3f} {offset_y:.3f} cm\n/Im0 Do\nQ\nQ\n"
                ).encode("latin-1")

                form_xobj = pypdf.generic.DecodedStreamObject()
                form_xobj.set_data(stream_content)
                form_xobj.update({
                    NameObject("/Type"): NameObject("/XObject"),
                    NameObject("/Subtype"): NameObject("/Form"),
                    NameObject("/BBox"): pypdf.generic.ArrayObject([
                        pypdf.generic.FloatObject(0),
                        pypdf.generic.FloatObject(0),
                        pypdf.generic.FloatObject(box_w),
                        pypdf.generic.FloatObject(box_h),
                    ]),
                    NameObject("/Resources"): pypdf.generic.DictionaryObject({
                        NameObject("/XObject"): pypdf.generic.DictionaryObject({
                            NameObject("/Im0"): img_xobj_ref
                        })
                    })
                })
                form_ref = writer._add_object(form_xobj)
                annot_obj[NameObject("/AP")] = pypdf.generic.DictionaryObject({
                    NameObject("/N"): form_ref
                })
                break

        # 2. Também mescla no conteúdo estático da página (para leitores que desativam formulários interativos)
        tx = x0 + offset_x
        ty = y0 + offset_y
        img_page = img_reader.pages[0]
        img_page.add_transformation(pypdf.Transformation().scale(scale, scale).translate(tx, ty))
        writer.pages[0].merge_page(img_page, over=False)
    except Exception:
        pass


def preencher_modelo(caminho_modelo, campos, caminho_imagem=None, formulas=None):
    """Limpa o modelo e preenche os campos dados; devolve os bytes do PDF.

    formulas: {campo: JavaScript} de cálculos a acrescentar (além das correções do modelo, que entram sempre).
    """
    leitor = PdfReader(caminho_modelo)
    writer = PdfWriter(clone_from=leitor)

    valores = {}
    for nome, campo in (leitor.get_fields() or {}).items():
        if campo.get("/FT") == "/Tx" and nome not in CAMPOS_ROTULO:
            valores[nome] = ""
    valores.update(campos)
    marcadores = {"Secreta": "/Off", "Pública": "/Off"}

    writer.update_page_form_field_values(None, valores, auto_regenerate=False)
    writer.update_page_form_field_values(None, marcadores, auto_regenerate=False)
    _ajustar_fonte_dos_poderes(writer)
    writer.set_need_appearances_writer(True)
    _corrigir_formula_do_combate_a_distancia(writer)
    _aplicar_formulas(writer, {**FORMULAS_CORRIGIDAS, **_formulas_que_mantem_texto(writer, campos),
                               **(formulas or {})})

    if caminho_imagem and Path(caminho_imagem).is_file():
        _inserir_imagem_do_personagem(writer, caminho_imagem)

    saida = io.BytesIO()
    writer.write(saida)
    return saida.getvalue()


def _ajustar_fonte_dos_poderes(writer):
    """Deixa o leitor ajustar o tamanho da fonte para caber em cada linha do PDF."""
    for pagina in writer.pages:
        for anotacao_ref in pagina.get("/Annots", []):
            anotacao = anotacao_ref.get_object()
            if str(anotacao.get("/T", "")).startswith("Poderes e Dispositivos "):
                anotacao[NameObject("/DA")] = TextStringObject("/Comi 0 Tf 0 g")
