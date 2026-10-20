"""Testes da ficha de personagem de jogador e da escalada dos NPCs."""

import random

import pytest

import app
from nucleo import generator
from nucleo import player
from nucleo import rules

ARQUETIPOS_PJ = ["pistoleiro", "cacador", "xerife", "fora_da_lei", "jogador", "medico", "veterano"]


def complicacoes_validas():
    return [{"categoria": "motivacao", "nome": "Justiça", "detalhe": ""},
            {"categoria": "complicacao", "nome": "Honra", "detalhe": "Nunca atira pelas costas."}]


def gerar(dados, arquetipo="pistoleiro", np=6, foco=None, riqueza="classe_media", semente=1, **extras):
    foco = foco or dados["jogador"]["arquetipos"][arquetipo]["focos"][0]["id"]
    return player.gerar_personagem(dados, arquetipo, np, foco, riqueza, extras.pop("complicacoes", complicacoes_validas()),
                                   rng=random.Random(semente), **extras)


@pytest.mark.parametrize("arquetipo", ARQUETIPOS_PJ)
@pytest.mark.parametrize("np", [2, 4, 6, 8, 10])
def test_gasta_exatamente_o_orcamento(dados, arquetipo, np):
    for foco in dados["jogador"]["arquetipos"][arquetipo]["focos"]:
        pj = gerar(dados, arquetipo, np, foco["id"])
        rel = pj["validacao"]
        assert rel["problemas"] == [], rel["problemas"]
        assert rel["total_pp"] == rules.orcamento_de_jogador(np)
        assert rel["status"] == "validada"


def test_riqueza_baixa_da_um_ponto_a_mais(dados):
    pj = gerar(dados, riqueza="trabalhador")
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(6) + 1
    assert pj["dinheiro"]["inicial"] == 75


def test_beneficio_riqueza_custa_pontos(dados):
    pj = gerar(dados, riqueza="prospero")
    assert pj["ficha"]["vantagens"]["Benefício (Riqueza)"] == 2
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(6)


def test_dinheiro_nao_fica_negativo(dados):
    for arquetipo in ARQUETIPOS_PJ:
        pj = gerar(dados, arquetipo, riqueza="trabalhador")
        assert pj["dinheiro"]["restante"] >= 0
        assert pj["dinheiro"]["gasto"] <= pj["dinheiro"]["inicial"]


def test_arma_acima_do_np_nao_e_sorteada(dados):
    for semente in range(10):
        pj = gerar(dados, "fora_da_lei", 2, "assaltante_trem", semente=semente)
        assert "dinamite" not in pj["ficha"]["equipamento"]
        assert pj["validacao"]["problemas"] == []


def test_arma_escolhida_acima_do_np_fica_de_fora_e_devolve_o_dinheiro(dados):
    pj = gerar(dados, "fora_da_lei", 2, "assaltante_trem",
               equipamento={"modo": "manual", "ids": ["dinamite", "revolver_leve", "cavalo"]})
    assert "dinamite" not in pj["ficha"]["equipamento"]
    assert any("Dinamite" in nome for nome in pj["dinheiro"]["fora_do_np"])
    assert pj["dinheiro"]["gasto"] == 10 + 150   # revólver + cavalo; a dinamite foi devolvida


def test_equipamento_automatico_e_coerente_com_o_arquetipo(dados):
    for arquetipo in ARQUETIPOS_PJ:
        arq = dados["jogador"]["arquetipos"][arquetipo]
        permitidos = set(arq["armas"]["principais"] + arq["armas"]["secundarias"]
                         + arq["itens"]["essenciais"] + arq["itens"]["opcionais"])
        for foco in arq["focos"]:
            permitidos |= set(foco["armas"] + foco["itens"])
        for semente in range(8):
            pj = gerar(dados, arquetipo, 6, semente=semente)
            municoes = {dados["equipamentos"][i].get("municao") for i in pj["ficha"]["equipamento"]}
            for item in pj["ficha"]["equipamento"]:
                assert item in permitidos or item in municoes, f"{arquetipo}: {item}"


def test_cada_arma_de_fogo_vem_com_municao(dados):
    for semente in range(8):
        pj = gerar(dados, "cacador", 6, semente=semente)
        for item in pj["ficha"]["equipamento"]:
            municao = dados["equipamentos"][item].get("municao")
            if municao:
                assert municao in pj["ficha"]["equipamento"]


