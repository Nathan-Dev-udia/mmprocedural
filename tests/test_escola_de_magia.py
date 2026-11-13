"""Testes do gênero Escola de Magia (Harry Potter / M&M 3e + Relacionamentos de Mecha & Mangá)."""

import io
import json
import random
from pathlib import Path

import openpyxl
from pypdf import PdfReader

import app
from nucleo import data_loader, escudo, generator, pdf_export, player, poderes as poderes_mod

MODELO_PDF = Path(__file__).resolve().parent.parent / "dados" / "comum" / "ficha_editavel.pdf"


def test_genero_e_catalogo_de_feiticos_carregam():
    assert "escola_de_magia" in data_loader.generos_disponiveis()
    dados = data_loader.carregar_genero("escola_de_magia")
    assert len(dados["poderes_do_genero"]) == 57
    for pid in dados["poderes_do_genero"]:
        resolvido = player.poder_do_genero(dados, pid, 2)
        assert resolvido["custo_informado"] is not None, pid


def test_arranjo_varinha_cobra_1_pp_por_feitico_adicional():
    dados = data_loader.carregar_genero("escola_de_magia")
    p1 = player.poder_do_genero(dados, "expelliarmus", 2)
    p2 = player.poder_do_genero(dados, "estupeca", 2)
    p3 = player.poder_do_genero(dados, "lumus", 2)
    custo_dois = poderes_mod.custo_total({"expelliarmus": p1, "estupeca": p2})
    custo_tres = poderes_mod.custo_total({"expelliarmus": p1, "estupeca": p2, "lumus": p3})
    assert custo_tres - custo_dois == 1


def test_todos_arquetipos_focos_e_casas_geram_fichas_validas():
    dados = data_loader.carregar_genero("escola_de_magia")
    casas = [r["id"] for r in player.racas(dados)]
    assert {"grifinoria", "corvinal", "lufa_lufa", "sonserina", "visitante"} <= set(casas)

    for arq in dados["jogador"]["arquetipos"].values():
        np = 2 if arq["id"] == "estudante" else 7
        for foco in arq["focos"]:
            for casa_id in casas:
                rng = random.Random(42)
                comps = player.sortear_complicacoes(dados, arq["id"], rng, foco_id=foco["id"])
                ficha = player.gerar_personagem(
                    dados, arq["id"], np,
                    foco_id=foco["id"], riqueza_id="comum",
                    complicacoes=comps, raca=casa_id, rng=rng,
                )
                v = ficha["validacao"]
                assert not v.get("problemas"), (arq["id"], foco["id"], casa_id, v["problemas"])
                assert v["total_pp"] == v["orcamento"]
                assert ficha["dinheiro"]["inicial"] > 0
                assert ficha["ficha"]["poderes"]


def test_escudo_tem_magia_e_relacionamentos_mecha_e_manga():
    dados = data_loader.carregar_genero("escola_de_magia")
    montado = escudo.montar("escola_de_magia", dados)
    assert montado["letalidade_atual"] == "heroica"
    ids_abas = [aba["id"] for aba in montado["abas"]]
    assert "magia" in ids_abas
    assert "relacionamentos" in ids_abas
    assert "quadribol" in ids_abas
    rel = next(aba for aba in montado["abas"] if aba["id"] == "relacionamentos")
    texto = str(rel)
    assert "Mecha & Mangá" in texto
    assert "1 PP" in str(next(aba for aba in montado["abas"] if aba["id"] == "magia"))
    quad = str(next(aba for aba in montado["abas"] if aba["id"] == "quadribol"))
    assert "Finta de Wronski" in quad and "Mutretar" in quad


def test_pdf_e_rotas_web_funcionam():
    dados = data_loader.carregar_genero("escola_de_magia")
    rng = random.Random(7)
    comps = player.sortear_complicacoes(dados, "estudante", rng, foco_id="duelista")
    ficha = player.gerar_personagem(
        dados, "estudante", 2, foco_id="duelista", riqueza_id="comum",
        complicacoes=comps, raca="grifinoria", rng=rng,
    )
    pdf_bytes = pdf_export.gerar_pdf(str(MODELO_PDF), ficha, ficha["validacao"], "Escola de Magia")
    leitor = PdfReader(io.BytesIO(pdf_bytes))
    assert len(leitor.pages) >= 2

    cliente = app.app.test_client()
    pagina = cliente.get("/?genero=escola_de_magia")
    assert pagina.status_code == 200
    assert "Escola de Magia" in pagina.get_data(as_text=True)
    assert cliente.get("/escudo/escola_de_magia.pdf").status_code == 200
    assert cliente.get("/escudo/escola_de_magia.xlsx").status_code == 200
    assert cliente.get("/livros/escola_de_magia/jogador.docx").status_code == 200
    assert cliente.get("/livros/escola_de_magia/mestre.docx").status_code == 200


