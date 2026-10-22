"""Testes da exportação para a ficha editável em PDF e das rotas de download."""

import io
import random
import zipfile

import pytest
from pypdf import PdfReader

import app
from nucleo import formatter, generator, pdf_export, player, validator

CASOS = [("capanga", 3), ("capanga", 5), ("policial", 5), ("cavalo", 4)]


def gerar_pdf(dados, arquetipo, np, semente=1):
    npc, _ = generator.gerar_npc(dados, arquetipo, np, "aleatorio", random.Random(semente))
    relatorio = validator.validar(npc["ficha"], np, dados["equipamentos"])
    campos = PdfReader(io.BytesIO(pdf_export.gerar_pdf(
        dados["ficha_pdf"], npc, relatorio, dados["genero"]["nome"]
    ))).get_fields()
    return npc, relatorio, {nome: campo.get("/V") for nome, campo in campos.items()}


def numero(valor):
    return int(valor) if valor not in (None, "") else 0


@pytest.mark.parametrize("arquetipo, np", CASOS)
def test_cabecalho_e_habilidades(dados, arquetipo, np):
    npc, relatorio, campos = gerar_pdf(dados, arquetipo, np)
    assert campos["Herói"] == npc["nome"]
    assert campos["Nível de Poder"] == str(np)
    assert numero(campos["Força"]) == relatorio["valores"]["habilidades"]["For"]
    assert numero(campos["Total"]) == relatorio["total_pp"]


@pytest.mark.parametrize("arquetipo, np", CASOS)
def test_dados_do_modelo_foram_apagados(dados, arquetipo, np):
    _, _, campos = gerar_pdf(dados, arquetipo, np)
    assert campos["Jogador"] in (None, "")
    assert "Tsuki" not in str(campos["Identidade"])


@pytest.mark.parametrize("arquetipo, np", CASOS)
def test_valores_obedecem_as_formulas_do_pdf(dados, arquetipo, np):
    """Se o leitor de PDF recalcular os campos, nada pode mudar."""
    _, _, c = gerar_pdf(dados, arquetipo, np)
    for defesa, hab in (("Esquiva", "Agilidade"), ("Aparar", "Luta"), ("Fortitude", "Vigor"),
                        ("Vontade", "Prontidão")):
        assert numero(c[defesa]) == numero(c[hab]) + numero(c[f"Grad.{defesa}"]) + numero(c[f"{defesa} Outros"])
    assert numero(c["Resistência"]) == numero(c["Vigor"]) + numero(c["Mod de Armadura"]) + numero(c["Resistência Outros"])
    for prefixo in pdf_export.PREFIXO_DA_PERICIA.values():
        if c.get(f"{prefixo}Total"):
            assert numero(c[f"{prefixo}Total"]) == (numero(c[f"{prefixo}Hab"]) + numero(c[f"{prefixo}Per"])
                                                     + numero(c[f"{prefixo}Outros"]))
    for _, prefixo, sufixo, linhas in pdf_export.LINHAS_ESPECIALIZADAS.values():
        for n in range(1, linhas + 1):
            if c.get(f"{prefixo}Total {n}"):
                assert numero(c[f"{prefixo}Total {n}"]) == (numero(c[f"{prefixo}Hab {n}"])
                                                            + numero(c[f"{prefixo}Per {n}"])
                                                            + numero(c[f"{prefixo}{sufixo} {n}"]))


def test_cavalgar_usa_agilidade_na_ficha(dados):
    # Especialidade: Cavalgar usa Agilidade; a ficha soma Intelecto, então a diferença vai em "Outros".
    npc, relatorio, c = gerar_pdf(dados, "policial", 5)
    linha = next(n for n in range(1, 5) if c.get(f"Especialidade {n}") == "Cavalgar")
    assert numero(c[f"EspTotal {linha}"]) == relatorio["valores"]["pericias"]["Especialidade: Cavalgar"]["total"]


def test_formula_do_combate_a_distancia_corrigida(dados):
    npc, _ = generator.gerar_npc(dados, "capanga", 3, "aleatorio", random.Random(1))
    relatorio = validator.validar(npc["ficha"], 3, dados["equipamentos"])
    leitor = PdfReader(io.BytesIO(pdf_export.gerar_pdf(
        dados["ficha_pdf"], npc, relatorio, dados["genero"]["nome"]
    )))
    for pagina in leitor.pages:
        for anotacao in pagina.get("/Annots", []):
            anotacao = anotacao.get_object()
            if anotacao.get("/T") == "CaDTotal 2":
                js = str(anotacao["/AA"]["/C"].get_object()["/JS"])
                assert '"CaDPer 2"' in js and '"CaD 2"' not in js
                return
    pytest.fail("Campo CaDTotal 2 não encontrado.")


