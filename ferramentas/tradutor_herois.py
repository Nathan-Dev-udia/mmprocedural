"""Módulo e ferramenta de tradução automática de fichas de M&M 3e (Marvel e DC).

Converte termos técnicos em inglês (efeitos de poderes, modificadores/extras/falhas,
condições de aflição, vantagens, perícias, sentidos, equipamentos e defesas) para
o português canônico do livro básico oficial.
"""

import argparse
import glob
import json
import re
from pathlib import Path

# Dicionários ordenados por tamanho decrescente para evitar substituições parciais
PODERES_EFEITOS = {
    "Enhanced Advantages": "Vantagens Aprimoradas",
    "Enhanced Advantage": "Vantagem Aprimorada",
    "Enhanced Defenses": "Defesas Aprimoradas",
    "Enhanced Defense": "Defesa Aprimorada",
    "Enhanced Abilities": "Habilidades Aprimoradas",
    "Enhanced Skills": "Perícias Aprimoradas",
    "Enhanced Skill": "Perícia Aprimorada",
    "Enhanced Traits": "Características Aprimoradas",
    "Enhanced Trait": "Característica Aprimorada",
    "Enhanced Strength": "Força Aprimorada",
    "Enhanced Stamina": "Vigor Aprimorado",
    "Enhanced Agility": "Agilidade Aprimorada",
    "Enhanced Dexterity": "Destreza Aprimorada",
    "Enhanced Fighting": "Luta Aprimorada",
    "Enhanced Intellect": "Intelecto Aprimorado",
    "Enhanced Awareness": "Prontidão Aprimorada",
    "Enhanced Presence": "Presença Aprimorada",
    "Enhanced Speed": "Velocidade Aprimorada",
    "Enhanced Dodge": "Esquiva Aprimorada",
    "Enhanced Parry": "Aparar Aprimorado",
    "Enhanced Fortitude": "Fortitude Aprimorada",
    "Enhanced Will": "Vontade Aprimorada",
    "Enhanced Toughness": "Resistência Aprimorada",
    "Enhanced Initiative": "Iniciativa Aprimorada",
    "Power-Lifting": "Levantamento de Peso",
    "Power Lifting": "Levantamento de Peso",
    "Variable Effect": "Efeito Variável",
    "Impervious Toughness": "Resistência Impenetrável",
    "Environmental Adaptation": "Adaptação Ambiental",
    "Environmental Adaption": "Adaptação Ambiental",
    "Dimensional Travel": "Viagem Dimensional",
    "Space Travel": "Viagem Espacial",
    "Time Travel": "Viagem no Tempo",
    "Wall-Crawling": "Escalar Paredes",
    "Wall-crawling": "Escalar Paredes",
    "Water Walking": "Andar na Água",
    "Sure-Footed": "Passo Firme",
    "Safe Fall": "Queda Segura",
    "Trackless": "Sem Rastros",
    "Swinging": "Balançar-se",
    "Permeate": "Permear",
    "Slithering": "Rastejar",
    "Remote Sensing": "Sensoriamento Remoto",
    "Extra Limbs": "Membros Extras",
    "Super-Senses": "Super-Sentidos",
    "Super Senses": "Super-Sentidos",
    "Mental Communication": "Comunicação Mental",
    "Communication Link": "Elo de Comunicação",
    "Mental Link": "Elo Mental",
    "Mental Effects": "Efeitos Mentais",
    "Fortitude Effects": "Efeitos de Fortitude",
    "Mind Reading": "Leitura Mental",
    "Mind Control": "Controle Mental",
    "Mental Blast": "Rajada Mental",
    "Move Object": "Mover Objetos",
    "Force Field": "Campo de Força",
    "Probability Control": "Controle de Probabilidade",
    "Luck Control": "Controle de Sorte",
    "Ranged Damage": "Dano à Distância",
    "Ranged Affliction": "Aflição à Distância",
    "Close Damage": "Dano Corpo a Corpo",
    "Close Affliction": "Aflição Corpo a Corpo",
    "Damage": "Dano",
    "Affliction": "Aflição",
    "Weaken": "Enfraquecer",
    "Nullify": "Nulificar",
    "Protection": "Proteção",
    "Impervious": "Impenetrável",
    "Immunity": "Imunidade",
    "Flight": "Voo",
    "Speed": "Velocidade",
    "Quickness": "Rapidez",
    "Leaping": "Salto",
    "Swimming": "Natação",
    "Burrowing": "Escavação",
    "Teleport": "Teleporte",
    "Movement": "Movimento",
    "Insubstantial": "Intangibilidade",
    "Concealment": "Camuflagem",
    "Strike": "Golpe",
    "Blast": "Raio",
    "Illusion": "Ilusão",
    "Create": "Criar Objetos",
    "Deflect": "Deflexão",
    "Healing": "Cura",
    "Regeneration": "Regeneração",
    "Immortality": "Imortalidade",
    "Morph": "Metamorfose",
    "Shapeshift": "Mudar de Forma",
    "Variable": "Variável",
    "Summon": "Invocar",
    "Transform": "Transformar",
    "Environment": "Ambiente",
    "Senses": "Sentidos",
    "Comprehend": "Compreender",
    "Communication": "Comunicação",
    "Features": "Características",
    "Feature": "Característica",
    "Shrinking": "Encolhimento",
    "Growth": "Crescimento",
    "Dazzle": "Ofuscar",
    "Elongation": "Alongamento",
    "Telepathy": "Telepatia",
    "Mimic": "Mimetismo",
    "Snare": "Aprisionar",
    "Device": "Dispositivo",
    "Enhanced": "Aprimorado",
}

