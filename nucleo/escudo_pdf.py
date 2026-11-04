"""Escudo do Mestre em PDF: A4 deitado, duas colunas, cada aba começando numa página nova.

Lê o mesmo escudo montado da página (nucleo/escudo.montar). Usa a Helvetica padrão do PDF, que dispensa arquivo de
fonte no servidor; por isso os caracteres fora do Windows-1252 (a seta →) são trocados antes de desenhar.
"""

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)

from . import escudo as escudo_mod

# Cores da ficha editável de M&M (as mesmas do site).
AZUL = colors.HexColor("#006fae")
AZUL_TITULO = colors.HexColor("#0083ca")
AZUL_CAMPO = colors.HexColor("#c7dbf1")
AZUL_CLARO = colors.HexColor("#f3f8fd")
BORDA = colors.HexColor("#b3cae2")
TINTA = colors.HexColor("#0f1c2b")
TINTA_SUAVE = colors.HexColor("#4a5d72")

MARGEM = 9 * mm
ESPACO_ENTRE_COLUNAS = 7 * mm
ALTURA_DO_TOPO = 10 * mm
TROCAS = str.maketrans({"→": "›", "≤": "<", "≥": ">"})

TEXTO = ParagraphStyle("texto", fontName="Helvetica", fontSize=7.4, leading=9, textColor=TINTA, alignment=TA_LEFT)
CELULA = ParagraphStyle("celula", parent=TEXTO, fontSize=7, leading=8.4)
CABECALHO = ParagraphStyle("cabecalho", parent=CELULA, fontName="Helvetica-Bold", textColor=TINTA)
TITULO = ParagraphStyle("titulo", parent=TEXTO, fontName="Helvetica-Bold", fontSize=9, leading=11,
                        textColor=AZUL_TITULO, spaceBefore=2, spaceAfter=2)
NOTA = ParagraphStyle("nota", parent=TEXTO, fontName="Helvetica-Oblique", fontSize=6.6, leading=8,
                      textColor=TINTA_SUAVE, spaceBefore=1.5)
ITEM = ParagraphStyle("item", parent=TEXTO, leftIndent=7, bulletIndent=0, spaceAfter=1.2)
FORMULA = ParagraphStyle("formula", parent=TEXTO, fontSize=7.8, leading=9.6, spaceAfter=1.2)


def _marcado(texto):
    """Texto do escudo (com **negrito**) em marcação de Paragraph."""
    return "".join(f"<b>{escape(t)}</b>" if negrito else escape(t)
                   for t, negrito in escudo_mod.partes_do_texto(str(texto).translate(TROCAS)))


class _MarcaAba(Flowable):
    """Marcador sem tamanho: avisa o cabeçalho da página qual aba está sendo desenhada."""

    def __init__(self, nome):
        super().__init__()
        self.nome = nome

    def wrap(self, *_):
        return 0, 0

    def draw(self):
        self.canv._aba_do_escudo = self.nome


def _maior_palavra(texto, fonte, tamanho):
    palavras = escudo_mod.partes_do_texto(str(texto).translate(TROCAS))
    return max((stringWidth(p, fonte, tamanho) for trecho, _ in palavras for p in trecho.split()), default=0)


def _larguras(bloco, largura_total):
    """Larguras das colunas: cada uma cabe a sua palavra mais longa (nunca quebra "Movimento" no meio) e o que sobra
    vai proporcionalmente ao texto mais longo de cada coluna."""
    folga = 6  # padding das células e um respiro
    minimos, pesos = [], []
    for i, nome in enumerate(bloco["colunas"]):
        celulas = [str(linha[i]) for linha in bloco["linhas"]]
        minimos.append(max([_maior_palavra(nome, "Helvetica-Bold", CABECALHO.fontSize)]
                           + [_maior_palavra(c, "Helvetica-Bold", CELULA.fontSize) for c in celulas]) + folga)
        pesos.append(min(max([len(str(nome))] + [len(c) for c in celulas]), 60))
    if sum(minimos) >= largura_total:
        return [largura_total * m / sum(minimos) for m in minimos]
    sobra = largura_total - sum(minimos)
    return [m + sobra * p / sum(pesos) for m, p in zip(minimos, pesos)]