def test_feiticos_utilitarios_nao_geram_ataques_falsos_e_imperdoaveis_ocultas():
    dados = data_loader.carregar_genero("escola_de_magia")
    ids_jogador = {p["id"] for p in player.implantes_do_jogador(dados)}
    assert not ({"avada_kedavra", "crucio", "imperio"} & ids_jogador)

    rng = random.Random(10)
    comps = player.sortear_complicacoes(dados, "estudante", rng, foco_id="duelista")
    ficha = player.gerar_personagem(
        dados, "estudante", 2, foco_id="duelista", riqueza_id="comum",
        complicacoes=comps, raca="grifinoria", rng=rng,
    )
    ataques_poderes = [
        p["nome"] for p in ficha["ficha"]["poderes"].values() if p.get("ataque")
    ]
    assert not any("Lumus" in n or "Colloportus" in n for n in ataques_poderes)


def test_todos_os_arquetipos_de_npc_e_modulos_geram_grupos_validos():
    dados = data_loader.carregar_genero("escola_de_magia")
    assert set(dados["arquetipos"].keys()) == {
        "estudante_rival", "monitor_escolar", "bruxo_das_trevas", "auror_patrulha"
    }
    for arq_id, arq in dados["arquetipos"].items():
        np_min = min(f["np"] for f in arq["faixas"])
        for np in range(np_min, arq["np_maximo"] + 1):
            for estilo_id in dados["estilos"].keys():
                grupo = generator.gerar_grupo(dados, arq_id, np, estilo_id, 2, random.Random(1))
                assert len(grupo["npcs"]) == 2, (arq_id, np, estilo_id, grupo.get("aviso"))
                for npc in grupo["npcs"]:
                    assert not npc["validacao"].get("problemas"), (arq_id, np, estilo_id, npc["validacao"]["problemas"])


def test_planilhas_de_escola_de_magia_itens_poderes_armas_e_pocoes():
    dados = data_loader.carregar_genero("escola_de_magia")
    cliente = app.app.test_client()

    pagina = cliente.get("/?genero=escola_de_magia").get_data(as_text=True)
    for tipo in ("armas", "itens", "poderes", "pocoes"):
        assert f"/planilhas/escola_de_magia/{tipo}.xlsx" in pagina
        resp = cliente.get(f"/planilhas/escola_de_magia/{tipo}.xlsx")
        assert resp.status_code == 200
        assert resp.mimetype == app.MIME_XLSX
        assert resp.headers["Content-Disposition"].endswith(f"{tipo}_escola_de_magia.xlsx")

    # Todo item do catálogo tem comércio e aparece em armas.xlsx ou itens.xlsx + na aba "Por comércio"
    assert all(i.get("comercio") for i in player.catalogo_do_jogador(dados))
    wb_itens = openpyxl.load_workbook(io.BytesIO(cliente.get("/planilhas/escola_de_magia/itens.xlsx").data))
    wb_armas = openpyxl.load_workbook(io.BytesIO(cliente.get("/planilhas/escola_de_magia/armas.xlsx").data))
    wb_poderes = openpyxl.load_workbook(io.BytesIO(cliente.get("/planilhas/escola_de_magia/poderes.xlsx").data))
    wb_pocoes = openpyxl.load_workbook(io.BytesIO(cliente.get("/planilhas/escola_de_magia/pocoes.xlsx").data))

    nomes_itens = {r[1] for r in wb_itens["Itens"].iter_rows(min_row=2, values_only=True)}
    nomes_armas = {r[0] for r in wb_armas["Varinhas e armas"].iter_rows(min_row=2, values_only=True)}
    assert nomes_itens | nomes_armas == {i["nome"] for i in player.catalogo_do_jogador(dados)}
    assert len(list(wb_itens["Por comércio"].iter_rows(min_row=2, values_only=True))) == len(player.catalogo_do_jogador(dados))
    assert len(list(wb_poderes["Poderes"].iter_rows(min_row=2, values_only=True))) == len(dados["poderes_do_genero"])

    # Sincronia de pocoes.xlsx / alquimia.json com equipment.json
    assert {"Regras e Preparo", "Poções e Elixires", "Plantas e Ingredientes", "Hogsmeade e Serviços"} <= set(wb_pocoes.sheetnames)
    alquimia = json.loads(Path("dados/generos/escola_de_magia/alquimia.json").read_text(encoding="utf-8"))
    equipamentos = dados["equipamentos"]
    for receita in alquimia["pocoes"] + alquimia["ingredientes"]:
        item = equipamentos[receita["id"]]
        assert receita["nome"] == item["nome"]
        assert receita["preco"] == f"{item['preco']} G"
        assert receita["peso"] == item["peso"] > 0
        assert item["comercio"] == "Boticário"
