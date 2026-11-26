"""Companheiros (pets): a ficha calculada pelo programa tem de bater com o Guia do Mestre de Jogo."""

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
