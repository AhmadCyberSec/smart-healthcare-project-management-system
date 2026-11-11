# Chapter 9: Risk Management

## Method represented in the implementation

`risks` stores a title/description, likelihood 1–5, impact 1–5, preventive and corrective actions, and status. The core sorts by likelihood × impact. The interface displays a matrix. This is a basic qualitative probability-impact approach; it does not contain risk owner, trigger, due date, residual risk, response cost, or formal escalation.

## Risk register

The first two risks are present in the case-study data. The remainder are proposed risks for a real project and are explicitly not claims of historical events. Probability and impact values in the proposed rows are initial planning judgments for discussion, not measured frequencies.

| ID | Risk (status) | Probability | Impact | Score | Response / mitigation |
|---|---|---:|---:|---:|---|
| R-01 | Critical defect may delay deployment (sample: Open) | 4/5 | 5/5 | 20 | Existing sample response: run concurrency/regression suites on every build; corrective: focused fix sprint and resequence dependent work |
| R-02 | Approved change pressure increases cost and duration (sample: Open) | 3/5 | 4/5 | 12 | Existing sample response: use change control, reserve capacity, reforecast, obtain steering approval |
| R-03 | Scope confusion: project-management tool mistaken for implemented clinical product (proposed) | 3/5 | 5/5 | 15 | Explicitly label capabilities; obtain signed requirements and acceptance matrix; prohibit unsupported product claims |
| R-04 | Unauthorized local/cross-origin requests alter project data (proposed) | 2/5 | 4/5 | 8 | Keep loopback-only; add origin/CSRF controls, authentication, and security testing before shared use |
| R-05 | Local database loss/corruption or inconsistent snapshots (proposed) | 3/5 | 4/5 | 12 | Define backups, restore drills, a single authoritative database, and schema migration/versioning |
| R-06 | Forecast or cost indicators mislead decisions (proposed) | 3/5 | 4/5 | 12 | Reconcile source data; validate algorithms with boundary cases and independent expected-value calculations |
| R-07 | Real patient/health data processed without privacy/security safeguards (proposed) | 2/5 | 5/5 | 10 | Do not enter real health data before privacy/security/legal review, access control, retention, encryption, and incident plans |
| R-08 | Team roles/approvals are illustrative and not attributable to accountable people (proposed) | 3/5 | 3/5 | 9 | Confirm sponsor, product owner, approvers, team names, and decision authority; record authenticated audit attribution |
| R-09 | No formal acceptance or deployment plan causes handover failure (proposed) | 3/5 | 4/5 | 12 | Define UAT, release criteria, rollback, training, operations ownership, and support readiness |

## Risk monitoring plan (proposed)

1. Review high/critical exposure weekly and after any material scope change.
2. Assign a named owner, trigger, mitigation due date, contingency, and residual score to each risk.
3. Treat likelihood × impact as prioritization aid, not a precise loss forecast.
4. Link risks to WBS activities, change decisions, test evidence, and status reports.
5. Escalate patient safety, privacy, legal, critical-defect, and budget/schedule threshold events promptly to confirmed decision-makers.

## Existing risk-data limitation

Current `pm.db` contains two sample risks and no assigned risk owners. “Open” status and sample scores are database values, not verified evidence that a real project team accepted or actively monitors the risks.
