"""Páginas de referência do personagem no PDF (depois da ficha): vantagens, poderes, itens e termos de regra.

O conteúdo vem de referencia.montar; aqui só se desenha, no visual da ficha (logo, bordas azuis arredondadas,
campos com linha). Quantas páginas forem precisas.

- Cabeçalho (só na primeira página): logo e um quadro com nome, jogador, identidade e nível de poder.
- Vantagens: cartões em três colunas (nome e custo no topo, o que faz embaixo).
- Poderes e equipamento: um quadro arredondado com um parágrafo por item.
- Termos de regra: título com faixa e a lista, sem quadro.
"""

import io
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import companheiros

LOGO = Path(__file__).resolve().parent.parent / "dados" / "comum" / "logo_ficha.png"
PROPORCAO_DO_LOGO = 174 / 650   # altura / largura da imagem

# Cores da ficha: borda azul, campos azul-claro; títulos num azul mais escuro.
AZUL = colors.HexColor("#3a86d4")
AZUL_ESCURO = colors.HexColor("#1f3f73")
AZUL_CLARO = colors.HexColor("#d6e5f6")
AZUL_FAIXA = colors.HexColor("#e6eff9")
TINTA = colors.HexColor("#1f2937")
TINTA_SUAVE = colors.HexColor("#4b5563")
ETIQUETA = "#9a5b13"

ESTILO_SECAO = ParagraphStyle("ref_secao", fontName="Helvetica-Bold", fontSize=13, leading=15,
                              textColor=AZUL_ESCURO, spaceBefore=2, spaceAfter=3)
ESTILO_NOTA = ParagraphStyle("ref_nota", fontName="Helvetica-Oblique", fontSize=7.3, leading=9.2,
                             textColor=TINTA_SUAVE)
ESTILO_ITEM = ParagraphStyle("ref_item", fontName="Helvetica", fontSize=7.8, leading=9.8, textColor=TINTA,
                             leftIndent=8, firstLineIndent=-8)
ESTILO_CARTAO_NOME = ParagraphStyle("ref_cartao_nome", fontName="Helvetica-Bold", fontSize=8.6, leading=10,
                                    textColor=AZUL_ESCURO)
ESTILO_CARTAO_TEXTO = ParagraphStyle("ref_cartao_texto", fontName="Helvetica", fontSize=7.2, leading=8.8,
                                     textColor=TINTA)

MARGEM = 24
ALTURA_DO_CABECALHO = 52
COLUNAS_DE_VANTAGENS = 3

# Títulos das seções no PDF, quando diferem dos dados.
TITULOS = {"Equipamento": "Equipamento & Itens"}


def _etiqueta(item, tamanho=6.8):
    if not item.get("etiqueta"):
        return ""
    return f" <font color='{ETIQUETA}' size='{tamanho}'>({escape(item['etiqueta'])})</font>"


def _paragrafo_do_item(item):
    texto = " ".join(escape(linha) for linha in item["linhas"])
    return Paragraph(f"<b>{escape(item['nome'])}</b>{_etiqueta(item)}" + (f" — {texto}" if texto else ""), ESTILO_ITEM)


def _titulo(secao):
    return Paragraph(escape(TITULOS.get(secao["titulo"], secao["titulo"]).upper()), ESTILO_SECAO)


PADDING_DO_CARTAO = {"lados": 5, "nome": (3, 2), "texto": (2, 4)}   # (em cima, embaixo)


def _partes_do_cartao(item):
    return (Paragraph(f"{escape(item['nome'])}{_etiqueta(item, 6.4)}", ESTILO_CARTAO_NOME),
            Paragraph(" ".join(escape(linha) for linha in item["linhas"]), ESTILO_CARTAO_TEXTO))


def _alturas(partes, largura):
    """Altura da faixa do nome e do texto de um cartão, com os espaçamentos."""
    util = largura - 2 * PADDING_DO_CARTAO["lados"]
    nome, texto = partes
    return (nome.wrap(util, 1000)[1] + sum(PADDING_DO_CARTAO["nome"]),
            texto.wrap(util, 1000)[1] + sum(PADDING_DO_CARTAO["texto"]))


