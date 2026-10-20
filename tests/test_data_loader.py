"""Testes do carregamento e da conferência dos arquivos JSON."""

import json
import shutil

import pytest

from nucleo import data_loader


@pytest.fixture
def pasta_copia(tmp_path):
    """Uma cópia da pasta data/ que cada teste pode estragar à vontade."""
    destino = tmp_path / "dados"
    shutil.copytree(data_loader.PASTA_DADOS, destino)
    return destino


def caminho_do_arquivo(pasta, arquivo):
    """Arquivos comuns ficam em dados/comum; os do gênero, em dados/generos/faroeste."""
    comum = pasta / "comum" / arquivo
    return comum if comum.exists() else pasta / "generos" / "faroeste" / arquivo


def editar(pasta, arquivo, funcao):
    caminho = caminho_do_arquivo(pasta, arquivo)
    conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    funcao(conteudo)
    caminho.write_text(json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")


def mensagens(pasta):
    with pytest.raises(data_loader.DataError) as erro:
        data_loader.carregar_genero("faroeste", pasta)
    return " | ".join(erro.value.mensagens)


def test_dados_reais_carregam(dados):
    assert {"capanga", "policial", "cavalo"} <= set(dados["arquetipos"])
    assert len(dados["modulos"]) >= 5


def test_id_duplicado(pasta_copia):
    editar(pasta_copia, "modules.json", lambda mods: mods.append(dict(mods[0])))
    assert "aparece mais de uma vez" in mensagens(pasta_copia)


def test_campo_obrigatorio_ausente(pasta_copia):
    editar(pasta_copia, "modules.json", lambda mods: mods[0].pop("estilos"))
    assert "faltam os campos estilos" in mensagens(pasta_copia)


def test_referencia_a_arquetipo_inexistente(pasta_copia):
    editar(pasta_copia, "modules.json", lambda mods: mods[0]["arquetipos"].append("dragao"))
    assert "arquétipo inexistente 'dragao'" in mensagens(pasta_copia)


def test_incompatibilidade_com_modulo_inexistente(pasta_copia):
    editar(pasta_copia, "modules.json",
           lambda mods: mods[0].setdefault("incompativel_com", []).append("ninja"))
    assert "módulo inexistente 'ninja'" in mensagens(pasta_copia)


def test_pericia_desconhecida(pasta_copia):
    editar(pasta_copia, "modules.json", lambda mods: mods[0]["adiciona"]["pericias"].update({"Laçar": 2}))
    assert "perícia desconhecida" in mensagens(pasta_copia)


def test_vantagem_desconhecida(pasta_copia):
    editar(pasta_copia, "modules.json", lambda mods: mods[0]["adiciona"]["vantagens"].update({"Voar": 1}))
    assert "vantagem desconhecida 'Voar'" in mensagens(pasta_copia)


def test_json_quebrado(pasta_copia):
    caminho_do_arquivo(pasta_copia, "styles.json").write_text("[{", encoding="utf-8")
    assert "JSON inválido" in mensagens(pasta_copia)


def test_varios_erros_sao_informados_juntos(pasta_copia):
    def estragar(mods):
        mods[0]["arquetipos"].append("dragao")
        mods[1]["status_dados"] = "talvez"
    editar(pasta_copia, "modules.json", estragar)
    texto = mensagens(pasta_copia)
    assert "dragao" in texto and "talvez" in texto


def test_genero_inexistente(pasta_copia):
    with pytest.raises(data_loader.DataError, match="não existe"):
        data_loader.carregar_genero("steampunk", pasta_copia)


def test_carregar_todos_lista_os_generos():
    dados, erros = data_loader.carregar_todos()
    assert "faroeste" in dados and not erros
    assert dados["faroeste"]["genero"]["perfis_de_poder"] == []
    assert dados["faroeste"]["poderes"] == {}   # faroeste não tem poderes
