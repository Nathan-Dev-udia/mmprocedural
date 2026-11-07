"""Mecânica de Sanidade adaptada de Chamado de Cthulhu para Mutantes & Malfeitores.

A Sanidade não é uma habilidade nem defesa do M&M; é um medidor à parte (0 a 99),
rolado em d100, fiel ao horror cósmico clássico.
"""

import random
import re

_DADO = re.compile(r"^(\d+)?d(\d+)(?:([+-])(\d+))?$", re.IGNORECASE)


def sanidade_inicial(vontade):
    """Calcula a Sanidade inicial a partir da defesa de Vontade do personagem (teto de 99)."""
    return min(99, max(0, 45 + 5 * vontade))


def sanidade_maxima(graduacao_mythos=0):
    """Calcula a Sanidade máxima permitida: 99 menos 5 vezes a graduação em Mythos de Cthulhu."""
    return max(0, 99 - 5 * max(0, graduacao_mythos))


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
