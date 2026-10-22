"""Gênero fantasia medieval: arranjos de magia, magias que acompanham o NP, raças, escudos e PJs."""

import random

import pytest

from nucleo import data_loader, formatter, generator, player, poderes, rules, validator


@pytest.fixture(scope="module")
def fantasia():
    return data_loader.carregar_genero("fantasia")


def _complicacoes():
    return [{"categoria": "motivacao", "nome": "Fé", "detalhe": ""},
            {"categoria": "complicacao", "nome": "Honra", "detalhe": "Nunca quebra a palavra dada."}]


def gerar_pj(dados, arquetipo="mago", np=5, foco=None, semente=1, riqueza="classe_media", **kwargs):
    arq = dados["jogador"]["arquetipos"][arquetipo]
    return player.gerar_personagem(dados, arquetipo, np, foco or arq["focos"][0]["id"], riqueza, _complicacoes(),
                                   rng=random.Random(semente), **kwargs)


# ---------------------------------------------------------------- arranjos (efeitos alternativos)

def _poder(custo, arranjo=None):
    return {"nome": "x", "custo_informado": custo, "ajustes": {}, **({"arranjo": arranjo} if arranjo else {})}


def test_arranjo_paga_o_mais_caro_e_1_pp_por_alternativo():
    # Cultista Arcano do Guia do Mestre: Dano à Distância 6 (12 PP) + 3 efeitos alternativos = Poderes 15.
    conjunto = {"dano": _poder(12, "Magia Negra"), "aflicao": _poder(12, "Magia Negra"),
                "teleporte": _poder(6, "Magia Negra"), "mover": _poder(12, "Magia Negra")}
    assert poderes.custo_total(conjunto) == 15
    papeis = poderes.papeis_no_arranjo(conjunto)
    assert papeis["dano"] == "principal"   # no empate, vale o primeiro
    assert sorted(papeis.values()).count("alternativo") == 3


def test_poderes_fora_de_arranjo_somam_normalmente():
    conjunto = {"a": _poder(10, "Arcana"), "b": _poder(4, "Arcana"), "c": _poder(3), "d": _poder(8, "Divina")}
    assert poderes.custo_total(conjunto) == 10 + 1 + 3 + 8


def test_validador_usa_o_custo_do_arranjo(fantasia):
    ficha = {"habilidades": {h: 0 for h in rules.HABILIDADES}, "vantagens": {}, "pericias": {},
             "poderes": {"a": _poder(10, "Arcana"), "b": _poder(9, "Arcana")}}
    custos, _, total = validator.calcular_custos(ficha)
    assert custos["poderes"] == 11 and total == 11


def test_exibicao_agrupa_o_arranjo(fantasia):
    pj = gerar_pj(fantasia, "mago", 5, "evocacao", implantes={"modo": "manual",
                  "ids": ["raio_de_fogo", "bola_de_fogo", "armadura_arcana"]})
    textos = formatter.exibicao(pj)["poderes"]
    principal = next(t for t in textos if "efeito principal" in t)
    alternativo = next(t for t in textos if "efeito alternativo" in t)
    assert textos.index(principal) < textos.index(alternativo)
    assert not any("Arranjo" in t for t in textos if t.startswith("Armadura arcana"))


# ---------------------------------------------------------------- magias que acompanham o NP

@pytest.mark.parametrize("np", [3, 5, 8, 10])
def test_magia_acompanha_o_np(fantasia, np):
    poder = player.poder_do_genero(fantasia, "raio_de_fogo", np)
    assert poder["graduacao"] == np and poder["ataque"]["efeito"] == np
    assert poder["custo_informado"] == 2 * np
    assert poder["ataque"]["pericia"] == "Combate à Distância: Magia"


def test_graduacao_minima_e_1(fantasia):
    assert player.poder_do_genero(fantasia, "armadura_arcana", 2)["graduacao"] == 1


def test_estatistica_do_genero_substitui_a_do_catalogo(fantasia):
    poder = player.poder_do_genero(fantasia, "misseis_magicos", 5)
    assert "força" in poder["nome"] and "Laser" not in poder["nome"]


# ---------------------------------------------------------------- raças

def test_raca_aplica_tracos_e_custa_pontos(fantasia):
    elfo = fantasia["jogador"]["racas"]["elfo"]
    pj = gerar_pj(fantasia, "ladino", 5, raca="elfo")
    assert pj["raca"] == {"id": "elfo", "nome": "Elfo"}
    assert {"visao_escuro", "ancestralidade_feerica", "sentidos_agucados"} <= set(pj["ficha"]["poderes"])
    assert pj["ficha"]["habilidades"]["Agi"] >= 1
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(5)
    assert player.custo_da_raca(fantasia, elfo, 5) == 2 + 2 + 2 + 1 + 1   # Agi, visão, feérica, sentidos, Percepção