def _tabela(bloco, largura):
    dados = [[Paragraph(_marcado(c), CABECALHO) for c in bloco["colunas"]]]
    dados += [[Paragraph(_marcado(c), CELULA) for c in linha] for linha in bloco["linhas"]]
    tabela = Table(dados, colWidths=_larguras(bloco, largura), repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_CAMPO),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, AZUL),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, BORDA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
    ]
    estilo += [("BACKGROUND", (0, i), (-1, i), AZUL_CLARO) for i in range(2, len(dados), 2)]
    tabela.setStyle(TableStyle(estilo))
    return tabela


def _bloco(bloco, largura):
    """Flowables de um bloco: título, conteúdo e nota."""
    partes = [Paragraph(_marcado(bloco["titulo"]), TITULO)] if bloco.get("titulo") else []
    if bloco["tipo"] == "tabela":
        corpo = [_tabela(bloco, largura)]
    elif bloco["tipo"] == "formulas":
        corpo = [Paragraph(_marcado(item), FORMULA) for item in bloco["itens"]]
    else:
        corpo = [Paragraph(_marcado(item), ITEM, bulletText="•") for item in bloco["itens"]]
    nota = [Paragraph(_marcado(bloco["nota"]), NOTA)] if bloco.get("nota") else []
    # Título, começo do conteúdo e nota não se separam; tabelas longas podem quebrar de coluna (o cabeçalho repete).
    if bloco["tipo"] == "tabela" and len(bloco["linhas"]) > 14:
        return [CondPageBreak(40 * mm)] + partes + corpo + nota + [Spacer(1, 3.5 * mm)]
    return [KeepTogether(partes + corpo + nota), Spacer(1, 3.5 * mm)]


def gerar_pdf(escudo, versao=""):
    """Bytes do PDF do escudo já montado (escudo.montar)."""
    saida = io.BytesIO()
    largura_pagina, altura_pagina = landscape(A4)
    largura_coluna = (largura_pagina - 2 * MARGEM - ESPACO_ENTRE_COLUNAS) / 2
    altura_util = altura_pagina - 2 * MARGEM - ALTURA_DO_TOPO
    colunas = [Frame(MARGEM + i * (largura_coluna + ESPACO_ENTRE_COLUNAS), MARGEM, largura_coluna, altura_util,
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id=f"coluna{i}")
               for i in range(2)]
    titulo = escudo["titulo"].translate(TROCAS)

    def topo(canv, doc):
        canv.saveState()
        y = altura_pagina - MARGEM - 5 * mm
        canv.setFillColor(AZUL)
        canv.setFont("Helvetica-Bold", 12)
        aba = getattr(canv, "_aba_do_escudo", "")
        canv.drawString(MARGEM, y, aba)
        canv.setFont("Helvetica", 8)
        canv.setFillColor(TINTA_SUAVE)
        canv.drawRightString(largura_pagina - MARGEM, y, f"{titulo}  ·  página {doc.page}"
                             + (f"  ·  v{versao}" if versao else ""))
        canv.setStrokeColor(AZUL)
        canv.setLineWidth(1)
        canv.line(MARGEM, y - 2.5 * mm, largura_pagina - MARGEM, y - 2.5 * mm)
        # Linha fina entre as colunas.
        x = MARGEM + largura_coluna + ESPACO_ENTRE_COLUNAS / 2
        canv.setStrokeColor(BORDA)
        canv.setLineWidth(0.4)
        canv.line(x, MARGEM, x, MARGEM + altura_util)
        canv.restoreState()

    doc = BaseDocTemplate(saida, pagesize=(largura_pagina, altura_pagina), leftMargin=MARGEM, rightMargin=MARGEM,
                          topMargin=MARGEM, bottomMargin=MARGEM, title=titulo, author="mmprocedural")
    doc.addPageTemplates([PageTemplate(id="escudo", frames=colunas, onPageEnd=topo)])

    historia = []
    for n, aba in enumerate(escudo["abas"]):
        if n:
            historia.append(PageBreak())
        historia.append(_MarcaAba(aba["nome"].translate(TROCAS)))
        for bloco in aba["blocos"]:
            historia.extend(_bloco(bloco, largura_coluna))
    doc.build(historia)
    return saida.getvalue()
