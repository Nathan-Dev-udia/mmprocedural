"""Testes do gerador. Todos usam sementes fixas para serem reproduzíveis."""

import copy
import random
from collections import Counter

import pytest

from nucleo import generator
from nucleo import validator


def gerar(dados, arquetipo="capanga", np=4, estilo="aleatorio", quantidade=4, semente=1):
    return generator.gerar_grupo(dados, arquetipo, np, estilo, quantidade, random.Random(semente))


def test_arquetipo_inexistente(dados):
    with pytest.raises(generator.GeneratorError):
        gerar(dados, arquetipo="dragao")


def test_np_fora_da_faixa(dados):
    with pytest.raises(generator.GeneratorError):
        gerar(dados, arquetipo="capanga", np=1)


def test_quantidade_acima_do_maximo(dados):
    with pytest.raises(generator.GeneratorError):
        gerar(dados, quantidade=dados["configuracoes"]["quantidade_maxima"] + 1)


@pytest.mark.parametrize("arquetipo, np", [("capanga", 3), ("capanga", 5), ("policial", 4), ("cavalo", 4)])
def test_quantidade_atendida(dados, arquetipo, np):
    assert len(gerar(dados, arquetipo, np, quantidade=6)["npcs"]) == 6


def test_todo_modulo_cabe_em_algum_np(dados):
    """Um módulo que nunca passa nos limites é erro de cadastro."""
    for mod in dados["modulos"].values():
        for arquetipo_id in mod["arquetipos"]:
            arquetipo = dados["arquetipos"][arquetipo_id]
            valido_em = []
            for np in generator.nps_disponiveis(dados, arquetipo):
                if np < mod.get("requisitos", {}).get("np_min", 0):
                    continue
                try:
                    ficha = generator.aplicar_modulos(generator.faixa_para_np(arquetipo, np)["ficha"], [mod])
                except generator.ModuloInaplicavel:
                    continue
                if not validator.validar(ficha, np, dados["equipamentos"])["problemas"]:
                    valido_em.append(np)
            assert valido_em, f"O módulo {mod['id']} não cabe em nenhum NP de {arquetipo_id}."


@pytest.mark.parametrize("arquetipo", ["medico", "geologo", "falastrao", "padre", "minerador", "vaqueiro"])
def test_novos_arquetipos_geram_grupo(dados, arquetipo):
    np = generator.nps_disponiveis(dados, dados["arquetipos"][arquetipo])[0]
    for estilo in dados["estilos"]:
        resultado = gerar(dados, arquetipo, np, estilo, 4)
        assert len(resultado["npcs"]) == 4
        assert all(n["validacao"]["problemas"] == [] for n in resultado["npcs"])


def test_todos_os_npcs_respeitam_o_np(dados):
    for semente in range(20):
        for npc in gerar(dados, "capanga", 3, "combate", 5, semente)["npcs"]:
            assert npc["validacao"]["problemas"] == []


def test_incompativeis_nunca_juntos(dados):
    for semente in range(40):
        for npc in gerar(dados, "capanga", 5, "aleatorio", 6, semente)["npcs"]:
            assert not {"bruto", "emboscador"} <= set(npc["combinacao"])


def test_requisito_de_np(dados):
    for semente in range(30):
        for npc in gerar(dados, "capanga", 4, "combate", 6, semente)["npcs"]:
            assert "explosivista" not in npc["combinacao"]


def test_modulo_que_estoura_o_np_e_rejeitado(dados):
    # No NP 3 o cavalo de carga teria coice +2 com Dano 5 = 7 > 6.
    for semente in range(30):
        for npc in gerar(dados, "cavalo", 3, "aleatorio", 3, semente)["npcs"]:
            assert "cavalo_carga" not in npc["combinacao"]


def test_limite_de_tentativas(dados, monkeypatch):
    dados_teste = copy.deepcopy(dados)
    dados_teste["configuracoes"]["tentativas_maximas"] = 7
    # Só sobram módulos que não cabem no NP 3.
    dados_teste["modulos"] = {k: v for k, v in dados_teste["modulos"].items()
                              if k in ("cavalo_carga", "cavalo_guerra")}
    chamadas = Counter()
    original = validator.validar

    def contar(*args):
        chamadas["validar"] += 1
        return original(*args)

    monkeypatch.setattr(generator.validator, "validar", contar)
    npc, motivo = generator.gerar_npc(dados_teste, "cavalo", 3, "aleatorio", random.Random(1))
    assert npc is None
    assert "7 tentativas" in motivo
    assert chamadas["validar"] <= 7


