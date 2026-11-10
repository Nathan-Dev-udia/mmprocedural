"""Gera o arquivo dados/escudo/cthulhu.json para o Escudo do Mestre de Chamado de Cthulhu.

As regras gerais de M&M (ações, manobras, condições, dano, tratamento) vêm de ferramentas/escudo_mm.py; os textos de Sanidade (acessos de loucura, estados de
loucura e recuperação) vêm de nucleo/sanidade.py, a mesma fonte da página de Sanidade do PDF da ficha.

Uso: python ferramentas/criar_cthulhu_escudo.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from nucleo import sanidade  # noqa: E402

sys.path.insert(0, str(RAIZ / "ferramentas"))
import escudo_mm as mm  # noqa: E402

DESTINO = RAIZ / "dados" / "escudo" / "cthulhu.json"

# ---------------------------------------------------------------- Testes

TESTES = {
    "id": "testes",
    "nome": "Testes",
    "blocos": [
        {
            "tipo": "formulas",
            "titulo": "Fórmulas",
            "itens": [
                "**Teste** = d20 + graduação + modificadores, contra a CD",
                "**Rotina** = 10 + graduação (sem pressão; só com treino na perícia)",
                "**Ataque** = d20 + bônus de ataque, contra defesa + 10 (Aparar corpo a corpo, Esquiva à distância)",
                "**Salvamento contra efeito** = d20 + defesa, contra 10 + graduação",
                "**Salvamento contra dano** = d20 + Resistência, contra 15 + Dano",
                "**Teste de Sanidade** = d100 contra a SAN atual; tirar igual ou menor é sucesso (veja a aba Sanidade)",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Classes de dificuldade",
            "colunas": ["CD", "Dificuldade", "Exemplo nos anos 1920"],
            "linhas": [
                ["0", "Muito fácil", "Achar o endereço de um hotel na lista telefônica"],
                ["5", "Fácil", "Encontrar um jornal da semana passada na biblioteca municipal de Arkham"],
                ["10", "Médio", "Notar pegadas de lama recentes no assoalho da cena do crime"],
                ["15", "Difícil", "Abrir sem ruído a fechadura de um cofre antigo durante a noite"],
                ["20", "Desafiador", "Identificar um dialeto arcaico gravado em tábuas de pedra pré-humanas"],
                ["25", "Formidável", "Despistar cultistas a pé pelas vielas de Innsmouth sob a névoa"],
                ["30", "Heroico", "Convencer o delegado de que o assassino não era humano, sem provas"],
                ["35", "Super-heroico", "Decifrar sozinho, numa noite, um capítulo inteiro dos Manuscritos Pnakóticos"],
                ["40", "Quase impossível", "—"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Graus de sucesso e de falha",
            "nota": "20 natural: o resultado sobe um grau. Em ataques, 20 sempre acerta e 1 sempre erra.",
            "colunas": ["Resultado", "Grau"],
            "linhas": [
                ["CD + 15 ou mais", "4 graus de sucesso"],
                ["CD + 10 a + 14", "3 graus de sucesso"],
                ["CD + 5 a + 9", "2 graus de sucesso"],
                ["CD a CD + 4", "1 grau de sucesso"],
                ["CD – 1 a CD – 5", "1 grau de falha"],
                ["CD – 6 a CD – 10", "2 graus de falha"],
                ["CD – 11 a CD – 15", "3 graus de falha"],
                ["CD – 16 ou menos", "4 graus de falha"],
            ],
        },
        {
            "tipo": "lista",
            "titulo": "Perícias investigativas",
            "itens": [
                "**Investigação:** buscar pistas, impressões digitais, gavetas de fundo falso e papéis queimados.",
                "**Percepção:** notar cheiro de enxofre ou de peixe podre, sussurros no sótão, vultos nas janelas.",
                "**Intuição:** perceber se a testemunha mente, está aterrorizada ou sob transe hipnótico.",
                "**Tratamento (medicina legal):** autópsia preliminar; distinguir cortes de faca de mordidas não humanas.",
                "**Especialidade: Ocultismo:** reconhecer símbolos de cultos, grimórios apócrifos e círculos rituais.",
                "**Especialidade: Mythos de Cthulhu:** conhecimento proibido; cada graduação baixa 5 pontos da SAN máxima.",
                "**Especialidade: História / Antiguidades:** decifrar crônicas coloniais, genealogias e estatuetas antigas.",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Testes opostos",
            "nota": "Os dois lados rolam e vence o maior total. Empate: vence quem tem o maior bônus.",
            "colunas": ["Situação", "Quem age", "Quem resiste"],
            "linhas": [
                ["Esgueirar-se pelo porão do templo do culto", "Furtividade", "Percepção"],
                ["Mentir para o delegado sobre a noite do crime", "Enganação", "Intuição"],
                ["Disfarçar-se de operário do cais", "Enganação", "Percepção"],
                ["Bater carteira na estação de trem", "Prestidigitação", "Percepção"],
                ["Seguir um suspeito pelas ruas sem ser notado", "Furtividade", "Percepção"],
                ["Intimidar um informante a falar", "Intimidação", "Vontade"],
                ["Fintar numa briga de rua", "Enganação", "Enganação ou Intuição"],
                ["Escapar de um cultista que agarra", "Acrobacia ou Atletismo", "Força de quem agarra"],
                ["Esconder um revólver sob o sobretudo", "Prestidigitação", "Percepção"],
            ],
        },
        {
            "tipo": "lista",
            "titulo": "Modificadores e ajuda",
            "itens": [
                "**Circunstância:** +2 ou –2 para uma pequena vantagem ou desvantagem; +5 ou –5 para uma grande.",
                "**Ferramentas:** sem a ferramenta certa (gazuas, maleta médica, reagentes), –5; improvisada, –2.",
                "**Teste de equipe:** os ajudantes fazem o mesmo teste contra CD 10. Um grau de sucesso dá +2 ao "
                "líder; três graus ou mais, +5; dois graus de falha, –2.",
                "**Pesquisa em arquivo:** horas de leitura viram teste de rotina; com pressa, role contra a CD.",
            ],
        },
        mm.esforco_extra("uma arma ou um automóvel"),
        mm.PONTOS_HEROICOS,
    ],
}

# ---------------------------------------------------------------- Combate

COMBATE = {
    "id": "combate",
    "nome": "Combate",
    "blocos": [
        mm.acoes([
            ["Recarregar", "Movimento", "Troca o pente da pistola ou o tambor da Thompson. Revólver bala a bala: "
                                        "padrão [Casa]."],
            ["Dirigir", "Movimento", "Conduz o automóvel até a Velocidade dele; manobras difíceis pedem Veículos."],
        ], comandar="um capanga ou cão treinado"),
        mm.manobras("de automóvel, por exemplo", extras=[
            ["Multiataque (Thompson)", "Alvo único: +2 no dano com dois graus de sucesso no ataque, +5 com três. "
                                       "Vários alvos: um ataque contra cada, com penalidade igual ao número de alvos."],
        ]),
        {
            "tipo": "tabela",
            "titulo": "Alcance",
            "nota": "Pistola .32 (Dano 2): 15 m sem penalidade, 60 m no máximo. Revólver .38 (Dano 3): 22,5 m e 90 m. "
                    "Colt .45 M1911 e Thompson (Dano 4): 30 m e 120 m. Springfield .30-06 e escopeta (Dano 5): "
                    "37,5 m e 150 m.",
            "colunas": ["Alcance", "Distância", "Ataque"],
            "linhas": [
                ["Curto", "graduação de dano × 7,5 m", "sem penalidade"],
                ["Médio", "graduação de dano × 15 m", "–2"],
                ["Longo", "graduação de dano × 30 m", "–5"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Camuflagem e cobertura",
            "nota": "A cobertura dá o mesmo valor como bônus na Esquiva contra explosões (atrás de um muro de "
                    "alvenaria, +5 contra a dinamite).",
            "colunas": ["Situação", "Ataque", "Exemplos"],
            "linhas": [
                ["Camuflagem parcial", "–2", "Névoa do porto, fumaça de pólvora, penumbra de um porão"],
                ["Camuflagem total", "–5", "Escuridão total, cripta sem luz, nevoeiro fechado"],
                ["Cobertura parcial", "–2", "Poste, caixote, mesa virada, porta do automóvel"],
                ["Cobertura total", "–5", "Muro de alvenaria, bloco do motor, coluna de pedra"],
            ],
        },
        {
            "tipo": "lista",
            "titulo": "Iniciativa, surpresa e capangas",
            "itens": [
                "**Iniciativa:** d20 + Agilidade + 4 por graduação de Iniciativa Aprimorada. Empate: Esquiva, depois "
                "Agilidade, depois Prontidão.",
                "**Surpresa:** quem é pego de surpresa (emboscada no beco) fica atordoado e vulnerável na rodada de surpresa.",
                "**Capangas:** cultistas comuns e capangas da máfia não fazem acertos críticos contra os investigadores; "
                "qualquer falha num salvamento aplica o pior grau do efeito.",
                "**Armas de área:** a dinamite pede Esquiva CD 10 + graduação; quem passa sofre metade do efeito.",
            ],
        },
    ],
}

# ---------------------------------------------------------------- Condições

CONDICOES = {
    "id": "condicoes",
    "nome": "Condições e graus",
    "blocos": [
        {"tipo": "gerado", "fonte": "aflicao"},
        {"tipo": "gerado", "fonte": "dano"},
        mm.condicoes_basicas("Ações ditadas pela fonte (hipnose, feitiço, a vontade de um Mythos)."),
        mm.CONDICOES_COMBINADAS,
        {"tipo": "gerado", "fonte": "recuperacao"},
        mm.tratamento("maleta médica", extras=[
            ["Acalmar acesso de loucura", "15", "Encerra o acesso de loucura (com Especialidade: Psicologia)."],
        ]),
    ],
}

# ---------------------------------------------------------------- Sanidade

SANIDADE = {
    "id": "sanidade",
    "nome": "Sanidade & Horror",
    "blocos": [
        {
            "tipo": "formulas",
            "titulo": "Fórmulas de Sanidade",
            "itens": [
                "**SAN inicial** = 45 + 5 × Vontade (no máximo 99, e nunca acima da SAN máxima)",
                "**SAN máxima** = 99 – 5 × graduação em Especialidade: Mythos de Cthulhu",
                "**Teste de Sanidade** = d100 contra a SAN atual: igual ou menor é sucesso; maior é falha",
                "**01:** sempre sucesso (sofre a perda normal do sucesso)",
                "**100:** sempre desastre (sofre a perda máxima da falha); com SAN abaixo de 50, de 96 a 100",
                "**Perda de 5 ou mais num teste:** Intelecto d20 + INT contra CD 10. Sucesso: entende o que viu e "
                "entra em insanidade temporária. Falha: a mente reprime o choque e segue em frente",
                "**Ponto de ruptura** = 1/5 da SAN do início do dia, arredondado para cima: perder isso ou mais no "
                "mesmo dia causa insanidade indefinida",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Perda típica de Sanidade",
            "colunas": ["Encontro ou descoberta", "Sucesso", "Falha", "Perda máx. (acostumar-se)"],
            "linhas": [
                ["Encontrar um cadáver comum", "0", "1D3", "—"],
                ["Encontrar um cadáver humano mutilado", "1", "1D4+1", "—"],
                ["Presenciar ritual com sacrifício humano", "0", "1D6", "—"],
                ["Descobrir que um parente ou amigo é um monstro", "1", "1D10", "—"],
                ["Carniçal ou Profundo", "0", "1D6", "6"],
                ["Mi-Go (fungo de Yuggoth)", "0", "1D6", "6"],
                ["Criatura insubstancial / poltergeist", "1", "1D8", "8"],
                ["Shoggoth ou Cria Estelar de Cthulhu", "1D6", "1D20", "20"],
                ["Avatar de Nyarlathotep ou o próprio Cthulhu", "1D10", "1D100", "100"],
            ],
            "nota": "Acostumar-se: some tudo o que o investigador já perdeu por um tipo de criatura; quando a soma "
                    "chega à perda máxima da falha, ele não perde mais SAN por aquele tipo. Eventos (—) sempre custam SAN.",
        },
        {
            "tipo": "tabela",
            "titulo": "Estados de loucura",
            "colunas": ["Estado", "Gatilho", "Duração e efeito"],
            "linhas": [list(e) for e in sanidade.ESTADOS_DE_LOUCURA],
        },
        {
            "tipo": "tabela",
            "titulo": "Acessos de loucura (d10)",
            "colunas": ["d10", "Acesso", "Efeito na mesa"],
            "linhas": [[str(d), nome, efeito] for d, nome, efeito in sanidade.ACESSOS_DE_LOUCURA],
            "nota": f"Duração: {sanidade.DURACAO_DO_ACESSO}.",
        },
        {
            "tipo": "lista",
            "titulo": "Recuperação de Sanidade",
            "itens": list(sanidade.RECUPERACAO_DE_SANIDADE),
        },
    ],
}

# ---------------------------------------------------------------- Viagem

VIAGEM = {
    "id": "viagem",
    "nome": "Viagem",
    "blocos": [
        {
            "tipo": "formulas",
            "titulo": "Fórmulas",
            "itens": [
                "**Tempo** = graduação de distância – graduação de Velocidade",
                "**Distância** = graduação de Velocidade + graduação de tempo",
                "**Ritmo normal a pé:** 5 km/h, cerca de 38 km num dia de 8 horas de caminhada.",
                "**Trem:** $1,50 por 50 km (ou fração); o expresso viaja a cerca de 60 km/h com as paradas.",
            ],
        },
        {"tipo": "gerado", "fonte": "tempo_de_viagem"},
        {"tipo": "gerado", "fonte": "montarias"},
        {"tipo": "gerado", "fonte": "carga"},
        {
            "tipo": "tabela",
            "titulo": "Trechos na Nova Inglaterra (anos 1920)",
            "colunas": ["Trecho", "Transporte", "Tempo", "Custo"],
            "linhas": [
                ["Boston a Arkham (~40 km)", "Trem de passageiros", "1 hora", "$1,50"],
                ["Arkham a Innsmouth", "Ônibus decrépito de Joe Sargent", "1 hora", "$0,75"],
                ["Arkham a Kingsport", "Bonde interurbano", "45 minutos", "$0,25"],
                ["Arkham a Dunwich", "Automóvel por estrada de terra", "3 horas", "$0,40 (gasolina)"],
                ["Boston a Nova York (~350 km)", "Trem expresso interestadual", "6 horas", "$10,50"],
                ["Nova York a Liverpool", "Transatlântico a vapor (classe turística)", "6 a 7 dias", "$100,00"],
            ],
            "nota": "Gasolina: cerca de $0,20 o galão (3,8 litros); um Ford T faz uns 8 km por litro.",
        },
    ],
}

# ---------------------------------------------------------------- Perigos

PERIGOS = {
    "id": "perigos",
    "nome": "Perigos",
    "blocos": [
        {"tipo": "gerado", "fonte": "queda"},
        {
            "tipo": "lista",
            "titulo": "Afogamento, venenos e doenças",
            "itens": [
                "**Afogamento:** prende a respiração por 10 rodadas + 2 × Vigor. Depois, Fortitude CD 10 (+1 por "
                "teste) a cada rodada; uma falha deixa incapacitado; na rodada seguinte, moribundo.",
                "**Arsênico ou estricnina:** Enfraquecer Vigor graduação 6 (Fortitude CD 16).",
                "**Clorofórmio no lenço:** Aflição graduação 4 (Fortitude CD 14: tonto, atordoado, inconsciente).",
                "**Doenças da época:** gripe espanhola (Fortitude CD 15), tuberculose (CD 16), tifo (CD 15).",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Calor e frio",
            "nota": "Espiral de Fortitude: CD 10, +1 por teste. Cada falha: fatigado → exausto → incapacitado → "
                    "moribundo. A vantagem Tolerância Maior dá +5.",
            "colunas": ["Exposição", "Exemplo", "Teste de Fortitude"],
            "linhas": [
                ["Desconfortável", "Noite de outono na mata de Dunwich, sótão abafado no verão", "1 por hora"],
                ["Intensa", "Nevasca na Nova Inglaterra, sala de caldeiras de um navio", "A cada 10 minutos"],
                ["Extrema", "Platô antártico, prédio em chamas, água gelada do Atlântico Norte", "A cada minuto"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Fogo e explosivos",
            "colunas": ["Perigo", "Dano", "Resistência", "Efeito adicional"],
            "linhas": [
                ["Tocha ou vela", "Dano 1 por rodada", "CD 16", "Pode inflamar roupas de algodão"],
                ["Fogueira ou fornalha", "Dano 2 por rodada", "CD 17", "As roupas pegam fogo"],
                ["Prédio em chamas", "Dano 5 por rodada", "CD 20", "Fumaça: espiral de Fortitude a cada minuto"],
                ["Banana de dinamite", "Dano 5 em área", "CD 20", "Esquiva CD 15 para sofrer metade"],
                ["Caixa de dinamite (10 bananas)", "Dano 10 em área", "CD 25", "Esquiva CD 20; derruba paredes de cripta"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Armadilhas e perigos (exemplos no NP 4)",
            "nota": "Notar: Percepção CD 15 a 20. Desarmar: Tecnologia com ferramentas; falha por 2 graus dispara o perigo.",
            "colunas": ["Perigo", "Efeito", "Exemplo"],
            "linhas": [
                ["Assoalho podre da casa abandonada", "Queda de 4 m (Dano 2) no porão", "Percepção CD 15 para notar"],
                ["Dinamite ligada à porta da cripta", "Dano 5 em área (Esquiva CD 15 metade)", "Tecnologia CD 20 para desarmar"],
                ["Desabamento num túnel sob o cemitério", "Dano 6 em área e soterramento", "Esquiva CD 16 para escapar"],
                ["Porta que tranca sozinha numa sala que alaga", "Afogamento em 1D6 minutos", "Força CD 20 para arrombar"],
            ],
        },
        {
            "tipo": "lista",
            "titulo": "Escuridão e luz",
            "itens": [
                "**Farol de automóvel:** ilumina com luz clara cerca de 30 m à frente.",
                "**Lanterna elétrica:** ilumina com luz clara 9 m; as pilhas duram umas 4 horas [Casa].",
                "**Lampião de querosene:** luz clara num raio de 9 m e penumbra até 18 m.",
                "**Fósforo ou isqueiro:** luz fraca a 1,5 m; dá para ler uma página ou achar a fechadura.",
                "**Penumbra:** camuflagem parcial (–2 em ataques e testes visuais).",
                "**Escuridão total:** camuflagem total (–5 em ataques e testes visuais).",
            ],
        },
    ],
}

# ---------------------------------------------------------------- Objetos e medidas

OBJETOS = {
    "id": "objetos",
    "nome": "Objetos e medidas",
    "blocos": [
        {
            "tipo": "formulas",
            "titulo": "Fórmulas",
            "itens": [
                "**Arremesso:** distância = Força – massa do objeto",
                "**Quebrar um objeto:** dano do golpe ou tiro contra a Resistência do material",
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Resistência dos materiais",
            "nota": "Para alguns centímetros de espessura; +1 a cada vez que a espessura dobra. Cofre de banco: 10 ou mais.",
            "colunas": ["Material", "Resistência", "Exemplo"],
            "linhas": [
                ["Papel, lona, couro fino", "0", "Livro, cortina, capota de lona"],
                ["Vidro", "1", "Janela, vitrine, frasco de laboratório"],
                ["Madeira leve", "2", "Porta interna, caixote, estante"],
                ["Madeira pesada", "3 a 4", "Porta de carvalho, baú antigo, alçapão"],
                ["Tijolo", "5", "Parede de casa, chaminé"],
                ["Pedra e concreto", "6 a 7", "Parede de cripta, coluna, muro do cemitério"],
                ["Ferro", "8", "Grade da cela, portão do mausoléu, algemas"],
                ["Aço", "10", "Porta de cofre, casco de navio"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Tamanho",
            "nota": "Furtividade e Intimidação são circunstância. Esquiva, Aparar, Força e Vigor contam nos limites do NP.",
            "colunas": ["Tamanho", "Exemplos", "Furtividade", "Intimidação", "Esquiva e Aparar", "Força e Vigor"],
            "linhas": [
                ["Miúdo (–4, ~50 cm)", "Rato, gato, corvo", "+8", "–4", "+4", "Força –2"],
                ["Pequeno (–3, ~1 m)", "Cachorro, criança", "+4", "–2", "+2", "Força –1"],
                ["Médio (–2, ~2 m)", "Humano, carniçal, Profundo", "—", "—", "—", "—"],
                ["Grande (–1, ~4 m)", "Cavalo, automóvel", "–4", "+2", "–2", "+4 (For +2, Vig +2)"],
                ["Enorme (0, ~8 m)", "Shoggoth, caminhão", "–8", "+4", "–4", "+8"],
                ["Imenso (1, ~15 m)", "Locomotiva, Cria Estelar", "–12", "+6", "–6", "+12"],
            ],
        },
        {"tipo": "gerado", "fonte": "medidas"},
    ],
}

# ---------------------------------------------------------------- Cidade

CIDADE = {
    "id": "cidade",
    "nome": "Cidade & Serviços (anos 1920)",
    "blocos": [
        {
            "tipo": "tabela",
            "titulo": "Serviços e comunicações",
            "colunas": ["Serviço", "Custo", "Observações"],
            "linhas": [
                ["Telegrama Western Union", "$0,05 por palavra", "Entregue em poucas horas na cidade"],
                ["Telefonema interurbano", "$5,00 por 3 min", "A telefonista conecta a ligação à mão"],
                ["Carta (selo de 1ª classe)", "$0,02", "1 a 2 dias entre cidades do mesmo estado"],
                ["Entrega especial (carta urgente)", "$0,12", "Entregue no mesmo dia por mensageiro"],
                ["Diária em hotel de luxo (Boston)", "$8,00 a $12,00", "Quarto amplo, serviço de quarto e telefone"],
                ["Diária em hotel médio (Arkham)", "$2,50", "Cama confortável, banheiro no corredor"],
                ["Pensão barata", "$0,75 por noite", "Bairro operário de imigrantes; ninguém pergunta o nome"],
                ["Refeição completa em restaurante", "$0,50 a $1,00", "Café, bife e torta numa lanchonete de esquina"],
                ["Garrafa de uísque ilegal (speakeasy)", "$3,00 a $5,00", "Contrabando sob a Lei Seca"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Instituições e arquivos",
            "colunas": ["Local", "O que pesquisar", "Acesso"],
            "linhas": [
                ["Universidade Miskatonic", "Tomos raros, história colonial, química", "Credencial acadêmica ou Persuasão"],
                ["Redação do Arkham Advertiser", "Notícias antigas e obituários", "Contato na imprensa ou gorjeta ao arquivista"],
                ["Cartório de Arkham", "Escrituras de imóveis e testamentos", "Taxa de $0,50 por busca"],
                ["Necrotério de Boston", "Autópsias e laudos do legista", "Autoridade policial ou suborno de $2,00"],
                ["Hospital Estadual de Danvers", "Prontuários psiquiátricos e pacientes", "Ordem judicial ou visita médica"],
            ],
        },
        {
            "tipo": "tabela",
            "titulo": "Honorários e serviços profissionais",
            "colunas": ["Profissional", "Honorário", "Serviço"],
            "linhas": [
                ["Médico particular", "$3,00", "Visita em casa e receita de sedativos"],
                ["Sanatório particular", "$15,00 por dia", "Quarto reservado e vigilância médica"],
                ["Psicanalista", "$5,00 por sessão", "Tratamento de Sanidade (teste mensal)"],
                ["Detetive particular", "$10,00 por dia", "Vigilância discreta e campanas na cidade"],
                ["Advogado criminalista", "$50,00 a $200,00", "Fiança e defesa no tribunal"],
                ["Mecânico de automóveis", "$2,00 a $5,00", "Conserto de motor, troca de pneus e correias"],
            ],
        },
    ],
}

# Tabelas de dano, Aflição e recuperação: geradas por nucleo/escudo.py conforme a letalidade escolhida.
LETALIDADE = {
    "padrao": "equilibrada",
    "ataques_letais": "tiros, lâminas, garras e mordidas",
    "ataques_padrao": "socos, coronhadas, cassetetes",
    "aflicao_nota": "Os surtos de loucura não são Aflição: veja a aba Sanidade.",
    "cura": {"mortal": "**Recuperação [Casa]:** sem atendimento, 1 condição de dano por dia, da pior para a melhor. "
                       "Com Tratamento de longo prazo e repouso num hospital, 1 a cada 8 horas."},
}

escudo_cthulhu = {
    "_fonte": "Resumo das regras de Chamado de Cthulhu 7ª edição adaptadas para Mutantes & Malfeitores 3ª edição. "
              "Gerado por ferramentas/criar_cthulhu_escudo.py; os textos de Sanidade vêm de nucleo/sanidade.py e os "
              "blocos 'gerado' são calculados por nucleo/escudo.py.",
    "genero": "cthulhu",
    "titulo": "Escudo do Mestre: Chamado de Cthulhu",
    "letalidade": LETALIDADE,
    "abas": [TESTES, COMBATE, CONDICOES, SANIDADE, VIAGEM, PERIGOS, OBJETOS, CIDADE],
}

if __name__ == "__main__":
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps(escudo_cthulhu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gravado {DESTINO}")
