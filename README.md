# Smart Healthcare Project Management System

[![CI](https://github.com/AhmadCyberSec/smart-healthcare-project-management-system/actions/workflows/tests.yml/badge.svg)](https://github.com/AhmadCyberSec/smart-healthcare-project-management-system/actions/workflows/tests.yml)

A local, browser-based project-management dashboard built with Python, SQLite, and vanilla JavaScript. It demonstrates project chartering, scope and change control, dependency-driven scheduling, earned-value tracking, quality checks, risk management, and project closure.

> **Scope note:** This is an educational project-management prototype, not a healthcare information system. Healthcare capabilities such as patient records, appointments, diagnosis, consultations, and billing are represented only as case-study planning items; they are not implemented clinical features. Do not use this application to store patient or other sensitive data.

## Features

- **Project charter and lifecycle:** record objectives, stakeholders, scope, budget, schedule, status, milestones, and closure.
- **Scope and change control:** manage requirements, approval decisions, work breakdown structure (WBS) items, and change requests.
- **Schedule and resources:** assign work to team members, model dependencies, validate dependency cycles, and forecast completion.
- **Cost tracking:** calculate planned value (PV), earned value (EV), actual cost (AC), cost performance index (CPI), and schedule performance index (SPI).
- **Quality and risk:** track defects, inspections, risk likelihood/impact, and response plans.
- **Dashboard and reports:** review project status, progress, forecasts, warnings, and scope/charter summaries.
- **SQLite persistence:** keep project records in a local database; load the illustrative case study from the dashboard.

## Technology

- Python 3.14 (the version used for the current regression tests)
- SQLite (Python standard library)
- HTML, CSS, and vanilla JavaScript

The application has no third-party Python or JavaScript dependencies and no frontend build step.

## Quick start

1. Install Python 3.14 (the version used by CI and the current regression tests).
2. Clone the repository and change into its directory:

   ```powershell
   git clone https://github.com/AhmadCyberSec/smart-healthcare-project-management-system.git
   cd smart-healthcare-project-management-system
   ```

3. Start the dashboard:

   ```powershell
   python web_app.py
   ```

   On Windows, if `python` is not on `PATH`, use the Python launcher:

   ```powershell
   py -3 web_app.py
   ```

4. Open [http://127.0.0.1:8765](http://127.0.0.1:8765) if it does not open automatically.
5. Select **Load case-study project** to populate the local database with illustrative project data. Sample data is available only when the database has no charter.

The server binds to the loopback interface (`127.0.0.1`); it is intended for local use, not deployment as a shared or production service. Stop it with `Ctrl+C`.

## Run the tests

Run the four regression and integration scripts from the repository root:

```powershell
python test_step1.py
python test_step2.py
python test_modules.py
python test_web_app.py
```

Or use `py -3` in place of `python` on Windows. The HTTP integration test uses an in-memory database and a temporary local port.

GitHub Actions runs the same scripts on pushes and pull requests.

## Repository layout

```text
.
├── .github/workflows/tests.yml       # Continuous integration
├── SPM_Project_Analysis/             # Detailed 16-chapter project analysis
├── web/                              # Dashboard HTML, CSS, JavaScript, and icon
├── pm_core.py                        # Business logic and SQLite persistence
├── web_app.py                        # Local HTTP server and API
├── schema.sql                        # Database schema
├── sample_data.sql                   # Optional SQL case-study dataset
├── step1_demo.py, step2_demo.py      # Charter and scope demonstrations
├── test_*.py                         # Regression and integration tests
└── README.md
```

Runtime SQLite databases, Python bytecode, and local virtual environments are intentionally excluded from version control. The application creates its database locally when it starts.

## Project analysis

The [`SPM_Project_Analysis/`](SPM_Project_Analysis/) folder contains the full project report, including requirements, architecture, database analysis, planning, scheduling, cost/resource estimates, risk, quality/testing, security/maintenance, limitations, and a consolidated summary. Start with [the complete project summary](SPM_Project_Analysis/16_Complete_Project_Summary.md).

## Case-study figures

The illustrative SQL seed uses an initial baseline of **PKR 5,000,000 / 16 weeks**. Its two approved example changes add **PKR 800,000 / 3 weeks**, producing a sample updated baseline of **PKR 5,800,000 / 19 weeks**. These are demonstration values, not verified real-world funding, expenditure, or schedule commitments.

## Limitations

- There is no authentication, authorization, multi-user access control, or production deployment configuration.
- The project does not implement patient-facing or clinical workflows and does not provide healthcare compliance controls.
- The database is local SQLite; backup, restore, migration, and multi-user concurrency processes are not provided.

See the detailed limitations and future scope in [`14_Project_Limitations_and_Future_Scope.md`](SPM_Project_Analysis/14_Project_Limitations_and_Future_Scope.md) and security/maintenance analysis in [`13_Security_and_Maintenance.md`](SPM_Project_Analysis/13_Security_and_Maintenance.md).