def test_grupo_impossivel_informa_aviso(dados):
    dados_teste = copy.deepcopy(dados)
    dados_teste["modulos"] = {k: v for k, v in dados_teste["modulos"].items() if k == "cavalo_carga"}
    resultado = generator.gerar_grupo(dados_teste, "cavalo", 3, "aleatorio", 3, random.Random(1))
    assert resultado["npcs"] == []
    assert any("0 de 3" in aviso for aviso in resultado["avisos"])


def test_mesma_semente_mesmo_resultado(dados):
    a = [n["combinacao"] for n in gerar(dados, semente=42)["npcs"]]
    b = [n["combinacao"] for n in gerar(dados, semente=42)["npcs"]]
    assert a == b


def test_novo_sorteio_pode_mudar(dados):
    resultados = {tuple(tuple(n["combinacao"]) for n in gerar(dados, semente=s)["npcs"]) for s in range(10)}
    assert len(resultados) > 1


def test_grupo_evita_repetir_combinacoes(dados):
    combinacoes = [tuple(n["combinacao"]) for n in gerar(dados, "capanga", 5, "aleatorio", 8, 3)["npcs"]]
    assert len(set(combinacoes)) == len(combinacoes)


def test_tematico_nao_repete_principal_enquanto_ha_opcoes(dados):
    npcs = gerar(dados, "capanga", 5, "tematico", 5, 7)["npcs"]
    principais = [n["modulos"][0]["id"] for n in npcs]
    assert len(set(principais)) == 5
    assert all(len(n["modulos"]) == 1 for n in npcs)


def test_estilo_combate_prioriza_modulos_de_combate(dados):
    def fracao_de_combate(estilo):
        npcs = [n for s in range(40) for n in gerar(dados, "capanga", 5, estilo, 1, s)["npcs"]]
        combate = [n for n in npcs if "combate" in dados["modulos"][n["modulos"][0]["id"]]["estilos"]]
        return len(combate) / len(npcs)
    assert fracao_de_combate("combate") > fracao_de_combate("utilidade")


def test_remocao_de_caracteristica(dados):
    base = dados["arquetipos"]["capanga"]["faixas"][0]["ficha"]
    assert "Especialidade: Manha" in base["pericias"]
    ficha = generator.aplicar_modulos(base, [dados["modulos"]["batedor"]])
    assert "Especialidade: Manha" not in ficha["pericias"]


def test_substituicao_de_equipamento(dados):
    base = dados["arquetipos"]["capanga"]["faixas"][0]["ficha"]
    ficha = generator.aplicar_modulos(base, [dados["modulos"]["batedor"]])
    assert "rifle" in ficha["equipamento"] and "revolver_leve" not in ficha["equipamento"]


def test_substituicao_inaplicavel(dados):
    base = copy.deepcopy(dados["arquetipos"]["capanga"]["faixas"][0]["ficha"])
    base["equipamento"].remove("revolver_leve")
    with pytest.raises(generator.ModuloInaplicavel):
        generator.aplicar_modulos(base, [dados["modulos"]["batedor"]])


def test_aplicar_nao_altera_a_ficha_base(dados):
    base = dados["arquetipos"]["capanga"]["faixas"][0]["ficha"]
    antes = copy.deepcopy(base)
    generator.aplicar_modulos(base, [dados["modulos"]["batedor"], dados["modulos"]["pistoleiro"]])
    assert base == antes


def test_status_reflete_modulo_pendente(dados):
    dados_teste = copy.deepcopy(dados)
    for mod in dados_teste["modulos"].values():
        mod["status_dados"] = "pendente"
    npc = gerar(dados_teste, quantidade=1)["npcs"][0]
    assert npc["validacao"]["status"] == "parcial"


def test_regerar_um_evita_combinacoes_existentes(dados):
    grupo = gerar(dados, "capanga", 5, "aleatorio", 4, 5)["npcs"]
    usadas = {frozenset(n["combinacao"]) for n in grupo}
    novo, _ = generator.gerar_npc(dados, "capanga", 5, "aleatorio", random.Random(99),
                                  combinacoes_usadas=set(usadas))
    assert frozenset(novo["combinacao"]) not in usadas
