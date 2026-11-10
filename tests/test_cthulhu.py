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
    import io
    from pathlib import Path
    import pypdf

    pj = gerar_investigador(cthulhu, "professor", np=3)
    relatorio = pj["validacao"]
    campos = pdf_export.valores_dos_campos(pj, relatorio, cthulhu["genero"]["nome"])
    assert "Sanidade:" in campos["Notas & Condições"]
    assert "$" in campos["Notas & Condições"]

    # Ficha completa com a 3ª página (Rastreador de Sanidade)
    modelo = Path(__file__).parent.parent / "dados" / "comum" / "ficha_editavel.pdf"
    if modelo.is_file():
        pdf_bytes = pdf_export.gerar_pdf(str(modelo), pj, relatorio, cthulhu["genero"]["nome"])
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) == 3
        texto_p3 = reader.pages[2].extract_text()
        assert "REGISTRO DE SANIDADE" in texto_p3
        assert "RASTREADOR DE PONTOS DE SANIDADE" in texto_p3
        assert "TABELA DE ACESSOS DE LOUCURA" in texto_p3


@pytest.mark.parametrize("genero", ["cthulhu", "faroeste"])
def test_itens_extras_nao_viram_vantagens(genero):
    """Regressão: os itens extras do sorteio de equipamento entravam na ficha como vantagens (e custavam PP)."""
    dados = data_loader.carregar_genero(genero)
    riquezas = dados["jogador"]["riqueza"]
    riqueza = (riquezas[2]["id"] if isinstance(riquezas, list) else list(riquezas)[2])
    for arq_id, arq in dados["jogador"]["arquetipos"].items():
        for semente in range(3):
            npc = player.gerar_personagem(dados, arq_id, 3, arq["focos"][0]["id"], riqueza, _complicacoes(),
                                          rng=random.Random(semente))
            desconhecidas = [v for v in npc["ficha"]["vantagens"] if rules.nome_base(v) not in dados["vantagens"]]
            assert not desconhecidas, f"{arq_id}: {desconhecidas}"


def test_sanidade_da_ficha_respeita_maxima_do_mythos():
    ficha = {"pericias": {sanidade.PERICIA_MYTHOS: 8}}
    san = sanidade.sanidade_da_ficha(6, ficha)
    assert san["maxima"] == 59
    assert san["inicial"] == san["atual"] == 59
    assert sanidade.sanidade_da_ficha(2, {"pericias": {}}) == {"inicial": 55, "atual": 55, "maxima": 99}


def test_ponto_de_ruptura_bate_com_insanidade_indefinida():
    for san in (1, 5, 37, 62, 99):
        ruptura = sanidade.ponto_de_ruptura(san)
        assert sanidade.insanidade_indefinida(ruptura, san)
        assert not sanidade.insanidade_indefinida(ruptura - 1, san)
    assert sanidade.ponto_de_ruptura(62) == 13


def test_pagina_de_sanidade_usa_a_ficha_e_a_ruptura_certa(cthulhu):
    from nucleo import sanidade_pdf
    pj = gerar_investigador(cthulhu, "professor", np=3)
    pj["sanidade"] = {"inicial": 62, "atual": 62, "maxima": 99}
    assert sanidade_pdf._sanidade_do_personagem(pj)["ruptura_diaria"] == 13
    sem_registro = dict(pj, sanidade=None, ficha={**pj["ficha"], "sanidade": None,
                                                  "pericias": {sanidade.PERICIA_MYTHOS: 8}})
    calculada = sanidade_pdf._sanidade_do_personagem(sem_registro)
    assert calculada["maxima"] == 59 and calculada["inicial"] <= 59


def test_pagina_de_sanidade_cabe_numa_folha_com_complicacoes_longas(cthulhu):
    import io
    from pypdf import PdfReader
    from nucleo import sanidade_pdf
    longa = "Desconfia de qualquer autoridade, sobretudo de policiais e padres que fazem perguntas demais. " * 3
    complicacoes = _complicacoes() + [{"categoria": "complicacao", "nome": nome, "detalhe": longa}
                                      for nome in ("Paranoia", "Mania", "Obsessão", "Pesadelos")]
    arq = cthulhu["jogador"]["arquetipos"]["professor"]
    pj = player.gerar_personagem(cthulhu, "professor", 5, arq["focos"][0]["id"], "classe_media", complicacoes,
                                 rng=random.Random(3))
    leitor = PdfReader(io.BytesIO(sanidade_pdf.gerar_pagina_sanidade(pj)))
    assert len(leitor.pages) == 1
    texto = leitor.pages[0].extract_text()
    assert "Jogador: Jogador" not in texto
    assert "REGISTRO DIÁRIO DE SANIDADE" in texto
