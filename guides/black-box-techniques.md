---
type: "guide"
title: "Black-box techniques in practice"
based_on: ["4.1", "4.2", "4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.4.1", "4.5.2", "5.1.5"]
authorship: "istqb-ai-ready maintainers (interpretation, not syllabus text)"
---

# Black-box techniques in practice

> **Our guide.** Interpretation and practical application, not ISTQB text. The concepts come from the
> sections cited in brackets; for the exact definitions, read the syllabus.

## 1. Which technique to use

| What the specification describes | Technique | Syllabus |
|---|---|---|
| Ranges or categories of values handled the same way | Equivalence partitioning (EP) | [4.2.1] |
| **Ordered** ranges with limits (age, amount, date, length) | Boundary value analysis (BVA) | [4.2.2] |
| A business rule with several combined conditions | Decision table testing | [4.2.3] |
| Behaviour that depends on the current state (status, flow, session) | State transition testing | [4.2.4] |
| Weak specification or a known defect history | Add error guessing | [4.4.1] |

Techniques combine. The most common pairing is EP to find the partitions, then BVA on the edges
of the ordered ones.

## 2. Equivalence partitioning [4.2.1]

1. For **each** relevant data item (input, output, configuration, time, interface), list the partitions.
2. Split them into **valid** and **invalid**. Check that none overlap and none are empty.
3. Write **one** case per partition. Invalid partitions count towards coverage too.
4. Coverage = partitions exercised ÷ partitions identified.
5. With several fields, the minimum is **Each Choice**: every partition of every field appears in at least one case.
   Put only **one** invalid partition per case, so one error does not hide another.

**Our example:** a "quantity" field accepts 1 to 99.
- Valid: 1..99
- Invalid: ≤ 0; ≥ 100; non-numeric; empty
- EP cases: 50, 0, 150, "abc", empty

## 3. Boundary value analysis [4.2.2]

Only for **ordered** partitions. For the same field (1..99):

| Variant | Items per boundary | Test values |
|---|---|---|
| 2-value BVA | boundary + nearest value in the adjacent partition | 0, 1, 99, 100 |
| 3-value BVA | boundary + both neighbours | 0, 1, 2, 98, 99, 100 |

Use 3-value BVA when the risk justifies it. It catches operator mistakes (`<` swapped for `<=`, `==` instead of `<=`)
that 2-value BVA can miss.

## 4. Decision table testing [4.2.3]

1. List the **conditions** (top rows) and the **actions** (bottom rows).
2. Generate the columns (rules). With *n* Boolean conditions there are up to 2ⁿ.
3. Mark infeasible columns (N/A) and drop them. Merge columns where a condition does not matter (–).
4. One test case per feasible column. Coverage = columns exercised ÷ feasible columns.
5. If the table gets too big, minimise it or prioritise by risk [5.1.5].

**Our example:** free shipping if "premium customer" **or** "order ≥ $200", except for "remote region".

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Premium | T | – | F | – |
| Order ≥ 200 | – | T | F | – |
| Remote region | F | F | F | T |
| **Free shipping** | X | X | | |

Reviewing the table often exposes gaps in the rule, such as "does a premium customer in a remote region pay shipping?".
Take these questions to refinement before testing.

## 5. State transition testing [4.2.4]

1. Draw the diagram: states, events, `[guard condition]` and `/action`.
2. Build the **state table**. Empty cells are the invalid transitions.
3. Pick the criterion:
   - **all states**: the weakest;
   - **valid transitions (0-switch)**: the usual default;
   - **all transitions**: also attempts the invalid ones, one per case. The minimum for critical systems.

**Our example:** an order `Created → Paid → Shipped → Delivered`, with `Cancelled` reachable from Created or Paid.
Invalid transitions to attempt: cancel a Shipped order; pay a Cancelled order.

## 6. Quick review checklist for the cases

- [ ] Each case names the technique and the coverage item it exercises.
- [ ] There are negative cases (invalid partitions, invalid transitions).
- [ ] Coverage for each technique was calculated and recorded.
- [ ] Cases are traced to the requirement or acceptance criterion [1.4.4], [4.5.2].
- [ ] Every case has a clear expected result.

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
