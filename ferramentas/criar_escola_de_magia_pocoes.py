"""Gera a planilha e os dados de poções, elixires, plantas mágicas (Herbologia),
ingredientes de criaturas (Animais Fantásticos e Onde Habitam) e preços de
Hogsmeade / Beco Diagonal para o gênero Escola de Magia (M&M 3e).

Gera:
- referencias/harry potter/pocoes.xlsx
- dados/generos/escola_de_magia/pocoes.xlsx
- dados/generos/escola_de_magia/alquimia.json

Uso: python ferramentas/criar_escola_de_magia_pocoes.py
"""

import json
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent

ROXO_ESCURO = PatternFill(start_color="3B1E54", end_color="3B1E54", fill_type="solid")
ROXO_MEDIO = PatternFill(start_color="5C3380", end_color="5C3380", fill_type="solid")
ZEBRA = PatternFill(start_color="F8F5FB", end_color="F8F5FB", fill_type="solid")
BRANCO = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

FONTE_TITULO = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
FONTE_CABECALHO = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
FONTE_CORPO = Font(name="Calibri", size=10)
FONTE_CORPO_BOLD = Font(name="Calibri", size=10, bold=True)

BORDA_FINA = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)

ALINHA_ESQ = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALINHA_CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALINHA_DIR = Alignment(horizontal="right", vertical="center")


def peso_em_texto(kg):
    if kg < 1:
        return f"{int(round(kg * 1000))} g"
    return f"{str(kg).replace('.', ',')} kg"


REGRAS = [
    ("1. Preparo de Poções no Caldeirão",
     "Preparar uma poção exige um Caldeirão (padrão: estanho nº 2), um Estojo de Ingredientes de Poções (ou o ingrediente "
     "específico da receita) e um teste de Especialidade: Poções (Intelecto) contra a CD da receita.\n"
     "• Sem Caldeirão: impossível preparar.\n"
     "• Ingredientes ou utensílios improvisados: penalidade de –2 a –5 no teste.\n"
     "• Teste de Equipe: até dois colegas podem ajudar (CD 10 em Especialidade: Poções ou Herbologia), concedendo +2 (ou +5 com 3+ graus)."),
    ("2. Graus de Sucesso e Acidentes Alquímicos",
     "• Sucesso (1 ou 2 graus): produz 1 frasco/dose perfeita da poção.\n"
     "• Sucesso Brilhante (3+ graus): rende 2 doses com os mesmos ingredientes ou aumenta a CD de resistência da poção em +1.\n"
     "• Falha (1 grau): a poção desanda (fica rala ou empelotada) e os ingredientes são perdidos.\n"
     "• Falha Grave (2 graus): fumaça fétida ou espirro cáustico; o aluno perde –5 pontos da Casa na aula.\n"
     "• Falha Crítica (3+ graus ou 1 natural): o caldeirão derrete ou explode (Dano 2 em área próxima ou efeito colateral "
     "cômico como furúnculos/orelhas de gato, exigindo visita à Ala Hospitalar e detenção)."),
    ("3. Herbologia e Colheita de Criaturas Mágicas",
     "• Estufas de Herbologia: colher ou replantar espécies mágicas pede Especialidade: Herbologia (CD 10 a 18) e Luvas de Couro de Dragão "
     "(sem luvas ou abafadores de ouvido no caso de Mandrágoras, o aluno sofre o efeito defensivo da planta).\n"
     "• Ingredientes de Criaturas (Animais Fantásticos): pelos de unicórnio caídos, penas e cascas de ovos podem ser recolhidos "
     "com Especialidade: Criaturas Mágicas (CD 12 a 20). Já veneno de Acromântula ou chifre de Bicórnio exigem abater ou "
     "acalmar a fera."),
    ("4. Uso em Cena e Poções Controladas",
     "• Sacar um frasco do bolso/cinto é 1 ação de movimento; beber ou administrar em um aliado adjacente é 1 ação padrão.\n"
     "• Poções Restritas (Polissuco, Veritaserum, Amortentia): seus ingredientes ficam trancados no estoque privado do "
     "professor de Poções e seu uso sem autorização do Ministério da Magia ou da direção é infração gravíssima."),
]

