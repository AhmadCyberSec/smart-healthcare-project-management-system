-- Smart Healthcare Project Management System: database schema
-- Step 1: Project Initiation and Integration Management

-- One row only (id is always 1): the charter AND the project management plan
CREATE TABLE IF NOT EXISTS project (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    name            TEXT    NOT NULL,
    objectives      TEXT    NOT NULL,
    stakeholders    TEXT    NOT NULL,
    scope_in        TEXT    NOT NULL,          -- what is included
    scope_out       TEXT    NOT NULL,          -- what is NOT included (scope boundary)
    budget          REAL    NOT NULL CHECK (budget > 0),
    deadline_weeks  INTEGER NOT NULL CHECK (deadline_weeks > 0),
    start_date      TEXT    NOT NULL,          -- YYYY-MM-DD
    status          TEXT    NOT NULL DEFAULT 'Initiating'
                    CHECK (status IN ('Initiating','Planning','Executing','Monitoring','Closed')),
    plan_scope      TEXT DEFAULT '',           -- project management plan sections
    plan_schedule   TEXT DEFAULT '',
    plan_cost       TEXT DEFAULT '',
    plan_quality    TEXT DEFAULT ''
);

-- Key checkpoints of the project, each with a responsible person
CREATE TABLE IF NOT EXISTS milestones (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    due_week  INTEGER NOT NULL CHECK (due_week > 0),
    owner     TEXT    NOT NULL,                -- responsibility
    status    TEXT    NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending','Achieved'))
);

-- History of every status change
CREATE TABLE IF NOT EXISTS status_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_on  TEXT NOT NULL DEFAULT (datetime('now')),
    status     TEXT NOT NULL,
    note       TEXT
);

-- Project closure record
CREATE TABLE IF NOT EXISTS closure (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    closed_on  TEXT NOT NULL DEFAULT (datetime('now')),
    summary    TEXT NOT NULL,
    lessons    TEXT
);

-- ===================== Step 2: Scope Management and WBS =====================

-- Project requirements (a requirement is only in scope when status = 'Approved')
CREATE TABLE IF NOT EXISTS requirements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority    TEXT NOT NULL CHECK (priority IN ('High','Medium','Low')),
    status      TEXT NOT NULL DEFAULT 'Proposed' CHECK (status IN ('Proposed','Approved','Rejected')),
    source      TEXT NOT NULL DEFAULT 'Original'   -- 'Original' or 'Change Request'
);

-- Hierarchical Work Breakdown Structure (code: 1, 1.1, 1.1.1 ...)
CREATE TABLE IF NOT EXISTS wbs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id       INTEGER REFERENCES wbs(id),
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    requirement_id  INTEGER REFERENCES requirements(id)   -- traceability to approved scope
);

-- Change requests: justification, cost impact, schedule impact, approval status
CREATE TABLE IF NOT EXISTS change_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    justification   TEXT NOT NULL,
    requirement_id  INTEGER NOT NULL REFERENCES requirements(id),
    cost_impact     REAL NOT NULL CHECK (cost_impact >= 0),
    weeks_impact    INTEGER NOT NULL CHECK (weeks_impact >= 0),
    status          TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending','Approved','Rejected')),
    submitted_on    TEXT NOT NULL DEFAULT (datetime('now')),
    decided_on      TEXT,
    decision_note   TEXT,
    budget_before   REAL, budget_after REAL,      -- recorded when approved
    weeks_before    INTEGER, weeks_after INTEGER
);

-- ===================== Schedule, cost, quality and risk =====================
CREATE TABLE IF NOT EXISTS team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    assigned_to TEXT NOT NULL,
    duration_weeks INTEGER NOT NULL CHECK (duration_weeks > 0),
    estimated_cost REAL NOT NULL CHECK (estimated_cost >= 0),
    actual_cost REAL NOT NULL DEFAULT 0 CHECK (actual_cost >= 0),
    percent_complete REAL NOT NULL DEFAULT 0 CHECK (percent_complete BETWEEN 0 AND 100),
    requested_start_week INTEGER NOT NULL DEFAULT 1 CHECK (requested_start_week > 0),
    start_week INTEGER NOT NULL DEFAULT 1,
    end_week INTEGER NOT NULL DEFAULT 1,
    wbs_id INTEGER REFERENCES wbs(id)
);

CREATE TABLE IF NOT EXISTS activity_dependencies (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    depends_on_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    PRIMARY KEY(activity_id, depends_on_id),
    CHECK(activity_id <> depends_on_id)
);

CREATE TABLE IF NOT EXISTS defects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    severity TEXT NOT NULL CHECK(severity IN ('Critical','High','Medium','Low')),
    assigned_to TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','In Progress','Resolved')),
    created_on TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS quality_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deliverable TEXT NOT NULL UNIQUE COLLATE NOCASE,
    criterion TEXT NOT NULL,
    result TEXT NOT NULL DEFAULT 'Not Tested'
        CHECK(result IN ('Not Tested','Pass','Fail')),
    notes TEXT NOT NULL DEFAULT '',
    inspected_on TEXT
);

CREATE TABLE IF NOT EXISTS risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    likelihood INTEGER NOT NULL CHECK(likelihood BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 5),
    preventive_action TEXT NOT NULL,
    corrective_action TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','Mitigated','Closed'))
);