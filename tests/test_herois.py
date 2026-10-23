"""Heróis conhecidos: catálogo de fichas prontas da Marvel e da DC, só para consulta e download."""

import app
from nucleo import data_loader, herois


def test_herois_e_um_catalogo_fora_do_gerador():
    assert data_loader.catalogos_disponiveis() == ["herois"]
    assert "herois" not in data_loader.generos_disponiveis()
    assert "herois" not in app.DADOS_POR_GENERO


def test_catalogo_traz_as_duas_editoras():
    lista = herois.lista()
    assert sum(h["editora"] == "marvel" for h in lista) == 116
    assert sum(h["editora"] == "dc" for h in lista) == 536
    assert len({h["id"] for h in lista}) == len(lista)
    arcanjo = next(h for h in lista if h["id"] == "marvel/archangel")
    assert arcanjo["nome_pt"] == "Arcanjo" and arcanjo["np"] == 10 and "Flight" in arcanjo["termos"]


def test_ficha_da_dc_traduz_as_habilidades_e_separa_os_poderes():
    ficha = herois.ficha("dc/volume1/adam_strange")
    assert ficha["habilidades"]["Lut"] == "3" and ficha["habilidades"]["Pro"] == "4"
    poderes = next(s for s in ficha["secoes"] if s["titulo"] == "Poderes")["itens"]
    assert poderes[0] == "Jet Pack: Flight 7 (250 MPH), Removable (–3 points) (11 PP)"
    assert len(poderes) == 5
    assert "Vol. I, p. 13" in ficha["fonte"]


def test_ficha_da_marvel_traz_as_notas_de_conversao():
    ficha = herois.ficha("marvel/archangel")
    titulos = [s["titulo"] for s in ficha["secoes"]]
    assert "Poderes" in titulos and "Notas de conversão" in titulos
    assert "Desarmado +12, Dano 6" in next(s for s in ficha["secoes"] if s["titulo"] == "Ataques")["itens"]


def test_ids_invalidos_nao_saem_da_pasta():
    assert herois.ficha("../../app") is None
    assert herois.ficha("marvel/../../app") is None


def test_pagina_e_consulta():
    cliente = app.app.test_client()
    pagina = cliente.get("/?genero=herois").get_data(as_text=True)
    assert "Heróis conhecidos" in pagina and "Marvel (116)" in pagina and "DC (536)" in pagina
    assert '"herois"' in cliente.get("/?genero=fantasia").get_data(as_text=True)   # na escolha de gênero

    assert len(cliente.get("/api/herois").get_json()["herois"]) == 652
    ficha = cliente.get("/api/herois/dc/volume1/batman").get_json()["ficha"]
    assert ficha["nome"] == "Batman" and ficha["np"] == 12
    assert cliente.get("/api/herois/marvel/nao_existe").status_code == 404
    assert cliente.get("/api/herois/../app.py").status_code == 404
