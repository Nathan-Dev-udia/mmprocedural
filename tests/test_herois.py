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


TRADUZIDAS = ["dc/volume1/aquaman", "dc/volume1/batman", "dc/volume1/green_arrow_oliver_queen",
              "dc/volume1/green_lantern_hal_jordan", "dc/volume1/the_flash_barry_allen", "dc/volume2/martian_manhunter",
              "dc/volume2/superman", "dc/volume2/wonder_woman"]


def test_fichas_traduzidas_substituem_o_texto_extraido():
    for ficha_id in TRADUZIDAS:
        ficha = herois.ficha(ficha_id)
        assert ficha["status"] == "Ficha publicada, conferida com o livro e traduzida", ficha_id
        custos = herois.traducao(ficha_id)["ficha"]["custos"]
        assert sum(custos.values()) == ficha["pp"], ficha_id
    aquaman = herois.ficha("dc/volume1/aquaman")
    poderes = next(s for s in aquaman["secoes"] if s["titulo"] == "Poderes")["itens"]
    assert poderes[0].startswith("Aquático: Imunidade 3 (Frio, Afogamento, Pressão)")
    assert "Desarmado +13, corpo a corpo, Dano 10" in next(s for s in aquaman["secoes"] if s["titulo"] == "Ataques")["itens"]
    mulher = next(h for h in herois.lista() if h["id"] == "dc/volume2/wonder_woman")
    assert mulher["nome_pt"] == "Mulher-Maravilha" and mulher["pp"] == 273 and "Laço Mágico" in mulher["termos"]


def test_pdf_usa_a_ficha_traduzida():
    from nucleo import herois_pdf
    for ficha_id in TRADUZIDAS:
        assert herois_pdf.gerar_pdf(app.Path(app.__file__).parent / "dados" / "comum" / "ficha_editavel.pdf", ficha_id)
    hal = herois_pdf.campos_do_heroi("dc/volume1/green_lantern_hal_jordan")
    assert hal["Herói"] == "Lanterna Verde (Hal Jordan)" and hal["Ataque 1"] == "Anel de Poder +10"
    assert hal["Dano 1"] == "18" and hal["Vontade"] == "18" and hal["Total"] == "222" and hal["Iniciativa"] == "+2"
    flash = herois_pdf.campos_do_heroi("dc/volume1/the_flash_barry_allen")
    assert flash["Ataque 2"] == "Redemoinho" and flash["Descrição 2"] == "Área de Explosão, agarrar, CD 20 de Esquiva"


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


def test_pdf_preenche_ficha_da_marvel_e_da_dc():
    from nucleo import herois_pdf
    beast = herois_pdf.campos_do_heroi("marvel/beast")
    assert beast["Herói"] in ("Beast", "Fera") and beast["Força"] == "6" and beast["Esquiva"] == "9"
    assert beast["AcrobPer"] == "12" and beast["Total"] == "183"
    adam = herois_pdf.campos_do_heroi("dc/volume1/adam_strange")
    assert adam["Luta"] == "3" and adam["Iniciativa"] == "+6" and adam["Resistência"] == "6"
    assert adam["AcrobTotal"] == "10" and adam["AcrobPer"] == "4"
    assert adam["Ataque 1"] == "Ray Guns +13" and adam["Dano 1"] == "7" and adam["Total"] == "150"
    assert herois_pdf.campos_do_heroi("dc/nao/existe") is None


def test_pdf_de_todas_as_fichas_e_gerado():
    from nucleo import herois_pdf
    for h in herois.lista():
        assert herois_pdf.campos_do_heroi(h["id"])["Herói"], h["id"]


def test_rota_do_pdf_do_heroi():
    resposta = app.app.test_client().get("/herois/marvel/beast.pdf")
    assert resposta.status_code == 200 and resposta.data.startswith(b"%PDF")
    assert app.app.test_client().get("/herois/dc/x/y.pdf").status_code == 404


def test_pdf_ajustes_da_conferencia():
    from nucleo import herois_pdf
    iron = herois_pdf.campos_do_heroi("marvel/iron_fist")
    assert iron["Habilidades"] == "70" and iron["Iniciativa"] == "+12"
    assert "≤" not in herois_pdf._compativel_com_a_fonte(iron["Notas & Condições"])
    comet = herois_pdf.campos_do_heroi("dc/volume1/captain_comet")
    assert comet["Ataque 1"] == "Unarmed +11"
    block = herois_pdf.campos_do_heroi("dc/volume1/blockbuster_roland_desmond")
    assert block["Descrição 1"] == "Corpo a corpo, crítico 16-20" and block["Complicações 1"] == "for His Own Good"
    dwarf = herois_pdf.campos_do_heroi("dc/volume2/dwarfstar")
    assert dwarf["Ataque 2"] == "Throwing Knife +10" and dwarf["Descrição 2"] == "À distância, crítico 19-20"
