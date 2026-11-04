"""Escudo do Mestre em planilha (.xlsx): uma folha por aba do escudo, com os blocos um embaixo do outro.

Lê o mesmo escudo montado da página e do PDF (nucleo/escudo.montar). Cada tabela tem título, cabeçalho azul e linhas
listradas; listas e fórmulas ocupam uma linha por item, mescladas na largura da folha; o **negrito** vira texto rico.
As folhas saem prontas para imprimir em A4 deitado, cabendo na largura da página.
"""

import io
import math
import re

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import escudo as escudo_mod

AZUL = "006FAE"
AZUL_TITULO = "0083CA"
CINZA = "4A5D72"
CABECALHO = PatternFill("solid", fgColor="C7DBF1")
LISTRA = PatternFill("solid", fgColor="F3F8FD")
LINHA_FORTE = Border(bottom=Side(style="medium", color=AZUL))
LINHA_FINA = Border(bottom=Side(style="thin", color="B3CAE2"))

# A folha é uma grade de colunas estreitas e iguais. Cada coluna de uma tabela mescla quantas colunas da grade
# precisar, nas proporções daquela tabela: assim uma tabela não herda as larguras de outra da mesma folha.
COLUNAS_DA_GRADE = 28
LARGURA_DA_GRADE = 5         # em caracteres; a folha tem 140 de largura útil
LARGURA_MINIMA, LARGURA_MAXIMA = 6, 60
ALTURA_DA_LINHA = 14         # pontos por linha de texto
FONTE, TAMANHO = "Calibri", 10
NUMERO = re.compile(r"^\d+$")


def _fonte(**estilo):
    return Font(name=FONTE, size=estilo.pop("size", TAMANHO), **estilo)


def _rico(texto, cor=None, italico=False):
    """Texto com **negrito** como texto rico do Excel (ou texto simples, se não tiver negrito)."""
    partes = escudo_mod.partes_do_texto(str(texto))
    if not any(negrito for _, negrito in partes) and cor is None and not italico:
        return str(texto)
    return CellRichText(*[TextBlock(InlineFont(rFont=FONTE, sz=TAMANHO, b=negrito, i=italico, color=cor), trecho)
                          for trecho, negrito in partes])


def _texto_puro(texto):
    return "".join(t for t, _ in escudo_mod.partes_do_texto(str(texto)))


def _linhas_de_texto(texto, colunas_da_grade):
    """Quantas linhas um texto ocupa em tantas colunas da grade, para ajustar a altura da linha."""
    largura = colunas_da_grade * LARGURA_DA_GRADE * 1.3   # Calibri 10 é mais estreita que a unidade de largura
    return max(1, math.ceil(len(_texto_puro(texto)) / largura))


def _vaos(bloco):
    """Quantas colunas da grade cada coluna da tabela ocupa: proporcional ao texto mais longo dela, no mínimo 2.
    Tabelas curtas não se esticam até a largura toda da folha."""
    preferidas = []
    for i, nome in enumerate(bloco["colunas"]):
        maior = max([len(_texto_puro(nome))] + [len(_texto_puro(linha[i])) for linha in bloco["linhas"]])
        preferidas.append(min(max(maior + 2, LARGURA_MINIMA), LARGURA_MAXIMA))
    total = min(COLUNAS_DA_GRADE, max(math.ceil(sum(preferidas) / LARGURA_DA_GRADE), 2 * len(preferidas)))
    vaos = [max(2, int(total * p / sum(preferidas))) for p in preferidas]
    # O que o arredondamento tirou vai para as colunas de texto mais longo.
    for i in sorted(range(len(vaos)), key=lambda i: -preferidas[i]):
        if sum(vaos) >= total:
            break
        vaos[i] += 1
    return vaos


def _celula(folha, linha, coluna, vao, valor, **estilo):
    """Escreve na célula e mescla `vao` colunas da grade; o estilo vai para todas, para a borda e o fundo
    aparecerem na mesclagem inteira (no Excel e no LibreOffice)."""
    folha.cell(row=linha, column=coluna, value=valor)
    for c in range(coluna, coluna + vao):
        celula = folha.cell(row=linha, column=c)
        celula.alignment = estilo.get("alignment", Alignment(wrap_text=True, vertical="top"))
        for nome in ("font", "fill", "border"):
            if nome in estilo:
                setattr(celula, nome, estilo[nome])
    if vao > 1:
        folha.merge_cells(start_row=linha, start_column=coluna, end_row=linha, end_column=coluna + vao - 1)


