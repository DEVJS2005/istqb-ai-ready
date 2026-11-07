---
tipo: "guia"
titulo: "Técnicas caixa-preta na prática"
baseado_em: ["4.1", "4.2", "4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.4.1", "4.5.2", "5.1.5"]
autoria: "mantenedores do istqb-ai-ready (interpretação, não é texto do syllabus)"
---

# Técnicas caixa-preta na prática

> **Guia nosso.** Interpretação e aplicação prática, não é texto do ISTQB. Os conceitos vêm das
> seções citadas entre colchetes, e para a definição exata consulte o syllabus.

## 1. Qual técnica usar

| Situação na especificação | Técnica | Syllabus |
|---|---|---|
| Faixas ou categorias de valores tratados da mesma forma | Particionamento de equivalência (EP) | [4.2.1] |
| Faixas **ordenadas** com limites (idade, valor, data, tamanho) | Análise de valor limite (BVA) | [4.2.2] |
| Regra de negócio com várias condições combinadas | Tabela de decisão | [4.2.3] |
| Comportamento que depende do estado atual (status, fluxo, sessão) | Transição de estados | [4.2.4] |
| Especificação fraca ou histórico de defeitos conhecido | Complementar com suposição de erro | [4.4.1] |

As técnicas se combinam. O caso mais comum é EP para achar as partições e BVA nos limites
das partições ordenadas.

## 2. Particionamento de equivalência [4.2.1]

1. Para **cada** dado relevante (entrada, saída, configuração, tempo, interface), liste as partições.
2. Separe as **válidas** das **inválidas**. Confira se nenhuma se sobrepõe e se nenhuma está vazia.
3. Escreva **um** caso por partição. As inválidas também contam para a cobertura.
4. Cobertura = partições exercitadas ÷ partições identificadas.
5. Com vários campos, o mínimo é **Each Choice**: cada partição de cada campo aparece em ao menos um caso.
   Combine **uma** partição inválida por caso, para um erro não esconder outro.

**Exemplo nosso:** campo "quantidade" aceita de 1 a 99.
- Válida: 1..99
- Inválidas: ≤ 0; ≥ 100; não numérico; vazio
- Casos (EP): 50, 0, 150, "abc", vazio

## 3. Análise de valor limite [4.2.2]

Só vale para partições **ordenadas**. Para o mesmo campo (1..99):

| Versão | Itens por limite | Valores de teste |
|---|---|---|
| BVA de 2 valores | limite + vizinho da partição adjacente | 0, 1, 99, 100 |
| BVA de 3 valores | limite + os dois vizinhos | 0, 1, 2, 98, 99, 100 |

Use a de 3 valores quando o risco justificar. Ela pega erros de operador (`<` trocado por `<=`, `==` no lugar de `<=`)
que a de 2 valores pode deixar passar.

## 4. Tabela de decisão [4.2.3]

1. Liste as **condições** (linhas de cima) e as **ações** (linhas de baixo).
2. Gere as colunas (regras). Com *n* condições booleanas, são até 2ⁿ.
3. Marque as colunas inviáveis (N/A) e remova-as. Junte as colunas em que uma condição não importa (–).
4. Um caso de teste por coluna viável. Cobertura = colunas exercitadas ÷ colunas viáveis.
5. Se a tabela crescer demais, minimize ou priorize por risco [5.1.5].

**Exemplo nosso:** frete grátis se "cliente premium" **ou** "pedido ≥ R$ 200", exceto para "região remota".

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Premium | T | – | F | – |
| Pedido ≥ 200 | – | T | F | – |
| Região remota | F | F | F | T |
| **Frete grátis** | X | X | | |

Revisar a tabela costuma revelar lacunas na regra, como "região remota premium paga frete?". Leve essas dúvidas ao
refinamento antes de testar.

## 5. Transição de estados [4.2.4]

1. Desenhe o diagrama: estados, eventos, `[condição de guarda]` e `/ação`.
2. Monte a **tabela de estados**. As células vazias são as transições inválidas.
3. Escolha o critério:
   - **todos os estados**: o mais fraco;
   - **transições válidas (0-switch)**: o padrão de mercado;
   - **todas as transições**: inclui tentar as inválidas, uma por caso. É o mínimo para sistemas críticos.

**Exemplo nosso:** pedido `Criado → Pago → Enviado → Entregue`, com `Cancelado` a partir de Criado ou Pago.
Transições inválidas a tentar: cancelar um pedido Enviado; pagar um pedido Cancelado.

## 6. Checklist rápido de revisão dos casos

- [ ] Cada caso aponta para a técnica e o item de cobertura que exercita.
- [ ] Há casos negativos (partições inválidas, transições inválidas).
- [ ] A cobertura de cada técnica foi calculada e registrada.
- [ ] Os casos estão rastreados até o requisito ou critério de aceite [1.4.4], [4.5.2].
- [ ] Existe um resultado esperado claro para cada caso.

[4.1]: ../syllabus/04-test-analysis-and-design/4.1-test-techniques-overview.md
[4.2]: ../syllabus/04-test-analysis-and-design/4.2-black-box-test-techniques.md
[4.2.1]: ../syllabus/04-test-analysis-and-design/4.2.1-equivalence-partitioning.md
[4.2.2]: ../syllabus/04-test-analysis-and-design/4.2.2-boundary-value-analysis.md
[4.2.3]: ../syllabus/04-test-analysis-and-design/4.2.3-decision-table-testing.md
[4.2.4]: ../syllabus/04-test-analysis-and-design/4.2.4-state-transition-testing.md
[4.4.1]: ../syllabus/04-test-analysis-and-design/4.4.1-error-guessing.md
[4.5.2]: ../syllabus/04-test-analysis-and-design/4.5.2-acceptance-criteria.md
[5.1.5]: ../syllabus/05-managing-the-test-activities/5.1.5-test-case-prioritization.md
[1.4.4]: ../syllabus/01-fundamentals-of-testing/1.4.4-traceability-between-the-test-basis-and-testware.md
