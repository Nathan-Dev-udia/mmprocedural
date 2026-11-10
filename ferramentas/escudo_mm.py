"""Blocos do Escudo do Mestre com as regras do livro básico de M&M 3e, iguais em todos os gêneros.

Texto conferido com o livro básico e com as seções 2.5 a 2.8, 5.4, 5.5, 6 e 7 dos Livros do Mestre do faroeste e do
cyberpunk. Cada gênero passa só os exemplos e as linhas próprias (recarga, dirigir, dinamite...).
Usado por ferramentas/criar_cthulhu_escudo.py e para corrigir dados/escudo/faroeste.json (que é editado à mão).
"""


def tabela(titulo, colunas, linhas, nota=None):
    bloco = {"tipo": "tabela", "titulo": titulo, "colunas": colunas, "linhas": linhas}
    if nota:
        bloco["nota"] = nota
    return bloco


def lista(titulo, itens):
    return {"tipo": "lista", "titulo": titulo, "itens": itens}


def acoes(extras=(), comandar="um capanga ou animal treinado"):
    """Tabela de ações do livro básico; `extras` são linhas [ação, tipo, efeito] do gênero, postas antes de
    Mover-se."""
    padrao = [
        ["Atacar", "Padrão", "Um teste de ataque contra um alvo ao alcance."],
        ["Mirar", "Padrão", "+5 no próximo ataque corpo a corpo ou à queima-roupa; +2 à distância. Fica vulnerável "
                            "enquanto mira, e a próxima ação tem de ser o ataque."],
        ["Agarrar", "Padrão", "Ataque; o alvo resiste com Força ou Esquiva. 1 grau: restrito; 2 ou mais: amarrado."],
        ["Ajudar", "Padrão", "Ataque contra CD 10; o aliado ganha +2 no ataque ou na defesa (+5 com três graus)."],
        ["Carga", "Padrão", "Move-se a toda velocidade em linha reta e ataca corpo a corpo com –2."],
        ["Defender-se", "Padrão", "Até o próximo turno, a defesa ativa vira teste oposto; 10 ou menos no dado vale +10."],
        ["Derrubar", "Padrão", "Ataque corpo a corpo com –2; depois, teste oposto de Acrobacia ou Atletismo."],
        ["Desarmar", "Padrão", "Ataque com –2 (–5 à distância), depois dano contra a Força do alvo."],
        ["Quebrar", "Padrão", "Ataque com –5 contra um objeto segurado."],
        ["Recuperar-se", "Padrão", "Uma vez por conflito: remove a pior condição de dano ou fadiga (ou dá um "
                                   "salvamento extra) e +2 nas defesas ativas até o próximo turno."],
        ["Preparar", "Padrão", "Define uma ação e o gatilho; age como reação quando ele acontecer."],
    ]
    movimento = [
        ["Mover-se", "Movimento", "Até a sua velocidade. Atletismo CD 15 (livre) dá +1 de velocidade por uma rodada."],
        ["Sacar ou guardar arma", "Movimento", "Livre com a vantagem Saque Rápido."],
        ["Levantar-se", "Movimento", "Livre com Acrobacia CD 20 ou com a vantagem De Pé."],
        ["Escapar", "Movimento", "Acrobacia ou Atletismo contra a Força de quem agarra."],
        ["Comandar", "Movimento", f"Dá uma ordem a {comandar}."],
        ["Jogar-se no chão", "Livre", "Fica caído (–5 para quem atira em você de longe)."],
        ["Atrasar", "Nenhuma", "Age mais tarde na ordem de iniciativa."],
    ]
    return tabela("Ações", ["Ação", "Tipo", "Efeito"], padrao + list(extras) + movimento)


