---
type: "guide"
title: "Test plan template"
based_on: ["5.1.1", "5.1.3", "5.1.4", "5.2", "5.3.2", "5.5", "2.2.1", "2.2.2"]
authorship: "istqb-ai-ready maintainers (interpretation, not syllabus text)"
---

# Test plan template

> **Our guide.** The structure follows the typical test plan content described in the syllabus
> ([5.1.1]). The fields, prompts and examples are ours. For more detail, the syllabus points to
> ISO/IEC/IEEE 29119-3.

Copy this file into your project and fill it in. Keep the plan **short and alive**: in an agile
context, one plan per release plus notes per iteration is usually enough [5.1.2].

---

## 0. Identification
| Field | Value |
|---|---|
| Project / product | |
| Plan version | |
| Owner (test management role) | |
| Date / status | draft · in review · approved |

## 1. Test context
- **Scope (in):**
- **Scope (out), with reason:**
- **Test objectives:** which decisions will this testing support? [1.1.1]
- **Test basis:** links to requirements, user stories, rules and contracts.
- **Test object and test items:** with versions [5.4].

## 2. Assumptions and constraints
- Assumptions (e.g. "staging environment available from …"):
- Constraints (deadline, budget, people, regulatory):

## 3. Stakeholders
| Stakeholder | Role | Interest in testing | Needs training? |
|---|---|---|---|
| | | | |

## 4. Communication
| What | To whom | Frequency | Channel | Format |
|---|---|---|---|---|
| Progress report [5.3.2] | | weekly | | |
| Completion report [5.3.2] | | per release | | |
| Critical defects | | immediately | | |

## 5. Risk register [5.2]
| ID | Risk | Type (product/project) | Likelihood | Impact | Level | Response / mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R1 | | | | | | | |

## 6. Test approach
### 6.1 Levels and types [2.2.1] [2.2.2]
| Level | Types (functional / non-functional / black-box / white-box) | Owner | Automation |
|---|---|---|---|
| Component | | | |
| Component integration | | | |
| System | | | |
| System integration | | | |
| Acceptance | | | |

### 6.2 Techniques and coverage
| Area / risk | Technique [4] | Coverage target |
|---|---|---|
| | | |

### 6.3 Independence, deliverables and metrics
- Degree of independence and who tests what [1.5.3]:
- Test deliverables (testware) [1.4.3]:
- Metrics to collect [5.3.1]:

### 6.4 Test data and environment
- Test data requirements:
- Environment requirements (stubs, drivers, simulators, virtualisation):

### 6.5 Entry and exit criteria [5.1.3]
| Activity / level | Entry criteria | Exit criteria |
|---|---|---|
| | | |

### 6.6 Defects [5.5]
- Tool and state workflow:
- Severity and priority scales:
- Mandatory defect report fields:

### 6.7 Deviations from the test policy or strategy
- (if any, with reason)

## 7. Budget and schedule
- Estimation technique used and assumptions [5.1.4]:
- Estimate (with margin of error):
- Milestones:

## 8. Approval
| Name | Role | Date | Decision |
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