# Tradução específica para os 10 poderes da Marvel que não tinham nome_pt
NOMES_PODERES_MARVEL = {
    "Adhesive X Blaster": "Lançador de Adesivo X",
    "Star-Spangled Shield": "Escudo Estrelado",
    "Harness": "Tentáculos Mecânicos",
    "Probability Control": "Controle de Probabilidade",
    "Concealment": "Camuflagem nas Sombras",
    "Dazzle": "Clarão Cegante",
    "Shrinking 4": "Encolhimento",
    "Death Dust": "Pó da Morte",
    "Mimic (All Powers at Once) 10": "Mimetismo de Poderes",
    "Shocker Suit": "Traje de Choque",
}

SENTIDOS = {
    "Counters All Concealment": "Ignora Toda Camuflagem",
    "Penetrates Concealment": "Penetra Camuflagem",
    "Counters Concealment": "Ignora Camuflagem",
    "Counters Illusion": "Ignora Ilusão",
    "Microscopic Vision": "Visão Microscópica",
    "Telescopic Vision": "Visão Telescópica",
    "Low-Light Vision": "Visão na Penumbra",
    "Low-light Vision": "Visão na Penumbra",
    "Extended Vision": "Visão Estendida",
    "Extended Hearing": "Audição Estendida",
    "X-Ray Vision": "Visão de Raios-X",
    "Heat Vision": "Visão de Calor",
    "Night Vision": "Visão Noturna",
    "Mental Awareness": "Consciência Mental",
    "Magic Awareness": "Consciência Mágica",
    "Cosmic Awareness": "Consciência Cósmica",
    "Danger Sense": "Sentido de Perigo",
    "Direction Sense": "Noção de Direção",
    "Distance Sense": "Noção de Distância",
    "Time Sense": "Noção do Tempo",
    "Postcognition": "Pós-cognição",
    "Precognition": "Precognição",
    "Darkvision": "Visão no Escuro",
    "Infravision": "Infravisão",
    "Ultravision": "Ultravisão",
    "Ultra-Hearing": "Ultra-Audição",
    "Tremorsense": "Sentido Sísmico",
    "Tracking": "Rastrear",
    "Track": "Rastrear",
    "Awareness": "Consciência",
    "Detect": "Detectar",
    "Radio": "Rádio",
    "Accurate": "Acurado",
    "Acute": "Aguçado",
    "Analytical": "Analítico",
    "Rapid": "Rápido",
    "Extended": "Estendido",
    "Radius": "Raio",
    "Ranged": "À Distância",
    "Olfactory": "Olfativo",
    "Auditory": "Auditivo",
    "Tactile": "Tátil",
    "Visual": "Visual",
    "Vision": "Visão",
    "Sight": "Visão",
    "Hearing": "Audição",
    "Smell": "Olfato",
}

CONDIÇÕES_AFLICAO = {
    "Dazed": "Tonto",
    "Stunned": "Atordoado",
    "Incapacitated": "Incapacitado",
    "Hindered": "Impedido",
    "Impaired": "Prejudicado",
    "Disabled": "Desabilitado",
    "Debilitated": "Debilitado",
    "Unaware": "Desatento",
    "Immobile": "Imóvel",
    "Paralyzed": "Paralisado",
    "Vulnerable": "Vulnerável",
    "Defenseless": "Indefeso",
    "Compelled": "Compelido",
    "Controlled": "Controlado",
    "Transformed": "Transformado",
    "Entranced": "Em Transe",
    "Bound": "Preso",
    "Restrained": "Restrito",
    "Prone": "Caído",
    "Surprised": "Surpreso",
    "Asleep": "Adormecido",
    "Blind": "Cego",
    "Deaf": "Surdo",
    "Fatigued": "Fatigado",
    "Weary": "Fatigado",
    "Exhausted": "Exausto",
    "Dying": "Moribundo",
}

