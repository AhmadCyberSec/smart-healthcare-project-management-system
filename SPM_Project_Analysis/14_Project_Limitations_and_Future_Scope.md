# Chapter 13: Project Limitations and Future Scope

## Current limitations

### Product and scope

- The workspace implements a project-management tool for a healthcare case study—not an operational healthcare information system.
- Healthcare services appear as charter text, requirements, WBS names, or changes. The source has no patient/appointment/lab/consultation/billing model or service endpoints.
- AI diagnosis and mobile application exist only as sample-approved change records.
- Stakeholders, team roster, budget, schedule, and approval notes are not verified real project records.

### Architecture and security

- Local, single-process SQLite design; no authentication, authorization, TLS, explicit CSRF defense, or multi-user tenancy.
- Foreign-key enforcement is not enabled explicitly; data integrity partly depends on business-layer validation.
- Several workflows commit multiple steps separately.
- No API schema/versioning, migration tooling, backup/restore procedure, operational monitoring, or deployment automation.

### Project-management fidelity

- EVM is simplified and operates on activity estimates/entered progress and costs.
- Project progress is a simple average of activity completion rather than a WBS-weighted or effort-weighted measure.
- No resource capacity/availability or resource leveling.
- Risk records lack owners, triggers, due dates, residual scores, and response funding.
- Quality checklists are manually recorded; they do not execute tests.
- The current database snapshots and seed methods differ. `pm.db` has no milestones; SQL sample status is Executing, while runtime-loaded example behavior differs.

### Quality/testing

- Existing unit-like and HTTP regression tests pass, but coverage percentage and automation in CI are unavailable.
- No systematic security, privacy, clinical safety, performance, accessibility, recovery, or production acceptance tests.
- Forecast calculation has a dependency sequencing edge case requiring a targeted test and review.

## Future scope options (proposed; not approved)

### Priority 0: confirm the product

Decide whether this project is intended to remain a project-management dashboard or become a healthcare operations system. Obtain stakeholders, users, workflows, data classification, regulatory constraints, and acceptance criteria before expanding scope.

### Priority 1: harden the existing project-management prototype

- Add authenticated users and authorization only if multi-user access is required.
- Add origin/CSRF protection, security headers, safe error responses, and security tests.
- Enable foreign keys; add transactions, migrations, backup/restore, and data provenance.
- Improve schedule forecast tests and EVM/progress definitions.
- Define APIs, accessibility target, supported browser/runtime matrix, and CI.

### Priority 2: implement any confirmed operational healthcare modules

Only following discovery and clinical/privacy/security review: requirements and architecture for patient identity, appointment conflict handling, laboratory result governance, doctor availability, telehealth, billing/payments, and auditability. The AI and mobile change labels are not adequate specifications. A diagnosis feature would require clinical governance, safety validation, data quality, explainability, monitoring, and an approved intended use; it must not be treated as a routine extension.

### Priority 3: deployment and support

For approved use, define secure hosting, availability/recovery targets, operational ownership, training, monitoring, incident response, support SLAs, release/rollback, data retention, and audit review.

## Prioritization principle

Resolve product identity, stakeholder authority, intended deployment, and data sensitivity first. These decisions determine the safe architecture, scope, cost, schedule, quality gates, and regulatory work. Avoid estimating clinical modules from the current PKR sample values.