# Todas as poções abaixo batem exatamente (id, nome, preco, peso, comercio="Boticário") com equipment.json
POCOES = [
    {
        "id": "pocao_furunculos",
        "nome": "Poção para Curar Furúnculos",
        "ano": "1º ano",
        "ingrediente": "Urtigas secas, presas de cobra moídas e lesmas chifrudas",
        "preparo": "Caldeirão de estanho (tirar do fogo antes de pôr os espinhos de porco-espinho!)",
        "cd": 10,
        "tempo": "30 min",
        "duracao": "Instantâneo",
        "efeito": "Cura furúnculos, pústulas de Bubotúbera e urticárias mágicas leves (remove 1 condição de Aflição cutânea de 1º ou 2º grau).",
        "preco": "4 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_esquecimento",
        "nome": "Poção do Esquecimento",
        "ano": "1º ano",
        "ingrediente": "Água do Rio Lete, ramos de valeriana e bagas de visco",
        "preparo": "2 gotas de água do Lete aquecidas por 20 segundos + 4 bagas de visco",
        "cd": 12,
        "tempo": "45 min",
        "duracao": "1 cena",
        "efeito": "Aflição 2 (resistida por Vontade CD 12; Tonto / Compelido a esquecer o que estava fazendo nos últimos minutos).",
        "preco": "6 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_cura",
        "nome": "Poção Wiggenweld (cura)",
        "ano": "1º ano",
        "ingrediente": "Casca de Wiggentree, ditamno, muco de verme-cego e crina de unicórnio",
        "preparo": "Mexer até o líquido mudar do vermelho ao verde-esmeralda",
        "cd": 12,
        "tempo": "45 min",
        "duracao": "Instantâneo",
        "efeito": "Restaura o fôlego e remove 1 condição de dano ou fadiga; também desperta imediatamente alguém da Poção do Morto-Vivo.",
        "preco": "8 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_estimulante",
        "nome": "Poção Estimulante (Pepperup)",
        "ano": "2º ano",
        "ingrediente": "Raiz de mandrágora seca, pimenta mágica e chifre de bicórnio",
        "preparo": "Fervura rápida em caldeirão aquecido",
        "cd": 13,
        "tempo": "1 hora",
        "duracao": "4 horas",
        "efeito": "Remove imediatamente Fatigado, hipotermia e resfriados; efeito colateral inofensivo: sai fumaça pelas orelhas por 3 horas.",
        "preco": "6 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_inchaco",
        "nome": "Solução de Inchaço",
        "ano": "2º ano",
        "ingrediente": "Olhos de baiacu, urtigas secas e baço de morcego",
        "preparo": "Cozimento médio até ficar amarela-viva",
        "cd": 13,
        "tempo": "1 hora",
        "duracao": "1 hora (ou até aplicar Solução Encolhedora)",
        "efeito": "Ao contato, faz a parte atingida inflar ao triplo do tamanho (Aflição 3 resistida por Fortitude CD 13: Impedido / Desabilitado).",
        "preco": "7 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_encolhedora",
        "nome": "Solução Encolhedora",
        "ano": "3º ano",
        "ingrediente": "Raízes de margarida picadas, figos secos descascados, sanguessuga e baço de rato",
        "preparo": "Deve ficar verde-ácido brilhante (se ficar laranja, é veneno!)",
        "cd": 15,
        "tempo": "1h30",
        "duracao": "1 hora",
        "efeito": "Anula instantaneamente a Solução de Inchaço; também reduz pequenos seres ou objetos (Encolhimento 2 temporário).",
        "preco": "12 G",
        "peso": 0.2,
    },
    {
        "id": "antidoto_comum",
        "nome": "Antídoto para venenos comuns",
        "ano": "3º ano",
        "ingrediente": "Bezoar triturado, bagas de visco e chifre de unicórnio",
        "preparo": "Infusão fria seguida de fervura branda",
        "cd": 14,
        "tempo": "1 hora",
        "duracao": "Instantâneo",
        "efeito": "Concede novo teste de Fortitude imediato com +5 contra venenos comuns, picadas de criaturas até XXX e poções nocivas simples.",
        "preco": "10 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_esquelece",
        "nome": "Esquelece (Skele-Gro)",
        "ano": "4º ano",
        "ingrediente": "Escaravelhos chineses, peixe-balão e artemísia",
        "preparo": "Destilação lenta e fumegante de gosto horrível",
        "cd": 16,
        "tempo": "3 horas",
        "duracao": "8 horas (uma noite de sono)",
        "efeito": "Regenera ossos quebrados ou inteiramente desaparecidos após 8 horas de repouso doloroso na Ala Hospitalar.",
        "preco": "18 G",
        "peso": 0.3,
    },
    {
        "id": "filtro_paz",
        "nome": "Filtro da Paz",
        "ano": "5º ano (N.O.M.)",
        "ingrediente": "Pedra da lua em pó, xarope de eléboro e espinhos de porco-espinho",
        "preparo": "Exige precisão absoluta na temperatura e no número de mexidas (solta vapor prateado)",
        "cd": 18,
        "tempo": "1h30",
        "duracao": "1 cena",
        "efeito": "Acalma agitação e medo: remove Abalado/Assustado e concede +4 em salvamentos de Vontade contra medo e intimidação.",
        "preco": "15 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_morto_vivo",
        "nome": "Poção do Morto-Vivo (sonífera)",
        "ano": "6º ano (N.I.E.M.)",
        "ingrediente": "Raiz de asfódelo em pó em infusão de losna, raiz de valeriana e vagem soporífera",
        "preparo": "Esmagar a vagem com a lateral da lâmina de prata; mexer 7 vezes anti-horário e 1 horário",
        "cd": 20,
        "tempo": "2 horas",
        "duracao": "Até receber Poção Wiggenweld",
        "efeito": "Aflição Cumulativa 6 (resistida por Fortitude CD 16; Tonto / Exausto / Adormecido profundo indistinguível do transe).",
        "preco": "25 G",
        "peso": 0.2,
    },
    {
        "id": "pocao_polissuco",
        "nome": "Poção Polissuco (dose)",
        "ano": "Avançada (Restrita)",
        "ingrediente": "Hemeróbios cozidos por 21 dias, sanguessugas, descurainia colhida na lua cheia, chifre de bicórnio, pele de araramboia e 1 fio de cabelo do alvo",
        "preparo": "Cozimento complexo de 1 mês; muda de cor e sabor conforme o caráter da pessoa-alvo",
        "cd": 22,
        "tempo": "30 dias",
        "duracao": "1 hora por dose",
        "efeito": "Morfo 3 (assume a aparência física e voz exatas de outro humano por 1 hora). Se usar pelo de animal, sofre transformação parcial!",
        "preco": "60 G",
        "peso": 0.2,
    },
    {
        "id": "veritaserum",
        "nome": "Veritaserum (Soro da Verdade)",
        "ano": "Avançada (Controlada pelo Ministério)",
        "ingrediente": "Penas de Dedo-Duro (Jobberknoll), infusão de Sophora e água lunar maturada por 1 ciclo",
        "preparo": "Líquido incolor e inodoro como água pura; leva um ciclo lunar completo",
        "cd": 25,
        "tempo": "28 dias",
        "duracao": "1 cena",
        "efeito": "Aflição Cumulativa 8 (resistida por Vontade CD 18; Tonto / Compelido / Controlado a responder com a verdade absoluta).",
        "preco": "90 G",
        "peso": 0.1,
    },
    {
        "id": "felix_felicis",
        "nome": "Felix Felicis (1 gole)",
        "ano": "Avançada (N.I.E.M. / Raríssima)",
        "ingrediente": "Ovo de Cinzal, tentáculo de Murtisco, tintura de tomilho e casca de ovo de Occami",
        "preparo": "Líquido dourado que salta como peixinhos no caldeirão; desastrosa se errada",
        "cd": 28,
        "tempo": "6 meses",
        "duracao": "1 missão / meio dia",
        "efeito": "Sorte Líquida: concede imediatamente 1 Ponto Heroico extra e a vantagem Sorte 2 durante toda a cena ou missão.",
        "preco": "150 G",
        "peso": 0.1,
    },
]

