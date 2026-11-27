"""Companheiros (pets): a ficha calculada pelo programa tem de bater com o Guia do Mestre de Jogo."""

import zipfile

import pytest

from nucleo import companheiros

TODOS = companheiros.lista()


def test_ha_companheiros_cadastrados():
    assert {c["id"] for c in TODOS} >= {"cao", "cavalo", "coruja", "lobo"}


@pytest.mark.parametrize("pet", TODOS, ids=lambda c: c["id"])
def test_ficha_bate_com_o_livro(pet):
    # "livro": valores impressos no Guia; "esperado": conta feita à mão para os derivados (regra da casa).
    rel = companheiros.relatorio(pet)
    livro, valores = pet.get("livro") or pet["esperado"], rel["valores"]
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
    for campo in ("id", "nome", "nivel_poder", "generos", "descricao", "fonte", "ficha"):
        assert pet.get(campo) not in (None, "", []), f"{pet.get('id')}: falta {campo}"
    assert pet.get("livro") or pet.get("esperado"), f"{pet['id']}: falta o bloco livro (Guia) ou esperado (derivado)"
    # Sem os números impressos no Guia, a ficha é nossa: a fonte tem de dizer que é regra da casa.
    assert ("livro" in pet) != ("regra da casa" in pet["fonte"]), f"{pet['id']}: ficha da casa tem de dizer na fonte"


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
    assert pj["companheiros"] == []


def test_animal_comprado_custa_dinheiro_e_nenhum_pp(fantasia):
    sem, com = _pj(fantasia), _pj(fantasia, "cavalo")
    assert com["companheiros"][0]["id"] == "cavalo" and com["companheiros"][0]["custo_pp"] == 0
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
    assert set(fantasia) == {"cao", "cavalo", "cavalo_guerra", "mula", "ponei"} and fantasia["cavalo"]["preco"] == 75
    assert fantasia["mula"]["item"] == "burro" and fantasia["cavalo_guerra"]["np"] == 4
    assert app.opcoes_da_interface(data_loader.carregar_genero("cthulhu"))["jogador"]["companheiros"] == []
    escola = app.opcoes_da_interface(data_loader.carregar_genero("escola_de_magia"))["jogador"]["companheiros"]
    assert [c["id"] for c in escola] == ["coruja"]


def test_ficha_do_companheiro_sai_em_pdf_proprio_e_no_docx_e_txt():
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3, "companheiro": "cavalo"}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    assert pj["companheiros"][0]["nome"] == "Cavalo" and "COMPANHEIRO: Cavalo" in pj["companheiro_texto"]

    # A ficha do personagem não leva o animal; ele tem um PDF próprio, de uma página.
    paginas = PdfReader(io.BytesIO(cliente.post("/api/ficha.pdf", json={"npc": pj}).data)).pages
    assert "COMPANHEIRO" not in "".join(p.extract_text() for p in paginas)
    assert "REFERÊNCIA DO PERSONAGEM" in paginas[2].extract_text()
    resposta = cliente.post("/api/companheiro.pdf", json={"npc": pj, "id": "cavalo"})
    assert resposta.status_code == 200 and "_cavalo.pdf" in resposta.headers["Content-Disposition"]
    so_o_animal = PdfReader(io.BytesIO(resposta.data)).pages
    assert len(so_o_animal) == 1 and "COMPANHEIRO" in so_o_animal[0].extract_text()
    assert "Cavalo" in so_o_animal[0].extract_text()

    doc = Document(io.BytesIO(cliente.post("/api/ficha.docx", json={"npc": pj}).data))
    assert any(p.text == "Companheiro: Cavalo" for p in doc.paragraphs)

    pacote = zipfile.ZipFile(io.BytesIO(cliente.post("/api/fichas.zip", json={"npcs": [pj]}).data))
    assert "COMPANHEIRO: Cavalo" in pacote.read("todas_as_fichas.txt").decode("utf-8")
    assert any(n.startswith("pdf/") and n.endswith("_cavalo.pdf") for n in pacote.namelist())


def test_servidor_refaz_a_ficha_do_companheiro_pelo_id():
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3, "companheiro": "cavalo"}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    pj["companheiros"][0].update({"nome": "Dragão Falso", "id": "cavalo"})   # o nome vindo da página não vale
    doc = Document(io.BytesIO(cliente.post("/api/ficha.docx", json={"npc": pj}).data))
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert "Companheiro: Cavalo" in texto and "Dragão Falso" not in texto


