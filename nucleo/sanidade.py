"""Mecânica de Sanidade adaptada de Chamado de Cthulhu para Mutantes & Malfeitores.

A Sanidade não é uma habilidade nem defesa do M&M; é um medidor à parte (0 a 99),
rolado em d100, fiel ao horror cósmico clássico.
"""

import math
import random
import re

_DADO = re.compile(r"^(\d+)?d(\d+)(?:([+-])(\d+))?$", re.IGNORECASE)


def sanidade_inicial(vontade):
    """Calcula a Sanidade inicial a partir da defesa de Vontade do personagem (teto de 99)."""
    return min(99, max(0, 45 + 5 * vontade))


def sanidade_maxima(graduacao_mythos=0):
    """Calcula a Sanidade máxima permitida: 99 menos 5 vezes a graduação em Mythos de Cthulhu."""
    return max(0, 99 - 5 * max(0, graduacao_mythos))


PERICIA_MYTHOS = "Especialidade: Mythos de Cthulhu"


def sanidade_da_ficha(vontade, ficha):
    """Sanidade inicial, atual e máxima de uma ficha; a atual nunca passa da máxima permitida pelo Mythos."""
    maxima = sanidade_maxima(ficha.get("pericias", {}).get(PERICIA_MYTHOS, 0))
    inicial = min(sanidade_inicial(vontade), maxima)
    return {"inicial": inicial, "atual": inicial, "maxima": maxima}


def rolar_expressao(expressao, maximo=False, rng=None):
    """Interpreta números inteiros ("0", "5") ou rolagens ("1D6", "1D10", "1D4+1", "1D100").

    Se `maximo` for True, devolve o resultado máximo possível da rolagem (usado em desastres).
    """
    expressao = str(expressao).strip()
    if expressao.isdigit():
        return int(expressao)
    m = _DADO.match(expressao)
    if not m:
        try:
            return int(expressao)
        except ValueError:
            return 0
    qtd = int(m.group(1)) if m.group(1) else 1
    lados = int(m.group(2))
    sinal = m.group(3)
    mod = int(m.group(4)) if m.group(4) else 0
    if sinal == "-":
        mod = -mod
    if maximo:
        return qtd * lados + mod
    _rng = rng or random
    return sum(_rng.randint(1, lados) for _ in range(qtd)) + mod


def teste_de_sanidade(rolagem, san_atual, perda_sucesso="0", perda_fracasso="1D6", rng=None):
    """Executa um teste de Sanidade em d100.

    Regras do Chamado de Cthulhu 7ª edição:
    - 01 é sempre sucesso.
    - 100 é sempre desastre (perda máxima do fracasso).
    - Com Sanidade atual menor que 50, resultados de 96 a 100 são desastres.
    - Se a perda de Sanidade for de 5 pontos ou mais em uma única rolagem,
      o personagem corre o risco de Insanidade Temporária (necessita teste de Intelecto).
    """
    if rolagem < 1 or rolagem > 100:
        raise ValueError("Rolagem de d100 deve ficar entre 1 e 100.")
    desastre = rolagem == 100 or (san_atual < 50 and rolagem >= 96)
    sucesso_auto = rolagem == 1
    sucesso = (rolagem <= san_atual or sucesso_auto) and not desastre

    if sucesso:
        perda = rolar_expressao(perda_sucesso, rng=rng)
    elif desastre:
        perda = rolar_expressao(perda_fracasso, maximo=True, rng=rng)
    else:
        perda = rolar_expressao(perda_fracasso, rng=rng)

    san_restante = max(0, san_atual - perda)
    return {
        "sucesso": sucesso,
        "desastre": desastre,
        "perda": perda,
        "san_anterior": san_atual,
        "san_restante": san_restante,
        "insanidade_temporaria_possivel": perda >= 5,
        "san_zero": san_restante == 0,
    }


def teste_insanidade_temporaria(rolagem_d20, intelecto, cd=10):
    """Teste de Intelecto do M&M para quando o investigador perde 5 ou mais pontos de SAN.

    Fiel ao Chamado de Cthulhu: se o teste tiver SUCESSO (rolagem + Int >= CD 10),
    a mente compreende a horrível magnitude do que presenciou e entra em insanidade
    temporária (1D10 horas). Se falhar no teste, a mente reprime a verdade e não entra em choque imediato.
    """
    return (rolagem_d20 + intelecto) >= cd


