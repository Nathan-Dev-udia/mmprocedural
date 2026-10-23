"""Tabelas de regras de Mutantes & Malfeitores 3ª edição usadas pelo validador.

Tudo aqui vem do livro básico (cap. 2 a 4). Quando uma regra nova for
implementada, ela entra neste arquivo, e o validador só a aplica.
"""

import math

# Habilidades, na ordem da ficha.
HABILIDADES = ["For", "Vig", "Agi", "Des", "Lut", "Int", "Pro", "Pre"]
HABILIDADE_MINIMA = -5

# Defesas que podem ser compradas com pontos e a habilidade que as sustenta.
# A Resistência não entra aqui: só sobe com vantagens, armadura ou poderes.
DEFESAS_COMPRAVEIS = {
    "Esquiva": "Agi",
    "Aparar": "Lut",
    "Fortitude": "Vig",
    "Vontade": "Pro",
}

# Perícias e a habilidade de cada uma.
PERICIAS = {
    "Acrobacia": "Agi",
    "Atletismo": "For",
    "Combate à Distância": "Des",
    "Combate Corpo-a-Corpo": "Lut",
    "Enganação": "Pre",
    "Especialidade": "Int",
    "Furtividade": "Agi",
    "Intimidação": "Pre",
    "Intuição": "Pro",
    "Investigação": "Int",
    "Percepção": "Pro",
    "Persuasão": "Pre",
    "Prestidigitação": "Des",
    "Tecnologia": "Int",
    "Tratamento": "Int",
    "Veículos": "Des",
}

# Perícias que exigem uma especialização depois de ":".
PERICIAS_COM_ESPECIALIZACAO = {"Combate à Distância", "Combate Corpo-a-Corpo", "Especialidade"}

# O livro básico manda usar Especialidade: Cavalgar com Agilidade.
PERICIAS_EXCECOES = {"Especialidade: Cavalgar": "Agi"}

# Custos (livro básico, tabela "Custo de Características").
CUSTO_POR_GRADUACAO_HABILIDADE = 2
CUSTO_POR_GRADUACAO_DEFESA = 1
GRADUACOES_DE_PERICIA_POR_PONTO = 2
CUSTO_POR_GRADUACAO_VANTAGEM = 1
PONTOS_DE_EQUIPAMENTO_POR_GRADUACAO = 5
INICIATIVA_POR_GRADUACAO = 4

# Vantagens que alteram valores calculados da ficha.
VANTAGEM_EQUIPAMENTO = "Equipamento"
VANTAGEM_RESISTENCIA = "Rolamento Defensivo"
VANTAGEM_INICIATIVA = "Iniciativa Aprimorada"
VANTAGEM_ATAQUE = {"corpo": "Ataque Corpo-a-Corpo", "distancia": "Ataque à Distância"}

# Habilidade usada no teste de ataque de cada tipo.
HABILIDADE_DE_ATAQUE = {"corpo": "Lut", "distancia": "Des"}

# Qualidades de arma do Gadget Guide: Archaic Weapons (Alcance e Perigosa custam 1 ponto por graduação; as
# outras, 1 ponto). Só a Perigosa muda a conta da ficha (o crítico); as outras valem na mesa.
QUALIDADES_DE_ARMA = {
    "Perigosa": "Amplia a margem de crítico em 1 por graduação (19–20 com uma graduação).",
    "Alcance": "Ataca alvos mais longe: 1,5 m por graduação (Alcance 2 = 3 m, como as armas de haste do D&D).",
    "Quebrar": "Como a vantagem Quebrar Arma: ao se defender de um ataque armado com sucesso, pode atacar a arma "
               "do atacante como reação.",
    "Esmagar": "Sem penalidade no teste de ataque para quebrar um objeto que outro personagem segura.",
    "Desarmar": "Tenta desarmar sem a penalidade de circunstância.",
    "Derrubar": "Como Derrubar Aprimorado: sem penalidade para derrubar, sem contra-ataque, e você escolhe se o alvo "
                "se defende com Acrobacia ou Atletismo.",
    "Agarrar": "Como Agarrar Rápido: depois de acertar, tenta agarrar o alvo como ação livre, usando o Dano da arma "
               "como Força.",
    "Enredar": "Quem está agarrado pela arma sofre –2 nos testes para escapar.",
    "Dupla": "Arma de duas pontas: pode dividir o dano entre dois alvos.",
}

# Pontos de poder iniciais de um personagem de jogador: 15 por NP (tabela "Pontos de Poder Iniciais").
PONTOS_POR_NP = 15

# Tabela "Referências de Habilidade": 7 é o ápice da capacidade humana.
HABILIDADE_MAXIMA_HUMANA = 7

# Sorte: no máximo graduações iguais à metade do NP (livro básico, vantagem Sorte).
VANTAGEM_SORTE = "Sorte"

# Vantagens que podem ser compradas várias vezes e que valem a pena subir aos poucos.
VANTAGENS_ESCALAVEIS = {"Ataque à Distância", "Ataque Corpo-a-Corpo", "Rolamento Defensivo",
                        "Iniciativa Aprimorada", "Sorte", "Crítico Aprimorado"}

TIPOS_DE_PASSO = {"habilidade", "pericia", "defesa", "vantagem"}


def nome_base(nome):
    """'Combate à Distância: Pistolas' -> 'Combate à Distância'; 'Benefício (Status)' -> 'Benefício'."""
    return nome.split(":")[0].split(" (")[0].strip()


def habilidade_da_pericia(nome):
    """Devolve a habilidade de uma perícia, ou None se a perícia não existir."""
    if nome in PERICIAS_EXCECOES:
        return PERICIAS_EXCECOES[nome]
    return PERICIAS.get(nome_base(nome))


def pericia_valida(nome):
    """Confere se o nome é uma perícia do livro, com especialização quando ela é exigida."""
    base = nome_base(nome)
    if base not in PERICIAS:
        return False
    if base in PERICIAS_COM_ESPECIALIZACAO:
        return ":" in nome and nome.split(":", 1)[1].strip() != ""
    return True


def custo_pericias(total_de_graduacoes):
    """1 ponto a cada 2 graduações. Um total ímpar é arredondado para cima."""
    return math.ceil(total_de_graduacoes / GRADUACOES_DE_PERICIA_POR_PONTO)


def orcamento_de_jogador(np):
    return PONTOS_POR_NP * np


def limite_de_sorte(np):
    return np // 2


def limites_do_np(np):
    """Tetos impostos pelo nível de poder (livro básico, cap. 2)."""
    return {
        "pericia": np + 10,
        "ataque_mais_efeito": 2 * np,
        "efeito_sem_ataque": np,
        "esquiva_mais_resistencia": 2 * np,
        "aparar_mais_resistencia": 2 * np,
        "fortitude_mais_vontade": 2 * np,
    }