def test_pedido_sem_companheiro_continua_sem_pagina_extra():
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    assert pj["companheiros"] == [] and pj["companheiro_texto"] == ""
    paginas = PdfReader(io.BytesIO(cliente.post("/api/ficha.pdf", json={"npc": pj}).data)).pages
    assert "COMPANHEIRO" not in "".join(p.extract_text() for p in paginas)
    assert cliente.post("/api/companheiro.pdf", json={"npc": pj}).status_code == 400


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
    assert com["companheiros"][0]["defesas"]["Resistência"] == sem["companheiros"][0]["defesas"]["Resistência"] + 3
    assert com["companheiros"][0]["equipamento"][0]["nome"] == "Barda de cota de malha"
    # A barda não protege o cavaleiro, e o peso dela vai no cavalo.
    assert com["validacao"]["valores"]["defesas"]["Resistência"] == sem["validacao"]["valores"]["defesas"]["Resistência"]
    assert com["validacao"]["valores"]["carga"]["na_montaria"] == sem["validacao"]["valores"]["carga"]["na_montaria"] + 55
    # O servidor refaz a ficha do companheiro com a barda do equipamento.
    doc = Document(io.BytesIO(app.app.test_client().post("/api/ficha.docx", json={"npc": {**com, "genero": "fantasia"}}).data))
    assert any(p.text.startswith("Barda de cota de malha: Proteção 3") for p in doc.paragraphs)


# ---------------------------------------------------------------- etapa 4: o animal que vem com os itens

def test_cavalo_do_kit_ganha_a_pagina():
    # No Faroeste, o kit do pistoleiro já compra o cavalo; sem pedir nada no passo Companheiro, ele ganha a ficha.
    faroeste = data_loader.carregar_genero("faroeste")
    arq = faroeste["jogador"]["arquetipos"]["pistoleiro"]
    pj = player.gerar_personagem(faroeste, "pistoleiro", 5, arq["focos"][0]["id"], "classe_media", COMPLICACOES,
                                 rng=random.Random(1))
    assert "cavalo" in pj["ficha"]["equipamento"]
    assert [(c["id"], c["origem"], c["custo_pp"]) for c in pj["companheiros"]] == [("cavalo", "equipamento", 0)]
    assert "Companheiro: Cavalo" in pj["faixa"]["observacao"]


def test_todo_animal_com_ficha_no_equipamento_tem_pagina():
    # Em todos os gêneros com animais à venda: se o item do animal está no equipamento, a ficha dele vem junto.
    for genero in ("fantasia", "faroeste", "escola_de_magia"):
        dados = data_loader.carregar_genero(genero)
        itens_dos_animais = {companheiros.item_de_compra(c, genero): c["id"] for c in companheiros.lista()
                             if companheiros.item_de_compra(c, genero)}
        riqueza = dados["jogador"]["riqueza"][-1]["id"]
        for arquetipo, arq in dados["jogador"]["arquetipos"].items():
            pj = player.gerar_personagem(dados, arquetipo, 5, arq["focos"][0]["id"], riqueza, COMPLICACOES,
                                         rng=random.Random(2))
            esperados = [itens_dos_animais[i] for i in dict.fromkeys(pj["ficha"]["equipamento"]) if i in itens_dos_animais]
            assert [c["id"] for c in pj["companheiros"]] == esperados, (genero, arquetipo)


def test_animal_marcado_em_escolher_ganha_a_pagina(fantasia):
    pj = _pj(fantasia, equipamento={"modo": "manual", "ids": ["espada_longa", "mastim"], "excesso": "divida"})
    assert [(c["id"], c["origem"]) for c in pj["companheiros"]] == [("cao", "equipamento")]


def test_cao_escolhido_e_cavalo_do_kit(fantasia):
    pj = _pj(fantasia, "cao", equipamento={"modo": "manual", "ids": ["cavalo_montaria", "barda_couro"],
                                           "excesso": "divida"})
    cao, cavalo = pj["companheiros"]
    assert (cao["id"], cao["origem"]) == ("cao", "passo") and (cavalo["id"], cavalo["origem"]) == ("cavalo", "equipamento")
    assert cao["equipamento"] == [] and cavalo["equipamento"][0]["nome"].startswith("Barda")   # a barda vai no cavalo
    assert "Companheiros: Cão (animal comprado, sem custo em PP), Cavalo (animal comprado" in pj["faixa"]["observacao"]

    cliente = app.app.test_client()
    pj["genero"] = "fantasia"
    for animal, nome in (("cao", "Cão"), ("cavalo", "Cavalo")):
        pdf = PdfReader(io.BytesIO(cliente.post("/api/companheiro.pdf", json={"npc": pj, "id": animal}).data))
        assert "COMPANHEIRO" in pdf.pages[0].extract_text() and nome in pdf.pages[0].extract_text()
    assert cliente.post("/api/companheiro.pdf", json={"npc": pj, "id": "lobo"}).status_code == 400
    doc = Document(io.BytesIO(cliente.post("/api/ficha.docx", json={"npc": pj}).data))
    titulos = [p.text for p in doc.paragraphs if p.text.startswith("Companheiro: ")]
    assert titulos == ["Companheiro: Cão", "Companheiro: Cavalo"]