def insanidade_indefinida(perdido_no_dia, san_inicio_dia):
    """Retorna True se o personagem perdeu 1/5 (20%) ou mais da Sanidade que possuía no início do dia."""
    if san_inicio_dia <= 0:
        return False
    return perdido_no_dia >= (san_inicio_dia / 5.0)


def ponto_de_ruptura(san_inicio_dia):
    """Menor perda no dia que causa insanidade indefinida: 1/5 da SAN do início do dia, arredondado para cima.

    Bate com `insanidade_indefinida` (perdido >= SAN/5): com SAN 62, a ruptura é 13 (12,4 arredondado para cima).
    """
    return max(0, math.ceil(san_inicio_dia / 5))


# ---------------------------------------------------------------- textos de regra (fonte única do escudo e do PDF)

# Acessos de loucura (d10): (resultado, nome, efeito na mesa). Duram o tempo de DURACAO_DO_ACESSO.
ACESSOS_DE_LOUCURA = [
    (1, "Amnésia", "Esquece quem é e como chegou ali; não usa Especialidades nem reconhece os aliados."),
    (2, "Catatonia", "Desmaia ou congela: fica imóvel e indefeso, sem agir até o fim do acesso."),
    (3, "Pânico e fuga", "Larga o que segura e foge do horror; só faz ações de movimento para se afastar."),
    (4, "Histeria", "Ri, grita ou chora sem controle: prejudicado (–2) em todos os testes e não fala com coerência."),
    (5, "Alucinações", "Vê paredes derretendo e sombras que atacam: prejudicado (–2) em Percepção e nos ataques."),
    (6, "Paranoia", "Crê que um aliado é cultista: recusa ajuda, testes de equipe e Tratamento vindos dele."),
    (7, "Fúria cega", "Ataca o ser mais próximo, amigo ou inimigo, com o que tiver à mão (Ataque Total)."),
    (8, "Ecolalia e tiques", "Repete em voz alta frases profanas: não consegue falar nada útil; –5 em Furtividade."),
    (9, "Fobia súbita", "Ganha uma fobia de algo da cena (água, sangue, insetos, escuro); evita ou foge do gatilho."),
    (10, "Fascínio mórbido", "Aproxima-se da abominação em transe: desatento a tudo o mais e vulnerável."),
]

DURACAO_DO_ACESSO = ("1D10 rodadas em tempo real (cena com ação) ou 1D10 horas em resumo "
                     "(o investigador volta a si em outro lugar, sem lembrar o que fez)")

# Estados de loucura: (estado, gatilho, duração e efeito).
ESTADOS_DE_LOUCURA = [
    ("Acesso de loucura", "Início de qualquer insanidade", DURACAO_DO_ACESSO + "; role na tabela d10."),
    ("Insanidade temporária", "Perda de 5 ou mais num só teste e sucesso no teste de Intelecto (CD 10); "
     "na falha, a mente reprime o choque", "1D10 horas; começa com um acesso de loucura."),
    ("Insanidade indefinida", "Perda no dia de 1/5 ou mais da SAN do início do dia",
     "1D6 meses; começa com um acesso de loucura e deixa uma fobia ou mania, que o tratamento pode curar."),
    ("Insanidade permanente", "SAN chega a 0", "Para sempre: o investigador vira um personagem do Mestre."),
]

RECUPERACAO_DE_SANIDADE = [
    "**Psicanálise:** uma vez por mês de tratamento, o terapeuta faz Tratamento CD 15 (com Especialidade: "
    "Psicologia ou Medicina). Sucesso: o paciente recupera 1D3 de SAN. Falha por 2 graus ou mais: perde 1D6.",
    "**Internação em sanatório:** a equipe faz o mesmo teste mensal da psicanálise; é onde o investigador passa "
    "os 1D6 meses de insanidade indefinida.",
    "**Fim da investigação:** derrotar o culto ou frustrar o plano recupera de 1D6 a 1D10 de SAN, a critério do "
    "Mestre; fracassar não recupera nada.",
    "**Teto:** a SAN nunca passa da máxima (99 – 5 × graduação em Mythos de Cthulhu).",
]