MODIFICADORES = {
    "Perception Range": "Alcance de Percepção",
    "Increased Range": "Alcance Aumentado",
    "Extended Range": "Alcance Estendido",
    "Diminished Range": "Alcance Diminuído",
    "Close Range": "Alcance Perto",
    "Alternate Resistance": "Resistência Alternativa",
    "Concentration Duration": "Duração de Concentração",
    "Easily Removable": "Facilmente Removível",
    "Easily removable": "Facilmente Removível",
    "Shapeable Area": "Área Moldável",
    "Cylinder Area": "Área Cilíndrica",
    "Burst Area": "Área de Explosão",
    "Cloud Area": "Área de Nuvem",
    "Cone Area": "Área de Cone",
    "Line Area": "Área de Linha",
    "Variable Descriptor": "Descritor Variável",
    "Variable General Type": "Tipo Geral Variável",
    "Variable Type": "Tipo Variável",
    "Affects Objects Only": "Afeta Apenas Objetos",
    "Affects Only Objects": "Afeta Apenas Objetos",
    "Affects Objects": "Afeta Objetos",
    "Affects Others": "Afeta Outros",
    "Affects Corporeal": "Afeta Corpóreo",
    "Affects Insubstantial": "Afeta Intangível",
    "Sense-Dependent": "Dependente de Sentidos",
    "Check Required": "Exige Teste",
    "Free Action": "Ação Livre",
    "Move Action": "Ação de Movimento",
    "Standard Action": "Ação Padrão",
    "Secondary Effect": "Efeito Secundário",
    "Side Effect": "Efeito Colateral",
    "Grab-based": "Baseado em Agarrar",
    "Dynamic Alternate Effect": "Efeito Alternativo Dinâmico",
    "Alternate Effect": "Efeito Alternativo",
    "Dynamic Array": "Arranjo Dinâmico",
    "Multiple Minions": "Múltiplos Capangas",
    "While Moving": "Enquanto se Move",
    "Selective": "Seletivo",
    "Simultaneous": "Simultâneo",
    "Multiattack": "Multiataque",
    "Penetrating": "Penetrante",
    "Precise": "Preciso",
    "Subtle": "Sutil",
    "Insidious": "Insidioso",
    "Triggered": "Gatilho",
    "Contagious": "Contagioso",
    "Cumulative": "Cumulativo",
    "Progressive": "Progressivo",
    "Continuous": "Contínuo",
    "Sustained": "Sustentado",
    "Reaction": "Reação",
    "Concentration": "Concentração",
    "Limited to Two Degrees": "Limitado a Dois Graus",
    "Limited to": "Limitado a",
    "Limited": "Limitado",
    "Removable": "Removível",
    "removable": "removível",
    "Array": "Arranjo",
    "Dynamic": "Dinâmico",
    "Broad": "Amplo",
    "Distracting": "Distrativo",
    "Fades": "Dissipação",
    "Tiring": "Cansativo",
    "Uncontrolled": "Descontrolado",
    "Unreliable": "Não Confiável",
    "Activation": "Ativação",
    "Quirk": "Peculiaridade",
    "Resistible": "Resistível",
    "Noticeable": "Perceptível",
    "Innate": "Inato",
    "Permanent": "Permanente",
    "Feedback": "Retroalimentação",
    "Dimensional": "Dimensional",
    "Linked to": "Ligado a",
    "Linked": "Ligado",
    "Indirect": "Indireto",
    "Split": "Dividido",
    "Homing": "Teleguiado",
    "Reversible": "Reversível",
    "Ricochet": "Ricochete",
    "Shapeable": "Moldável",
    "Cylinder": "Cilindro",
    "Cloud": "Nuvem",
    "Burst": "Estouro",
    "Horde": "Horda",
    "Flat": "Fixo",
    "Only": "Apenas",
    "Ranged": "À Distância",
    "Close": "Corpo a Corpo",
}