def manobras(encontrao="a cavalo, por exemplo", extras=()):
    return tabela("Manobras", ["Manobra", "Efeito"], [
        ["Ataque Acurado", "Até –2 no efeito para +2 no ataque."],
        ["Ataque Poderoso", "Até –2 no ataque para +2 no efeito."],
        ["Ataque Defensivo", "Até –2 no ataque para +2 em Esquiva e Aparar."],
        ["Ataque Imprudente", "Até –2 em Esquiva e Aparar para +2 no ataque."],
        ["Ataque de Equipe", "Atacantes atrasam para o mesmo ponto da iniciativa; cada acerto extra soma +2 (+5 com "
                             "três graus) ao efeito principal."],
        ["Ataque Surpresa", "Alvo pego de surpresa fica vulnerável."],
        ["Ataque Final", "Contra alvo indefeso ao alcance perto: ataque de rotina, ou rolado e todo acerto é crítico."],
        ["Desmoralizar", "Intimidação contra Intuição ou Vontade: alvo prejudicado (desabilitado com quatro graus) até "
                         "o fim do próximo turno dele."],
        ["Fintar", "Enganação contra Enganação ou Intuição: alvo vulnerável contra o seu próximo ataque."],
        ["Encontrão", f"Durante uma carga ({encontrao}), o dano usa a velocidade +1; você sofre metade do impacto."],
    ] + list(extras), nota="Os ajustes valem até o início do próximo turno. Com a vantagem de mesmo nome, a troca vai "
                           "até 5 pontos.")


def esforco_extra(equipamento="uma arma ou uma montaria"):
    return lista("Esforço extra", [
        "Uma vez por turno, ação livre. Escolha: **ação** padrão extra; **+2** num teste (ou +2 vira +5); "
        "**salvamento** extra contra efeito em andamento; **+1 Velocidade ou Força** até o próximo turno.",
        "**Custo:** fatigado no início do próximo turno (fatigado vira exausto; exausto vira incapacitado). Um ponto "
        "heroico anula a fadiga.",
        f"Equipamento não aceita esforço extra: para forçar {equipamento} além do limite, gaste um ponto heroico.",
    ])


PONTOS_HEROICOS = lista("Pontos heroicos", [
    "Cada jogador começa a sessão com **1 ponto heroico**; os não gastos não passam para a próxima aventura.",
    "**Melhorar uma rolagem:** rerrole o d20; de 1 a 10 no novo dado, some 10 (fica entre 11 e 20).",
    "**Feito heroico:** uma graduação de vantagem (que não seja de sorte) até o fim do próximo turno.",
    "**Recuperar-se:** remove tonto, atordoado ou fatigado sem gastar ação, ou converte exausto em fatigado.",
    "**Editar a cena**, **Inspiração** (uma pista do mestre) ou **repelir** um efeito como reação.",
])


def aflicao(nota_extra="", quarto_grau=None):
    """`quarto_grau`: texto da linha do 4º grau, que não existe no livro básico (só como regra da casa)."""
    linhas = [
        ["1º grau (falha por 1 a 5)", "Tonto, em transe, fatigado, impedido, prejudicado ou vulnerável"],
        ["2º grau (falha por 6 a 10)", "Atordoado, caído, compelido, desabilitado, exausto, imóvel ou vulnerável"],
        ["3º grau (falha por 11 a 15)", "Adormecido, controlado, desatento, incapacitado, paralisado ou transformado"],
    ]
    if quarto_grau:
        linhas.append(["4º grau [Casa] (16 ou mais)", quarto_grau])
    nota = ("O efeito define uma condição para cada grau; graus mais altos substituem os mais baixos. No fim de cada "
            "turno, o alvo faz um salvamento para tirar as condições de 1º e 2º grau; as de 3º grau exigem um minuto "
            "ou ajuda (Tratamento CD 10 + graduação).")
    return tabela("Aflição: condição por grau de falha", ["Grau de falha", "Condições possíveis"], linhas,
                  nota=f"{nota} {nota_extra}".strip())


