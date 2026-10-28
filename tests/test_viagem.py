"""Testes da rolagem de eventos de viagem: categorias por gênero, tabelas consistentes, contas iguais às da planilha e a API."""

import random

import pytest

import app
from nucleo import bestiario, viagem

SITUACAO = {"area": "Média", "periodo": "Noite", "estacao": "Outono", "terreno": "Floresta",
            "situacao": "Acampado com fogueira"}


def test_categorias_por_genero():
    categorias = viagem.categorias()
    assert [c["id"] for c in categorias] == ["fantasia"]
    assert categorias[0]["nome"] == "Fantasia medieval"
    with pytest.raises(ValueError):
        viagem.tabelas("faroeste")


@pytest.mark.parametrize("categoria", [c["id"] for c in viagem.categorias()])
def test_tabelas_fecham_e_cobrem_todas_as_situacoes(categoria):
    t = viagem.tabelas(categoria)
    areas = [a["id"] for a in t["areas"]]
    for estacao in t["estacoes"]:
        assert sum(c["pesos"][estacao] for c in t["climas"]) == 100
    for area in areas:
        assert sum(x["pesos"][area] for x in t["tipos"]) == 100
    for tipo in t["tipos"]:
        assert len(t["eventos"][tipo["nome"]]) == 6
    # Toda categoria pedida por um tipo tem criatura possível em qualquer área, período e terreno.
    for categoria in {x["categoria"] for x in t["tipos"] if x["categoria"]}:
        candidatas = [c for c in t["criaturas"] if c["categoria"] == categoria]
        for area in areas:
            for periodo in t["atividade"]["Qualquer"]:
                for terreno in (x["id"] for x in t["terrenos"]):
                    assert sum(viagem.peso_da_criatura(t, c, area, periodo, terreno) for c in candidatas) > 0


@pytest.mark.parametrize("categoria", [c["id"] for c in viagem.categorias()])
def test_fichas_do_bestiario_existem(categoria):
    for criatura in viagem.tabelas(categoria)["criaturas"]:
        if criatura["bestiario_id"]:
            assert bestiario.ficha(criatura["bestiario_id"]) is not None, criatura["nome"]


def test_dia_da_simulacao():
    # Os mesmos dados da simulação feita na conversa: noite com neblina, nekkers.
    r = viagem.rolar("fantasia", SITUACAO, {"clima": 80, "evento": 11, "tipo": 71, "qual": 5, "criatura": 30, "intensidade": 4})
    assert [e["id"] for e in r["etapas"]] == ["clima", "evento", "tipo", "qual", "criatura", "intensidade"]
    assert r["clima"]["nome"] == "Neblina"
    assert r["acontece"]  # 11 + 2 (noite) + 1 (fogueira) + 2 (neblina) = 16 ≥ 14
    assert r["tipo"] == "Monstro"  # 71 + 10 + 10 = 91
    assert r["evento"]["nome"] == "Ataque da água ou do mato"
    assert r["criatura"]["nome"] == "Nekkers"
    assert r["intensidade"]["nome"] == "Encontro padrão"
    assert r["combate"]
    assert all(e["informado"] for e in r["etapas"])


def test_nada_acontece_para_na_segunda_etapa():
    r = viagem.rolar("fantasia", {**SITUACAO, "periodo": "Manhã", "situacao": "Na estrada"}, {"clima": 62, "evento": 13})
    assert r["clima"]["nome"] == "Chuva forte"
    assert not r["acontece"]  # 13 - 2 (manhã) - 1 (chuva) = 10 < 14
    assert [e["id"] for e in r["etapas"]] == ["clima", "evento"]
    assert r["narrar"][-1]["rotulo"] == "Cena"


def test_pista_mostra_quem_deixou_o_sinal_sem_intensidade():
    r = viagem.rolar("fantasia", {**SITUACAO, "periodo": "Madrugada"},
                     {"mudanca_clima": 2, "evento": 9, "tipo": 40, "qual": 2, "criatura": 88}, clima_atual="Neblina")
    assert r["etapas"][0]["id"] == "mudanca_clima" and r["clima"]["nome"] == "Neblina"
    assert r["tipo"] == "Pista / presságio"  # 40 + 15 + 10 = 65
    assert r["criatura"]["nome"] == "Lobisomem"
    assert r["intensidade"] is None and not r["combate"]


def test_clima_muda_no_seis_e_aviso_de_segundo_combate():
    r = viagem.rolar("fantasia", SITUACAO, {"mudanca_clima": 6, "clima": 5, "evento": 20, "tipo": 95, "intensidade": 6},
                     clima_atual="Neblina", combate_hoje=True, rng=random.Random(1))
    assert [e["id"] for e in r["etapas"]][:2] == ["mudanca_clima", "clima"]
    assert r["clima"]["nome"] == "Céu limpo"
    assert r["combate"] and r["avisos"]


def test_sorteio_com_semente_e_dados_invalidos():
    a = viagem.rolar("fantasia", SITUACAO, rng=random.Random(7))
    b = viagem.rolar("fantasia", SITUACAO, rng=random.Random(7))
    assert a == b
    with pytest.raises(ValueError):
        viagem.rolar("fantasia", SITUACAO, {"evento": 21})
    with pytest.raises(ValueError):
        viagem.rolar("fantasia", {**SITUACAO, "area": "Inexistente"})


def test_rotas_da_api():
    cliente = app.app.test_client()
    assert cliente.get("/api/viagem").get_json()["categorias"][0]["id"] == "fantasia"
    opcoes = cliente.get("/api/viagem/fantasia").get_json()
    assert [a["id"] for a in opcoes["areas"]] == ["Tranquila", "Média", "Perigosa", "Mortal"]
    assert cliente.get("/api/viagem/faroeste").status_code == 404
    resposta = cliente.post("/api/viagem/rolar", json={"categoria": "fantasia", "situacao": SITUACAO,
                                                       "dados": {"evento": 1, "clima": 1}})
    assert resposta.status_code == 200 and resposta.get_json()["acontece"] is False
    assert cliente.post("/api/viagem/rolar", json={"categoria": "fantasia", "situacao": {}}).status_code == 400
    assert cliente.post("/api/viagem/rolar", json={"categoria": "faroeste", "situacao": SITUACAO}).status_code == 400
    assert 'data-aba="viagem"' in cliente.get("/?genero=fantasia").get_data(as_text=True)
