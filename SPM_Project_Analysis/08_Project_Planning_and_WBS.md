# Chapters 6–7: Project Planning, Charter, Scope, WBS, and Resources

## Project charter

The following charter is reconstructed from project source/sample records. It is not proof of a formally signed charter.

| Charter element | Recorded case-study value | Status |
|---|---|---|
| Project title | Smart Healthcare Project Management and Monitoring System | Verified text |
| Objective | Manage appointments, lab reports, doctor schedules, online consultations, and billing for five hospitals | Case-study statement; operating functionality not implemented |
| Stakeholders | Hospital management, doctors, patients, billing staff, development company | Case-study text; identities and authority unconfirmed |
| In scope (stated) | Appointments, lab reports, doctor schedules, online consultations, billing | Case-study scope |
| Out of scope (stated) | Pharmacy inventory, insurance claims, hardware procurement | Case-study scope boundary |
| Original budget / deadline | PKR 5,000,000 / 16 weeks | Illustrative SQL and runtime sample baseline |
| Approved sample changes | AI preliminary diagnosis + PKR 500,000/+2 weeks; mobile application + PKR 300,000/+1 week | Illustrative records; approval authority not independently confirmed |
| Revised budget / deadline | PKR 5,800,000 / 19 weeks | Derived from sample figures |
| Start date | 2026-09-01 | Seed/snapshot date; actual start requires confirmation |
| Current actual project status | Not Available – Requires Confirmation | `pm.db` says Planning, seed SQL says Executing; inconsistent evidence |
| Charter signatory / sponsor | Not Available – Requires Confirmation | No signature or approval record |

## Scope statement

### Product scope actually evidenced

Local software for project planning and monitoring. It manages project metadata, requirements and their approval, a WBS, change control, team-role assignments, activities/dependencies, schedule and cost indicators, defect/inspection/risk records, dashboard summaries, and closure.

### Exclusions and unimplemented scope

Although listed in charter/sample requirements, clinical and hospital functions are not demonstrated. This includes live appointment booking, patient account/record management, laboratory result handling, doctor roster management, telemedicine, billing/payment, AI diagnosis, and mobile application delivery. Pharmacy inventory, insurance claims, and hardware procurement are named out of scope in the case-study records.

## Scope management and change process

**Verified workflow:** requirement starts Proposed → decision → approved scope can enter WBS. For a change request, submit justification and cost/week impact → authorized decision (authorization is modeled as a status/note, not tied to a real user) → approval adjusts budget/deadline and requirement state; rejection leaves budget/deadline unchanged.

**Proposed governance:** require a change ID, business owner, impact assessment, privacy/security/safety assessment where relevant, approval record, baseline version, and communication of approved/rejected decisions. Require an impact review of scope, schedule, cost, quality, risk, data, and acceptance criteria before implementation.

## Work breakdown structure

The runtime sample and SQL seed are not identical. The SQL seed describes seven top-level workstreams, with a mix of child packages; the current `pm.db` has seven major healthcare-related items and one additional child record. These are case-study data, not evidence that the underlying hospital modules are built.

### Illustrative WBS (proposed baseline for planning; refine after stakeholder confirmation)

| WBS | Work package / deliverable | Current evidence |
|---|---|---|
| 1 | Project initiation and requirements | Charter and planning workflows exist; healthcare requirements are largely names/descriptions |
| 1.1 | Confirm stakeholders, workflow, constraints, acceptance criteria | Not Available – Requires Confirmation |
| 2 | Architecture and design | Design activity and milestone appear in sample planning data |
| 3 | Project-management dashboard | Implemented in Python/HTML/CSS/JavaScript |
| 3.1 | Charter, scope, WBS, change control | Implemented |
| 3.2 | Schedule, cost, EVM, resources | Implemented |
| 3.3 | Quality, defects, risk, reports, closure | Implemented |
| 4 | Healthcare operational services | Not implemented; only case-study requirements |
| 4.1 | Appointment/lab/doctor/consultation/billing workflows | Not implemented |
| 4.2 | AI and mobile | Approved sample change requests only; not implemented |
| 5 | Verification and acceptance | Existing regression tests cover project-management logic/API; clinical/product acceptance is absent |
| 6 | Deployment, training, handover, support | No verified deployment record or plan |

This WBS labels deliverables by evidence and should not be presented as a completed historical WBS without approval.

## Project development life cycle

**Observed lifecycle:** Initiating → Planning → Executing → Monitoring ↔ Executing → Closed. The code defines status transitions but does not encode a full software-development methodology or sprint process.

**Recommended lifecycle (proposed):** discovery/requirements → architecture and threat/privacy assessment → iterative implementation → verification and user acceptance → deployment readiness → controlled release → support/maintenance → closure/lessons learned. Use explicit entry/exit criteria for each phase.

## Resource planning

Sample role list: Project Manager; two Backend Developers; two Frontend Developers; Database Developer; QA Engineer. These are role labels seeded by the application, not confirmed named employees, allocations, or availability. The current project database stores seven team-role records.

**Not Available – Requires Confirmation:** actual people, sponsor, product owner, clinical/domain experts, security/privacy reviewer, deployment/operations support, allocation percentages, rate cards, labor capacity, procurement needs, and holiday/calendar assumptions.

**Proposed resource controls:** assign a named accountable owner per WBS package; track capacity and workload separately from role names; identify decision authority; reserve QA/security review; document backups and handover.
