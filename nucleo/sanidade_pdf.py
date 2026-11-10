"""Gera a página extra do PDF (Página 3) para o gênero Chamado de Cthulhu:
Registro de Sanidade d100, contador 00-99, regras de choque mental, acessos de loucura e fobias.
"""

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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


def _sanidade_do_personagem(npc):
    san = npc.get("sanidade") or npc.get("ficha", {}).get("sanidade") or {}
    val = npc.get("validacao", {}).get("valores", {})
    vontade = val.get("defesas", {}).get("Vontade", 0)
    inicial = san.get("inicial", min(99, max(0, 45 + 5 * vontade)))
    atual = san.get("atual", inicial)
    maxima = san.get("maxima", 99)
    ruptura_diaria = max(1, round(inicial * 0.2))
    return {
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
    jogador = escape(npc.get("jogador", "Jogador") or "Jogador")
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
    tab_cab = Table(dados_cab, colWidths=[largura_util * 0.35, largura_util * 0.30, largura_util * 0.22, largura_util * 0.13])
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
    dados_stats = [
        [
            Paragraph("<font size=6>SANIDADE INICIAL</font><br/>"
                      f"<font size=12><b>{san['inicial']}</b></font><br/>"
                      f"<font size=5.5 color='#4b5563'>45 + 5×Von ({san['vontade']:+d})</font>", ParagraphStyle("c1", parent=ESTILO_BASE, alignment=TA_CENTER)),
            Paragraph("<font size=6>SANIDADE ATUAL</font><br/>"
                      f"<font size=12><b>{san['atual']}</b></font><br/>"
                      "<font size=5.5 color='#4b5563'>Rastrear na grade</font>", ParagraphStyle("c2", parent=ESTILO_BASE, alignment=TA_CENTER)),
            Paragraph("<font size=6>SANIDADE MÁXIMA</font><br/>"
                      f"<font size=12><b>{san['maxima']}</b></font><br/>"
                      "<font size=5.5 color='#4b5563'>99 - 5×Mythos</font>", ParagraphStyle("c3", parent=ESTILO_BASE, alignment=TA_CENTER)),
            Paragraph("<font size=6>PONTO DE RUPTURA</font><br/>"
                      f"<font size=12 color='#7a1c1c'><b>-{san['ruptura_diaria']}</b></font><br/>"
                      "<font size=5.5 color='#7a1c1c'>Perda diária (20%)</font>", ParagraphStyle("c4", parent=ESTILO_BASE, alignment=TA_CENTER)),
            Paragraph("<font size=6>CHOQUE TEMPORÁRIO</font><br/>"
                      "<font size=12 color='#7a1c1c'><b>≥ 5</b></font><br/>"
                      "<font size=5.5 color='#7a1c1c'>Em um único teste</font>", ParagraphStyle("c5", parent=ESTILO_BASE, alignment=TA_CENTER)),
        ]
    ]
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

    tab_grade = Table(grade_dados, colWidths=[larg_celula] * 10, rowHeights=[14.5] * 10)
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
    regras_texto = (
        "<b>• O Teste de Sanidade (d100):</b> Rola d100 contra a <i>Sanidade Atual</i>.<br/>"
        "&nbsp;&nbsp;– <b>Sucesso (≤ SAN):</b> Perde o mínimo (ex: 0, 1 ou 1D3).<br/>"
        "&nbsp;&nbsp;– <b>Fracasso (> SAN):</b> Perde o valor total (ex: 1D6, 1D10, 1D20).<br/>"
        "&nbsp;&nbsp;– <b>01</b> é sempre Sucesso Crítico (perde 0 ou o menor dano).<br/>"
        "&nbsp;&nbsp;– <b>100</b> é sempre Desastre (perde o valor MÁXIMO da rolagem).<br/>"
        "&nbsp;&nbsp;– <b>SAN < 50:</b> Resultados de <b>96 a 100</b> tornam-se Desastres.<br/>"
        "<b>• Insanidade Temporária (Perda ≥ 5 em 1 teste):</b><br/>"
        "&nbsp;&nbsp;Faça um <b>Teste de Intelecto do M&M (d20 + INT vs CD 10)</b>:<br/>"
        "&nbsp;&nbsp;– <i>Sucesso:</i> A mente compreende o horror cósmico e entra em <b>Acesso de Loucura</b> "
        "(1D10 rodadas em combate ou 1D10 horas em narrativa).<br/>"
        "&nbsp;&nbsp;– <i>Falha:</i> A mente reprime o choque; sem loucura imediata.<br/>"
        "<b>• Insanidade Indefinida (Perda diária ≥ 20%):</b><br/>"
        "&nbsp;&nbsp;Se o investigador perder 20% da Sanidade inicial do dia (Ponto de Ruptura), "
        "entra em colapso mental por 1D6 meses e ganha nova <b>Fobia</b> ou <b>Mania</b>.<br/>"
        "<b>• Insanidade Permanente (SAN = 0):</b><br/>"
        "&nbsp;&nbsp;A mente foi consumida pelos Deuses Exteriores. O personagem torna-se um NPC sob controle do Mestre.<br/>"
        "<b>• Recuperação de Sanidade:</b><br/>"
        "&nbsp;&nbsp;– <i>Tratamento Psiquiátrico:</i> Teste semanal de Tratamento CD 15 recupera 1D3 SAN.<br/>"
        "&nbsp;&nbsp;– <i>Vitória sobre o Culto:</i> Destruir um plano maligno recupera 1D6 a 1D10 SAN."
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

    # --- Conteúdo da Coluna Direita ---
    bloco_dir = []

    # Tabela de Acessos de Loucura (d10)
    bloco_dir.append(Paragraph("<b>TABELA DE ACESSOS DE LOUCURA (1d10)</b>", ESTILO_SEC))
    bloco_dir.append(Paragraph("<font size=5.5 color='#4b5563'>Role 1d10 durante episódios de insanidade temporária.</font>", ESTILO_TEXTO))
    bloco_dir.append(Spacer(1, 2))

    loucuras = [
        ("1", "<b>Amnésia:</b> Não se lembra de quem é nem de como chegou aqui."),
        ("2", "<b>Catatonia:</b> Desmaia ou fica imóvel e mudo em estado de choque."),
        ("3", "<b>Pânico & Fuga:</b> Foge aos berros para a direção oposta ao horror."),
        ("4", "<b>Histeria:</b> Risos compulsivos, gritos ou choro incontrolável."),
        ("5", "<b>Alucinações:</b> Vê geometrias não-euclidianas e sombras atacando."),
        ("6", "<b>Paranoia Aguda:</b> Acredita que seus aliados são cultistas traidores."),
        ("7", "<b>Fúria Cega:</b> Ataca violentamente o ser mais próximo (amigo ou inimigo)."),
        ("8", "<b>Ecolalia / Tiques:</b> Balbucia frases profanas repetidamente sem parar."),
        ("9", "<b>Fobia Súbita:</b> Pavor paralisante de algo no ambiente (água, sangue, etc.)."),
        ("10", "<b>Fascínio Mórbido:</b> Aproxima-se da abominação em reverência silenciosa."),
    ]
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
    linhas_fobias = []
    # Cabeçalho da tabela de fobias
    linhas_fobias.append([Paragraph("<b>Tipo / Nome</b>", ESTILO_CAB), Paragraph("<b>Gatilho Mental & Efeitos</b>", ESTILO_CAB)])
    # Linhas preenchidas ou vazias
    for i in range(4):
        if i < len(comp_mentais):
            nome_comp, detalhe_comp = comp_mentais[i]
            linhas_fobias.append([Paragraph(f"<b>{nome_comp}</b>", ESTILO_TEXTO), Paragraph(detalhe_comp, ESTILO_TEXTO)])
        else:
            linhas_fobias.append([Paragraph("__________________", ESTILO_TEXTO), Paragraph("____________________________________", ESTILO_TEXTO)])

    tab_fobias = Table(linhas_fobias, colWidths=[larg_col * 0.35, larg_col * 0.65])
    tab_fobias.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CINZA_CLARO),
        ("BOX", (0, 0), (-1, -1), 0.6, ABISSO),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDA_SUAVE),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    bloco_dir.append(tab_fobias)
    bloco_dir.append(Spacer(1, 6))

    # Diário de Criaturas do Mythos, Tomos e Perda Máxima
    bloco_dir.append(Paragraph("<b>ENCONTROS DO MYTHOS, TOMOS & PERDA MÁXIMA</b>", ESTILO_SEC))
    bloco_dir.append(Paragraph("<font size=5.5 color='#4b5563'>Depois de perder o dano máximo de uma criatura, você se acostuma a ela.</font>", ESTILO_TEXTO))
    bloco_dir.append(Spacer(1, 1))

    linhas_mythos = [
        [
            Paragraph("<b>Criatura / Tomo Proibido</b>", ESTILO_CAB),
            Paragraph("<b>SAN Perdida</b>", ESTILO_CAB),
            Paragraph("<b>Perda Máx.</b>", ESTILO_CAB),
            Paragraph("<b>Feitiço / Efeito</b>", ESTILO_CAB),
        ]
    ]
    for _ in range(4):
        linhas_mythos.append([
            Paragraph("_____________________________", ESTILO_TEXTO),
            Paragraph("[ &nbsp;&nbsp;&nbsp; ]", ParagraphStyle("c", parent=ESTILO_TEXTO, alignment=TA_CENTER)),
            Paragraph("[ &nbsp;&nbsp;&nbsp; ]", ParagraphStyle("c", parent=ESTILO_TEXTO, alignment=TA_CENTER)),
            Paragraph("______________________", ESTILO_TEXTO),
        ])

    tab_mythos = Table(linhas_mythos, colWidths=[larg_col * 0.42, larg_col * 0.18, larg_col * 0.18, larg_col * 0.22])
    tab_mythos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CINZA_CLARO),
        ("BOX", (0, 0), (-1, -1), 0.6, ABISSO),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDA_SUAVE),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    bloco_dir.append(tab_mythos)

    # 4. Tabela de 2 Colunas para o Bloco Principal
    tab_duas_colunas = Table([[bloco_esq, bloco_dir]], colWidths=[larg_col, larg_col])
    tab_duas_colunas.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tab_duas_colunas)

    doc.build(elementos)
    return buf.getvalue()
