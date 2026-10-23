# Fichas Marvel — conversao de M&M 2e para 3e

As fichas individuais em `fichas/` partem dos perfis do PDF `mutants-masterminds-marvel-files-pr_e5850f76d9cea8b6721dc9f1fe9fe08e.pdf` e seguem as orientacoes de `conversor 2e para a 3e.pdf`.

## Como ler os arquivos

- `edicao_origem`, `edicao_destino`, `fonte` e `pontos_poder_origem` identificam o perfil impresso.
- `ficha.habilidades` usa as abreviacoes do projeto (`For`, `Vig`, `Agi`, `Des`, `Lut`, `Int`, `Pro`, `Pre`); `defesas` registra os valores finais de 3e.
- Pericias, vantagens, poderes, equipamento e complicacoes estao separados para que equivalencias e itens removidos nao se misturem.
- `validacao_np` registra ataque + efeito e os limites defensivos de 3e: Esquiva + Resistencia, Aparar + Resistencia e Fortitude + Vontade.
- `pontos_poder_3e` so e preenchido quando os custos conhecidos podem ser somados sem adivinhar poderes ou modificadores; fichas parcialmente calculadas trazem um subtotal discriminado.
- Nomes de vantagens e efeitos permanecem em ingles quando essa e a designacao mecanica da fonte; explicacoes e notas estao em portugues.
- Para pericias, Drive e Pilot viram `Veículos`; Survival vira `Especialidade: Sobrevivência`. Preserve pericias diferentes quando a fonte distingue usos: Computers vira `Tecnologia`, enquanto Knowledge (Technology) vira `Especialidade: Tecnologia`; nao eliminar esta ultima como redundante sem verificar o significado original.

Estas sao conversoes de trabalho, nao fichas oficiais de 3e. As notas identificam escolhas de conversao e ajustes de legalidade para revisao do Mestre. Os perfis sao NPCs/personagens publicados: a regra de duas complicacoes, incluindo Motivacao, e para personagens jogadores; complicacoes nao sao inventadas quando a fonte nao as informa.

Ao adaptar uma ficha como personagem jogador, registrar as complicacoes explicitamente publicadas e completar Motivacao e outra complicacao apenas quando a campanha exigir; propostas nao presentes na fonte devem ser identificadas como sugestoes, nao como fatos canonicos.

## Progresso

Este conjunto cobre 116 perfis, um por pagina, das paginas 2 a 117 do PDF de personagens; a pagina 1 nao contem perfil. Todos os perfis identificados no livro foram convertidos e nao restam perfis pendentes. Os 116 arquivos JSON foram validados quanto a sintaxe e cobertura das paginas.

Os custos totais em PP de 3e permanecem pendentes quando poderes ou modificadores nao puderam ser determinados com seguranca; esses casos estao marcados nas fichas e nao foram estimados. O NP publicado e os PP convertidos sao informacoes distintas: personagens podem ultrapassar o orcamento padrao de criacao de 15 PP por NP.
