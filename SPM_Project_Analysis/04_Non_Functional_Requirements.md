# Chapter 3 support: Non-Functional Requirements

## Evidence classification

The repository does not include an approved non-functional requirements specification. This register classifies measurable or architectural qualities as **verified behavior**, **inferred**, or **proposed**. No service-level objectives, clinical standards, privacy regime, or performance targets should be assumed.

| ID | Quality attribute | Verified evidence / current limitation | Recommended requirement |
|---|---|---|---|
| NFR-01 | Deployment boundary | `web_app.py` binds to `127.0.0.1:8765`; README describes local-only use | Confirm whether single-user local usage is the target. For any shared deployment, define approved network boundary and threat model |
| NFR-02 | Runtime dependencies | README says Python 3 and SQLite with no third-party packages | Record tested Python/browser versions and pin a supported compatibility range |
| NFR-03 | Data persistence | SQLite database is stored beside source as `pm.db` | Define backup/restore, retention, recovery point, recovery time, and migration policy |
| NFR-04 | Request handling | Threaded HTTP server; an `RLock` serializes database-backed operations; request body limit is 1,000,000 bytes | Define concurrency and maximum supported project size; test contention and behavior under client disconnects |
| NFR-05 | Input validation | Business layer validates many fields, enums, dates, numeric ranges, and existence checks | Add systematic boundary/invalid-type tests; reject non-finite numeric values and define maximum lengths |
| NFR-06 | Data integrity | SQL uses primary keys, `CHECK`, `UNIQUE`, and declared references | Enable SQLite foreign-key enforcement and test all relationships; use atomic transactions for multi-record changes |
| NFR-07 | Usability | Multi-page dashboard, forms, search/filter, toast errors, mobile navigation, responsive CSS | Add user validation and keyboard/screen-reader acceptance tests |
| NFR-08 | Accessibility | HTML has landmarks, navigation labels, button labels and an aria-live toast region | No accessibility conformance target or automated/manual audit is documented; adopt an explicit WCAG target and test it |
| NFR-09 | Performance | No benchmark, response-time objective, or dataset-size test exists | Set response targets for expected records and verify under representative load |
| NFR-10 | Availability | Application is a local foreground process; no service supervision, health monitoring, or recovery mechanism | Define supported uptime and restart/recovery behavior only if deployment requires it |
| NFR-11 | Security | No authentication, authorization, TLS, CSRF token, CSP, or production hardening is present | Do not use for multi-user, internet-facing, or sensitive patient data until reviewed and hardened |
| NFR-12 | Privacy | Sample stakeholder text and local database records exist; no privacy design is documented | Identify personal/health data (if any), lawful purpose, access, retention, deletion, and breach procedures before handling real data |
| NFR-13 | Maintainability | Core logic separated from HTTP/UI; standard library; code is function-oriented | Add developer setup, API contract, schema migration approach, logging policy, type/lint policy, and CI |
| NFR-14 | Portability | Python/SQLite and static files are portable in principle; path is derived from source location | Test supported operating systems and browsers; current validation occurred on Windows |
| NFR-15 | Interoperability | No external protocols or integrations are implemented | Define data exchange requirements and safe integration contracts if needed |

## Inferred user needs

The dashboard implies a project manager needs an at-a-glance view of schedule, scope, cost, unresolved critical defects, and pending changes. The test scripts imply deterministic business rules and validation are expected. These are reasonable product inferences, not requirements signed off by an identified customer.

## Constraints

- Standard-library-only approach limits dependency/setup overhead, but does not itself establish security or production suitability.
- Local SQLite storage is suitable for a small local prototype; concurrent multi-user usage, remote access, and high availability are not demonstrated.
- The project has no package manifest, CI pipeline, platform support matrix, or documented database migration mechanism.
- No confirmed regulatory, safety, privacy, data residency, or clinical integration constraints are provided.
