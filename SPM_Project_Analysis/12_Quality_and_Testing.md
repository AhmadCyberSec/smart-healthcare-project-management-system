# Chapter 10: Quality Assurance and Testing

## Quality management approach visible in the repository

The project stores a four-field quality plan, manual deliverable checklists, pass/fail/not-tested results, defects with severity and status, and a dashboard readiness summary. The case study calls for inspection of each deliverable and resolution of critical defects before release. It does not define a formal quality standard, test strategy, coverage target, or release approval authority.

## Test assets and observed validation

| Script | Coverage evidenced | Result when run 31 Oct 2026 |
|---|---|---|
| `test_step1.py` | Charter validation, status transitions, milestones, closure | 20/20 test cases passed |
| `test_step2.py` | Requirements, WBS, change approval/rejection and baseline effects | 40/40 test cases passed |
| `test_modules.py` | Dependency schedule, cycle handling, forecast, EVM, defects, inspections, risk, dashboard | Passed |
| `test_web_app.py` | HTTP static assets, state API, sample loading, requirements/WBS, activities, changes, quality/risk, closure, errors | Passed |

The tests use Python `assert` statements and in-memory SQLite stores; the HTTP integration test binds to an ephemeral loopback port and shuts its server down. No third-party test framework, coverage measurement, CI workflow, or test-data generator was found. The two demo scripts are examples, not automated tests; they contain file deletion of their named demonstration database files and were not executed as part of this investigation.

## Current database quality evidence

`pm.db` has 2 unresolved example defects (one Critical and one High); its appointment-scheduling quality check is Fail, and patient-record and billing checks are Not Tested. This sample snapshot is not independent product-test evidence. It is, however, a clear warning against claiming that the illustrative product is release-ready.

## Quality plan proposed

| Quality activity | Proposed acceptance evidence |
|---|---|
| Requirements review | Approved, uniquely identified requirements with measurable acceptance criteria and traceability to WBS/tests |
| Code review | Reviewed changes, static checks, dependency/security review, and documented disposition |
| Unit/business-rule tests | Boundary values, invalid payloads, database integrity, schedule edge cases, EVM formulas |
| API integration tests | Schema validation, success/error contract, limits, concurrency, unauthorized request cases |
| UI testing | Supported browser matrix, keyboard and screen-reader review, responsive viewport checks |
| Security/privacy testing | Authentication/authorization, CSRF/origin, data exposure, input handling, logging, backup and recovery |
| Acceptance/UAT | Named authorized users sign off against agreed requirements; unresolved severity thresholds documented |
| Release gate | No open critical defects; all required checks pass; backup/restore and rollback tested; approval recorded |

## Coverage gaps and recommendations

- No test confirms that SQLite foreign-key relationships are enforced.
- No focused regression test covers the forecast case where a delayed predecessor remains incomplete while a dependent task is already scheduled.
- No tests address malformed JSON edge cases, missing/negative/oversized content lengths, non-finite numbers, or concurrent mutations.
- No direct security, privacy, accessibility, browser-compatibility, load, recovery, or deployment tests were found.
- No clinical correctness, medical safety, privacy, or regulatory validation exists; none can be inferred from PM-system tests.
- Add reproducible test instructions and CI on the intended Python/browser support matrix. Keep all test data synthetic.

## Quality status conclusion

The project-management prototype demonstrates meaningful regression coverage and core validation. Production quality, operational suitability, and healthcare product acceptance are not established. Treat the tests as logic/regression evidence, not proof of healthcare feature completeness.
