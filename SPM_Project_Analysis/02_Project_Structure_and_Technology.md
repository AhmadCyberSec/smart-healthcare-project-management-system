# Chapter 5 support: Project Structure and Technology

## Complete workspace structure at inspection

The inventory below describes the application source. Local SQLite database files and generated Python bytecode may exist during development but are excluded from version control.

```text
.
|-- .github\workflows\tests.yml
|-- .gitignore
|-- README.md
|-- pm_core.py
|-- sample_data.sql
|-- schema.sql
|-- SPM_Project_Analysis\
|-- step1_demo.py
|-- step2_demo.py
|-- test_modules.py
|-- test_step1.py
|-- test_step2.py
|-- test_web_app.py
|-- web_app.py
`-- web\
|   |-- app.js
|   |-- favicon.svg
|   |-- index.html
|   `-- styles.css
```

`SPM_Project_Analysis\` contains 16 Markdown reports. Runtime databases and bytecode are generated/local files and are not part of the tracked source.

## Languages, frameworks, and technologies

| Technology | Use | Evidence |
|---|---|---|
| Python 3 | HTTP server, business rules, SQLite persistence, regression scripts | `web_app.py`, `pm_core.py`, tests |
| SQLite / SQL | Relational storage, schema constraints, case-study seed dataset | `schema.sql`, `sample_data.sql`, `.db` files |
| HTML5 | Dashboard shell and navigation/modal structure | `web/index.html` |
| CSS | Responsive dashboard styling and layout | `web/styles.css` |
| JavaScript (browser, no framework detected) | Rendering, form handling, API requests, charts, filtering | `web/app.js` |
| Python standard library | `http.server`, `sqlite3`, `json`, `threading`, `webbrowser`, `urllib`, `datetime` | Imports in Python files |
| Mermaid | Report diagrams only | Created in the report, not a project runtime dependency |

No Python dependency manifest, JavaScript package manifest, framework package, ORM, migration framework, test runner configuration, or environment file was found in the pre-report workspace. The README says no third-party packages are required. The installed Python interpreter used for regression checks was Python 3.14.7; the source itself does not declare a minimum/maximum supported Python version.

## File-by-file inventory and purpose

| Path | Observed purpose |
|---|---|
| `README.md` | Setup instructions, project scope, module summary, validation commands |
| `web_app.py` | Seeds sample project, exposes HTTP/JSON API, serves whitelisted static assets, launches browser |
| `pm_core.py` | SQLite access, input/business-rule validation, calculations, scheduling, reports |
| `schema.sql` | SQLite table definitions and basic constraints |
| `sample_data.sql` | Alternative SQL initialization data for the case study |
| `step1_demo.py`, `step2_demo.py` | Demonstrations of charter and scope/change-control logic |
| `test_step1.py` | Charter, lifecycle, milestone, and closure regression tests |
| `test_step2.py` | Requirement, WBS, and change-request regression tests |
| `test_modules.py` | Schedule, dependency, EVM, defect, quality, risk, and dashboard assertions |
| `test_web_app.py` | Local HTTP integration test using an in-memory database |
| `web/index.html` | UI shell, navigation, modal, toast region |
| `web/app.js` | Dashboard rendering and event/API logic |
| `web/styles.css` | Visual system, responsive layout, printable dashboard styling |
| `web/favicon.svg` | UI icon asset |
| `*.db` | Local SQLite databases created during use; excluded from version control |
| `__pycache__\*.pyc` | Generated Python bytecode; excluded from version control |

## Configuration and integrations

The application selects `pm.db` beside `web_app.py` and binds the server to `127.0.0.1` on port `8765`. The browser is opened using Python's `webbrowser` module. No API credentials, passwords, bearer tokens, `.env` files, external service endpoints, cloud databases, or third-party integration settings were identified in the reviewed source. The existing database content is sample-like; it may still contain locally identifying records and should be handled as private workspace data.

## Static assets and deployment dependencies

The server serves only the explicit paths `/`, `/index.html`, `/styles.css`, `/app.js`, and `/favicon.svg`; it does not expose a general filesystem path route. The client uses browser APIs including `fetch`, `localStorage`, `dialog`, Canvas, Blob, and `window.print`. A modern browser is therefore assumed. No build/bundling step is present.

## Source evidence

See `README.md`, `web_app.py`, `pm_core.py`, `schema.sql`, `sample_data.sql`, and `web\` assets. The application entry point is `web_app.py`; its `main()` constructs the `PM` store and loopback HTTP server.