VANTAGENS = {
    "Accurate Attack": "Ataque Acurado",
    "Precise Attack": "Ataque Preciso",
    "Agile Feint": "Finta Ágil",
    "All-out Attack": "Ataque Imprudente",
    "All-Out Attack": "Ataque Imprudente",
    "Animal Empathy": "Empatia com Animais",
    "Artificer": "Artífice",
    "Assessment": "Avaliação",
    "Attractive": "Atraente",
    "Beginner's Luck": "Sorte de Principiante",
    "Beginner’s Luck": "Sorte de Principiante",
    "Benefit": "Benefício",
    "Chokehold": "Estrangular",
    "Close Attack": "Ataque Corpo-a-Corpo",
    "Connected": "Bem Relacionado",
    "Contacts": "Contatos",
    "Daze": "Tontear",
    "Defensive Attack": "Ataque Defensivo",
    "Defensive Roll": "Rolamento Defensivo",
    "Diehard": "Duro de Matar",
    "Eidetic Memory": "Memória Eidética",
    "Environment Adaptation": "Adaptação Ambiental",
    "Equipment": "Equipamento",
    "Evasion": "Evasão",
    "Extraordinary Effort": "Esforço Extraordinário",
    "Fascinate": "Fascinar",
    "Fast Grab": "Agarrar Rápido",
    "Favored Environment": "Ambiente Favorito",
    "Favored Foe": "Inimigo Favorito",
    "Fearless": "Destemido",
    "Grabbing Finesse": "Agarrar Preciso",
    "Great Endurance": "Tolerância Maior",
    "Hide in Plain Sight": "Esconder-se à Plena Vista",
    "Improved Aim": "Mira Aprimorada",
    "Improved Critical": "Crítico Aprimorado",
    "Improved Defense": "Defesa Aprimorada",
    "Improved Disarm": "Desarmar Aprimorado",
    "Improved Grab": "Agarrar Aprimorado",
    "Improved Hold": "Imobilizar Aprimorado",
    "Improved Initiative": "Iniciativa Aprimorada",
    "Improved Smash": "Quebrar Aprimorado",
    "Improved Trip": "Derrubar Aprimorado",
    "Improvised Tools": "Ferramentas Aprimoradas",
    "Improvised Weapon": "Arma Improvisada",
    "Inspire": "Inspirar",
    "Instant Up": "De Pé",
    "Interpose": "Interpor-se",
    "Inventor": "Inventor",
    "Jack-of-all-trades": "Faz Tudo",
    "Jack-of-All-Trades": "Faz Tudo",
    "Jack of All Trades": "Faz Tudo",
    "Endurance (Great Endurance)": "Tolerância Maior",
    "Endurance": "Tolerância Maior",
    "Improved Grapple": "Agarrar Aprimorado",
    "Improved Sunder": "Quebrar Aprimorado",
    "Grappling Finesse": "Agarrar Preciso",
    "Precise Shot": "Ataque Preciso",
    "Quickdraw": "Saque Rápido",
    "Quick Draw": "Saque Rápido",
    "Move By Action": "Ação em Movimento",
    "Move By-Action": "Ação em Movimento",
    "Move-by Action": "Ação em Movimento",
    "Move-by Attack": "Ação em Movimento",
    "All Out Attack": "Ataque Imprudente",
    "All-Out attack": "Ataque Imprudente",
    "Ambidexterity": "Benefício (Ambidestria)",
    "Favred Environment": "Ambiente Favorito",
    "Languages": "Idiomas",
    "Leadership": "Liderança",
    "Luck": "Sorte",
    "Minion": "Capanga",
    "Power Attack": "Ataque Poderoso",
    "Prone Fighting": "Luta no Chão",
    "Quick Draw": "Saque Rápido",
    "Ranged Attack": "Ataque à Distância",
    "Redirect": "Redirecionar",
    "Ritualist": "Ritualista",
    "Second Chance": "Segunda Chance",
    "Seize Initiative": "Tomar a Iniciativa",
    "Set-up": "Armação",
    "Set-Up": "Armação",
    "Sidekick": "Parceiro",
    "Skill Mastery": "Maestria em Perícia",
    "Startle": "Assustar",
    "Takedown Attack": "Ataque Dominó",
    "Takedown": "Ataque Dominó",
    "Taunt": "Zombar",
    "Teamwork": "Trabalho em Equipe",
    "Throwing Mastery": "Maestria em Arremesso",
    "Tracking": "Rastrear",
    "Trance": "Transe",
    "Ultimate Effort": "Esforço Supremo",
    "Uncanny Dodge": "Esquiva Fabulosa",
    "Weapon Bind": "Prender Arma",
    "Weapon Break": "Quebrar Arma",
    "Well-informed": "Bem Informado",
    "Well-Informed": "Bem Informado",
    "Sneak Attack": "Ataque Furtivo",
}
_VANTAGENS_LOWER = {k.lower(): v for k, v in VANTAGENS.items()}

PERICIAS = {
    "Acrobatics": "Acrobacia",
    "Athletics": "Atletismo",
    "Close Combat": "Combate Corpo-a-Corpo",
    "Deception": "Enganação",
    "Expertise": "Especialidade",
    "Insight": "Intuição",
    "Intimidation": "Intimidação",
    "Intimidate": "Intimidação",
    "Investigation": "Investigação",
    "Investigate": "Investigação",
    "Perception": "Percepção",
    "Persuasion": "Persuasão",
    "Ranged Combat": "Combate à Distância",
    "Sleight of Hand": "Prestidigitação",
    "Stealth": "Furtividade",
    "Technology": "Tecnologia",
    "Treatment": "Tratamento",
    "Vehicles": "Veículos",
}

ESPECIALIDADES_PERICIAS = {
    "Behavioral Sciences": "Ciências Comportamentais",
    "Physical Sciences": "Ciências Físicas",
    "Earth Sciences": "Ciências da Terra",
    "Life Sciences": "Ciências da Vida",
    "Theology and Philosophy": "Teologia e Filosofia",
    "Journalism and Politics": "Jornalismo e Política",
    "Current Events": "Atualidades",
    "Popular Culture": "Cultura Popular",
    "Law Enforcement": "Policiamento",
    "Arcane Lore": "Conhecimento Arcano",
    "Streetwise": "Manha",
    "Criminology": "Criminologia",
    "Cryptozoology": "Criptozoologia",
    "Psychology": "Psicologia",
    "Psychiatry": "Psiquiatria",
    "Philosophy": "Filosofia",
    "Astronomy": "Astronomia",
    "Chemistry": "Química",
    "Physics": "Física",
    "Biology": "Biologia",
    "Genetics": "Genética",
    "Engineering": "Engenharia",
    "Electronics": "Eletrônica",
    "Mechanics": "Mecânica",
    "Computers": "Computação",
    "Robotics": "Robótica",
    "Journalism": "Jornalismo",
    "Literature": "Literatura",
    "Photography": "Fotografia",
    "Navigation": "Navegação",
    "History": "História",
    "Medicine": "Medicina",
    "Business": "Negócios",
    "Tactics": "Tática",
    "Military": "Militar",
    "Civics": "Cidadania",
    "Law": "Direito",
    "Magic": "Magia",
    "Science": "Ciência",
    "Politics": "Política",
    "Survival": "Sobrevivência",
    "Singing": "Canto",
    "Acting": "Atuação",
    "Cooking": "Culinária",
    "Dancing": "Dança",
    "Drawing": "Desenho",
    "Painting": "Pintura",
    "Farming": "Agricultura",
    "Gambling": "Jogos de Azar",
    "Comedy": "Comédia",
    "Music": "Música",
    "Art": "Arte",
    "Firearms": "Armas de Fogo",
    "Throwing": "Arremesso",
    "Thrown": "Arremesso",
    "Archery": "Arco e Flecha",
    "Unarmed": "Desarmado",
    "Pistols": "Pistolas",
    "Rifles": "Rifles",
    "Swords": "Espadas",
    "Blades": "Lâminas",
    "Clubs": "Clavas",
    "Bows": "Arcos",
    "Bow": "Arco",
    "Guns": "Armas de Fogo",
}

