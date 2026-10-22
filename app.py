"""Servidor Flask do gerador de NPCs.

Rode com:  python app.py
A página abre sozinha no navegador.
"""

import io
import os
import random
import re
import subprocess
import threading
import unicodedata
import webbrowser
import zipfile

from flask import Flask, jsonify, render_template, request, send_file

from nucleo import data_loader, docx_export, formatter, generator, livros, pdf_export, player, validator

app = Flask(__name__)
PASTA_LIVROS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "livros")
PLANILHAS_POR_GENERO = {
    "faroeste": {
        "armas": os.path.join(PASTA_LIVROS, "faroeste", "armas.xlsx"),
        "itens": os.path.join(PASTA_LIVROS, "faroeste", "itens.xlsx"),
    },
    "fantasia": {
        "armas": os.path.join(PASTA_LIVROS, "fantasia", "armas.xlsx"),
        "itens": os.path.join(PASTA_LIVROS, "fantasia", "itens.xlsx"),
    },
}
NOMES_DAS_PLANILHAS = {"armas": "Armas", "itens": "Itens"}

# Versão mostrada no rodapé. Suba a cada entrega: 1.0 original, 1.1 passo a passo, 1.2 quantidades, 1.3 fantasia,
# 1.4 distribuição dos pontos parecida com a dos arquétipos do livro, 1.5 subclasses e tipo de NPC, 1.6 goblinoides e caçador de monstros, 1.7 livros do faroeste e da fantasia.
VERSAO = "1.7.0"


def _commit_atual():
    """Commit em execução: o Render informa em RENDER_GIT_COMMIT; rodando local, pergunta ao git."""
    commit = os.environ.get("RENDER_GIT_COMMIT", "")
    if not commit:
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=2,
                                    cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            commit = ""
    return commit[:7]


COMMIT = _commit_atual()


@app.context_processor
def versao_do_programa():
    # Livros (do Jogador e do Mestre) de cada gênero, para os botões de download e o rodapé.
    todos_os_livros = [{"genero": g, "nome": d["genero"]["nome"], "tipos": livros.livros_disponiveis(g)}
                       for g, d in DADOS_POR_GENERO.items()]
    todas_as_planilhas = [
        {"genero": genero_id, "nome": DADOS_POR_GENERO[genero_id]["genero"]["nome"],
         "tipos": [tipo for tipo, caminho in tipos.items() if os.path.isfile(caminho)]}
        for genero_id, tipos in PLANILHAS_POR_GENERO.items() if genero_id in DADOS_POR_GENERO
    ]
    return {"versao": VERSAO, "commit": COMMIT, "livros": [l for l in todos_os_livros if l["tipos"]],
            "nomes_dos_livros": livros.TIPOS, "planilhas": [p for p in todas_as_planilhas if p["tipos"]],
            "nomes_das_planilhas": NOMES_DAS_PLANILHAS}

MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

DADOS_POR_GENERO, ERROS_POR_GENERO = data_loader.carregar_todos()
GENERO_PADRAO = "faroeste" if "faroeste" in DADOS_POR_GENERO else next(iter(DADOS_POR_GENERO), None)


def _dados(genero_id=None):
    """Dados do gênero pedido (ou do padrão)."""
    genero_id = genero_id or GENERO_PADRAO
    if genero_id not in DADOS_POR_GENERO:
        raise generator.GeneratorError(f"Gênero '{genero_id}' não existe ou tem erros nos dados.")
    return DADOS_POR_GENERO[genero_id]