def _cartao(partes, largura, alturas):
    """Um cartão de vantagem: nome e custo numa faixa azul-clara, o que faz embaixo. `alturas` iguala os
    cartões da mesma linha da grade."""
    tabela = Table([[partes[0]], [partes[1]]], colWidths=[largura], rowHeights=list(alturas))
    tabela.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, AZUL),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_CLARO),
        ("LEFTPADDING", (0, 0), (-1, -1), PADDING_DO_CARTAO["lados"]),
        ("RIGHTPADDING", (0, 0), (-1, -1), PADDING_DO_CARTAO["lados"]),
        ("TOPPADDING", (0, 0), (-1, 0), PADDING_DO_CARTAO["nome"][0]),
        ("BOTTOMPADDING", (0, 0), (-1, 0), PADDING_DO_CARTAO["nome"][1]),
        ("TOPPADDING", (0, 1), (-1, 1), PADDING_DO_CARTAO["texto"][0]),
        ("BOTTOMPADDING", (0, 1), (-1, 1), PADDING_DO_CARTAO["texto"][1]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tabela


def _quadro(linhas, largura, padding=6):
    """Quadro de borda azul arredondada; cada linha é uma célula (a tabela quebra entre páginas por linha)."""
    tabela = Table([[linha] for linha in linhas], colWidths=[largura])
    tabela.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.2, AZUL),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("TOPPADDING", (0, 0), (-1, 0), padding),
        ("BOTTOMPADDING", (0, -1), (-1, -1), padding),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tabela


def _secao_em_cartoes(secao, largura):
    espaco, borda, n = 5, 6, COLUNAS_DE_VANTAGENS
    largura_do_cartao = (largura - 2 * borda - (n - 1) * espaco) / n
    linhas = []
    for i in range(0, len(secao["itens"]), n):
        partes = [_partes_do_cartao(item) for item in secao["itens"][i:i + n]]
        alturas = [_alturas(p, largura_do_cartao) for p in partes]
        iguais = (max(a[0] for a in alturas), max(a[1] for a in alturas))
        linha = [_cartao(p, largura_do_cartao, iguais) for p in partes]
        linhas.append(linha + [""] * (n - len(linha)))
    # Cada célula tem meio espaço de cada lado; a primeira e a última têm a borda do quadro no lado de fora.
    meio = espaco / 2
    larguras = [largura_do_cartao + espaco] * n
    larguras[0] += borda - meio
    larguras[-1] += borda - meio
    grade = Table(linhas, colWidths=larguras)
    grade.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.2, AZUL),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), meio),
        ("RIGHTPADDING", (0, 0), (-1, -1), meio),
        ("LEFTPADDING", (0, 0), (0, -1), borda),
        ("RIGHTPADDING", (-1, 0), (-1, -1), borda),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
    ]))
    elementos = [_titulo(secao)]
    if secao.get("nota"):
        elementos += [Paragraph(escape(secao["nota"]), ESTILO_NOTA), Spacer(1, 2)]
    return [KeepTogether(elementos + [grade])] if len(linhas) <= 3 else elementos + [grade]


def _secao_em_quadro(secao, largura):
    linhas = []
    if secao.get("nota"):
        linhas.append(Paragraph(escape(secao["nota"]), ESTILO_NOTA))
    linhas += [_paragrafo_do_item(item) for item in secao["itens"]]
    quadro = _quadro(linhas, largura)
    # O título não fica sozinho no pé da página: o quadro quebra por linha e o título vai junto da primeira.
    return [_titulo(secao), quadro]


def _secao_em_lista(secao, largura):
    faixa = Table([[_titulo(secao)]], colWidths=[largura])
    faixa.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL_FAIXA),
        ("LINEBELOW", (0, 0), (-1, -1), 1, AZUL),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    cabecalho = [faixa, Spacer(1, 3)]
    if secao.get("nota"):
        cabecalho += [Paragraph(escape(secao["nota"]), ESTILO_NOTA), Spacer(1, 2)]
    itens = []
    for item in secao["itens"]:
        itens += [_paragrafo_do_item(item), Spacer(1, 2)]
    return [KeepTogether(cabecalho + itens[:2])] + itens[2:]