DEFESAS = {
    "Dodge": "Esquiva",
    "Parry": "Aparar",
    "Fortitude": "Fortitude",
    "Toughness": "Resistência",
    "Will": "Vontade",
}

HABILIDADES = {
    "Strength": "Força",
    "Stamina": "Vigor",
    "Agility": "Agilidade",
    "Dexterity": "Destreza",
    "Fighting": "Luta",
    "Intellect": "Intelecto",
    "Awareness": "Prontidão",
    "Presence": "Presença",
}

TERMOS_GERAIS = {
    "Strength-based": "Baseado em Força",
    "Strength-Based": "Baseado em Força",
    "Str-based": "Baseado em Força",
    "Damage-based": "Baseado em Dano",
    "Resisted and Overcome by": "Resistido e Superado por",
    "Resisted by": "resistido por",
    "Overcome by": "Superado por",
    "Without Defensive Roll": "sem Rolamento Defensivo",
    "Without Venom": "sem Veneno",
    "Varies based on Shapeshifting": "Varia com Mudar de Forma",
    "Will saves": "salvamentos de Vontade",
    "Toughness saves": "salvamentos de Resistência",
    "Fortitude saves": "salvamentos de Fortitude",
    "Damage resistance": "Resistência a Dano",
    "Starvation and Thirst": "Fome e Sede",
    "Need for Sleep": "Necessidade de Sono",
    "Own Powers": "Próprios Poderes",
    "Slam Damage": "Dano de Investida",
    "Falling Damage": "Dano de Queda",
    "High Pressure": "Alta Pressão",
    "Improved Initiative": "Iniciativa Aprimorada",
    "Seize Initiative": "Tomar a Iniciativa",
    "Defensive Roll": "Rolamento Defensivo",
    "Eidetic Memory": "Memória Eidética",
    "Uncanny Dodge": "Esquiva Fabulosa",
    "Move-by Action": "Ação em Movimento",
    "Hide in Plain Sight": "Esconder-se à Plena Vista",
    "Second Chance": "Segunda Chance",
    "All-out Attack": "Ataque Imprudente",
    "All-Out Attack": "Ataque Imprudente",
    "Agile Feint": "Finta Ágil",
    "Instant Up": "De Pé",
    "Interpose": "Interpor-se",
    "Takedown": "Ataque Dominó",
    "Evasion": "Evasão",
    "Ball and Chain": "Bola e Corrente",
    "Knife Attack": "Ataque com Faca",
    "Shield Bash": "Golpe com Escudo",
    "Optic Blasters": "Disparadores Ópticos",
    "Mini-Torpedoes": "Minitorpedos",
    "Grapple-Wire": "Cabo de Gancho",
    "Electric Shock": "Choque Elétrico",
    "Twin Blades": "Lâminas Gêmeas",
    "Lapel Flower": "Flor de Lapela",
    "Joker Venom": "Veneno do Coringa",
    "Squirting Acid": "Ácido Espirrado",
    "Joy Buzzer": "Campainha Elétrica",
    "Life Support": "Suporte Vital",
    "Omega Effect": "Efeito Ômega",
    "Crit.": "Crít.",
    "Crit": "Crít",
    "points": "pontos",
    "point": "ponto",
    "ranks": "graduações",
    "rank": "graduação",
    "Unarmed": "Desarmado",
    "Initiative": "Iniciativa",
    "Close": "corpo a corpo",
    "Ranged": "à distância",
    "Area": "área",
    "DC": "CD",
    "Airborne": "Aéreo",
    "Underwater": "Subaquático",
    "Abilities": "Habilidades",
    "Ability": "Habilidade",
    "Defenses": "Defesas",
    "Advantages": "Vantagens",
    "Advantage": "Vantagem",
    "Skills": "Perícias",
    "Skill": "Perícia",
    "Effects": "Efeitos",
    "Powers": "Poderes",
    "Power": "Poder",
    "Checks": "Testes",
    "Check": "Teste",
    "Degrees": "Graus",
    "Degree": "Grau",
    "Immune": "Imune",
    "Animals": "Animais",
    "Machines": "Máquinas",
    "Objects": "Objetos",
    "Plants": "Plantas",
    "Spirits": "Espíritos",
    "minions": "capangas",
    "minion": "capanga",
    "miles": "milhas",
    "feet": "pés",
    "ft.": "pés",
    "tons": "toneladas",
    "lbs.": "libras",
    "lbs": "libras",
    "Aging": "Envelhecimento",
    "Cold": "Frio",
    "Heat": "Calor",
    "Fire": "Fogo",
    "Ice": "Gelo",
    "Pressure": "Pressão",
    "Drowning": "Afogamento",
    "Disease": "Doença",
    "Poison": "Veneno",
    "Sleep": "Sono",
    "Suffocation": "Sufocamento",
    "Radiation": "Radiação",
    "Vacuum": "Vácuo",
    "Starvation": "Inanição",
    "Energy": "Energia",
    "Light": "Luz",
    "Darkness": "Escuridão",
    "Electricity": "Eletricidade",
    "Electrical": "Elétrico",
    "Magnetic": "Magnético",
    "Gravity": "Gravidade",
    "Sonic": "Sônico",
    "Vibration": "Vibração",
    "Acid": "Ácido",
    "Weather": "Clima",
    "Magic": "Magia",
    "Magical": "Mágico",
    "Psionic": "Psiônico",
    "Psychic": "Psíquico",
    "Cosmic": "Cósmico",
    "Divine": "Divino",
    "Mystic": "Místico",
    "Bludgeoning": "Contusão",
    "Piercing": "Perfurante",
    "Slashing": "Cortante",
    "Ballistic": "Balístico",
    "Bullets": "Balas",
    "plus others": "mais outros",
    "Pistol": "Pistola",
    "Rifle": "Rifle",
    "Sword": "Espada",
    "Shield": "Escudo",
    "Tommy Gun": "Metralhadora Tommy",
    "Bio-Shell Strikes": "Golpes de Bio-Carapaça",
    "Marbles": "Bolinhas de Gude",
    "Batarangs": "Batarangues",
    "Batarang": "Batarangue",
    "Immortal": "Imortal",
    "Destruction": "Destruição",
    "Pain": "Dor",
    "Transportation": "Transporte",
    "without": "sem",
    "against": "contra",
    "with": "com",
    "and": "e",
}

