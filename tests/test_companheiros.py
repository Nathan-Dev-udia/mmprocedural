"""Companheiros (pets): a ficha calculada pelo programa tem de bater com o Guia do Mestre de Jogo."""

import zipfile

import pytest

from nucleo import companheiros

TODOS = companheiros.lista()


def test_ha_companheiros_cadastrados():
    assert {c["id"] for c in TODOS} >= {"cao", "cavalo", "coruja", "lobo"}


@pytest.mark.parametrize("pet", TODOS, ids=lambda c: c["id"])
def test_ficha_bate_com_o_livro(pet):
    rel = companheiros.relatorio(pet)
    livro, valores = pet["livro"], rel["valores"]
    assert valores["habilidades"] == livro["habilidades"]
    assert {d: valores["defesas"][d] for d in livro["defesas"]} == livro["defesas"]
    assert {p: valores["pericias"][p]["total"] for p in livro["pericias"]} == livro["pericias"]
    assert valores["iniciativa"] == livro["iniciativa"]
    ataques = {a["nome"]: {"bonus": a["bonus"], "dano": a["dano"]} for a in valores["ataques"]}
    assert ataques == livro["ataques"]
    assert rel["custos"] == livro["custos"]
    assert rel["total_pp"] == livro["total"]


@pytest.mark.parametrize("pet", TODOS, ids=lambda c: c["id"])
def test_ficha_cabe_no_np(pet):
    rel = companheiros.relatorio(pet)
    assert rel["problemas"] == []


@pytest.mark.parametrize("pet", TODOS, ids=lambda c: c["id"])
def test_campos_obrigatorios(pet):
    for campo in ("id", "nome", "nivel_poder", "generos", "descricao", "fonte", "ficha", "livro"):
        assert pet.get(campo) not in (None, "", []), f"{pet.get('id')}: falta {campo}"


def test_custo_para_o_heroi():
    # Parceiro: 5 PP de ficha por graduação; Capanga: 15 (livro básico, p. 85 e 81). Arredonda para cima.
    assert companheiros.custo_para_o_heroi(companheiros.carregar("cao")) == {"total": 10, "parceiro": 2, "capanga": 1}
    assert companheiros.custo_para_o_heroi(companheiros.carregar("lobo")) == {"total": 23, "parceiro": 5, "capanga": 2}
    assert companheiros.graduacao_da_vantagem(0, "parceiro") == 1


def test_efeitos_de_tamanho_do_livro_basico():
    # Exemplos do próprio livro: Crescimento 8 e Encolhimento 12.
    assert companheiros.efeitos_de_tamanho("Crescimento", 8) == (
        {"For": 8, "Vig": 8, "Esquiva": -4, "Aparar": -4}, {"Furtividade": -8, "Intimidação": 4})
    assert companheiros.efeitos_de_tamanho("Encolhimento", 12) == (
        {"For": -3, "Esquiva": 6, "Aparar": 6}, {"Furtividade": 12, "Intimidação": -6})


def test_lista_por_genero():
    assert {c["id"] for c in companheiros.lista("escola_de_magia")} == {"coruja"}
    assert "cavalo" in {c["id"] for c in companheiros.lista("faroeste")}


# ---------------------------------------------------------------- animal comprado (passo "Companheiro")

import io
import random

from docx import Document
from pypdf import PdfReader

import app
from nucleo import data_loader, player

COMPLICACOES = [{"categoria": "motivacao", "nome": "Fé", "detalhe": ""},
                {"categoria": "complicacao", "nome": "Honra", "detalhe": "Nunca quebra a palavra dada."}]


@pytest.fixture(scope="module")
def fantasia():
    return data_loader.carregar_genero("fantasia")


def _pj(dados, companheiro=None, riqueza="classe_media", equipamento=None, semente=3, arquetipo="guerreiro"):
    foco = dados["jogador"]["arquetipos"][arquetipo]["focos"][0]["id"]
    return player.gerar_personagem(dados, arquetipo, 5, foco, riqueza, COMPLICACOES, rng=random.Random(semente),
                                   companheiro=companheiro, equipamento=equipamento)


def test_sem_pedido_nao_ha_companheiro(fantasia):
    pj = _pj(fantasia)
    assert pj["companheiro"] is None


