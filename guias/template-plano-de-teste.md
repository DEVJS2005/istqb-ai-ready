---
tipo: "guia"
titulo: "Template de plano de teste"
baseado_em: ["5.1.1", "5.1.3", "5.1.4", "5.2", "5.3.2", "5.5", "2.2.1", "2.2.2"]
autoria: "mantenedores do istqb-ai-ready (interpretação, não é texto do syllabus)"
---

# Template de plano de teste

> **Guia nosso.** A estrutura segue o conteúdo típico de um plano de teste descrito no syllabus
> ([5.1.1]). Os campos, as perguntas e os exemplos são nossos. Para mais detalhes, o syllabus remete
> à ISO/IEC/IEEE 29119-3.

Copie este arquivo para o seu projeto e preencha. Mantenha o plano **curto e vivo**: em contexto
ágil, um plano por release e notas por iteração costumam bastar [5.1.2].

---

## 0. Identificação
| Campo | Valor |
|---|---|
| Projeto / produto | |
| Versão do plano | |
| Responsável (papel de gestão de teste) | |
| Data / status | rascunho · em revisão · aprovado |

## 1. Contexto do teste
- **Escopo (dentro):**
- **Escopo (fora), com justificativa:**
- **Objetivos de teste:** quais decisões este teste vai apoiar? [1.1.1]
- **Base de teste:** links para requisitos, user stories, regras e contratos.
- **Objeto de teste e itens de teste:** com versões [5.4].

## 2. Premissas e restrições
- Premissas (ex.: "ambiente de homologação disponível a partir de …"):
- Restrições (prazo, orçamento, pessoas, regulatório):

## 3. Stakeholders
| Stakeholder | Papel | Interesse no teste | Precisa de treinamento? |
|---|---|---|---|
| | | | |

## 4. Comunicação
| O quê | Para quem | Frequência | Canal | Formato |
|---|---|---|---|---|
| Relatório de progresso [5.3.2] | | semanal | | |
| Relatório de conclusão [5.3.2] | | por release | | |
| Defeitos críticos | | imediato | | |

## 5. Registro de riscos [5.2]
| ID | Risco | Tipo (produto/projeto) | Probabilidade | Impacto | Nível | Resposta / mitigação | Dono |
|---|---|---|---|---|---|---|---|
| R1 | | | | | | | |

## 6. Abordagem de teste
### 6.1 Níveis e tipos [2.2.1] [2.2.2]
| Nível | Tipos (funcional / não funcional / caixa-preta / caixa-branca) | Responsável | Automação |
|---|---|---|---|
| Componente | | | |
| Integração de componentes | | | |
| Sistema | | | |
| Integração de sistemas | | | |
| Aceite | | | |

### 6.2 Técnicas e cobertura
| Área / risco | Técnica [4] | Meta de cobertura |
|---|---|---|
| | | |

### 6.3 Independência, entregáveis e métricas
- Grau de independência e quem testa o quê [1.5.3]:
- Entregáveis de teste (testware) [1.4.3]:
- Métricas a coletar [5.3.1]:

### 6.4 Dados e ambiente de teste
- Requisitos de dados de teste:
- Requisitos de ambiente (stubs, drivers, simuladores, virtualização):

### 6.5 Critérios de entrada e saída [5.1.3]
| Atividade / nível | Critérios de entrada | Critérios de saída |
|---|---|---|
| | | |

### 6.6 Defeitos [5.5]
- Ferramenta e fluxo de estados:
- Escala de severidade e de prioridade:
- Campos obrigatórios do relatório de defeito:

### 6.7 Desvios da política ou estratégia de teste
- (se houver, com justificativa)

## 7. Orçamento e cronograma
- Técnica de estimativa usada e premissas [5.1.4]:
- Estimativa (com margem de erro):
- Marcos:

## 8. Aprovação
| Nome | Papel | Data | Decisão |
|---|---|---|---|
| | | | |

[1.1.1]: ../syllabus/01-fundamentals-of-testing/1.1.1-test-objectives.md
[1.4.3]: ../syllabus/01-fundamentals-of-testing/1.4.3-testware.md
[1.5.3]: ../syllabus/01-fundamentals-of-testing/1.5.3-independence-of-testing.md
[2.2.1]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.2.1-test-levels.md
[2.2.2]: ../syllabus/02-testing-throughout-the-software-development-lifecycle/2.2.2-test-types.md
[4]: ../syllabus/04-test-analysis-and-design/_index.md
[5.1.1]: ../syllabus/05-managing-the-test-activities/5.1.1-purpose-and-content-of-a-test-plan.md
[5.1.2]: ../syllabus/05-managing-the-test-activities/5.1.2-testers-contribution-to-iteration-and-release-planning.md
[5.1.3]: ../syllabus/05-managing-the-test-activities/5.1.3-entry-criteria-and-exit-criteria.md
[5.1.4]: ../syllabus/05-managing-the-test-activities/5.1.4-estimation-techniques.md
[5.2]: ../syllabus/05-managing-the-test-activities/5.2-risk-management.md
[5.3.1]: ../syllabus/05-managing-the-test-activities/5.3.1-metrics-used-in-testing.md
[5.3.2]: ../syllabus/05-managing-the-test-activities/5.3.2-purpose-content-and-audience-for-test-reports.md
[5.4]: ../syllabus/05-managing-the-test-activities/5.4-configuration-management.md
[5.5]: ../syllabus/05-managing-the-test-activities/5.5-defect-management.md
