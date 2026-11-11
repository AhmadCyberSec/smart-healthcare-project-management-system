"""pm_core.py - business logic and database access (no GUI code).

Step 1: Project Initiation and Integration Management
  - project charter, project management plan, status workflow,
    milestones with owners, closure records, formatted charter report.
"""
import os
import sqlite3
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
STATUSES = ("Initiating", "Planning", "Executing", "Monitoring", "Closed")

# Allowed status changes (Closed is only reachable through close_project)
TRANSITIONS = {
    "Initiating": {"Planning"},
    "Planning": {"Executing"},
    "Executing": {"Monitoring"},
    "Monitoring": {"Executing"},
    "Closed": set(),
}
TEXT_FIELDS = ("name", "objectives", "stakeholders", "scope_in", "scope_out")
PRIORITIES = ("High", "Medium", "Low")


class PMError(ValueError):
    """Raised whenever a validation check or business rule fails."""


# ------------------------- validation helpers -------------------------
def _need(label, value):
    if value is None or not str(value).strip():
        raise PMError(f"{label} cannot be empty.")
    return str(value).strip()


def _positive(label, value, cast):
    try:
        number = cast(value)
    except (TypeError, ValueError):
        raise PMError(f"{label} must be a valid number.")
    if number <= 0:
        raise PMError(f"{label} must be greater than zero.")
    return number


def _date(value):
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
    except ValueError:
        raise PMError("Start date must use the format YYYY-MM-DD (e.g. 2026-09-01).")
    return str(value)


