"""Testes para o gênero Chamado de Cthulhu (anos 1920): Sanidade d100, ocupações e NPCs."""

import copy
import random
import pytest

from nucleo import data_loader, formatter, generator, pdf_export, player, rules, sanidade, validator


@pytest.fixture(scope="module")
def cthulhu():
    return data_loader.carregar_genero("cthulhu")


def _complicacoes():
    return [
        {"categoria": "motivacao", "nome": "Conhecimento", "detalhe": "Descobrir a verdade sobre o culto."},
        {"categoria": "complicacao", "nome": "Fobia", "detalhe": "Nictofobia: pavor da escuridão."},
    ]


def gerar_investigador(dados, ocupacao="detetive", np=3, foco=None, semente=42, riqueza="classe_media", **kwargs):
    arq = dados["jogador"]["arquetipos"][ocupacao]
    foco_id = foco or arq["focos"][0]["id"]
    return player.gerar_personagem(
        dados, ocupacao, np, foco_id, riqueza, _complicacoes(),
        rng=random.Random(semente), **kwargs
    )


# ---------------------------------------------------------------- dados e mecânica de Sanidade

def test_genero_cthulhu_carrega_sem_erros(cthulhu):
    assert cthulhu["genero"]["id"] == "cthulhu"
    assert cthulhu["genero"]["nome"] == "Chamado de Cthulhu"
    assert cthulhu["configuracoes"]["equipamento"] == "dinheiro"
    assert cthulhu["configuracoes"]["moeda"] == "$"
    assert cthulhu["configuracoes"]["sanidade"] is True
    assert cthulhu["configuracoes"]["np_padrao_jogador"] == 3
    assert len(cthulhu["jogador"]["arquetipos"]) == 15
    assert len(cthulhu["equipamentos"]) >= 25


def test_mecanica_sanidade_inicial_e_teto():
    # Will 0 -> 45
    assert sanidade.sanidade_inicial(0) == 45
    # Will 2 -> 55
    assert sanidade.sanidade_inicial(2) == 55
    # Will 10 -> 95
    assert sanidade.sanidade_inicial(10) == 95
    # Will 12 -> max 99
    assert sanidade.sanidade_inicial(12) == 99
    # Will -10 -> min 0
    assert sanidade.sanidade_inicial(-10) == 0

    # Sanidade máxima sem Mythos = 99
    assert sanidade.sanidade_maxima(0) == 99
    # Com 2 graduações em Mythos = 89
    assert sanidade.sanidade_maxima(2) == 89
    # Com 20 graduações = 0
    assert sanidade.sanidade_maxima(20) == 0


def test_teste_de_sanidade_sucesso_desastre_e_insanidade():
    # Sucesso normal: rolagem 30 com SAN 50 perde 0
    res = sanidade.teste_de_sanidade(30, 50, perda_sucesso="0", perda_fracasso="1D6")
    assert res["sucesso"] is True
    assert res["desastre"] is False
    assert res["perda"] == 0
    assert res["san_restante"] == 50

    # Auto-sucesso no 01 mesmo se SAN for baixíssima
    res_01 = sanidade.teste_de_sanidade(1, 5, perda_sucesso="1", perda_fracasso="1D10")
    assert res_01["sucesso"] is True
    assert res_01["desastre"] is False
    assert res_01["perda"] == 1

    # Desastre no 100: perda máxima do fracasso
    res_100 = sanidade.teste_de_sanidade(100, 70, perda_sucesso="0", perda_fracasso="1D6")
    assert res_100["sucesso"] is False
    assert res_100["desastre"] is True
    assert res_100["perda"] == 6  # 1D6 maximizado
    assert res_100["insanidade_temporaria_possivel"] is True

    # Com SAN < 50, 96 a 99 também são desastres
    res_96 = sanidade.teste_de_sanidade(96, 40, perda_sucesso="0", perda_fracasso="1D6")
    assert res_96["desastre"] is True
    assert res_96["perda"] == 6

    # Teste de intelecto para choque temporário
    # Sucesso no Int check (d20 + Int >= 10) compreende a verdade e enlouquece
    assert sanidade.teste_insanidade_temporaria(10, 0, cd=10) is True
    assert sanidade.teste_insanidade_temporaria(5, 2, cd=10) is False

    # Perda indefinida de 20% do dia
    assert sanidade.insanidade_indefinida(10, 50) is True
    assert sanidade.insanidade_indefinida(9, 50) is False


# ---------------------------------------------------------------- criação de investigadores (PJs)

@pytest.mark.parametrize("ocupacao", [
    "professor", "detetive", "medico", "jornalista", "antiquario",
    "veterano", "policial", "bibliotecario", "diletante", "clero",
    "escritor", "parapsicologo", "enfermeira", "advogado", "criminoso"
])
def test_todas_as_15_ocupacoes_geram_investigadores_validos_np3(cthulhu, ocupacao):
    arq = cthulhu["jogador"]["arquetipos"][ocupacao]
    for foco in arq["focos"]:
        pj = gerar_investigador(cthulhu, ocupacao, np=3, foco=foco["id"], semente=42)
        assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(3)
        assert pj["validacao"]["problemas"] == []
        assert pj["sanidade"] is not None
        assert 0 <= pj["sanidade"]["atual"] <= 99
        assert pj["sanidade"]["maxima"] <= 99
        # Sanidade inicial calculada a partir de Vontade
        vontade = pj["validacao"]["valores"]["defesas"]["Vontade"]
        assert pj["sanidade"]["inicial"] == min(99, max(0, 45 + 5 * vontade))
        # Formatação
        texto = formatter.texto(pj)
        assert "Sanidade:" in texto
        assert "$" in texto


@pytest.mark.parametrize("np", [1, 2, 3, 4, 5])
def test_investigador_nos_nps_permitidos(cthulhu, np):
    pj = gerar_investigador(cthulhu, "detetive", np=np, semente=np)
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(np)
    assert pj["validacao"]["problemas"] == []


def test_faixas_de_credito_e_riqueza(cthulhu):
    # Pobretão devolve 1 PP (orçamento sobe para 46 PP no NP 3)
    pj_pobretao = gerar_investigador(cthulhu, "criminoso", np=3, riqueza="pobretao")
    assert pj_pobretao["validacao"]["total_pp"] == 46
    assert pj_pobretao["dinheiro"]["inicial"] == 20

    # Ricaço tem $50.000 e 6 PP de Benefício: Riqueza
    pj_ricaco = gerar_investigador(cthulhu, "diletante", np=3, riqueza="ricaco")
    assert pj_ricaco["ficha"]["vantagens"]["Benefício (Riqueza)"] == 6
    assert pj_ricaco["dinheiro"]["inicial"] == 50000


# ---------------------------------------------------------------- NPCs e exportação

def test_npcs_cthulhu_gerados_com_sanidade(cthulhu):
    for arq_id in ("cultista", "policial_ronda"):
        grupo = generator.gerar_grupo(cthulhu, arq_id, 3, "combate", 2, rng=random.Random(42))
        assert grupo["npcs"]
        for npc in grupo["npcs"]:
            assert npc["validacao"]["status"] != "invalida"
            assert npc["sanidade"] is not None
            assert "Sanidade:" in formatter.texto(npc)


def test_exportacao_pdf_cthulhu_inclui_sanidade(cthulhu):
    pj = gerar_investigador(cthulhu, "professor", np=3)
    relatorio = pj["validacao"]
    campos = pdf_export.valores_dos_campos(pj, relatorio, cthulhu["genero"]["nome"])
    assert "Sanidade:" in campos["Notas & Condições"]
    assert "$" in campos["Notas & Condições"]
