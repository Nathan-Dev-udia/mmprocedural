"""Gera os arquivos JSON do Bestiário de Chamado de Cthulhu."""

import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "dados" / "bestiario" / "cthulhu"

CRIATURAS = [
    {
        "pasta": "cultistas",
        "arquivo": "cultista_iniciado.json",
        "dados": {
            "id": "cthulhu/cultistas/cultista_iniciado",
            "genero": "cthulhu",
            "familia": "Cultista",
            "variante": "Iniciado",
            "padrao": True,
            "nome": "Cultista Iniciado",
            "tipo": "Humanoide",
            "subtipo": "Cultista",
            "papel": "Lacaio",
            "chefe": False,
            "tamanho": "Médio",
            "nivel_poder": 2,
            "ambientes": [
                "Celas e porões urbanos",
                "Templos abandonados",
                "Bosques e pântanos à meia-noite"
            ],
            "descricao": "Um devoto recém-admitido nas ordens secretas que adoram as divindades cósmicas. Veste túnicas rústicas com capuz para ocultar sua identidade de cidadão comum e carrega símbolos entalhados com geometrias não-euclidianas.",
            "tatica": "Ataca em bando para proteger os altares ou rituais. Dispara de longe com armas de calibre pequeno e avança com facas cerimoniais quando ordenado pelos sacerdotes.",
            "complicacoes": [
                "Fanatismo Cego: cumpre qualquer ordem blasfema dos líderes do culto sem questionar.",
                "Obsessão pelos Mythos: mente degradada por cânticos e vislumbres profanos."
            ],
            "fonte": "Chamado de Cthulhu (7ª Edição) & M&M 3e Supernatural Handbook",
            "ficha": {
                "habilidades": {
                    "For": 1,
                    "Vig": 1,
                    "Agi": 1,
                    "Des": 1,
                    "Lut": 1,
                    "Int": 0,
                    "Pro": 1,
                    "Pre": 0
                },
                "defesas": {
                    "Esquiva": 2,
                    "Aparar": 2,
                    "Fortitude": 2,
                    "Resistencia": 2,
                    "Vontade": 2
                },
                "pericias": {
                    "Furtividade": 3,
                    "Intimidação": 2,
                    "Percepção": 2,
                    "Especialidade: Ocultismo": 3,
                    "Combate à Distância: Armas de Fogo": 1,
                    "Combate Corpo-a-Corpo: Lâminas": 1
                },
                "vantagens": [
                    "Benefício (Membro do Culto)",
                    "Equipamento 2"
                ],
                "poderes": [],
                "ataques": [
                    {
                        "nome": "Adaga Ritual",
                        "bonus": 2,
                        "dano": 2,
                        "critico": 19,
                        "descricao": "Dano baseado em Força com lâmina cerimonial"
                    },
                    {
                        "nome": "Revólver .32",
                        "bonus": 2,
                        "dano": 2,
                        "critico": 20,
                        "descricao": "À distância, balístico"
                    }
                ],
                "equipamento": [
                    "Adaga ritual (Dano 1, Crítico 19-20)",
                    "Revólver .32 (Dano 2, À Distância)",
                    "Túnica cerimonial e amuleto estranho"
                ]
            }
        }
    },
    {
        "pasta": "cultistas",
        "arquivo": "cultista_fanatico.json",
        "dados": {
            "id": "cthulhu/cultistas/cultista_fanatico",
            "genero": "cthulhu",
            "familia": "Cultista",
            "variante": "Fanático",
            "padrao": False,
            "nome": "Cultista Fanático",
            "tipo": "Humanoide",
            "subtipo": "Cultista",
            "papel": "Bruto / Lacaio",
            "chefe": False,
            "tamanho": "Médio",
            "nivel_poder": 3,
            "ambientes": [
                "Círculos rituais externos",
                "Ruínas isoladas",
                "Casarões decadentes"
            ],
            "descricao": "Um crente fervoroso cuja psique já foi completamente consumida pela loucura cósmica. Ele não sente dor ordinária nem teme a morte, empunhando machados ou armas pesadas com frenesi assassino.",
            "tatica": "Avança cegamente em direção aos investigadores gritando nomes impronunciáveis, ignorando ferimentos leves para golpear de forma violenta e visceral.",
            "complicacoes": [
                "Fúria Incontrolável: quando o combate começa, não recua a menos que receba ordem direta do sacerdote.",
                "Mente Quebrada: sofre alucinações constantes das entidades do vácuo."
            ],
            "fonte": "Chamado de Cthulhu (7ª Edição) & M&M 3e Supernatural Handbook",
            "ficha": {
                "habilidades": {
                    "For": 2,
                    "Vig": 2,
                    "Agi": 1,
                    "Des": 1,
                    "Lut": 2,
                    "Int": -1,
                    "Pro": 1,
                    "Pre": 1
                },
                "defesas": {
                    "Esquiva": 3,
                    "Aparar": 3,
                    "Fortitude": 3,
                    "Resistencia": 3,
                    "Vontade": 3
                },
                "pericias": {
                    "Intimidação": 4,
                    "Atletismo": 3,
                    "Percepção": 2,
                    "Combate Corpo-a-Corpo: Machados e Cutelos": 1,
                    "Combate à Distância: Armas de Fogo": 2
                },
                "vantagens": [
                    "Destemido",
                    "Ataque Poderoso",
                    "Equipamento 3"
                ],
                "poderes": [
                    {
                        "nome": "Fervor Entorpecente",
                        "construcao": "Proteção 1 (insensibilidade à dor e fervor fanático sustentado por loucura)."
                    }
                ],
                "ataques": [
                    {
                        "nome": "Cutelo Pesado",
                        "bonus": 3,
                        "dano": 3,
                        "critico": 19,
                        "descricao": "Dano baseado em Força com gume pesado"
                    },
                    {
                        "nome": "Espingarda Calibre 12",
                        "bonus": 3,
                        "dano": 3,
                        "critico": 20,
                        "descricao": "À distância, balístico"
                    }
                ],
                "equipamento": [
                    "Cutelo pesado de carniceiro",
                    "Espingarda Calibre 12 (cano duplo)",
                    "Manto manchado de sangue"
                ]
            }
        }
    },
    {
        "pasta": "cultistas",
        "arquivo": "cultista_sacerdote.json",
        "dados": {
            "id": "cthulhu/cultistas/cultista_sacerdote",
            "genero": "cthulhu",
            "familia": "Cultista",
            "variante": "Sumo Sacerdote",
            "padrao": False,
            "nome": "Sumo Sacerdote do Culto",
            "tipo": "Humanoide",
            "subtipo": "Cultista",
            "papel": "Líder / Conjurador / Chefe",
            "chefe": True,
            "tamanho": "Médio",
            "nivel_poder": 5,
            "ambientes": [
                "Câmaras secretas de rituais",
                "Monólitos ancestrais",
                "Bibliotecas ocultistas particulares"
            ],
            "descricao": "O mestre de cerimônias da seita profana. Portador de fragmentos traduzidos de grimórios como o Necronomicon ou o De Vermis Mysteriis, comanda os servos mortais e canaliza energias das abominações além das estrelas.",
            "tatica": "Permanece atrás de seus acólitos e fanáticos, entoando encantamentos que abalam a mente dos heróis e conjurando rajadas de escuridão viva. Recorre à adaga cerimonial sacrificial apenas se encurralado.",
            "complicacoes": [
                "Obsessão Apocalíptica: devotado a despertar as divindades adormecidas, mesmo que isso destrua a Terra.",
                "Orgulho Sacerdotal: recusa-se a fugir se seu altar sagrado for profanado."
            ],
            "fonte": "Chamado de Cthulhu (7ª Edição) & M&M 3e Supernatural Handbook",
            "ficha": {
                "habilidades": {
                    "For": 0,
                    "Vig": 2,
                    "Agi": 1,
                    "Des": 1,
                    "Lut": 3,
                    "Int": 4,
                    "Pro": 4,
                    "Pre": 4
                },
                "defesas": {
                    "Esquiva": 5,
                    "Aparar": 5,
                    "Fortitude": 4,
                    "Resistencia": 5,
                    "Vontade": 6
                },
                "pericias": {
                    "Especialidade: Ocultismo": 8,
                    "Intimidação": 6,
                    "Enganação": 6,
                    "Intuição": 4,
                    "Percepção": 4,
                    "Combate Corpo-a-Corpo: Lâminas": 2,
                    "Combate à Distância: Magia dos Mythos": 4
                },
                "vantagens": [
                    "Ritualista",
                    "Fascinar (Intimidação)",
                    "Liderança",
                    "Destemido",
                    "Equipamento 2"
                ],
                "poderes": [
                    {
                        "nome": "Maldição do Vazio",
                        "construcao": "Dano 5 (À Distância, Místico / Necrótico)."
                    },
                    {
                        "nome": "Onda de Loucura Cósmica",
                        "construcao": "Aflição 5 (resistida por Vontade; Pasmo, Atordoado, Incapacitado), Área Cone (18 m)."
                    },
                    {
                        "nome": "Barreira Mística dos Antigos",
                        "construcao": "Proteção 3 (Sustentado)."
                    }
                ],
                "ataques": [
                    {
                        "nome": "Adaga Sacrificial Ondulada",
                        "bonus": 5,
                        "dano": 5,
                        "critico": 19,
                        "descricao": "Dano 5 (místico e perfurante) com gume cerimonial entalhado"
                    },
                    {
                        "nome": "Maldição do Vazio",
                        "bonus": 5,
                        "dano": 5,
                        "critico": 20,
                        "descricao": "À distância, energia do vácuo cósmico"
                    },
                    {
                        "nome": "Onda de Loucura Cósmica",
                        "bonus": 0,
                        "dano": 5,
                        "critico": 20,
                        "descricao": "Área Cone 18 m; Aflição 5 (CD 15 de Vontade; Pasmo / Atordoado / Incapacitado)"
                    }
                ],
                "equipamento": [
                    "Adaga sacrificial ondulada",
                    "Manto de seda negra com insígnias douradas",
                    "Tomo de rituais com anotações em latim"
                ]
            }
        }
    },
    {
        "pasta": "aberracoes",
        "arquivo": "carnical_mythos.json",
        "dados": {
            "id": "cthulhu/aberracoes/carnical_mythos",
            "genero": "cthulhu",
            "familia": "Carniçal dos Mythos",
            "variante": "Carniçal Nefrófago",
            "padrao": True,
            "nome": "Carniçal dos Mythos",
            "tipo": "Aberração",
            "subtipo": "Carniçal",
            "papel": "Emboscador / Lacaio",
            "chefe": False,
            "tamanho": "Médio",
            "nivel_poder": 4,
            "ambientes": [
                "Cemitérios e mausoléus antigos",
                "Túneis sob cidades litorâneas",
                "Galerias subterrâneas e catacumbas"
            ],
            "descricao": "Uma figura humanoide grotesca com feições caninas repulsivas, pele gomosa e acinzentada, membros compridos e garras encardidas com restos de sepulturas violadas. Fala em uivos guturais e grunhidos em dialetos antiquíssimos.",
            "tatica": "Espreita nas sombras e ataca de surpresa surgindo de buracos ou valas. Arrasta presas isoladas para a escuridão dos túneis enquanto outros membros do bando distraem os companheiros.",
            "complicacoes": [
                "Sensibilidade à Luz Forte: sofre desconforto e desvantagem sob sol intenso do meio-dia.",
                "Fome Necrófaga: atração obsessiva por restos mortais e carne em putrefação."
            ],
            "fonte": "H.P. Lovecraft (O Modelo de Pickman) & Chamado de Cthulhu (7ª Edição)",
            "ficha": {
                "habilidades": {
                    "For": 3,
                    "Vig": 3,
                    "Agi": 3,
                    "Des": 0,
                    "Lut": 4,
                    "Int": 0,
                    "Pro": 2,
                    "Pre": -1
                },
                "defesas": {
                    "Esquiva": 4,
                    "Aparar": 4,
                    "Fortitude": 5,
                    "Resistencia": 4,
                    "Vontade": 3
                },
                "pericias": {
                    "Furtividade": 5,
                    "Percepção": 4,
                    "Atletismo": 3,
                    "Intimidação": 4
                },
                "vantagens": [
                    "Ocultar-se à Vista de Todos",
                    "Ataque Descuidado"
                ],
                "poderes": [
                    {
                        "nome": "Garras Imundas e Mordida",
                        "construcao": "Dano 4 (Baseado em Força)."
                    },
                    {
                        "nome": "Febre dos Cadáveres",
                        "construcao": "Aflição 4 (resistida por Fortitude; Prejudicado, Indefeso), Ligado ao ataque de Garras e Mordida."
                    },
                    {
                        "nome": "Sentidos Subterrâneos",
                        "construcao": "Sentidos 3 (Visão na Penumbra, Olfato Aguçado, Rastrear)."
                    },
                    {
                        "nome": "Escalador Ágil",
                        "construcao": "Movimento 1 (Escalar Paredes 1)."
                    },
                    {
                        "nome": "Imunidades",
                        "construcao": "Imunidade 2 (Doenças e Venenos ordinários)."
                    },
                    {
                        "nome": "Pele Gomosa",
                        "construcao": "Proteção 1."
                    }
                ],
                "ataques": [
                    {
                        "nome": "Garras e Mordida",
                        "bonus": 4,
                        "dano": 4,
                        "critico": 20,
                        "descricao": "Corpo a corpo, cortante e perfurante + Aflição 4 (CD 14 de Fortitude; Febre cadavérica)"
                    }
                ]
            }
        }
    },
    {
        "pasta": "aberracoes",
        "arquivo": "profundo.json",
        "dados": {
            "id": "cthulhu/aberracoes/profundo",
            "genero": "cthulhu",
            "familia": "Profundo",
            "variante": "Guerreiro Profundo",
            "padrao": True,
            "nome": "Profundo",
            "tipo": "Aberração",
            "subtipo": "Profundo",
            "papel": "Soldado / Predador",
            "chefe": False,
            "tamanho": "Médio",
            "nivel_poder": 5,
            "ambientes": [
                "Profundezas oceânicas",
                "Costas rochosas e recifes isolados",
                "Portos decadentes (como Innsmouth)"
            ],
            "descricao": "Criatura anfíbia semi-humanoide com cabeça de peixe ou batráquio, olhos protuberantes e vítreos que jamais piscam, guelras pulsantes na garganta e membranas interdigitais. Sua pele verde-acinzentada brilha com uma camada mucosa oleosa.",
            "tatica": "Ataca em emboscadas coordenadas partindo da água. Arrasta oponentes para o fundo do mar ou rios, onde ganha vantagem absoluta de mobilidade e sufocamento.",
            "complicacoes": [
                "Dependência de Água: resseca-se e enfraquece gravemente se passar dias longe de água salgada.",
                "Devoção Absoluta: reverência inabalável ao Pai Dagon, à Mãe Hydra e ao Grande Cthulhu."
            ],
            "fonte": "H.P. Lovecraft (A Sombra sobre Innsmouth) & Chamado de Cthulhu (7ª Edição)",
            "ficha": {
                "habilidades": {
                    "For": 4,
                    "Vig": 4,
                    "Agi": 2,
                    "Des": 1,
                    "Lut": 4,
                    "Int": 0,
                    "Pro": 2,
                    "Pre": 0
                },
                "defesas": {
                    "Esquiva": 4,
                    "Aparar": 4,
                    "Fortitude": 6,
                    "Resistencia": 6,
                    "Vontade": 4
                },
                "pericias": {
                    "Atletismo": 6,
                    "Percepção": 4,
                    "Furtividade": 4,
                    "Combate Corpo-a-Corpo: Garras e Tridente": 1
                },
                "vantagens": [
                    "Luta no Chão",
                    "Empunhadura Aprimorada",
                    "Equipamento 1"
                ],
                "poderes": [
                    {
                        "nome": "Anfíbio Abissal",
                        "construcao": "Imunidade 3 (Afogamento, Frio Oceânico, Pressão das Profundezas)."
                    },
                    {
                        "nome": "Natação Veloz",
                        "construcao": "Natação 3 (15 km/h)."
                    },
                    {
                        "nome": "Couraça Escamosa e Borrachuda",
                        "construcao": "Proteção 2."
                    },
                    {
                        "nome": "Visão Abissal",
                        "construcao": "Sentidos 2 (Visão no Escuro)."
                    }
                ],
                "ataques": [
                    {
                        "nome": "Garras Lacradoras",
                        "bonus": 5,
                        "dano": 5,
                        "critico": 19,
                        "descricao": "Corpo a corpo, cortante baseado em Força"
                    },
                    {
                        "nome": "Tridente Profano",
                        "bonus": 5,
                        "dano": 5,
                        "critico": 20,
                        "descricao": "Corpo a corpo, perfurante"
                    }
                ],
                "equipamento": [
                    "Tridente de bronze trabalhado com motivos blasfemos"
                ]
            }
        }
    },
    {
        "pasta": "aberracoes",
        "arquivo": "mi_go.json",
        "dados": {
            "id": "cthulhu/aberracoes/mi_go",
            "genero": "cthulhu",
            "familia": "Mi-Go",
            "variante": "Fungo de Yuggoth",
            "padrao": True,
            "nome": "Mi-Go",
            "tipo": "Aberração",
            "subtipo": "Mi-Go",
            "papel": "Conjurador / Voador",
            "chefe": False,
            "tamanho": "Médio",
            "nivel_poder": 6,
            "ambientes": [
                "Montanhas isoladas de Vermont e Himalaia",
                "Minas e cavernas profundas",
                "Vácuo interestelar e bases em Plutão"
            ],
            "descricao": "Um ser alienígena com consistência fungosa e carapaça crustácea rosada, dotado de múltiplos pares de membros articulados, asas membranosas capazes de viajar pelo éter interestelar e uma cabeça convoluta sem rosto, cercada de pequenas antenas ciliadas que pulsam com luzes policromáticas.",
            "tatica": "Usa a mobilidade aérea e ataques à distância com seus projetores elétricos. Se engajado em combate próximo, tenta desarmar e imobilizar o oponente para capturá-lo para extração cirúrgica de cérebro.",
            "complicacoes": [
                "Estranheza Fotográfica: sua matéria não emite nem reflete a luz de forma comum, aparecendo desfocado ou invisível em emulsões fotográficas comuns.",
                "Vulnerabilidade Sônica: frequências de ressonância acústica específicas perturbam suas antenas sensoriais."
            ],
            "fonte": "H.P. Lovecraft (A Coisa no Nevoeiro) & Chamado de Cthulhu (7ª Edição)",
            "ficha": {
                "habilidades": {
                    "For": 3,
                    "Vig": 3,
                    "Agi": 2,
                    "Des": 3,
                    "Lut": 4,
                    "Int": 6,
                    "Pro": 3,
                    "Pre": 1
                },
                "defesas": {
                    "Esquiva": 6,
                    "Aparar": 5,
                    "Fortitude": 5,
                    "Resistencia": 6,
                    "Vontade": 7
                },
                "pericias": {
                    "Especialidade: Ciências Alienígenas": 8,
                    "Especialidade: Medicina Cirúrgica": 6,
                    "Percepção": 5,
                    "Tecnologia": 6,
                    "Furtividade": 4,
                    "Combate à Distância: Armas de Raio": 3,
                    "Combate Corpo-a-Corpo: Pinças": 2
                },
                "vantagens": [
                    "Inventor",
                    "Trabalho em Equipe",
                    "Ataque à Distância 3"
                ],
                "poderes": [
                    {
                        "nome": "Projetor Elétrico Alienígena",
                        "construcao": "Dano 6 (À Distância, Balístico / Energia)."
                    },
                    {
                        "nome": "Asas do Éter",
                        "construcao": "Voo 3 (250 m por rodada); Movimento 1 (Adaptação Espacial)."
                    },
                    {
                        "nome": "Fisiologia Extraterrestre Quase-Fúngica",
                        "construcao": "Imunidade 6 (Sufocamento, Vácuo, Frio Extremo, Radiação); Proteção 3."
                    },
                    {
                        "nome": "Cirurgia Extratora de Cérebros",
                        "construcao": "Aflição 6 (resistida por Fortitude; Tonto, Atordoado, Incapacitado); Permite transplante para cilindro metálico em vítimas indefesas."
                    },
                    {
                        "nome": "Comunicação Ciliada Óptica",
                        "construcao": "Comunicação 1 (Sensorial Óptico por vibração luminosa de antenas); Sentidos 3 (Visão no Escuro, Sentido Eletromagnético)."
                    }
                ],
                "ataques": [
                    {
                        "nome": "Pinças Articuladas",
                        "bonus": 6,
                        "dano": 4,
                        "critico": 20,
                        "descricao": "Corpo a corpo, cortante e contundente; agarra a vítima"
                    },
                    {
                        "nome": "Projetor Elétrico Alienígena",
                        "bonus": 6,
                        "dano": 6,
                        "critico": 20,
                        "descricao": "À distância, elétrico"
                    }
                ],
                "equipamento": [
                    "Cilindro metálico preservador de cérebros",
                    "Instrumentos cirúrgicos alienígenas"
                ]
            }
        }
    },
    {
        "pasta": "aberracoes",
        "arquivo": "shoggoth.json",
        "dados": {
            "id": "cthulhu/aberracoes/shoggoth",
            "genero": "cthulhu",
            "familia": "Shoggoth",
            "variante": "Massa Protoplasmática",
            "padrao": True,
            "nome": "Shoggoth",
            "tipo": "Aberração",
            "subtipo": "Shoggoth",
            "papel": "Bruto / Chefe (Solo)",
            "chefe": True,
            "tamanho": "Enorme",
            "nivel_poder": 9,
            "ambientes": [
                "Cidades esquecidas na Antártida",
                "Fossas submarinas abissais",
                "Ruínas pré-humanas subterrâneas"
            ],
            "descricao": "Uma gigantesca e horripilante massa plástica negra e luminescente de vários metros de diâmetro. Brota continuamente dezenas de olhos verdes pustulentos, bocas repletas de dentes pontiagudos e tentáculos espessos que se desmancham na própria gosma. Arrasta-se avassaladoramente entoando como zombaria o pavoroso grito: 'Tekeli-li! Tekeli-li!'.",
            "tatica": "Avança como uma avalanche de matéria viva esmagadora, cobrindo o campo de batalha com pseudópodes e engolindo investigadores para triturá-los sob toneladas de protoplasma.",
            "complicacoes": [
                "Pavor Ardente: sensível ao fogo contínuo e altas voltagens que incineram sua matriz orgânica.",
                "Eco dos Criadores: repete incessantemente a mímica sonora 'Tekeli-li', o que impede qualquer tentativa de passar furtivo enquanto se move."
            ],
            "fonte": "H.P. Lovecraft (Nas Montanhas da Loucura) & Chamado de Cthulhu (7ª Edição)",
            "ficha": {
                "habilidades": {
                    "For": 11,
                    "Vig": 11,
                    "Agi": 0,
                    "Des": -2,
                    "Lut": 6,
                    "Int": -3,
                    "Pro": 2,
                    "Pre": -1
                },
                "defesas": {
                    "Esquiva": 4,
                    "Aparar": 4,
                    "Fortitude": 11,
                    "Resistencia": 14,
                    "Vontade": 7
                },
                "pericias": {
                    "Intimidação": 12,
                    "Atletismo": 4,
                    "Percepção": 6,
                    "Combate Corpo-a-Corpo: Pseudópodes": 1
                },
                "vantagens": [
                    "Agarrar Aprimorado",
                    "Derrubar Aprimorado",
                    "Estrangular",
                    "Destemido",
                    "Quebrar Aprimorado",
                    "Interposição"
                ],
                "poderes": [
                    {
                        "nome": "Tamanho Enorme",
                        "construcao": "Crescimento 8 (Permanente, Inato: +8 Força, +8 Vigor, -4 Esquiva/Aparar, +1 de Velocidade)."
                    },
                    {
                        "nome": "Massa Protoplasmática Amorfa",
                        "construcao": "Imunidade 20 (Golpes Críticos, Aprisionamento, Flanqueamento, Dano Contundente reduzido à metade, Sufocamento); Proteção 3 (Impenetrável 8)."
                    },
                    {
                        "nome": "Esmagamento Protoplasmático",
                        "construcao": "Dano 11 (Baseado em Força) Ligado a Aflição 9 (resistida por Fortitude; Tonto, Atordoado, Incapacitado)."
                    },
                    {
                        "nome": "Onda de Pseudópodes",
                        "construcao": "Dano 9 (Área Explosão 9 m)."
                    },
                    {
                        "nome": "Uivo Perturbador (Tekeli-li!)",
                        "construcao": "Aflição 9 (resistida por Vontade; Pasmo, Compelido a fugir em pânico), Área Auditiva (Percepção)."
                    },
                    {
                        "nome": "Sentidos Onidirecionais",
                        "construcao": "Sentidos 4 (Visão no Escuro, Percepção Sísmica 2)."
                    },
                    {
                        "nome": "Deslocamento Plástico",
                        "construcao": "Movimento 2 (Deslizar, Escalar Paredes 1)."
                    }
                ],
                "ataques": [
                    {
                        "nome": "Esmagamento Protoplasmático",
                        "bonus": 7,
                        "dano": 11,
                        "critico": 20,
                        "descricao": "Corpo a corpo, contundente esmagador + Aflição 9 (CD 19 de Fortitude; Tonto / Atordoado / Incapacitado)"
                    },
                    {
                        "nome": "Onda de Pseudópodes",
                        "bonus": 0,
                        "dano": 9,
                        "critico": 20,
                        "descricao": "Área Explosão 9 m (CD 19 de Esquiva para metade do Dano 9 contundente)"
                    }
                ]
            }
        }
    }
]


def gerar():
    for item in CRIATURAS:
        destino = BASE / item["pasta"] / item["arquivo"]
        destino.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(item["dados"], ensure_ascii=False, indent=2) + "\n"
        destino.write_text(texto, encoding="utf-8")
        print(f"Criado: {destino.relative_to(BASE.parent.parent)}")


if __name__ == "__main__":
    gerar()
