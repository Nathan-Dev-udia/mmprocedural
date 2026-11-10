"""Gera a página extra do PDF (Página 3) para o gênero Chamado de Cthulhu:
Registro de Sanidade d100, contador 00-99, regras de choque mental, acessos de loucura e fobias.
"""

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import sanidade

# Paleta temática de horror cósmico (tons abissais e pergaminho)
ABISSO = colors.HexColor("#142834")
VERDE_OCULTO = colors.HexColor("#1b4d3e")
VERMELHO_SANGUE = colors.HexColor("#7a1c1c")
CINZA_FUNDO = colors.HexColor("#f4f7f6")
CINZA_CLARO = colors.HexColor("#e8eeec")
BORDA = colors.HexColor("#8ca0a8")
BORDA_SUAVE = colors.HexColor("#c5d0d4")
TINTA = colors.HexColor("#111827")
TINTA_SUAVE = colors.HexColor("#4b5563")
BRANCO = colors.white

ESTILO_BASE = ParagraphStyle("base", fontName="Helvetica", fontSize=7, leading=8.5, textColor=TINTA)
ESTILO_TITULO = ParagraphStyle("titulo", parent=ESTILO_BASE, fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=ABISSO, alignment=TA_CENTER)
ESTILO_SUB = ParagraphStyle("sub", parent=ESTILO_BASE, fontName="Helvetica-Oblique", fontSize=7.5, leading=9.5, textColor=TINTA_SUAVE, alignment=TA_CENTER)
ESTILO_CAB = ParagraphStyle("cab", parent=ESTILO_BASE, fontName="Helvetica-Bold", fontSize=7, leading=8.5, textColor=ABISSO)
ESTILO_SEC = ParagraphStyle("sec", parent=ESTILO_BASE, fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=ABISSO)
ESTILO_SEC_REV = ParagraphStyle("sec_rev", parent=ESTILO_BASE, fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=BRANCO)
ESTILO_TEXTO = ParagraphStyle("txt", parent=ESTILO_BASE, fontSize=6.5, leading=8)
ESTILO_TEXTO_BOLD = ParagraphStyle("txt_bold", parent=ESTILO_TEXTO, fontName="Helvetica-Bold")
ESTILO_NUMERO = ParagraphStyle("num", parent=ESTILO_BASE, fontName="Helvetica", fontSize=6.5, leading=7.5, alignment=TA_CENTER)
ESTILO_NUM_DEST = ParagraphStyle("num_dest", parent=ESTILO_NUMERO, fontName="Helvetica-Bold", textColor=VERMELHO_SANGUE)
ESTILO_CARTAO_ROTULO = ParagraphStyle("cartao_rotulo", parent=ESTILO_BASE, fontSize=6, leading=7.5, alignment=TA_CENTER)
ESTILO_CARTAO_VALOR = ParagraphStyle("cartao_valor", parent=ESTILO_BASE, fontName="Helvetica-Bold", fontSize=14,
                                     leading=17, alignment=TA_CENTER)
ESTILO_CARTAO_NOTA = ParagraphStyle("cartao_nota", parent=ESTILO_BASE, fontSize=5.5, leading=7, alignment=TA_CENTER,
                                    textColor=TINTA_SUAVE)

# Altura das linhas em branco das tabelas de anotação.
ALTURA_LINHA_EM_BRANCO = 17


def _negrito(texto):
    """'**Psicanálise:** ...' (markdown do escudo) -> '<b>Psicanálise:</b> ...' (reportlab), com o resto escapado."""
    partes = escape(texto).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(partes))


def _cartao(rotulo, valor, nota, cor=None):
    """Célula dos cartões do topo: rótulo, valor grande e nota, cada um com o próprio espaçamento."""
    abre, fecha = (f"<font color='{cor}'>", "</font>") if cor else ("", "")
    return [Paragraph(rotulo, ESTILO_CARTAO_ROTULO),
            Paragraph(f"{abre}{valor}{fecha}", ESTILO_CARTAO_VALOR),
            Paragraph(f"{abre}{nota}{fecha}", ESTILO_CARTAO_NOTA)]


def _tabela_de_anotacao(cabecalho, larguras, linhas_em_branco, preenchidas=()):
    """Tabela com cabeçalho, linhas já preenchidas e linhas em branco (sem sublinhados que quebram)."""
    linhas = [[Paragraph(f"<b>{c}</b>", ESTILO_CAB) for c in cabecalho]]
    linhas += [list(linha) for linha in preenchidas]
    linhas += [[""] * len(cabecalho) for _ in range(max(0, linhas_em_branco - len(preenchidas)))]
    alturas = [None] * (1 + len(preenchidas)) + [ALTURA_LINHA_EM_BRANCO] * (len(linhas) - 1 - len(preenchidas))
    tabela = Table(linhas, colWidths=larguras, rowHeights=alturas)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CINZA_CLARO),
        ("BOX", (0, 0), (-1, -1), 0.6, ABISSO),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDA_SUAVE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tabela