BENEFICIOS_VANTAGEM = {
    "Cover and Concealment": "Cobertura e Camuflagem",
    "Independently Wealthy": "Independentemente Rico",
    "Diplomatic Immunity": "Imunidade Diplomática",
    "Security Clearance": "Credencial de Segurança",
    "Multi-millionaire": "Multimilionário",
    "Millionaire": "Milionário",
    "Billionaire": "Bilionário",
    "Ambidexterity": "Ambidestria",
    "Concealment": "Camuflagem",
    "Close": "Corpo a Corpo",
    "Ranged": "À Distância",
    "Cover": "Cobertura",
    "Well-off": "Abastado",
    "Wealth": "Riqueza",
    "Cipher": "Cifra",
    "Zero-G": "Gravidade Zero",
    "Underwater": "Subaquático",
    "Portuguese": "Português",
    "English": "Inglês",
    "Spanish": "Espanhol",
    "French": "Francês",
    "German": "Alemão",
    "Italian": "Italiano",
    "Russian": "Russo",
    "Japanese": "Japonês",
    "Chinese": "Chinês",
    "Arabic": "Árabe",
    "Latin": "Latim",
    "Greek": "Grego",
    "Sense Motive": "Intuição",
    "Gather Information": "Investigação",
    "Escape Artist": "Acrobacia",
    "Disable Device": "Tecnologia",
    "Ultimate Toughness Save": "Salvamento de Resistência Supremo",
    "Environmental Adaptation": "Adaptação Ambiental",
    "Knowledge": "Especialidade",
    "Diplomacy": "Persuasão",
    "Concentration": "Concentração",
    "Computers": "Tecnologia",
    "Bluff": "Enganação",
    "Climb": "Atletismo",
    "Craft": "Especialidade",
    "Search": "Investigação",
    "Notice": "Percepção",
    "Drive": "Veículos",
    "Pilot": "Veículos",
    "Ride": "Veículos",
    "Claws": "Garras",
    "Airborn": "Aéreo",
    "Storms": "Tempestades",
}

_NORMALIZAR_PERICIAS_PT = {
    "Combate a Distancia": "Combate à Distância",
    "Combate a distância": "Combate à Distância",
    "Reunir Informacoes": "Reunir Informações",
    "Enganacao": "Enganação",
    "Intimidacao": "Intimidação",
    "Intuicao": "Intuição",
    "Investigacao": "Investigação",
    "Percepcao": "Percepção",
    "Persuasao": "Persuasão",
    "Prestidigitacao": "Prestidigitação",
    "Veiculos": "Veículos",
    "Ciencias": "Ciências",
    "Fisicas": "Físicas",
    "Mecanica": "Mecânica",
    "Taticas": "Táticas",
    "Laminas": "Lâminas",
    "Civica": "Cívica",
    "Eletrica": "Elétrica",
    "Mercenario": "Mercenário",
    "Quimica": "Química",
    "Sobrevivencia": "Sobrevivência",
    "Webbing": "Teia",
}

