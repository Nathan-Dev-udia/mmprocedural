"""Gera o arquivo dados/escudo/cthulhu.json para o Escudo do Mestre de Chamado de Cthulhu."""

import json
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "dados" / "escudo" / "cthulhu.json"

escudo_cthulhu = {
  "_fonte": "Resumo das regras de Chamado de Cthulhu 7ª edição adaptadas para Mutantes & Malfeitores 3ª edição. Os blocos 'gerado' são calculados por nucleo/escudo.py.",
  "genero": "cthulhu",
  "titulo": "Escudo do Mestre: Chamado de Cthulhu",
  "abas": [
    {
      "id": "testes",
      "nome": "Testes",
      "blocos": [
        {
          "tipo": "formulas",
          "titulo": "Fórmulas básicas",
          "itens": [
            "**Teste** = d20 + graduação + modificadores, contra a CD",
            "**Rotina** = 10 + graduação (sem pressão imediata; só com treino na perícia)",
            "**Ataque** = d20 + bônus de ataque, contra defesa ativa + 10 (Aparar corpo a corpo, Esquiva à distância)",
            "**Salvamento contra efeito** = d20 + defesa, contra 10 + graduação",
            "**Salvamento contra dano** = d20 + Resistência, contra 15 + Dano",
            "**Teste de Sanidade** = d100 contra a Sanidade atual (rolar menor ou igual para ter sucesso)"
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Classes de dificuldade",
          "colunas": ["CD", "Dificuldade", "Exemplo nos anos 1920"],
          "linhas": [
            ["0", "Muito fácil", "Disparar uma escopeta à queima-roupa contra um monstro imenso imóvel"],
            ["5", "Fácil", "Encontrar um livro comum ou jornal recente na biblioteca municipal de Arkham"],
            ["10", "Médio", "Notar pegadas de lama recentes no chão de madeira da cena do crime"],
            ["15", "Difícil", "Abrir a fechadura do cofre de aço antigo sem ruído durante a noite"],
            ["20", "Desafiador", "Identificar um dialeto arcaico gravado em tábuas de pedra pré-humanas"],
            ["25", "Formidável", "Despistar cultistas hostis correndo a pé pelas vielas de Innsmouth sob névoa"],
            ["30", "Quase impossível", "Traduzir o Necronomicon completo em latim sem gritar ou desmaiar"]
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Graus de sucesso e de falha",
          "colunas": ["Margem", "Sucesso (rolagem ≥ CD)", "Falha (rolagem < CD)"],
          "linhas": [
            ["0 a 4", "1º grau: sucesso normal", "1º grau: falha simples sem complicação maior"],
            ["5 a 9", "2º grau: sucesso com rapidez ou pista extra", "2º grau: falha evidente; perde tempo ou chama atenção"],
            ["10 a 14", "3º grau: sucesso exemplar; informação oculta", "3º grau: falha grave; quebra ferramenta ou estraga pista"],
            ["15 ou mais", "4º grau: sucesso crítico perfeito", "4º grau: desastre total; pior consequência da cena"]
          ]
        },
        {
          "tipo": "lista",
          "titulo": "Perícias investigativas fundamentais",
          "itens": [
            "**Investigação:** Buscar pistas minuciosas, impressões digitais, gavetas de fundo falso e papéis queimados.",
            "**Percepção:** Notar cheiro acre de enxofre ou peixe podre, ouvir sussurros no sótão ou vultos nas janelas.",
            "**Intuição:** Discernir se um depoimento é sincero, se a testemunha está aterrorizada ou sob transe hipnótico.",
            "**Tratamento (Medicina Legal):** Autópsia preliminar; distinguir lacerações de faca de mordidas não-humanas.",
            "**Especialidade: Ocultismo:** Reconhecer símbolos de cultos profanos, grimórios apócrifos e círculos rituais.",
            "**Especialidade: História / Antiguidades:** Decifrar crônicas coloniais, genealogias e estatuetas de pedra negra."
          ]
        },
        {
          "tipo": "lista",
          "titulo": "Testes opostos e cooperação",
          "itens": [
            "**Teste oposto:** Os dois lados rolam; quem tirar a maior graduação de sucesso vence.",
            "**Trabalho em equipe (Ajuda):** Um aliado rola contra CD 10. Sucesso dá +2 de bônus ao líder (+5 com 3 graus de sucesso); falha por 2 graus impõe –2 de penalidade."
          ]
        }
      ]
    },
    {
      "id": "combate",
      "nome": "Combate",
      "blocos": [
        {
          "tipo": "tabela",
          "titulo": "Ações de combate",
          "colunas": ["Tipo de ação", "Exemplos nos anos 1920"],
          "linhas": [
            ["Padrão", "Disparar arma de fogo, golpear com faca ou cassetete, realizar primeiros socorros de emergência."],
            ["Movimento", "Correr até cobertura, sacar arma do coldre, subir escadaria, manobrar automóvel."],
            ["Livre", "Gritar um aviso aos companheiros, largar objeto, examinar visualmente o ambiente."],
            ["Reação", "Teste de Esquiva contra explosivos, teste de Resistência ao ser atingido."]
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Manobras de combate",
          "colunas": ["Manobra", "Ataque", "Efeito / Defesa", "Uso tático"],
          "linhas": [
            ["Ataque Acurado", "+1 ou +2", "–1 ou –2 no Dano", "Mirar em ponto vulnerável do monstro"],
            ["Ataque Defensivo", "–1 ou –2", "+1 ou +2 nas defesas ativas", "Recuar com cautela buscando abrigo"],
            ["Ataque Poderoso", "–1 ou –2", "+1 ou +2 no Dano", "Golpe com força total contra barreira"],
            ["Ataque Imprudente", "+1 ou +2", "–1 ou –2 nas defesas ativas", "Desespero absoluto para abater o alvo"],
            ["Mirar", "Gasta ação de mov.", "+2 de ataque (+5 se gastar rodada)", "Tiro de fuzil Springfield com apoio"]
          ]
        },
        {
          "tipo": "lista",
          "titulo": "Regras de armas de fogo e tiroteios",
          "itens": [
            "**Revólveres e Pistolas:** Alcances de 15 m (curto), 30 m (médio) e 60 m (longo). Ágeis em corredores e becos.",
            "**Escopeta calibre 12:** Dano 5 à distância. A curta distância (até 7,5 m), causa estrago devastador.",
            "**Thompson .45 (Submetralhadora):** Multiataque (+2 de Dano com 2 graus de acerto, +5 com 3 graus de acerto contra um alvo; ou rajada espalhada em área).",
            "**Dinamite:** Dano 5 em área de explosão; Esquiva CD 15 para sofrer metade do dano.",
            "**Cobertura:** Parcial (+2 na Esquiva) atrás de postes e caixotes; Total (+5 na Esquiva e Resistência do obstáculo) atrás de blocos de motor ou muros de alvenaria."
          ]
        },
        {
          "tipo": "lista",
          "titulo": "Iniciativa e capangas",
          "itens": [
            "**Iniciativa** = d20 + Agilidade + vantagens (Iniciativa Aprimorada dá +4).",
            "**Surpresa:** Se um lado não percebe a emboscada, fica Indefeso durante a primeira rodada e não age.",
            "**Cultistas e Capangas:** Não fazem acertos críticos contra investigadores; qualquer falha num salvamento aplica o pior grau da consequência."
          ]
        }
      ]
    },
    {
      "id": "condicoes",
      "nome": "Condições",
      "blocos": [
        {
          "tipo": "tabela",
          "titulo": "Dano e salvamentos de Resistência",
          "colunas": ["Falha por", "Grau", "Efeito na vítima"],
          "linhas": [
            ["1 a 4", "1º grau", "Machucado: –1 cumulativo em futuros testes de Resistência contra Dano."],
            ["5 a 9", "2º grau", "Machucado e Atordoado (perde a próxima ação)."],
            ["10 a 14", "3º grau", "Machucado e Cambaleando (limitado a uma única ação padrão ou de movimento)."],
            ["15 ou mais", "4º grau", "Incapacitado (desacordado, indefeso e incapaz de agir). Se o dano for letal: Moribundo."]
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Aflição e choque",
          "colunas": ["Grau de falha", "Exemplos mentais", "Exemplos físicos"],
          "linhas": [
            ["1º grau", "Transe, Confuso ou Prejudicado", "Lentidão, Desatento ou Vulnerável"],
            ["2º grau", "Compelido, Histérico ou Indefeso", "Impedido, Atordoado ou Imóvel"],
            ["3º grau", "Controlado, Em Pânico ou Em Choque", "Incapacitado, Paralisado ou Inconsciente"]
          ]
        },
        {
          "tipo": "lista",
          "titulo": "Moribundo e estabilização",
          "itens": [
            "**Estado Moribundo:** Rola Fortitude CD 15 a cada rodada. Falha piora a condição; 3 falhas causam a morte.",
            "**Primeiros Socorros:** Aliado com perícia Tratamento e maleta médica estabiliza o ferido com teste CD 15.",
            "**Cirurgia e Repouso:** Cada dia de descanso completo em hospital ou sob cuidados médicos recupera 1 grau de ferimento."
          ]
        }
      ]
    },
    {
      "id": "sanidade",
      "nome": "Sanidade & Horror",
      "blocos": [
        {
          "tipo": "tabela",
          "titulo": "Perda típica de Sanidade por horror",
          "colunas": ["Encontro ou Manifestação", "Sucesso", "Fracasso", "Máx. da Espécie"],
          "linhas": [
            ["Cadáver grotescamente mutilado", "0", "1D4", "4"],
            ["Presenciar ritual com sacrifício humano", "0", "1D6", "6"],
            ["Carniçal (Ghoul) ou Profundo (Deep One)", "0", "1D6", "6"],
            ["Mi-Go (Fungo alienígena de Yuggoth)", "0", "1D6", "6"],
            ["Criatura Insubstancial / Poltergeist", "1", "1D8", "8"],
            ["Shoggoth ou Cria Estelar de Cthulhu", "1D6", "1D20", "20"],
            ["Avatar de Nyarlathotep ou Cthulhu", "1D10", "1D100", "100"],
            ["Descobrir que parente ou amigo é um monstro", "1", "1D10", "10"]
          ],
          "nota": "Regra de acostumar-se: após sofrer a perda máxima listada para uma espécie, o investigador não perde mais Sanidade contra ela."
        },
        {
          "tipo": "formulas",
          "titulo": "Mecânica do Teste de Sanidade (d100)",
          "itens": [
            "**Teste:** Rola d100 contra a **Sanidade Atual**. Rolar ≤ SAN é sucesso; > SAN é fracasso.",
            "**01:** Sempre Sucesso Crítico (perde zero ou o mínimo absoluto).",
            "**100:** Sempre Desastre (perde o valor máximo da rolagem de dano mental).",
            "**SAN < 50:** Com Sanidade abaixo de 50, rolagens de **96 a 100** tornam-se Desastres automáticos."
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Acessos de loucura imediata (1d10)",
          "colunas": ["d10", "Surto", "Efeito na mesa"],
          "linhas": [
            ["1", "Amnésia", "Esquece sua identidade e como foi parar no local; atordoado por 1 rodada."],
            ["2", "Catatonia", "Desmaia ou congela imóvel em estado de torpor por 1d10 rodadas."],
            ["3", "Pânico", "Larga o que estiver nas mãos e corre aos berros para a direção oposta."],
            ["4", "Histeria", "Risos incontroláveis ou gritos agudos; não consegue comunicar-se nem mirar."],
            ["5", "Alucinações", "Vê paredes derretendo e monstros onde só há sombras; –2 em testes."],
            ["6", "Paranoia", "Passa a crer que um dos aliados é um cultista traidor; recusa ajuda."],
            ["7", "Fúria Cega", "Ataca descontroladamente a pessoa ou criatura mais próxima com o que tiver."],
            ["8", "Ecolalia", "Repete frases desconexas ou profanas em voz alta sem parar."],
            ["9", "Fobia Súbita", "Ganha fobia aguda de algo no ambiente (água, sangue, insetos, altura)."],
            ["10", "Fascínio Mórbido", "Aproxima-se da abominação em transe reverente; fica Indefeso."]
          ],
          "nota": "Duração: 1d10 rodadas em combate ou 1d10 horas fora de combate."
        },
        {
          "tipo": "lista",
          "titulo": "Colapso e recuperação",
          "itens": [
            "**Insanidade Temporária (Perda ≥ 5 num teste):** Teste de Intelecto d20 + INT vs CD 10. Se passar, compreende a verdade e entra em surto.",
            "**Insanidade Indefinida (Perda diária ≥ 20%):** Se perder 1/5 da SAN do início do dia, entra em colapso por 1d6 meses e adquire fobia ou mania permanente.",
            "**Insanidade Permanente (SAN = 0):** A mente colapsa de forma irreversível; o personagem torna-se um NPC do Mestre.",
            "**Tratamento e Psicanálise:** Sessão semanal de Tratamento CD 15 recupera 1d3 de Sanidade. Falha crítica custa 1d3 de SAN ao terapeuta."
          ]
        }
      ]
    },
    {
      "id": "viagem",
      "nome": "Viagem",
      "blocos": [
        {
          "tipo": "formulas",
          "titulo": "Fórmulas de locomoção",
          "itens": [
            "**Tempo** = graduação de distância – graduação de Velocidade",
            "**Distância** = graduação de velocidade + graduação de tempo",
            "**Ritmo normal a pé:** 5 km/h, cerca de 38 km por dia de marcha contínua de 8 horas."
          ]
        },
        {
          "tipo": "gerado",
          "fonte": "tempo_de_viagem"
        },
        {
          "tipo": "gerado",
          "fonte": "montarias"
        },
        {
          "tipo": "gerado",
          "fonte": "carga"
        },
        {
          "tipo": "tabela",
          "titulo": "Trens e viagens na Nova Inglaterra (anos 20)",
          "colunas": ["Trecho / Rota", "Meio de transporte", "Tempo estimado", "Preço passagem"],
          "linhas": [
            ["Boston a Arkham", "Trem expresso de passageiros", "1 hora e meia", "$1,50"],
            ["Arkham a Innsmouth", "Ônibus rural decrépito de Joe Sargent", "1 hora", "$0,75"],
            ["Arkham a Kingsport", "Trem local ou automóvel", "45 minutos", "$0,80"],
            ["Arkham a Dunwich", "Estrada de terra esburacada (carro)", "3 horas", "$2,00 (gasolina)"],
            ["Boston a New York", "Linha férrea principal interestadual", "5 horas", "$6,00"],
            ["New York a Liverpool", "Transatlântico a vapor (classe turística)", "6 a 7 dias", "$100,00"]
          ]
        }
      ]
    },
    {
      "id": "perigos",
      "nome": "Perigos",
      "blocos": [
        {
          "tipo": "gerado",
          "fonte": "queda"
        },
        {
          "tipo": "tabela",
          "titulo": "Fogo, calor e explosivos",
          "colunas": ["Perigo", "Dano por rodada", "Resistência", "Efeito adicional"],
          "linhas": [
            ["Tocha ou vela", "Dano 1", "CD 16", "Pode inflamar roupas de algodão"],
            ["Fogueira ou fogão a carvão", "Dano 3", "CD 18", "Queimadura de 2º grau"],
            ["Prédio em chamas / Incêndio", "Dano 5", "CD 20", "Fumaça densa: asfixia CD 15"],
            ["Banana de Dinamite (1 unidade)", "Dano 5 em área", "CD 20", "Esquiva CD 15 reduz para metade"],
            ["Caixa de Dinamite (10 bananas)", "Dano 10 em área", "CD 25", "Desabamento de criptas e paredes"]
          ]
        },
        {
          "tipo": "lista",
          "titulo": "Luz, penumbra e escuridão",
          "itens": [
            "**Farol de automóvel:** Ilumina cone de 30 metros à frente com luz plena.",
            "**Lanterna elétrica:** Ilumina raio de 9 metros (6 quadrados); funciona sob chuva moderada.",
            "**Tocha ou lampião de querosene:** Ilumina raio de 4,5 metros de luz plena e mais 4,5 m de penumbra.",
            "**Fósforo ou isqueiro:** Luz tênue em raio de 1,5 metro (permite ler uma página ou destrancar fechadura).",
            "**Penumbra:** Camuflagem parcial (–2 nos ataques visuais à distância).",
            "**Escuridão total:** Camuflagem total (–5 no ataque; alvos ficam Indefesos contra ataques das sombras)."
          ]
        },
        {
          "tipo": "gerado",
          "fonte": "medidas"
        }
      ]
    },
    {
      "id": "cidade",
      "nome": "Cidade & Serviços (1920)",
      "blocos": [
        {
          "tipo": "tabela",
          "titulo": "Serviços e comunicações da época",
          "colunas": ["Serviço", "Custo médio", "Tempo de resposta / Observações"],
          "linhas": [
            ["Telegrama Western Union", "$0,05 por palavra", "Entregue em poucas horas na cidade"],
            ["Telefonema interurbano", "$5,00 por 3 min", "Operadora conecta cabos manualmente"],
            ["Carta por correio expresso", "$0,02", "1 a 2 dias entre cidades do mesmo estado"],
            ["Diária em hotel de luxo (Boston)", "$8,00 a $12,00", "Quarto amplo, serviço de quarto e telefone"],
            ["Diária em hotel médio (Arkham)", "$2,50", "Cama confortável e banho no corredor"],
            ["Pensão barata em cortiço", "$0,75 por noite", "Bairro operário de imigrantes; sem registro"],
            ["Refeição completa em restaurante", "$0,50 a $1,00", "Café, bife e torta em diner de esquina"],
            ["Garrafa de uísque ilegal (speakeasy)", "$3,00 a $5,00", "Contrabando da máfia sob a Lei Seca"]
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Instituições e arquivos investigativos",
          "colunas": ["Local", "O que pesquisar", "Requisito de acesso"],
          "linhas": [
            ["Universidade Miskatonic", "Tomos raros, história colonial, química", "Credencial acadêmica ou persuasão"],
            ["Redação do Arkham Advertiser", "Arquivos de notícias antigas e óbitos", "Contato jornalístico ou gorjeta ao arquivista"],
            ["Cartório Municipal de Arkham", "Escrituras de imóveis e testamentos", "Taxa pública de $0,50 por busca"],
            ["Necrotério Municipal de Boston", "Autópsias e relatórios de legistas", "Autoridade policial ou suborno de $2,00"],
            ["Sanatório Estadual de Danvers", "Prontuários psiquiátricos e pacientes", "Autorização judicial ou visita médica"]
          ]
        },
        {
          "tipo": "tabela",
          "titulo": "Honorários e serviços profissionais",
          "colunas": ["Profissional", "Honorário", "Serviço padrão"],
          "linhas": [
            ["Consulta com médico particular", "$3,00", "Visita domiciliar e prescrição de sedativos"],
            ["Internação em sanatório particular", "$15,00 por dia", "Acomodação reservada e vigilância médica"],
            ["Detetive particular diarista", "$10,00 por dia", "Vigilância discreta e campanas na cidade"],
            ["Advogado criminalista (defesa)", "$50,00 a $200,00", "Audiência de fiança e representação judicial"],
            ["Mecânico de automóveis", "$2,00 a $5,00", "Conserto de motor, troca de pneus e correias"]
          ]
        }
      ]
    }
  ]
}

DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(json.dumps(escudo_cthulhu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Gravado {DESTINO}")
