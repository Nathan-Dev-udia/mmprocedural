"""Preenche a ficha de personagem editável (PDF) com um NPC gerado.

O modelo fica em data/ficha_editavel.pdf. Ele tem campos de formulário com
cálculos automáticos (totais de perícias, defesas e custos). Por isso os
valores são preenchidos de forma coerente com essas fórmulas: se o leitor de
PDF recalcular, os números continuam certos.

Ajustes feitos na cópia gerada (o modelo original não é alterado):
- todos os campos de dados são limpos antes (o modelo veio preenchido);
- a fórmula do total do 2º Combate à Distância é corrigida (ela somava o
  nome da especialização em vez das graduações).
"""

import io
import textwrap

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

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
            campos[f"{prefixo}Total"] = str(pericia["total"])
            continue
        campo_nome, prefixo, sufixo_outros, maximo = LINHAS_ESPECIALIZADAS[base]
        if usadas[base] == maximo:
            notas_extras.append(f"Perícia: {nome} {pericia['graduacoes']} ({_sinal(pericia['total'])})")
            continue
        usadas[base] += 1
        n = usadas[base]
        hab_padrao = val["habilidades"][HABILIDADE_PADRAO_DA_LINHA[base]]
        outros = val["habilidades"][hab_da_pericia] - hab_padrao
        campos[campo_nome.format(n=n)] = nome.split(":", 1)[1].strip()
        campos[f"{prefixo}Hab {n}"] = str(hab_padrao)
        campos[f"{prefixo}Per {n}"] = str(pericia["graduacoes"])
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


def gerar_pdf(caminho_modelo, npc, relatorio, genero_nome):
    """Devolve os bytes de um PDF preenchido com o NPC."""
    return preencher_modelo(caminho_modelo, valores_dos_campos(npc, relatorio, genero_nome))


def preencher_modelo(caminho_modelo, campos):
    """Limpa o modelo e preenche os campos dados; devolve os bytes do PDF."""
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
