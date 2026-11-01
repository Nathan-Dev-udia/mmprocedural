"""Tabela de Medidas do livro básico (dados/comum/medidas.json): graduações de massa, tempo, distância e volume.

Fora da tabela (abaixo de –5 ou acima de 30), cada graduação divide pela metade ou dobra a anterior. Um valor
pertence à menor graduação que o alcança: 12 horas é tempo 13, que vai de mais de 8 até 16 horas.
"""

import json
from functools import lru_cache
from pathlib import Path

ARQUIVO = Path(__file__).parent.parent / "dados" / "comum" / "medidas.json"


@lru_cache(maxsize=1)
def tabela():
    return {linha["graduacao"]: linha for linha in json.loads(ARQUIVO.read_text(encoding="utf-8"))["graduacoes"]}


def _valor(coluna, graduacao):
    linhas = tabela()
    menor, maior = min(linhas), max(linhas)
    if graduacao < menor:
        return linhas[menor][coluna] / 2 ** (menor - graduacao)
    if graduacao > maior:
        return linhas[maior][coluna] * 2 ** (graduacao - maior)
    return linhas[graduacao][coluna]


def _graduacao(coluna, valor):
    graduacao = min(tabela())
    while _valor(coluna, graduacao) > valor:
        graduacao -= 1
    while _valor(coluna, graduacao) < valor:
        graduacao += 1
    return graduacao


def graduacao_de_massa(kg):
    """Graduação de massa de um peso em kg; None para o que não pesa nada que conte (uma folha, um apito)."""
    return None if not kg else _graduacao("massa_kg", kg)


def massa(graduacao):
    """Texto da massa ("250 kg", "500 g") de uma graduação."""
    if graduacao in tabela():
        return tabela()[graduacao]["massa"]
    kg = _valor("massa_kg", graduacao)
    return f"{kg * 1000:g} g" if kg < 1 else f"{kg / 1000:g} t"


def distancia(graduacao):
    if graduacao in tabela():
        return tabela()[graduacao]["distancia"]
    metros = _valor("distancia_metros", graduacao)
    return f"{metros * 100:g} cm" if metros < 1 else f"{metros / 1000:g} km"


TEMPO_DE_UMA_HORA = 9


def km_por_hora(velocidade):
    """Distância coberta em uma hora (Distância = Tempo + Velocidade), como o Guia do Mestre: cavalo com
    Velocidade 4 anda 60 km/h."""
    return _valor("distancia_metros", TEMPO_DE_UMA_HORA + velocidade) / 1000


def capacidade_de_carga(forca):
    """Limites em kg de carga leve (sem penalidades) e carga máxima (esforço máximo) para uma graduação de Força."""
    leve = _valor("massa_kg", forca - 1)
    maxima = _valor("massa_kg", forca)
    return {"leve": leve, "maxima": maxima}


def categoria_de_carga(peso_kg, forca):
    """Classifica a carga transportada em 'leve', 'pesada' ou 'sobrecarregado' conforme a Força."""
    if not peso_kg or peso_kg <= 0:
        return "leve"
    cap = capacidade_de_carga(forca)
    if peso_kg <= cap["leve"]:
        return "leve"
    if peso_kg <= cap["maxima"]:
        return "pesada"
    return "sobrecarregado"
