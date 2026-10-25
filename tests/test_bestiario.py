"""Testes do Bestiário como aba, filtros por gênero/tipo/família/NP e geração de PDF."""

from pathlib import Path
import app
from nucleo import bestiario, bestiario_pdf


def test_catalogo_contem_criaturas_e_variantes():
    bestiario.limpar_cache()
    lista = bestiario.lista()
    # Temos pelo menos 40 criaturas agora incluindo Tomo dos Monstros e monstros classicos
    assert len(lista) >= 40
    assert len({c["id"] for c in lista}) == len(lista)
    
    # Conferência da família Goblin
    goblins = [c for c in lista if c["familia"] == "Goblin"]
    assert len(goblins) >= 10
    assert any(g["variante"] == "De Areia (Goblestiário)" for g in goblins)
    assert any(g["variante"] == "Elétrico (Goblestiário)" for g in goblins)
    assert any(g["variante"] == "Das Ventanias (Goblestiário)" for g in goblins)
    assert any(g["variante"] == "Quebra-Gelo (Goblestiário)" for g in goblins)
    assert any(g["variante"] == "Tóxico (Goblestiário)" for g in goblins)

    # Conferencia de familias expandidas do Passo 3
    assert any(c["id"] == "fantasia/mortos_vivos/carnical_darakhul" for c in lista)
    assert any(c["id"] == "fantasia/monstruosidades/troll" for c in lista)
    assert any(c["id"] == "fantasia/monstruosidades/minotauro" for c in lista)
    assert any(c["id"] == "fantasia/construtos/golem_pedra" for c in lista)


def test_filtros_de_genero_familias_tipos_e_faixas():
    generos = bestiario.generos()
    assert any(g["id"] == "fantasia" and g["quantidade"] >= 40 for g in generos)

    fams = bestiario.familias()
    assert any(f["id"] == "Goblin" for f in fams)
    assert any(f["id"] == "Hobgoblin" for f in fams)
    assert any(f["id"] == "Bugbear" for f in fams)
    assert any(f["id"] == "Lobo" for f in fams)
    assert any(f["id"] == "Esqueleto" for f in fams)
    assert any(f["id"] == "Carniçal" for f in fams)
    assert any(f["id"] == "Bruxa" for f in fams)
    assert any(f["id"] == "Troll" for f in fams)

    tipos = bestiario.tipos()
    assert any(t["id"] == "Goblinoide" for t in tipos)
    assert any(t["id"] == "Morto-Vivo" for t in tipos)
    assert any(t["id"] == "Besta" for t in tipos)
    assert any(t["id"] == "Monstruosidade" for t in tipos)
    assert any(t["id"] == "Construto" for t in tipos)

    faixas = bestiario.faixas_np()
    assert any(f["id"] == "1-3" and f["quantidade"] > 0 for f in faixas)
    assert any(f["id"] == "4-6" and f["quantidade"] > 0 for f in faixas)
    assert any(f["id"] == "7-9" and f["quantidade"] > 0 for f in faixas)


def test_ficha_completa_com_variantes_da_familia():
    ficha = bestiario.ficha("fantasia/goblins/goblin_saqueador")
    assert ficha is not None
    assert ficha["nome"] == "Goblin Saqueador"
    assert ficha["familia"] == "Goblin"
    assert ficha["total_variantes"] >= 10
    
    # A lista de variantes tem o chip atual marcado
    atual = next(v for v in ficha["variantes"] if v["atual"])
    assert atual["id"] == "fantasia/goblins/goblin_saqueador"

    # Confere criatura do Goblestiário
    areia = bestiario.ficha("fantasia/goblins/goblin_areia")
    assert areia is not None
    poderes_texto = " ".join(item for s in areia["secoes"] if "Poderes" in s["titulo"] for item in s["itens"])
    assert "Rajada de Areia Cegante" in poderes_texto
    assert "Goblestiário" in areia["fonte"]

    # Confere criatura do Tomo dos Monstros (Carniçal Darakhul)
    darakhul = bestiario.ficha("fantasia/mortos_vivos/carnical_darakhul")
    assert darakhul is not None
    assert "Tomo dos Monstros" in darakhul["fonte"]
    assert darakhul["familia"] == "Carniçal"
    assert darakhul["total_variantes"] >= 2


def test_pagina_aba_e_rotas_api():
    cliente = app.app.test_client()
    
    # Rota direta /bestiario redireciona para a aba
    resp_redirect = cliente.get("/bestiario")
    assert resp_redirect.status_code == 302
    assert "aba=bestiario" in resp_redirect.headers["Location"]

    # Página principal com aba bestiario e checkbox de agrupamento
    resp = cliente.get("/?aba=bestiario")
    assert resp.status_code == 200
    texto = resp.get_data(as_text=True)
    assert 'data-aba="bestiario"' in texto
    assert 'id="aba-bestiario"' in texto
    assert 'id="bestiario-agrupar"' in texto

    # API lista
    resp_api = cliente.get("/api/bestiario")
    assert resp_api.status_code == 200
    criaturas = resp_api.get_json()["criaturas"]
    assert len(criaturas) >= 28

    # API ficha de criatura do Goblestiário
    resp_ficha = cliente.get("/api/bestiario/fantasia/goblins/goblin_eletrico")
    assert resp_ficha.status_code == 200
    assert resp_ficha.get_json()["ficha"]["nome"] == "Goblin Elétrico"


def test_pdf_da_criatura_e_gerado():
    modelo = Path(__file__).parent.parent / "dados" / "comum" / "ficha_editavel.pdf"
    conteudo = bestiario_pdf.gerar_pdf(modelo, "fantasia/goblins/goblin_eletrico")
    assert conteudo is not None
    assert conteudo.startswith(b"%PDF")

    campos = bestiario_pdf.campos_da_criatura("fantasia/goblins/goblin_eletrico")
    assert campos["Herói"] == "Goblin Elétrico"
    assert "Elétrico" in campos["Descrição 1"]

    # Rota de download HTTP
    cliente = app.app.test_client()
    resp_pdf = cliente.get("/bestiario/fantasia/goblins/goblin_eletrico.pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.data.startswith(b"%PDF")
