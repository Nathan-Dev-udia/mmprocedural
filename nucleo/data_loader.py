"""Leitura e conferência dos arquivos JSON da pasta data/.

Se algo estiver errado (campo faltando, ID repetido, referência quebrada,
perícia ou vantagem que não existe), levanta DataError com a lista completa
de problemas, para você corrigir tudo de uma vez.
"""

import json
from pathlib import Path

from . import poderes as poderes_mod
from . import rules

PASTA_DADOS = Path(__file__).parent.parent / "dados"

# Arquivos comuns a todos os gêneros (dados/comum) e arquivos de cada gênero (dados/generos/<id>).
ARQUIVOS_COMUNS = ("styles", "vantagens")
ARQUIVOS_DO_GENERO = ("archetypes", "modules", "equipment", "names", "player", "complications")

STATUS_DADOS = {"validado", "ilustrativo", "pendente", "conceitual"}
PAPEIS = {"principal", "extra", "ambos"}
MODOS_DE_ESTILO = {"uniforme", "preferencia", "tematico"}
TIPOS_DE_ATAQUE = {"corpo", "distancia", "area", "percepcao"}
SECOES_ADICIONA = {"habilidades", "defesas_compradas", "pericias", "vantagens", "equipamento", "poderes"}
SECOES_SUBSTITUI = {"equipamento", "poderes"}
SECOES_REMOVE = {"pericias", "vantagens", "equipamento", "poderes"}


class DataError(Exception):
    """Erro nos arquivos de dados. Guarda todas as mensagens encontradas."""

    def __init__(self, mensagens):
        self.mensagens = mensagens
        super().__init__("Problemas nos arquivos de dados:\n- " + "\n- ".join(mensagens))


def _ler_json(pasta, nome, erros):
    caminho = Path(pasta) / nome
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        erros.append(f"{nome}: arquivo não encontrado em {caminho}.")
    except json.JSONDecodeError as e:
        erros.append(f"{nome}: JSON inválido (linha {e.lineno}, coluna {e.colno}): {e.msg}.")
    return None


def _indexar(lista, nome_arquivo, campos_obrigatorios, erros):
    """Transforma a lista em {id: item}, conferindo campos obrigatórios e IDs repetidos."""
    indice = {}
    if not isinstance(lista, list):
        erros.append(f"{nome_arquivo}: o arquivo deve conter uma lista.")
        return indice
    for posicao, item in enumerate(lista, start=1):
        rotulo = f"{nome_arquivo}, item {posicao} ({item.get('id', 'sem id')})"
        faltando = [c for c in campos_obrigatorios if c not in item]
        if faltando:
            erros.append(f"{rotulo}: faltam os campos {', '.join(faltando)}.")
            continue
        if item["id"] in indice:
            erros.append(f"{nome_arquivo}: o id '{item['id']}' aparece mais de uma vez.")
            continue
        indice[item["id"]] = item
    return indice


def _conferir_tracos(rotulo, secoes, vantagens_validas, equipamentos, erros):
    """Confere habilidades, perícias, vantagens e equipamento citados numa ficha ou módulo."""
    for hab in secoes.get("habilidades", {}):
        if hab not in rules.HABILIDADES:
            erros.append(f"{rotulo}: habilidade desconhecida '{hab}'.")
    for defesa in secoes.get("defesas_compradas", {}):
        if defesa not in rules.DEFESAS_COMPRAVEIS:
            erros.append(f"{rotulo}: defesa '{defesa}' não pode ser comprada (Resistência só sobe com vantagem, "
                         "armadura ou poder).")
    for pericia in secoes.get("pericias", {}):
        if not rules.pericia_valida(pericia):
            erros.append(f"{rotulo}: perícia desconhecida ou sem especialização: '{pericia}'.")
    for vantagem in secoes.get("vantagens", {}):
        if rules.nome_base(vantagem) not in vantagens_validas:
            erros.append(f"{rotulo}: vantagem desconhecida '{vantagem}'.")
    for item in secoes.get("equipamento", []):
        if item not in equipamentos:
            erros.append(f"{rotulo}: equipamento desconhecido '{item}'.")
    for poder_id, poder in secoes.get("poderes", {}).items():
        if "nome" not in poder:
            erros.append(f"{rotulo}: o poder '{poder_id}' não tem nome.")