# Todos os ingredientes abaixo batem com equipment.json (id, nome, preco, peso, comercio="Boticário")
INGREDIENTES = [
    {
        "id": "ing_mandragora",
        "nome": "Folha de Mandrágora",
        "origem": "Herbologia (Estufa 3)",
        "classificacao": "Planta Mágica Perigosa",
        "colheita": "Especialidade: Herbologia CD 14 (exige abafadores de ouvido; choro causa Aflição Auditiva em Área 4)",
        "usos": "Tônico Restaurador de Mandrágora (desfaz petrificação) e Poção Estimulante.",
        "preco": "5 G",
        "peso": 0.1,
    },
    {
        "id": "ing_guelricho",
        "nome": "Guelricho (Gillyweed — 1 porção)",
        "origem": "Herbologia (Mediterrâneo)",
        "classificacao": "Planta Mágica Aquática",
        "colheita": "Especialidade: Herbologia CD 14 (ou estoque do professor de Poções)",
        "usos": "Consumido puro: cria guelras e membranas entre os dedos por 1 hora (Imunidade a Afogamento + Natação 2).",
        "preco": "12 G",
        "peso": 0.1,
    },
    {
        "id": "ing_bezoar",
        "nome": "Bezoar (pedra estomacal de cabra)",
        "origem": "Boticário / Armário de Poções",
        "classificacao": "Reagente Mineral/Animal",
        "colheita": "Encontrado no estômago de cabras ou no armário de suprimentos (Investigação CD 12)",
        "usos": "Engolido inteiro: neutraliza quase todos os venenos mágicos na hora (Nulificar Veneno 6). Base do Antídoto Comum.",
        "preco": "20 G",
        "peso": 0.1,
    },
    {
        "id": "ing_bubotubera",
        "nome": "Pus de Bubotúbera (frasco)",
        "origem": "Herbologia (Estufa 2)",
        "classificacao": "Planta Mágica",
        "colheita": "Especialidade: Herbologia CD 10 com Luvas de Couro de Dragão (espremer as protuberâncias)",
        "usos": "Diluído: poções dermatológicas e curativas. Puro: causa furúnculos amarelos ao contato (Aflição 2).",
        "preco": "4 G",
        "peso": 0.2,
    },
    {
        "id": "ing_aconito",
        "nome": "Acônito (Licoctono / Lupária)",
        "origem": "Herbologia / Floresta Proibida",
        "classificacao": "Planta Mágica Tóxica",
        "colheita": "Especialidade: Herbologia CD 15 (manusear apenas com luvas)",
        "usos": "Ingrediente essencial da Poção Mata-Cão (Wolfsbane) e da Poção de Despertar.",
        "preco": "6 G",
        "peso": 0.1,
    },
    {
        "id": "ing_boomslang",
        "nome": "Pele de Araramboia picada",
        "origem": "Animais Fantásticos (África)",
        "classificacao": "Criatura Mágica (XXX — Restrito)",
        "colheita": "Boticário especializado ou estoque privado do professor de Poções",
        "usos": "Ingrediente indispensável da Poção Polissuco.",
        "preco": "18 G",
        "peso": 0.1,
    },
    {
        "id": "ing_bicornio",
        "nome": "Chifre de Bicórnio em pó",
        "origem": "Animais Fantásticos",
        "classificacao": "Criatura Mágica (XXX)",
        "colheita": "Troca anual de chifre da criatura; vendido em pó no Boticário",
        "usos": "Poção Polissuco e Poção Estimulante.",
        "preco": "15 G",
        "peso": 0.1,
    },
    {
        "id": "ing_acromantula",
        "nome": "Veneno de Acromântula (frasco)",
        "origem": "Animais Fantásticos (Floresta Proibida)",
        "classificacao": "Criatura Mágica (XXXXX)",
        "colheita": "Especialidade: Criaturas Mágicas CD 18 logo após a morte da Acromântula (seca rápido)",
        "usos": "Valiosíssimo (50 G a dose; 100 G o meio litro); usado em elixires raros e antídotos de alto nível.",
        "preco": "50 G",
        "peso": 0.1,
    },
    {
        "id": "ing_cinzal",
        "nome": "Ovos de Cinzal congelados",
        "origem": "Animais Fantásticos",
        "classificacao": "Criatura Mágica (XXX)",
        "colheita": "Recolher com feitiço Congelante (Glacius) antes que incendeiem a sala (CD 16)",
        "usos": "Ingrediente da Felix Felicis, Amortentia e elixires contra febres agudas.",
        "preco": "25 G",
        "peso": 0.2,
    },
    {
        "id": "ing_unicornio",
        "nome": "Crina de Unicórnio (fio)",
        "origem": "Animais Fantásticos (Floresta Proibida)",
        "classificacao": "Criatura Mágica (XXXX)",
        "colheita": "Fios prateados presos em galhos da floresta (Percepção ou Criaturas Mágicas CD 14)",
        "usos": "Núcleo de varinhas, bandagens mágicas resistentes e Poção Wiggenweld.",
        "preco": "10 G",
        "peso": 0.05,
    },
]