def test_animal_comprado_custa_dinheiro_e_nenhum_pp(fantasia):
    sem, com = _pj(fantasia), _pj(fantasia, "cavalo")
    assert com["companheiro"]["id"] == "cavalo" and com["companheiro"]["custo_pp"] == 0
    assert com["validacao"]["total_pp"] == sem["validacao"]["total_pp"] == 75     # o orçamento do NP 5 não muda
    compras = com["dinheiro"]["compras"]
    assert compras[0]["id"] == "cavalo_montaria" and compras[0]["preco"] == 75   # é o primeiro item pago
    assert "cavalo_montaria" in com["ficha"]["equipamento"]
    din = com["dinheiro"]
    assert din["inicial"] - din["restante"] == din["gasto"] and din["gasto"] >= 75


def test_animal_comprado_nao_duplica_item_escolhido(fantasia):
    equip = {"modo": "manual", "ids": ["cavalo_montaria", "sela"], "excesso": "divida"}
    pj = _pj(fantasia, "cavalo", equipamento=equip)
    assert pj["ficha"]["equipamento"].count("cavalo_montaria") == 1
    so_o_animal = _pj(fantasia, "cao", equipamento={"modo": "manual", "ids": [], "excesso": "divida"})
    assert so_o_animal["ficha"]["equipamento"] == ["mastim"]


def test_animal_pedido_e_mesma_ficha_com_a_mesma_semente(fantasia):
    a, b = _pj(fantasia, "cavalo"), _pj(fantasia, "cavalo")
    assert a["ficha"] == b["ficha"] and a["dinheiro"] == b["dinheiro"]


def test_animal_que_nao_esta_a_venda_no_genero(fantasia):
    with pytest.raises(player.GeneratorError, match="não está à venda"):
        _pj(fantasia, "coruja")                       # a coruja só se vende na Escola de Magia
    with pytest.raises(player.GeneratorError, match="não está à venda"):
        _pj(fantasia, "dragao")
    cthulhu = data_loader.carregar_genero("cthulhu")
    foco = next(iter(cthulhu["jogador"]["arquetipos"].values()))
    with pytest.raises(player.GeneratorError, match="não está à venda"):
        player.gerar_personagem(cthulhu, foco["id"], 5, foco["focos"][0]["id"], "classe_media", COMPLICACOES,
                                rng=random.Random(1), companheiro="cao")


def test_sem_dinheiro_para_o_animal_da_erro(fantasia):
    with pytest.raises(player.GeneratorError, match="só tem"):
        _pj(fantasia, "cavalo", riqueza="trabalhador")     # 30 po não pagam um cavalo de 75 po


def test_opcoes_da_tela_listam_so_o_que_se_vende():
    fantasia = {c["id"]: c for c in app.opcoes_da_interface(data_loader.carregar_genero("fantasia"))
                ["jogador"]["companheiros"]}
    assert set(fantasia) == {"cao", "cavalo"} and fantasia["cavalo"]["preco"] == 75
    assert app.opcoes_da_interface(data_loader.carregar_genero("cthulhu"))["jogador"]["companheiros"] == []
    escola = app.opcoes_da_interface(data_loader.carregar_genero("escola_de_magia"))["jogador"]["companheiros"]
    assert [c["id"] for c in escola] == ["coruja"]


def test_ficha_do_companheiro_sai_no_pdf_docx_e_txt():
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3, "companheiro": "cavalo"}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    assert pj["companheiro"]["nome"] == "Cavalo" and "COMPANHEIRO: Cavalo" in pj["companheiro_texto"]

    paginas = PdfReader(io.BytesIO(cliente.post("/api/ficha.pdf", json={"npc": pj}).data)).pages
    textos = [p.extract_text() for p in paginas[2:]]
    assert "COMPANHEIRO" in textos[0] and "Cavalo" in textos[0]          # a página dele vem antes da referência
    assert "REFERÊNCIA DO PERSONAGEM" in textos[1]

    doc = Document(io.BytesIO(cliente.post("/api/ficha.docx", json={"npc": pj}).data))
    assert any(p.text == "Companheiro: Cavalo" for p in doc.paragraphs)

    pacote = zipfile.ZipFile(io.BytesIO(cliente.post("/api/fichas.zip", json={"npcs": [pj]}).data))
    assert "COMPANHEIRO: Cavalo" in pacote.read("todas_as_fichas.txt").decode("utf-8")