def test_humano_nao_tem_tracos_e_e_o_padrao(fantasia):
    assert player.custo_da_raca(fantasia, fantasia["jogador"]["racas"]["humano"], 5) == 0
    assert gerar_pj(fantasia, "guerreiro")["raca"]["id"] == "humano"


def test_raca_com_poder_que_acompanha_o_np(fantasia):
    draconato = fantasia["jogador"]["racas"]["draconato"]
    assert player.custo_da_raca(fantasia, draconato, 8) > player.custo_da_raca(fantasia, draconato, 5)


def test_raca_desconhecida(fantasia):
    with pytest.raises(generator.GeneratorError, match="Raça"):
        gerar_pj(fantasia, raca="hobgoblin")


def test_nome_segue_a_raca(fantasia):
    nomes_anoes = set(fantasia["nomes"]["anao"]["nomes"])
    pj = gerar_pj(fantasia, "guerreiro", raca="anao")
    assert pj["nome"].split(" ")[0] in nomes_anoes


def test_generos_sem_raca_continuam_iguais(dados):
    pj = player.gerar_personagem(dados, "pistoleiro", 6, "duelista", "classe_media", _complicacoes_faroeste(),
                                 rng=random.Random(1))
    assert pj["raca"] is None
    assert player.racas(dados) == []


def _complicacoes_faroeste():
    return [{"categoria": "motivacao", "nome": "Justiça"}, {"categoria": "complicacao", "nome": "Honra"}]


# ---------------------------------------------------------------- equipamento

def test_escudo_soma_nas_defesas_ativas(fantasia):
    ficha = {"habilidades": {h: 0 for h in rules.HABILIDADES}, "equipamento": ["escudo"]}
    valores = validator.calcular(ficha, fantasia["equipamentos"])
    assert valores["defesas"]["Esquiva"] == 2 and valores["defesas"]["Aparar"] == 2


def test_escudo_que_estoura_o_np_sai_e_devolve_o_dinheiro(fantasia):
    pj = gerar_pj(fantasia, "guerreiro", 3, equipamento={"modo": "manual",
                  "ids": ["espada_longa", "cota_malha", "escudo_torre"]})
    assert "escudo_torre" not in pj["ficha"]["equipamento"]
    assert "Escudo de torre" in pj["dinheiro"]["fora_do_np"]
    assert pj["validacao"]["problemas"] == []


def test_preco_em_pecas_de_ouro(fantasia):
    assert formatter.dolares(120, "po") == "120 po"
    assert formatter.dolares(2.5, "po") == "2,50 po"
    assert formatter.dolares(2550, "eb") == "2.550eb"
    assert formatter.dolares(250, "$") == "$250"


def test_sorteio_nao_compra_municao_sem_arma(fantasia):
    municoes = {i["municao"] for i in fantasia["equipamentos"].values() if i.get("municao")}
    for semente in range(10):
        pj = gerar_pj(fantasia, "guerreiro", 5, "campeao", semente=semente, raca="anao")
        armas = {fantasia["equipamentos"][i].get("municao") for i in pj["ficha"]["equipamento"]}
        for item in pj["ficha"]["equipamento"]:
            if item in municoes:
                assert item in armas


# ---------------------------------------------------------------- todas as classes

@pytest.mark.parametrize("np", [3, 5, 8])
def test_todas_as_classes_e_subclasses_fecham_o_orcamento(fantasia, np):
    for arquetipo in fantasia["jogador"]["arquetipos"].values():
        for foco in arquetipo["focos"]:
            for raca in ("humano", "elfo", "anao"):
                pj = gerar_pj(fantasia, arquetipo["id"], np, foco["id"], raca=raca)
                rel = pj["validacao"]
                assert rel["problemas"] == [], (arquetipo["id"], foco["id"], raca, rel["problemas"])
                assert rel["total_pp"] == rules.orcamento_de_jogador(np)


def test_conjuradores_recebem_a_magia_principal(fantasia):
    for arquetipo, magia in (("mago", "raio_de_fogo"), ("clerigo", "chama_sagrada"), ("druida", "chamar_relampago"),
                             ("bruxo", "rajada_mistica"), ("bardo", "zombaria_cruel")):
        pj = gerar_pj(fantasia, arquetipo, 5)
        assert magia in pj["ficha"]["poderes"], arquetipo


# ---------------------------------------------------------------- NPCs do bestiário

