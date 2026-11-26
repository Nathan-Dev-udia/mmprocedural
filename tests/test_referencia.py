"""Referência do personagem: a página extra do PDF, do DOCX e do TXT que explica o que a ficha tem."""

import io
import random
import zipfile

import pytest
from docx import Document
from pypdf import PdfReader

import app
from nucleo import data_loader, docx_export, generator, player, referencia, referencia_pdf, validator

COMPLICACOES = [{"categoria": "motivacao", "nome": "Fé", "detalhe": ""},
                {"categoria": "complicacao", "nome": "Honra", "detalhe": "Nunca quebra a palavra dada."}]


@pytest.fixture(scope="module")
def fantasia():
    return data_loader.carregar_genero("fantasia")


@pytest.fixture(scope="module")
def bruxo(fantasia):
    return player.gerar_personagem(fantasia, "bruxo", 7, "cacador_monstros", "classe_media", COMPLICACOES,
                                   rng=random.Random(1), variante="lobo")


def _secao(ref, titulo):
    return next(s for s in ref["secoes"] if s["titulo"] == titulo)


def _item(secao, nome):
    return next(i for i in secao["itens"] if i["nome"].startswith(nome))


def test_vantagens_trazem_o_que_fazem(fantasia, bruxo):
    ref = referencia.montar(bruxo, fantasia)
    vantagens = _secao(ref, "Vantagens")
    assert len(vantagens["itens"]) == len(bruxo["ficha"]["vantagens"])
    assert "medo" in _item(vantagens, "Destemido")["linhas"][0]
    assert all(item["linhas"][0] for item in vantagens["itens"])


def test_vantagem_com_detalhe_acha_a_descricao_da_base(fantasia, bruxo):
    pj = dict(bruxo, ficha=dict(bruxo["ficha"], vantagens={"Ambiente Favorito (floresta)": 1}))
    item = _secao(referencia.montar(pj, fantasia), "Vantagens")["itens"][0]
    assert "ambiente" in item["linhas"][0].lower()


def test_sinais_explicam_teste_custo_e_arranjo(fantasia, bruxo):
    ref = referencia.montar(bruxo, fantasia)
    poderes = _secao(ref, "Magias e dons")
    igni = " ".join(_item(poderes, "Igni")["linhas"])
    assert "Esquiva CD 17" in igni and "Resistência CD 22" in igni   # Dano 7 em área
    assert "+2 PP por graduação" in igni
    aard = " ".join(_item(poderes, "Aard")["linhas"])
    assert "sozinho custaria 12 PP" in aard and "15 PP" in aard
    assert "Arranjo" in poderes["nota"] and "Sinais" in poderes["nota"]
    metabolismo = " ".join(_item(poderes, "Metabolismo")["linhas"])
    assert "Imunidade" in metabolismo


def test_itens_trazem_estatistica_e_descricao(fantasia, bruxo):
    equipamento = _secao(referencia.montar(bruxo, fantasia), "Equipamento")
    nomes = [i["nome"] for i in equipamento["itens"]]
    assert not any(n.startswith("Kit de bruxo") for n in nomes)   # o kit vem aberto, peça por peça
    espada = " ".join(_item(equipamento, "Espada de prata")["linhas"])
    assert "Aparar" in espada and "prata" in espada
    assert "Proteção +2" in " ".join(_item(equipamento, "Couro batido")["linhas"])
    assert "Recupera" in " ".join(_item(equipamento, "Poção Andorinha")["linhas"])


def test_termos_so_os_que_aparecem(fantasia, bruxo):
    termos = _secao(referencia.montar(bruxo, fantasia), "Termos de regra")
    nomes = {i["nome"] for i in termos["itens"]}
    assert {"Dano", "Aflição", "Área", "Cone", "Sustentado", "Vulnerável", "Caído", "Versátil"} <= nomes
    assert "Voo" not in nomes and "Incapacitado" not in nomes


def test_texto_tem_todas_as_secoes(fantasia, bruxo):
    texto = referencia.texto(referencia.montar(bruxo, fantasia))
    for titulo in ("VANTAGENS", "MAGIAS E DONS", "EQUIPAMENTO", "TERMOS DE REGRA"):
        assert titulo in texto


def test_npc_tambem_ganha_referencia(dados):
    npc, _ = generator.gerar_npc(dados, "policial", 5, "aleatorio", random.Random(1))
    relatorio = validator.validar(npc["ficha"], 5, dados["equipamentos"])
    ref = referencia.montar(npc, dados, relatorio)
    assert ref["secoes"]
    assert referencia_pdf.gerar_paginas(ref)


def test_sem_nada_para_explicar_nao_gera_pagina():
    vazia = {"titulo": "Referência: x", "subtitulo": "", "secoes": []}
    assert referencia_pdf.gerar_paginas(vazia) is None
    assert referencia.texto(vazia) == ""


def test_docx_ganha_a_pagina_de_referencia(fantasia, bruxo):
    ref = referencia.montar(bruxo, fantasia)
    doc = Document(io.BytesIO(docx_export.gerar_docx([(bruxo, bruxo["validacao"], ref)])))
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert ref["titulo"] in texto and "Igni" in texto and "Termos de regra" in texto


def test_rotas_levam_a_referencia():
    cliente = app.app.test_client()
    resposta = cliente.post("/api/jogador/gerar", json={
        "genero": "fantasia", "arquetipo": "bruxo", "foco": "cacador_monstros", "np": 7,
        "riqueza": "classe_media", "complicacoes": COMPLICACOES, "variante": "lobo", "semente": 1})
    pj = resposta.get_json()["personagem"]
    assert "TERMOS DE REGRA" in pj["referencia_texto"]
    paginas = PdfReader(io.BytesIO(cliente.post("/api/ficha.pdf", json={"npc": pj}).data)).pages
    assert len(paginas) > 2
    texto_da_referencia = "".join(p.extract_text() for p in paginas[2:])
    assert "REFERÊNCIA DO PERSONAGEM" in texto_da_referencia and pj["nome"] in texto_da_referencia
    pacote = zipfile.ZipFile(io.BytesIO(cliente.post("/api/fichas.zip", json={"npcs": [pj]}).data))
    assert "TERMOS DE REGRA" in pacote.read("todas_as_fichas.txt").decode("utf-8")