def _sanidade_do_personagem(npc):
    san = npc.get("sanidade") or npc.get("ficha", {}).get("sanidade") or {}
    val = npc.get("validacao", {}).get("valores", {})
    vontade = val.get("defesas", {}).get("Vontade", 0)
    calculada = sanidade.sanidade_da_ficha(vontade, npc.get("ficha", {}))
    inicial = san.get("inicial", calculada["inicial"])
    atual = san.get("atual", inicial)
    maxima = san.get("maxima", calculada["maxima"])
    # A ruptura vale para a SAN do início do dia; na ficha impressa, a SAN atual é o ponto de partida.
    ruptura_diaria = sanidade.ponto_de_ruptura(atual)
    return {
        "limitada_pelo_mythos": inicial < sanidade.sanidade_inicial(vontade),
        "inicial": inicial,
        "atual": atual,
        "maxima": maxima,
        "vontade": vontade,
        "ruptura_diaria": ruptura_diaria,
    }


def gerar_pagina_sanidade(npc, largura=603, altura=783):
    """Gera os bytes de um PDF de página única com o registro de Sanidade do investigador."""
    san = _sanidade_do_personagem(npc)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=(largura, altura),
        leftMargin=20,
        rightMargin=20,
        topMargin=18,
        bottomMargin=18,
    )

    largura_util = largura - 40  # 563 pt
    elementos = []

    # 1. Cabeçalho
    nome = escape(npc.get("nome", "Investigador"))
    ocupacao = escape(npc.get("arquetipo", {}).get("nome", "Investigador"))
    jogador = escape(npc.get("jogador") or "") or "____________________"
    np = npc.get("np_pretendido", 3)

    elementos.append(Paragraph("REGISTRO DE SANIDADE & TRAUMA DO INVESTIGADOR", ESTILO_TITULO))
    elementos.append(Paragraph("Chamado de Cthulhu (anos 1920) · Regras de Horror Cósmico em Mutantes & Malfeitores 3ª Ed.", ESTILO_SUB))
    elementos.append(Spacer(1, 4))

    # Tabela com dados gerais do personagem
    dados_cab = [
        [
            Paragraph(f"<b>Investigador:</b> {nome}", ESTILO_CAB),
            Paragraph(f"<b>Ocupação:</b> {ocupacao}", ESTILO_CAB),
            Paragraph(f"<b>Jogador:</b> {jogador}", ESTILO_CAB),
            Paragraph(f"<b>Nível de Poder:</b> NP {np}", ESTILO_CAB),
        ]
    ]
    tab_cab = Table(dados_cab, colWidths=[largura_util * 0.32, largura_util * 0.28, largura_util * 0.23, largura_util * 0.17])
    tab_cab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CINZA_FUNDO),
        ("BOX", (0, 0), (-1, -1), 0.8, ABISSO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tab_cab)
    elementos.append(Spacer(1, 5))

    # 2. Cartões de Estatísticas de Sanidade
    rotulo_inicial = ("45 + 5×Von, limitada pelo Mythos" if san["limitada_pelo_mythos"]
                      else f"45 + 5×Von ({san['vontade']:+d})")
    vermelho = "#7a1c1c"
    dados_stats = [[
        _cartao("SANIDADE INICIAL", san["inicial"], rotulo_inicial),
        _cartao("SANIDADE ATUAL", san["atual"], "Rastrear na grade"),
        _cartao("SANIDADE MÁXIMA", san["maxima"], "99 − 5×Mythos"),
        _cartao("PONTO DE RUPTURA", f"−{san['ruptura_diaria']}", "1/5 da SAN do início do dia", vermelho),
        _cartao("CHOQUE TEMPORÁRIO", "≥ 5", "Perda num único teste", vermelho),
    ]]
    larg_col_stat = largura_util / 5
    tab_stats = Table(dados_stats, colWidths=[larg_col_stat] * 5)
    tab_stats.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CINZA_CLARO),
        ("BACKGROUND", (3, 0), (4, 0), colors.HexColor("#faeeee")),
        ("BOX", (0, 0), (-1, -1), 0.8, ABISSO),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDA_SUAVE),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(tab_stats)
    elementos.append(Spacer(1, 6))

    # 3. Bloco Principal em Duas Colunas
    # Coluna 1 (Esquerda, 275 pt): Contador 00-99 + Regras Rápidas de Sanidade
    # Coluna 2 (Direita, 275 pt): Tabela de Loucura (1d10) + Fobias & Manias + Tomos & Criaturas
    larg_col = (largura_util - 12) / 2  # 275.5 pt

    # --- Conteúdo da Coluna Esquerda ---
    bloco_esq = []

    # Título do Rastreador
    bloco_esq.append(Paragraph("<b>RASTREADOR DE PONTOS DE SANIDADE (00–99)</b>", ESTILO_SEC))
    bloco_esq.append(Paragraph("<font size=5.5 color='#4b5563'>Marque ou risque os pontos perdidos. Cuidado ao cruzar o 50 e o 00.</font>", ESTILO_TEXTO))
    bloco_esq.append(Spacer(1, 2))

    # Grade 10x10 do Rastreador de Sanidade
    grade_dados = []
    # 10 linhas de 10 números: de 0 a 99
    larg_celula = larg_col / 10
    for linha_idx in range(10):
        linha = []
        for col_idx in range(10):
            n = linha_idx * 10 + col_idx
            # Destaques visuais
            if n == 0:
                texto_cel = f"<font color='#7a1c1c'><b>[{n:02d}]</b></font>"
            elif n == 50:
                texto_cel = f"<font color='#1b4d3e'><b>{n:02d}</b></font>"
            elif n > san["maxima"]:
                texto_cel = f"<font color='#9ca3af'><s>{n:02d}</s></font>"
            elif n == san["atual"]:
                texto_cel = f"<b><u>{n:02d}</u></b>"
            else:
                texto_cel = f"{n:02d}"
            linha.append(Paragraph(texto_cel, ESTILO_NUMERO))
        grade_dados.append(linha)

    tab_grade = Table(grade_dados, colWidths=[larg_celula] * 10, rowHeights=[17] * 10)
    tab_grade.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, ABISSO),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDA_SUAVE),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#fed7d7")),  # 00 em vermelho claro
        ("BACKGROUND", (0, 5), (0, 5), colors.HexColor("#d1fae5")),  # 50 em verde claro
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    bloco_esq.append(tab_grade)
    bloco_esq.append(Spacer(1, 6))

    # Regras Rápidas de Sanidade
    bloco_esq.append(Paragraph("<b>REGRAS RÁPIDAS DE SANIDADE NA MESA</b>", ESTILO_SEC))
    estados = {estado: (gatilho, duracao) for estado, gatilho, duracao in sanidade.ESTADOS_DE_LOUCURA}
    recuperacao = "<br/>".join("&nbsp;&nbsp;– " + _negrito(item) for item in sanidade.RECUPERACAO_DE_SANIDADE)
    regras_texto = (
        "<b>• O Teste de Sanidade (d100):</b> Rola d100 contra a <i>SAN atual</i>.<br/>"
        "&nbsp;&nbsp;– <b>Sucesso (≤ SAN):</b> sofre a perda do sucesso (ex.: 0, 1 ou 1D6).<br/>"
        "&nbsp;&nbsp;– <b>Falha (> SAN):</b> sofre a perda da falha (ex.: 1D6, 1D10, 1D20).<br/>"
        "&nbsp;&nbsp;– <b>01</b> é sempre sucesso (com a perda normal do sucesso).<br/>"
        "&nbsp;&nbsp;– <b>100</b> é sempre desastre (perde o valor MÁXIMO da falha).<br/>"
        "&nbsp;&nbsp;– <b>SAN < 50:</b> resultados de <b>96 a 100</b> são desastres.<br/>"
        "<b>• Perda ≥ 5 num só teste:</b> Teste de Intelecto (d20 + INT contra CD 10).<br/>"
        f"&nbsp;&nbsp;– <i>Sucesso:</i> insanidade temporária ({escape(estados['Insanidade temporária'][1])})<br/>"
        f"&nbsp;&nbsp;– <i>Falha:</i> a mente reprime o choque; sem loucura imediata.<br/>"
        f"<b>• Acesso de loucura:</b> {escape(sanidade.DURACAO_DO_ACESSO)}.<br/>"
        "<b>• Insanidade indefinida (Ponto de Ruptura):</b><br/>"
        "&nbsp;&nbsp;Perder no mesmo dia 1/5 ou mais da SAN do início do dia: "
        f"{escape(estados['Insanidade indefinida'][1])}<br/>"
        f"<b>• SAN = 0:</b> {escape(estados['Insanidade permanente'][1])}<br/>"
        "<b>• Recuperação de Sanidade:</b><br/>"
        f"{recuperacao}"
    )
    quadro_regras = Table([[Paragraph(regras_texto, ESTILO_TEXTO)]], colWidths=[larg_col])
    quadro_regras.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CINZA_FUNDO),
        ("BOX", (0, 0), (-1, -1), 0.6, ABISSO),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    bloco_esq.append(quadro_regras)
    bloco_esq.append(Spacer(1, 6))

    # Registro diário: a insanidade indefinida compara a perda do dia com a SAN do início do dia.
    bloco_esq.append(Paragraph("<b>REGISTRO DIÁRIO DE SANIDADE</b>", ESTILO_SEC))
    bloco_esq.append(Paragraph("<font size=5.5 color='#4b5563'>Anote a SAN ao começar o dia; se a perda do dia chegar "
                               "ao ponto de ruptura (1/5, arredondado para cima), começa a insanidade indefinida.</font>",
                               ESTILO_TEXTO))
    bloco_esq.append(Spacer(1, 1))
    bloco_esq.append(_tabela_de_anotacao(["Dia / Data", "SAN no início", "Ruptura (1/5)", "Perdido no dia"],
                                         [larg_col * 0.31, larg_col * 0.23, larg_col * 0.23, larg_col * 0.23], 5))

    # --- Conteúdo da Coluna Direita ---
    bloco_dir = []

    # Tabela de Acessos de Loucura (d10)
    bloco_dir.append(Paragraph("<b>TABELA DE ACESSOS DE LOUCURA (1d10)</b>", ESTILO_SEC))
    bloco_dir.append(Paragraph("<font size=5.5 color='#4b5563'>Role 1d10 no início de cada insanidade (temporária ou indefinida).</font>", ESTILO_TEXTO))
    bloco_dir.append(Spacer(1, 2))

    loucuras = [(str(d), f"<b>{escape(nome)}:</b> {escape(efeito)}") for d, nome, efeito in sanidade.ACESSOS_DE_LOUCURA]
    dados_loucuras = [[Paragraph(f"<b>{d}</b>", ParagraphStyle("d", parent=ESTILO_TEXTO_BOLD, alignment=TA_CENTER)),
                       Paragraph(desc, ESTILO_TEXTO)] for d, desc in loucuras]
    tab_loucuras = Table(dados_loucuras, colWidths=[larg_col * 0.10, larg_col * 0.90])
    tab_loucuras.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, ABISSO),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDA_SUAVE),
        ("BACKGROUND", (0, 0), (0, -1), CINZA_CLARO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    bloco_dir.append(tab_loucuras)
    bloco_dir.append(Spacer(1, 6))

    # Registro de Fobias e Manias
    bloco_dir.append(Paragraph("<b>REGISTRO DE FOBIAS, MANIAS & CICATRIZES MENTAIS</b>", ESTILO_SEC))
    bloco_dir.append(Spacer(1, 1))

    # Coleta complicações mentais que o personagem já possui
    comp_mentais = [
        (c['nome'], escape(c.get('detalhe', '')))
        for c in npc.get("complicacoes", [])
        if c.get("nome") in ("Fobia", "Mania", "Pesadelos", "Paranoia", "Obsessão", "Trauma da Grande Guerra")
    ]
    preenchidas = [(Paragraph(f"<b>{escape(nome)}</b>", ESTILO_TEXTO), Paragraph(detalhe, ESTILO_TEXTO))
                   for nome, detalhe in comp_mentais]
    tab_fobias = _tabela_de_anotacao(["Tipo / Nome", "Gatilho Mental & Efeitos"], [larg_col * 0.35, larg_col * 0.65],
                                     max(5, len(preenchidas)), preenchidas)
    bloco_dir.append(tab_fobias)
    bloco_dir.append(Spacer(1, 6))

    # Diário de Criaturas do Mythos, Tomos e Perda Máxima
    bloco_dir.append(Paragraph("<b>ENCONTROS DO MYTHOS, TOMOS & PERDA MÁXIMA</b>", ESTILO_SEC))
    bloco_dir.append(Paragraph("<font size=5.5 color='#4b5563'>Some as perdas por tipo de criatura: quando a soma chega à perda máxima dela, você se acostuma.</font>", ESTILO_TEXTO))
    bloco_dir.append(Spacer(1, 1))

    tab_mythos = _tabela_de_anotacao(["Criatura / Tomo Proibido", "SAN perdida (soma)", "Perda Máx.", "Feitiço / Efeito"],
                                     [larg_col * 0.40, larg_col * 0.18, larg_col * 0.16, larg_col * 0.26], 8)
    bloco_dir.append(tab_mythos)

    # 4. Tabela de 2 Colunas para o Bloco Principal
    tab_duas_colunas = Table([[bloco_esq, bloco_dir]], colWidths=[larg_col + 12, larg_col])
    tab_duas_colunas.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 12),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tab_duas_colunas)

    doc.build(elementos)
    return buf.getvalue()
