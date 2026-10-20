"""Extrai os poderes do livro Perfis de Poder (M&M 3e) para JSON.

Cada poder do livro tem: título em maiúsculas, descrição e uma ou mais linhas de estatística
no formato "Nome: efeitos e modificadores • custo". O extrator guarda o texto original da
estatística e tenta identificar efeito-base, alcance, área, defesa e custo. O que não for
reconhecido fica marcado em "conferir".
"""

import json
import re
import subprocess
import sys
import unicodedata

sys.path.insert(0, __import__('os').path.dirname(__file__))
import extrair_perfis_ajustes as ajustes

pdf, saida = sys.argv[1], sys.argv[2]
texto = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True).stdout.decode("utf-8")
paginas = texto.split("\f")

# Efeitos do livro básico (cap. 6), do nome mais longo para o mais curto, para casar primeiro "Mover Objetos".
EFEITOS = sorted([
    "Aflição", "Alongamento", "Ambiente", "Camuflagem", "Características", "Característica", "Comunicação",
    "Compreender", "Controle de Sorte", "Crescimento", "Criar", "Cura", "Dano", "Deflexão", "Encolhimento",
    "Enfraquecer", "Escavação", "Forma Alternativa", "Ilusão", "Imortalidade", "Imunidade", "Intangibilidade",
    "Intangível", "Invocar", "Leitura Mental", "Membros Extras", "Morfar", "Movimento", "Mover Objetos",
    "Mover Objeto", "Nulificar", "Pasmar", "Proteção", "Rapidez", "Regeneração", "Sentidos", "Sentido Remoto",
    "Sentidos Remotos", "Teleporte", "Transformar", "Transformação", "Variável", "Velocidade", "Voo", "Vôo",
    "Natação", "Salto", "Sono", "Sufocamento", "Armadilha", "Controle Mental", "Controle de Elemento",
    "Aumento de Vantagem", "Aumento de Vantagens", "Aumento de Defesa", "Aumento de Defesas",
    "Aumento de Modificador", "Aumento de Perícia", "Aumento de Perícias", "Aumento de Habilidade",
    "Aumento de Habilidades", "Aumento de Força", "Força Aumentada", "Vigor Aumentado", "Agilidade Aumentada",
    "Destreza Aumentada", "Luta Aumentada", "Intelecto Aumentado", "Prontidão Aumentada", "Presença Aumentada",
    "Defesa Aumentada", "Esquiva Aumentada", "Aparar Aumentado", "Fortitude Aumentada", "Vontade Aumentada",
    "Ataque Aumentado", "Absorção", "Aura", "Campo de Força", "Disfarce", "Visão", "Detecção",
], key=len, reverse=True)

CATEGORIAS = {"PODERES OFENSIVOS": "ofensivo", "PODERES DEFENSIVOS": "defensivo",
              "PODERES DE MOVIMENTO": "movimento", "PODERES UTILITÁRIOS": "utilitario",
              "PODERES SENSORIAIS": "sensorial", "PODERES DE CONTROLE": "controle"}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def capitulos_do_sumario():
    """[(nome, página do livro)] na ordem do sumário. Os títulos no corpo do livro são imagens."""
    capitulos = []
    for linha in texto.split("\n")[:130]:
        m = re.match(r"^((?:PODERES|META-PODERES|TALENTOS|LICENÇA)[A-ZÀ-Ú &\-]*?)\s*\.{3,}\s*(\d+)", linha.strip())
        if m:
            capitulos.append((m.group(1).strip(), int(m.group(2))))
    return capitulos


def deslocamento_de_paginas(capitulos):
    """Diferença entre a página do PDF e a do livro, achada pelo 'DESCRITORES' do primeiro perfil."""
    nome, pagina_livro = next((n, p) for n, p in capitulos if n.startswith("PODERES"))
    alvo = nome.replace("PODERES", "DESCRITORES")
    for numero, pagina in enumerate(paginas, start=1):
        if alvo in pagina:
            return numero - pagina_livro
    raise SystemExit(f"Não achei '{alvo}' para calibrar as páginas.")


def ler_custo(t):
    t = t.strip().rstrip(".").replace("–", "-")
    custo = {"texto": t, "fixo": None, "por_graduacao": None}
    m = re.match(r"^(-?\d+) pontos? \+ (-?\d+) pontos? por gradua", t)
    if m:
        custo.update(fixo=int(m.group(1)), por_graduacao=int(m.group(2)))
        return custo
    m = re.match(r"^(-?\d+) pontos? por gradua", t)
    if m:
        custo.update(por_graduacao=int(m.group(1)))
        return custo
    m = re.match(r"^(-?\d+) pontos?$", t)
    if m:
        custo.update(fixo=int(m.group(1)))
    return custo