EQUIPAMENTO_TERMOS = {
    "Damage": "Dano",
    "Toughness": "Resistência",
    "Protection": "Proteção",
    "Autofire": "Multiataque",
    "Auto-Fire": "Multiataque",
    "Mighty": "Baseado em Força",
    "Improved Critical": "Crítico Aprimorado",
    "Subtle": "Sutil",
    "EP": "PE",
    "Crit": "Crítico",
}


def _substituir_mapa(texto, mapa):
    """Substitui termos inteiros baseando-se em limites de palavras e regex."""
    if not texto:
        return texto
    for k in sorted(mapa.keys(), key=len, reverse=True):
        v = mapa[k]
        padrao = r"\b" + re.escape(k) + r"\b"
        texto = re.sub(padrao, v, texto, flags=re.IGNORECASE)
    return texto


def _formatar_kmh(match):
    bruto = match.group(1).replace(",", "")
    if not bruto.isdigit():
        return match.group(0)
    valor = int(int(bruto) * 1.6)
    return f"{valor:,}".replace(",", ".") + " km/h"


def traduzir_construcao(texto):
    """Traduz fórmulas mecânicas de poderes e efeitos (ex: construcao_3e)."""
    if not texto:
        return texto

    texto = re.sub(
        r"(Enhanced Advantages?(?:\s+\d+)?\s*)\(([^)]+)\)",
        lambda m: m.group(1) + "(" + ", ".join(traduzir_vantagem(v.strip()) for v in m.group(2).split(",")) + ")",
        texto,
    )

    texto = _substituir_mapa(texto, PODERES_EFEITOS)
    texto = _substituir_mapa(texto, SENTIDOS)
    texto = _substituir_mapa(texto, CONDIÇÕES_AFLICAO)
    texto = _substituir_mapa(texto, MODIFICADORES)
    texto = _substituir_mapa(texto, DEFESAS)
    texto = _substituir_mapa(texto, HABILIDADES)
    texto = _substituir_mapa(texto, PERICIAS)
    texto = _substituir_mapa(texto, ESPECIALIDADES_PERICIAS)
    texto = _substituir_mapa(texto, TERMOS_GERAIS)

    # Ajustar MPH para km/h (aceitando separador de milhar por vírgula)
    texto = re.sub(r"([\d,]+)\s*MPH\b", _formatar_kmh, texto, flags=re.IGNORECASE)
    return texto


traduzir_texto_poder = traduzir_construcao


def _normalizar_espacos_vantagem(texto):
    texto = texto.replace("’", "'").strip()
    texto = re.sub(r"([A-Za-z])-\s+([A-Za-z])", r"\1-\2", texto)
    texto = re.sub(r"([A-Za-z])\s+-([A-Za-z])", r"\1-\2", texto)
    return texto


def traduzir_vantagem(nome):
    """Traduz o nome de uma vantagem (ex: 'Uncanny Dodge', 'Improved Critical 2 (Unarmed)')."""
    if not nome:
        return nome

    nome = _normalizar_espacos_vantagem(nome)

    if nome.startswith("Feature:"):
        detalhe = nome.split(":", 1)[1].strip()
        detalhe_pt = re.sub(r"\[([^\]]+)\]", r"(\1)", detalhe)
        detalhe_pt = _substituir_mapa(detalhe_pt, BENEFICIOS_VANTAGEM)
        detalhe_pt = _substituir_mapa(detalhe_pt, TERMOS_GERAIS)
        return f"Característica: {detalhe_pt}"

    m = re.match(r"^([^(\[]+)[\(\[](.+?)[\)\]](.*)$", nome)
    if m:
        base, dentro, resto = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        m_rank = re.match(r"^(.+?)\s+(\d+)$", base)
        if m_rank:
            nome_base, rank = m_rank.group(1).strip(), m_rank.group(2)
            base_pt = _VANTAGENS_LOWER.get(nome_base.lower(), nome_base)
            base_pt = f"{base_pt} {rank}"
        else:
            base_pt = _VANTAGENS_LOWER.get(base.lower(), base)

        dentro_pt = _substituir_mapa(dentro, PERICIAS)
        dentro_pt = _substituir_mapa(dentro_pt, ESPECIALIDADES_PERICIAS)
        dentro_pt = _substituir_mapa(dentro_pt, BENEFICIOS_VANTAGEM)
        dentro_pt = _substituir_mapa(dentro_pt, SENTIDOS)
        dentro_pt = _substituir_mapa(dentro_pt, DEFESAS)
        dentro_pt = _substituir_mapa(dentro_pt, HABILIDADES)
        dentro_pt = _substituir_mapa(dentro_pt, TERMOS_GERAIS)
        res = f"{base_pt} ({dentro_pt})"
        if resto:
            res += f" {resto}"
        return res

    m_num = re.match(r"^(.+?)\s+(\d+)$", nome)
    if m_num:
        base, num = m_num.group(1).strip(), m_num.group(2)
        base_pt = _VANTAGENS_LOWER.get(base.lower(), base)
        return f"{base_pt} {num}"

    return _VANTAGENS_LOWER.get(nome.lower(), nome)