def dano(letal, padrao="socos, coronhadas, garrafadas"):
    """Tabela de dano com as duas colunas: padrão (livro básico) e letal (Guia do Mestre)."""
    return tabela("Dano: padrão e letal", ["Grau de falha", f"Padrão ({padrao})", f"Letal ({letal})"], [
        ["Sucesso", "Sem efeito.", "Sem efeito."],
        ["1º grau (1 a 5)", "–1 nos próximos salvamentos de Resistência (cumulativo).",
         "Ferido: –1 na Resistência (cumulativo)."],
        ["2º grau (6 a 10)", "–1 e tonto até o fim do próximo turno.", "Ferido e tonto até o fim do próximo turno."],
        ["3º grau (11 a 15)", "–1 e abatido (tonto e impedido). Se já estava abatido, aplique o 4º grau.",
         "Ferido, abatido e desabilitado (–5 em todos os testes)."],
        ["4º grau (16 ou mais)", "Incapacitado.", "Incapacitado e moribundo."],
    ], nota="Salvamento: d20 + Resistência contra 15 + Dano. Incapacitado que falha fica moribundo; moribundo que "
            "falha morre. Opcional: cinco ou mais graus de falha contra dano letal matam na hora.")


def condicoes_basicas(compelido="Ações ditadas por outra pessoa (hipnose, feitiço, droga)."):
    return tabela("Condições básicas", ["Condição", "Efeito"], [
        ["Prejudicado", "–2 em todos os testes (ou nos indicados)."],
        ["Desabilitado", "–5 em todos os testes (ou nos indicados). Sobrepõe prejudicado."],
        ["Tonto", "Só ações livres e uma ação padrão por turno."],
        ["Atordoado", "Não pode fazer nenhuma ação, nem livre. Sobrepõe tonto."],
        ["Impedido", "Move-se à metade (–1 graduação de velocidade)."],
        ["Imóvel", "Não se move do lugar. Sobrepõe impedido."],
        ["Vulnerável", "Esquiva e Aparar pela metade, arredondando para cima."],
        ["Indefeso", "Esquiva e Aparar 0. Atacantes podem fazer ataques de rotina; um ataque rolado que acerte vira "
                     "crítico. Sobrepõe vulnerável."],
        ["Desatento", "Não percebe o ambiente nem age com base nele."],
        ["Fatigado", "Impedido. Some com 1 hora de descanso."],
        ["Compelido / Controlado", compelido],
    ])


CONDICOES_COMBINADAS = tabela("Condições combinadas", ["Condição", "Efeito"], [
    ["Abatido", "Tonto e impedido."],
    ["Exausto", "Prejudicado e impedido. Some com 1 hora de descanso em lugar confortável."],
    ["Caído", "Impedido; –5 nos ataques corpo a corpo; atacantes têm +5 corpo a corpo e –5 à distância. "
              "Levantar-se: ação de movimento."],
    ["Restrito", "Impedido e vulnerável (imóvel se preso a algo fixo)."],
    ["Amarrado", "Indefeso, imóvel e prejudicado."],
    ["Surpreso", "Atordoado e vulnerável."],
    ["Cego", "Impedido, visualmente desatento e vulnerável; tudo tem camuflagem total contra ele."],
    ["Paralisado", "Indefeso, imóvel e fisicamente atordoado; ainda percebe o que acontece."],
    ["Incapacitado", "Indefeso, atordoado e desatento; normalmente caído."],
    ["Moribundo", "Incapacitado; Fortitude CD 15 na hora e a cada rodada: dois graus de sucesso estabilizam, três "
                  "graus de falha somados matam."],
])


def tratamento(kit="maleta médica", extras=()):
    return tabela(f"Tratamento (só treinado; sem {kit}, –5)", ["Tarefa", "CD", "Efeito"], [
        ["Diagnosticar (1 minuto)", "10", "+2 nos testes seguintes de Tratamento."],
        ["Estabilizar (padrão)", "15", "Estanca o sangramento de um moribundo."],
        ["Reviver (padrão)", "15", "Remove tonto ou atordoado; não remove ferimentos."],
        ["Longo prazo (no descanso)", "15", "Reduz a recuperação em 1 graduação de tempo."],
        ["Doença ou veneno", "15", "+2 no salvamento do paciente (+5 com três graus de sucesso)."],
    ] + list(extras), nota="Tratar a si mesmo: só diagnosticar, longo prazo e doenças ou venenos, com –5.")