def opcoes_da_interface(DADOS):
    """O que a página precisa para montar os campos do formulário de um gênero."""
    config = DADOS["configuracoes"]
    return {
        "genero": DADOS["genero"],
        "generos": [{"id": g, "nome": d["genero"]["nome"], "descricao": d["genero"]["descricao"]}
                    for g, d in DADOS_POR_GENERO.items()],
        "arquetipos": [{"id": a["id"], "nome": a["nome"], "descricao": a["descricao"],
                        "nps": generator.nps_disponiveis(DADOS, a), "tipos": _tipos_para_a_tela(DADOS, a)}
                       for a in DADOS["arquetipos"].values()],
        "estilos": [{"id": e["id"], "nome": e["nome"], "descricao": e["descricao"]}
                    for e in DADOS["estilos"].values()],
        "quantidade_padrao": config.get("quantidade_padrao", 4),
        "quantidade_maxima": config["quantidade_maxima"],
        "pdf_disponivel": DADOS["ficha_pdf"] is not None,
        "jogador": {
            "arquetipos": [{"id": a["id"], "nome": a["nome"], "conceito": a["conceito"],
                            "focos": [{"id": f["id"], "nome": f["nome"], "descricao": f["descricao"],
                                       "vantagens": f.get("vantagens", []), "armas": f.get("armas", []),
                                       "itens": f.get("itens", []), "implantes": f.get("implantes", []),
                                       "implantes_da_escolha": player.implantes_da_escolha(a, f),
                                       "substitui": f.get("substitui", {}),
                                       "falhas": f.get("falhas", [])}
                                      for f in a["focos"]],
                            "sugestoes": a["sugestoes"],
                            "vantagens_essenciais": a["vantagens_essenciais"],
                            "vantagens_opcionais": a["vantagens_opcionais"],
                            "armas": a["armas"], "itens": a["itens"],
                            "implantes": a.get("implantes", {"essenciais": [], "opcionais": []})}
                           for a in DADOS["jogador"]["arquetipos"].values()],
            "catalogo": [_item_para_a_tela(i) for i in player.catalogo_do_jogador(DADOS)],
            "itens_basicos": player.itens_basicos(DADOS),
            "quantidade_maxima": player.QUANTIDADE_MAXIMA,
            # "dinheiro": itens pagos em dólares; "pontos": itens pagos com a vantagem Equipamento.
            "equipamento_modo": config.get("equipamento", "dinheiro"),
            "moeda": config.get("moeda", "$"),
            "implantes_em_dinheiro": player.implantes_em_dinheiro(DADOS),
            "rotulo_poderes": config.get("rotulo_poderes", "Poderes"),
            "rotulo_arquetipo": config.get("rotulo_arquetipo", "Arquétipo"),
            "rotulo_foco": config.get("rotulo_foco", "Foco"),
            "implantes": [{"id": i["id"], "nome": i["nome"], "descricao": i.get("descricao", ""),
                           "categoria": i.get("categoria", ""), "custo": i["poder"]["custo_informado"],
                           # Poderes que acompanham o NP mudam de graduação e de custo com ele.
                           "por_np": {np: _poder_no_np(DADOS, i["id"], np) for np in config["nps_jogador"]},
                           "arranjo": i.get("arranjo"),
                           "preco": i.get("preco"), "preco_estimado": bool(i.get("preco_estimado")),
                           "estatistica": i["poder"]["nome"]}
                          for i in player.implantes_do_jogador(DADOS)],
            "racas": [{"id": r["id"], "nome": r["nome"], "descricao": r["descricao"],
                       "tracos": player.tracos_da_raca(DADOS, r),
                       "custo_por_np": {np: player.custo_da_raca(DADOS, r, np) for np in config["nps_jogador"]}}
                      for r in player.racas(DADOS)],
            "vantagens": [{"nome": v["nome"], "tipo": v["tipo"], "efeito": v["efeito"], "faroeste": v["faroeste"]}
                          for v in player.vantagens_do_jogador(DADOS)],
            "nps": config["nps_jogador"],
            "np_padrao": config.get("np_padrao_jogador", config["nps_jogador"][0]),
            "riqueza": [{"id": r["id"], "nome": r["nome"], "descricao": r["descricao"], "dinheiro": r["dinheiro"],
                         "beneficio": r["beneficio"], "ajuste_de_pontos": r["ajuste_de_pontos"]}
                        for r in DADOS["jogador"]["riqueza"]],
            "motivacoes": DADOS["complicacoes"]["motivacoes"],
            "complicacoes": DADOS["complicacoes"]["complicacoes"],
        },
    }


