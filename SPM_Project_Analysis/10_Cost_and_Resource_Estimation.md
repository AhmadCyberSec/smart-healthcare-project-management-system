# Chapter 8 support: Cost Estimation and Budget Management

## Evidence and confidence

All currency values in the source/sample data are PKR. The dataset includes a budget, change impacts, activity estimates, and example actual costs. Because files are explicitly case-study/demo records and disagree in state, none should be represented as authorized project funding, paid invoices, payroll, or audited actual spend without confirmation.

## Budget baseline and changes

| Element | PKR | Weeks | Evidence |
|---|---:|---:|---|
| Original sample baseline | 5,000,000 | 16 | `sample_data.sql`, `step1_demo.py`, runtime sample |
| AI preliminary diagnosis change | +500,000 | +2 | Approved sample change request |
| Mobile application change | +300,000 | +1 | Approved sample change request |
| Revised sample baseline | 5,800,000 | 19 | Derived; recorded in seed data and current `pm.db` |

## Illustrative activity estimate breakdown

The seven seed/runtime activities have estimated costs totaling PKR 5,000,000. Activity-level estimates are not equivalent to a validated budget estimate or an approved cost account structure.

| Activity | Estimate (PKR) |
|---|---:|
| Requirements and design | 700,000 |
| Appointment scheduling | 900,000 |
| Patient records and reports | 800,000 |
| Frontend screens | 700,000 |
| Database integration | 500,000 |
| System and defect testing | 600,000 |
| AI and mobile enhancements | 800,000 |
| **Listed activity estimate total** | **5,000,000** |
| **Revised sample budget less listed estimates** | **800,000** |

The PKR 800,000 difference equals the two approved sample change impacts, but the activity estimates do not show whether those change estimates are incremental, included, or double-counted. The budget breakdown therefore needs reconciliation. No contingency, tax, license, infrastructure, training, support, or management reserve amounts are provided.

## Earned value method actually implemented

- **PV:** estimated cost multiplied by planned fraction elapsed by the reporting week.
- **EV:** estimated cost multiplied by reported percent complete.
- **AC:** sum of entered activity actual-cost amounts.
- **CPI:** EV / AC (when AC is non-zero).
- **SPI:** EV / PV (when PV is non-zero).
- **Budget variance:** approved project budget minus AC.
- Warnings are emitted if actual or total planned estimate exceeds approved budget, or CPI/SPI falls below 0.90.

These are simplified activity-level calculations. No cost account, period-by-period actual ledger, labor-hour capture, procurement cost, tax, or independent financial reconciliation is present.

## Project resource model

The sample team contains seven role entries: one Project Manager, two Backend Developers, two Frontend Developers, one Database Developer, and one QA Engineer. They are default labels, not confirmed individuals. `activities.assigned_to` stores the role/name as text; it does not record FTE allocation, work hours, skills, availability, or hourly/daily rate.

### Not Available – Requires Confirmation

- Authorized budget owner, currency confirmation, funding source, and approval date.
- Named staff, salary/vendor rates, effort estimates, procurement and infrastructure needs.
- Contingency/reserve policy, taxes, financial reporting period, actual-cost evidence.
- Whether the approved changes are included in or additive to the activity estimate.
- Actual spent/committed/forecast-at-completion values.

## Proposed estimation and control approach

Use an approved WBS and estimate each work package using documented effort/rate assumptions, procurement/licensing, environment, training, deployment, support, and a separately justified contingency. Establish a time-phased cost baseline. Report budget at completion, PV, EV, AC, CPI, SPI, estimate to complete, estimate at completion, and variance with actual source evidence. Review baseline changes through the same formal change control used for scope. Do not copy the sample estimates into a real project budget without validation.