def test_rotas_de_download(dados):
    cliente = app.app.test_client()
    grupo = cliente.post("/api/gerar", json={"arquetipo": "capanga", "np": 4, "estilo": "aleatorio",
                                             "quantidade": 3, "semente": 1}).get_json()["npcs"]

    resposta = cliente.post("/api/ficha.pdf", json={"npc": grupo[0]})
    assert resposta.status_code == 200
    assert resposta.mimetype == "application/pdf"
    assert resposta.data.startswith(b"%PDF")

    resposta = cliente.post("/api/fichas.zip", json={"npcs": grupo})
    assert resposta.status_code == 200
    nomes = zipfile.ZipFile(io.BytesIO(resposta.data)).namelist()
    assert len([n for n in nomes if n.endswith(".pdf")]) == 3
    assert "todas_as_fichas.txt" in nomes


def test_serie_da_ficha_reflete_o_genero():
    dados_fantasia = app.DADOS_POR_GENERO["fantasia"]
    arquetipo_id = next(iter(dados_fantasia["arquetipos"]))
    arquetipo = dados_fantasia["arquetipos"][arquetipo_id]
    np = generator.nps_disponiveis(dados_fantasia, arquetipo)[0]
    npc, motivo = generator.gerar_npc(
        dados_fantasia, arquetipo_id, np, "aleatorio", random.Random(1)
    )
    assert npc is not None, motivo
    relatorio = validator.validar(npc["ficha"], np, dados_fantasia["equipamentos"])

    resposta = app.app.test_client().post("/api/ficha.pdf", json={"npc": npc})
    assert resposta.status_code == 200
    campos = PdfReader(io.BytesIO(resposta.data)).get_fields()

    assert campos["Series"].get("/V") == "Fantasia medieval em Mutantes & Malfeitores"


def test_pdf_do_bruxo_inclui_graduacoes_e_efeitos_das_magias():
    dados = app.DADOS_POR_GENERO["fantasia"]
    complicacoes = [
        {"categoria": "motivacao", "nome": "Fé", "detalhe": ""},
        {"categoria": "complicacao", "nome": "Honra", "detalhe": ""},
    ]
    bruxo = player.gerar_personagem(
        dados, "bruxo", 7, "cacador_monstros", "classe_media", complicacoes,
        nome="Osric da Ponte", rng=random.Random(1),
    )
    pdf = pdf_export.gerar_pdf(
        dados["ficha_pdf"], bruxo, bruxo["validacao"], dados["genero"]["nome"]
    )
    leitor = PdfReader(io.BytesIO(pdf))
    campos = leitor.get_fields()
    linhas = "\n".join(
        str(campos[f"Poderes e Dispositivos {n}"].get("/V") or "")
        for n in range(1, pdf_export.LINHAS["poderes"] + 1)
    )

    assert "Igni 7" in linhas
    assert "Aard 6" in linhas
    assert "Aflição" in linhas
    assert "indefeso e caído" in linhas
    assert "Arranjo Sinais: efeito principal" in linhas
    assert "efeito alternativo (1 PP)" in linhas
    for pagina in leitor.pages:
        for referencia in pagina.get("/Annots", []):
            anotacao = referencia.get_object()
            if str(anotacao.get("/T", "")).startswith("Poderes e Dispositivos "):
                assert anotacao["/DA"] == "/Comi 0 Tf 0 g"


def test_pdf_mostra_o_saldo_de_dinheiro_em_notas_e_condicoes(dados):
    foco = dados["jogador"]["arquetipos"]["pistoleiro"]["focos"][0]["id"]
    pj = player.gerar_personagem(
        dados, "pistoleiro", 6, foco, "classe_media",
        [{"categoria": "motivacao", "nome": "Justiça", "detalhe": ""},
         {"categoria": "complicacao", "nome": "Honra", "detalhe": ""}],
        rng=random.Random(1),
    )
    campos = PdfReader(io.BytesIO(pdf_export.gerar_pdf(
        dados["ficha_pdf"], pj, pj["validacao"], dados["genero"]["nome"]
    ))).get_fields()
    notas = campos["Notas & Condições"].get("/V")

    assert "Dinheiro:" in notas
    assert "iniciais" in notas
    assert "gastos" in notas
    assert f"sobram {formatter.dolares(pj['dinheiro']['restante'])}." in notas
    assert all("Dinheiro:" not in str(campos[f"Equipamento {n}"].get("/V") or "")
               for n in range(1, pdf_export.LINHAS["equipamento"] + 1))


def test_download_sem_ficha_da_erro_controlado():
    resposta = app.app.test_client().post("/api/ficha.pdf", json={})
    assert resposta.status_code == 400
