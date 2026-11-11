# Chapter 3: Functional Requirements Analysis

## Interpretation

The following requirements describe behavior verified in source. Acceptance statuses separate executable project-management functionality from healthcare features that occur only as case-study text. Unless noted otherwise, data operations require an open charter and are performed through `pm_core.PM` and the `/api/` dispatcher in `web_app.py`.

## Functional requirements register

| ID | Requirement | Evidence/acceptance observation | Status |
|---|---|---|---|
| FR-01 | Create a single project charter with name, objectives, stakeholders, scope boundaries, positive budget, positive duration, and ISO date | `PM.create_charter`; invalid name, zero budget, invalid date, and second charter covered by `test_step1.py` | Implemented and tested |
| FR-02 | Edit charter fields and prevent changes after closure | Whitelisted fields and validation in `PM.update_charter`; closed-project test | Implemented and tested |
| FR-03 | Save scope, schedule, cost, and quality management-plan text | `PM.update_plan`; first save advances Initiating to Planning | Implemented and tested |
| FR-04 | Enforce lifecycle transitions Initiating → Planning → Executing → Monitoring, with Monitoring ↔ Executing; close only through closure workflow | `TRANSITIONS`, `set_status`, `close_project` | Implemented and tested |
| FR-05 | Add and achieve named milestones with due week and owner; disallow duplicate names and dates beyond the project duration | `add_milestone`, `achieve_milestone`, `milestone_progress` | Implemented and tested |
| FR-06 | Prevent closure while milestones remain pending; record closure summary and lessons | `close_project`; tests cover blocked and successful closure | Implemented and tested |
| FR-07 | Add, edit, approve, reject, and prioritize project requirements | Priority and status rules in `pm_core.py`; source-specific change requests must use their approval path | Implemented and tested |
| FR-08 | Build hierarchical WBS items; require top-level items to link to approved requirements and make children inherit the requirement | `add_wbs_item`, `wbs_items`; tested for hierarchy and scope gate | Implemented and tested |
| FR-09 | Submit, approve, or reject change requests with justification, cost and duration effects | Approval updates current charter budget/duration and requirement status; sample changes total PKR 800,000 and 3 weeks | Implemented and tested |
| FR-10 | Maintain project team member names and role labels | `team_members`, `add_team_member`; role text is not an authorization role | Implemented |
| FR-11 | Record activities with owner, duration, cost estimate, earliest start, optional WBS link, and predecessor activities | `add_activity`; owner and approved-scope checks | Implemented and tested |
| FR-12 | Recalculate schedule from activity dependencies and reject dependency cycles | `recompute_schedule`, `set_activity_dependencies`; regression test covers cycle rejection | Implemented and tested |
| FR-13 | Record activity completion and actual cost; forecast activity dates and delayed work | `update_activity_progress`, `schedule_forecast`, dashboard | Implemented and tested; forecast edge cases remain |
| FR-14 | Calculate PV, EV, AC, CPI, SPI, cost variance, and warning thresholds | `earned_value`; CPI/SPI warnings threshold at 0.90 | Implemented and tested |
| FR-15 | Record defects with severity, owner, and status | `add_defect`, `update_defect`; unresolved and critical defect summaries | Implemented and tested |
| FR-16 | Define deliverable inspections and record Pass/Fail/Not Tested results and notes | `quality_checks`, `record_quality_result` | Implemented and tested |
| FR-17 | Register risks using 1–5 likelihood and impact, provide preventive/corrective actions, and update status | `add_risk`, `risks`, `update_risk_status` | Implemented and tested |
| FR-18 | Present dashboard state and export/print project summaries | `/api/state`, `/api/export`, dashboard and report views | Implemented; export is text, not a signed/controlled report |
| FR-19 | Load case-study data only into an empty project store | `/api/sample` checks for existing charter | Implemented and tested |
| FR-20 | Book patient appointments, upload lab results, manage doctor rosters, conduct online consultations, or issue/reconcile hospital bills | These appear in project scope/requirements only. No healthcare domain schema or operational feature was found. | Not implemented in inspected source |
| FR-21 | Deliver AI-based diagnosis or patient mobile application | Seed requirement/change-request names exist; no model, clinical workflow, mobile client, or mobile API found | Not implemented in inspected source |

## User roles and permissions

**Verified:** project data has descriptive stakeholder strings, team member `role` values, and task/defect assignments.

**Not implemented:** user accounts, authentication, sessions tied to identities, role-based access control (RBAC), permission checks by action, separation of approval authority, or audit attribution to an authenticated user. Any project role listed in the UI is not a system permission.

## Use cases and workflows

1. **Initialize a project:** create charter → save management plan → advance status.
2. **Control requirements:** create proposed requirement → approve/reject → create WBS deliverable only after approval.
3. **Control changes:** submit justification and impact → approve/reject → on approval update budget/duration and approve its requirement → add it to the WBS.
4. **Plan delivery:** create team roles → define activities and predecessors → recalculate schedule → update completion/cost → review forecast and EVM.
5. **Manage quality and risks:** record issues/inspections/risks → update outcomes/status → review dashboard readiness.
6. **Close:** achieve every milestone → enter closure summary and lessons → mark project Closed.

## Evidence and traceability

Core behavior is in `pm_core.py`; HTTP actions are in `_dispatch()` in `web_app.py`; browser controls are in `web/app.js`. Test evidence is in `test_step1.py`, `test_step2.py`, `test_modules.py`, and `test_web_app.py`. Requirements about real hospital care require stakeholder elicitation and are not traceable to operational implementation.