def _tipos_para_a_tela(DADOS, arquetipo):
    """Tipos (módulos principais) do arquétipo de NPC, com os NPs em que cada um pode aparecer."""
    tipos = {}
    for np in generator.nps_disponiveis(DADOS, arquetipo):
        for mod in generator.tipos_do_arquetipo(DADOS, arquetipo["id"], np):
            tipos.setdefault(mod["id"], {"id": mod["id"], "nome": mod["nome"], "descricao": mod["descricao"],
                                         "nps": []})["nps"].append(np)
    return list(tipos.values())


def _poder_no_np(DADOS, implante_id, np):
    poder = player.poder_do_genero(DADOS, implante_id, np)
    return {"custo": poder["custo_informado"], "estatistica": poder["nome"]}


def _nome_no_kit(item_id, quantidade):
    for dados in DADOS_POR_GENERO.values():
        if item_id in dados["equipamentos"]:
            nome = dados["equipamentos"][item_id]["nome"]
            return f"{nome} ×{quantidade}" if quantidade > 1 else nome
    return item_id


def _item_para_a_tela(item):
    """Resumo de um item do catálogo para a lista de compras da ficha de jogador."""
    ataque = item.get("ataque")
    resumo = ""
    if ataque:
        efeito = ataque.get("efeito_nome", "Dano")
        if ataque["tipo"] == "area":
            resumo = f"{efeito} {ataque['efeito']} em área"
        else:
            forca = " + For" if ataque.get("soma_forca") else ""
            resumo = f"{efeito} {ataque['efeito']}{forca} · {ataque['pericia'].split(': ')[1]}"
        if item.get("classe"):
            resumo = f"{item['classe']} · {resumo}"
    elif item.get("protecao"):
        resumo = f"+{item['protecao']} Resistência"
    elif item.get("kit"):
        nomes = [_nome_no_kit(item_id, quantidade) for item_id, quantidade in player.conteudo_do_kit(item)]
        resumo = "Contém: " + ", ".join(nomes)
    return {"id": item["id"], "nome": item["nome"], "categoria": item["categoria"], "preco": item.get("preco"),
            "custo": item.get("custo"), "preco_estimado": bool(item.get("preco_estimado")),
            "categoria_de_preco": item.get("categoria_de_preco", ""),
            "resumo": resumo, "notas": item.get("notas", ""), "descricao": item.get("descricao", ""),
            "municao": item.get("municao"), "quantidade": player.tem_quantidade(item)}


def _preparar(npc):
    """Acrescenta os textos de exibição a um NPC gerado."""
    npc["exibicao"] = formatter.exibicao(npc)
    npc["texto"] = formatter.texto(npc)
    return npc


def _parametros(corpo):
    try:
        return (str(corpo["arquetipo"]), int(corpo["np"]), str(corpo["estilo"]))
    except (KeyError, TypeError, ValueError):
        raise generator.GeneratorError("Informe arquétipo, NP e estilo válidos.")


def _tipo(corpo):
    """Tipo de NPC escolhido na tela (módulo principal); vazio = sortear."""
    return str(corpo.get("tipo") or "") or None


def _rng(corpo):
    semente = corpo.get("semente")
    return random.Random(semente) if semente not in (None, "") else random.Random()


@app.errorhandler(generator.GeneratorError)
def erro_de_geracao(erro):
    return jsonify({"erro": str(erro)}), 400


@app.get("/")
def pagina_inicial():
    genero_id = request.args.get("genero") or GENERO_PADRAO
    erros = [m for mensagens in ERROS_POR_GENERO.values() for m in mensagens]
    if genero_id not in DADOS_POR_GENERO:
        return render_template("index.html", opcoes=None,
                               erros=erros or [f"Gênero '{genero_id}' não encontrado."]), 500
    return render_template("index.html", opcoes=opcoes_da_interface(DADOS_POR_GENERO[genero_id]), erros=erros)