def ler_efeito(t):
    """Identifica efeito-base, graduação, alcance, área e defesa de um trecho de estatística."""
    t_limpo = t.strip()
    efeito = ajustes.efeito_base(t_limpo, EFEITOS)
    grad = None
    if efeito:
        m = re.search(rf"{re.escape(efeito)}\s+(\d+)", t_limpo)
        grad = int(m.group(1)) if m else None
    baixo = t_limpo.lower()
    if "percepção" in baixo and ("alcance" in baixo or "distância a percepção" in baixo or "aumento de distância: percepção" in baixo):
        alcance = "percepcao"
    elif "à distância" in baixo or "a distância" in baixo or re.search(r"\bdistância\b", baixo):
        alcance = "distancia"
    elif "pessoal" in baixo:
        alcance = "pessoal"
    else:
        alcance = None
    area = bool(re.search(r"\b(área|explosão|cone|linha|nuvem|moldável)\b", baixo))
    m = re.search(r"resistid[oa](?: e superad[oa])? (?:por|pela|pelo) (\w+)", baixo)
    resistido = m.group(1).capitalize() if m else None
    return {"texto": t_limpo, "efeito_base": efeito, "graduacao": grad, "alcance": alcance,
            "area": area, "resistido_por": resistido}


sumario = capitulos_do_sumario()
desloc = deslocamento_de_paginas(sumario)
inicio_do_capitulo = {pagina + desloc: nome for nome, pagina in sumario}
poderes, perfil, categoria = [], None, None
titulo, descricao = None, []
variante = 0
estat = re.compile(r"^([^:•]{2,70}):\s(.+?)\s•\s(.+)$")

for numero, pagina in enumerate(paginas, start=1):
    if numero in inicio_do_capitulo:
        nome_capitulo = inicio_do_capitulo[numero]
        perfil = nome_capitulo if nome_capitulo.startswith(("PODERES", "META-PODERES", "TALENTOS")) else None
        categoria, titulo, descricao = None, None, []
    for bruta in pagina.split("\n"):
        linha = bruta.strip()
        if not linha:
            continue
        if perfil is None:
            continue
        if linha in CATEGORIAS or linha.startswith("OUTROS PODERES"):
            categoria = CATEGORIAS.get(linha, "outros")
            titulo, descricao = None, []
            continue
        if linha.isupper() and 2 < len(linha) < 60 and not linha.endswith("."):
            titulo, descricao, variante = linha, [], 0
            continue
        m = estat.match(linha)
        if m and "ponto" in m.group(3):
            nome, corpo, custo_txt = m.group(1).strip(), m.group(2), m.group(3)
            variante += 1
            # Divide efeitos ligados (";" fora de parênteses).
            partes, nivel, atual = [], 0, ""
            for ch in corpo:
                nivel += ch == "("
                nivel -= ch == ")"
                if ch == ";" and nivel == 0:
                    partes.append(atual)
                    atual = ""
                else:
                    atual += ch
            partes.append(atual)
            efeitos = [ler_efeito(p) for p in partes if p.strip()]
            custo = ajustes.ler_custo(custo_txt)
            conferir = []
            modificador = bool(ajustes.MODIFICADOR_DE_OUTRO.search(corpo))
            if custo["fixo"] is None and custo["por_graduacao"] is None and not custo["opcoes"]:
                conferir.append("custo não reconhecido")
            if custo["opcoes"]:
                conferir.append("custo com opções (escolha uma)")
            if not modificador and (not efeitos or efeitos[0]["efeito_base"] is None):
                conferir.append("efeito-base não reconhecido")
            poderes.append({
                "id": f"{slug(perfil.replace('PODERES ', ''))}__{slug(nome)}" + (f"_{variante}" if variante > 1 else ""),
                "nome": nome,
                "titulo": (titulo or nome).title(),
                "perfil": perfil.replace("PODERES ", "").title(),
                "categoria": categoria or "geral",
                "descricao": " ".join(descricao)[:1200],
                "estatistica": corpo,
                "efeitos": efeitos,
                "custo": custo,
                "modifica_outro_poder": modificador,
                "pagina_pdf": numero,
                "conferir": conferir,
            })
            continue
        if titulo:
            descricao.append(linha)

# IDs únicos
vistos = {}
for p in poderes:
    if p["id"] in vistos:
        vistos[p["id"]] += 1
        p["id"] += f"_{vistos[p['id']]}"
    else:
        vistos[p["id"]] = 1

json.dump({"_fonte": "Mutantes & Malfeitores 3e — Perfis de Poder (extração automática; confira os itens marcados)",
           "poderes": poderes}, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

from collections import Counter
print("poderes:", len(poderes))
print("por perfil:", dict(Counter(p["perfil"] for p in poderes)))
print("por categoria:", dict(Counter(p["categoria"] for p in poderes)))
print("com algo a conferir:", sum(1 for p in poderes if p["conferir"]),
      dict(Counter(c for p in poderes for c in p["conferir"])))
print("efeitos-base:", Counter(e["efeito_base"] for p in poderes for e in p["efeitos"]).most_common(25))
