"""Escudo do Mestre: dados, tabelas geradas, página e PDF."""

import io

import openpyxl
import pypdf
import pytest

import app
from nucleo import data_loader, escudo, escudo_pdf, escudo_xlsx, medidas


@pytest.fixture(scope="module")
def montado():
    return escudo.montar("fantasia", data_loader.carregar_genero("fantasia"))


def _bloco(montado, titulo):
    return next(b for aba in montado["abas"] for b in aba["blocos"] if b.get("titulo") == titulo)


def test_todos_os_escudos_tem_estrutura_valida():
    assert escudo.generos_com_escudo() == ["cthulhu", "fantasia", "faroeste"]
    for genero in escudo.generos_com_escudo():
        assert escudo.conferir(escudo.montar(genero, data_loader.carregar_genero(genero))) == []


def test_gerados_viram_tabelas(montado):
    tipos = {b["tipo"] for aba in montado["abas"] for b in aba["blocos"]}
    assert "gerado" not in tipos


def test_queda_segue_a_regra_do_livro():
    # Livro básico e Livro do Mestre: 4 m é Dano 2, 30 m é Dano 8, máximo 16; até 2 m não machuca.
    assert medidas.dano_de_queda(2) == 0
    assert medidas.dano_de_queda(4) == 2
    assert medidas.dano_de_queda(30) == 8
    assert medidas.dano_de_queda(10_000) == 16


@pytest.mark.parametrize("genero", ["fantasia", "faroeste", "cthulhu"])
def test_tempo_de_viagem_usa_as_velocidades_do_catalogo(genero):
    dados = data_loader.carregar_genero(genero)
    montado_genero = escudo.montar(genero, dados)
    tabela = _bloco(montado_genero, "Tempo de viagem (velocidade máxima contínua)")
    linha_60km = next(l for l in tabela["linhas"] if l[0].startswith("60 km"))
    # 60 km é distância 13: a pé 16 horas, ritmo normal 1,5 dia.
    assert linha_60km[1] == "16 horas"
    assert linha_60km[-1] == "1,5 dia"
    if genero in ("fantasia", "faroeste"):
        assert linha_60km[4] == "1 hora"
    elif genero == "cthulhu":
        # Ford T (Velocidade 4) é 1 hora; Packard (Velocidade 5) é 30 minutos
        assert linha_60km[2] == "1 hora"
        assert linha_60km[3] == "30 minutos"


def test_carga_bate_com_o_validador(montado):
    tabela = _bloco(montado, "Carga [Casa]")
    forca_2 = next(l for l in tabela["linhas"] if l[0] == "+2")
    cap = medidas.capacidade_de_carga(2)
    assert forca_2[1:] == [f"{cap['leve']} kg", f"{cap['maxima']} kg"]


def test_aflicao_tem_os_graus(montado):
    tabela = _bloco(montado, "Aflição: condição por grau de falha")
    assert [l[0] for l in tabela["linhas"]][:3] == ["1º grau", "2º grau", "3º grau"]


def test_negrito_vira_partes():
    assert escudo.partes_do_texto("**Teste** = d20") == [("Teste", True), (" = d20", False)]


@pytest.mark.parametrize("genero", ["fantasia", "faroeste", "cthulhu"])
def test_pdf_tem_uma_pagina_por_aba(genero):
    dados = data_loader.carregar_genero(genero)
    montado_genero = escudo.montar(genero, dados)
    leitor = pypdf.PdfReader(io.BytesIO(escudo_pdf.gerar_pdf(montado_genero, "teste")))
    texto = "\n".join(p.extract_text() for p in leitor.pages)
    assert len(leitor.pages) >= len(montado_genero["abas"])
    for aba in montado_genero["abas"]:
        assert aba["nome"] in texto


@pytest.mark.parametrize("genero", ["fantasia", "faroeste", "cthulhu"])
def test_planilha_tem_uma_folha_por_aba(genero):
    dados = data_loader.carregar_genero(genero)
    montado_genero = escudo.montar(genero, dados)
    livro = openpyxl.load_workbook(io.BytesIO(escudo_xlsx.gerar_xlsx(montado_genero)))
    assert livro.sheetnames == [aba["nome"] for aba in montado_genero["abas"]]
    viagem = livro["Viagem"]
    valores = [c for linha in viagem.iter_rows(values_only=True) for c in linha if c is not None]
    assert "Tempo de viagem (velocidade máxima contínua)" in valores and "1,5 dia" in valores
    assert viagem.page_setup.orientation == "landscape"


def test_pagina_e_download():
    cliente = app.app.test_client()
    for genero in ("fantasia", "faroeste", "cthulhu"):
        pagina = cliente.get(f"/?genero={genero}").get_data(as_text=True)
        assert 'id="aba-escudo"' in pagina and "<strong>Teste</strong>" in pagina
        resposta = cliente.get(f"/escudo/{genero}.pdf")
        assert resposta.status_code == 200 and resposta.data.startswith(b"%PDF")
        planilha = cliente.get(f"/escudo/{genero}.xlsx")
        assert planilha.status_code == 200 and planilha.data.startswith(b"PK")
    assert 'id="aba-escudo"' not in cliente.get("/?genero=cyberpunk").get_data(as_text=True)
    assert cliente.get("/escudo/cyberpunk.pdf").status_code == 404
    assert cliente.get("/escudo/fantasia.docx").status_code == 404