def test_ficha_antiga_com_um_companheiro_so():
    # Fichas geradas antes desta versão mandam "companheiro" (um só); o download continua funcionando.
    cliente = app.app.test_client()
    pedido = {"genero": "fantasia", "arquetipo": "guerreiro", "foco": "campeao", "np": 5, "riqueza": "classe_media",
              "complicacoes": COMPLICACOES, "semente": 3, "companheiro": "cavalo"}
    pj = cliente.post("/api/jogador/gerar", json=pedido).get_json()["personagem"]
    pj["companheiro"] = pj.pop("companheiros")[0]
    doc = Document(io.BytesIO(cliente.post("/api/ficha.docx", json={"npc": pj}).data))
    assert any(p.text == "Companheiro: Cavalo" for p in doc.paragraphs)


# ---------------------------------------------------------------- etapa 3: Parceiro (custa PP)

def test_parceiro_custa_pp_pela_regra_do_livro(fantasia):
    # Livro Básico, vantagem Parceiro: 5 PP de ficha por graduação. O lobo tem 23 PP: Parceiro 5.
    sem = _pj(fantasia)
    for semente in range(4):
        pj = player.gerar_personagem(fantasia, "guerreiro", 5, fantasia["jogador"]["arquetipos"]["guerreiro"]["focos"][0]["id"],
                                     "classe_media", COMPLICACOES, rng=random.Random(semente), parceiro="lobo")
        assert pj["ficha"]["vantagens"]["Parceiro"] == 5                    # o gerador não sobe a graduação
        assert pj["validacao"]["total_pp"] == sem["validacao"]["total_pp"] == 75   # sai do orçamento, não soma
        assert pj["validacao"]["problemas"] == []
        lobo = pj["companheiros"][-1]
        assert (lobo["id"], lobo["origem"], lobo["custo_pp"]) == ("lobo", "parceiro", 5)
        assert lobo["posse"] == "Parceiro, 5 graduações" and lobo["total_pp"] < pj["validacao"]["total_pp"]
    assert "Lobo (Parceiro, 5 PP)" in pj["faixa"]["observacao"]


def test_parceiro_precisa_caber_no_np(fantasia):
    with pytest.raises(player.GeneratorError, match="precisa caber no NP"):
        player.gerar_personagem(fantasia, "guerreiro", 3, fantasia["jogador"]["arquetipos"]["guerreiro"]["focos"][0]["id"],
                                "classe_media", COMPLICACOES, rng=random.Random(1), parceiro="cavalo_guerra")
    faroeste = data_loader.carregar_genero("faroeste")
    foco = faroeste["jogador"]["arquetipos"]["pistoleiro"]["focos"][0]["id"]
    with pytest.raises(player.GeneratorError, match="não pode ser Parceiro"):
        player.gerar_personagem(faroeste, "pistoleiro", 5, foco, "classe_media", COMPLICACOES,
                                rng=random.Random(1), parceiro="coruja")        # a coruja não é do Faroeste


def test_parceiros_da_tela():
    fantasia = {p["id"]: p for p in app.opcoes_da_interface(data_loader.carregar_genero("fantasia"))["jogador"]["parceiros"]}
    assert fantasia["lobo"] == {**fantasia["lobo"], "np": 3, "total_pp": 23, "graduacao": 5}
    assert fantasia["ponei"]["graduacao"] == 1 and fantasia["cavalo_guerra"]["graduacao"] == 3
    # Cthulhu não vende animais, mas o cão pode ser Parceiro.
    cthulhu = app.opcoes_da_interface(data_loader.carregar_genero("cthulhu"))["jogador"]
    assert cthulhu["companheiros"] == [] and [p["id"] for p in cthulhu["parceiros"]] == ["cao"]


def test_cavalo_comprado_e_cavalo_parceiro_tem_pdfs_separados(fantasia):
    pj = player.gerar_personagem(fantasia, "guerreiro", 5, fantasia["jogador"]["arquetipos"]["guerreiro"]["focos"][0]["id"],
                                 "em_ascensao", COMPLICACOES, rng=random.Random(3), companheiro="cavalo", parceiro="cavalo")
    assert [(c["id"], c["origem"]) for c in pj["companheiros"]] == [("cavalo", "passo"), ("cavalo", "parceiro")]
    pj["genero"] = "fantasia"
    cliente = app.app.test_client()
    resposta = cliente.post("/api/companheiro.pdf", json={"npc": pj, "id": "cavalo", "parceiro": True})
    assert resposta.status_code == 200 and "_cavalo_parceiro.pdf" in resposta.headers["Content-Disposition"]
    assert "Parceiro" in PdfReader(io.BytesIO(resposta.data)).pages[0].extract_text()
    comprado = cliente.post("/api/companheiro.pdf", json={"npc": pj, "id": "cavalo"})
    assert "_cavalo.pdf" in comprado.headers["Content-Disposition"]
    pacote = zipfile.ZipFile(io.BytesIO(cliente.post("/api/fichas.zip", json={"npcs": [pj]}).data))
    nomes = [n for n in pacote.namelist() if "cavalo" in n]
    assert len(nomes) == 2 and any(n.endswith("_cavalo_parceiro.pdf") for n in nomes)


