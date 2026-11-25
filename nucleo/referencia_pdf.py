"""Páginas de referência do personagem no PDF (depois da ficha): vantagens, poderes, itens e termos de regra.

O conteúdo vem de referencia.montar; aqui só se desenha. Quantas páginas forem precisas.
"""

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DESTAQUE = colors.HexColor("#9a3412")
FUNDO = colors.HexColor("#f4ede1")
TINTA = colors.HexColor("#1f2937")
TINTA_SUAVE = colors.HexColor("#6b5a48")

ESTILO_TITULO = ParagraphStyle("ref_titulo", fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=DESTAQUE)
ESTILO_SUB = ParagraphStyle("ref_sub", fontName="Helvetica-Oblique", fontSize=8, leading=10, textColor=TINTA_SUAVE)
ESTILO_SECAO = ParagraphStyle("ref_secao", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=DESTAQUE)
ESTILO_NOTA = ParagraphStyle("ref_nota", fontName="Helvetica-Oblique", fontSize=7.5, leading=9.5, textColor=TINTA_SUAVE)
ESTILO_ITEM = ParagraphStyle("ref_item", fontName="Helvetica", fontSize=7.8, leading=9.8, textColor=TINTA,
                             leftIndent=8, firstLineIndent=-8, spaceAfter=2.5)


def _faixa_da_secao(titulo, largura):
    tabela = Table([[Paragraph(escape(titulo.upper()), ESTILO_SECAO)]], colWidths=[largura])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FUNDO),
        ("LINEBELOW", (0, 0), (-1, -1), 0.8, DESTAQUE),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabela


def _paragrafo_do_item(item):
    etiqueta = (f" <font color='#6b5a48' size='6.8'>[{escape(item['etiqueta'])}]</font>"
                if item.get("etiqueta") else "")
    texto = " ".join(escape(linha) for linha in item["linhas"])
    return Paragraph(f"<b>{escape(item['nome'])}</b>{etiqueta} — {texto}", ESTILO_ITEM)


def gerar_paginas(referencia, largura=603, altura=783):
    """Bytes de um PDF com a referência; None se não houver nada para explicar."""
    if not referencia["secoes"]:
        return None
    buf = io.BytesIO()
    margem = 24
    doc = SimpleDocTemplate(buf, pagesize=(largura, altura), leftMargin=margem, rightMargin=margem,
                            topMargin=22, bottomMargin=22, title=referencia["titulo"])
    largura_util = largura - 2 * margem
    elementos = [Paragraph(escape(referencia["titulo"]), ESTILO_TITULO),
                 Paragraph(escape(referencia["subtitulo"]), ESTILO_SUB), Spacer(1, 6)]
    for secao in referencia["secoes"]:
        cabecalho = [_faixa_da_secao(secao["titulo"], largura_util), Spacer(1, 3)]
        if secao.get("nota"):
            cabecalho += [Paragraph(escape(secao["nota"]), ESTILO_NOTA), Spacer(1, 3)]
        itens = [_paragrafo_do_item(item) for item in secao["itens"]]
        # O título da seção não fica sozinho no pé da página: vai junto com o primeiro item.
        elementos.append(KeepTogether(cabecalho + itens[:1]))
        elementos += itens[1:]
        elementos.append(Spacer(1, 6))
    doc.build(elementos)
    return buf.getvalue()