class PM:
    def __init__(self, path="pm.db"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        with open(os.path.join(HERE, "schema.sql")) as f:
            self.db.executescript(f.read())
        if not self.rows("SELECT id FROM team_members LIMIT 1"):
            self.db.executemany(
                "INSERT INTO team_members(name,role) VALUES (?,?)",
                [("Project Manager", "Project Manager"),
                 ("Backend Developer 1", "Backend Developer"),
                 ("Backend Developer 2", "Backend Developer"),
                 ("Frontend Developer 1", "Frontend Developer"),
                 ("Frontend Developer 2", "Frontend Developer"),
                 ("Database Developer", "Database Developer"),
                 ("QA Engineer", "Quality Assurance")])
            self.db.commit()

    # ------------------------- low-level helpers -------------------------
    def run(self, sql, args=()):
        cur = self.db.execute(sql, args)
        self.db.commit()
        return cur

    def rows(self, sql, args=()):
        return [dict(r) for r in self.db.execute(sql, args)]

    def get_project(self):
        found = self.rows("SELECT * FROM project WHERE id = 1")
        return found[0] if found else None

    def _open_project(self):
        """Return the project, making sure it exists and is not closed."""
        p = self.get_project()
        if not p:
            raise PMError("Create the project charter first.")
        if p["status"] == "Closed":
            raise PMError("The project is closed; no further changes are allowed.")
        return p

    def _log(self, status, note):
        self.run("INSERT INTO status_log(status, note) VALUES (?,?)", (status, note))

    # ------------------------- 1. Project charter -------------------------
    def create_charter(self, name, objectives, stakeholders, scope_in, scope_out,
                       budget, deadline_weeks, start_date):
        if self.get_project():
            raise PMError("A charter already exists. Use update_charter().")
        values = [_need("Name", name), _need("Objectives", objectives),
                  _need("Stakeholders", stakeholders),
                  _need("Scope (included)", scope_in),
                  _need("Scope (excluded)", scope_out),
                  _positive("Budget", budget, float),
                  _positive("Deadline (weeks)", deadline_weeks, int),
                  _date(start_date)]
        self.run("""INSERT INTO project(id,name,objectives,stakeholders,scope_in,
                    scope_out,budget,deadline_weeks,start_date)
                    VALUES (1,?,?,?,?,?,?,?,?)""", values)
        self._log("Initiating", "Charter created")

    def update_charter(self, **changes):
        """Change any charter field, e.g. update_charter(budget=5800000)."""
        p = self._open_project()
        if not changes:
            raise PMError("Nothing to update.")
        clean = {}
        for field, value in changes.items():
            if field in TEXT_FIELDS:
                clean[field] = _need(field.replace("_", " ").title(), value)
            elif field == "budget":
                clean[field] = _positive("Budget", value, float)
            elif field == "deadline_weeks":
                clean[field] = _positive("Deadline (weeks)", value, int)
                late = [m["name"] for m in self.milestones()
                        if m["due_week"] > clean[field]]
                if late:
                    raise PMError("Milestones fall after the new deadline: "
                                  + ", ".join(late))
            elif field == "start_date":
                clean[field] = _date(value)
            else:
                raise PMError(f"'{field}' is not an updatable charter field.")
        sets = ", ".join(f"{f}=?" for f in clean)       # field names are whitelisted
        self.run(f"UPDATE project SET {sets} WHERE id=1", tuple(clean.values()))
        self._log(p["status"], "Charter updated: " + ", ".join(clean))

    # --------------------- 2. Project management plan ---------------------
    def update_plan(self, scope, schedule, cost, quality):
        p = self._open_project()
        self.run("""UPDATE project SET plan_scope=?, plan_schedule=?,
                    plan_cost=?, plan_quality=? WHERE id=1""",
                 (_need("Scope plan", scope), _need("Schedule plan", schedule),
                  _need("Cost plan", cost), _need("Quality plan", quality)))
        self._log(p["status"], "Project management plan updated")
        if p["status"] == "Initiating":
            self.set_status("Planning", "Plan approved, moving to planning")

    # ------------------------------ 3. Status ------------------------------
    def set_status(self, status, note=""):
        p = self._open_project()
        if status not in STATUSES:
            raise PMError(f"Status must be one of {STATUSES}.")
        if status == "Closed":
            raise PMError("Use close_project() to close the project.")
        if status not in TRANSITIONS[p["status"]]:
            raise PMError(f"Cannot move from {p['status']} to {status}.")
        self.run("UPDATE project SET status=? WHERE id=1", (status,))
        self._log(status, note)

    # ------------------- 4. Milestones and responsibilities -------------------
    def add_milestone(self, name, due_week, owner):
        p = self._open_project()
        name, owner = _need("Milestone name", name), _need("Owner", owner)
        due_week = _positive("Due week", due_week, int)
        if due_week > p["deadline_weeks"]:
            raise PMError(f"Due week must be between 1 and {p['deadline_weeks']}.")
        if self.rows("SELECT id FROM milestones WHERE lower(name)=lower(?)", (name,)):
            raise PMError(f"Milestone '{name}' already exists.")
        self.run("INSERT INTO milestones(name,due_week,owner) VALUES (?,?,?)",
                 (name, due_week, owner))

    def achieve_milestone(self, milestone_id):
        self._open_project()
        m = self.rows("SELECT * FROM milestones WHERE id=?", (milestone_id,))
        if not m:
            raise PMError("Milestone not found.")
        if m[0]["status"] == "Achieved":
            raise PMError("Milestone is already achieved.")
        self.run("UPDATE milestones SET status='Achieved' WHERE id=?", (milestone_id,))

    def milestones(self):
        return self.rows("SELECT * FROM milestones ORDER BY due_week, id")

    def milestone_progress(self):
        ms = self.milestones()
        done = sum(1 for m in ms if m["status"] == "Achieved")
        pct = round(100 * done / len(ms)) if ms else 0
        return {"achieved": done, "total": len(ms), "pct": pct}

    # ------------------------------ 5. Closure ------------------------------
    def close_project(self, summary, lessons=""):
        self._open_project()
        pending = [m["name"] for m in self.milestones() if m["status"] != "Achieved"]
        if pending:
            raise PMError("Cannot close. Pending milestones: " + ", ".join(pending))
        summary = _need("Closure summary", summary)
        self.run("INSERT INTO closure(summary, lessons) VALUES (?,?)", (summary, lessons))
        self.run("UPDATE project SET status='Closed' WHERE id=1")
        self._log("Closed", "Project closed")

    # ------------------------------ 6. Report ------------------------------
    def charter_report(self):
        p = self.get_project()
        if not p:
            raise PMError("Create the project charter first.")
        end = datetime.strptime(p["start_date"], "%Y-%m-%d") + timedelta(weeks=p["deadline_weeks"])
        prog = self.milestone_progress()
        line, bar = "=" * 74, "-" * 74
        out = [line, " PROJECT CHARTER AND MANAGEMENT PLAN", line,
               f"Project     : {p['name']}",
               f"Status      : {p['status']}",
               f"Start date  : {p['start_date']}",
               f"Deadline    : {p['deadline_weeks']} weeks (planned end {end:%Y-%m-%d})",
               f"Budget      : PKR {p['budget']:,.0f}", bar,
               f"Objectives  : {p['objectives']}",
               f"Stakeholders: {p['stakeholders']}",
               f"In scope    : {p['scope_in']}",
               f"Out of scope: {p['scope_out']}", bar, "MANAGEMENT PLAN"]
        for label, key in [("Scope", "plan_scope"), ("Schedule", "plan_schedule"),
                           ("Cost", "plan_cost"), ("Quality", "plan_quality")]:
            out.append(f"  {label:<9}: {p[key] or 'Not defined yet'}")
        out += [bar, f"MILESTONES ({prog['achieved']}/{prog['total']} achieved, {prog['pct']}%)"]
        for m in self.milestones():
            out.append(f"  Week {m['due_week']:>2} | {m['name']:<26} | {m['owner']:<17} | {m['status']}")
        out.append(line)
        return "\n".join(out)

    # ======================================================================
    # STEP 2: Scope Management and WBS
    # ======================================================================

    # ----------------------------- Requirements -----------------------------
    def get_requirement(self, req_id):
        found = self.rows("SELECT * FROM requirements WHERE id=?", (req_id,))
        if not found:
            raise PMError("Requirement not found.")
        return found[0]

    def add_requirement(self, title, description, priority, _source="Original"):
        """New requirements always start as 'Proposed' (not yet in scope)."""
        self._open_project()
        title = _need("Requirement title", title)
        if priority not in PRIORITIES:
            raise PMError(f"Priority must be one of {PRIORITIES}.")
        if self.rows("SELECT id FROM requirements WHERE lower(title)=lower(?)", (title,)):
            raise PMError(f"Requirement '{title}' already exists.")
        return self.run("""INSERT INTO requirements(title,description,priority,source)
                           VALUES (?,?,?,?)""",
                        (title, (description or "").strip(), priority, _source)).lastrowid

    def update_requirement(self, req_id, **changes):
        self._open_project()
        r = self.get_requirement(req_id)
        if r["status"] == "Rejected":
            raise PMError("A rejected requirement cannot be edited.")
        if not changes:
            raise PMError("Nothing to update.")
        clean = {}
        for field, value in changes.items():
            if field == "title":
                clean[field] = _need("Requirement title", value)
                if self.rows("SELECT id FROM requirements WHERE lower(title)=lower(?) AND id<>?",
                             (clean[field], req_id)):
                    raise PMError(f"Requirement '{clean[field]}' already exists.")
            elif field == "description":
                clean[field] = (value or "").strip()
            elif field == "priority":
                if value not in PRIORITIES:
                    raise PMError(f"Priority must be one of {PRIORITIES}.")
                clean[field] = value
            else:
                raise PMError(f"'{field}' cannot be updated.")
        sets = ", ".join(f"{f}=?" for f in clean)
        self.run(f"UPDATE requirements SET {sets} WHERE id=?", (*clean.values(), req_id))

    def approve_requirement(self, req_id):
        self._open_project()
        r = self.get_requirement(req_id)
        if r["source"] == "Change Request":
            raise PMError("This requirement came from a change request; "
                          "approve it through the change request.")
        if r["status"] != "Proposed":
            raise PMError(f"Only proposed requirements can be approved (current: {r['status']}).")
        self.run("UPDATE requirements SET status='Approved' WHERE id=?", (req_id,))

    def reject_requirement(self, req_id):
        self._open_project()
        r = self.get_requirement(req_id)
        if r["source"] == "Change Request":
            raise PMError("This requirement came from a change request; "
                          "reject it through the change request.")
        if r["status"] != "Proposed":
            raise PMError(f"Only proposed requirements can be rejected (current: {r['status']}).")
        self.run("UPDATE requirements SET status='Rejected' WHERE id=?", (req_id,))

    def requirements(self, status=None):
        """All requirements, highest priority first."""
        sql = ("SELECT * FROM requirements {} ORDER BY CASE priority WHEN 'High' THEN 1 "
               "WHEN 'Medium' THEN 2 ELSE 3 END, id")
        if status:
            return self.rows(sql.format("WHERE status=?"), (status,))
        return self.rows(sql.format(""))

    # ------------------------- Work Breakdown Structure -------------------------
    def add_wbs_item(self, name, parent_id=None, requirement_id=None):
        """Top-level deliverables must link to an APPROVED requirement;
        children inherit the link. This keeps unapproved work out of the scope."""
        self._open_project()
        name = _need("WBS item name", name)
        if parent_id is None:
            if requirement_id is None:
                raise PMError("A top-level deliverable must be linked to an approved requirement.")
            req = self.get_requirement(requirement_id)
            if req["status"] != "Approved":
                raise PMError(f"Requirement '{req['title']}' is not approved, "
                              "so it cannot enter the project scope.")
            code = str(self.rows("SELECT COUNT(*) n FROM wbs WHERE parent_id IS NULL")[0]["n"] + 1)
        else:
            found = self.rows("SELECT * FROM wbs WHERE id=?", (parent_id,))
            if not found:
                raise PMError("Parent WBS item not found.")
            parent = found[0]
            requirement_id = parent["requirement_id"]
            count = self.rows("SELECT COUNT(*) n FROM wbs WHERE parent_id=?", (parent_id,))[0]["n"]
            code = f"{parent['code']}.{count + 1}"
        return self.run("INSERT INTO wbs(parent_id,code,name,requirement_id) VALUES (?,?,?,?)",
                        (parent_id, code, name, requirement_id)).lastrowid

    def wbs_items(self):
        items = self.rows("SELECT * FROM wbs")
        parents = {i["parent_id"] for i in items if i["parent_id"]}
        for i in items:
            i["depth"] = i["code"].count(".") + 1
            if i["depth"] == 1:
                i["type"] = "Deliverable"
            else:
                i["type"] = "Sub-deliverable" if i["id"] in parents else "Work Package"
        return sorted(items, key=lambda i: [int(x) for x in i["code"].split(".")])

    def wbs_text(self):
        items = self.wbs_items()
        if not items:
            return "  (no WBS items yet)"
        return "\n".join(f"  {'   ' * (i['depth'] - 1)}{i['code']:<6} {i['name']} [{i['type']}]"
                         for i in items)

    # ----------------------------- Change requests -----------------------------
    def _cr(self, cr_id):
        found = self.rows("SELECT * FROM change_requests WHERE id=?", (cr_id,))
        if not found:
            raise PMError("Change request not found.")
        return found[0]

    def submit_change_request(self, title, justification, description, priority,
                              cost_impact, schedule_impact_weeks):
        """Records the proposed change and creates its requirement as 'Proposed'."""
        self._open_project()
        justification = _need("Justification", justification)
        cost = _non_negative("Cost impact", cost_impact, float)
        weeks = _non_negative("Schedule impact (weeks)", schedule_impact_weeks, int)
        req_id = self.add_requirement(title, description, priority, "Change Request")
        return self.run("""INSERT INTO change_requests(title,justification,requirement_id,
                           cost_impact,weeks_impact) VALUES (?,?,?,?,?)""",
                        (title.strip(), justification, req_id, cost, weeks)).lastrowid

    def approve_change_request(self, cr_id, note=""):
        """Approval updates scope (requirement), budget AND deadline together."""
        p = self._open_project()
        cr = self._cr(cr_id)
        if cr["status"] != "Pending":
            raise PMError(f"Change request #{cr_id} is already {cr['status']}.")
        new_budget = p["budget"] + cr["cost_impact"]
        new_weeks = p["deadline_weeks"] + cr["weeks_impact"]
        self.update_charter(budget=new_budget, deadline_weeks=new_weeks)
        self.run("UPDATE requirements SET status='Approved' WHERE id=?", (cr["requirement_id"],))
        self.run("""UPDATE change_requests SET status='Approved', decision_note=?,
                    decided_on=datetime('now'), budget_before=?, budget_after=?,
                    weeks_before=?, weeks_after=? WHERE id=?""",
                 (note, p["budget"], new_budget, p["deadline_weeks"], new_weeks, cr_id))
        self._log(p["status"], f"Change request #{cr_id} approved: "
                               f"+PKR {cr['cost_impact']:,.0f}, +{cr['weeks_impact']} weeks")
        return {"requirement_id": cr["requirement_id"],
                "budget_before": p["budget"], "budget_after": new_budget,
                "weeks_before": p["deadline_weeks"], "weeks_after": new_weeks}

    def reject_change_request(self, cr_id, note=""):
        p = self._open_project()
        cr = self._cr(cr_id)
        if cr["status"] != "Pending":
            raise PMError(f"Change request #{cr_id} is already {cr['status']}.")
        self.run("UPDATE requirements SET status='Rejected' WHERE id=?", (cr["requirement_id"],))
        self.run("""UPDATE change_requests SET status='Rejected', decision_note=?,
                    decided_on=datetime('now') WHERE id=?""", (note, cr_id))
        self._log(p["status"], f"Change request #{cr_id} rejected")

    def change_requests(self, status=None):
        if status:
            return self.rows("SELECT * FROM change_requests WHERE status=? ORDER BY id", (status,))
        return self.rows("SELECT * FROM change_requests ORDER BY id")

    def pending_change_requests(self):
        return len(self.change_requests("Pending"))

    def baseline(self):
        """Original budget/deadline = current values minus all approved changes."""
        p = self.get_project()
        s = self.rows("""SELECT COALESCE(SUM(cost_impact),0) c, COALESCE(SUM(weeks_impact),0) w
                         FROM change_requests WHERE status='Approved'""")[0]
        return {"budget": p["budget"] - s["c"], "deadline_weeks": p["deadline_weeks"] - s["w"],
                "approved_cost": s["c"], "approved_weeks": s["w"]}

    # --------------------------------- Report ---------------------------------
    def scope_report(self):
        p = self.get_project()
        if not p:
            raise PMError("Create the project charter first.")
        b, reqs, crs = self.baseline(), self.requirements(), self.change_requests()
        n = lambda s: sum(1 for r in reqs if r["status"] == s)
        line, bar = "=" * 74, "-" * 74
        out = [line, " SCOPE AND CHANGE REPORT", line,
               f"Baseline budget / deadline : PKR {b['budget']:,.0f} / {b['deadline_weeks']} weeks",
               f"Approved changes           : +PKR {b['approved_cost']:,.0f} / +{b['approved_weeks']} weeks",
               f"Current budget / deadline  : PKR {p['budget']:,.0f} / {p['deadline_weeks']} weeks", bar,
               f"REQUIREMENTS (approved {n('Approved')}, proposed {n('Proposed')}, rejected {n('Rejected')})"]
        out += [f"  R{r['id']:<2} {r['status']:<9} {r['priority']:<7} {r['title']} ({r['source']})"
                for r in reqs]
        out += [bar, "CHANGE REQUESTS"]
        out += [f"  CR{c['id']:<2} {c['status']:<9} {c['title']}  +PKR {c['cost_impact']:,.0f}, "
                f"+{c['weeks_impact']} wk" for c in crs] or ["  None"]
        out += [bar, "WORK BREAKDOWN STRUCTURE", self.wbs_text(), line]
        return "\n".join(out)

    # ---------------------- Schedule and resource management ----------------------
    def add_team_member(self, name, role):
        name, role = _need("Team member name", name), _need("Role", role)
        if self.rows("SELECT id FROM team_members WHERE lower(name)=lower(?)", (name,)):
            raise PMError(f"Team member '{name}' already exists.")
        return self.run("INSERT INTO team_members(name,role) VALUES (?,?)",
                        (name, role)).lastrowid

    def team_members(self):
        return self.rows("SELECT * FROM team_members ORDER BY role,name")

    def add_activity(self, name, assigned_to, duration_weeks, estimated_cost,
                     start_week=1, dependencies=(), wbs_id=None):
        self._open_project()
        name, assigned_to = _need("Activity name", name), _need("Assigned team member", assigned_to)
        duration = _positive("Duration (weeks)", duration_weeks, int)
        cost = _non_negative("Estimated cost", estimated_cost, float)
        start = _positive("Start week", start_week, int)
        if not self.rows("SELECT id FROM team_members WHERE lower(name)=lower(?)", (assigned_to,)):
            raise PMError(f"Team member '{assigned_to}' is not in the project team.")
        if wbs_id is not None and not self.rows("SELECT id FROM wbs WHERE id=?", (wbs_id,)):
            raise PMError("WBS item not found.")
        if wbs_id is not None:
            wbs = self.rows("""SELECT r.status FROM wbs w
                               JOIN requirements r ON r.id=w.requirement_id WHERE w.id=?""",
                            (wbs_id,))
            if not wbs or wbs[0]["status"] != "Approved":
                raise PMError("Activities can only be linked to WBS items in approved scope.")
        if self.rows("SELECT id FROM activities WHERE lower(name)=lower(?)", (name,)):
            raise PMError(f"Activity '{name}' already exists.")
        dep_ids = tuple(dict.fromkeys(dependencies))
        if any(not self.rows("SELECT id FROM activities WHERE id=?", (dep_id,))
               for dep_id in dep_ids):
            raise PMError("Every activity dependency must reference an existing activity.")
        cur = self.db.execute(
            """INSERT INTO activities(name,assigned_to,duration_weeks,estimated_cost,
               requested_start_week,start_week,end_week,wbs_id) VALUES (?,?,?,?,?,?,?,?)""",
            (name, assigned_to, duration, cost, start, start, start + duration - 1, wbs_id))
        activity_id = cur.lastrowid
        self.db.executemany(
            "INSERT INTO activity_dependencies(activity_id,depends_on_id) VALUES (?,?)",
            [(activity_id, dep_id) for dep_id in dep_ids])
        self.db.commit()
        self.recompute_schedule()
        return activity_id

    def set_activity_dependencies(self, activity_id, dependencies):
        if not self.rows("SELECT id FROM activities WHERE id=?", (activity_id,)):
            raise PMError("Activity not found.")
        dep_ids = tuple(dict.fromkeys(dependencies))
        if activity_id in dep_ids or any(
                not self.rows("SELECT id FROM activities WHERE id=?", (dep_id,))
                for dep_id in dep_ids):
            raise PMError("Dependencies must be existing activities and cannot include the activity itself.")
        previous = [r["depends_on_id"] for r in self.rows(
            "SELECT depends_on_id FROM activity_dependencies WHERE activity_id=?", (activity_id,))]
        self.db.execute("DELETE FROM activity_dependencies WHERE activity_id=?", (activity_id,))
        self.db.executemany(
            "INSERT INTO activity_dependencies(activity_id,depends_on_id) VALUES (?,?)",
            [(activity_id, dep_id) for dep_id in dep_ids])
        self.db.commit()
        try:
            self.recompute_schedule()
        except PMError:
            self.db.execute("DELETE FROM activity_dependencies WHERE activity_id=?", (activity_id,))
            self.db.executemany(
                "INSERT INTO activity_dependencies(activity_id,depends_on_id) VALUES (?,?)",
                [(activity_id, dep_id) for dep_id in previous])
            self.db.commit()
            raise

    def recompute_schedule(self):
        activities = self.rows("SELECT * FROM activities ORDER BY id")
        by_id = {a["id"]: a for a in activities}
        deps = {a["id"]: [r["depends_on_id"] for r in self.rows(
            "SELECT depends_on_id FROM activity_dependencies WHERE activity_id=?",
            (a["id"],))] for a in activities}
        remaining = set(by_id)
        scheduled = {}
        while remaining:
            ready = [activity_id for activity_id in remaining
                     if all(dep in scheduled for dep in deps[activity_id])]
            if not ready:
                raise PMError("Activity dependencies contain a cycle.")
            for activity_id in ready:
                activity = by_id[activity_id]
                start = max([activity["requested_start_week"]] +
                            [scheduled[dep]["end_week"] + 1 for dep in deps[activity_id]])
                end = start + activity["duration_weeks"] - 1
                scheduled[activity_id] = {"start_week": start, "end_week": end}
                remaining.remove(activity_id)
        for activity_id, dates in scheduled.items():
            self.db.execute("UPDATE activities SET start_week=?,end_week=? WHERE id=?",
                            (dates["start_week"], dates["end_week"], activity_id))
        self.db.commit()
        return self.activities()

    def update_activity_progress(self, activity_id, percent_complete, actual_cost):
        if not self.rows("SELECT id FROM activities WHERE id=?", (activity_id,)):
            raise PMError("Activity not found.")
        pct = _non_negative("Percent complete", percent_complete, float)
        cost = _non_negative("Actual cost", actual_cost, float)
        if pct > 100:
            raise PMError("Percent complete must be between 0 and 100.")
        self.run("UPDATE activities SET percent_complete=?,actual_cost=? WHERE id=?",
                 (pct, cost, activity_id))

    def activities(self):
        rows = self.rows("""SELECT a.*, GROUP_CONCAT(d.name, ', ') AS dependency_names
                            FROM activities a
                            LEFT JOIN activity_dependencies x ON x.activity_id=a.id
                            LEFT JOIN activities d ON d.id=x.depends_on_id
                            GROUP BY a.id ORDER BY a.start_week,a.id""")
        for activity in rows:
            activity["start_date"] = self._week_date(activity["start_week"])
            activity["end_date"] = self._week_date(activity["end_week"])
        return rows

    def _week_date(self, week):
        project = self.get_project()
        start = datetime.strptime(project["start_date"], "%Y-%m-%d")
        return (start + timedelta(weeks=week - 1)).strftime("%Y-%m-%d")

    def delayed_activities(self, current_week=None):
        current_week = self.current_week() if current_week is None else current_week
        return [a for a in self.activities()
                if a["end_week"] < current_week and a["percent_complete"] < 100]

    def schedule_forecast(self, current_week=None):
        project = self.get_project()
        if not project:
            if current_week is not None:
                _positive("Reporting week", current_week, int)
            return {"current_week": 1, "activities": [], "projected_end_week": 0,
                    "deadline_week": 0, "deadline_variance_weeks": 0, "delayed": []}
        week = self.current_week() if current_week is None else _positive(
            "Reporting week", current_week, int)
        activities = self.activities()
        by_id = {a["id"]: a for a in activities}
        dependencies = {a["id"]: [r["depends_on_id"] for r in self.rows(
            "SELECT depends_on_id FROM activity_dependencies WHERE activity_id=?", (a["id"],))]
                        for a in activities}
        forecast = {}
        remaining = set(by_id)
        while remaining:
            ready = [activity_id for activity_id in remaining
                     if all(dep in forecast for dep in dependencies[activity_id])]
            if not ready:
                raise PMError("Activity dependencies contain a cycle.")
            for activity_id in ready:
                activity = by_id[activity_id]
                predecessor_end = max([0] + [forecast[dep]["forecast_end_week"]
                                             for dep in dependencies[activity_id]])
                if activity["percent_complete"] >= 100:
                    start, end = activity["start_week"], activity["end_week"]
                elif activity["start_week"] <= week:
                    start = max(activity["start_week"], week)
                    remaining_duration = max(
                        1, int((activity["duration_weeks"]
                                * (100 - activity["percent_complete"]) + 99) // 100))
                    end = max(activity["end_week"], start + remaining_duration - 1)
                else:
                    start = max(activity["start_week"], predecessor_end + 1)
                    end = start + activity["duration_weeks"] - 1
                forecast[activity_id] = {
                    "forecast_start_week": start, "forecast_end_week": end,
                    "delay_weeks": max(0, end - activity["end_week"]),
                    "delayed": activity["end_week"] < week and activity["percent_complete"] < 100
                }
                remaining.remove(activity_id)
        rows = []
        for activity in activities:
            rows.append({**activity, **forecast[activity["id"]]})
        projected_end = max([0] + [r["forecast_end_week"] for r in rows])
        return {
            "current_week": week, "activities": rows,
            "projected_end_week": projected_end,
            "deadline_week": project["deadline_weeks"],
            "deadline_variance_weeks": max(0, projected_end - project["deadline_weeks"]),
            "delayed": [r for r in rows if r["delayed"]]
        }

    def current_week(self):
        project = self.get_project()
        if not project:
            raise PMError("Create the project charter first.")
        start = datetime.strptime(project["start_date"], "%Y-%m-%d").date()
        today = datetime.now().date()
        return max(1, (today - start).days // 7 + 1)

    # ------------------------- Cost and earned value -------------------------
    def earned_value(self, current_week=None):
        project = self.get_project()
        if not project:
            raise PMError("Create the project charter first.")
        week = self.current_week() if current_week is None else _positive(
            "Reporting week", current_week, int)
        activities = self.activities()
        pv = 0.0
        ev = 0.0
        ac = 0.0
        for activity in activities:
            elapsed = max(0, min(activity["duration_weeks"],
                                 week - activity["start_week"] + 1))
            planned_fraction = elapsed / activity["duration_weeks"]
            pv += activity["estimated_cost"] * planned_fraction
            ev += activity["estimated_cost"] * activity["percent_complete"] / 100
            ac += activity["actual_cost"]
        cpi = ev / ac if ac else None
        spi = ev / pv if pv else None
        estimate_total = sum(a["estimated_cost"] for a in activities)
        return {
            "week": week, "pv": pv, "ev": ev, "ac": ac, "cpi": cpi, "spi": spi,
            "planned_budget": estimate_total, "approved_budget": project["budget"],
            "budget_variance": project["budget"] - ac,
            "cost_overrun": ac > project["budget"] or estimate_total > project["budget"],
            "warnings": (["Actual or planned cost exceeds the approved project budget."]
                         if ac > project["budget"] or estimate_total > project["budget"] else [])
                        + (["CPI is below 0.90; investigate cost performance."]
                           if cpi is not None and cpi < 0.9 else [])
                        + (["SPI is below 0.90; investigate schedule performance."]
                           if spi is not None and spi < 0.9 else [])
        }

    # ---------------------------- Quality and risk ----------------------------
    def add_defect(self, title, description, severity, assigned_to):
        self._open_project()
        title, assigned_to = _need("Defect title", title), _need("Assigned team member", assigned_to)
        if severity not in ("Critical", "High", "Medium", "Low"):
            raise PMError("Severity must be Critical, High, Medium, or Low.")
        if not self.rows("SELECT id FROM team_members WHERE lower(name)=lower(?)", (assigned_to,)):
            raise PMError(f"Team member '{assigned_to}' is not in the project team.")
        return self.run("""INSERT INTO defects(title,description,severity,assigned_to)
                           VALUES (?,?,?,?)""",
                        (title, (description or "").strip(), severity, assigned_to)).lastrowid

    def update_defect(self, defect_id, status):
        self._open_project()
        if status not in ("Open", "In Progress", "Resolved"):
            raise PMError("Defect status must be Open, In Progress, or Resolved.")
        if not self.rows("SELECT id FROM defects WHERE id=?", (defect_id,)):
            raise PMError("Defect not found.")
        self.run("UPDATE defects SET status=? WHERE id=?", (status, defect_id))

    def defects(self, unresolved_only=False):
        if unresolved_only:
            return self.rows("""SELECT * FROM defects WHERE status<>'Resolved'
                                ORDER BY CASE severity WHEN 'Critical' THEN 1
                                WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,id""")
        return self.rows("""SELECT * FROM defects ORDER BY CASE severity WHEN 'Critical' THEN 1
                            WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,id""")

    def add_quality_check(self, deliverable, criterion):
        self._open_project()
        deliverable = _need("Deliverable", deliverable)
        criterion = _need("Quality criterion", criterion)
        if self.rows("SELECT id FROM quality_checks WHERE lower(deliverable)=lower(?)",
                     (deliverable,)):
            raise PMError(f"Quality checklist item for '{deliverable}' already exists.")
        return self.run("INSERT INTO quality_checks(deliverable,criterion) VALUES (?,?)",
                        (deliverable, criterion)).lastrowid

    def record_quality_result(self, check_id, result, notes=""):
        self._open_project()
        if result not in ("Pass", "Fail", "Not Tested"):
            raise PMError("Result must be Pass, Fail, or Not Tested.")
        if not self.rows("SELECT id FROM quality_checks WHERE id=?", (check_id,)):
            raise PMError("Quality check not found.")
        self.run("""UPDATE quality_checks SET result=?,notes=?,inspected_on=datetime('now')
                    WHERE id=?""", (result, (notes or "").strip(), check_id))

    def quality_checks(self):
        return self.rows("SELECT * FROM quality_checks ORDER BY id")

    def add_risk(self, title, description, likelihood, impact,
                 preventive_action, corrective_action):
        self._open_project()
        title = _need("Risk title", title)
        likelihood = _positive("Likelihood", likelihood, int)
        impact = _positive("Impact", impact, int)
        if likelihood > 5 or impact > 5:
            raise PMError("Likelihood and impact must each be from 1 to 5.")
        preventive = _need("Preventive action", preventive_action)
        corrective = _need("Corrective action", corrective_action)
        return self.run("""INSERT INTO risks(title,description,likelihood,impact,
                           preventive_action,corrective_action) VALUES (?,?,?,?,?,?)""",
                        (title, (description or "").strip(), likelihood, impact,
                         preventive, corrective)).lastrowid

    def risks(self):
        rows = self.rows("SELECT * FROM risks ORDER BY likelihood * impact DESC,id")
        for risk in rows:
            risk["score"] = risk["likelihood"] * risk["impact"]
        return rows

    def update_risk_status(self, risk_id, status):
        self._open_project()
        if status not in ("Open", "Mitigated", "Closed"):
            raise PMError("Risk status must be Open, Mitigated, or Closed.")
        if not self.rows("SELECT id FROM risks WHERE id=?", (risk_id,)):
            raise PMError("Risk not found.")
        self.run("UPDATE risks SET status=? WHERE id=?", (status, risk_id))

    def dashboard(self):
        project = self.get_project()
        if not project:
            raise PMError("Create the project charter first.")
        activities = self.activities()
        delayed = self.delayed_activities()
        forecast = self.schedule_forecast()
        evm = self.earned_value()
        pct = round(sum(a["percent_complete"] for a in activities) / len(activities)) if activities else 0
        return {
            "project": project, "progress_pct": pct, "pending_change_requests": self.pending_change_requests(),
            "delayed_activities": delayed, "schedule_forecast": forecast, "evm": evm,
            "critical_defects": [d for d in self.defects(unresolved_only=True)
                                 if d["severity"] == "Critical"],
            "unresolved_defect_count": len(self.defects(unresolved_only=True)),
            "activities": activities
        }


def _non_negative(label, value, cast):
    try:
        number = cast(value)
    except (TypeError, ValueError):
        raise PMError(f"{label} must be a valid number.")
    if number < 0:
        raise PMError(f"{label} must be zero or greater.")
    return number
