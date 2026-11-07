---
type: "guide"
title: "Test planning checklist"
based_on: ["1.4.1", "1.4.2", "2.1.5", "2.2.1", "2.2.2", "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5", "5.1.6", "5.1.7", "5.2.2", "5.2.3", "5.2.4", "5.3.1", "5.3.2", "5.4", "5.5"]
authorship: "istqb-ai-ready maintainers (interpretation, not syllabus text)"
---

# Test planning checklist

> **Our guide.** A practical checklist built from the syllabus, not ISTQB text. The syllabus
> section behind each concept is shown in brackets.

Use it at the start of a project, release or iteration. Mark items that do not apply as "N/A" with a
reason instead of deleting them.

## 1. Context [1.4.2] [5.1.1]
- [ ] Test object and scope defined (what **is** and what **is not** in scope).
- [ ] Test objectives written down and linked to the business [1.1.1].
- [ ] Test basis identified (requirements, user stories, contracts, rules).
- [ ] Stakeholders and roles defined: test management and testing [1.4.5].
- [ ] Lifecycle (sequential, iterative, agile, DevOps) and what it changes for testing [2.1.1].
- [ ] Assumptions and constraints recorded (deadline, budget, environments, people).

## 2. Risks [5.2]
- [ ] **Product** risks identified with the team (brainstorming, workshop) [5.2.3].
- [ ] **Project** risks identified: organisation, people, technical, suppliers [5.2.2].
- [ ] Each risk has likelihood, impact and level (matrix or likelihood × impact) [5.2.1].
- [ ] A response defined for each high risk: mitigate through testing, accept, transfer or contingency [5.2.4].
- [ ] Risks are in the plan's risk register.

## 3. Approach [5.1.1]
- [ ] Test levels chosen: component, integration, system, system integration, acceptance [2.2.1].
- [ ] Test types: functional, non-functional (which ISO 25010 characteristics?), black-box, white-box [2.2.2].
- [ ] Techniques per risk area (see the [black-box techniques guide](black-box-techniques.md)) [4].
- [ ] Coverage target defined per technique or per level.
- [ ] Degree of independence suited to the risk [1.5.3].
- [ ] Automation strategy using the test pyramid as a reference [5.1.6], with the quadrants checked [5.1.7].
- [ ] Shift-left practices: requirement reviews, static analysis, tests in CI [2.1.5] [3.1].
- [ ] Regression and confirmation strategy [2.2.3].

## 4. Criteria [5.1.3]
- [ ] **Entry** criteria per level or activity (environment ready, stable build, smoke passing).
- [ ] Measurable **exit** criteria (coverage, open defects by severity, tests executed).
- [ ] Definition of Ready and Definition of Done agreed, if agile.
- [ ] Agreed what happens if time or budget runs out: who accepts the residual risk.

## 5. Estimation and schedule [5.1.4] [5.1.5]
- [ ] Estimate made with an explicit technique: ratios, extrapolation, Wideband Delphi/Planning Poker or three-point.
- [ ] Estimate assumptions recorded, with the margin of error communicated.
- [ ] Large tasks broken down before estimating.
- [ ] Execution order prioritised (by risk, coverage or requirements), respecting dependencies and resources.

## 6. Environment, data and tools [1.4.3] [6.1]
- [ ] Test environment requirements (stubs, drivers, simulators, service virtualisation).
- [ ] Test data requirements, including volume, anonymisation and reset.
- [ ] Tools defined: management, execution, coverage, CI/CD and defects.
- [ ] Configuration management of test items: versions of the test object, scripts and environment [5.4].

## 7. Monitoring, communication and defects [5.3] [5.5]
- [ ] Metrics to collect [5.3.1].
- [ ] Format and frequency of the progress report and the completion report, and who receives them [5.3.2] [5.3.3].
- [ ] Defect workflow (states, severity, priority, who triages) and report template [5.5].
- [ ] Traceability requirements ↔ cases ↔ results ↔ defects [1.4.4].

## 8. Closure [1.4.1] [2.1.6]
- [ ] Completion milestone defined (end of iteration, release, level).
- [ ] Retrospective scheduled, with lessons recorded in the completion report.
- [ ] Testware to archive or hand over, and environment to shut down.

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