def _resolver_poderes(rotulo, poderes, catalogo, do_genero, erros):
    """Troca, no lugar, as referências pelo poder pronto:
    {"catalogo": id, "graduacao": n} (catálogo dos livros) ou {"do_genero": id} (powers.json do gênero)."""
    for poder_id, poder in list(poderes.items()):
        if "do_genero" in poder:
            if poder["do_genero"] not in do_genero or "poder" not in do_genero[poder["do_genero"]]:
                erros.append(f"{rotulo}: poder do gênero desconhecido '{poder['do_genero']}'.")
            else:
                poderes[poder_id] = dict(do_genero[poder["do_genero"]]["poder"])
        elif "catalogo" in poder:
            try:
                poderes[poder_id] = poderes_mod.resolver(poder, catalogo)
            except poderes_mod.PoderInvalido as erro:
                erros.append(f"{rotulo}: {erro}")


def _conferir_ataque(rotulo, ataque, erros):
    if ataque.get("tipo") not in TIPOS_DE_ATAQUE:
        erros.append(f"{rotulo}: tipo de ataque inválido '{ataque.get('tipo')}'.")
    if "efeito" not in ataque:
        erros.append(f"{rotulo}: ataque sem 'efeito'.")
    if ataque.get("tipo") in ("corpo", "distancia") and not rules.pericia_valida(ataque.get("pericia", "")):
        erros.append(f"{rotulo}: ataque com perícia inválida '{ataque.get('pericia')}'.")
    defesas_de_salvamento = set(rules.DEFESAS_COMPRAVEIS) | {"Resistência"}
    if ataque.get("resistido_por", "Resistência") not in defesas_de_salvamento:
        erros.append(f"{rotulo}: 'resistido_por' deve ser uma defesa ({', '.join(sorted(defesas_de_salvamento))}).")


def _conferir_passos(rotulo, passos, vantagens_validas, erros):
    """Prioridades no formato 'tipo:nome' (ex.: 'pericia:Percepção', 'habilidade:Des')."""
    for texto in passos:
        tipo, _, nome = texto.partition(":")
        tipo, nome = tipo.strip(), nome.strip()
        if tipo not in rules.TIPOS_DE_PASSO:
            erros.append(f"{rotulo}: prioridade '{texto}' tem tipo inválido (use {', '.join(sorted(rules.TIPOS_DE_PASSO))}).")
        elif tipo == "habilidade" and nome not in rules.HABILIDADES:
            erros.append(f"{rotulo}: prioridade com habilidade desconhecida '{nome}'.")
        elif tipo == "pericia" and not rules.pericia_valida(nome):
            erros.append(f"{rotulo}: prioridade com perícia desconhecida '{nome}'.")
        elif tipo == "defesa" and nome not in rules.DEFESAS_COMPRAVEIS:
            erros.append(f"{rotulo}: prioridade com defesa que não pode ser comprada '{nome}'.")
        elif tipo == "vantagem" and rules.nome_base(nome) not in vantagens_validas:
            erros.append(f"{rotulo}: prioridade com vantagem desconhecida '{nome}'.")


