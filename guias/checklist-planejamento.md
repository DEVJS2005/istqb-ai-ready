---
tipo: "guia"
titulo: "Checklist de planejamento de teste"
baseado_em: ["1.4.1", "1.4.2", "2.1.5", "2.2.1", "2.2.2", "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5", "5.1.6", "5.1.7", "5.2.2", "5.2.3", "5.2.4", "5.3.1", "5.3.2", "5.4", "5.5"]
autoria: "mantenedores do istqb-ai-ready (interpretação, não é texto do syllabus)"
---

# Checklist de planejamento de teste

> **Guia nosso.** Checklist prático montado a partir do syllabus, não é texto do ISTQB. Entre
> colchetes, a seção do syllabus onde está o conceito.

Use no início de um projeto, release ou iteração. Itens que não se aplicam devem ser marcados como
"N/A" e justificados, sem apagar.

## 1. Contexto [1.4.2] [5.1.1]
- [ ] Objeto de teste e escopo definidos (o que **está** e o que **não está** no escopo).
- [ ] Objetivos de teste escritos e ligados ao negócio [1.1.1].
- [ ] Base de teste identificada (requisitos, user stories, contratos, regras).
- [ ] Stakeholders e papéis definidos: gestão de teste e teste [1.4.5].
- [ ] Ciclo de vida (sequencial, iterativo, ágil, DevOps) e o que isso muda no teste [2.1.1].
- [ ] Premissas e restrições registradas (prazo, orçamento, ambientes, pessoas).

## 2. Riscos [5.2]
- [ ] Riscos de **produto** identificados com o time (brainstorming, workshop) [5.2.3].
- [ ] Riscos de **projeto** identificados: organização, pessoas, técnica, fornecedores [5.2.2].
- [ ] Cada risco tem probabilidade, impacto e nível (matriz ou probabilidade × impacto) [5.2.1].
- [ ] Resposta definida para cada risco alto: mitigar pelo teste, aceitar, transferir ou contingência [5.2.4].
- [ ] Os riscos estão no registro de riscos do plano.

## 3. Abordagem [5.1.1]
- [ ] Níveis de teste escolhidos: componente, integração, sistema, integração de sistemas, aceite [2.2.1].
- [ ] Tipos de teste: funcional, não funcional (quais características da ISO 25010?), caixa-preta, caixa-branca [2.2.2].
- [ ] Técnicas por área de risco (ver [guia de técnicas caixa-preta](tecnicas-caixa-preta.md)) [4].
- [ ] Meta de cobertura definida por técnica ou por nível.
- [ ] Grau de independência adequado ao risco [1.5.3].
- [ ] Estratégia de automação com a pirâmide de teste como referência [5.1.6] e os quadrantes conferidos [5.1.7].
- [ ] Práticas de shift left: revisão de requisitos, análise estática, testes na CI [2.1.5] [3.1].
- [ ] Estratégia de regressão e de confirmação [2.2.3].

## 4. Critérios [5.1.3]
- [ ] Critérios de **entrada** por nível ou atividade (ambiente pronto, build estável, smoke ok).
- [ ] Critérios de **saída** mensuráveis (cobertura, defeitos abertos por severidade, testes executados).
- [ ] Definition of Ready e Definition of Done acordadas, se for ágil.
- [ ] Combinado o que fazer se tempo ou verba acabarem: quem aceita o risco residual.

## 5. Estimativa e cronograma [5.1.4] [5.1.5]
- [ ] Estimativa feita com técnica explícita: razões, extrapolação, Wideband Delphi/Planning Poker ou três pontos.
- [ ] Premissas da estimativa registradas, com a margem de erro comunicada.
- [ ] Tarefas grandes decompostas antes de estimar.
- [ ] Ordem de execução priorizada (por risco, cobertura ou requisitos), respeitando dependências e recursos.

## 6. Ambiente, dados e ferramentas [1.4.3] [6.1]
- [ ] Requisitos do ambiente de teste (stubs, drivers, simuladores, virtualização de serviços).
- [ ] Requisitos de dados de teste, incluindo massa, anonimização e reset.
- [ ] Ferramentas definidas: gestão, execução, cobertura, CI/CD e defeitos.
- [ ] Gestão de configuração dos itens de teste: versão do objeto, dos scripts e do ambiente [5.4].