@app.post("/api/gerar")
def gerar():
    corpo = request.get_json(silent=True) or {}
    DADOS = _dados(corpo.get("genero"))
    arquetipo, np, estilo = _parametros(corpo)
    try:
        quantidade = int(corpo.get("quantidade", 1))
    except (TypeError, ValueError):
        raise generator.GeneratorError("A quantidade precisa ser um número.")
    resultado = generator.gerar_grupo(DADOS, arquetipo, np, estilo, quantidade, _rng(corpo), tipo=_tipo(corpo))
    resultado["npcs"] = [_preparar(npc) for npc in resultado["npcs"]]
    return jsonify(resultado)


@app.post("/api/regerar")
def regerar():
    """Troca um único NPC do grupo, evitando as combinações e nomes que já estão na tela."""
    corpo = request.get_json(silent=True) or {}
    DADOS = _dados(corpo.get("genero"))
    arquetipo, np, estilo = _parametros(corpo)
    usadas = {frozenset(c) for c in corpo.get("combinacoes", [])}
    nomes = set(corpo.get("nomes", []))
    npc, motivo = generator.gerar_npc(DADOS, arquetipo, np, estilo, _rng(corpo),
                                      combinacoes_usadas=usadas, nomes_usados=nomes, tipo=_tipo(corpo))
    if npc is None:
        return jsonify({"erro": motivo}), 422
    return jsonify({"npc": _preparar(npc)})


@app.post("/api/jogador/gerar")
def gerar_jogador():
    corpo = request.get_json(silent=True) or {}
    DADOS = _dados(corpo.get("genero"))
    try:
        np = int(corpo["np"])
        arquetipo, foco = str(corpo["arquetipo"]), str(corpo["foco"])
        riqueza = str(corpo.get("riqueza") or "")
    except (KeyError, TypeError, ValueError):
        raise generator.GeneratorError("Informe arquétipo, NP, foco e condição financeira.")
    personagem = player.gerar_personagem(
        DADOS, arquetipo, np, foco, riqueza, corpo.get("complicacoes", []),
        nome=str(corpo.get("nome", "")).strip() or None, jogador=str(corpo.get("jogador", "")).strip(),
        rng=_rng(corpo), equipamento=corpo.get("equipamento"), vantagens=corpo.get("vantagens"),
        implantes=corpo.get("implantes"), raca=str(corpo.get("raca") or "") or None)
    return jsonify({"personagem": _preparar(personagem)})


@app.post("/api/jogador/complicacoes")
def sortear_complicacoes():
    corpo = request.get_json(silent=True) or {}
    DADOS = _dados(corpo.get("genero"))
    return jsonify({"complicacoes": player.sortear_complicacoes(DADOS, str(corpo.get("arquetipo", "")), _rng(corpo),
                                                                foco_id=str(corpo.get("foco") or "") or None)})