def test_parceiro_pelo_servidor():
    cliente = app.app.test_client()
    pedido = {"genero": "cthulhu", "np": 3, "riqueza": "classe_media", "complicacoes": COMPLICACOES, "semente": 2,
              "parceiro": "cao"}
    dados = data_loader.carregar_genero("cthulhu")
    arq = next(iter(dados["jogador"]["arquetipos"].values()))
    pedido.update(arquetipo=arq["id"], foco=arq["focos"][0]["id"])
    resposta = cliente.post("/api/jogador/gerar", json=pedido).get_json()
    pj = resposta["personagem"]
    assert pj["ficha"]["vantagens"]["Parceiro"] == 2 and "COMPANHEIRO: Cão" in pj["companheiro_texto"]


# ---------------------------------------------------------------- etapa 5: a criatura do poder de Invocar

def _da_subclasse(dados, foco_id, np, **extra):
    arquetipo = next(a for a in dados["jogador"]["arquetipos"].values() if any(f["id"] == foco_id for f in a["focos"]))
    return player.gerar_personagem(dados, arquetipo["id"], np, foco_id, "classe_media", COMPLICACOES,
                                   rng=random.Random(1), **extra)


@pytest.mark.parametrize("foco, criatura", [("mestre_feras", "lobo"), ("invocacao", "elemental_menor"),
                                            ("ferreiro_batalha", "defensor_de_aco")])
def test_subclasse_com_invocar_traz_a_ficha_da_criatura(fantasia, foco, criatura):
    pj = _da_subclasse(fantasia, foco, 5)
    invocados = [c for c in pj["companheiros"] if c["origem"] == "poder"]
    assert [c["id"] for c in invocados] == [criatura]
    assert invocados[0]["custo_pp"] == 6 and invocados[0]["posse"].startswith("Invocado, ")   # Invocar 2, Heroico
    assert pj["validacao"]["total_pp"] == 75                                  # já estava pago: nada muda no custo


def test_mestre_das_feras_no_np_2_tem_cao(fantasia):
    # O lobo é NP 3: abaixo disso, o Companheiro animal traz o cão (a criatura respeita o NP do dono).
    pj = _da_subclasse(fantasia, "mestre_feras", 2)
    assert [c["id"] for c in pj["companheiros"] if c["origem"] == "poder"] == ["cao"]


def test_criatura_cabe_no_invocar_e_no_np(fantasia):
    # Livro Básico, Invocar: 15 PP de criatura por graduação; capangas de PJ respeitam o NP.
    for poder_id, entrada in fantasia["poderes_do_genero"].items():
        for companheiro_id in entrada.get("companheiros", []):
            assert companheiros.carregar(companheiro_id)["nivel_poder"] >= 2, poder_id
        for np in range(2, 11):
            c = companheiros.invocado_do_poder(entrada, entrada.get("graduacao"), np) if entrada.get("companheiros") else None
            if c:
                assert c["nivel_poder"] <= np
                assert companheiros.relatorio(c)["total_pp"] <= 15 * entrada["graduacao"]


def test_homunculo_do_artifice(fantasia):
    pj = _da_subclasse(fantasia, fantasia["jogador"]["arquetipos"]["artifice"]["focos"][0]["id"], 5,
                       implantes={"modo": "manual", "ids": ["servo_homunculo"]})
    assert "homunculo" in [c["id"] for c in pj["companheiros"] if c["origem"] == "poder"]


def test_invocados_nao_viram_parceiro():
    ids = {p["id"] for p in companheiros.parceiros("fantasia")}
    assert not ids & {"elemental_menor", "defensor_de_aco", "homunculo"}


def test_pdf_do_invocado(fantasia):
    pj = _da_subclasse(fantasia, "mestre_feras", 5, parceiro="lobo")           # o lobo invocado e um lobo parceiro
    assert sorted(c["origem"] for c in pj["companheiros"] if c["id"] == "lobo") == ["parceiro", "poder"]
    pj["genero"] = "fantasia"
    cliente = app.app.test_client()
    resposta = cliente.post("/api/companheiro.pdf", json={"npc": pj, "id": "lobo", "tipo": "invocado"})
    assert resposta.status_code == 200 and "_lobo_invocado.pdf" in resposta.headers["Content-Disposition"]
    assert "Invocado" in PdfReader(io.BytesIO(resposta.data)).pages[0].extract_text()