def test_equipamento_escolhido(dados):
    ids = ["colt_army_44", "municao_pistola", "cavalo", "sela", "stetson"]
    pj = gerar(dados, equipamento={"modo": "manual", "ids": ids})
    assert pj["ficha"]["equipamento"] == ids
    assert pj["validacao"]["status"] == "validada"


ACIMA_DO_DINHEIRO = ["colt_army_44", "municao_pistola", "cavalo", "sela", "carrocao_conestoga"]   # $390


def test_passar_do_dinheiro_pagando_com_pontos(dados):
    pj = gerar(dados, equipamento={"modo": "manual", "ids": ACIMA_DO_DINHEIRO, "excesso": "pontos"})
    assert pj["dinheiro"]["condicao"].startswith("Em ascensão")
    assert pj["dinheiro"]["subiu_de"].startswith("Classe média")
    assert pj["dinheiro"]["pontos_da_riqueza"] == 1
    assert pj["ficha"]["vantagens"]["Benefício (Riqueza)"] == 1
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(6)   # o PP saiu do orçamento
    assert pj["dinheiro"]["divida"] == 0


def test_pagar_com_pontos_e_o_padrao(dados):
    pj = gerar(dados, equipamento={"modo": "manual", "ids": ACIMA_DO_DINHEIRO})
    assert pj["dinheiro"]["subiu_de"]


def test_passar_do_dinheiro_ficando_devendo(dados):
    pj = gerar(dados, equipamento={"modo": "manual", "ids": ACIMA_DO_DINHEIRO, "excesso": "divida"})
    assert pj["dinheiro"]["divida"] == 140
    assert pj["dinheiro"]["restante"] == 0
    assert "Benefício (Riqueza)" not in pj["ficha"]["vantagens"]
    assert pj["validacao"]["status"] == "validada"


def test_trabalhador_que_sobe_perde_o_ponto_extra(dados):
    pj = gerar(dados, riqueza="trabalhador", equipamento={"modo": "manual", "ids": ["colt_army_44", "cavalo"]})
    assert pj["dinheiro"]["condicao"].startswith("Classe média")
    assert pj["dinheiro"]["pontos_da_riqueza"] == 1
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(6)


def test_nunca_desce_a_condicao_financeira(dados):
    pj = gerar(dados, riqueza="prospero", equipamento={"modo": "manual", "ids": ["cavalo"]})
    assert pj["dinheiro"]["condicao"].startswith("Próspero")


def test_valor_acima_da_maior_condicao(dados):
    with pytest.raises(generator.GeneratorError, match="maior condição"):
        gerar(dados, equipamento={"modo": "manual", "ids": ["carrocao_conestoga"] * 300})


def test_divida_com_arma_devolvida_abate_a_divida(dados):
    # Dinamite não cabe no NP 2: o dinheiro dela volta e reduz a dívida.
    pj = gerar(dados, "fora_da_lei", 2, "assaltante_trem",
               equipamento={"modo": "manual", "ids": ["dinamite", "cavalo", "sela", "carrocao_conestoga"],
                            "excesso": "divida"})
    assert pj["dinheiro"]["divida"] == 3 + 150 + 25 + 200 - 250 - 3


def test_equipamento_escolhido_desconhecido(dados):
    with pytest.raises(generator.GeneratorError, match="desconhecidos"):
        gerar(dados, equipamento={"modo": "manual", "ids": ["sabre_de_luz"]})


def test_vantagens_escolhidas_nao_ganham_outras(dados):
    nomes = ["Saque Rápido", "Ataque à Distância", "Zombar"]
    for semente in range(5):
        pj = gerar(dados, vantagens={"modo": "manual", "nomes": nomes}, semente=semente)
        assert set(pj["ficha"]["vantagens"]) == set(nomes)
        assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(6)


def test_vantagem_escolhida_desconhecida(dados):
    with pytest.raises(generator.GeneratorError, match="desconhecida"):
        gerar(dados, vantagens={"modo": "manual", "nomes": ["Voar"]})


def test_maximo_e_muito_raro(dados):
    no_maximo = 0
    total = 0
    for arquetipo in ARQUETIPOS_PJ:
        for semente in range(6):
            pj = gerar(dados, arquetipo, 8, semente=semente)
            total += 1
            no_maximo += any(c["valor"] >= c["maximo"] for c in pj["validacao"]["limites"]
                             if c["nome"].startswith("Perícia"))
    assert no_maximo / total < 0.05