def _nome_de_arquivo(texto):
    """'Josiah "Corvo" Sutter, o Bruto' -> 'josiah_corvo_sutter_o_bruto'."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_") or "npc"


def _relatorio(npc):
    """Recalcula a validação no servidor: não confia nos números vindos da página."""
    DADOS = _dados(npc.get("genero"))
    try:
        return validator.validar(npc["ficha"], int(npc["np_pretendido"]), DADOS["equipamentos"],
                                 npc.get("regras_validacao"))
    except (KeyError, TypeError, ValueError) as erro:
        raise generator.GeneratorError(f"Ficha incompleta ou inválida para exportar: {erro}.")


def _pdf_do_npc(npc):
    DADOS = _dados(npc.get("genero"))
    if DADOS["ficha_pdf"] is None:
        raise generator.GeneratorError("O modelo de ficha em PDF não foi encontrado na pasta data/.")
    return pdf_export.gerar_pdf(DADOS["ficha_pdf"], npc, _relatorio(npc), DADOS["genero"]["nome"])


def _docx_dos_npcs(npcs):
    return docx_export.gerar_docx([(npc, _relatorio(npc)) for npc in npcs])


def _npc_do_pedido():
    npc = (request.get_json(silent=True) or {}).get("npc")
    if not npc:
        raise generator.GeneratorError("Nenhuma ficha enviada.")
    return npc


# Livros já montados: {(gênero, tipo, data do texto): bytes}. Montar um livro leva alguns segundos.
_LIVROS_PRONTOS = {}


@app.get("/livros/<genero_id>/<tipo>.docx")
def baixar_livro(genero_id, tipo):
    DADOS = _dados(genero_id)
    caminho = livros.caminho_do_texto(genero_id, tipo)
    if tipo not in livros.TIPOS or not caminho.is_file():
        return jsonify({"erro": "Livro não encontrado."}), 404
    chave = (genero_id, tipo, caminho.stat().st_mtime)
    if chave not in _LIVROS_PRONTOS:
        _LIVROS_PRONTOS[chave] = livros.gerar_livro(DADOS, tipo, VERSAO)
    return send_file(io.BytesIO(_LIVROS_PRONTOS[chave]), mimetype=MIME_DOCX, as_attachment=True,
                     download_name=f"{_nome_de_arquivo(livros.TIPOS[tipo])}_{genero_id}.docx")


@app.get("/planilhas/<genero_id>/<tipo>.xlsx")
def baixar_planilha(genero_id, tipo):
    caminho = PLANILHAS_POR_GENERO.get(genero_id, {}).get(tipo)
    if tipo not in NOMES_DAS_PLANILHAS or not caminho or not os.path.isfile(caminho):
        return jsonify({"erro": "Planilha não encontrada."}), 404
    return send_file(caminho, mimetype=MIME_XLSX, as_attachment=True,
                     download_name=f"{tipo}_{genero_id}.xlsx")


@app.post("/api/ficha.pdf")
def baixar_pdf():
    npc = _npc_do_pedido()
    return send_file(io.BytesIO(_pdf_do_npc(npc)), mimetype="application/pdf", as_attachment=True,
                     download_name=f"{_nome_de_arquivo(npc.get('nome', 'npc'))}.pdf")


@app.post("/api/ficha.docx")
def baixar_docx():
    npc = _npc_do_pedido()
    return send_file(io.BytesIO(_docx_dos_npcs([npc])), mimetype=MIME_DOCX, as_attachment=True,
                     download_name=f"{_nome_de_arquivo(npc.get('nome', 'npc'))}.docx")


@app.post("/api/fichas.zip")
def baixar_zip():
    """Todas as fichas do grupo: PDF e DOCX de cada NPC, um DOCX com todos e um TXT com todos."""
    npcs = (request.get_json(silent=True) or {}).get("npcs") or []
    if not npcs:
        raise generator.GeneratorError("Nenhuma ficha enviada.")
    pacote = io.BytesIO()
    with zipfile.ZipFile(pacote, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:
        nomes_usados = set()
        for npc in npcs:
            nome = _nome_de_arquivo(npc.get("nome", "npc"))
            while nome in nomes_usados:
                nome += "_2"
            nomes_usados.add(nome)
            arquivo_zip.writestr(f"docx/{nome}.docx", _docx_dos_npcs([npc]))
            if _dados(npc.get("genero"))["ficha_pdf"]:
                arquivo_zip.writestr(f"pdf/{nome}.pdf", _pdf_do_npc(npc))
        arquivo_zip.writestr("todas_as_fichas.docx", _docx_dos_npcs(npcs))
        separador = "\n\n" + "-" * 60 + "\n\n"
        arquivo_zip.writestr("todas_as_fichas.txt", separador.join(npc.get("texto", "") for npc in npcs))
    pacote.seek(0)
    return send_file(pacote, mimetype="application/zip", as_attachment=True, download_name="fichas_npcs.zip")


if __name__ == "__main__":
    porta = _dados()["configuracoes"].get("porta", 5000) if DADOS_POR_GENERO else 5000
    endereco = f"http://127.0.0.1:{porta}/"
    # O recarregador do Flask roda o arquivo duas vezes; só abre o navegador na primeira.
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Timer(1.0, webbrowser.open, args=[endereco]).start()
    print(f"Gerador de NPCs rodando em {endereco} (Ctrl+C para parar)")
    app.run(host="127.0.0.1", port=porta, debug=False)
