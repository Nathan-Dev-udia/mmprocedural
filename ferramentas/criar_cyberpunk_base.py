"""Gera os arquivos básicos do gênero cyberpunk: gênero, equipamento, implantes, nomes e complicações.

Uso: python ferramentas/criar_cyberpunk_base.py
Os valores de equipamento vêm do livro básico (cap. 7); os implantes apontam para o catálogo
extraído do Perfis de Poder (o custo é o do livro).

ATENÇÃO: este script recria genero.json, equipment.json e powers.json do zero. Os arquivos atuais já
foram ajustados à mão depois (dinheiro em eurobucks, prioridades e perícias do gênero) e receberam os
preços do Cyberpunk RED. Se rodar de novo, rode em seguida `python ferramentas/precos_cyberpunk_red.py`
e confira o genero.json.
"""

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "dados" / "generos" / "cyberpunk"
PASTA.mkdir(parents=True, exist_ok=True)


def gravar(nome, conteudo):
    (PASTA / nome).write_text(json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


gravar("genero.json", {
    "id": "cyberpunk",
    "nome": "Cyberpunk",
    "descricao": "Futuro próximo: megacorporações, gangues de rua, netrunners e corpos cheios de implantes.",
    "perfis_de_poder": ["Blindados", "Tecnológicos", "Sensoriais", "Elétricos", "Velozes", "Fortes"],
    "configuracoes": {"rotulo_poderes": "Implantes", "equipamento": "pontos"},
})

F = "Livro básico, cap. 7"
G = F + ": itens de equipamento geral são uma Característica de 1 graduação (1 ponto)"


def arma(id_, nome, cat, custo, tipo, efeito, pericia=None, critico=20, multi=False, efeito_nome=None,
         resistido=None, forca=False, notas="", fonte=F):
    ataque = {"tipo": tipo, "efeito": efeito, "critico": critico}
    if pericia:
        ataque["pericia"] = pericia
    if multi:
        ataque["multiataque"] = True
    if efeito_nome:
        ataque["efeito_nome"] = efeito_nome
    if resistido:
        ataque["resistido_por"] = resistido
    if forca:
        ataque["soma_forca"] = True
    return {"id": id_, "nome": nome, "categoria": cat, "custo": custo, "preco": None, "notas": notas,
            "ataque": ataque, "fonte": fonte}


def item(id_, nome, cat, custo=1, descricao="", fonte=G, **extra):
    dados = {"id": id_, "nome": nome, "categoria": cat, "custo": custo, "preco": None, "descricao": descricao,
             "fonte": fonte}
    dados.update(extra)
    return dados


P, SM, FZ = "Combate à Distância: Pistolas", "Combate à Distância: Submetralhadoras", "Combate à Distância: Fuzis"
ES, EN, PE = "Combate à Distância: Escopetas", "Combate à Distância: Armas de energia", "Combate à Distância: Armas pesadas"

gravar("equipment.json", [
    arma("pistola_apoio", "Pistola de bolso", "Arma de fogo", 4, "distancia", 2, P, notas="Fácil de esconder"),
    arma("pistola_leve", "Pistola leve", "Arma de fogo", 6, "distancia", 3, P),
    arma("pistola_pesada", "Pistola pesada", "Arma de fogo", 8, "distancia", 4, P),
    arma("submetralhadora", "Submetralhadora", "Arma de fogo", 12, "distancia", 4, SM, multi=True),
    arma("fuzil_assalto", "Fuzil de assalto", "Arma de fogo", 15, "distancia", 5, FZ, multi=True),
    arma("fuzil_precisao", "Fuzil de precisão", "Arma de fogo", 11, "distancia", 5, FZ, critico=19,
         notas="Com mira telescópica"),
    arma("escopeta", "Escopeta", "Arma de fogo", 10, "distancia", 5, ES,
         notas="Chumbo: +2 no ataque, Dano máximo 3 contra Proteção"),
    arma("pistola_energia", "Pistola de energia", "Arma de energia", 10, "distancia", 5, EN),
    arma("fuzil_energia", "Fuzil de energia", "Arma de energia", 16, "distancia", 8, EN),
    arma("pistola_taser", "Pistola taser", "Arma de energia", 10, "distancia", 5, P, efeito_nome="Aflição",
         resistido="Fortitude", notas="Tonto, atordoado, incapacitado"),
    arma("metralhadora", "Metralhadora", "Arma pesada", 18, "distancia", 6, PE, multi=True),
    arma("lanca_granadas", "Lança-granadas", "Arma pesada", 15, "area", 5, notas="Granadas de fragmentação"),
    arma("granada_fragmentacao", "Granada de fragmentação", "Explosivo", 15, "area", 5),
    arma("granada_atordoante", "Granada atordoante (flash-bang)", "Explosivo", 16, "area", 4, efeito_nome="Pasmar",
         resistido="Fortitude", notas="Cega e ensurdece"),
    arma("explosivo_plastico", "Explosivo plástico (0,5 kg)", "Explosivo", 30, "area", 10),
    arma("faca", "Faca", "Arma branca", 2, "corpo", 1, "Combate Corpo-a-Corpo: Facas", critico=19, forca=True),
    arma("laminas_retrateis", "Lâminas retráteis (implante)", "Arma branca", 3, "corpo", 1,
         "Combate Corpo-a-Corpo: Facas", critico=19, forca=True, notas="Escondidas no antebraço (Sutil)",
         fonte="Livro básico: faca (Dano 1, crítico 19–20, 2 pontos) + Sutil (1 ponto)"),
    arma("katana", "Katana", "Arma branca", 4, "corpo", 3, "Combate Corpo-a-Corpo: Lâminas", critico=19,
         forca=True, fonte=F + " (espada)"),
    arma("tonfa", "Tonfa", "Arma branca", 2, "corpo", 2, "Combate Corpo-a-Corpo: Porretes", forca=True,
         fonte=F + " (porrete)"),
    arma("soqueira", "Soqueira", "Arma branca", 1, "corpo", 1, "Combate Corpo-a-Corpo: Briga", forca=True),
    arma("bastao_choque", "Bastão de choque", "Arma branca", 5, "corpo", 5, "Combate Corpo-a-Corpo: Porretes",
         efeito_nome="Aflição", resistido="Fortitude", fonte=F + " (taser de contato)",
         notas="Tonto, atordoado, incapacitado"),
    item("jaqueta_couro", "Jaqueta de couro", "Armadura", 1, "Proteção 1.", F, protecao=1),
    item("colete_oculto", "Colete oculto", "Armadura", 2,
         "Proteção 2 contra ataques balísticos; invisível sob a roupa (Sutil).", F, protecao=2,
         limitada_a="balísticos"),
    item("colete_balistico", "Colete à prova de balas", "Armadura", 2, "Proteção 4 contra ataques balísticos.", F,
         protecao=4, limitada_a="balísticos"),
    item("armadura_tatica", "Armadura corporal militar", "Armadura", 2, "Proteção 3 contra ataques balísticos.",
         "Livro básico p. 210 (armadura do Soldado, +3) como Proteção Limitada: 3 graduações a meio ponto = 2 pontos",
         protecao=3, limitada_a="balísticos"),
    item("celular", "Celular", "Eletrônicos", 1, "Telefone com bateria de um dia."),
    item("smartphone", "Smartphone", "Eletrônicos", 2, "Celular com as capacidades de um computador portátil."),
    item("comunicador", "Comunicador", "Eletrônicos", 1, "Rádio do tamanho de um botão, cerca de 1 km."),
    item("computador", "Cyberdeck (computador portátil)", "Eletrônicos", 1,
         "Computador para usar Tecnologia e invadir sistemas."),
    item("gravador", "Gravador de áudio", "Eletrônicos", 1, "Até oito horas de gravação."),
    item("camera", "Câmera", "Eletrônicos", 1, "Câmera fotográfica digital."),
    item("binoculos", "Binóculos", "Vigilância", 1, "+5 em Percepção visual à distância."),
    item("oculos_visao_noturna", "Óculos de visão noturna", "Vigilância", 1, "Visão no escuro, com –2 em Percepção."),
    item("microfone_parabolico", "Microfone parabólico", "Vigilância", 1, "+5 em Percepção para ouvir à distância."),
    item("rastreador", "Mini-rastreador", "Vigilância", 1,
         "Transmissor de cerca de 3 km; plantar exige ataque ou Prestidigitação."),
    item("gazua_automatica", "Gazua automática", "Equipamento geral", 1,
         "Abre trancas mecânicas comuns como teste de rotina."),
    item("algemas", "Algemas", "Equipamento geral", 1, "Resistência 9; escapar exige Prestidigitação CD 20."),
    item("mascara_gas", "Máscara de gás", "Equipamento geral", 1, "Imunidade a gases irritantes por 12 horas."),
    item("multiferramenta", "Multiferramenta", "Equipamento geral", 1,
         "Reduz para –2 a penalidade de perícias sem a ferramenta certa."),
    item("kit_medico", "Kit de primeiros socorros", "Equipamento geral", 1,
         "Ferramentas para usar Tratamento sem a penalidade de –5."),
    item("lanterna", "Lanterna", "Equipamento geral", 1, "Anula a penalidade de escuridão num cone de 9 m."),
    item("gps", "GPS", "Equipamento geral", 1, "+5 em testes de navegação."),
])


def implante(id_, nome, cat, catalogo, descricao, graduacao=None, tags=(), **extras):
    dados = {"id": id_, "nome": nome, "categoria": cat, "catalogo": catalogo, "descricao": descricao,
             "tags": list(tags)}
    if graduacao:
        dados["graduacao"] = graduacao
    dados.update(extras)
    return dados


gravar("powers.json", [
    implante("blindagem_subdermica", "Blindagem subdérmica", "defensivo", "blindados__armadura",
             "Placas finas sob a pele. Proteção 2.", 2, ["defesa"]),
    implante("placas_dermicas", "Placas dérmicas", "defensivo", "blindados__armadura",
             "Placas visíveis de liga metálica. Proteção 4.", 4, ["defesa"]),
    implante("braco_cibernetico", "Braço cibernético", "utilitario", "blindados__servo_motores",
             "Servo-motores no lugar dos músculos. +2 Força.", 2, ["forca", "combate"]),
    implante("olhos_ciberneticos", "Olhos cibernéticos", "utilitario", "blindados__sensores",
             "Zoom, visão noturna e infravermelho (3 graduações de Sentidos).", 3, ["percepcao"]),
    implante("audicao_amplificada", "Audição amplificada", "utilitario", "sensoriais__sonar_6",
             "Ouvidos sintéticos: audição acurada e ultra-audição.", None, ["percepcao"]),
    implante("radar_subcutaneo", "Radar subcutâneo", "utilitario", "sensoriais__radio_5",
             "Percebe tudo ao redor, inclusive pelas costas.", None, ["percepcao"]),
    implante("scanner_raio_x", "Scanner de raio X", "utilitario", "sensoriais__visao_de_raio_x_7",
             "Vê através de paredes e roupas.", None, ["percepcao"]),
    implante("alerta_de_combate", "Alerta de combate", "defensivo", "sensoriais__sentido_de_perigo",
             "Software que avisa de ameaças antes de você perceber.", None, ["percepcao", "defesa"]),
    implante("interface_neural", "Interface neural", "utilitario", "tecnologicos__interface",
             "Conecta o cérebro direto às máquinas: entende e conversa com qualquer sistema.", None, ["tecnologia"]),
    implante("radio_implantado", "Rádio implantado", "utilitario", "blindados__sistema_de_comunicacao",
             "Comunicação por rádio direto do crânio.", 1, ["tecnologia"]),
    implante("acesso_a_cameras", "Acesso a câmeras", "utilitario", "tecnologicos__rede_de_sensores",
             "Vê e ouve pelas câmeras e microfones da rede (4 graduações).", 4, ["tecnologia", "percepcao"]),
    implante("reflexos_turbinados", "Reflexos turbinados", "defensivo", "velozes__defesa_rapida",
             "Nervos sintéticos: +2 de Esquiva e de Aparar.", 2, ["defesa", "combate"],
             # Defesa Rápida: 1 PP por graduação de uma defesa, 2 PP por graduação das duas.
             custo_por_graduacao=2,
             _custo="Defesa Rápida: 2 PP por graduação quando aumenta Esquiva e Aparar juntas (Perfis de Poder)."),
    implante("nanorreparo", "Nanorreparo", "defensivo", "velozes__cura_acelerada",
             "Nanorrobôs que fecham ferimentos (Regeneração 2).", 2, ["defesa"]),
    implante("pernas_hidraulicas", "Pernas hidráulicas", "movimento", "blindados__pernas_hidraulicas",
             "Pistões nas pernas para saltos enormes (Salto 2).", 2, ["movimento"]),
    implante("firewall_cortical", "Firewall cortical", "defensivo", "blindados__escudo_mental",
             "Protege a mente de invasões: +2 de Vontade contra efeitos mentais.", 2, ["defesa", "tecnologia"]),
    implante("filtros_sinteticos", "Pulmões e filtros sintéticos", "defensivo", "blindados__sistema_de_suporte_vital",
             "Respira em qualquer ambiente e resiste a toxinas (Imunidade 10).", None, ["defesa"]),
    implante("camuflagem_optica", "Camuflagem óptica", "defensivo", "sensoriais__invisibilidade",
             "Revestimento que dobra a luz: invisível à visão normal.", None, ["furtividade"]),
    implante("braco_canhao", "Braço-canhão", "ofensivo", "blindados__canhoes",
             "Canhão que sai do antebraço (Dano 5 à distância).", 5, ["combate"]),
    implante("metralhadora_embutida", "Metralhadora embutida", "ofensivo", "blindados__metralhadora",
             "Metralhadora no ombro (Dano 4 à distância, Multiataque).", 4, ["combate"]),
    implante("taser_implantado", "Taser implantado", "ofensivo", "eletricos__teaser",
             "Dardos elétricos disparados do pulso (Aflição 5: tonto, atordoado, incapacitado).", 5,
             ["combate", "controle"]),
    implante("pulso_eletromagnetico", "Pulso eletromagnético", "ofensivo", "eletricos__pem",
             "Descarga que frita eletrônicos ao redor (Enfraquecer 4 em área, só objetos).", 4,
             ["tecnologia", "combate"]),
])

gravar("names.json", {"humano": {
    "nomes": ["Kenji", "Mara", "Rex", "Nova", "Dex", "Yuki", "Ivo", "Zara", "Tomás", "Aiko", "Léo", "Raj",
              "Sasha", "Ingrid", "Malik", "Luana", "Chen", "Ada", "Bruno", "Kofi", "Vera", "Hiro", "Noor", "Otto"],
    "sobrenomes": ["Tanaka", "Okafor", "Silva", "Volkov", "Reyes", "Kim", "Novak", "Haddad", "Ferreira", "Ishikawa",
                   "Mbeki", "Larsen", "Castillo", "Zhou", "Petrov", "Moreau", "Adeyemi", "Sato"],
    "apelidos": ["Cromo", "Neon", "Glitch", "Zero", "Ferrugem", "Cascavel", "Fantasma", "Byte", "Faísca", "Viúva",
                 "Sucata", "Nove-Vidas", "Estática", "Bala", "Circuito", "Lâmina"]}})

gravar("complications.json", {
    "_fonte": "Livro básico, cap. 2 (complicações), com exemplos de cyberpunk",
    "motivacoes": [
        {"nome": "Cobiça", "exemplo": "Créditos, implantes melhores, um apartamento acima da poluição."},
        {"nome": "Justiça", "exemplo": "Derrubar a corporação que destruiu sua vida."},
        {"nome": "Vingança", "exemplo": "Acertar as contas com quem o deixou para morrer num beco."},
        {"nome": "Adrenalina", "exemplo": "A emoção do próximo trabalho perigoso."},
        {"nome": "Reconhecimento", "exemplo": "Virar lenda nas ruas e nos fóruns da rede."},
        {"nome": "Responsabilidade", "exemplo": "A família, a gangue ou o bairro que depende de você."},
        {"nome": "Fazer o Bem", "exemplo": "Proteger quem a cidade esqueceu."},
        {"nome": "Aceitação", "exemplo": "Provar que ainda é humano, apesar de tanto metal."},
        {"nome": "Patriotismo", "exemplo": "Lealdade à corporação, à nação ou ao clã."},
    ],
    "complicacoes": [
        {"nome": "Inimigo", "exemplo": "Uma corporação quer você morto ou de volta ao laboratório."},
        {"nome": "Responsabilidade", "exemplo": "Uma dívida enorme com o médico que instalou seus implantes."},
        {"nome": "Vício", "exemplo": "Drogas de combate, realidade virtual, adrenalina."},
        {"nome": "Segredo", "exemplo": "Seu corpo é propriedade de uma corporação, e você fugiu com ele."},
        {"nome": "Perda de Poder", "exemplo": "Implantes que falham com pulsos eletromagnéticos ou sem manutenção."},
        {"nome": "Reputação", "exemplo": "Conhecido por trair contratantes."},
        {"nome": "Rivalidade", "exemplo": "Outro netrunner ou mercenário que quer superá-lo."},
        {"nome": "Relacionamento", "exemplo": "Um irmão mais novo metido com uma gangue."},
        {"nome": "Honra", "exemplo": "Nunca abandona um parceiro nem quebra um contrato."},
        {"nome": "Obsessão", "exemplo": "Encontrar a IA que apagou suas memórias."},
        {"nome": "Ódio", "exemplo": "Odeia executivos de corporação."},
        {"nome": "Fobia", "exemplo": "Pânico de perder a conexão com a rede."},
        {"nome": "Irritação", "exemplo": "Perde a cabeça quando chamam você de máquina."},
        {"nome": "Peculiaridade", "exemplo": "Grava tudo o que vê; nunca desliga os olhos cibernéticos."},
        {"nome": "Deficiência", "exemplo": "Um implante rejeitado deixou uma mão sem sensibilidade."},
        {"nome": "Preconceito", "exemplo": "Pessoas sem implantes desconfiam de ciborgues como você."},
        {"nome": "Fama", "exemplo": "Seu rosto está em todos os noticiários depois do último trabalho."},
    ],
})
print("Arquivos básicos do cyberpunk gravados em", PASTA)
