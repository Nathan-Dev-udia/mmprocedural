"""Tabela de Medidas do livro básico e pesos/velocidades do equipamento."""

import pytest

from nucleo import data_loader, medidas, player


def test_tabela_bate_com_os_exemplos_do_livro():
    tabela = medidas.tabela()
    assert tabela[3]["massa"] == "250 kg"          # Força 3 ergue 250 kg
    assert tabela[10]["massa"] == "30 t"           # Força 10 ergue 30 toneladas
    assert tabela[9]["tempo"] == "1 hora" and tabela[9]["distancia"] == "4 km"   # pessoa a pé em uma hora
    assert tabela[13]["tempo"] == "16 horas" and tabela[16]["tempo"] == "4 dias"
    assert tabela[4]["distancia"] == "120 m" and tabela[6]["distancia"] == "500 m"
    assert sorted(tabela) == list(range(-5, 31))


@pytest.mark.parametrize("kg,graduacao", [(1, -5), (1.5, -4), (0.5, -6), (0.25, -7), (27.5, 0), (30, 0),
                                          (32.5, 1), (250, 3), (30000, 10), (0, None)])
def test_graduacao_de_massa_pega_a_mais_alta_mais_proxima(kg, graduacao):
    assert medidas.graduacao_de_massa(kg) == graduacao


def test_velocidade_em_km_por_hora_segue_o_guia_do_mestre():
    assert medidas.km_por_hora(4) == 60     # Cavalo: Velocidade 4 (60 km/h)
    assert medidas.km_por_hora(0) == 4      # pessoa normal: 4 km em uma hora
    assert medidas.km_por_hora(2) == 15


def test_todo_item_da_fantasia_tem_peso_ou_velocidade():
    dados = data_loader.carregar_genero("fantasia")
    for item in dados["equipamentos"].values():
        if item.get("carga"):
            assert item["velocidade"] in (3, 4), item["id"]
        else:
            assert player.peso_do_item(dados, item) is not None, item["id"]
    kit = dados["equipamentos"]["kit_bruxo"]
    soma = sum(player.peso_do_item(dados, dados["equipamentos"][i]) * q for i, q in player.conteudo_do_kit(kit))
    assert player.peso_do_item(dados, kit) == pytest.approx(soma)
    assert dados["equipamentos"]["cavalo_montaria"]["velocidade"] == 4


def test_peso_em_texto_do_faroeste_nao_conta():
    dados = data_loader.carregar_genero("faroeste")
    assert player.peso_do_item(dados, {"peso": "2,5 (cheio)/1 (vazio)"}) is None