def _faixa(folha, linha, valor, altura_em_linhas=1, **estilo):
    """Uma linha com o texto na largura toda da folha."""
    _celula(folha, linha, 1, COLUNAS_DA_GRADE, valor, **estilo)
    folha.row_dimensions[linha].height = ALTURA_DA_LINHA * altura_em_linhas + 2


def _tabela(folha, linha, bloco):
    vaos = _vaos(bloco)
    inicios = [1 + sum(vaos[:i]) for i in range(len(vaos))]
    for nome, inicio, vao in zip(bloco["colunas"], inicios, vaos):
        _celula(folha, linha, inicio, vao, _texto_puro(nome), font=_fonte(bold=True), fill=CABECALHO,
                border=LINHA_FORTE, alignment=Alignment(wrap_text=True, vertical="center"))
    folha.row_dimensions[linha].height = ALTURA_DA_LINHA * max(
        _linhas_de_texto(n, v) for n, v in zip(bloco["colunas"], vaos)) + 3
    linha += 1
    for n, valores in enumerate(bloco["linhas"]):
        for valor, inicio, vao in zip(valores, inicios, vaos):
            texto = str(valor)
            estilo = {"font": _fonte(), "border": LINHA_FINA,
                      "alignment": Alignment(wrap_text=True, vertical="top", horizontal="left")}
            if n % 2:
                estilo["fill"] = LISTRA
            _celula(folha, linha, inicio, vao, int(texto) if NUMERO.match(texto) else _rico(texto), **estilo)
        folha.row_dimensions[linha].height = ALTURA_DA_LINHA * max(
            _linhas_de_texto(v, vao) for v, vao in zip(valores, vaos)) + 2
        linha += 1
    return linha


def _folha_da_aba(livro, aba):
    folha = livro.create_sheet(aba["nome"][:31])
    for i in range(1, COLUNAS_DA_GRADE + 1):
        folha.column_dimensions[get_column_letter(i)].width = LARGURA_DA_GRADE

    _faixa(folha, 1, aba["nome"], font=_fonte(bold=True, size=15, color=AZUL), border=LINHA_FORTE)
    folha.row_dimensions[1].height = 22
    linha = 3
    for bloco in aba["blocos"]:
        if bloco.get("titulo"):
            _faixa(folha, linha, bloco["titulo"], font=_fonte(bold=True, size=12, color=AZUL_TITULO))
            folha.row_dimensions[linha].height = 18
            linha += 1
        if bloco["tipo"] == "tabela":
            linha = _tabela(folha, linha, bloco)
        else:
            marcador = "" if bloco["tipo"] == "formulas" else "• "
            for item in bloco["itens"]:
                _faixa(folha, linha, _rico(marcador + item), _linhas_de_texto(item, COLUNAS_DA_GRADE),
                       font=_fonte())
                linha += 1
        if bloco.get("nota"):
            _faixa(folha, linha, _rico(bloco["nota"], cor=CINZA, italico=True),
                   _linhas_de_texto(bloco["nota"], COLUNAS_DA_GRADE), font=_fonte(italic=True, color=CINZA))
            linha += 1
        linha += 1

    folha.sheet_view.showGridLines = False
    folha.page_setup.orientation = "landscape"
    folha.page_setup.paperSize = folha.PAPERSIZE_A4
    folha.page_setup.fitToWidth, folha.page_setup.fitToHeight = 1, 0
    folha.sheet_properties.pageSetUpPr.fitToPage = True
    folha.print_options.horizontalCentered = True
    folha.page_margins.left = folha.page_margins.right = 0.4
    folha.page_margins.top = folha.page_margins.bottom = 0.5
    return folha


def gerar_xlsx(escudo):
    """Bytes da planilha do escudo já montado (escudo.montar)."""
    livro = Workbook()
    for aba in escudo["abas"]:
        _folha_da_aba(livro, aba)
    del livro[livro.sheetnames[0]]   # a folha vazia que o Workbook cria
    livro.properties.title = escudo["titulo"]
    saida = io.BytesIO()
    livro.save(saida)
    return saida.getvalue()