def _campo(canvas, rotulo, valor, x, y, ate):
    """Rótulo em negrito, o valor e a linha do campo até a coordenada `ate` (como os campos da ficha)."""
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(AZUL_ESCURO)
    canvas.drawString(x, y, rotulo)
    inicio = x + canvas.stringWidth(rotulo, "Helvetica-Bold", 9) + 4
    canvas.setStrokeColor(AZUL)
    canvas.setLineWidth(0.8)
    canvas.line(inicio, y - 2, ate, y - 2)
    if valor not in (None, ""):
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(TINTA)
        canvas.drawString(inicio + 2, y, str(valor))


def _desenhar_cabecalho(rotulo, nome, campos):
    """Cabeçalho da primeira página: o logo e o quadro de campos. `campos`: três (rótulo, valor) na segunda linha."""
    def desenhar(canvas, doc):
        largura, altura = doc.pagesize
        topo = altura - 20
        canvas.saveState()
        largura_do_logo = 165
        if LOGO.is_file():
            canvas.drawImage(str(LOGO), MARGEM, topo - largura_do_logo * PROPORCAO_DO_LOGO - 2,
                             width=largura_do_logo, height=largura_do_logo * PROPORCAO_DO_LOGO, mask="auto")
        x = MARGEM + largura_do_logo + 8
        fim = largura - MARGEM
        canvas.setStrokeColor(AZUL)
        canvas.setLineWidth(1.2)
        canvas.roundRect(x, topo - ALTURA_DO_CABECALHO + 4, fim - x, ALTURA_DO_CABECALHO - 4, 8)
        dentro, fim_dentro = x + 7, fim - 7
        _campo(canvas, rotulo, nome, dentro, topo - 18, fim_dentro)
        linha = topo - 38
        terco = (fim_dentro - dentro) / 3
        (r1, v1), (r2, v2), (r3, v3) = campos
        _campo(canvas, r1, v1, dentro, linha, dentro + terco + 10)
        _campo(canvas, r2, v2, dentro + terco + 18, linha, dentro + 2 * terco + 5)
        _campo(canvas, r3, v3, dentro + 2 * terco + 13, linha, fim_dentro)
        canvas.restoreState()
    return desenhar


def gerar_paginas(referencia, largura=603, altura=783):
    """Bytes de um PDF com a referência; None se não houver nada para explicar."""
    if not referencia["secoes"]:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(largura, altura), leftMargin=MARGEM, rightMargin=MARGEM,
                            topMargin=22, bottomMargin=22, title=referencia["titulo"])
    largura_util = largura - 2 * MARGEM
    elementos = [Spacer(1, ALTURA_DO_CABECALHO + 2)]
    for secao in referencia["secoes"]:
        if secao["titulo"] == "Vantagens":
            elementos += _secao_em_cartoes(secao, largura_util)
        elif secao["titulo"] == "Termos de regra":
            elementos += _secao_em_lista(secao, largura_util)
        else:
            elementos += _secao_em_quadro(secao, largura_util)
        elementos.append(Spacer(1, 8))
    cabecalho = _desenhar_cabecalho("REFERÊNCIA DO PERSONAGEM:", referencia.get("nome"),
                                    [("JOGADOR:", referencia.get("jogador")), ("IDENTIDADE:", ""),
                                     ("NÍVEL DE PODER:", referencia.get("np"))])
    doc.build(elementos, onFirstPage=cabecalho)
    return buf.getvalue()


# ---------------------------------------------------------------- página do companheiro

NOMES_DAS_HABILIDADES = {"For": "Força", "Agi": "Agilidade", "Lut": "Luta", "Pro": "Prontidão",
                         "Vig": "Vigor", "Des": "Destreza", "Int": "Intelecto", "Pre": "Presença"}
ESTILO_ROTULO = ParagraphStyle("ref_rotulo", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=AZUL_ESCURO)
ESTILO_VALOR = ParagraphStyle("ref_valor", fontName="Helvetica-Bold", fontSize=11, leading=13, textColor=TINTA,
                              alignment=1)