HOGSMEADE_SERVICOS = [
    {
        "categoria": "Bebidas e Doces",
        "item": "Cerveja Amanteigada (caneca ou garrafa)",
        "local": "Três Vassouras / Cabeça de Javali",
        "preco_moedas": "2 Sicles",
        "valor_g": "0,2 G",
        "detalhes": "Bebida quente e espumante; concede +1 de circunstância em Fortitude contra o frio por 1 hora.",
    },
    {
        "categoria": "Bebidas e Doces",
        "item": "Sapo de Chocolate (com figurinha de bruxo famoso)",
        "local": "Dedosdemel / Expresso de Hogwarts",
        "preco_moedas": "3 Sicles",
        "valor_g": "0,2 G",
        "detalhes": "As figurinhas colecionáveis às vezes trazem dicas históricas úteis (+1 em História da Magia sobre o bruxo).",
    },
    {
        "categoria": "Bebidas e Doces",
        "item": "Feijõezinhos de Todos os Sabores (caixa)",
        "local": "Dedosdemel / Expresso de Hogwarts",
        "preco_moedas": "2 Sicles",
        "valor_g": "0,15 G",
        "detalhes": "De morango e hortelã até pimenta, fígado e cera de ouvido.",
    },
    {
        "categoria": "Bebidas e Doces",
        "item": "Bolo de Caldeirão / Tortinha de Abóbora",
        "local": "Carrinho do Expresso de Hogwarts",
        "preco_moedas": "2 Sicles",
        "valor_g": "0,15 G",
        "detalhes": "Lanche favorito durante a viagem de trem para a escola.",
    },
    {
        "categoria": "Hospedagem",
        "item": "Quarto com café da manhã no Caldeirão Furado",
        "local": "Londres (entrada do Beco Diagonal)",
        "preco_moedas": "1 Galeão / noite",
        "valor_g": "1 G",
        "detalhes": "Estalagem clássica de Tom; ponto seguro de descanso entre viagens.",
    },
    {
        "categoria": "Transporte Mágico",
        "item": "Passagem no Nôitibus Andante",
        "local": "Qualquer meio-fio (erguendo a varinha)",
        "preco_moedas": "11 Sicles (13 com chocolate quente)",
        "valor_g": "0,7 G",
        "detalhes": "Ônibus roxo de três andares para bruxos desamparados; chega a qualquer destino terrestre em minutos.",
    },
    {
        "categoria": "Transporte Mágico",
        "item": "Punhado de Pó de Flu",
        "local": "Rede de Flu / Beco Diagonal",
        "preco_moedas": "2 Sicles a colherada (ou 1 G o pote)",
        "valor_g": "1 G",
        "detalhes": "Teleporte instantâneo entre lareiras conectadas. Pronunciar mal o nome leva à lareira errada!",
    },
    {
        "categoria": "Comunicação",
        "item": "Aluguel de Coruja-Correio / Envio expresso",
        "local": "Correio-Coruja de Hogsmeade",
        "preco_moedas": "1 a 5 Nuques (local) / 2 Sicles (longa distância)",
        "valor_g": "0,1 G",
        "detalhes": "Gratuito se o estudante já possuir sua própria Coruja de estimação.",
    },
]


