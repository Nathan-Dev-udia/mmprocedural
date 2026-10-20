"""Gênero cyberpunk: fichas-base do livro, implantes, dinheiro em eurobucks (Cyberpunk RED) e PJs."""

import copy
import math
import random

import pytest

from nucleo import data_loader, formatter, generator, player, rules, validator


@pytest.fixture(scope="module")
def cyber():
    return data_loader.carregar_genero("cyberpunk")


def _complicacoes():
    return [{"categoria": "motivacao", "nome": "Cobiça", "detalhe": ""},
            {"categoria": "complicacao", "nome": "Inimigo", "detalhe": "Uma corporação."}]


def gerar_pj(dados, arquetipo="solo", np=6, foco=None, semente=1, riqueza="classe_media", **kwargs):
    arq = dados["jogador"]["arquetipos"][arquetipo]
    return player.gerar_personagem(dados, arquetipo, np, foco or arq["focos"][0]["id"], riqueza, _complicacoes(),
                                   rng=random.Random(semente), **kwargs)


# ---------------------------------------------------------------- dados

def test_genero_carrega_com_implantes_e_dinheiro(cyber):
    assert cyber["configuracoes"]["equipamento"] == "dinheiro"
    assert cyber["configuracoes"]["moeda"] == "eb"
    assert cyber["configuracoes"]["rotulo_poderes"] == "Implantes"
    assert len(cyber["poderes_do_genero"]) >= 20
    assert all(p["perfil"] in cyber["genero"]["perfis_de_poder"] for p in cyber["poderes"].values())


@pytest.mark.parametrize("arquetipo,faixa,total", [
    ("gangue", "Gangueiro", 30),
    ("seguranca", "Guarda corporativo", 45),
    ("netrunner", "Hacker", 24),
    ("fixer", "Chefão do submundo", 60),
    ("agente", "Agente", 60),
])
def test_fichas_base_somam_o_total_e_cabem_no_np(cyber, arquetipo, faixa, total):
    base = next(f for f in cyber["arquetipos"][arquetipo]["faixas"] if f["nome"] == faixa)
    ficha = copy.deepcopy(base["ficha"])
    relatorio = validator.validar(ficha, base["np"], cyber["equipamentos"])
    assert relatorio["total_pp"] == total
    assert relatorio["problemas"] == []


def test_defesa_rapida_aumenta_esquiva_e_aparar_pelo_preco_das_duas(cyber):
    poder = cyber["poderes_do_genero"]["reflexos_turbinados"]["poder"]
    assert poder["ajustes"] == {"Esquiva": 2, "Aparar": 2}
    assert poder["custo_informado"] == 4


def test_colete_balistico_nao_conta_contra_golpes(cyber):
    ficha = {"habilidades": {h: 0 for h in rules.HABILIDADES} | {"Vig": 2, "Lut": 4},
             "defesas_compradas": {}, "pericias": {}, "vantagens": {"Equipamento": 1},
             "equipamento": ["colete_balistico"], "poderes": {}}
    valores = validator.calcular(ficha, cyber["equipamentos"])
    assert valores["defesas"]["Resistência"] == 6
    assert valores["resistencia_plena"] == 2


# ---------------------------------------------------------------- NPCs

@pytest.mark.parametrize("arquetipo", ["gangue", "seguranca", "mercenario", "netrunner", "fixer", "agente"])
def test_npcs_gerados_cabem_no_np(cyber, arquetipo):
    for np in generator.nps_disponiveis(cyber, cyber["arquetipos"][arquetipo]):
        grupo = generator.gerar_grupo(cyber, arquetipo, np, "aleatorio", 4, random.Random(np))
        assert grupo["npcs"]
        for npc in grupo["npcs"]:
            assert npc["validacao"]["status"] != "invalida", npc["validacao"]["problemas"]
            assert npc["rotulo_poderes"] == "Implantes"


def test_braco_canhao_so_a_partir_do_np_5(cyber):
    assert cyber["modulos"]["braco_canhao"]["requisitos"]["np_min"] == 5
    for semente in range(30):
        npc, _ = generator.gerar_npc(cyber, "mercenario", 6, "combate", random.Random(semente))
        if npc and "braco_canhao" in npc["combinacao"]:
            assert "canhao" in npc["ficha"]["poderes"]
            break


def test_todo_item_e_implante_tem_preco_do_red_ou_estimado(cyber):
    for item in list(cyber["equipamentos"].values()) + list(cyber["poderes_do_genero"].values()):
        # Preço zero só para munição sem custo em pontos ou para o que é emprestado (a moto do clã do Nômade).
        assert item["preco"] > 0 or item.get("custo") == 0 or item.get("categoria_de_preco") == "Emprestado"
        assert item.get("fonte_preco")
        assert item.get("preco_estimado") or "Cyberpunk RED" in item["fonte_preco"]