def _caixas_de_valores(pares, colunas, largura):
    """Grade de (rótulo, valor): o rótulo em negrito e o valor numa caixa azul-clara, como os campos da ficha."""
    linhas = [pares[i:i + colunas] for i in range(0, len(pares), colunas)]
    celulas, estilo = [], [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for r, linha in enumerate(linhas):
        celulas.append([])
        for c in range(colunas):
            rotulo, valor = linha[c] if c < len(linha) else ("", "")
            celulas[r] += [Paragraph(escape(rotulo), ESTILO_ROTULO), Paragraph(escape(str(valor)), ESTILO_VALOR)]
            if rotulo:
                estilo += [("BACKGROUND", (2 * c + 1, r), (2 * c + 1, r), AZUL_CLARO),
                           ("ROUNDEDCORNERS", [4, 4, 4, 4])]
    larg_rotulo, larg_valor = (largura - 12) / colunas * 0.62, (largura - 12) / colunas * 0.38
    tabela = Table(celulas, colWidths=[larg_rotulo, larg_valor] * colunas)
    tabela.setStyle(TableStyle(estilo))
    return tabela


def gerar_pagina_do_companheiro(bloco, posse="", dono="", jogador=""):
    """Bytes de um PDF de uma página com a ficha do companheiro (bloco de companheiros.bloco)."""
    buf = io.BytesIO()
    largura, altura = 603, 783
    doc = SimpleDocTemplate(buf, pagesize=(largura, altura), leftMargin=MARGEM, rightMargin=MARGEM,
                            topMargin=22, bottomMargin=22, title=f"Companheiro: {bloco['nome']}")
    util = largura - 2 * MARGEM
    sinal = lambda v: f"{v:+d}"
    habilidades = [(NOMES_DAS_HABILIDADES[h], sinal(bloco["habilidades"][h]))
                   for h in ("For", "Agi", "Lut", "Pro", "Vig", "Des", "Int", "Pre")]
    defesas = [(d, bloco["defesas"][d]) for d in bloco["defesas"]] + [("Iniciativa", sinal(bloco["iniciativa"]))]
    elementos = [Spacer(1, ALTURA_DO_CABECALHO + 2),
                 _quadro([_caixas_de_valores(habilidades, 4, util - 12)], util),
                 Spacer(1, 6),
                 _quadro([_caixas_de_valores(defesas, 3, util - 12)], util), Spacer(1, 8)]

    def secao(titulo, itens):
        if itens:
            elementos.extend([_titulo({"titulo": titulo}), _quadro([_paragrafo_do_item(i) for i in itens], util),
                              Spacer(1, 8)])

    secao("Ataque", [{"nome": a["nome"], "etiqueta": "", "linhas": [
        f"{sinal(a['bonus'])} de bônus, Dano {a['dano']}, crítico {companheiros.critico(a)}."]}
        for a in bloco["ataques"]])
    secao("Perícias", [{"nome": p["nome"], "etiqueta": "", "linhas": [
        f"{sinal(p['total'])} ({p['graduacoes']} graduações)."]} for p in bloco["pericias"]])
    secao("Poderes", [{"nome": p["nome"], "etiqueta": f"{p['custo']} PP", "linhas": [p["explicacao"]] if p["explicacao"] else []}
                      for p in bloco["poderes"]])
    secao("Vantagens", [{"nome": v["nome"], "etiqueta": "", "linhas": [v["explicacao"]]} for v in bloco["vantagens"]])
    secao("Equipamento", [{"nome": e["nome"], "etiqueta": "", "linhas": [e["explicacao"]]}
                          for e in bloco.get("equipamento", [])])
    secao("Sobre o companheiro", [{"nome": bloco["nome"], "etiqueta": posse,
                                   "linhas": [bloco["descricao"], f"Fonte: {bloco['fonte']}."]}])
    cabecalho = _desenhar_cabecalho("COMPANHEIRO:", bloco["nome"],
                                    [("DONO:", dono), ("POSSE:", posse.split()[-1] if posse else ""),
                                     ("NÍVEL DE PODER:", bloco["np"])])
    doc.build(elementos, onFirstPage=cabecalho)
    return buf.getvalue()