## 7. Monitoramento, comunicação e defeitos [5.3] [5.5]
- [ ] Métricas que serão coletadas [5.3.1].
- [ ] Formato e frequência do relatório de progresso e do relatório de conclusão, e quem recebe [5.3.2] [5.3.3].
- [ ] Fluxo de defeitos (estados, severidade, prioridade, quem triagem) e modelo de relatório [5.5].
- [ ] Rastreabilidade de requisitos ↔ casos ↔ resultados ↔ defeitos [1.4.4].

## 8. Encerramento [1.4.1] [2.1.6]
- [ ] Marco de conclusão definido (fim de iteração, release, nível).
- [ ] Retrospectiva agendada, com lições registradas no relatório de conclusão.
- [ ] Testware a arquivar ou entregar, e ambiente a desligar.

[1.1.1]: ../syllabus/01-fundamentals-of-testing/1.1.1-test-objectives.md
[1.4.1]: ../syllabus/01-fundamentals-of-testing/1.4.1-test-activities-and-tasks.md
[1.4.2]: ../syllabus/01-fundamentals-of-testing/1.4.2-test-process-in-context.md
[1.4.3]: ../syllabus/01-fundamentals-of-testing/1.4.3-testware.md
[1.4.4]: ../syllabus/01-fundamentals-of-testing/1.4.4-traceability-between-the-test-basis-and-testware.md
[1.4.5]: ../syllabus/01-fundamentals-of-testing/1.4.5-roles-in-testing.md
[1.5.3]: ../syllabus/01-fundamentals-of-testing/1.5.3-independence-of-testing.md
[2.1.1]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.1-impact-of-the-software-development-lifecycle-on-testing.md
[2.1.5]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.5-shift-left.md
[2.1.6]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.6-retrospectives-and-process-improvement.md
[2.2.1]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.2.1-test-levels.md
[2.2.2]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.2.2-test-types.md
[2.2.3]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.2.3-confirmation-testing-and-regression-testing.md
[3.1]: ../syllabus/03-static-testing/3.1-static-testing-basics.md
[4]: ../syllabus/04-test-analysis-and-design/_index.md
[5.1.1]: ../syllabus/05-managing-the-test-activities/5.1.1-purpose-and-content-of-a-test-plan.md
[5.1.3]: ../syllabus/05-managing-the-test-activities/5.1.3-entry-criteria-and-exit-criteria.md
[5.1.4]: ../syllabus/05-managing-the-test-activities/5.1.4-estimation-techniques.md
[5.1.5]: ../syllabus/05-managing-the-test-activities/5.1.5-test-case-prioritization.md
[5.1.6]: ../syllabus/05-managing-the-test-activities/5.1.6-test-pyramid.md
[5.1.7]: ../syllabus/05-managing-the-test-activities/5.1.7-testing-quadrants.md
[5.2]: ../syllabus/05-managing-the-test-activities/5.2-risk-management.md
[5.2.1]: ../syllabus/05-managing-the-test-activities/5.2.1-risk-definition-and-risk-attributes.md
[5.2.2]: ../syllabus/05-managing-the-test-activities/5.2.2-project-risks-and-product-risks.md
[5.2.3]: ../syllabus/05-managing-the-test-activities/5.2.3-product-risk-analysis.md
[5.2.4]: ../syllabus/05-managing-the-test-activities/5.2.4-product-risk-control.md
[5.3]: ../syllabus/05-managing-the-test-activities/5.3-test-monitoring-test-control-and-test-completion.md
[5.3.1]: ../syllabus/05-managing-the-test-activities/5.3.1-metrics-used-in-testing.md
[5.3.2]: ../syllabus/05-managing-the-test-activities/5.3.2-purpose-content-and-audience-for-test-reports.md
[5.3.3]: ../syllabus/05-managing-the-test-activities/5.3.3-communicating-the-status-of-testing.md
[5.4]: ../syllabus/05-managing-the-test-activities/5.4-configuration-management.md
[5.5]: ../syllabus/05-managing-the-test-activities/5.5-defect-management.md
[6.1]: ../syllabus/06-test-tools/6.1-tool-support-for-testing.md
