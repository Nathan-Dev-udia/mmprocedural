"""Testes do validador. As fichas-base precisam reproduzir os totais impressos nos livros."""

import copy

import pytest

from nucleo import validator


def ficha_base(dados, arquetipo, np):
    faixa = next(f for f in dados["arquetipos"][arquetipo]["faixas"] if f["np"] == np)
    ficha = copy.deepcopy(faixa["ficha"])
    ficha["fontes"] = [{"nome": faixa["nome"], "status_dados": faixa["status_dados"]}]
    return ficha


@pytest.mark.parametrize("arquetipo, np, custos_do_livro, total_do_livro", [
    ("capanga", 3, {"habilidades": 18, "defesas": 3, "pericias": 7, "vantagens": 2}, 30),     # Bandido
    ("capanga", 4, {"habilidades": 16, "defesas": 10, "pericias": 16, "vantagens": 3}, 45),   # Guerrilheiro
    ("policial", 4, {"habilidades": 22, "defesas": 5, "pericias": 15, "vantagens": 3}, 45),   # Policial
    ("policial", 5, {"habilidades": 28, "defesas": 8, "pericias": 18, "vantagens": 6}, 60),   # Policial de elite
    ("cavalo", 3, {"habilidades": -14, "defesas": 6, "pericias": 2, "vantagens": 0, "poderes": 15}, 9),
    ("medico", 2, {"habilidades": 12, "defesas": 3, "pericias": 8, "vantagens": 1}, 24),       # Cientista
    ("geologo", 2, {"habilidades": 12, "defesas": 3, "pericias": 8, "vantagens": 1}, 24),      # Cientista
    ("falastrao", 2, {"habilidades": 12, "defesas": 5, "pericias": 10, "vantagens": 3}, 30),   # Informante
    ("padre", 2, {"habilidades": 10, "defesas": 2, "pericias": 16, "vantagens": 2}, 30),       # Repórter
    ("minerador", 3, {"habilidades": 18, "defesas": 3, "pericias": 7, "vantagens": 2}, 30),    # Bandido
    ("vaqueiro", 3, {"habilidades": 12, "defesas": 3, "pericias": 13, "vantagens": 2}, 30),    # Criminoso
])
def test_totais_batem_com_o_livro(dados, arquetipo, np, custos_do_livro, total_do_livro):
    relatorio = validator.validar(ficha_base(dados, arquetipo, np), np, dados["equipamentos"])
    assert relatorio["custos"] == custos_do_livro
    assert relatorio["total_pp"] == total_do_livro
    assert relatorio["problemas"] == []


def test_valores_do_cavalo_batem_com_o_guia(dados):
    valores = validator.validar(ficha_base(dados, "cavalo", 3), 3, dados["equipamentos"])["valores"]
    assert valores["defesas"] == {"Esquiva": 2, "Aparar": 2, "Fortitude": 5, "Vontade": 1, "Resistência": 4}
    ataque = valores["ataques"][0]
    assert (ataque["bonus"], ataque["dano"]) == (2, 4)


def test_laco_e_armadilha_resistida_por_esquiva(dados):
    valores = validator.validar(ficha_base(dados, "vaqueiro", 3), 3, dados["equipamentos"])["valores"]
    laco = next(a for a in valores["ataques"] if a["nome"] == "Laço")
    assert laco["efeito_nome"] == "Armadilha" and laco["resistido_por"] == "Esquiva"
    assert (laco["bonus"], laco["dano"], laco["cd_resistencia"]) == (3, 3, 13)   # CD 10 + graduação


def test_limite_de_ataque_violado(dados):
    ficha = ficha_base(dados, "capanga", 3)
    ficha["habilidades"]["For"] += 1   # desarmado passa a +3 com Dano 4 = 7 > 6
    relatorio = validator.validar(ficha, 3, dados["equipamentos"])
    assert relatorio["status"] == "invalida"
    assert any("Desarmado" in p for p in relatorio["problemas"])


def test_equipamento_acima_do_orcamento(dados):
    ficha = ficha_base(dados, "capanga", 3)
    ficha["equipamento"].append("escopeta")   # 7 + 10 = 17 > 10 pontos
    relatorio = validator.validar(ficha, 10, dados["equipamentos"])
    assert any("vantagem Equipamento" in p for p in relatorio["problemas"])


def test_status_validada_quando_tudo_e_calculado(dados):
    relatorio = validator.validar(ficha_base(dados, "capanga", 3), 3, dados["equipamentos"])
    assert relatorio["status"] == "validada"


def test_status_calculada_com_custo_informado(dados):
    relatorio = validator.validar(ficha_base(dados, "cavalo", 3), 3, dados["equipamentos"])
    assert relatorio["status"] == "calculada"
    assert relatorio["origem_dos_custos"]["poderes"] == "informado"


def test_status_parcial_com_custo_pendente(dados):
    ficha = ficha_base(dados, "cavalo", 3)
    ficha["poderes"]["velocidade"]["custo_informado"] = None
    relatorio = validator.validar(ficha, 3, dados["equipamentos"])
    assert relatorio["status"] == "parcial"
    assert relatorio["total_pp"] is None


def test_status_parcial_com_fonte_pendente(dados):
    ficha = ficha_base(dados, "capanga", 3)
    ficha["fontes"].append({"nome": "Módulo X", "status_dados": "pendente"})
    assert validator.validar(ficha, 3, dados["equipamentos"])["status"] == "parcial"


def test_dados_ilustrativos_geram_aviso(dados):
    ficha = ficha_base(dados, "capanga", 3)
    ficha["fontes"].append({"nome": "Módulo X", "status_dados": "ilustrativo"})
    relatorio = validator.validar(ficha, 3, dados["equipamentos"])
    assert any("ilustrativos" in a for a in relatorio["avisos"])