@pytest.mark.parametrize("arquetipo,faixa,total", [
    ("cultista", "Acólito", 12), ("cultista", "Feiticeiro do culto", 88), ("soldado", "Soldado", 45),
    ("bandido", "Bandido", 32), ("demonio", "Demônio brutamontes", 100), ("dragao", "Dragão", 88),
])
def test_fichas_base_batem_com_o_livro(fantasia, arquetipo, faixa, total):
    base = next(f for f in fantasia["arquetipos"][arquetipo]["faixas"] if f["nome"] == faixa)
    rel = validator.validar(base["ficha"], base["np"], fantasia["equipamentos"])
    assert rel["total_pp"] == total
    assert rel["problemas"] == []


def test_protecao_das_armaduras_reflete_as_equivalencias_do_catalogo(fantasia):
    protecoes = {
        "acolchoada": 1,
        "couro": 1,
        "couro_batido": 2,
        "gibao_peles": 2,
        "camisao_malha": 2,
        "brunea": 3,
        "peitoral": 4,
        "cota_malha": 3,
        "meia_armadura": 5,
        "cota_talas": 4,
        "placas": 6,
    }
    for item_id, protecao in protecoes.items():
        armadura = fantasia["equipamentos"][item_id]
        assert armadura["protecao"] == protecao
        assert armadura["custo"] == protecao


def test_npcs_de_todos_os_arquetipos_e_nps(fantasia):
    for arquetipo in fantasia["arquetipos"].values():
        for np in generator.nps_disponiveis(fantasia, arquetipo):
            grupo = generator.gerar_grupo(fantasia, arquetipo["id"], np, "aleatorio", 3, random.Random(np))
            for npc in grupo["npcs"]:
                assert npc["validacao"]["problemas"] == [], (arquetipo["id"], np)


def test_habilidade_ausente_nao_sobe(fantasia):
    for semente in range(6):
        for arquetipo in ("esqueleto", "zumbi"):
            grupo = generator.gerar_grupo(fantasia, arquetipo, 6, "aleatorio", 2, random.Random(semente))
            assert all(n["ficha"]["habilidades"]["Vig"] == rules.HABILIDADE_MINIMA for n in grupo["npcs"])


# ---------------------------------------------------------------- tipo de NPC (módulo principal escolhido)

def test_tipo_escolhido_vira_o_principal_de_todos(fantasia):
    grupo = generator.gerar_grupo(fantasia, "dragao", 10, "aleatorio", 4, random.Random(1), tipo="dragao_relampago")
    assert len(grupo["npcs"]) == 4
    assert all(n["modulos"][0]["id"] == "dragao_relampago" for n in grupo["npcs"])
    assert not any("repetem" in a for a in grupo["avisos"])


def test_tipo_que_nao_existe_no_np(fantasia):
    with pytest.raises(generator.GeneratorError, match="tipo"):
        generator.gerar_grupo(fantasia, "lobo", 3, "aleatorio", 2, random.Random(1), tipo="dragao_relampago")


def test_tipos_listam_so_os_principais(fantasia):
    tipos = {m["id"] for m in generator.tipos_do_arquetipo(fantasia, "dragao", 10)}
    assert "dragao_relampago" in tipos
    assert all(fantasia["modulos"][t].get("papel", "ambos") != "extra" for t in tipos)


# ---------------------------------------------------------------- caçador de monstros (referencias/dd/The witcher.docx)

def test_cacador_de_monstros_segue_a_ficha_de_referencia(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 7, "cacador_monstros", variante="lobo")
    poderes = pj["ficha"]["poderes"]
    papeis = poderes_mod_papeis(poderes)
    assert papeis["igni"] == "principal" and poderes["igni"]["graduacao"] == 7
    assert {papeis[s] for s in ("quen", "aard", "axii")} == {"alternativo"}
    assert "rajada_mistica" not in poderes   # não fez pacto
    assert "Especialidade: Bruxo" in pj["ficha"]["pericias"]
    assert {"Ritualista", "Artífice", "Rastrear"} <= set(pj["ficha"]["vantagens"])


def poderes_mod_papeis(poderes_da_ficha):
    return poderes.papeis_no_arranjo(poderes_da_ficha)


def test_complicacao_fixa_sempre_sorteada(fantasia):
    for semente in range(10):
        sorteadas = player.sortear_complicacoes(fantasia, "bruxo", random.Random(semente), foco_id="cacador_monstros")
        assert any(c["nome"] == "Preconceito" and "odiado" in c["detalhe"] for c in sorteadas)


