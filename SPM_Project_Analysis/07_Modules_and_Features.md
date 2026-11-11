# Chapter 5 support: Modules and Features

## Module inventory

| Module | Verified capability | Boundaries / status |
|---|---|---|
| Project charter and lifecycle | Store charter, management-plan text, status, status history, milestones, closure | Implemented; no approval identity or multi-user controls |
| Scope and requirements | Create/propose/edit/approve/reject requirements; priority and source | Implemented for project requirements, not healthcare service behavior |
| WBS | Hierarchical deliverables and work packages; dotted codes; approved-scope gate | Implemented; no automatic traceability coverage report |
| Change control | Justification, cost/week impact, approve/reject, update budget/deadline, preserve calculated baseline | Implemented; updates are issued as separate commits rather than one transaction |
| Team and resources | Add team names and role descriptions; associate activities/defects | Implemented as project records; no HR, authentication, workload capacity, or availability planning |
| Schedule | Activities, dependencies, topological scheduling, cycle detection, delay and forecast fields | Implemented; forecast edge case needs review |
| Cost and EVM | Estimates, actual cost, PV/EV/AC, CPI/SPI, warnings | Implemented as simple activity-level calculations; no detailed cost-accounting or actual ledger evidence |
| Quality and defects | Severity/status register, checklist results, quality summaries | Implemented as manual tracking; no automated product test execution or clinical validation |
| Risk | 1–5 likelihood and impact, score, action, status | Implemented; no owner, due date, residual exposure, or escalation workflow |
| Dashboard and reports | Progress KPIs, forecast, reports, print, text export | Implemented; report evidence is not versioned, signed, or immutable |
| Healthcare appointments | Requirement label and case-study description | Not implemented as booking service |
| Laboratory reports | Requirement label and case-study description | Not implemented as lab-result storage or access |
| Doctor schedules | Requirement label and case-study description | Not implemented as clinician roster/availability service |
| Online consultations | Requirement label and case-study description | Not implemented as video or consultation workflow |
| Hospital billing | Requirement label and case-study description | Not implemented as billing or payment service |
| AI preliminary diagnosis | Approved change-request/requirement sample | No AI/ML code, model, data pipeline, clinical safeguards, or inference endpoint |
| Mobile application | Approved change-request/requirement sample | No mobile-specific project, native app, or responsive patient product |

## Important business logic

- New requirements are Proposed; only approved requirements may be linked to top-level WBS items.
- Change-derived requirements cannot be approved directly. Approval is performed through their linked change request.
- Approval adjusts current budget and project duration by the recorded impacts; rejected requests do not adjust them.
- Activity start is the later of requested start and all predecessor end weeks plus one; duration determines end week.
- Cycles in dependency edits are rejected, and prior dependencies are restored on that validation failure.
- EVM planned value is time-phased against each activity’s scheduled duration; earned value uses estimated cost multiplied by reported completion; actual cost is summed from reported costs.
- CPI = EV / AC and SPI = EV / PV when denominators are non-zero; warnings use a 0.90 threshold.
- Closure is blocked until every milestone is Achieved.

## Feature completeness judgement

**Complete relative to visible project-management prototype:** charter, scope, WBS, change, scheduling, EVM, defects, checklist, risk, dashboard, and closure flows have implementation and regression coverage.

**Partial or unsupported:** production controls, change history attribution, API contract/versioning, robust persistence operations, clinical domain implementation, formal acceptance evidence, and operations/deployment.

## User workflow

`Create charter → define plan → propose and approve requirements → build WBS → add/approve changes → schedule activities and dependencies → record progress/cost → inspect defects/risks/quality → achieve milestones → close and record lessons.`