def _estilizar_aba(ws, titulo, cabecalho, linhas, col_negrito=1, altura_linha=38):
    ws.views.sheetView[0].showGridLines = True
    ultima_letra = get_column_letter(len(cabecalho))
    ws.merge_cells(f"A1:{ultima_letra}1")
    ws["A1"] = titulo
    ws["A1"].font = FONTE_TITULO
    ws["A1"].fill = ROXO_ESCURO
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    for col_idx, (nome_col, larg, _) in enumerate(cabecalho, start=1):
        cell = ws.cell(row=2, column=col_idx, value=nome_col)
        cell.font = FONTE_CABECALHO
        cell.fill = ROXO_MEDIO
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDA_FINA
        ws.column_dimensions[get_column_letter(col_idx)].width = larg
    ws.row_dimensions[2].height = 28

    for r_idx, linha in enumerate(linhas, start=3):
        fill = ZEBRA if r_idx % 2 == 0 else BRANCO
        ws.row_dimensions[r_idx].height = altura_linha
        for col_idx, val in enumerate(linha, start=1):
            cell = ws.cell(row=r_idx, column=col_idx, value=val)
            cell.font = FONTE_CORPO_BOLD if col_idx == col_negrito else FONTE_CORPO
            cell.fill = fill
            cell.border = BORDA_FINA
            cell.alignment = cabecalho[col_idx - 1][2]


