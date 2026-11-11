# Chapter 12: Security and Maintenance

## Security mechanisms verified

- The HTTP listener is bound to `127.0.0.1`, not all interfaces.
- The server serves static resources from a fixed allow-list rather than accepting arbitrary file paths.
- JSON request bodies larger than 1,000,000 bytes are rejected.
- Static responses include `X-Content-Type-Options: nosniff`; API responses are marked `Cache-Control: no-store`.
- Most SQL values are passed as bound parameters; dynamic update field names are selected from a whitelist.
- Front-end display code uses an HTML escaping helper in many dynamic contexts.
- Business validation checks project status, enumerations, positive/non-negative values, assigned roles, requirement approval, and dependency cycles.

These controls provide limited local-prototype safeguards. They do not amount to a production security design.

## Material security weaknesses and privacy risks

| Finding | Evidence and impact | Recommended action |
|---|---|---|
| No authentication or authorization | Any process/user able to reach the local service can read state and invoke mutation endpoints; team roles are labels only | Keep single-user/local-only unless access control is implemented and tested; add authenticated identity and least-privilege permission checks before sharing |
| No explicit CSRF/origin validation | Mutation endpoints accept POST JSON; OPTIONS advertises methods/headers but there is no origin allow-list or CSRF token mechanism | Validate Origin/Host and use a robust CSRF design if browser access can be influenced by other sites; do not rely on CORS alone |
| No TLS | Loopback HTTP only; no encrypted remote transport | Do not expose remotely; add TLS via a controlled deployment boundary for any networked environment |
| No security headers policy | Only `nosniff` appears on static assets; no CSP/frame/referrer policy identified | Define and test appropriate CSP, frame, referrer, and cache policies |
| Exception detail returned to caller | Generic exception handler returns `Unexpected server error: {exc}` | Log detailed exception server-side with safe IDs; return non-sensitive generic error to client |
| SQLite FK enforcement not explicitly enabled | Foreign keys declared in schema; source lacks `PRAGMA foreign_keys=ON` | Enable at connection startup and add integrity tests |
| Multi-step operations not atomic | Each `PM.run()` commits; change approval updates budget, requirement, request, and log in separate commits | Wrap related changes in one transaction with rollback on error |
| No backup, retention, encryption-at-rest, or recovery documentation | Local `.db` files persist in workspace; no operational data procedure identified | Define data classification, backup encryption, retention, restore drills, and deletion policy |
| Healthcare privacy/safety controls absent | No patient service implementation, access model, audit identity, or clinical safeguards | Do not store real patient/health information in this prototype; perform legal/privacy/safety review before any expansion |

## Threat and trust assumptions

Current loopback binding reduces remote network exposure but does not protect against local malicious processes, browser-origin attacks against localhost services, device compromise, workspace disclosure, shared-machine access, or accidental inclusion of database files in backups/source exchange. The help card’s wording “saved locally and securely” is not substantiated by a security assessment and should not be interpreted as a guarantee.

## Maintenance and operations plan (proposed)

1. **Database:** establish authoritative database location, automated backup, restore drills, schema versioning, migration procedure, integrity checks, and ownership.
2. **Dependencies/runtime:** record Python/browser support matrix; keep standard-library rationale; review Python security support and upgrade compatibility.
3. **Logging:** add structured, privacy-safe logs for request ID, operation outcome, and errors; avoid logging sensitive project or patient data.
4. **Change/release:** version-control source, require peer review, run regression/security tests, record build/release identifiers and rollback steps.
5. **Data handling:** use synthetic data for demos; define retention, deletion, access, incident response, and device protections.
6. **Monitoring:** define process health, database disk capacity, error reporting, and support ownership only if deployment needs it.
7. **Security testing:** perform a threat model and independent review before multi-user, remote, or sensitive-data use.

## Maintenance status

No production deployment guide, owner, support rota, backup procedure, upgrade plan, issue tracker, or release history is available in the workspace. Maintenance personnel and service expectations are **Not Available – Requires Confirmation**.