def _conferir_jogador(bruto, vantagens_validas, equipamentos, erros, poderes_do_genero=None):
    """Confere player.json e complications.json; devolve os arquétipos de jogador indexados."""
    jogador = bruto["player"]
    nomes_de_complicacao = {c["nome"] for c in bruto["complications"].get("complicacoes", [])}
    nomes_de_motivacao = {m["nome"] for m in bruto["complications"].get("motivacoes", [])}
    for opcao in jogador.get("riqueza", []):
        for campo in ("id", "nome", "riqueza", "dinheiro", "beneficio", "ajuste_de_pontos"):
            if campo not in opcao:
                erros.append(f"player.json (riqueza {opcao.get('id')}): falta o campo '{campo}'.")
    arquetipos = _indexar(jogador.get("arquetipos", []), "player.json",
                          ["id", "nome", "conceito", "vantagens_essenciais", "vantagens_opcionais",
                           "prioridades", "armas", "itens", "sugestoes", "focos"], erros)
    for arq in arquetipos.values():
        rotulo = f"player.json ({arq['id']})"
        for vantagem in arq["vantagens_essenciais"] + arq["vantagens_opcionais"]:
            if rules.nome_base(vantagem) not in vantagens_validas:
                erros.append(f"{rotulo}: vantagem desconhecida '{vantagem}'.")
        _conferir_passos(rotulo, arq["prioridades"], vantagens_validas, erros)
        listas = [arq["armas"].get("principais", []), arq["armas"].get("secundarias", []),
                  arq["itens"].get("essenciais", []), arq["itens"].get("opcionais", [])]
        if not arq["armas"].get("principais"):
            erros.append(f"{rotulo}: precisa de pelo menos uma arma principal.")
        for item in [i for lista in listas for i in lista]:
            if item not in equipamentos or not equipamentos[item].get("categoria"):
                erros.append(f"{rotulo}: item desconhecido ou sem categoria '{item}'.")
        for motivacao in arq["sugestoes"].get("motivacoes", []):
            if motivacao not in nomes_de_motivacao:
                erros.append(f"{rotulo}: motivação sugerida '{motivacao}' não existe em complications.json.")
        for complicacao in arq["sugestoes"].get("complicacoes", []):
            if complicacao.get("nome") not in nomes_de_complicacao:
                erros.append(f"{rotulo}: complicação sugerida '{complicacao.get('nome')}' não existe em complications.json.")
        implantes = arq.get("implantes", {})
        for implante in (implantes.get("essenciais", []) + implantes.get("opcionais", [])
                         + [i for foco in arq["focos"] for i in foco.get("implantes", [])]):
            if implante not in (poderes_do_genero or {}):
                erros.append(f"{rotulo}: implante/poder desconhecido '{implante}' (não está em powers.json).")
        if not arq["focos"]:
            erros.append(f"{rotulo}: precisa de pelo menos um foco.")
        focos_vistos = set()
        for foco in arq["focos"]:
            rotulo_foco = f"{rotulo}, foco {foco.get('id')}"
            for campo in ("id", "nome", "descricao"):
                if campo not in foco:
                    erros.append(f"{rotulo_foco}: falta o campo '{campo}'.")
            if foco.get("id") in focos_vistos:
                erros.append(f"{rotulo_foco}: id de foco repetido.")
            focos_vistos.add(foco.get("id"))
            for vantagem in foco.get("vantagens", []):
                if rules.nome_base(vantagem) not in vantagens_validas:
                    erros.append(f"{rotulo_foco}: vantagem desconhecida '{vantagem}'.")
            _conferir_passos(rotulo_foco, foco.get("prioridades", []), vantagens_validas, erros)
            for item in foco.get("armas", []) + foco.get("itens", []):
                if item not in equipamentos or not equipamentos[item].get("categoria"):
                    erros.append(f"{rotulo_foco}: item desconhecido ou sem categoria '{item}'.")
    return {"riqueza": jogador.get("riqueza", []), "arquetipos": arquetipos}


def generos_disponiveis(pasta=PASTA_DADOS):
    """IDs dos gêneros: cada subpasta de dados/generos que tem um genero.json."""
    raiz = Path(pasta) / "generos"
    return sorted(p.name for p in raiz.iterdir() if (p / "genero.json").is_file()) if raiz.is_dir() else []


def carregar_todos(pasta=PASTA_DADOS):
    """Carrega todos os gêneros. Devolve ({id: dados}, {id: [erros]})."""
    dados, erros = {}, {}
    for genero_id in generos_disponiveis(pasta):
        try:
            dados[genero_id] = carregar_genero(genero_id, pasta)
        except DataError as erro:
            erros[genero_id] = erro.mensagens
    return dados, erros


def _carregar_poderes(pasta_comum, genero, erros):
    """Catálogo de poderes (dados/comum/poderes/*.json), filtrado pelos perfis que o gênero aceita."""
    permitidos = genero.get("perfis_de_poder", [])
    if not permitidos:
        return {}
    poderes = {}
    for arquivo in sorted((Path(pasta_comum) / "poderes").glob("*.json")):
        conteudo = _ler_json(arquivo.parent, arquivo.name, erros) or {}
        for poder in conteudo.get("poderes", []):
            if permitidos == "todos" or poder.get("perfil") in permitidos:
                poderes[poder["id"]] = dict(poder, arquivo=arquivo.name)
    return poderes