def test_kit_de_bruxo_traz_os_itens_com_estatistica(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 5, "cacador_monstros", variante="lobo")
    equipamento = pj["ficha"]["equipamento"]
    assert {"kit_bruxo", "espada_prata", "espada_longa", "couro_batido"} <= set(equipamento)
    assert pj["ficha"]["quantidades"]["elixires"] == 3
    compras = {c["id"]: c["preco"] for c in pj["dinheiro"]["compras"]}
    assert compras["kit_bruxo"] == 120 and "espada_prata" not in compras   # paga o pacote, não as peças
    ataques = {a["nome"] for a in pj["validacao"]["valores"]["ataques"]}
    assert {"Espada de prata", "Espada longa"} <= ataques
    assert pj["validacao"]["valores"]["protecao"] == 2


def test_ficha_explica_protecao_da_armadura_na_resistencia(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 5, "cacador_monstros", variante="lobo")
    exibicao = formatter.exibicao(pj)
    assert "Resistência" in exibicao["defesas"]
    assert "Proteção +2 de Couro batido" in exibicao["defesas"]


def test_kit_escolhido_a_mao(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 5, "cacador_monstros", variante="lobo",
                  equipamento={"modo": "manual", "ids": ["kit_bruxo"]})
    assert pj["dinheiro"]["gasto"] == 120
    assert "espada_prata" in pj["ficha"]["equipamento"]


# ---------------------------------------------------------------- escolas do caçador de monstros

ESCOLAS = ["lobo", "gato", "grifo", "vibora", "urso", "manticora", "lince", "garca"]


@pytest.mark.parametrize("np", [3, 5, 8])
@pytest.mark.parametrize("escola", ESCOLAS)
def test_todas_as_escolas_fecham_o_orcamento(fantasia, np, escola):
    pj = gerar_pj(fantasia, "bruxo", np, "cacador_monstros", variante=escola)
    assert pj["validacao"]["problemas"] == []
    assert pj["validacao"]["total_pp"] == rules.orcamento_de_jogador(np)
    assert pj["estilo"]["nome"].startswith("Caçador de monstros · Escola")


def test_vibora_troca_as_espadas_por_adagas(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 6, "cacador_monstros", variante="vibora")
    equipamento = set(pj["ficha"]["equipamento"])
    assert {"kit_bruxo_vibora", "adaga_longa_prata", "adaga_longa"} <= equipamento
    assert not equipamento & {"espada_prata", "espada_longa"}
    assert "Combate Corpo-a-Corpo: Adagas" in pj["ficha"]["pericias"]
    assert "Combate Corpo-a-Corpo: Espadas" not in pj["ficha"]["pericias"]
    assert {"Investigação", "Furtividade"} <= set(pj["ficha"]["pericias"])


def test_urso_usa_cota_de_malha_e_grifo_ganha_yrden(fantasia):
    urso = gerar_pj(fantasia, "bruxo", 6, "cacador_monstros", variante="urso")
    assert "cota_malha" in urso["ficha"]["equipamento"] and "Ataque Poderoso" in urso["ficha"]["vantagens"]
    grifo = gerar_pj(fantasia, "bruxo", 6, "cacador_monstros", variante="grifo")
    assert "yrden" in grifo["ficha"]["poderes"]


def test_lince_treina_a_besta(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 6, "cacador_monstros", variante="lince")
    assert "besta_leve" in pj["ficha"]["equipamento"]
    assert "Combate à Distância: Bestas" in pj["ficha"]["pericias"]


def test_escola_sorteada_quando_nao_escolhida(fantasia):
    nomes = {gerar_pj(fantasia, "bruxo", 5, "cacador_monstros", semente=s)["estilo"]["nome"] for s in range(12)}
    assert len(nomes) > 1 and all("Escola" in n for n in nomes)


def test_escola_que_nao_existe(fantasia):
    with pytest.raises(generator.GeneratorError):
        gerar_pj(fantasia, "bruxo", 5, "cacador_monstros", variante="escola_do_pato")


def test_complicacao_da_escola_entra_no_sorteio(fantasia):
    for semente in range(10):
        sorteadas = player.sortear_complicacoes(fantasia, "bruxo", random.Random(semente),
                                                foco_id="cacador_monstros", variante_id="gato")
        nomes = [c["nome"] for c in sorteadas]
        assert "Preconceito" in nomes and "Reputação" in nomes


def test_subclasses_sem_escola_continuam_iguais(fantasia):
    pj = gerar_pj(fantasia, "bruxo", 5, "lamina", variante="lobo")   # variante ignorada sem escolas
    assert pj["estilo"]["nome"] == "Pacto da lâmina"