def test_servidor_refaz_a_ficha_do_companheiro_pelo_id():
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3, "companheiro": "cavalo"}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    pj["companheiro"].update({"nome": "Dragão Falso", "id": "cavalo"})   # o nome vindo da página não vale
    doc = Document(io.BytesIO(cliente.post("/api/ficha.docx", json={"npc": pj}).data))
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert "Companheiro: Cavalo" in texto and "Dragão Falso" not in texto


def test_pedido_sem_companheiro_continua_sem_pagina_extra():
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    assert pj["companheiro"] is None and pj["companheiro_texto"] == ""
    paginas = PdfReader(io.BytesIO(cliente.post("/api/ficha.pdf", json={"npc": pj}).data)).pages
    assert "COMPANHEIRO" not in "".join(p.extract_text() for p in paginas)


def test_poderes_e_vantagens_do_companheiro_vem_explicados():
    cavalo = companheiros.bloco(companheiros.carregar("cavalo"))
    tamanho = next(p for p in cavalo["poderes"] if p["nome"].startswith("Crescimento"))
    assert "Força +4" in tamanho["explicacao"] and "Esquiva –2" in tamanho["explicacao"]
    assert "Furtividade –4" in tamanho["explicacao"]
    for pet in TODOS:
        b = companheiros.bloco(pet)
        assert all(p["explicacao"] for p in b["poderes"] + b["vantagens"]), pet["id"]
    lobo = companheiros.bloco(companheiros.carregar("lobo"))
    assert lobo["vantagens"] == [{"nome": "Derrubar Aprimorado",
                                  "explicacao": "Sem penalidade para usar a ação derrubar."}]


def test_sorteio_nao_compra_sela_sem_animal():
    # No faroeste o trabalhador ($75) não paga o cavalo ($150): antes saía com a sela ($25) e sem cavalo.
    faroeste = data_loader.carregar_genero("faroeste")
    catalogo = faroeste["equipamentos"]
    for arquetipo, dados_arq in faroeste["jogador"]["arquetipos"].items():
        for semente in range(3):
            pj = player.gerar_personagem(faroeste, arquetipo, 5, dados_arq["focos"][0]["id"], "trabalhador",
                                         COMPLICACOES, rng=random.Random(semente))
            itens = pj["ficha"]["equipamento"]
            tem_animal = any(catalogo[i].get("carga") and catalogo[i].get("categoria") == "Transporte" for i in itens)
            assert tem_animal or not {"sela", "alforjes"} & set(itens), (arquetipo, itens)
            din = pj["dinheiro"]
            assert round(din["inicial"] - din["gasto"], 2) == din["restante"]


def test_barda_soma_na_resistencia_do_companheiro(fantasia):
    sem = _pj(fantasia, "cavalo", riqueza="em_ascensao",
              equipamento={"modo": "manual", "ids": ["couro", "sela_militar"], "excesso": "divida"})
    com = _pj(fantasia, "cavalo", riqueza="em_ascensao",
              equipamento={"modo": "manual", "ids": ["couro", "sela_militar", "barda_malha"], "excesso": "divida"})
    assert com["companheiro"]["defesas"]["Resistência"] == sem["companheiro"]["defesas"]["Resistência"] + 3
    assert com["companheiro"]["equipamento"][0]["nome"] == "Barda de cota de malha"
    # A barda não protege o cavaleiro, e o peso dela vai no cavalo.
    assert com["validacao"]["valores"]["defesas"]["Resistência"] == sem["validacao"]["valores"]["defesas"]["Resistência"]
    assert com["validacao"]["valores"]["carga"]["na_montaria"] == sem["validacao"]["valores"]["carga"]["na_montaria"] + 55
    # O servidor refaz a ficha do companheiro com a barda do equipamento.
    doc = Document(io.BytesIO(app.app.test_client().post("/api/ficha.docx", json={"npc": {**com, "genero": "fantasia"}}).data))
    assert any(p.text.startswith("Barda de cota de malha: Proteção 3") for p in doc.paragraphs)