# ---------------------------------------------------------------- PJs

@pytest.mark.parametrize("arquetipo", ["rockerboy", "solo", "netrunner", "techie", "medtech", "media", "exec",
                                       "lawman", "fixer", "nomade"])
@pytest.mark.parametrize("np", [2, 6, 10])
def test_pj_fecha_o_orcamento_exato(cyber, arquetipo, np):
    for foco in cyber["jogador"]["arquetipos"][arquetipo]["focos"]:
        pj = gerar_pj(cyber, arquetipo, np, foco["id"], semente=np)
        assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(np)
        assert pj["validacao"]["problemas"] == []
        assert pj["dinheiro"]["gasto"] <= pj["dinheiro"]["inicial"]


def test_classe_media_comeca_com_os_2550eb_do_pacote_completo(cyber):
    pj = gerar_pj(cyber, "solo", 6)
    assert pj["dinheiro"]["inicial"] == 2550
    assert pj["dinheiro"]["moeda"] == "eb"
    assert "eb" in formatter.texto(pj)
    assert pj["regras_validacao"]["equipamento_gratuito"] is True


def test_implantes_custam_pp_e_eurobucks(cyber):
    pj = gerar_pj(cyber, "netrunner", 6, equipamento={"modo": "manual", "ids": ["computador", "pistola_leve"]},
                  implantes={"modo": "manual", "ids": ["interface_neural", "firewall_cortical"]})
    assert pj["ficha"]["equipamento"] == ["computador", "pistola_leve"]
    assert set(pj["ficha"]["poderes"]) == {"interface_neural", "firewall_cortical"}
    # Cyberdeck 500 + pistola pesada 100 + Link Neural e plugs 1.000 + firewall 500
    assert pj["dinheiro"]["gasto"] == 2100
    assert {c["id"] for c in pj["dinheiro"]["compras"] if c.get("implante")} == {"interface_neural", "firewall_cortical"}
    assert pj["validacao"]["total_pp"] == 90
    assert "cyberware" in formatter.texto(pj)


def test_cyberware_acima_do_dinheiro_sobe_a_riqueza_ou_vira_divida(cyber):
    pedido = {"modo": "manual", "ids": ["camuflagem_optica"]}  # 5.000eb
    pj = gerar_pj(cyber, "solo", 6, implantes=pedido, equipamento={"modo": "manual", "ids": []})
    assert pj["dinheiro"]["condicao"].startswith("Quitinete")
    assert pj["ficha"]["vantagens"]["Benefício (Riqueza)"] == 1
    pj = gerar_pj(cyber, "solo", 6, implantes=pedido, equipamento={"modo": "manual", "ids": [], "excesso": "divida"})
    assert pj["dinheiro"]["divida"] == 2450


def test_implante_que_estoura_o_np_fica_de_fora(cyber):
    # Braço-canhão (Dano 5 à distância) com Ataque à Distância passa do teto de ataque + efeito do NP 2.
    pj = gerar_pj(cyber, "solo", 2, implantes={"modo": "manual", "ids": ["braco_canhao"]},
                  vantagens={"modo": "manual", "nomes": ["Ataque à Distância"]})
    assert "braco_canhao" not in pj["ficha"]["poderes"]
    assert pj["implantes"]["fora"]
    assert "Ficou de fora" in formatter.texto(pj)


def test_modo_pontos_continua_funcionando(cyber):
    dados = copy.deepcopy(cyber)
    dados["configuracoes"]["equipamento"] = "pontos"
    pj = gerar_pj(dados, "solo", 6)
    assert pj["dinheiro"] is None
    pe = pj["pontos_de_equipamento"]
    assert pj["ficha"]["vantagens"]["Equipamento"] == math.ceil(pe["usados"] / 5)
    assert pj["validacao"]["total_pp"] == 90
    with pytest.raises(generator.GeneratorError, match="orçamento"):
        gerar_pj(dados, "solo", 2, equipamento={"modo": "manual", "ids": ["computador"] * 160})


def test_faroeste_continua_sem_implantes(dados):
    arq = next(iter(dados["jogador"]["arquetipos"].values()))
    pj = player.gerar_personagem(dados, arq["id"], 6, arq["focos"][0]["id"], "classe_media", _complicacoes(),
                                 rng=random.Random(1))
    assert pj["implantes"] is None and pj["dinheiro"] is not None
    assert "$" in formatter.texto(pj)
