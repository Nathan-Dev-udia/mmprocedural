"""Gera os arquivos básicos do gênero fantasia medieval: gênero, equipamento, magias e traços raciais,
nomes e complicações.

Uso: python ferramentas/criar_fantasia_base.py

- Equipamento: estatísticas do livro básico de M&M (cap. 7: armas arcaicas, armaduras e escudos) com o
  preço do Livro do Jogador de D&D 5e (cap. 5), em peças de ouro (1 pp = 0,1 po; 1 pc = 0,01 po).
  Armas que o livro de M&M não tem (espada grande, arco longo, besta pesada...) são a arma mais próxima com
  +1 de Dano e +1 ponto de custo; a fonte diz "adaptado".
- Magias e traços raciais apontam para o catálogo extraído do Perfis de Poder (o custo é o do livro).
  As magias de cada tradição formam um Arranjo (efeitos alternativos: 1 PP cada, além da principal).
  "graduacao_np" faz a graduação acompanhar o NP do personagem (NP + ajuste, mínimo 1).

ATENÇÃO: este script recria esses arquivos do zero. Se algum for ajustado à mão depois, não rode de novo
sem conferir a diferença.
"""

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "dados" / "generos" / "fantasia"
PASTA.mkdir(parents=True, exist_ok=True)


def gravar(nome, conteudo):
    (PASTA / nome).write_text(json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


gravar("genero.json", {
    "id": "fantasia",
    "nome": "Fantasia medieval",
    "descricao": "Espadas e magia: aventureiros, masmorras, dragões e reinos em guerra. Classes e raças inspiradas em D&D 5e.",
    "perfis_de_poder": ["Mágicos", "Vitais", "Flamejantes", "Congelantes", "Elementais", "Sombrios", "Luminosos",
                        "Animais", "Vegetais", "Ilusórios", "Mentais", "Marciais", "Fatais", "Terrestres",
                        "Climáticos", "Talentos Poderosos", "De Teleporte"],
    "configuracoes": {
        "rotulo_poderes": "Magias e dons",
        "rotulo_arquetipo": "Classe",
        "rotulo_foco": "Subclasse",
        "equipamento": "dinheiro",
        "moeda": "po",
        "np_padrao_jogador": 5,
        # Os NPCs do bestiário têm NP 7 (Cavaleiro) e 9 (Dragão): a fantasia oferece todos os NPs de 1 a 10.
        "nps_disponiveis": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "itens_basicos": ["racoes"],
        "prioridades_gerais": ["defesa:Esquiva", "defesa:Aparar", "defesa:Fortitude", "defesa:Vontade",
                               "pericia:Percepção", "pericia:Atletismo", "pericia:Intuição",
                               "vantagem:Rolamento Defensivo", "habilidade:Vig"],
        "pericias_de_reserva": ["Percepção", "Atletismo", "Intuição", "Furtividade", "Acrobacia", "Persuasão",
                                "Enganação", "Intimidação", "Investigação", "Especialidade: Sobrevivência"],
    },
})

M = "Livro básico de M&M, cap. 7"
PHB = "preço do Livro do Jogador (D&D 5e), cap. 5"
LITE = "Manual dos Mecanismos Lite, armaduras"
GERAL = M + ": itens de equipamento geral são uma Característica de 1 graduação (1 ponto)"


def fonte(base, adaptado=""):
    return f"{base} ({adaptado}); {PHB}" if adaptado else f"{base}; {PHB}"


GUIA = "Gadget Guide: Archaic Weapons"


def custo_da_arma(efeito, tipo, qualidades, nao_confiavel=False):
    """PP pelo guia: 1 por graduação de Dano (+1 por graduação à distância, salvo se Não Confiável, com 5 usos ou
    menos), mais as qualidades (Alcance e Perigosa por graduação; as outras, 1 ponto cada)."""
    por_graduacao = 2 if tipo == "distancia" and not nao_confiavel else 1
    extras = 0
    for qualidade in qualidades:
        nome, _, graduacao = qualidade.partition(" ")
        extras += int(graduacao) if graduacao.isdigit() else 1
    return efeito * por_graduacao + extras


def arma(id_, nome, cat, preco, dado, efeito, pericia, descritor, qualidades=(), tipo="corpo", forca=True,
         municao=None, notas="", familia="", efeito_nome=None, resistido=None, nao_confiavel=False, custo=None):
    """Arma pelo guia de gadgets, com o que ela faz tirado do Livro do Jogador (D&D 5e).

    O Dano segue o dado do D&D (d4 → 1, d6 → 2, d8 → 3, d10, d12 ou 2d6 → 4), como a tabela do próprio guia; o
    descritor é o tipo de dano; as qualidades são as da família da arma no guia, só onde o D&D concorda (Alcance só
    nas armas de alcance do D&D). Perigosa amplia o crítico em 1 por graduação.
    """
    qualidades = list(qualidades)
    perigosa = sum(int(q.partition(" ")[2] or 1) for q in qualidades if q.startswith("Perigosa"))
    ataque = {"tipo": tipo, "efeito": efeito, "critico": 20 - perigosa, "pericia": pericia, "descritor": descritor}
    if qualidades:
        ataque["qualidades"] = qualidades
    if forca:
        ataque["soma_forca"] = True
    if efeito_nome:
        ataque["efeito_nome"] = efeito_nome
    if resistido:
        ataque["resistido_por"] = resistido
    if custo is None:
        custo = custo_da_arma(efeito, tipo, qualidades, nao_confiavel)
    origem = f"{dado} no Livro do Jogador (D&D 5e)" if dado else "sem equivalente no Livro do Jogador"
    dados = {"id": id_, "nome": nome, "categoria": cat, "custo": custo, "preco": preco, "notas": notas,
             "ataque": ataque, "fonte": f"{GUIA} ({familia}); Dano {efeito}: {origem}; {PHB}"}
    if municao:
        dados["municao"] = municao
    return dados


def item(id_, nome, cat, preco, descricao="", custo=1, fonte_=None, **extra):
    dados = {"id": id_, "nome": nome, "categoria": cat, "custo": custo, "preco": preco, "descricao": descricao,
             "fonte": fonte_ or fonte(GERAL)}
    dados.update(extra)
    return dados


ESP, MAC, MAZ = "Combate Corpo-a-Corpo: Espadas", "Combate Corpo-a-Corpo: Machados", "Combate Corpo-a-Corpo: Maças"
LAN, ADA, POR = "Combate Corpo-a-Corpo: Lanças", "Combate Corpo-a-Corpo: Adagas", "Combate Corpo-a-Corpo: Porretes"
ARC, BES, ARR = "Combate à Distância: Arcos", "Combate à Distância: Bestas", "Combate à Distância: Arremesso"
BR = "Arma branca"

# Peso em kg, do Livro do Jogador (D&D 5e), cap. 5; 0 é o que o livro marca com "–" (uma folha, um apito) e não
# chega a ter graduação de massa. Os pesos com "*" no comentário não estão no livro e foram estimados.
PESOS = {
    # Armas
    "adaga": 0.5, "porrete": 1, "bordao": 2, "maca": 2, "machadinha": 1, "lanca": 1.5, "foice_curta": 1,
    "martelo_leve": 1, "clava_grande": 5, "espada_curta": 1, "espada_longa": 1.5, "cimitarra": 1.5, "rapieira": 1,
    "espada_grande": 3, "espada_prata": 1.5, "adaga_longa": 1, "adaga_longa_prata": 1,   # * como a espada curta
    "machado_batalha": 2, "machado_grande": 3.5, "martelo_guerra": 1, "maca_estrela": 2, "mangual": 1, "malho": 5,
    "alabarda": 3, "lanca_montaria": 3, "glaive": 3, "pique": 4, "tridente": 2, "picareta_guerra": 1, "chicote": 1.5,
    "arco_curto": 1, "arco_longo": 1, "besta_leve": 2.5, "besta_mao": 1.5, "besta_pesada": 4.5, "funda": 0,
    "azagaia": 4, "dardos": 1, "zarabatana": 0.5, "rede": 1.5, "frasco_acido": 0.5, "fogo_alquimico": 0.5,
    "flechas": 0.5, "virotes": 0.75, "balas_de_funda": 0.75, "agulhas": 0.5,
    # Armaduras e escudos
    "acolchoada": 4, "couro": 5, "couro_batido": 6.5, "gibao_peles": 6, "camisao_malha": 10, "brunea": 22.5,
    "cota_malha": 27.5, "peitoral": 10, "cota_talas": 30, "meia_armadura": 20, "placas": 32.5,
    "broquel": 1.5, "escudo": 3, "escudo_torre": 7.5,   # * broquel e escudo de torre
    # Itens de conjurador
    "grimorio": 1.5, "bolsa_componentes": 1, "simbolo_sagrado": 0.5, "foco_druidico": 0, "varinha": 0.5, "orbe": 1.5,
    "giz_runico": 0.25, "agua_benta": 0.5,   # * giz rúnico
    # Ferramentas
    "ferramentas_ladrao": 0.5, "kit_disfarce": 1.5, "kit_herbalismo": 1.5, "kit_primeiros_socorros": 1.5,
    "kit_escalada": 6, "alaude": 1, "flauta": 0.5, "luneta": 0.5, "suprimentos_alquimista": 4, "kit_envenenador": 1,
    "kit_falsificacao": 2.5, "ferramentas_ferreiro": 4, "ferramentas_carpinteiro": 3, "ferramentas_cartografo": 3,
    "ferramentas_joalheiro": 1, "ferramentas_navegador": 1, "utensilios_cozinheiro": 4, "dados": 0, "baralho": 0,
    "lira": 1, "viola": 3, "tambor": 1.5, "trompa": 1, "gaita_foles": 3,
    # Equipamento de aventura
    "mochila": 2.5, "saco_dormir": 3.5, "corda": 5, "tochas": 5, "lanterna_coberta": 1, "cantil": 2.5,
    "pe_de_cabra": 2.5, "tenda": 10, "algemas": 2, "manto": 2, "aljava": 0.5, "ampulheta": 0.5, "apito": 0,
    "ariete": 17.5, "balanca": 1.5, "barril": 35, "bau": 12.5, "bolsa_cinto": 0.5, "cadeado": 0.5, "cobertor": 1.5,
    "corda_seda": 2.5, "corrente": 5, "espelho": 0.25, "esferas": 1, "estrepes": 1, "estojo_mapas": 0.5, "frasco": 0,
    "gancho": 2, "giz": 0, "lamparina": 0.5, "lanterna_furta_fogo": 1, "livro": 2.5, "lupa": 0, "martelo": 1.5,
    "oleo": 0.5, "pa": 2.5, "papel": 0, "pederneira": 0.5, "pena_escrever": 0, "pergaminho": 0, "picareta": 5,
    "pitoes": 0, "sabao": 0, "saco": 0.25, "sinete": 0, "sino": 0, "tinta": 0, "vara": 3.5, "velas": 0,
    "kit_refeicao": 0.5, "armadilha_caca": 12.5,
    # Poções e alquimia (* bomba, elixires e óleos de bruxo, como os frascos do livro)
    "pocao_cura": 0.25, "antitoxina": 0, "veneno": 0, "bomba_bruxo": 0.5, "elixires": 0.25, "oleo_laminas": 0.5,
    # Comida e bebida (* o livro não pesa pão, queijo, carne nem bebidas)
    "racoes": 5, "vinho": 2, "cerveja": 4, "pao": 0.25, "queijo": 0.25, "carne": 0.5, "refeicao": 0,
    "cerveja_caneca": 0, "vinho_fino": 1,
    # Arreios e veículos (os animais não têm peso de item: veja MONTARIAS)
    "sela": 12.5, "alforjes": 4, "carroca": 100, "carruagem": 300, "barco_remo": 45,
    # Roupas
    "roupas_viajante": 2, "roupas_finas": 3, "robes": 2, "roupas_comuns": 1.5, "traje_artista": 2,
}
PESO_ESTIMADO = {"adaga_longa", "adaga_longa_prata", "broquel", "escudo_torre", "giz_runico", "bomba_bruxo",
                 "elixires", "oleo_laminas", "vinho", "cerveja", "pao", "queijo", "carne", "vinho_fino"}

# Velocidade das montarias pelo Guia do Mestre (Cavalo: Velocidade 4; Animal de rebanho: Velocidade 3), na ordem do
# deslocamento do Livro do Jogador (18 m: cavalos de montaria e de guerra; 12 a 15 m: os outros). Carga em kg, do
# Livro do Jogador. Os veículos andam no passo de quem os puxa ou rema (barco a remo: 2 km/h no Livro do Jogador).
MONTARIAS = {
    "cavalo_montaria": (4, 220), "cavalo_guerra": (4, 270), "cavalo_tracao": (3, 270), "ponei": (3, 115),
    "burro": (3, 210), "camelo": (3, 240), "mastim": (3, 100),
}
VEICULOS = {"carroca": 1, "carruagem": 2, "barco_remo": -1}


def com_pesos(itens):
    """Põe peso (kg), Velocidade e carga nos itens; kits pesam a soma do que levam (calculada nas planilhas)."""
    for item in itens:
        if item["id"] in MONTARIAS:
            item["velocidade"], item["carga"] = MONTARIAS[item["id"]]
            item["fonte_velocidade"] = "Guia do Mestre, Cavalo e Animal de rebanho; carga do Livro do Jogador"
        elif item.get("kit"):
            continue
        else:
            assert item["id"] in PESOS, f"falta o peso de {item['id']}"
            item["peso"] = PESOS[item["id"]]
            if item["id"] in PESO_ESTIMADO:
                item["peso_estimado"] = True
        if item["id"] in VEICULOS:
            item["velocidade"] = VEICULOS[item["id"]]
            item["fonte_velocidade"] = "estimada: o passo do animal que puxa ou de quem rema"
    return itens


gravar("equipment.json", com_pesos([
    # Armas simples (corpo a corpo)
    arma("adaga", "Adaga", BR, 2, "1d4 perfurante", 1, ADA, "perfuração", ["Perigosa"],
         notas="Leve; pode ser arremessada", familia="adaga"),
    arma("porrete", "Porrete", BR, 0.1, "1d4 concussão", 1, POR, "esmagamento", notas="Leve", familia="porrete"),
    arma("bordao", "Bordão (cajado)", BR, 0.2, "1d6 concussão", 2, POR, "esmagamento", ["Dupla"],
         notas="Versátil; também serve de foco arcano", familia="bastão"),
    arma("maca", "Maça", BR, 5, "1d6 concussão", 2, MAZ, "esmagamento", ["Perigosa"], familia="maça"),
    arma("machadinha", "Machadinha", BR, 5, "1d6 cortante", 2, MAC, "corte", ["Perigosa", "Quebrar"],
         notas="Leve; pode ser arremessada", familia="machado"),
    arma("lanca", "Lança", BR, 1, "1d6 perfurante", 2, LAN, "perfuração", ["Perigosa"],
         notas="Versátil; pode ser arremessada", familia="lança, sem Alcance: no D&D a lança não tem alcance"),
    arma("foice_curta", "Foice curta", BR, 1, "1d4 cortante", 1, "Combate Corpo-a-Corpo: Foices", "corte",
         ["Perigosa"], notas="Leve", familia="lâmina curta"),
    arma("martelo_leve", "Martelo leve", BR, 2, "1d4 concussão", 1, MAZ, "esmagamento", ["Esmagar"],
         notas="Leve; pode ser arremessado", familia="martelo"),
    arma("clava_grande", "Clava grande", BR, 0.2, "1d8 concussão", 3, POR, "esmagamento",
         notas="Duas mãos, pesada", familia="porrete"),
    # Armas marciais (corpo a corpo)
    arma("espada_curta", "Espada curta", BR, 10, "1d6 perfurante", 2, ESP, "perfuração", ["Perigosa"],
         notas="Leve", familia="espada de estocada"),
    arma("espada_longa", "Espada longa", BR, 15, "1d8 cortante", 3, ESP, "corte", notas="Versátil",
         familia="espada"),
    arma("cimitarra", "Cimitarra", BR, 25, "1d6 cortante", 2, ESP, "corte", ["Perigosa"], notas="Leve",
         familia="espada curva"),
    arma("rapieira", "Rapieira", BR, 25, "1d8 perfurante", 3, ESP, "perfuração", ["Perigosa"],
         familia="espada de estocada"),
    arma("espada_grande", "Espada grande", BR, 50, "2d6 cortante", 4, ESP, "corte", notas="Duas mãos, pesada",
         familia="espada"),
    arma("espada_prata", "Espada de prata", BR, 115, "1d8 cortante", 3, ESP, "corte, prata",
         notas="Versátil; fere monstros vulneráveis à prata",
         familia="espada; preço: espada longa (15 po) + prateamento (100 po), regra de armas prateadas do Livro do "
                 "Jogador"),
    # Lâminas da escola da Víbora, que troca as espadas do bruxo por um par de adagas longas.
    arma("adaga_longa", "Adaga longa", BR, 10, "", 2, ADA, "perfuração", ["Perigosa"],
         notas="Comprida quase como uma espada curta, leve como uma adaga",
         familia="adaga, com o Dano da espada curta; preço da espada curta"),
    arma("adaga_longa_prata", "Adaga longa de prata", BR, 110, "", 2, ADA, "perfuração, prata", ["Perigosa"],
         notas="Fere monstros vulneráveis à prata",
         familia="adaga, com o Dano da espada curta; preço: espada curta (10 po) + prateamento (100 po)"),
    arma("machado_batalha", "Machado de batalha", BR, 10, "1d8 cortante", 3, MAC, "corte", ["Perigosa", "Quebrar"],
         notas="Versátil", familia="machado"),
    arma("machado_grande", "Machado grande", BR, 30, "1d12 cortante", 4, MAC, "corte", ["Perigosa", "Quebrar"],
         notas="Duas mãos, pesada", familia="machado"),
    arma("martelo_guerra", "Martelo de guerra", BR, 15, "1d8 concussão", 3, MAZ, "esmagamento", ["Esmagar"],
         notas="Versátil", familia="martelo"),
    arma("maca_estrela", "Maça estrela", BR, 15, "1d8 perfurante", 3, MAZ, "perfuração", ["Perigosa"],
         familia="maça"),
    arma("mangual", "Mangual", BR, 10, "1d8 concussão", 3, MAZ, "esmagamento", ["Perigosa", "Desarmar"],
         familia="mangual, sem Alcance: no D&D o mangual não tem alcance"),
    arma("malho", "Malho", BR, 10, "2d6 concussão", 4, MAZ, "esmagamento", ["Esmagar"], notas="Duas mãos, pesada",
         familia="martelo"),
    arma("picareta_guerra", "Picareta de guerra", BR, 5, "1d8 perfurante", 3, MAZ, "perfuração", ["Perigosa"],
         familia="martelo com bico"),
    arma("alabarda", "Alabarda", BR, 20, "1d10 cortante", 4, LAN, "corte", ["Alcance 2", "Derrubar"],
         notas="Duas mãos, pesada, alcance de 3 m", familia="arma de haste"),
    arma("glaive", "Glaive", BR, 20, "1d10 cortante", 4, LAN, "corte", ["Alcance 2", "Derrubar"],
         notas="Duas mãos, pesada, alcance de 3 m", familia="arma de haste"),
    arma("pique", "Pique", BR, 5, "1d10 perfurante", 4, LAN, "perfuração", ["Alcance 2", "Perigosa"],
         notas="Duas mãos, pesada, alcance de 3 m", familia="arma de haste"),
    arma("lanca_montaria", "Lança de montaria", BR, 10, "1d12 perfurante", 4, LAN, "perfuração", ["Alcance 2"],
         notas="Alcance de 3 m; –2 para atacar um alvo colado; a pé, exige as duas mãos", familia="arma de haste"),
    arma("tridente", "Tridente", BR, 5, "1d6 perfurante", 2, LAN, "perfuração", ["Perigosa", "Desarmar"],
         notas="Versátil; pode ser arremessado", familia="tridente, sem Alcance: no D&D o tridente não tem alcance"),
    arma("chicote", "Chicote", BR, 2, "1d4 cortante", 1, "Combate Corpo-a-Corpo: Chicotes", "corte",
         ["Alcance 2", "Desarmar", "Agarrar"], notas="Alcance de 3 m", familia="chicote"),
    # Armas à distância
    arma("arco_curto", "Arco curto", "Arma à distância", 25, "1d6 perfurante", 2, ARC, "perfuração",
         tipo="distancia", forca=False, municao="flechas", notas="Duas mãos", familia="arco"),
    arma("arco_longo", "Arco longo", "Arma à distância", 50, "1d8 perfurante", 3, ARC, "perfuração",
         tipo="distancia", forca=False, municao="flechas", notas="Duas mãos, pesada", familia="arco"),
    arma("besta_leve", "Besta leve", "Arma à distância", 25, "1d8 perfurante", 3, BES, "perfuração",
         tipo="distancia", forca=False, municao="virotes", notas="Duas mãos, recarga", familia="besta"),
    arma("besta_mao", "Besta de mão", "Arma à distância", 75, "1d6 perfurante", 2, BES, "perfuração",
         tipo="distancia", forca=False, municao="virotes", notas="Leve, recarga", familia="besta"),
    arma("besta_pesada", "Besta pesada", "Arma à distância", 50, "1d10 perfurante", 4, BES, "perfuração",
         tipo="distancia", forca=False, municao="virotes", notas="Duas mãos, pesada, recarga", familia="besta"),
    arma("funda", "Funda", "Arma à distância", 0.1, "1d4 concussão", 1, ARR, "esmagamento", tipo="distancia",
         forca=False, municao="balas_de_funda", familia="funda"),
    arma("azagaia", "Azagaias (4)", "Arma à distância", 2, "1d6 perfurante", 2, ARR, "perfuração",
         tipo="distancia", nao_confiavel=True, notas="Arremessadas; somam a Força",
         familia="azagaia; com 4 usos, Não Confiável no lugar do custo à distância"),
    arma("dardos", "Dardos (10)", "Arma à distância", 0.5, "1d4 perfurante", 1, ARR, "perfuração",
         tipo="distancia", notas="Arremessados; somam a Força", familia="azagaia"),
    arma("zarabatana", "Zarabatana", "Arma à distância", 10, "1 perfurante", 1, "Combate à Distância: Zarabatanas",
         "perfuração", tipo="distancia", forca=False, municao="agulhas", notas="Recarga; silenciosa, boa para veneno",
         familia="funda"),
    arma("rede", "Rede", "Arma à distância", 1, "especial", 2, ARR, "—", ["Enredar"], tipo="distancia",
         forca=False, efeito_nome="Agarrar", resistido="Esquiva", custo=3,
         notas="Arremessada; sem dano: prende o alvo, que depois escapa com Força ou Acrobacia",
         familia="rede: Agarrar 2, Enredar"),
    arma("frasco_acido", "Frasco de ácido", "Arma à distância", 25, "2d6 ácido", 4, ARR, "ácido",
         tipo="distancia", forca=False, nao_confiavel=True, notas="Arremessado; uso único",
         familia="arma de uso único: Não Confiável"),
    arma("fogo_alquimico", "Fogo alquímico (frasco)", "Arma à distância", 50, "1d4 fogo", 1, ARR, "fogo",
         tipo="distancia", forca=False, nao_confiavel=True,
         notas="Arremessado; uso único; o alvo segue queimando até gastar uma ação para apagar",
         familia="arma de uso único: Não Confiável"),
    # Munição
    item("flechas", "Flechas (20)", "Munição", 1, "Para arcos.", custo=0),
    item("virotes", "Virotes (20)", "Munição", 1, "Para bestas.", custo=0),
    item("balas_de_funda", "Balas de funda (20)", "Munição", 0.04, "Para fundas.", custo=0),
    item("agulhas", "Agulhas de zarabatana (50)", "Munição", 1, "Para zarabatanas.", custo=0),
    # Armaduras (Proteção) e escudos (defesas ativas)
    # Proteção pela escada do Manual dos Mecanismos Lite (armaduras arcaicas: couro 1, couro cravejado 2, cota de
    # malha ou escamas 3, cota com peitoral 4, placas 5, armadura completa 6). Onde o manual não fala da peça, ela fica
    # entre os vizinhos do D&D, sem que uma armadura mais cara do mesmo tipo proteja menos que outra mais barata.
    item("acolchoada", "Armadura acolchoada", "Armadura", 5, "Proteção 1.", protecao=1,
         fonte_=fonte(LITE, "tecido acolchoado, como o couro; as \"acolchoadas\" do manual são armaduras de samurai")),
    item("couro", "Armadura de couro", "Armadura", 10, "Proteção 1.", protecao=1, fonte_=fonte(LITE, "couro")),
    item("couro_batido", "Couro batido", "Armadura", 45, "Proteção 2.", custo=2, protecao=2,
         fonte_=fonte(LITE, "couro cravejado")),
    item("gibao_peles", "Gibão de peles", "Armadura", 10, "Proteção 2.", custo=2, protecao=2,
         fonte_=fonte(LITE, "como o couro cravejado")),
    item("camisao_malha", "Camisão de malha", "Armadura", 30, "Proteção 2.", custo=2, protecao=2,
         fonte_=fonte(LITE, "cota de malha sem mangas: –1 de Proteção")),
    item("brunea", "Brunea", "Armadura", 50, "Proteção 3.", custo=3, protecao=3,
         fonte_=fonte(LITE, "armadura de escamas")),
    item("cota_malha", "Cota de malha", "Armadura", 75, "Proteção 3.", custo=3, protecao=3,
         fonte_=fonte(LITE, "cota de malha")),
    item("peitoral", "Peitoral", "Armadura", 400, "Proteção 4.", custo=4, protecao=4,
         fonte_=fonte(LITE, "peitoral completo de metal")),
    item("cota_talas", "Cota de talas", "Armadura", 200, "Proteção 4.", custo=4, protecao=4,
         fonte_=fonte(LITE, "talas de metal sobre couro e malha, como a cota com peitoral; acima da cota de malha")),
    item("meia_armadura", "Meia-armadura", "Armadura", 750, "Proteção 5.", custo=5, protecao=5,
         fonte_=fonte(LITE, "armadura de placas: placas afiveladas sobre a malha")),
    item("placas", "Armadura de placas", "Armadura", 1500, "Proteção 6.", custo=6, protecao=6,
         fonte_=fonte(LITE, "armadura completa articulada")),
    item("broquel", "Broquel", "Escudo", 5, "+1 em Esquiva e Aparar.", custo=2, defesas_ativas=1,
         fonte_=fonte(M, "escudo pequeno")),
    item("escudo", "Escudo", "Escudo", 10, "+2 em Esquiva e Aparar.", custo=4, defesas_ativas=2,
         fonte_=fonte(M, "escudo médio")),
    item("escudo_torre", "Escudo de torre", "Escudo", 30, "+3 em Esquiva e Aparar; pesado.", custo=6,
         defesas_ativas=3, fonte_=fonte(M, "escudo grande; preço estimado")),
    # Focos e itens de conjurador
    item("grimorio", "Grimório", "Itens de conjurador", 50, "O livro de magias do mago."),
    item("bolsa_componentes", "Bolsa de componentes", "Itens de conjurador", 25, "Ingredientes para conjurar."),
    item("simbolo_sagrado", "Símbolo sagrado (amuleto)", "Itens de conjurador", 5, "Foco de clérigos e paladinos."),
    item("foco_druidico", "Foco druídico (ramo de visco)", "Itens de conjurador", 1, "Foco de druidas e patrulheiros."),
    item("varinha", "Varinha arcana", "Itens de conjurador", 10, "Foco arcano."),
    item("orbe", "Orbe de cristal", "Itens de conjurador", 20, "Foco arcano."),
    item("giz_runico", "Giz e tintas rúnicas", "Itens de conjurador", 5,
         "Para desenhar as runas que o mago rúnico precisa.", fonte_=fonte(GERAL + "; preço estimado")),
    item("agua_benta", "Água benta (frasco)", "Itens de conjurador", 25, "Fere mortos-vivos e demônios."),
    # Ferramentas e kits
    item("ferramentas_ladrao", "Ferramentas de ladrão", "Ferramentas", 25,
         "Abre fechaduras e desarma armadilhas sem a penalidade de –5."),
    item("kit_disfarce", "Kit de disfarce", "Ferramentas", 25, "Maquiagem e roupas para Enganação."),
    item("kit_herbalismo", "Kit de herbalismo", "Ferramentas", 5, "Prepara remédios e antídotos."),
    item("kit_primeiros_socorros", "Kit de primeiros-socorros", "Ferramentas", 5,
         "Usa Tratamento sem a penalidade de –5."),
    item("kit_escalada", "Kit de escalada", "Ferramentas", 25, "+2 em Atletismo para escalar."),
    item("alaude", "Alaúde", "Ferramentas", 35, "Instrumento de bardo."),
    item("flauta", "Flauta", "Ferramentas", 2, "Instrumento de bardo."),
    item("luneta", "Luneta", "Ferramentas", 1000, "+5 em Percepção visual à distância."),
    item("suprimentos_alquimista", "Suprimentos de alquimista", "Ferramentas", 50,
         "Prepara ácido, fogo alquímico e antitoxina (Especialidade: Alquimia sem a penalidade de –5)."),
    item("kit_envenenador", "Kit de envenenador", "Ferramentas", 50, "Prepara e aplica venenos sem se envenenar."),
    item("kit_falsificacao", "Kit de falsificação", "Ferramentas", 15,
         "Papéis, tintas e selos para falsificar documentos (Enganação sem a penalidade de –5)."),
    item("ferramentas_ferreiro", "Ferramentas de ferreiro", "Ferramentas", 20,
         "Conserta armas e armaduras e forja peças de metal (Tecnologia sem a penalidade de –5)."),
    item("ferramentas_carpinteiro", "Ferramentas de carpinteiro", "Ferramentas", 8,
         "Constrói e conserta portas, carroças e barricadas (Tecnologia sem a penalidade de –5)."),
    item("ferramentas_cartografo", "Ferramentas de cartógrafo", "Ferramentas", 15, "Desenha mapas precisos."),
    item("ferramentas_joalheiro", "Ferramentas de joalheiro", "Ferramentas", 25, "Avalia e lapida gemas."),
    item("ferramentas_navegador", "Ferramentas de navegador", "Ferramentas", 25,
         "Sextante, bússola e cartas para se orientar no mar."),
    item("utensilios_cozinheiro", "Utensílios de cozinheiro", "Ferramentas", 1,
         "Panela, facas e temperos: refeição quente no acampamento."),
    item("dados", "Jogo de dados", "Ferramentas", 0.1, "Para apostar na taverna."),
    item("baralho", "Baralho", "Ferramentas", 0.5, "Para apostar (e trapacear) na taverna."),
    item("lira", "Lira", "Ferramentas", 30, "Instrumento de bardo."),
    item("viola", "Viola", "Ferramentas", 30, "Instrumento de bardo."),
    item("tambor", "Tambor", "Ferramentas", 6, "Instrumento de bardo; marca o passo da tropa."),
    item("trompa", "Trompa", "Ferramentas", 3, "Instrumento de bardo; o toque de caça ou de guerra."),
    item("gaita_foles", "Gaita de foles", "Ferramentas", 30, "Instrumento de bardo; ouvida a quilômetros."),
    # Equipamento de aventura
    item("mochila", "Mochila", "Equipamento de aventura", 2, "Carrega o resto do equipamento."),
    item("saco_dormir", "Saco de dormir", "Equipamento de aventura", 1, "Para dormir ao relento."),
    item("corda", "Corda de cânhamo (15 m)", "Equipamento de aventura", 1, "Para escalar e amarrar."),
    item("tochas", "Tochas (10)", "Equipamento de aventura", 0.1, "Iluminam 6 m por uma hora cada."),
    item("lanterna_coberta", "Lanterna coberta", "Equipamento de aventura", 5, "Ilumina 9 m; não apaga com vento."),
    item("cantil", "Cantil", "Equipamento de aventura", 0.2, "Água para um dia."),
    item("pe_de_cabra", "Pé de cabra", "Equipamento de aventura", 2, "+2 em Força para forçar portas."),
    item("tenda", "Tenda (duas pessoas)", "Equipamento de aventura", 2, "Abrigo de viagem."),
    item("algemas", "Algemas", "Equipamento de aventura", 2, "Prende prisioneiros."),
    item("manto", "Manto", "Equipamento de aventura", 1, "Protege do frio e da chuva."),
    item("aljava", "Aljava", "Equipamento de aventura", 1, "Carrega 20 flechas."),
    item("ampulheta", "Ampulheta", "Equipamento de aventura", 25, "Marca a passagem do tempo."),
    item("apito", "Apito de sinalização", "Equipamento de aventura", 0.05, "Ouvido a centenas de metros."),
    item("ariete", "Aríete portátil", "Equipamento de aventura", 4, "+2 em Força para arrombar portas."),
    item("balanca", "Balança de mercador", "Equipamento de aventura", 5, "Pesa moedas e mercadorias."),
    item("barril", "Barril", "Equipamento de aventura", 2, "Guarda 150 litros de líquido."),
    item("bau", "Baú", "Equipamento de aventura", 5, "Guarda o tesouro; tranca com cadeado."),
    item("bolsa_cinto", "Bolsa de cinto", "Equipamento de aventura", 0.5, "Para moedas e miudezas."),
    item("cadeado", "Cadeado", "Equipamento de aventura", 10,
         "Abri-lo sem a chave pede ferramentas de ladrão e um teste de Tecnologia (CD 15)."),
    item("cobertor", "Cobertor", "Equipamento de aventura", 0.5, "Para as noites frias."),
    item("corda_seda", "Corda de seda (15 m)", "Equipamento de aventura", 10, "Mais leve e forte que a de cânhamo."),
    item("corrente", "Corrente (3 m)", "Equipamento de aventura", 5, "Rompê-la pede Força (CD 20)."),
    item("espelho", "Espelho de aço", "Equipamento de aventura", 5,
         "Espia em volta das esquinas e mostra a medusa sem precisar encará-la."),
    item("esferas", "Esferas de metal (bolsa com 1.000)", "Equipamento de aventura", 1,
         "Espalhadas no chão: quem passa correndo resiste com Acrobacia (CD 10) ou cai."),
    item("estrepes", "Estrepes (saco com 20)", "Equipamento de aventura", 1,
         "Espalhados no chão: quem passa sem cuidado resiste com Esquiva (CD 10) ou fica impedido."),
    item("estojo_mapas", "Estojo para mapas", "Equipamento de aventura", 1, "Protege mapas e pergaminhos da chuva."),
    item("frasco", "Frasco de vidro", "Equipamento de aventura", 1, "Para poções, ácido e amostras."),
    item("gancho", "Gancho de escalada", "Equipamento de aventura", 2,
         "Preso à corda, +2 em Atletismo para escalar muros."),
    item("giz", "Giz (peça)", "Equipamento de aventura", 0.01, "Marca o caminho na masmorra."),
    item("lamparina", "Lamparina", "Equipamento de aventura", 0.5, "Ilumina 4,5 m por 6 horas com um frasco de óleo."),
    item("lanterna_furta_fogo", "Lanterna furta-fogo", "Equipamento de aventura", 10,
         "Facho de luz de 18 m que se fecha num instante."),
    item("livro", "Livro", "Equipamento de aventura", 25, "Um tratado, uma crônica ou um diário em branco."),
    item("lupa", "Lupa", "Equipamento de aventura", 100,
         "+2 em Investigação para examinar de perto; acende fogo com a luz do sol."),
    item("martelo", "Martelo", "Equipamento de aventura", 1, "Para pregos e pitões."),
    item("oleo", "Óleo (frasco)", "Equipamento de aventura", 0.1,
         "Combustível de lamparina; derramado e aceso, queima o chão por alguns turnos."),
    item("pa", "Pá", "Equipamento de aventura", 2, "Cava buracos, covas e trincheiras."),
    item("papel", "Papel (folha)", "Equipamento de aventura", 0.2, "Para cartas e mapas."),
    item("pederneira", "Estojo de pederneira", "Equipamento de aventura", 0.5, "Acende uma fogueira em um minuto."),
    item("pena_escrever", "Pena de escrever", "Equipamento de aventura", 0.02, "Para escrever com tinta."),
    item("pergaminho", "Pergaminho (folha)", "Equipamento de aventura", 0.1, "Mais resistente que o papel."),
    item("picareta", "Picareta de minerador", "Equipamento de aventura", 2, "Cava pedra e terra."),
    item("pitoes", "Pitões de ferro (10)", "Equipamento de aventura", 0.5, "Cravados na rocha, ancoram a corda."),
    item("sabao", "Sabão", "Equipamento de aventura", 0.02, "Para lavar a lama da estrada."),
    item("saco", "Saco", "Equipamento de aventura", 0.01, "Carrega até 15 kg."),
    item("sinete", "Anel de sinete", "Equipamento de aventura", 5, "Lacra cartas com o brasão da família."),
    item("sino", "Sino", "Equipamento de aventura", 1, "Alarme simples para o acampamento."),
    item("tinta", "Tinta (frasco)", "Equipamento de aventura", 10, "Dá para escrever um livro inteiro."),
    item("vara", "Vara de 3 m", "Equipamento de aventura", 0.05, "Cutuca o chão à procura de armadilhas."),
    item("velas", "Velas (10)", "Equipamento de aventura", 0.1, "Iluminam 1,5 m por uma hora cada."),
    item("kit_refeicao", "Kit de refeição", "Equipamento de aventura", 0.2, "Prato, caneca e talheres de lata."),
    item("armadilha_caca", "Armadilha de caça", "Equipamento de aventura", 5,
         "Mandíbulas de ferro escondidas no chão: quem pisa resiste com Esquiva (CD 13) ou fica imóvel até "
         "abri-la com Força (CD 13)."),
    item("pocao_cura", "Poção de cura", "Poções", 50,
         "Recupera um grau de dano (teste de recuperação imediato)."),
    item("antitoxina", "Antitoxina (frasco)", "Poções", 50, "+5 nos testes de Fortitude contra veneno por uma hora."),
    item("veneno", "Veneno básico (frasco)", "Poções", 100,
         "Passado numa lâmina, dardo ou agulha: no próximo acerto, o alvo também resiste com Fortitude (CD 12) "
         "ou fica tonto até o fim da cena."),
    item("bomba_bruxo", "Bomba de bruxo", "Poções", 50,
         "Arremessada, explode num raio de 3 m: quem estiver nele resiste com Fortitude (CD 14) ou fica tonto; "
         "Samum cega, Estrela dançante queima e Gás do dragão envenena (combine o efeito com o mestre).",
         fonte_=GERAL + "; item de The Witcher, sem equivalente no Livro do Jogador; preço do fogo alquímico"),
    item("elixires", "Elixires de bruxo (dose)", "Poções", 50,
         "Andorinha, Trovão, Gato...: o efeito é narrado pelo mestre. Tóxicos para quem não passou pelas mutações.",
         fonte_=GERAL + "; item de The Witcher; preço da poção de cura e do antídoto do Livro do Jogador (50 po)"),
    item("oleo_laminas", "Óleo para lâminas (contra monstros)", "Poções", 5,
         "Passado na espada antes de enfrentar uma espécie de monstro.",
         fonte_=GERAL + "; item de The Witcher, sem equivalente no Livro do Jogador; preço estimado"),
    item("kit_bruxo", "Kit de bruxo", "Kits", 120,
         "O que o bruxo leva da escola: espada de prata, espada de aço, armadura de couro (+2), 3 doses de elixir, "
         "2 óleos para lâminas, kit de herbalismo e bolsa de componentes. Os itens avulsos somariam 365 po; "
         "o kit sai com desconto da escola.", custo=0,
         fonte_=GERAL + "; pacote do gerador para o bruxo caçador de monstros",
         kit=["espada_prata", "espada_longa", "couro_batido", {"id": "elixires", "quantidade": 3},
              {"id": "oleo_laminas", "quantidade": 2}, "kit_herbalismo", "bolsa_componentes"]),
    item("kit_bruxo_vibora", "Kit de bruxo da Víbora", "Kits", 120,
         "O kit do bruxo com um par de adagas longas (uma de prata, uma de aço) no lugar das espadas e um kit de "
         "disfarce para chegar perto do alvo. Os itens avulsos somariam 380 po; o kit sai com desconto da escola.",
         custo=0, fonte_=GERAL + "; pacote do gerador para o bruxo da escola da Víbora",
         kit=["adaga_longa_prata", "adaga_longa", "couro_batido", {"id": "elixires", "quantidade": 3},
              {"id": "oleo_laminas", "quantidade": 2}, "kit_herbalismo", "bolsa_componentes", "kit_disfarce"]),
    item("kit_bruxo_urso", "Kit de bruxo do Urso", "Kits", 150,
         "O kit do bruxo com cota de malha (+3) no lugar do couro batido. Os itens avulsos somariam 395 po; "
         "o kit sai com desconto da escola.",
         custo=0, fonte_=GERAL + "; pacote do gerador para o bruxo da escola do Urso",
         kit=["espada_prata", "espada_longa", "cota_malha", {"id": "elixires", "quantidade": 3},
              {"id": "oleo_laminas", "quantidade": 2}, "kit_herbalismo", "bolsa_componentes"]),
    item("kit_explorador", "Pacote de explorador", "Kits", 10,
         "Mochila, saco de dormir, kit de refeição, estojo de pederneira, 10 tochas, 10 dias de rações, cantil e "
         "corda de cânhamo.", custo=0, fonte_=GERAL + "; pacote do Livro do Jogador (D&D 5e), cap. 5",
         kit=["mochila", "saco_dormir", "kit_refeicao", "pederneira", "tochas", {"id": "racoes", "quantidade": 2},
              "cantil", "corda"]),
    item("kit_masmorra", "Pacote de masmorra", "Kits", 12,
         "Mochila, pé de cabra, martelo, 10 pitões, 10 tochas, estojo de pederneira, 10 dias de rações, cantil e "
         "corda de cânhamo.", custo=0, fonte_=GERAL + "; pacote do Livro do Jogador (D&D 5e), cap. 5",
         kit=["mochila", "pe_de_cabra", "martelo", "pitoes", "tochas", "pederneira",
              {"id": "racoes", "quantidade": 2}, "cantil", "corda"]),
    item("kit_estudioso", "Pacote de estudioso", "Kits", 40,
         "Mochila, livro, tinta, pena de escrever, 10 folhas de pergaminho e uma bolsa de cinto.", custo=0,
         fonte_=GERAL + "; pacote do Livro do Jogador (D&D 5e), cap. 5",
         kit=["mochila", "livro", "tinta", "pena_escrever", "pergaminho", "bolsa_cinto"]),
    # Comida e bebida
    item("racoes", "Rações de viagem (5 dias)", "Comida", 2.5, "Carne seca, pão duro e frutas secas."),
    item("vinho", "Vinho comum (jarra)", "Bebida", 0.2, "Para a estrada ou para a taverna."),
    item("cerveja", "Cerveja (barril pequeno)", "Bebida", 0.4, "Alegra o acampamento."),
    item("pao", "Pão (pedaço)", "Comida", 0.02, "Pão de centeio do dia."),
    item("queijo", "Queijo (pedaço)", "Comida", 0.1, "Dura semanas na mochila."),
    item("carne", "Carne (pedaço)", "Comida", 0.3, "Assada na hora ou salgada para a viagem."),
    item("refeicao", "Refeição na taverna", "Comida", 0.3, "Ensopado, pão e uma caneca."),
    item("cerveja_caneca", "Cerveja (caneca)", "Bebida", 0.04, "Na taverna."),
    item("vinho_fino", "Vinho fino (garrafa)", "Bebida", 10, "Para impressionar um nobre."),
    # Montarias
    item("ponei", "Pônei", "Montaria", 30, "Montaria de halflings e anões.", custo=None),
    item("cavalo_montaria", "Cavalo de montaria", "Montaria", 75, "Montaria comum.", custo=None),
    item("cavalo_guerra", "Cavalo de guerra", "Montaria", 400, "Treinado para o combate.", custo=None),
    item("sela", "Sela de montaria", "Montaria", 10, "Para viajar a cavalo.", custo=None),
    item("burro", "Burro ou mula", "Montaria", 8, "Carrega a bagagem sem reclamar (muito).", custo=None),
    item("cavalo_tracao", "Cavalo de tração", "Montaria", 50, "Puxa carroças e arados.", custo=None),
    item("camelo", "Camelo", "Montaria", 50, "Atravessa o deserto dias sem beber.", custo=None),
    item("mastim", "Mastim", "Montaria", 25, "Cão de guarda e de caça.", custo=None),
    item("alforjes", "Alforjes", "Montaria", 4, "Bolsas presas à sela.", custo=None),
    item("carroca", "Carroça", "Veículos", 35, "Puxada por um cavalo ou burro; leva a carga do grupo.", custo=None),
    item("carruagem", "Carruagem", "Veículos", 100, "Para viajar com conforto (e chamar atenção).", custo=None),
    item("barco_remo", "Barco a remo", "Veículos", 50, "Leva quatro pessoas por rios e lagos.", custo=None),
    # Roupas
    item("roupas_viajante", "Roupas de viajante", "Roupas", 2, "Resistentes, para a estrada."),
    item("roupas_finas", "Roupas finas", "Roupas", 15, "Para a corte e os salões."),
    item("robes", "Robes", "Roupas", 1, "Típicos de magos e sacerdotes."),
    item("roupas_comuns", "Roupas comuns", "Roupas", 0.5, "As de qualquer camponês."),
    item("traje_artista", "Traje de artista", "Roupas", 5, "Cores berrantes para o palco."),
]))


def magia(id_, nome, categoria, catalogo, descricao, arranjo=None, graduacao=None, graduacao_np=None,
          estatistica=None, pericia=None, so_racial=False, tags=(), **extras):
    dados = {"id": id_, "nome": nome, "categoria": categoria, "catalogo": catalogo, "descricao": descricao,
             "tags": list(tags)}
    for chave, valor in (("arranjo", arranjo), ("graduacao", graduacao), ("graduacao_np", graduacao_np),
                         ("estatistica", estatistica), ("pericia", pericia)):
        if valor is not None:
            dados[chave] = valor
    if so_racial:
        dados["so_racial"] = True
    dados.update(extras)
    return dados


ARCANA, DIVINA, NATUREZA = "Magia arcana", "Magia divina", "Magia da natureza"
PACTO, BARDICA = "Magia de pacto", "Magia bárdica"
SINAIS = "Sinais"
FEITICO = "Combate à Distância: Magia"
SINAL = "Combate à Distância: Sinais"

gravar("powers.json", [
    # ---- magia arcana (mago, feiticeiro)
    magia("raio_de_fogo", "Raio de fogo", "arcana", "magicos__raio_mistico_5",
          "Um raio de chamas lançado da ponta dos dedos.", ARCANA, graduacao_np=0,
          estatistica="Dano à Distância (fogo)", pericia=FEITICO, tags=["combate"]),
    magia("misseis_magicos", "Mísseis mágicos", "arcana", "luminosos__pulso_laser_2",
          "Dardos de força mágica que procuram o alvo.", ARCANA, graduacao_np=-2,
          estatistica="Dano à Distância, Multiataque (força)", pericia=FEITICO, tags=["combate"]),
    magia("raio_gelido", "Raio gélido", "arcana", "congelantes__rajada_de_gelo",
          "Um feixe azulado de frio que congela o alvo.", ARCANA, graduacao_np=0,
          estatistica="Dano à Distância (frio)", pericia=FEITICO, tags=["combate"]),
    magia("relampago", "Relâmpago", "arcana", "climaticos__raio",
          "Um raio elétrico que estala entre as mãos e o alvo.", ARCANA, graduacao_np=0,
          estatistica="Dano à Distância (elétrico)", pericia=FEITICO, tags=["combate"]),
    magia("bola_de_fogo", "Bola de fogo", "arcana", "climaticos__tempestade_de_granizo",
          "Uma conta de fogo que explode no ponto escolhido.", ARCANA, graduacao_np=-1,
          estatistica="Dano à Distância, Área Explosão (fogo)", tags=["combate", "area"]),
    magia("sono", "Sono", "arcana", "magicos__feitico_de_sonambulo_2",
          "Uma nuvem de sonolência mágica que derruba os inimigos.", ARCANA, graduacao_np=-1,
          estatistica="Aflição Cumulativa, Área Nuvem (Vontade; tonto, atordoado, adormecido)",
          tags=["controle", "area"]),
    magia("teia", "Teia", "arcana", "animais__teia",
          "Fios grudentos que prendem quem estiver no caminho.", ARCANA, graduacao_np=-1,
          estatistica="Aflição Cumulativa à Distância (Esquiva; impedido e vulnerável, indefeso e imóvel)",
          pericia=FEITICO, tags=["controle"]),
    magia("enfeiticar_pessoa", "Enfeitiçar pessoa", "arcana", "mentais__controle_mental",
          "Faz o alvo ver você como um amigo e obedecer.", ARCANA, graduacao_np=-1,
          pericia=FEITICO, estatistica="Aflição Cumulativa à Percepção (Vontade; tonto, compelido, controlado)",
          tags=["controle", "social"]),
    magia("imagem_silenciosa", "Imagem silenciosa", "arcana", "magicos__fantasmas_de_phoros_2",
          "Cria uma imagem ilusória convincente.", ARCANA, graduacao=4, estatistica="Ilusão (visual)",
          tags=["utilidade"]),
    magia("levitacao", "Levitação", "arcana", "magicos__levitacao_2",
          "Flutua no ar, subindo e descendo à vontade.", ARCANA, graduacao=2, estatistica="Voo",
          tags=["movimento"]),
    magia("passo_nebuloso", "Passo nebuloso", "arcana", "magicos__passagem_mistica_3",
          "Some numa névoa prateada e reaparece adiante.", ARCANA, graduacao=2, estatistica="Teleporte",
          tags=["movimento"]),
    magia("maos_magicas", "Mãos mágicas", "arcana", "magicos__mao_de_heshem_5",
          "Uma mão espectral que move objetos à distância.", ARCANA, graduacao=2, estatistica="Mover Objetos",
          tags=["utilidade"]),
    magia("armadura_arcana", "Armadura arcana", "arcana", "magicos__escudo_mistico",
          "Uma camada invisível de força protege o corpo. Fica de fora do arranjo: dura enquanto o mago conjura outras magias.",
          graduacao_np=-3, estatistica="Proteção, Sustentado", tags=["defesa"]),
    # ---- magia de pacto (bruxo)
    magia("rajada_mistica", "Rajada mística", "pacto", "magicos__poder_de_malador_4",
          "Um raio de energia crepitante dado pelo patrono.", PACTO, graduacao_np=0,
          estatistica="Dano à Distância (força mística)", pericia=FEITICO, tags=["combate"]),
    magia("enfeiticar_pacto", "Encanto do patrono", "pacto", "mentais__controle_mental",
          "O olhar do bruxo prende a vontade do alvo.", PACTO, graduacao_np=-1,
          pericia=FEITICO, estatistica="Aflição Cumulativa à Percepção (Vontade; tonto, compelido, controlado)",
          tags=["controle", "social"]),
    magia("medo_pacto", "Medo", "pacto", "talentos_poderosos__presenca_assustadora",
          "Uma onda de pavor sobrenatural.", PACTO, graduacao_np=-1,
          estatistica="Aflição, Área Percepção visual (Vontade; prejudicado, desabilitado, paralisado)",
          tags=["controle", "area"]),
    magia("passo_sombrio", "Passo sombrio", "pacto", "magicos__caminho_tortuoso_de_karkradas",
          "Entra numa sombra e sai de outra.", PACTO, graduacao=2, estatistica="Teleporte, Acurado (sombras)",
          tags=["movimento"]),
    magia("visao_diabo", "Visão do diabo", "pacto", "sombrios__visao_no_escuro",
          "Enxerga na escuridão, até na mágica.", estatistica="Sentidos 2 (visão no escuro)",
          tags=["percepcao"]),
    # ---- magia bárdica
    magia("zombaria_cruel", "Zombaria cruel", "bardica", "mentais__rajada_mental",
          "Um insulto carregado de magia que machuca a mente.", BARDICA, graduacao_np=-2,
          pericia=FEITICO, estatistica="Dano à Percepção, resistido por Vontade", tags=["combate"]),
    magia("palavra_de_cura", "Palavra de cura", "bardica", "luminosos__cura_luminosa",
          "Um verso que fecha feridas.", BARDICA, graduacao_np=-1, estatistica="Cura", tags=["cura"]),
    magia("sono_bardico", "Canção de ninar", "bardica", "magicos__feitico_de_sonambulo_2",
          "Uma melodia que faz os ouvintes cochilarem.", BARDICA, graduacao_np=-1,
          estatistica="Aflição Cumulativa, Área Nuvem (Vontade; tonto, atordoado, adormecido)",
          tags=["controle", "area"]),
    magia("encantar_plateia", "Encantar plateia", "bardica", "mentais__controle_mental",
          "Prende a atenção de quem escuta.", BARDICA, graduacao_np=-1,
          pericia=FEITICO, estatistica="Aflição Cumulativa à Percepção (Vontade; tonto, compelido, controlado)",
          tags=["controle", "social"]),
    magia("ilusao_bardica", "Truque de ilusão", "bardica", "magicos__fantasmas_de_phoros_2",
          "Imagens e sons ilusórios para distrair.", BARDICA, graduacao=3, estatistica="Ilusão (visual)",
          tags=["utilidade"]),
    # ---- magia divina (clérigo, paladino)
    magia("chama_sagrada", "Chama sagrada", "divina", "magicos__sois_brilhantes_de_sirrion_4",
          "Uma chama radiante desce sobre o alvo.", DIVINA, graduacao_np=0,
          estatistica="Dano à Distância (radiante)", pericia=FEITICO, tags=["combate"]),
    magia("curar_ferimentos", "Curar ferimentos", "divina", "luminosos__cura_luminosa",
          "O toque do sacerdote fecha feridas.", DIVINA, graduacao_np=-1, estatistica="Cura", tags=["cura"]),
    magia("palavra_sagrada", "Palavra sagrada", "divina", "magicos__sinal_de_modrossus_3",
          "Uma palavra divina que atordoa os inimigos ao redor.", DIVINA, graduacao_np=-1,
          estatistica="Aflição, Área Explosão (Vontade; tonto e impedido, atordoado e imóvel, incapacitado)",
          tags=["controle", "area"]),
    magia("expulsar_mortos_vivos", "Expulsar mortos-vivos", "divina", "fatais__comandar_os_mortos",
          "Apresenta o símbolo sagrado e os mortos-vivos recuam.", DIVINA, graduacao_np=-1,
          estatistica="Aflição, Área Percepção auditiva (Vontade; tonto, compelido, controlado), só mortos-vivos",
          tags=["controle", "area"]),
    magia("restauracao", "Restauração menor", "divina", "vitais__cura",
          "Cura doenças e venenos.", DIVINA, graduacao=4, estatistica="Cura, Limitado a doenças e venenos",
          tags=["cura"]),
    magia("luz_divina", "Luz do dia", "divina", "magicos__iluminacao_de_abbridon_3",
          "Uma luz sagrada que espanta a escuridão.", DIVINA, graduacao=1,
          estatistica="Ambiente (luz do dia)", tags=["utilidade"]),
    magia("augurio", "Augúrio", "divina", "magicos__auspicioso_augurio_de_ahgrazu",
          "Os deuses mostram um vislumbre do que vem.",
          estatistica="Segunda Chance, Sentidos 4 (precognição, limitada)", tags=["percepcao"]),
    magia("escudo_da_fe", "Escudo da fé", "divina", "magicos__escudo_brilhante",
          "Um brilho sagrado envolve o devoto. Fica de fora do arranjo.", graduacao_np=-3,
          estatistica="Proteção, Sustentado", tags=["defesa"]),
    magia("destruicao_divina", "Destruição divina", "divina", "fatais__soulfire",
          "A arma do paladino brilha com poder sagrado.", DIVINA, graduacao_np=-2,
          estatistica="Dano corpo a corpo (radiante), resistido por Vontade",
          pericia="Combate Corpo-a-Corpo: Destruição divina", tags=["combate"]),
    magia("cura_pelas_maos", "Cura pelas mãos", "divina", "luminosos__cura_luminosa",
          "Uma reserva de cura que o paladino passa pelo toque.", DIVINA, graduacao_np=-2, estatistica="Cura",
          tags=["cura"]),
    magia("aura_de_coragem", "Aura de coragem", "divina", "mentais__escudo_mental",
          "A fé do paladino protege a mente contra o medo. Fica de fora do arranjo.", graduacao_np=-3,
          estatistica="Vontade Aumentada, Limitada a efeitos mentais", tags=["defesa"],
          ajustes_limitados={"Vontade": "graduacao"}),
    # ---- magia da natureza (druida, patrulheiro)
    magia("chamar_relampago", "Chamar relâmpago", "natureza", "climaticos__raio",
          "Um raio desce das nuvens sobre o inimigo.", NATUREZA, graduacao_np=0,
          estatistica="Dano à Distância (elétrico)", pericia=FEITICO, tags=["combate"]),
    magia("chicote_espinhos", "Chicote de espinhos", "natureza", "vegetais__arremesso_de_espinhos",
          "Espinhos disparados de um galho vivo.", NATUREZA, graduacao_np=-2,
          estatistica="Dano à Distância, Multiataque (perfurante)", pericia=FEITICO, tags=["combate"]),
    magia("constricao", "Constrição", "natureza", "vegetais__rede_de_vinhas",
          "Raízes e vinhas brotam do chão e agarram os inimigos.", NATUREZA, graduacao_np=-1,
          estatistica="Aflição à Distância, Área Explosão (Esquiva; impedido e vulnerável, indefeso e imóvel)",
          tags=["controle", "area"]),
    magia("curar_natureza", "Bálsamo da natureza", "natureza", "luminosos__cura_luminosa",
          "Ervas e seiva fecham feridas.", NATUREZA, graduacao_np=-1, estatistica="Cura", tags=["cura"]),
    magia("falar_com_animais", "Falar com animais", "natureza", "animais__falar_com_animais",
          "Entende e é entendido pelos animais.", estatistica="Compreender 2 (animais)", tags=["social"]),
    magia("passo_sem_rastro", "Passo sem rastro", "natureza", "vegetais__passeio_pela_floresta",
          "Atravessa a mata sem deixar pegadas.", estatistica="Movimento 2 (sem rastros), em áreas com vegetação",
          tags=["movimento"]),
    magia("pele_de_casca", "Pele de casca", "natureza", "animais__pele_protetora",
          "A pele endurece como casca de árvore. Fica de fora do arranjo.", graduacao_np=-3, estatistica="Proteção",
          tags=["defesa"]),
    magia("forma_selvagem", "Forma selvagem", "natureza", "animais__forma_animal",
          "Assume a forma de um animal que já viu.", estatistica="Morfar 2 (formas animais), Metamorfo",
          tags=["utilidade"]),
    magia("companheiro_animal", "Companheiro animal", "natureza", "animais__companheiro_animal",
          "Um animal leal que luta ao lado do patrulheiro.", graduacao=2,
          estatistica="Invocar Companheiro Animal, Heroico", tags=["combate"]),
    # ---- dons marciais (guerreiro, bárbaro, monge, ladino)
    magia("retomar_folego", "Retomar o fôlego", "marcial", "marciais__segundo_folego",
          "Um último fôlego quando o combate aperta.", graduacao=2,
          estatistica="Cura, Engatilhado (dois graus de dano), Limitado a si mesmo", tags=["cura"]),
    magia("furia", "Fúria", "marcial", "marciais__furia_berserker",
          "A fúria do bárbaro: mais força e nenhum medo, mas menos cuidado na defesa.", graduacao_np=-3,
          estatistica="Destemido, Força Aumentada, Sustentada (–1 nas defesas ativas)", tags=["combate"]),
    magia("golpe_atordoante", "Golpe atordoante", "marcial", "talentos_poderosos__ponto_de_pressao",
          "Um golpe preciso num ponto vital que deixa o alvo tonto.", graduacao_np=-1,
          estatistica="Aflição corpo a corpo (Fortitude; tonto, atordoado, incapacitado)",
          pericia="Combate Corpo-a-Corpo: Briga", tags=["combate"]),
    magia("artes_marciais", "Artes marciais", "marcial", "talentos_poderosos__forca_impressionante",
          "Socos e chutes treinados que batem como armas.", graduacao_np=-3,
          estatistica="Dano baseado em Força (golpes de artes marciais)", pericia="Combate Corpo-a-Corpo: Briga",
          tags=["combate"]),
    magia("integridade_corporal", "Integridade corporal", "marcial", "marciais__balanco_de_chi",
          "O monge usa o ki para curar o próprio corpo.", graduacao=2, estatistica="Cura (ki)", tags=["cura"]),
    magia("queda_lenta", "Queda lenta", "marcial", "marciais__queda_de_gato",
          "Cai de pé e sem se machucar.", estatistica="De Pé, Movimento 1 (queda segura)", tags=["movimento"]),
    magia("corrida_parede", "Passo do vento", "marcial", "marciais__corrida_pela_parede",
          "Corre pelas paredes por alguns passos.", estatistica="Movimento 2 (escalar paredes), só em movimento",
          tags=["movimento"]),
    magia("escamas_draconicas", "Escamas dracônicas", "arcana", "animais__pele_protetora",
          "O sangue de dragão do feiticeiro aparece na pele. Fica de fora do arranjo.", graduacao_np=-3,
          estatistica="Proteção", tags=["defesa"]),
    # ---- magias das subclasses extras
    magia("raio_necrotico", "Raio necrótico", "arcana", "magicos__poder_de_malador_4",
          "Um raio esverdeado que apodrece a carne.", ARCANA, graduacao_np=0,
          estatistica="Dano à Distância (necrótico)", pericia=FEITICO, tags=["combate"]),
    magia("toque_vampirico", "Toque da morte", "arcana", "fatais__toque_mortal",
          "O toque gelado do necromante tira a vida do alvo.", ARCANA, graduacao_np=-1,
          estatistica="Aflição Cumulativa corpo a corpo (Fortitude; prejudicado, desabilitado, moribundo)",
          pericia="Combate Corpo-a-Corpo: Magia", tags=["combate"]),
    magia("falar_com_mortos", "Falar com os mortos", "arcana", "fatais__falar_com_os_mortos",
          "Faz um cadáver responder a algumas perguntas.", ARCANA,
          estatistica="Sentidos 4 (pós-cognição, só com mortos)", tags=["percepcao"]),
    magia("videncia", "Vidência", "arcana", "magicos__perscrutar_4",
          "Vê e ouve um lugar distante numa bola de cristal ou numa bacia com água.", ARCANA, graduacao=2,
          estatistica="Sentido Remoto (visual, auditivo)", tags=["percepcao"]),
    magia("visao_verdadeira", "Visão verdadeira", "arcana", "ilusorios__percepcao_verdadeira",
          "Enxerga através de ilusões e disfarces mágicos.", ARCANA,
          estatistica="Sentidos 5 (vê através de ilusões)", tags=["percepcao"]),
    magia("pele_de_pedra", "Pele de pedra", "arcana", "terrestres__armadura_rochosa",
          "A pele vira pedra por algumas horas. Fica de fora do arranjo.", graduacao_np=-4,
          estatistica="Proteção, Impenetrável", tags=["defesa"]),
    magia("raio_sombrio", "Raio sombrio", "arcana", "sombrios__explosao_negra",
          "Uma lança de escuridão gelada.", ARCANA, graduacao_np=0,
          estatistica="Dano à Distância (sombras geladas)", pericia=FEITICO, tags=["combate"]),
    magia("telepatia", "Telepatia", "arcana", "mentais__comunicacao_mental",
          "Fala de mente para mente.", ARCANA, graduacao=1, estatistica="Comunicação 1 (mental)",
          tags=["social"]),
    magia("ler_mentes", "Ler mentes", "arcana", "mentais__leitura_mental_2",
          "Lê os pensamentos de superfície de quem está perto.", ARCANA, graduacao_np=-2,
          estatistica="Leitura Mental", tags=["social"]),
    magia("golpe_arcano", "Lâmina arcana", "arcana", "magicos__fisgo_de_heshem_3",
          "A lâmina brilha com magia e corta através de armaduras.", ARCANA, graduacao_np=-2,
          estatistica="Dano corpo a corpo, Penetrante (força arcana)", pericia="Combate Corpo-a-Corpo: Magia",
          tags=["combate"]),
    magia("onda_trovejante", "Ira da tempestade", "divina", "climaticos__raio",
          "O deus da tempestade lança trovões pelas mãos do clérigo.", DIVINA, graduacao_np=0,
          estatistica="Dano à Distância (trovão e relâmpago)", pericia=FEITICO, tags=["combate"]),
    magia("duplicata_divina", "Invocar duplicata", "divina", "ilusorios__duplicata_ilusoria",
          "Uma cópia ilusória do clérigo engana os inimigos.", DIVINA,
          estatistica="Ilusão 2 (visual e auditiva), só uma cópia de si mesmo", tags=["utilidade"]),
    magia("toque_sombrio_divino", "Toque do ceifador", "divina", "fatais__toque_mortal",
          "O clérigo da morte suga a vida com um toque.", DIVINA, graduacao_np=-1,
          estatistica="Aflição Cumulativa corpo a corpo (Fortitude; prejudicado, desabilitado, moribundo)",
          pericia="Combate Corpo-a-Corpo: Magia", tags=["combate"]),
    magia("medo_divino", "Presença aterradora", "divina", "talentos_poderosos__presenca_assustadora",
          "Os inimigos tremem diante do conquistador.", DIVINA, graduacao_np=-1,
          estatistica="Aflição, Área Percepção visual (Vontade; prejudicado, desabilitado, paralisado)",
          tags=["controle", "area"]),
    magia("chamas_selvagens", "Chamas selvagens", "natureza", "flamejantes__explosao_de_fogo",
          "O fogo que destrói para a floresta renascer.", NATUREZA, graduacao_np=0,
          estatistica="Dano à Distância (fogo)", pericia=FEITICO, tags=["combate"]),
    magia("nuvem_esporos", "Nuvem de esporos", "natureza", "vegetais__nuvem_de_polen",
          "Esporos que sufocam e enfraquecem.", NATUREZA, graduacao_np=-1,
          estatistica="Aflição, Área Nuvem (Fortitude; fatigado, exausto, incapacitado)", tags=["controle", "area"]),
    magia("flecha_estelar", "Flecha estelar", "natureza", "luminosos__feixe_laser",
          "Um raio de luz das estrelas.", NATUREZA, graduacao_np=0,
          estatistica="Dano à Distância (luz estelar)", pericia=FEITICO, tags=["combate"]),
    magia("lamina_pacto", "Lâmina do pacto", "pacto", "magicos__fisgo_de_heshem_3",
          "Uma arma mágica dada pelo patrono, que aparece na mão do bruxo.", PACTO, graduacao_np=-2,
          estatistica="Dano corpo a corpo, Penetrante (arma do pacto)", pericia="Combate Corpo-a-Corpo: Espadas",
          tags=["combate"]),
    magia("cura_celestial", "Luz curativa", "pacto", "luminosos__cura_luminosa",
          "O patrono celestial fecha feridas.", PACTO, graduacao_np=-1, estatistica="Cura", tags=["cura"]),
    magia("medo_bardico", "Sussurros assustadores", "bardica", "talentos_poderosos__presenca_assustadora",
          "Segredos sussurrados que enchem o alvo de pavor.", BARDICA, graduacao_np=-1,
          estatistica="Aflição, Área Percepção visual (Vontade; prejudicado, desabilitado, paralisado)",
          tags=["controle", "area"]),
    magia("raio_solar_monge", "Raio solar", "marcial", "luminosos__feixe_laser",
          "O monge concentra o ki num raio de luz.", graduacao_np=-1,
          estatistica="Dano à Distância (luz do ki)", pericia=FEITICO, tags=["combate"]),
    # ---- Sinais e mutações do caçador de monstros (bruxo no estilo The Witcher)
    magia("igni", "Igni", "sinais", "flamejantes__baforada_de_fogo",
          "Sinal de fogo: um cone de chamas arcanas que sai da palma da mão.", SINAIS, graduacao_np=0,
          estatistica="Dano, Área Cone (chama arcana)", tags=["combate", "area"]),
    magia("aard", "Aard", "sinais", "marciais__grito_de_kiai",
          "Sinal telecinético: uma onda de força em cone que derruba e desarma.", SINAIS, graduacao_np=-1,
          estatistica="Aflição, Área Cone (Esquiva, superada por Fortitude; impedido e vulnerável, indefeso e caído)",
          tags=["controle", "area"]),
    magia("axii", "Axii", "sinais", "luminosos__strobo_hipinotico",
          "Sinal de influência: confunde a mente e acalma feras.", SINAIS, graduacao_np=-1,
          estatistica="Aflição com Distância de Percepção (Resistido e Superado por Vontade; em Transe, Compelido), "
                      "Grau Limitado, Depende de Visão", pericia=SINAL,
          tags=["controle", "social"]),
    magia("yrden", "Yrden", "sinais", "elementais__encaixotar",
          "Sinal de armadilha: um círculo mágico que prende criaturas e espectros.", SINAIS, graduacao_np=-2,
          estatistica="Aflição à Distância (Esquiva; impedido e vulnerável, indefeso e imóvel), círculo no chão",
          pericia=SINAL, tags=["controle"]),
    magia("quen", "Quen", "sinais", "magicos__escudo_mistico",
          "Sinal de proteção: um escudo cinético ao redor do corpo.", SINAIS, graduacao_np=-2,
          estatistica="Proteção, Sustentado (escudo cinético)", tags=["defesa"]),
    magia("sentidos_de_bruxo", "Sentidos de bruxo", "mutacao", "animais__sentidos_animais",
          "Mutação: pupilas de gato, faro de cão de caça e o arrepio que denuncia a magia por perto.", graduacao=5,
          estatistica="Sentidos 5 (visão no escuro, faro aguçado, rastrear pelo faro, percepção da magia)",
          tags=["percepcao"]),
    magia("olhos_de_gato", "Olhos de gato", "mutacao", "sombrios__visao_no_escuro",
          "Mutação: pupilas verticais que enxergam no escuro.", estatistica="Sentidos 2 (visão no escuro)",
          tags=["percepcao"]),
    magia("metabolismo_mutante", "Metabolismo mutante", "mutacao", "talentos_poderosos__imunidade_adquirida",
          "Mutação: resiste a venenos, doenças e às toxinas dos próprios elixires.",
          estatistica="Imunidade 2 (doenças e venenos), Limitada a meio efeito", tags=["defesa"]),
    # ---- traços raciais (não aparecem na lista de magias; vêm com a raça)
    magia("visao_escuro", "Visão no escuro", "racial", "sombrios__visao_no_escuro",
          "Enxerga no escuro como se fosse penumbra.", estatistica="Sentidos 2 (visão no escuro)", so_racial=True),
    magia("resiliencia_ana", "Resiliência anã", "racial", "talentos_poderosos__imunidade_adquirida",
          "Resiste a venenos e doenças.", estatistica="Imunidade 2 (doenças e venenos), Limitada a meio efeito",
          so_racial=True),
    magia("ancestralidade_feerica", "Ancestralidade feérica", "racial", "mentais__escudo_mental",
          "Magia de encantamento tem dificuldade com sua mente.", graduacao=2,
          estatistica="Vontade Aumentada 2, Limitada a efeitos mentais", so_racial=True,
          ajustes_limitados={"Vontade": "graduacao"}),
    magia("sentidos_agucados", "Sentidos aguçados", "racial", "talentos_poderosos__olho_de_aguia",
          "Vê longe e com detalhes.", estatistica="Sentidos 1 (visão estendida)", so_racial=True),
    magia("esperteza_gnomica", "Esperteza gnômica", "racial", "mentais__escudo_mental",
          "A mente rápida dos gnomos resiste à magia.", graduacao=2,
          estatistica="Vontade Aumentada 2, Limitada a efeitos mentais", so_racial=True,
          ajustes_limitados={"Vontade": "graduacao"}),
    magia("sopro_draconico", "Sopro dracônico", "racial", "flamejantes__baforada_de_fogo",
          "Sopra fogo como os ancestrais dragões.", graduacao_np=-2, estatistica="Dano, Área Cone (fogo)",
          so_racial=True),
    magia("legado_infernal", "Legado infernal", "racial", "magicos__chamas_dos_phoros",
          "Chamas infernais herdadas de um ancestral demoníaco.", graduacao=2,
          estatistica="Dano à Distância (fogo infernal)", pericia=FEITICO, so_racial=True),
])

gravar("names.json", {
    "humano": {
        "nomes": ["Aldric", "Brenna", "Cedric", "Daria", "Edmund", "Freya", "Gareth", "Helena", "Ivo", "Jocelyn",
                  "Kael", "Lyra", "Marcus", "Nadia", "Osric", "Petra", "Roland", "Selene", "Tobias", "Ursula",
                  "Viktor", "Wren", "Isolde", "Bran"],
        "sobrenomes": ["de Valdoria", "Martelo-Firme", "do Vale Verde", "Corvo-Negro", "de Altamira", "Ferreira",
                       "Lobo-Cinzento", "da Ponte", "Cervo-Branco", "Pedra-Alta", "do Norte", "Mão-de-Prata"],
        "apelidos": ["o Ousado", "a Raposa", "o Justo", "a Sombra", "o Ferreiro", "a Lâmina", "o Errante",
                     "o Velho", "a Corajosa", "o Silencioso"]},
    "anao": {
        "nomes": ["Thorin", "Dagna", "Balin", "Helga", "Gimrik", "Brunhilda", "Durgan", "Vistra", "Rurik", "Eldeth",
                  "Bruenor", "Kathra"],
        "sobrenomes": ["Barba-de-Ferro", "Martelo-de-Pedra", "Forjafogo", "Quebra-Rochas", "Escudo-de-Bronze",
                       "Machado-Rubro", "Punho-de-Granito"]},
    "elfo": {
        "nomes": ["Aelar", "Lia", "Thamior", "Naivara", "Erevan", "Sariel", "Galinndan", "Keyleth", "Ivellios",
                  "Shava", "Soveliss", "Enna"],
        "sobrenomes": ["Folha-de-Prata", "Brisa-da-Lua", "Estrela-Cadente", "Galho-Alto", "Orvalho-Claro",
                       "Canto-do-Rio"]},
    "halfling": {
        "nomes": ["Milo", "Rosie", "Perrin", "Lidda", "Corrin", "Seraphina", "Wellby", "Callie", "Roscoe", "Merla"],
        "sobrenomes": ["Pé-Leve", "Bom-Barril", "Morro-Verde", "Folha-de-Chá", "Toca-Funda", "Mão-Ligeira"]},
    "monstro": {
        "nomes": ["Grishnak", "Vorgath", "Skarr", "Mordrek", "Ulgra", "Zarkhul", "Bhaal", "Kragg", "Nyx", "Azgor",
                  "Malgrim", "Thraxx"],
        "sobrenomes": ["o Devorador", "o Cruel", "Presa-Negra", "Olho-de-Brasa", "o Antigo", "Garra-Rubra"]},
    "animal": {
        "nomes": ["Presa", "Sombra", "Uivo", "Garra", "Cinza", "Trovão", "Brasa", "Neve", "Rasga", "Pata-Larga"],
        "sobrenomes": ["da Matilha", "da Floresta", "da Montanha", "das Cavernas"]},
    "goblin": {
        "nomes": ["Snik", "Grubb", "Zizzik", "Nakk", "Ruzga", "Pixa", "Krub", "Fizzig", "Gubbo", "Skritch", "Yark",
                  "Bozz", "Tikka", "Grax", "Nubb", "Zogg", "Murk", "Rikka", "Drub", "Squee"],
        "sobrenomes": ["Dente-Torto", "Orelha-Rasgada", "Nariz-de-Batata", "Rói-Corda", "Pé-de-Lama", "Olho-Furado",
                       "Unha-Suja", "Sopa-Fria", "Mão-Leve", "Rabo-de-Rato"]},
})

gravar("complications.json", {
    "_fonte": "Livro básico, cap. 2 (complicações), com exemplos de fantasia medieval",
    "motivacoes": [
        {"nome": "Cobiça", "exemplo": "Ouro, joias e o tesouro do dragão."},
        {"nome": "Justiça", "exemplo": "Livrar o reino do tirano que o oprime."},
        {"nome": "Vingança", "exemplo": "Os orcs que queimaram sua aldeia vão pagar."},
        {"nome": "Adrenalina", "exemplo": "A próxima masmorra, o próximo monstro."},
        {"nome": "Reconhecimento", "exemplo": "Ter seu nome cantado pelos bardos."},
        {"nome": "Responsabilidade", "exemplo": "A aldeia, a ordem ou o clã que depende de você."},
        {"nome": "Fazer o Bem", "exemplo": "Proteger os fracos, como manda o juramento."},
        {"nome": "Fé", "exemplo": "Levar a palavra do seu deus até os confins do mundo."},
        {"nome": "Conhecimento", "exemplo": "Descobrir os segredos da magia antiga."},
        {"nome": "Patriotismo", "exemplo": "Lealdade à coroa e ao reino."},
    ],
    "complicacoes": [
        {"nome": "Inimigo", "exemplo": "Um necromante jurou trazer você de volta como servo."},
        {"nome": "Responsabilidade", "exemplo": "Um juramento a uma ordem de cavalaria ou a um templo."},
        {"nome": "Vício", "exemplo": "Jogo de dados, vinho ou a emoção do roubo."},
        {"nome": "Segredo", "exemplo": "Um pacto com um demônio que ninguém pode descobrir."},
        {"nome": "Perda de Poder", "exemplo": "Sem o grimório ou o símbolo sagrado, a magia some."},
        {"nome": "Reputação", "exemplo": "Conhecido como ladrão em todas as cidades do reino."},
        {"nome": "Rivalidade", "exemplo": "Outro aventureiro que disputa as mesmas recompensas."},
        {"nome": "Relacionamento", "exemplo": "Um irmão capturado pelos homens do barão."},
        {"nome": "Honra", "exemplo": "Nunca foge de um duelo nem quebra a palavra dada."},
        {"nome": "Obsessão", "exemplo": "Encontrar a cidade perdida dos antigos."},
        {"nome": "Ódio", "exemplo": "Odeia mortos-vivos e quem os ergue."},
        {"nome": "Fobia", "exemplo": "Pavor de lugares fechados, como masmorras."},
        {"nome": "Irritação", "exemplo": "Perde a cabeça quando duvidam da sua coragem."},
        {"nome": "Peculiaridade", "exemplo": "Conversa com a própria espada."},
        {"nome": "Deficiência", "exemplo": "Perdeu um olho para um basilisco."},
        {"nome": "Preconceito", "exemplo": "Ninguém confia num meio-orc ou num tiefling."},
        {"nome": "Fama", "exemplo": "Todos conhecem o matador do troll da ponte."},
        {"nome": "Maldição", "exemplo": "Uma bruxa amaldiçoou sua família até a sétima geração."},
    ],
})
# ---------------------------------------------------------------- player.json: classes, subclasses e raças

def foco(id_, nome, descricao, vantagens=(), prioridades=(), armas=(), itens=(), implantes=(), implantes_opcionais=(),
         substitui=None, falhas=(), variantes=(), rotulo_variante=None):
    dados = {"id": id_, "nome": nome, "descricao": descricao, "vantagens": list(vantagens),
             "prioridades": list(prioridades), "armas": list(armas), "itens": list(itens), "implantes": list(implantes)}
    if implantes_opcionais:
        dados["implantes_opcionais"] = list(implantes_opcionais)
    if substitui:
        dados["substitui"] = substitui   # campos da classe que o foco troca inteiros
    if falhas:
        dados["falhas"] = list(falhas)
    if variantes:
        dados["rotulo_variante"] = rotulo_variante or "Variante"
        dados["variantes"] = list(variantes)   # aplicadas por cima do foco (ex.: as escolas do bruxo)
    return dados


def variante(id_, nome, descricao, vantagens=(), prioridades=(), armas=(), itens=(), implantes=(), substitui=None,
             complicacoes=()):
    dados = {"id": id_, "nome": nome, "descricao": descricao}
    for campo, valor in (("vantagens", vantagens), ("prioridades", prioridades), ("armas", armas), ("itens", itens),
                         ("implantes", implantes)):
        if valor:
            dados[campo] = list(valor)
    if substitui:
        dados["substitui"] = substitui
    if complicacoes:
        dados["complicacoes"] = [{"nome": n, "detalhe": d} for n, d in complicacoes]
    return dados


def classe(id_, nome, conceito, essenciais, opcionais, prioridades, principais, secundarias, itens_ess, itens_opc,
           magias_ess, magias_opc, motivacoes, complicacoes, focos):
    return {"id": id_, "nome": nome, "conceito": conceito, "vantagens_essenciais": essenciais,
            "vantagens_opcionais": opcionais, "prioridades": prioridades,
            "armas": {"principais": principais, "secundarias": secundarias},
            "itens": {"essenciais": itens_ess, "opcionais": itens_opc},
            "implantes": {"essenciais": magias_ess, "opcionais": magias_opc},
            "sugestoes": {"motivacoes": motivacoes,
                          "complicacoes": [{"nome": n, "detalhe": d} for n, d in complicacoes]},
            "focos": focos}


def p(*textos):
    return list(textos)


PRIORIDADES_DO_BRUXO = p("habilidade:Lut", "pericia:Combate Corpo-a-Corpo: Espadas", "pericia:Especialidade: Bruxo",
                         "habilidade:Vig", "habilidade:Agi", "defesa:Vontade", "defesa:Fortitude", "habilidade:For",
                         "defesa:Aparar", "pericia:Percepção", "pericia:Combate à Distância: Sinais", "habilidade:Pro",
                         "pericia:Furtividade", "pericia:Atletismo", "defesa:Esquiva", "pericia:Intimidação")

# Escolas dos bruxos de The Witcher, escolhidas depois da subclasse Caçador de monstros. Lince e Garça quase não
# aparecem nos jogos e livros: o estilo delas é uma leitura do gerador.
ESCOLAS_DE_BRUXO = [
    variante("lobo", "Escola do Lobo",
             "Equilibrada: espada, Sinais e saber sobre monstros na mesma medida. É o bruxo clássico."),
    variante("gato", "Escola do Gato",
             "Rápidos e traiçoeiros: confiam na agilidade, na esquiva e em atacar das sombras.",
             vantagens=["Finta Ágil"],
             prioridades=p("habilidade:Agi", "pericia:Combate Corpo-a-Corpo: Espadas", "defesa:Esquiva",
                           "pericia:Furtividade", "pericia:Acrobacia"),
             complicacoes=[("Reputação", "Medalhão de gato: todos acham que é um assassino de aluguel sem código.")]),
    variante("grifo", "Escola do Grifo",
             "Estudiosos e cavalheirescos: os Sinais são mais fortes que os de qualquer outra escola.",
             prioridades=p("pericia:Combate à Distância: Sinais", "pericia:Especialidade: Bruxo", "habilidade:Des",
                           "defesa:Vontade"),
             implantes=["yrden"],
             complicacoes=[("Honra", "O código do Grifo: protege os fracos, cumpre a palavra e nunca abandona "
                                     "um contrato.")]),
    variante("vibora", "Escola da Víbora",
             "Caçam pessoas, não monstros: investigam, se infiltram e matam com venenos e um par de adagas longas "
             "no lugar das espadas. Muitos servem a reis como assassinos.",
             vantagens=["Esconder-se à Plena Vista"],
             prioridades=p("pericia:Combate Corpo-a-Corpo: Adagas", "pericia:Investigação", "pericia:Furtividade",
                           "pericia:Intimidação", "pericia:Enganação"),
             substitui={"prioridades": [x.replace("Espadas", "Adagas") for x in PRIORIDADES_DO_BRUXO],
                        "armas": {"principais": ["kit_bruxo_vibora"], "secundarias": ["besta_mao", "dardos"]}},
             complicacoes=[("Segredo", "Já matou um rei a mando de outro; se descobrirem, a cabeça dele vale ouro."),
                           ("Responsabilidade", "Serve a um senhor que paga bem e não aceita recusas.")]),
    variante("urso", "Escola do Urso",
             "Brutos e solitários: armadura pesada, golpes fortes e resistência para aguentar o que mataria outro "
             "bruxo.",
             vantagens=["Ataque Poderoso", "Duro de Matar"],
             prioridades=p("habilidade:For", "habilidade:Vig", "defesa:Fortitude"),
             substitui={"armas": {"principais": ["kit_bruxo_urso"], "secundarias": ["machado_batalha", "adaga"]}},
             complicacoes=[("Irritação", "Perde a cabeça fácil e resolve tudo no braço.")]),
    variante("manticora", "Escola da Manticora",
             "Alquimistas: vivem de elixires e óleos e conhecem as ervas melhor que qualquer herbalista.",
             vantagens=["Inventor"],
             prioridades=p("pericia:Especialidade: Bruxo", "habilidade:Int", "pericia:Tratamento"),
             itens=["elixires", "pocao_cura"],
             complicacoes=[("Vício", "Toma elixires demais, até quando não precisa.")]),
    variante("lince", "Escola do Lince",
             "Atiradores: preferem acertar o monstro de longe, com a besta e olhos de caçador, antes de puxar "
             "a espada.",
             vantagens=["Mira Aprimorada"],
             prioridades=p("pericia:Combate à Distância: Bestas", "habilidade:Des", "pericia:Percepção"),
             armas=["besta_leve"]),
    variante("garca", "Escola da Garça",
             "Do litoral e dos rios: nadam, escalam e lutam em barcos melhor que ninguém e caçam afogadores e "
             "sereias como rotina. Gostam de lanças.",
             vantagens=["Ambiente Favorito (aquático)"],
             prioridades=p("pericia:Atletismo", "habilidade:Agi", "pericia:Acrobacia"),
             armas=["lanca"]),
]


ARCANAS = ["misseis_magicos", "raio_gelido", "relampago", "bola_de_fogo", "sono", "teia", "enfeiticar_pessoa",
           "imagem_silenciosa", "levitacao", "passo_nebuloso", "maos_magicas", "armadura_arcana"]
AVENTURA = ["mochila", "saco_dormir", "corda", "tochas", "cantil"]

CLASSES = [
    classe("guerreiro", "Guerreiro", "Mestre das armas e da armadura, treinado para a linha de frente.",
           ["Ataque Poderoso", "Iniciativa Aprimorada", "Rolamento Defensivo"],
           ["Ataque Defensivo", "Duro de Matar", "Interpor-se", "Derrubar Aprimorado", "Liderança", "Quebrar Arma"],
           p("habilidade:Lut", "pericia:Combate Corpo-a-Corpo: Espadas", "habilidade:Vig", "habilidade:For",
             "defesa:Aparar", "pericia:Atletismo", "pericia:Intimidação", "defesa:Fortitude", "pericia:Percepção"),
           ["espada_longa", "machado_batalha", "martelo_guerra", "espada_grande"],
           ["arco_longo", "besta_leve", "adaga", "lanca"], ["cota_malha", "escudo", "mochila"],
           ["saco_dormir", "corda", "tochas", "cantil", "kit_primeiros_socorros"], ["retomar_folego"], [],
           ["Reconhecimento", "Cobiça", "Responsabilidade", "Adrenalina"],
           [("Honra", "Nunca ataca um inimigo desarmado nem foge de um desafio."),
            ("Rivalidade", "Um antigo companheiro de armas quer provar que é melhor."),
            ("Responsabilidade", "Serve a um senhor que nem sempre manda fazer o certo."),
            ("Inimigo", "O mercenário que ele derrotou num torneio quer revanche.")],
           [foco("campeao", "Campeão", "Força bruta e golpes certeiros: cada acerto pode ser o último.",
                 ["Crítico Aprimorado (espada grande)"], p("habilidade:For", "pericia:Atletismo"), ["espada_grande"]),
            foco("mestre_batalha", "Mestre de batalha", "Usa manobras para derrubar e desarmar os inimigos.",
                 ["Derrubar Aprimorado", "Desarmar Aprimorado"], p("pericia:Intuição"), ["espada_longa"]),
            foco("cavaleiro_arcano", "Cavaleiro arcano", "Combina a espada com um pouco de magia arcana.",
                 [], p("habilidade:Int", "pericia:Especialidade: Magia"), ["espada_longa"], ["grimorio"],
                 ["armadura_arcana", "raio_de_fogo"])]),
    classe("barbaro", "Bárbaro", "Guerreiro selvagem que luta movido pela fúria.",
           ["Ataque Poderoso", "Destemido", "Duro de Matar"],
           ["Ataque Imprudente", "Agarrar Aprimorado", "Assustar", "Tolerância Maior", "Quebrar Aprimorado"],
           p("habilidade:For", "habilidade:Vig", "pericia:Combate Corpo-a-Corpo: Machados", "habilidade:Lut",
             "defesa:Fortitude", "pericia:Atletismo", "pericia:Intimidação", "pericia:Percepção",
             "pericia:Especialidade: Sobrevivência"),
           ["machado_grande", "espada_grande", "malho", "machado_batalha"], ["machadinha", "azagaia", "lanca"],
           ["gibao_peles", "mochila"], ["saco_dormir", "cantil", "corda", "tochas", "cerveja"], ["furia"], [],
           ["Adrenalina", "Vingança", "Responsabilidade", "Reconhecimento"],
           [("Irritação", "Perde a cabeça quando é desafiado."),
            ("Preconceito", "Nas cidades, todos o tratam como um selvagem."),
            ("Inimigo", "Os escravistas que levaram sua tribo sabem que ele os caça."),
            ("Vício", "Não recusa uma bebida nem uma briga de taverna.")],
           [foco("furioso", "Caminho do furioso", "Entra numa fúria tão grande que esquece a dor.",
                 ["Ataque Imprudente"], p("habilidade:For")),
            foco("totemico", "Guerreiro totêmico", "Um espírito animal guia sua fúria.",
                 ["Empatia com Animais"], p("pericia:Percepção"), implantes=["falar_com_animais"]),
            foco("montanhes", "Selvagem das montanhas", "Cresceu no frio e na neve, longe de qualquer cidade.",
                 ["Tolerância Maior"], p("pericia:Especialidade: Sobrevivência", "defesa:Fortitude"))]),
    classe("ladino", "Ladino", "Especialista em furtividade, armadilhas e golpes pelas costas.",
           ["Finta Ágil", "Evasão", "Ferramentas Aprimoradas"],
           ["Esconder-se à Plena Vista", "Ataque Acurado", "Tontear", "Ação em Movimento", "Contatos",
            "Sorte de Principiante"],
           p("habilidade:Agi", "pericia:Furtividade", "pericia:Prestidigitação", "habilidade:Des", "pericia:Enganação",
             "defesa:Esquiva", "pericia:Percepção", "pericia:Acrobacia", "pericia:Combate Corpo-a-Corpo: Espadas",
             "pericia:Investigação"),
           ["rapieira", "espada_curta"], ["besta_mao", "arco_curto", "adaga", "dardos"],
           ["couro", "ferramentas_ladrao", "mochila"], ["corda", "kit_disfarce", "tochas", "pe_de_cabra", "roupas_finas"],
           [], [], ["Cobiça", "Adrenalina", "Reconhecimento", "Vingança"],
           [("Reputação", "Procurado em duas cidades por roubo."),
            ("Inimigo", "A guilda de ladrões quer de volta o que ele levou."),
            ("Vício", "Não resiste a um bolso cheio."),
            ("Segredo", "Ninguém sabe que ele é filho de um nobre.")],
           [foco("ladrao", "Ladrão", "Entra e sai de qualquer lugar com o que veio buscar.",
                 [], p("pericia:Prestidigitação", "pericia:Atletismo"), itens=["pe_de_cabra"]),
            foco("assassino", "Assassino", "Ataca primeiro e some antes de alguém perceber.",
                 ["Tomar a Iniciativa"], p("pericia:Furtividade", "pericia:Enganação"), itens=["kit_disfarce"]),
            foco("trapaceiro_arcano", "Trapaceiro arcano", "Usa truques de magia para roubar e enganar.",
                 [], p("habilidade:Int", "pericia:Especialidade: Magia"), implantes=["maos_magicas", "imagem_silenciosa"])]),
    classe("mago", "Mago", "Estudioso da magia arcana, que guarda as fórmulas no grimório.",
           ["Ritualista", "Esforço Extraordinário"],
           ["Memória Eidética", "Bem Informado", "Idiomas", "Artífice", "Mira Aprimorada"],
           p("habilidade:Int", "pericia:Especialidade: Magia", "pericia:Combate à Distância: Magia", "vantagem:Ataque à Distância", "habilidade:Des",
             "defesa:Vontade", "defesa:Esquiva", "pericia:Investigação", "pericia:Percepção",
             "pericia:Especialidade: História"),
           ["bordao", "adaga"], ["besta_leve", "dardos"], ["grimorio", "bolsa_componentes", "robes"],
           ["mochila", "tochas", "saco_dormir", "varinha", "orbe"], ["raio_de_fogo", "armadura_arcana"], ARCANAS,
           ["Conhecimento", "Reconhecimento", "Cobiça", "Fazer o Bem"],
           [("Perda de Poder", "Sem o grimório, não prepara as magias."),
            ("Obsessão", "Procura um tomo perdido de magia antiga."),
            ("Rivalidade", "Um colega da academia quer superá-lo."),
            ("Fobia", "Tem pavor de demônios desde que invocou um por engano.")],
           [foco("evocacao", "Escola de Evocação", "Fogo, gelo e relâmpagos: magia para destruir.",
                 [], p("pericia:Combate à Distância: Magia"), implantes=["bola_de_fogo", "relampago"]),
            foco("ilusao", "Escola de Ilusão", "Engana os sentidos e as mentes.",
                 [], p("pericia:Enganação"), implantes=["imagem_silenciosa", "enfeiticar_pessoa"]),
            foco("abjuracao", "Escola de Abjuração", "Protege, bloqueia e escapa.",
                 [], p("defesa:Vontade", "defesa:Esquiva"), implantes=["passo_nebuloso", "teia"])]),
    classe("feiticeiro", "Feiticeiro", "Nasceu com magia no sangue e a conjura por instinto.",
           ["Esforço Extraordinário", "Destemido"], ["Atraente", "Fascinar", "Inspirar", "Mira Aprimorada",
                                                     "Tomar a Iniciativa"],
           p("habilidade:Pre", "pericia:Combate à Distância: Magia", "vantagem:Ataque à Distância", "habilidade:Des", "pericia:Persuasão",
             "pericia:Intimidação", "defesa:Vontade", "defesa:Esquiva", "pericia:Especialidade: Magia"),
           ["adaga", "bordao"], ["dardos", "besta_leve"], ["bolsa_componentes", "robes"], ["mochila", "orbe", "saco_dormir"],
           ["raio_de_fogo"], ARCANAS, ["Reconhecimento", "Adrenalina", "Conhecimento", "Vingança"],
           [("Segredo", "Ninguém pode saber de onde vem sua magia."),
            ("Inimigo", "Caçadores de bruxas estão no seu encalço."),
            ("Irritação", "Quando perde a calma, a magia escapa sozinha."),
            ("Preconceito", "O povo da aldeia acha que ele é amaldiçoado.")],
           [foco("draconico", "Linhagem dracônica", "Um dragão ancestral deu a ele escamas e fogo.",
                 [], p("pericia:Intimidação"), implantes=["escamas_draconicas", "bola_de_fogo"]),
            foco("selvagem", "Magia selvagem", "A magia sai do controle, para o bem ou para o mal.",
                 ["Sorte"], p("pericia:Acrobacia"), implantes=["passo_nebuloso"]),
            foco("tempestade", "Alma da tempestade", "Raios e ventos respondem ao seu humor.",
                 [], p("pericia:Combate à Distância: Magia"), implantes=["relampago", "levitacao"])]),
    classe("bruxo", "Bruxo", "Fez um pacto com um ser poderoso em troca de magia.",
           ["Esforço Extraordinário", "Assustar"], ["Atraente", "Fascinar", "Bem Informado", "Contatos", "Ritualista"],
           p("habilidade:Pre", "pericia:Combate à Distância: Magia", "vantagem:Ataque à Distância", "pericia:Enganação", "pericia:Intimidação",
             "defesa:Vontade", "habilidade:Des", "defesa:Esquiva", "pericia:Especialidade: Magia", "pericia:Investigação"),
           ["adaga", "bordao"], ["besta_leve"], ["couro", "bolsa_componentes"], ["orbe", "mochila", "grimorio"],
           ["rajada_mistica"], ["enfeiticar_pacto", "medo_pacto", "passo_sombrio", "visao_diabo"],
           ["Cobiça", "Conhecimento", "Vingança", "Reconhecimento"],
           [("Segredo", "Ninguém pode descobrir o pacto."),
            ("Responsabilidade", "O patrono cobra favores na pior hora."),
            ("Inimigo", "Um paladino jurou destruir quem lida com demônios."),
            ("Obsessão", "Quer quebrar o pacto sem perder a magia.")],
           [foco("corruptor", "Pacto com o Corruptor", "Um demônio deu a ele fogo e medo.",
                 [], p("pericia:Intimidação"), implantes=["medo_pacto"]),
            foco("arquifada", "Pacto com a Arquifada", "Uma senhora das fadas empresta seu encanto.",
                 [], p("pericia:Persuasão", "pericia:Enganação"), implantes=["enfeiticar_pacto"]),
            foco("grande_antigo", "Pacto com o Grande Antigo", "Uma entidade de além das estrelas sussurra segredos.",
                 ["Bem Informado"], p("pericia:Investigação", "pericia:Intuição"), implantes=["visao_diabo", "passo_sombrio"])]),
    classe("clerigo", "Clérigo", "Sacerdote guerreiro que canaliza o poder do seu deus.",
           ["Inspirar", "Ritualista"], ["Liderança", "Duro de Matar", "Interpor-se", "Bem Relacionado", "Tolerância Maior"],
           p("habilidade:Pro", "pericia:Combate à Distância: Magia", "vantagem:Ataque à Distância", "pericia:Especialidade: Religião", "defesa:Vontade",
             "pericia:Tratamento", "pericia:Intuição", "habilidade:Vig", "defesa:Fortitude", "pericia:Persuasão",
             "pericia:Combate Corpo-a-Corpo: Maças"),
           ["maca", "martelo_guerra", "maca_estrela"], ["besta_leve", "funda"],
           ["cota_malha", "escudo", "simbolo_sagrado"], ["mochila", "agua_benta", "kit_primeiros_socorros", "tochas"],
           ["chama_sagrada", "curar_ferimentos"],
           ["palavra_sagrada", "expulsar_mortos_vivos", "restauracao", "luz_divina", "augurio", "escudo_da_fe"],
           ["Fé", "Fazer o Bem", "Responsabilidade", "Justiça"],
           [("Responsabilidade", "Deve obediência ao templo e ao sumo sacerdote."),
            ("Honra", "Nunca nega ajuda a quem pede em nome do seu deus."),
            ("Ódio", "Odeia mortos-vivos e quem os ergue."),
            ("Inimigo", "Um culto rival quer seu templo em ruínas.")],
           [foco("vida", "Domínio da Vida", "Curandeiro acima de tudo.",
                 [], p("pericia:Tratamento"), implantes=["restauracao"]),
            foco("guerra", "Domínio da Guerra", "Sacerdote de um deus da batalha, na linha de frente.",
                 ["Ataque Poderoso"], p("habilidade:Lut", "pericia:Combate Corpo-a-Corpo: Maças")),
            foco("luz", "Domínio da Luz", "Leva a luz divina para os lugares mais escuros.",
                 [], p("pericia:Percepção"), implantes=["luz_divina", "palavra_sagrada"])]),
    classe("paladino", "Paladino", "Cavaleiro sagrado ligado a um juramento.",
           ["Destemido", "Interpor-se"], ["Ataque Poderoso", "Liderança", "Inspirar", "Duro de Matar",
                                          "Rolamento Defensivo"],
           p("habilidade:Lut", "habilidade:For", "pericia:Combate Corpo-a-Corpo: Espadas", "habilidade:Pre",
             "defesa:Vontade", "defesa:Aparar", "pericia:Persuasão", "pericia:Intimidação",
             "pericia:Especialidade: Religião", "pericia:Especialidade: Cavalgar"),
           ["espada_longa", "martelo_guerra", "maca_estrela", "espada_grande"], ["lanca", "azagaia", "lanca_montaria"],
           ["cota_malha", "escudo", "simbolo_sagrado"], ["cavalo_montaria", "sela", "mochila", "agua_benta"],
           ["cura_pelas_maos", "aura_de_coragem"], ["destruicao_divina", "escudo_da_fe", "luz_divina", "curar_ferimentos"],
           ["Justiça", "Fazer o Bem", "Fé", "Responsabilidade"],
           [("Honra", "Nunca mente e nunca quebra o juramento."),
            ("Responsabilidade", "Responde à ordem de cavalaria que o sagrou."),
            ("Inimigo", "Um cavaleiro caído quer arrastá-lo junto."),
            ("Fama", "Os camponeses o chamam para resolver qualquer problema.")],
           [foco("devocao", "Juramento de Devoção", "O cavaleiro sagrado das histórias: honesto, corajoso e justo.",
                 [], p("pericia:Persuasão"), implantes=["destruicao_divina"]),
            foco("ancioes", "Juramento dos Anciões", "Protege a luz e a vida contra as trevas.",
                 ["Tolerância Maior"], p("defesa:Vontade"), implantes=["escudo_da_fe"]),
            foco("vinganca", "Juramento de Vingança", "Caça os grandes malfeitores até o fim.",
                 ["Inimigo Favorito"], p("pericia:Investigação", "pericia:Intimidação"), implantes=["destruicao_divina"])]),
    classe("patrulheiro", "Patrulheiro", "Caçador e batedor das terras selvagens.",
           ["Rastrear", "Inimigo Favorito"], ["Mira Aprimorada", "Ataque à Distância", "Empatia com Animais",
                                              "Saque Rápido", "Iniciativa Aprimorada"],
           p("habilidade:Des", "pericia:Combate à Distância: Arcos", "pericia:Percepção", "pericia:Furtividade",
             "pericia:Especialidade: Sobrevivência", "habilidade:Pro", "defesa:Esquiva", "pericia:Atletismo",
             "habilidade:Agi"),
           ["arco_longo", "arco_curto"], ["espada_curta", "cimitarra", "machadinha"],
           ["couro_batido", "mochila", "saco_dormir"], ["corda", "cantil", "tenda", "kit_herbalismo", "cavalo_montaria"],
           ["passo_sem_rastro"], ["falar_com_animais", "curar_natureza", "constricao", "chicote_espinhos"],
           ["Responsabilidade", "Vingança", "Fazer o Bem", "Adrenalina"],
           [("Ódio", "Odeia os orcs que destruíram sua aldeia."),
            ("Responsabilidade", "Protege uma floresta e todos que vivem nela."),
            ("Peculiaridade", "Fica desconfortável dentro de cidades."),
            ("Inimigo", "Uma tribo de goblins conhece seu rosto.")],
           [foco("cacador", "Caçador", "Especialista em derrubar monstros.",
                 ["Ataque à Distância"], p("pericia:Combate à Distância: Arcos")),
            foco("mestre_feras", "Mestre das feras", "Luta ao lado de um animal companheiro.",
                 ["Empatia com Animais"], p("pericia:Tratamento"), implantes=["companheiro_animal"]),
            foco("batedor", "Batedor da fronteira", "Vai na frente, abrindo caminho e espionando.",
                 [], p("pericia:Furtividade", "pericia:Especialidade: Sobrevivência"), itens=["corda"])]),
    classe("druida", "Druida", "Guardião da natureza, que tira poder das plantas, dos animais e do clima.",
           ["Empatia com Animais", "Ritualista"], ["Rastrear", "Bem Informado", "Tolerância Maior"],
           p("habilidade:Pro", "pericia:Combate à Distância: Magia", "vantagem:Ataque à Distância", "pericia:Especialidade: Natureza",
             "pericia:Tratamento", "defesa:Vontade", "pericia:Percepção", "pericia:Especialidade: Sobrevivência",
             "habilidade:Vig", "defesa:Fortitude"),
           ["bordao", "cimitarra", "foice_curta"], ["funda", "dardos", "lanca"],
           ["couro", "foco_druidico", "kit_herbalismo"], ["mochila", "saco_dormir", "cantil"],
           ["chamar_relampago", "curar_natureza"],
           ["constricao", "chicote_espinhos", "falar_com_animais", "pele_de_casca", "passo_sem_rastro", "forma_selvagem"],
           ["Responsabilidade", "Fazer o Bem", "Fé", "Vingança"],
           [("Responsabilidade", "Protege um bosque sagrado."),
            ("Preconceito", "Na cidade, o chamam de bruxo."),
            ("Honra", "Nunca usa armadura nem escudo de metal."),
            ("Ódio", "Odeia quem derruba florestas por lucro.")],
           [foco("terra", "Círculo da Terra", "Tira poder da terra e das plantas.",
                 [], p("pericia:Especialidade: Natureza"), implantes=["constricao"]),
            foco("lua", "Círculo da Lua", "Vira fera e luta como uma.",
                 [], p("habilidade:Vig"), implantes=["forma_selvagem"]),
            foco("pastor", "Círculo do Pastor", "Fala com os animais e os chama para ajudar.",
                 [], p("pericia:Tratamento"), implantes=["falar_com_animais"])]),
    classe("monge", "Monge", "Artista marcial que domina o próprio corpo com o ki.",
           ["Evasão", "Iniciativa Aprimorada"], ["Agarrar Aprimorado", "Derrubar Aprimorado", "Esquiva Fabulosa",
                                                 "Defesa Aprimorada", "Ação em Movimento", "Luta no Chão"],
           p("habilidade:Agi", "habilidade:Lut", "pericia:Combate Corpo-a-Corpo: Briga", "defesa:Esquiva",
             "defesa:Aparar", "pericia:Acrobacia", "pericia:Intuição", "pericia:Atletismo", "pericia:Furtividade",
             "defesa:Vontade"),
           ["bordao", "lanca", "espada_curta"], ["dardos"], ["roupas_viajante", "mochila"],
           ["saco_dormir", "cantil", "flauta"], ["artes_marciais", "golpe_atordoante"], ["integridade_corporal", "queda_lenta", "corrida_parede"],
           ["Conhecimento", "Fazer o Bem", "Responsabilidade", "Fé"],
           [("Honra", "Nunca usa armas de corte nem armadura."),
            ("Responsabilidade", "Deve obediência ao mosteiro."),
            ("Rivalidade", "Um monge de outro mosteiro quer provar seu estilo."),
            ("Peculiaridade", "Medita antes de qualquer luta.")],
           [foco("mao_aberta", "Caminho da Mão Aberta", "Derruba e empurra com as mãos nuas.",
                 ["Derrubar Aprimorado"], p("pericia:Combate Corpo-a-Corpo: Briga")),
            foco("sombra", "Caminho da Sombra", "Ninja que usa o ki para se esconder e atacar.",
                 [], p("pericia:Furtividade"), implantes=["passo_sombrio"]),
            foco("elementos", "Caminho dos Quatro Elementos", "Molda fogo e vento com o ki.",
                 [], p("pericia:Combate à Distância: Magia"), implantes=["raio_de_fogo"])]),
    classe("bardo", "Bardo", "Músico e contador de histórias cuja magia vem da música.",
           ["Inspirar", "Fascinar"], ["Atraente", "Zombar", "Contatos", "Faz Tudo", "Bem Informado", "Sorte de Principiante"],
           p("habilidade:Pre", "pericia:Especialidade: Música", "pericia:Persuasão", "pericia:Enganação",
             "pericia:Combate à Distância: Magia", "pericia:Intuição", "habilidade:Des", "defesa:Esquiva",
             "defesa:Vontade", "pericia:Acrobacia"),
           ["rapieira", "espada_curta"], ["besta_mao", "arco_curto", "adaga"], ["couro", "alaude"],
           ["flauta", "roupas_finas", "kit_disfarce", "mochila", "vinho"], ["zombaria_cruel", "palavra_de_cura"],
           ["sono_bardico", "encantar_plateia", "ilusao_bardica"],
           ["Reconhecimento", "Adrenalina", "Conhecimento", "Cobiça"],
           [("Fama", "Todo mundo conhece suas canções, inclusive quem ele satirizou."),
            ("Vício", "Não resiste a um jogo de cartas ou a um romance."),
            ("Inimigo", "Um nobre que ele ridicularizou quer vingança."),
            ("Peculiaridade", "Narra as próprias aventuras em voz alta.")],
           [foco("conhecimento", "Colégio do Conhecimento", "Sabe um pouco de tudo e muito de histórias antigas.",
                 ["Bem Informado"], p("pericia:Investigação", "pericia:Especialidade: História")),
            foco("bravura", "Colégio da Bravura", "Canta no meio da batalha, de espada na mão.",
                 ["Ataque Defensivo"], p("habilidade:Lut", "pericia:Combate Corpo-a-Corpo: Espadas")),
            foco("glamour", "Colégio do Glamour", "Encanta qualquer plateia com magia feérica.",
                 [], p("pericia:Persuasão"), implantes=["encantar_plateia"])]),
]


# Subclasses extras: estilos de luta, escolas de magia, linhagens, pactos, domínios, juramentos e caminhos.
RUNAS = {"id": "runas", "nome": "Magias rúnicas", "arranjo": ARCANA, "custo": -2,
         "descricao": "Só conjura desenhando as runas no ar, no chão ou na pele: Ativação (ação padrão)."}
EXTRAS = {
    "guerreiro": [
        foco("cavaleiro", "Cavaleiro", "Luta montado, de lança em riste.", ["Ação em Movimento"],
             p("pericia:Especialidade: Cavalgar", "pericia:Combate Corpo-a-Corpo: Lanças"), ["lanca_montaria"],
             ["cavalo_montaria", "sela"]),
        foco("arqueiro", "Arqueiro de elite", "Derruba o inimigo antes que ele chegue perto.",
             ["Mira Aprimorada", "Ataque à Distância"], p("habilidade:Des", "pericia:Combate à Distância: Arcos"),
             ["arco_longo"]),
        foco("gladiador", "Gladiador", "Luta para a plateia: provoca, finta e termina com estilo.",
             ["Zombar", "Ataque Imprudente"], p("pericia:Intimidação", "pericia:Acrobacia"), ["espada_curta"]),
    ],
    "barbaro": [
        foco("guardiao_ancestral", "Guardião ancestral", "Os espíritos dos antepassados protegem os aliados.",
             ["Interpor-se"], p("defesa:Vontade", "pericia:Intuição")),
        foco("coracao_fera", "Coração de fera", "Na fúria, luta com a força e a ferocidade de um animal.",
             ["Agarrar Aprimorado"], p("habilidade:For", "pericia:Atletismo")),
    ],
    "ladino": [
        foco("espadachim", "Espadachim", "Duelista elegante que vence com fintas e charme.",
             ["Zombar", "Ataque Defensivo"],
             p("pericia:Acrobacia", "pericia:Persuasão", "pericia:Combate Corpo-a-Corpo: Espadas"), ["rapieira"],
             ["roupas_finas"]),
        foco("mestre_intriga", "Mestre da intriga", "Espião e manipulador das cortes.", ["Contatos", "Bem Relacionado"],
             p("pericia:Enganação", "pericia:Persuasão", "pericia:Intuição"), itens=["kit_disfarce", "roupas_finas"]),
    ],
    "mago": [
        foco("necromancia", "Escola de Necromancia", "Estuda a morte e conversa com quem já se foi.",
             [], p("pericia:Especialidade: Religião"),
             implantes=["raio_necrotico", "toque_vampirico", "falar_com_mortos"]),
        foco("adivinhacao", "Escola de Adivinhação", "Vê longe, vê o futuro e vê através de mentiras.",
             ["Avaliação"], p("pericia:Percepção", "pericia:Intuição"), implantes=["videncia", "visao_verdadeira"]),
        foco("encantamento", "Escola de Encantamento", "Dobra a vontade dos outros com palavras e magia.",
             ["Fascinar"], p("habilidade:Pre", "pericia:Persuasão"), implantes=["enfeiticar_pessoa", "sono"]),
        foco("transmutacao", "Escola de Transmutação", "Muda a matéria: pedra na pele, chumbo que flutua.",
             [], p("habilidade:Vig", "pericia:Especialidade: Alquimia"), implantes=["pele_de_pedra", "levitacao"]),
        foco("runico", "Mago rúnico",
             "As magias só funcionam quando ele desenha as runas (Ativação: ação padrão, –2 PP no arranjo). "
             "Mais lento para conjurar, mas sobra ponto para o resto.",
             [], p("pericia:Especialidade: Runas", "pericia:Prestidigitação"), itens=["giz_runico"],
             implantes=["armadura_arcana", "teia"], falhas=[RUNAS]),
        foco("lamina_cantante", "Lâmina cantante", "Dança com a espada e a magia ao mesmo tempo.", ["Finta Ágil"],
             p("habilidade:Agi", "pericia:Acrobacia", "pericia:Combate Corpo-a-Corpo: Magia"), ["rapieira"],
             implantes=["golpe_arcano"]),
    ],
    "feiticeiro": [
        foco("sombrio", "Linhagem sombria", "Nasceu das sombras: conjura escuridão e enxerga nela.",
             [], p("pericia:Furtividade"), implantes=["raio_sombrio", "visao_diabo"]),
        foco("mente_aberrante", "Mente aberrante", "Uma mente tocada por algo de fora do mundo.",
             [], p("pericia:Intuição"), implantes=["telepatia", "ler_mentes"]),
    ],
    "bruxo": [
        foco("cacador_monstros", "Caçador de monstros",
             "No estilo dos bruxos de The Witcher: passou pelas mutações, carrega uma espada de aço para homens e "
             "uma de prata para monstros, usa Sinais simples e conhece as criaturas que caça. Não fez pacto: "
             "troca as magias de pacto da classe pelos Sinais.",
             substitui={
                 "conceito": "Caçador de monstros mutante, treinado desde criança para matar o que assombra o mundo.",
                 # Vantagens, perícia única e Sinais como na ficha de referência do usuário (Gaelen de Venger).
                 "vantagens_essenciais": ["Ritualista", "Artífice", "Rastrear", "Saque Rápido", "Destemido"],
                 "vantagens_opcionais": ["Ataque Poderoso", "Ataque Acurado", "Iniciativa Aprimorada",
                                         "Rolamento Defensivo", "Inimigo Favorito", "Esquiva Fabulosa"],
                 "prioridades": PRIORIDADES_DO_BRUXO,
                 # Sobra do orçamento sem Presença: o bruxo é frio e estranho (Presença –1 na ficha de referência).
                 "habilidades_de_reserva": ["Vig", "Agi", "For", "Pro", "Lut", "Des", "Int"],
                 # O kit traz as espadas, a armadura e os elixires; as armas soltas são extras.
                 "armas": {"principais": ["kit_bruxo"], "secundarias": ["besta_mao", "adaga"]},
                 "itens": {"essenciais": [], "opcionais": ["cavalo_montaria", "sela", "corda", "saco_dormir"]},
                 # Os Sinais são padrão: Igni é o efeito principal e os outros, efeitos alternativos (1 PP cada).
                 "implantes": {"essenciais": ["igni", "quen", "aard", "axii", "sentidos_de_bruxo",
                                              "metabolismo_mutante"],
                               "opcionais": ["yrden"]},
                 "sugestoes": {"motivacoes": ["Cobiça", "Responsabilidade", "Fazer o Bem", "Vingança"],
                               "complicacoes": [
                                   {"nome": "Preconceito", "fixa": True,
                                    "detalhe": "Mutante odiado e temido: os olhos de gato, a pele pálida e o estigma "
                                               "dos bruxos fazem o povo, os guardas e os nobres desconfiarem dele."},
                                   {"nome": "Honra", "detalhe": "O código do bruxo: não mata inocentes nem criaturas "
                                                                 "injustiçadas, cobra pelas caçadas e foge da política."},
                                   {"nome": "Peculiaridade", "detalhe": "Toxicidade alquímica: depois dos elixires, "
                                                                         "veias pretas no rosto e ninguém quer conversa."},
                                   {"nome": "Relacionamento", "detalhe": "Uma criança de sangue nobre que ele jurou proteger."},
                                   {"nome": "Inimigo", "detalhe": "Caçadores de bruxas querem vê-lo na fogueira."}]},
             },
             rotulo_variante="Escola", variantes=ESCOLAS_DE_BRUXO),
        foco("lamina", "Pacto da lâmina", "O patrono deu uma arma mágica que aparece na mão do bruxo.",
             ["Ataque Poderoso"], p("habilidade:Lut", "pericia:Combate Corpo-a-Corpo: Espadas"),
             implantes=["lamina_pacto"]),
        foco("celestial", "Pacto com o Celestial", "Um ser de luz empresta poder de cura.", [],
             p("pericia:Tratamento"), implantes=["cura_celestial"]),
    ],
    "clerigo": [
        foco("tempestade", "Domínio da Tempestade", "Serve ao deus dos trovões e do mar.", [],
             p("pericia:Combate à Distância: Magia"), implantes=["onda_trovejante"]),
        foco("trapaca", "Domínio da Trapaça", "Serve a um deus das mentiras e dos ladrões.", [],
             p("pericia:Enganação", "pericia:Furtividade"), implantes=["duplicata_divina"]),
        foco("morte", "Domínio da Morte", "Serve ao deus que leva as almas.", [],
             p("pericia:Intimidação"), implantes=["toque_sombrio_divino"]),
        foco("conhecimento", "Domínio do Conhecimento", "Guarda os segredos da biblioteca do templo.",
             ["Bem Informado"], p("pericia:Investigação", "pericia:Especialidade: História"), implantes=["augurio"]),
    ],
    "paladino": [
        foco("coroa", "Juramento da Coroa", "Serve ao rei e à lei.", ["Liderança"],
             p("pericia:Persuasão", "defesa:Fortitude"), implantes=["escudo_da_fe"]),
        foco("conquista", "Juramento de Conquista", "Governa pelo medo e pela força.", ["Assustar"],
             p("pericia:Intimidação"), implantes=["medo_divino"]),
    ],
    "patrulheiro": [
        foco("perseguidor", "Perseguidor sombrio", "Caça nas trevas, onde os outros não enxergam.",
             ["Tomar a Iniciativa"], p("pericia:Furtividade", "pericia:Percepção"), implantes=["olhos_de_gato"]),
        foco("andarilho_feerico", "Andarilho feérico", "Tocado pelas fadas: encanta e some num piscar de olhos.",
             [], p("habilidade:Pre", "pericia:Persuasão"), implantes=["passo_nebuloso"]),
    ],
    "druida": [
        foco("fogo", "Círculo do Fogo selvagem", "O fogo que destrói para a floresta renascer.", [],
             p("pericia:Combate à Distância: Magia"), implantes=["chamas_selvagens"]),
        foco("esporos", "Círculo dos Esporos", "Fungos e decomposição: a natureza que apodrece.", [],
             p("pericia:Especialidade: Natureza"), implantes=["nuvem_esporos"]),
        foco("estrelas", "Círculo das Estrelas", "Lê o futuro nas constelações e lança luz estelar.", [],
             p("pericia:Percepção"), implantes=["flecha_estelar", "augurio"]),
    ],
    "monge": [
        foco("bebado", "Caminho do Mestre Bêbado", "Cambaleia, confunde e acerta quando ninguém espera.",
             ["Finta Ágil", "Esquiva Fabulosa"], p("pericia:Acrobacia", "pericia:Enganação"), itens=["vinho"]),
        foco("alma_solar", "Caminho da Alma Solar", "Concentra o ki em raios de luz.", [],
             p("pericia:Combate à Distância: Magia"), implantes=["raio_solar_monge"]),
    ],
    "bardo": [
        foco("espadas", "Colégio das Espadas", "Artista de lâminas: malabarismo e combate como espetáculo.",
             ["Finta Ágil"], p("pericia:Acrobacia", "pericia:Combate Corpo-a-Corpo: Espadas"), ["cimitarra"]),
        foco("sussurros", "Colégio dos Sussurros", "Espião que usa o medo e os segredos alheios.", ["Contatos"],
             p("pericia:Enganação", "pericia:Intimidação"), implantes=["medo_bardico"]),
    ],
}
for _classe in CLASSES:
    _classe["focos"] += EXTRAS.get(_classe["id"], [])


def raca(id_, nome, descricao, nomes="humano", habilidades=None, vantagens=None, pericias=None, poderes=()):
    return {"id": id_, "nome": nome, "descricao": descricao, "nomes": nomes, "habilidades": habilidades or {},
            "vantagens": vantagens or {}, "pericias": pericias or {}, "poderes": list(poderes)}


RACAS = [
    raca("humano", "Humano", "Versáteis e ambiciosos. Sem traços raciais: todos os pontos ficam livres para a classe."),
    raca("anao", "Anão", "Robustos e teimosos, filhos das montanhas.", "anao", {"Vig": 1},
         poderes=["visao_escuro", "resiliencia_ana"]),
    raca("elfo", "Elfo", "Graciosos e de vida longa, com sentidos afiados e sangue feérico.", "elfo", {"Agi": 1},
         pericias={"Percepção": 2}, poderes=["visao_escuro", "ancestralidade_feerica", "sentidos_agucados"]),
    raca("halfling", "Halfling", "Pequenos, discretos e sortudos.", "halfling", {"Agi": 1},
         vantagens={"Sorte": 1}, pericias={"Furtividade": 2}),
    raca("draconato", "Draconato", "Descendentes de dragões, orgulhosos e com um sopro de fogo.", "humano",
         {"For": 1, "Pre": 1}, poderes=["sopro_draconico"]),
    raca("gnomo", "Gnomo", "Pequenos, curiosos e inventivos.", "halfling", {"Int": 1},
         poderes=["visao_escuro", "esperteza_gnomica"]),
    raca("meio_elfo", "Meio-elfo", "Entre dois mundos, à vontade em ambos.", "elfo", {"Pre": 1},
         pericias={"Persuasão": 2}, poderes=["visao_escuro", "ancestralidade_feerica"]),
    raca("meio_orc", "Meio-orc", "Fortes e difíceis de derrubar.", "monstro", {"For": 1},
         vantagens={"Duro de Matar": 1}, pericias={"Intimidação": 2}, poderes=["visao_escuro"]),
    raca("tiefling", "Tiefling", "Têm sangue infernal: chifres, cauda e chamas na ponta dos dedos.", "humano",
         {"Pre": 1}, poderes=["visao_escuro", "legado_infernal"]),
]

gravar("player.json", {
    "_fonte": "Classes, subclasses e raças do Livro do Jogador de D&D 5e, convertidas para M&M 3e pelo gerador. "
              "Dinheiro inicial em peças de ouro: o aventureiro padrão recebe 150 po (o bastante para o kit "
              "inicial das classes no Livro do Jogador, como a cota de malha do guerreiro); as outras faixas seguem a escada de Riqueza/Benefício do "
              "faroeste (Guia do Mestre).",
    "riqueza": [
        {"id": "trabalhador", "nome": "Camponês (Riqueza 4)", "riqueza": 4, "dinheiro": 30, "beneficio": 0,
         "ajuste_de_pontos": 1,
         "descricao": "Sai da aldeia com pouco mais que a roupa do corpo. Riqueza abaixo da média devolve 1 PP."},
        {"id": "classe_media", "nome": "Aventureiro (Riqueza 8)", "riqueza": 8, "dinheiro": 150, "beneficio": 0,
         "ajuste_de_pontos": 0, "descricao": "Padrão: dá para o kit inicial das classes do Livro do Jogador (o guerreiro já começa de cota de malha)."},
        {"id": "em_ascensao", "nome": "Burguês (Benefício: Riqueza 1)", "riqueza": 12, "dinheiro": 400,
         "beneficio": 1, "ajuste_de_pontos": 0, "descricao": "Custa 1 PP. Família de comerciantes ou artesãos."},
        {"id": "prospero", "nome": "Mercador próspero (Benefício: Riqueza 2)", "riqueza": 16, "dinheiro": 1600,
         "beneficio": 2, "ajuste_de_pontos": 0, "descricao": "Custa 2 PP. Dá para comprar uma armadura de placas."},
        {"id": "rico", "nome": "Nobre menor (Benefício: Riqueza 4)", "riqueza": 24, "dinheiro": 6000, "beneficio": 4,
         "ajuste_de_pontos": 0, "descricao": "Custa 4 PP. Filho de um barão, com terras e servos."},
        {"id": "muito_rico", "nome": "Grande nobre (Benefício: Riqueza 6)", "riqueza": 32, "dinheiro": 30000,
         "beneficio": 6, "ajuste_de_pontos": 0, "descricao": "Custa 6 PP. Herdeiro de um ducado."},
    ],
    "racas": RACAS,
    "arquetipos": CLASSES,
})
print("Arquivos básicos da fantasia gravados em", PASTA)
