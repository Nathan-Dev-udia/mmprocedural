"""Audita as fichas de heróis (dados/generos/herois): regras do M&M 3e (custos, limites de NP, consistência interna)
e sinais de texto quebrado vindo da extração dos PDFs. Não altera nenhum arquivo de dados.

Uso, a partir da raiz do projeto:
    python ferramentas/auditar_herois.py [saida.json] [--editora dc|marvel]

Imprime o resumo por código de problema e quantas fichas ficam em cada nível:
- "revisar": falta algo essencial (habilidade, defesa) ou a ficha se contradiz de forma grave;
- "ressalvas": divergência de custo/perícia/limite que o Mestre deve conferir;
- "jogável": nada acusado.
O JSON de saída lista, por código, as fichas afetadas. Compare antes e depois de mexer na extração.

Atenção ao interpretar: nem todo alerta é erro. Marvel com valor null por travessão no livro (Chamber, Sentinel) é
intencional, e alguns livros da DC usam regras alternativas que estouram limites de NP.
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nucleo import herois, herois_pdf, rules  # noqa: E402

problemas = collections.defaultdict(list)  # código -> [(id, detalhe)]
contagem = collections.Counter()


def p(codigo, ficha_id, detalhe=""):
    problemas[codigo].append((ficha_id, detalhe))


def texto_quebrado(ficha_id, texto):
    if not isinstance(texto, str):
        return
    if "�" in texto or "�" in texto:
        p("TEXTO_CARACTERE_QUEBRADO", ficha_id, texto[:60])
    if re.search(r"\b[a-z]{1,4}\s*$", texto.strip()) and not texto.strip().endswith((".", "!", "?", ")", "*")):
        pass


def checar_limites(fid, np, hab, d, atk_dano):
    """Limites de NP: defesa+resistência ≤ 2NP, fort+vontade ≤ 2NP, ataque+dano ≤ 2NP."""
    lim = 2 * np
    if "Esquiva" in d and "Resistência" in d and d["Esquiva"] + d["Resistência"] > lim:
        p("LIMITE_ESQUIVA_RESIST", fid, f"{d['Esquiva']}+{d['Resistência']}>{lim}")
    if "Aparar" in d and "Resistência" in d and d["Aparar"] + d["Resistência"] > lim:
        p("LIMITE_APARAR_RESIST", fid, f"{d['Aparar']}+{d['Resistência']}>{lim}")
    if "Fortitude" in d and "Vontade" in d and d["Fortitude"] + d["Vontade"] > lim:
        p("LIMITE_FORT_VONTADE", fid, f"{d['Fortitude']}+{d['Vontade']}>{lim}")
    for nome, bonus, dano in atk_dano:
        if isinstance(bonus, int) and isinstance(dano, int) and bonus + dano > lim:
            p("LIMITE_ATAQUE_DANO", fid, f"{nome}: {bonus}+{dano}>{lim}")


def auditar_marvel(fid, d):
    contagem["marvel"] += 1
    f = d["ficha"]
    np = d["nivel_poder"]
    hab = f.get("habilidades", {})
    for k, v in list(hab.items()) + list(f.get("habilidades_base", {}).items()):
        if not isinstance(v, int):
            p("HABILIDADE_NULA", fid, f"{k}={v}")
    hab = {k: v for k, v in hab.items() if isinstance(v, int)}
    if sorted(hab) != sorted(["For", "Vig", "Agi", "Des", "Lut", "Int", "Pro", "Pre"]):
        p("HABILIDADES_INCOMPLETAS", fid, str(sorted(hab)))
    defs = {("Resistência" if k == "Resistencia" else k): v for k, v in f.get("defesas", {}).items()}
    for k in ("Esquiva", "Aparar", "Fortitude", "Resistência", "Vontade"):
        if not isinstance(defs.get(k), int):
            p("DEFESA_AUSENTE", fid, k)
    defs = {k: v for k, v in defs.items() if isinstance(v, int)}
    checar_limites(fid, np, hab, defs, [(a["nome"], a.get("bonus"), a.get("dano")) for a in f.get("ataques", [])])
    if not f.get("ataques"):
        p("SEM_ATAQUES", fid)
    vnp = f.get("validacao_np", {})
    if vnp.get("legal") is False:
        p("MARVEL_ILEGAL_PELO_PROPRIO_JSON", fid, str(vnp))
    # perícias: graduação máxima NP+10
    for nome, g in f.get("pericias", {}).items():
        if not isinstance(g, (int, float)):
            p("PERICIA_NAO_NUMERICA", fid, f"{nome}={g}")
        elif g > np + 10:
            p("PERICIA_ACIMA_DO_LIMITE", fid, f"{nome} {g} > {np + 10}")
        if herois_pdf._nome_da_pericia(nome) is None:
            p("PERICIA_NAO_RECONHECIDA", fid, nome)
    # custos
    c = d.get("custos_3e")
    if c is None:
        p("MARVEL_SEM_CUSTOS", fid)
    else:
        base = {k: v for k, v in (f.get("habilidades_base") or hab).items() if isinstance(v, int)}
        custo_hab = 2 * sum(base.values())
        pub = c.get("habilidades", c.get("habilidades_base"))
        if pub is not None and pub != custo_hab:
            p("CUSTO_HABILIDADES_DIVERGE", fid, f"json {pub} x calculado {custo_hab}")
        pericias = sum(v for v in f.get("pericias", {}).values() if isinstance(v, (int, float)))
        custo_per = pericias / 2
        if c.get("pericias") is not None and abs(c["pericias"] - custo_per) > 0.5:
            p("CUSTO_PERICIAS_DIVERGE", fid, f"json {c['pericias']} x calculado {custo_per}")
        if c.get("poderes_pendentes"):
            p("MARVEL_PODERES_PENDENTES", fid)
        if c.get("total") is None and d.get("pontos_poder_3e") is None:
            p("MARVEL_SEM_TOTAL_PP", fid)
    # poderes sem construção
    for pod in f.get("poderes", []):
        cons = pod.get("construcao_3e", "")
        if not cons.strip():
            p("PODER_SEM_CONSTRUCAO_3E", fid, pod.get("nome", ""))
        elif re.search(r"pendente|nao foi convertid|não foi convertid", cons, re.I):
            p("PODER_CONSTRUCAO_PENDENTE", fid, pod.get("nome", ""))
    if d.get("status_conversao") == "convertida_com_ajustes_de_np":
        contagem["marvel_ajustada_np"] += 1
    texto_json = json.dumps(d, ensure_ascii=False)
    if "�" in texto_json:
        p("TEXTO_CARACTERE_QUEBRADO", fid)
    # coerência de NP: pontos 3e esperados ≈ 15*NP
    tot = d.get("pontos_poder_3e")
    if tot is not None and tot > 15 * np:
        p("TOTAL_ACIMA_DE_15xNP", fid, f"{tot} > {15 * np}")


def auditar_dc(fid, d):
    contagem["dc"] += 1
    f = d["ficha_publicada"]
    np = d["nivel_poder"]
    if np is None:
        p("DC_SEM_NP", fid)
        np = 0
    brutos = f.get("habilidades", {})
    hab = {}
    for sigla in herois.HABILIDADES_DC:
        v = brutos.get(sigla)
        if v is None:
            p("HABILIDADE_AUSENTE", fid, sigla)
        elif re.fullmatch(r"-?\d+", str(v).replace("–", "-").strip()):
            hab[herois.HABILIDADES_DC[sigla]] = int(str(v).replace("–", "-"))
        else:
            hab[herois.HABILIDADES_DC[sigla]] = None
            p("HABILIDADE_NAO_NUMERICA", fid, f"{sigla}={v}")
    h = herois_pdf._ler_dc(d)
    defs = h["defesas"]
    for k in ("Esquiva", "Aparar", "Fortitude", "Resistência", "Vontade"):
        if k not in defs:
            p("DEFESA_AUSENTE", fid, k)
    if np:
        checar_limites(fid, np, hab, defs, [(a[0], a[1], int(a[2])) for a in h["ataques"]])
    # defesa não pode ser menor que a habilidade base
    pares = {"Esquiva": "Agi", "Aparar": "Lut", "Fortitude": "Vig", "Vontade": "Pro", "Resistência": "Vig"}
    for k, s in pares.items():
        if k in defs and hab.get(s) is not None and defs[k] < hab[s]:
            p("DEFESA_MENOR_QUE_HABILIDADE", fid, f"{k} {defs[k]} < {s} {hab[s]}")
    # perícias
    for nome, per in h["pericias"].items():
        sigla = rules.habilidade_da_pericia(nome)
        if hab.get(sigla) is not None and per["total"] is not None and per["total"] < per["grad"] + hab[sigla] - 0:
            p("PERICIA_TOTAL_MENOR_QUE_BASE", fid, f"{nome} {per['grad']} ({per['total']}) hab {hab[sigla]}")
        if np and per["grad"] > np + 10:
            p("PERICIA_ACIMA_DO_LIMITE", fid, f"{nome} {per['grad']} > {np + 10}")
    texto_perícias = f.get("pericias", "")
    n_itens = len([x for x in herois_pdf._separar_por_virgula(texto_perícias)])
    if texto_perícias and n_itens != len(h["pericias"]):
        p("PERICIAS_NAO_LIDAS", fid, f"{n_itens} no texto, {len(h['pericias'])} lidas")
    # pontos publicados
    pp = f.get("pontos_poder", "")
    custos = h["custos"]
    total = h["total"]
    if total is None:
        p("DC_SEM_TOTAL_PP", fid)
    else:
        soma = sum(custos.values())
        if len(custos) < 5:
            p("PONTOS_CATEGORIAS_INCOMPLETAS", fid, pp[:80])
        elif soma != total:
            p("PONTOS_SOMA_DIVERGE_DO_TOTAL", fid, f"soma {soma} x total {total}")
        if np and total != 15 * np:
            contagem["dc_total_diferente_de_15xNP"] += 1
    if "Habilidades" in custos and all(v is not None for v in hab.values()):
        calc = 2 * sum(hab.values())
        if calc != custos["Habilidades"]:
            p("CUSTO_HABILIDADES_DIVERGE", fid, f"publicado {custos['Habilidades']} x calculado {calc}")
    if "Perícias" in custos and h["pericias"]:
        calc = math.ceil(sum(x["grad"] for x in h["pericias"].values()) / 2)
        if calc != custos["Perícias"]:
            p("CUSTO_PERICIAS_DIVERGE", fid, f"publicado {custos['Perícias']} x calculado {calc} (pode haver perícia não lida)")
    # poderes: soma dos custos listados × pontos publicados
    if f.get("poderes") and "Poderes" in custos:
        itens = herois._dividir_por_custo(f["poderes"])
        soma = 0
        for it in itens:
            m = re.search(r"\((-?\d+) PP\)$", it)
            if m:
                soma += int(m.group(1))
        if soma != custos["Poderes"]:
            p("CUSTO_PODERES_DIVERGE", fid, f"soma dos itens {soma} x publicado {custos['Poderes']} (inclui equipamento? {bool(f.get('equipamento'))})")
    # seções mínimas
    for campo in ("habilidades", "defesas", "pontos_poder", "pericias"):
        if not f.get(campo):
            p(f"DC_SEM_{campo.upper()}", fid)
    if not f.get("vantagens"):
        contagem["dc_sem_vantagens"] += 1
    if not h["ataques"]:
        p("DC_SEM_ATAQUE_LIDO", fid, (f.get("ataques") or "")[:70])
    # texto
    comp = f.get("complicacoes", "")
    if not comp:
        p("DC_SEM_COMPLICACOES", fid)
    elif not comp.rstrip().endswith((".", "!", "?", "”", "’", '"', ")")):
        p("COMPLICACOES_TEXTO_CORTADO", fid, "…" + comp[-60:])
    for k, v in f.items():
        texto_quebrado(fid, v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))
    if re.search(r"\b(?:Initiative|Dodge|Fortitude)\b", f.get("complicacoes", "")):
        p("COMPLICACOES_COM_TEXTO_ESTRANHO", fid, comp[:60])
    # vantagens tiradas do texto
    if f.get("vantagens") and re.search(r"\d+\s*points?\b", f["vantagens"]):
        p("VANTAGENS_COM_TEXTO_ESTRANHO", fid, f["vantagens"][:60])


argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
filtro = sys.argv[sys.argv.index("--editora") + 1] if "--editora" in sys.argv else None
if filtro:
    argumentos = [a for a in argumentos if a != filtro]

for entrada_id, (caminho, resumo) in herois._catalogo().items():
    if filtro and resumo["editora"] != filtro:
        continue
    d = json.loads(caminho.read_text(encoding="utf-8"))
    try:
        (auditar_marvel if resumo["editora"] == "marvel" else auditar_dc)(entrada_id, d)
    except (TypeError, KeyError, ValueError) as e:
        p("AUDITORIA_ERRO_DADOS_INVALIDOS", entrada_id, repr(e)[:90])

ESSENCIAIS = {"HABILIDADE_AUSENTE", "HABILIDADE_NULA", "HABILIDADES_INCOMPLETAS", "DEFESA_AUSENTE", "DC_SEM_DEFESAS",
              "MARVEL_ILEGAL_PELO_PROPRIO_JSON", "PERICIA_ACIMA_DO_LIMITE", "AUDITORIA_ERRO_DADOS_INVALIDOS",
              "TEXTO_CARACTERE_QUEBRADO"}
MECANICOS = {"PONTOS_SOMA_DIVERGE_DO_TOTAL", "CUSTO_HABILIDADES_DIVERGE", "CUSTO_PERICIAS_DIVERGE",
             "PERICIA_TOTAL_MENOR_QUE_BASE", "LIMITE_ESQUIVA_RESIST", "LIMITE_APARAR_RESIST", "LIMITE_FORT_VONTADE",
             "LIMITE_ATAQUE_DANO", "DEFESA_MENOR_QUE_HABILIDADE", "PERICIAS_NAO_LIDAS", "HABILIDADE_NAO_NUMERICA",
             "DC_SEM_ATAQUE_LIDO", "DC_SEM_PERICIAS"}
por_ficha = collections.defaultdict(set)
for codigo, itens in problemas.items():
    for ficha_id, _ in itens:
        por_ficha[ficha_id].add(codigo)
niveis = collections.defaultdict(collections.Counter)
for ficha_id, (_, resumo) in herois._catalogo().items():
    if filtro and resumo["editora"] != filtro:
        continue
    codigos = por_ficha[ficha_id]
    niveis[resumo["editora"]]["revisar" if codigos & ESSENCIAIS else
                              "ressalvas" if codigos & MECANICOS else "jogável"] += 1

print("fichas:", dict(contagem))
print("níveis:", {editora: dict(n) for editora, n in niveis.items()})
for codigo, itens in sorted(problemas.items(), key=lambda kv: -len(kv[1])):
    print(f"\n{codigo}: {len(itens)}")
    for ficha_id, detalhe in itens[:3]:
        print(f"   {ficha_id}  {detalhe}")
if argumentos:
    Path(argumentos[0]).write_text(json.dumps(problemas, ensure_ascii=False, indent=1), encoding="utf-8")