def traduzir_pericia(nome):
    """Traduz nome de perícia (ex: 'Close Combat: Unarmed' -> 'Combate Corpo-a-Corpo: Desarmado')."""
    if not nome:
        return nome
    for sem, com in _NORMALIZAR_PERICIAS_PT.items():
        nome = re.sub(r"\b" + re.escape(sem) + r"\b", com, nome)
    for k, v in PERICIAS.items():
        if nome.lower().startswith(k.lower()):
            resto = nome[len(k):]
            resto = _substituir_mapa(resto, ESPECIALIDADES_PERICIAS)
            resto = _substituir_mapa(resto, TERMOS_GERAIS)
            return f"{v}{resto}"
    if ":" in nome:
        base, _, esp = nome.partition(":")
        esp = _substituir_mapa(esp, ESPECIALIDADES_PERICIAS)
        return f"{base}:{esp}"
    return nome


def traduzir_equipamento(texto):
    """Traduz termos comuns em equipamentos (ex: '+3 Damage; Mighty; 2 EP')."""
    if not texto:
        return texto
    return _substituir_mapa(texto, EQUIPAMENTO_TERMOS)


def traduzir_ficha_marvel(dados):
    """Traduz os campos de uma ficha da Marvel (JSON)."""
    ficha = dados.get("ficha", {})
    
    # 1. Poderes
    for p in ficha.get("poderes", []):
        nome = p.get("nome", "")
        nome_pt = p.get("nome_pt", "")
        if not nome_pt or nome_pt == nome:
            trad = NOMES_PODERES_MARVEL.get(nome) or PODERES_EFEITOS.get(nome) or SENTIDOS.get(nome)
            if trad:
                p["nome_pt"] = trad
        if "construcao_3e" in p:
            p["construcao_3e"] = traduzir_construcao(p["construcao_3e"])
            
    # 2. Vantagens
    novas_vantagens = []
    for v in ficha.get("vantagens", []):
        novas_vantagens.append(traduzir_vantagem(v))
    ficha["vantagens"] = novas_vantagens
    
    # 3. Perícias
    pericias = ficha.get("pericias", {})
    if isinstance(pericias, dict):
        novas_pericias = {}
        for k, val in pericias.items():
            novas_pericias[traduzir_pericia(k)] = val
        ficha["pericias"] = novas_pericias

    # 4. Equipamento
    if "equipamento" in ficha and isinstance(ficha["equipamento"], list):
        ficha["equipamento"] = [traduzir_equipamento(eq) for eq in ficha["equipamento"]]
        
    return dados


def traduzir_ficha_dc_publicada(ficha_pub):
    """Traduz os blocos de texto publicados das fichas da DC."""
    res = dict(ficha_pub)
    
    if "defesas" in res:
        res["defesas"] = _substituir_mapa(res["defesas"], DEFESAS)
        res["defesas"] = res["defesas"].replace("Without Defensive Roll", "sem Rolamento Defensivo")
        
    if "pericias" in res:
        itens = [p.strip() for p in res["pericias"].split(",")]
        novos = [_substituir_mapa(it, PERICIAS) for it in itens]
        res["pericias"] = ", ".join(novos)
        
    if "vantagens" in res:
        itens = [v.strip() for v in res["vantagens"].split(",")]
        novos = [traduzir_vantagem(v) for v in itens]
        res["vantagens"] = ", ".join(novos)
        
    if "poderes" in res:
        res["poderes"] = traduzir_construcao(res["poderes"])
        
    if "ataques" in res:
        res["ataques"] = _substituir_mapa(res["ataques"], TERMOS_GERAIS)
        res["ataques"] = _substituir_mapa(res["ataques"], PODERES_EFEITOS)
        
    return res


def aplicar_traducao_marvel(raiz_projeto=None):
    """Aplica a tradução nos 116 arquivos da Marvel salvando os arquivos no disco."""
    raiz = Path(raiz_projeto) if raiz_projeto else Path(__file__).resolve().parent.parent
    pasta_marvel = raiz / "dados" / "generos" / "herois" / "marvel"
    arquivos = list(pasta_marvel.glob("*.json"))
    total_modificados = 0

    for arq in arquivos:
        original = json.loads(arq.read_text(encoding="utf-8"))
        copia = json.loads(json.dumps(original))
        traduzido = traduzir_ficha_marvel(copia)
        
        str_orig = json.dumps(original, ensure_ascii=False, indent=2)
        str_trad = json.dumps(traduzido, ensure_ascii=False, indent=2)
        if str_orig != str_trad:
            arq.write_text(str_trad + "\n", encoding="utf-8")
            total_modificados += 1

    print(f"Tradução da Marvel concluída: {total_modificados} de {len(arquivos)} arquivos atualizados.")
    return total_modificados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tradutor de fichas de heróis de M&M 3e.")
    parser.add_argument("--marvel", action="store_true", help="Aplica tradução nos arquivos da Marvel")
    args = parser.parse_args()

    if args.marvel:
        aplicar_traducao_marvel()
    else:
        print("Use --marvel para aplicar a tradução aos arquivos da Marvel.")