def carregar_genero(genero_id, pasta=PASTA_DADOS):
    """Lê os arquivos comuns e os do gênero e devolve um dicionário pronto para o gerador."""
    erros = []
    pasta_comum = Path(pasta) / "comum"
    pasta_genero = Path(pasta) / "generos" / genero_id
    if not pasta_genero.is_dir():
        raise DataError([f"Gênero '{genero_id}' não existe em {Path(pasta) / 'generos'}."])
    configuracoes = _ler_json(pasta_comum, "settings.json", erros)
    genero = _ler_json(pasta_genero, "genero.json", erros)
    bruto = {nome: _ler_json(pasta_comum, f"{nome}.json", erros) for nome in ARQUIVOS_COMUNS}
    bruto.update({nome: _ler_json(pasta_genero, f"{nome}.json", erros) for nome in ARQUIVOS_DO_GENERO})
    if erros:
        raise DataError([f"[{genero_id}] {e}" for e in erros])
    configuracoes = {**configuracoes, **genero.get("configuracoes", {})}
    for campo in ("id", "nome", "descricao"):
        if campo not in genero:
            erros.append(f"genero.json: falta o campo '{campo}'.")
    catalogo_de_poderes = _carregar_poderes(pasta_comum, genero, erros)
    poderes_do_genero = {}
    if (pasta_genero / "powers.json").is_file():
        lista = _ler_json(pasta_genero, "powers.json", erros) or []
        poderes_do_genero = _indexar(lista, "powers.json", ["id", "nome", "descricao", "catalogo"], erros)
        for item in poderes_do_genero.values():
            try:
                item["poder"] = poderes_mod.resolver(item, catalogo_de_poderes)
            except poderes_mod.PoderInvalido as erro:
                erros.append(f"powers.json ({item['id']}): {erro}")

    for campo in ("nps_disponiveis", "nps_jogador", "quantidade_maxima", "tentativas_maximas",
                  "modulos_extras_maximos"):
        if campo not in configuracoes:
            erros.append(f"settings.json: falta o campo '{campo}'.")

    vantagens_validas = {v["nome"] for v in bruto["vantagens"].get("vantagens", [])}
    if not vantagens_validas:
        erros.append("vantagens.json: nenhuma vantagem cadastrada.")

    equipamentos = _indexar(bruto["equipment"], "equipment.json", ["id", "nome"], erros)
    for item in equipamentos.values():
        if "ataque" in item:
            _conferir_ataque(f"equipment.json ({item['id']})", item["ataque"], erros)
        if item.get("municao") and item["municao"] not in [e.get("id") for e in bruto["equipment"]]:
            erros.append(f"equipment.json ({item['id']}): munição desconhecida '{item['municao']}'.")

    for item_id in configuracoes.get("itens_basicos", []):
        if item_id not in equipamentos:
            erros.append(f"genero.json: item básico desconhecido '{item_id}'.")

    estilos = _indexar(bruto["styles"], "styles.json", ["id", "nome", "descricao", "modo"], erros)
    for estilo in estilos.values():
        if estilo["modo"] not in MODOS_DE_ESTILO:
            erros.append(f"styles.json ({estilo['id']}): modo '{estilo['modo']}' inválido.")

    arquetipos = _indexar(bruto["archetypes"], "archetypes.json",
                          ["id", "nome", "nomes", "descricao", "faixas", "np_maximo"], erros)
    for arq in arquetipos.values():
        if arq["nomes"] not in bruto["names"]:
            erros.append(f"archetypes.json ({arq['id']}): lista de nomes '{arq['nomes']}' não existe em names.json.")
        if not arq["faixas"]:
            erros.append(f"archetypes.json ({arq['id']}): precisa de pelo menos uma faixa de NP.")
        nps_vistos = set()
        for faixa in arq["faixas"]:
            rotulo = f"archetypes.json ({arq['id']}, faixa NP {faixa.get('np')})"
            faltando = [c for c in ("np", "nome", "fonte", "status_dados", "ficha") if c not in faixa]
            if faltando:
                erros.append(f"{rotulo}: faltam os campos {', '.join(faltando)}.")
                continue
            if faixa["np"] in nps_vistos:
                erros.append(f"{rotulo}: duas faixas com o mesmo NP.")
            nps_vistos.add(faixa["np"])
            if faixa["status_dados"] not in STATUS_DADOS:
                erros.append(f"{rotulo}: status_dados '{faixa['status_dados']}' inválido.")
            ficha = faixa["ficha"]
            if "habilidades" not in ficha:
                erros.append(f"{rotulo}: a ficha não tem habilidades.")
            _resolver_poderes(rotulo, ficha.get("poderes", {}), catalogo_de_poderes, poderes_do_genero, erros)
            _conferir_tracos(rotulo, ficha, vantagens_validas, equipamentos, erros)
            for ataque in ficha.get("ataques_naturais", []):
                _conferir_ataque(rotulo, ataque, erros)
        _conferir_passos(f"archetypes.json ({arq['id']})", arq.get("prioridades", []), vantagens_validas, erros)

    modulos = _indexar(bruto["modules"], "modules.json",
                       ["id", "nome", "descricao", "tags", "estilos", "arquetipos", "status_dados"], erros)
    for mod in modulos.values():
        rotulo = f"modules.json ({mod['id']})"
        for arq_id in mod["arquetipos"]:
            if arq_id not in arquetipos:
                erros.append(f"{rotulo}: arquétipo inexistente '{arq_id}'.")
        for estilo_id in mod["estilos"]:
            if estilo_id not in estilos:
                erros.append(f"{rotulo}: estilo inexistente '{estilo_id}'.")
        for outro in mod.get("incompativel_com", []):
            if outro not in modulos:
                erros.append(f"{rotulo}: incompatível com módulo inexistente '{outro}'.")
        if mod["status_dados"] not in STATUS_DADOS:
            erros.append(f"{rotulo}: status_dados '{mod['status_dados']}' inválido.")
        if mod.get("papel", "ambos") not in PAPEIS:
            erros.append(f"{rotulo}: papel '{mod.get('papel')}' inválido.")
        for secao, permitidas in (("adiciona", SECOES_ADICIONA), ("substitui", SECOES_SUBSTITUI),
                                  ("remove", SECOES_REMOVE)):
            for chave in mod.get(secao, {}):
                if chave not in permitidas:
                    erros.append(f"{rotulo}: '{secao}' não aceita a seção '{chave}'.")
        _resolver_poderes(rotulo, mod.get("adiciona", {}).get("poderes", {}), catalogo_de_poderes,
                          poderes_do_genero, erros)
        _conferir_tracos(rotulo, mod.get("adiciona", {}), vantagens_validas, equipamentos, erros)
        for antigo, novo in mod.get("substitui", {}).get("equipamento", {}).items():
            for item in (antigo, novo):
                if item not in equipamentos:
                    erros.append(f"{rotulo}: substitui equipamento desconhecido '{item}'.")
        _conferir_passos(rotulo, mod.get("prioridades", []), vantagens_validas, erros)

    _conferir_passos("settings.json (prioridades_gerais)", configuracoes.get("prioridades_gerais", []),
                     vantagens_validas, erros)
    jogador = _conferir_jogador(bruto, vantagens_validas, equipamentos, erros, poderes_do_genero)

    if erros:
        raise DataError([f"[{genero_id}] {e}" for e in erros])

    # O modelo de PDF é opcional: sem ele, a página só oferece o download em texto.
    ficha_pdf = pasta_comum / configuracoes.get("ficha_pdf", "")
    ficha_pdf = str(ficha_pdf) if configuracoes.get("ficha_pdf") and ficha_pdf.is_file() else None

    return {
        "genero": {"id": genero["id"], "nome": genero["nome"], "descricao": genero["descricao"],
                   "perfis_de_poder": genero.get("perfis_de_poder", [])},
        "poderes": catalogo_de_poderes,
        "poderes_do_genero": poderes_do_genero,
        "configuracoes": configuracoes,
        "ficha_pdf": ficha_pdf,
        "estilos": estilos,
        "arquetipos": arquetipos,
        "modulos": modulos,
        "equipamentos": equipamentos,
        "nomes": bruto["names"],
        "vantagens": vantagens_validas,
        "vantagens_detalhes": bruto["vantagens"].get("vantagens", []),
        "jogador": jogador,
        "complicacoes": bruto["complications"],
    }