def test_sorte_respeita_metade_do_np(dados):
    for np in (2, 3, 6, 10):
        pj = gerar(dados, "jogador", np)
        assert pj["ficha"]["vantagens"].get("Sorte", 0) <= np // 2


def test_iniciativa_nao_dispara(dados):
    for semente in range(10):
        pj = gerar(dados, "pistoleiro", 10, "duelista", semente=semente)
        assert pj["ficha"]["vantagens"]["Iniciativa Aprimorada"] <= 10 // 3


def test_exige_motivacao(dados):
    with pytest.raises(generator.GeneratorError, match="Motivação"):
        gerar(dados, complicacoes=[{"categoria": "complicacao", "nome": "Honra"},
                                   {"categoria": "complicacao", "nome": "Vício"}])


def test_exige_duas_complicacoes(dados):
    with pytest.raises(generator.GeneratorError, match="duas"):
        gerar(dados, complicacoes=[{"categoria": "motivacao", "nome": "Justiça"}])


def test_varia_a_cada_geracao_e_repete_com_a_mesma_semente(dados):
    fichas = {str(sorted(gerar(dados, semente=s)["ficha"]["pericias"].items())) for s in range(6)}
    assert len(fichas) > 1
    assert gerar(dados, semente=3)["ficha"] == gerar(dados, semente=3)["ficha"]


def test_sortear_complicacoes(dados):
    for arquetipo in ARQUETIPOS_PJ:
        lista = player.sortear_complicacoes(dados, arquetipo, random.Random(1))
        assert sum(1 for c in lista if c["categoria"] == "motivacao") == 1
        assert len(lista) >= 2


def test_nome_e_jogador(dados):
    pj = gerar(dados, nome="Jesse Calloway", jogador="Nathan")
    assert pj["nome"] == "Jesse Calloway" and pj["jogador"] == "Nathan"
    assert gerar(dados)["nome"]   # sem nome, o gerador sorteia


def test_rotas_do_jogador(dados):
    cliente = app.app.test_client()
    comp = cliente.post("/api/jogador/complicacoes", json={"arquetipo": "xerife", "semente": 1}).get_json()
    resposta = cliente.post("/api/jogador/gerar", json={"arquetipo": "xerife", "np": 6, "foco": "pacificador",
                                                         "riqueza": "classe_media", "complicacoes": comp["complicacoes"],
                                                         "jogador": "Nathan", "semente": 2})
    assert resposta.status_code == 200
    personagem = resposta.get_json()["personagem"]
    assert "Complicações" in personagem["texto"]
    for rota in ("/api/ficha.pdf", "/api/ficha.docx"):
        assert cliente.post(rota, json={"npc": personagem}).status_code == 200


def test_pdf_do_jogador_tem_complicacoes_e_jogador(dados):
    import io

    from pypdf import PdfReader

    from nucleo import pdf_export
    pj = gerar(dados, jogador="Nathan")
    campos = PdfReader(io.BytesIO(pdf_export.gerar_pdf(dados["ficha_pdf"], pj, pj["validacao"]))).get_fields()
    assert campos["Jogador"].get("/V") == "Nathan"
    assert "Justiça" in campos["Complicações 1"].get("/V")


# ---------------------------------------------------------------- escalada de NPC

@pytest.mark.parametrize("arquetipo", ["capanga", "policial", "medico", "padre", "vaqueiro"])
def test_npc_acompanha_o_np_pedido(dados, arquetipo):
    nps = generator.nps_disponiveis(dados, dados["arquetipos"][arquetipo])
    for np in nps:
        npcs = generator.gerar_grupo(dados, arquetipo, np, "aleatorio", 4, random.Random(np))["npcs"]
        for npc in npcs:
            assert npc["validacao"]["problemas"] == []
            assert npc["validacao"]["np_efetivo"] >= np - 2
    alto = generator.gerar_grupo(dados, arquetipo, nps[-1], "aleatorio", 3, random.Random(1))["npcs"]
    baixo = generator.gerar_grupo(dados, arquetipo, nps[0], "aleatorio", 3, random.Random(1))["npcs"]
    assert min(n["validacao"]["total_pp"] for n in alto) > max(n["validacao"]["total_pp"] for n in baixo)