def criar_planilha():
    wb = openpyxl.Workbook()

    # Folha 1: Regras e Preparo
    ws1 = wb.active
    ws1.title = "Regras e Preparo"
    _estilizar_aba(
        ws1,
        "REGRAS DE POÇÕES, CALDEIRÕES E HERBOLOGIA — ESCOLA DE MAGIA (M&M 3e)",
        [("Tópico", 34, ALINHA_ESQ), ("Regras Mecânicas e Uso em Jogo", 95, ALINHA_ESQ)],
        [[t, d] for t, d in REGRAS],
        col_negrito=1,
        altura_linha=72,
    )

    # Folha 2: Poções e Elixires
    ws2 = wb.create_sheet(title="Poções e Elixires")
    _estilizar_aba(
        ws2,
        "CATÁLOGO DE POÇÕES E ELIXIRES ESCOLARES E AVANÇADOS (1º AO 7º ANO)",
        [
            ("Poção / Elixir", 28, ALINHA_ESQ),
            ("Ano / Nível", 18, ALINHA_CENTRO),
            ("Ingredientes Principais", 34, ALINHA_ESQ),
            ("Preparo no Caldeirão", 32, ALINHA_ESQ),
            ("CD Poções", 11, ALINHA_CENTRO),
            ("Tempo", 12, ALINHA_CENTRO),
            ("Duração", 16, ALINHA_CENTRO),
            ("Efeito Mecânico (M&M 3e)", 52, ALINHA_ESQ),
            ("Preço", 10, ALINHA_DIR),
            ("Peso", 10, ALINHA_DIR),
        ],
        [
            [
                p["nome"], p["ano"], p["ingrediente"], p["preparo"], p["cd"],
                p["tempo"], p["duracao"], p["efeito"], p["preco"], peso_em_texto(p["peso"]),
            ]
            for p in POCOES
        ],
        col_negrito=1,
        altura_linha=44,
    )

    # Folha 3: Plantas e Ingredientes
    ws3 = wb.create_sheet(title="Plantas e Ingredientes")
    _estilizar_aba(
        ws3,
        "PLANTAS MÁGICAS (HERBOLOGIA) E REAGENTES DE CRIATURAS (ANIMAIS FANTÁSTICOS)",
        [
            ("Ingrediente / Planta", 28, ALINHA_ESQ),
            ("Origem", 24, ALINHA_CENTRO),
            ("Classificação M.M.", 24, ALINHA_CENTRO),
            ("Colheita e Cuidados", 42, ALINHA_ESQ),
            ("Usos e Efeitos em Jogo", 46, ALINHA_ESQ),
            ("Preço", 10, ALINHA_DIR),
            ("Peso", 10, ALINHA_DIR),
        ],
        [
            [
                i["nome"], i["origem"], i["classificacao"], i["colheita"],
                i["usos"], i["preco"], peso_em_texto(i["peso"]),
            ]
            for i in INGREDIENTES
        ],
        col_negrito=1,
        altura_linha=42,
    )

    # Folha 4: Hogsmeade e Serviços
    ws4 = wb.create_sheet(title="Hogsmeade e Serviços")
    _estilizar_aba(
        ws4,
        "TABELA DE PREÇOS DE HOGSMEADE, EXPRESSO DE HOGWARTS E TRANSPORTE BRUXO",
        [
            ("Categoria", 20, ALINHA_CENTRO),
            ("Item / Serviço", 34, ALINHA_ESQ),
            ("Local", 28, ALINHA_CENTRO),
            ("Preço Tradicional", 20, ALINHA_CENTRO),
            ("Valor (G)", 12, ALINHA_DIR),
            ("Detalhes e Efeito", 52, ALINHA_ESQ),
        ],
        [
            [
                s["categoria"], s["item"], s["local"], s["preco_moedas"],
                s["valor_g"], s["detalhes"],
            ]
            for s in HOGSMEADE_SERVICOS
        ],
        col_negrito=2,
        altura_linha=36,
    )

    return wb


def main():
    wb = criar_planilha()

    caminho_ref = RAIZ / "referencias" / "harry potter" / "pocoes.xlsx"
    caminho_ref.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho_ref)

    caminho_dados = RAIZ / "dados" / "generos" / "escola_de_magia" / "pocoes.xlsx"
    caminho_dados.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho_dados)

    dados_json = {
        "regras": [{"titulo": t, "descricao": d} for t, d in REGRAS],
        "pocoes": POCOES,
        "ingredientes": INGREDIENTES,
        "hogsmeade_servicos": HOGSMEADE_SERVICOS,
    }
    caminho_json = RAIZ / "dados" / "generos" / "escola_de_magia" / "alquimia.json"
    caminho_json.write_text(json.dumps(dados_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Planilhas e alquimia.json de escola_de_magia gerados com sucesso.")


if __name__ == "__main__":
    main()
