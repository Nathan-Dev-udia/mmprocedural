"""Distribuição dos pontos das fichas de jogador, comparada com os arquétipos do livro básico.

Sem contar poderes, os 13 arquétipos de NP 10 do livro básico (p. 28–47) gastam em média 48% em habilidades,
20% em perícias (de 13% no Guerreiro a 32% no Mestre de Armas), 20% em defesas e 7% em vantagens.
"""

import random
import statistics

import pytest

from nucleo import data_loader, player


def _fichas(genero):
    dados = data_loader.carregar_genero(genero)
    motivacao = dados["complicacoes"]["motivacoes"][0]["nome"]
    complicacoes = [{"categoria": "motivacao", "nome": motivacao}, {"categoria": "complicacao", "nome": "Honra"}]
    for arquetipo in dados["jogador"]["arquetipos"].values():
        for np in (4, 8):
            foco = arquetipo["focos"][np % len(arquetipo["focos"])]
            yield arquetipo, foco, np, player.gerar_personagem(dados, arquetipo["id"], np, foco["id"], "classe_media",
                                                              complicacoes, rng=random.Random(np))


@pytest.mark.parametrize("genero", ["faroeste", "cyberpunk", "fantasia"])
def test_distribuicao_parecida_com_a_do_livro(genero):
    partes = {"habilidades": [], "pericias": []}
    for _, _, _, pj in _fichas(genero):
        custos = pj["validacao"]["custos"]
        sem_poderes = sum(v for secao, v in custos.items() if secao != "poderes")
        for secao in partes:
            partes[secao].append(custos[secao] / sem_poderes)
    assert statistics.mean(partes["habilidades"]) >= 0.35
    assert statistics.mean(partes["pericias"]) <= player.PARTE_DAS_PERICIAS + 0.03


@pytest.mark.parametrize("genero", ["faroeste", "cyberpunk", "fantasia"])
def test_pericias_fora_da_classe_ficam_baixas(genero):
    for arquetipo, foco, np, pj in _fichas(genero):
        da_classe = {p.split(":", 1)[1] for p in arquetipo["prioridades"] + foco.get("prioridades", [])
                     if p.startswith("pericia:")}
        teto = player.teto_de_pericia_fora_da_classe(np)
        # Perícias de ataque (da arma ou da magia) e as da raça também são do personagem.
        for nome, graduacoes in pj["ficha"]["pericias"].items():
            if nome not in da_classe and not nome.startswith("Combate"):
                assert graduacoes <= teto + 2, (arquetipo["id"], nome, graduacoes)


def test_conjurador_treina_a_magia_e_nao_o_bordao():
    dados = data_loader.carregar_genero("fantasia")
    complicacoes = [{"categoria": "motivacao", "nome": "Fé"}, {"categoria": "complicacao", "nome": "Honra"}]
    for semente in range(4):
        pj = player.gerar_personagem(dados, "mago", 7, "evocacao", "classe_media", complicacoes,
                                     rng=random.Random(semente))
        pericias = pj["ficha"]["pericias"]
        assert pericias.get("Combate Corpo-a-Corpo: Porretes", 0) <= player.teto_de_pericia_fora_da_classe(7)
        assert pericias.get("Combate à Distância: Magia", 0) > 0
