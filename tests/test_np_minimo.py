"""NP mínimo da subclasse: abaixo dele os poderes essenciais não cabem e a ficha não é gerada."""

import copy
import random

import pytest

import app
from nucleo import data_loader, player
from nucleo.generator import GeneratorError

COMPLICACOES = [{"categoria": "motivacao", "nome": "Fé", "detalhe": ""},
                {"categoria": "complicacao", "nome": "Honra", "detalhe": "Nunca quebra a palavra dada."}]


@pytest.fixture(scope="module")
def fantasia():
    return data_loader.carregar_genero("fantasia")


def _foco(dados, arquetipo_id, foco_id):
    arquetipo = dados["jogador"]["arquetipos"][arquetipo_id]
    return arquetipo, next(f for f in arquetipo["focos"] if f["id"] == foco_id)


def _gerar(dados, arquetipo_id, foco_id, np, **kwargs):
    return player.gerar_personagem(dados, arquetipo_id, np, foco_id, "classe_media", COMPLICACOES,
                                   rng=random.Random(1), **kwargs)


def test_bruxo_cacador_de_monstros_comeca_no_np_4(fantasia):
    arquetipo, foco = _foco(fantasia, "bruxo", "cacador_monstros")
    assert player.np_minimo(fantasia, arquetipo, foco) == 4
    for variante in foco["variantes"]:
        assert player.np_minimo(fantasia, arquetipo, player.foco_com_variante(arquetipo, foco, variante)) == 4


def test_abaixo_do_minimo_a_ficha_nao_sai(fantasia):
    with pytest.raises(GeneratorError, match="precisa de NP 4"):
        _gerar(fantasia, "bruxo", "cacador_monstros", 3, variante="lobo")
    with pytest.raises(GeneratorError, match="precisa de NP 4"):
        _gerar(fantasia, "bruxo", "cacador_monstros", 2)   # variante sorteada: também não cabe
    assert _gerar(fantasia, "bruxo", "cacador_monstros", 4, variante="lobo")["np_pretendido"] == 4


def test_subclasse_sem_poderes_pesados_vale_desde_o_menor_np(fantasia):
    arquetipo, foco = _foco(fantasia, "guerreiro", "campeao")
    assert player.np_minimo(fantasia, arquetipo, foco) == fantasia["configuracoes"]["nps_jogador"][0]


def test_np_minimo_declarado_no_json_vale_quando_e_maior(fantasia):
    dados = copy.deepcopy(fantasia)
    dados["genero"] = dict(dados["genero"], id="fantasia_teste")   # não usa o cache do gênero de verdade
    arquetipo, foco = _foco(dados, "guerreiro", "campeao")
    foco["np_minimo"] = 6
    assert player.np_minimo(dados, arquetipo, foco) == 6
    with pytest.raises(GeneratorError, match="precisa de NP 6"):
        _gerar(dados, "guerreiro", "campeao", 5)


@pytest.mark.parametrize("genero", ["fantasia", "escola_de_magia"])
def test_no_np_minimo_toda_subclasse_sai_com_os_poderes_essenciais(genero):
    dados = data_loader.carregar_genero(genero)
    for arquetipo_id, arquetipo in dados["jogador"]["arquetipos"].items():
        for foco in arquetipo["focos"]:
            variante = (foco.get("variantes") or [{}])[0]
            com_variante = player.foco_com_variante(arquetipo, foco, variante) if variante else foco
            np = player.np_minimo(dados, arquetipo, com_variante)
            pj = player.gerar_personagem(dados, arquetipo_id, np, foco["id"], dados["jogador"]["riqueza"][0]["id"],
                                         COMPLICACOES, rng=random.Random(1), variante=variante.get("id"))
            essenciais, _ = player.implantes_da_escolha(player.arquetipo_com_foco(arquetipo, com_variante),
                                                        com_variante)
            faltam = set(essenciais) - set(pj["ficha"]["poderes"])
            assert not faltam, f"{arquetipo_id}/{foco['id']} no NP {np}: faltam {faltam}"


def test_tela_recebe_o_np_minimo():
    opcoes = app.opcoes_da_interface(app._dados("fantasia"))
    bruxo = next(a for a in opcoes["jogador"]["arquetipos"] if a["id"] == "bruxo")
    cacador = next(f for f in bruxo["focos"] if f["id"] == "cacador_monstros")
    assert cacador["np_minimo"] == 4
    assert all(v["np_minimo"] == 4 for v in cacador["variantes"])
