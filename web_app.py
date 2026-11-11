"""Local HTML dashboard for the Smart Healthcare PM system."""
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from pm_core import PM, PMError

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_ROOT = os.path.join(HERE, "web")
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}


def _sample_project(pm):
    pm.create_charter(
        "Smart Healthcare Project Management and Monitoring System",
        "Manage appointments, lab reports, doctor schedules, online consultations and billing for five hospitals.",
        "Hospital management, doctors, patients, billing staff, development company",
        "Appointments, lab reports, doctor schedules, online consultations, billing",
        "Pharmacy inventory, insurance claims, hardware procurement",
        5_000_000, 16, "2026-09-01")
    pm.update_plan(
        "Five approved hospital modules; scope changes require approval.",
        "16-week dependency-driven schedule; review weekly.",
        "Baseline PKR 5,000,000; track weekly earned value.",
        "Inspect each deliverable; resolve critical defects before release.")
    members = [member["name"] for member in pm.team_members()]
    for title, description, deliverable in [
        ("Patient appointment management", "Book, reschedule and cancel appointments", "Appointment Management"),
        ("Laboratory reports", "Upload and view lab results", "Laboratory Reports"),
        ("Doctor schedules", "Manage doctor availability", "Doctor Schedules"),
        ("Online consultations", "Video consultations", "Online Consultations"),
        ("Hospital billing", "Invoices and payments", "Hospital Billing")]:
        requirement_id = pm.add_requirement(title, description, "High")
        pm.approve_requirement(requirement_id)
        pm.add_wbs_item(deliverable, requirement_id=requirement_id)
    for title, justification, description, priority, cost, weeks in [
        ("AI-based preliminary diagnosis", "Hospital management wants faster patient triage",
         "Suggest a preliminary diagnosis from symptoms", "High", 500_000, 2),
        ("Mobile application", "Patients need mobile access",
         "Patient mobile app for appointments and reports", "Medium", 300_000, 1)]:
        request_id = pm.submit_change_request(
            title, justification, description, priority, cost, weeks)
        pm.approve_change_request(request_id, "Approved by steering committee")
        requirement_id = pm.change_requests()[-1]["requirement_id"]
        pm.add_wbs_item(title, requirement_id=requirement_id)
    for name, week, owner in [
        ("Requirements signed off", 3, "Project Manager"),
        ("Design completed", 5, "Backend Developer 1"),
        ("Development complete", 12, "Backend Developer 1"),
        ("Testing complete", 18, "QA Engineer"),
        ("Go-live", 19, "Project Manager")]:
        pm.add_milestone(name, week, owner)
    pm.set_status("Executing", "Development underway")
    activities = []
    activity_data = [
        ("Requirements and design", members[0], 3, 700_000, 1, []),
        ("Appointment scheduling", members[1], 4, 900_000, 4, [0]),
        ("Patient records and reports", members[2], 4, 800_000, 4, [0]),
        ("Frontend screens", members[3], 5, 700_000, 5, [0]),
        ("Database integration", members[5], 3, 500_000, 5, [0]),
        ("System and defect testing", members[6], 3, 600_000, 12, [1, 2, 3, 4]),
        ("AI and mobile enhancements", members[1], 3, 800_000, 17, [5])]
    for name, owner, duration, cost, start_week, predecessors in activity_data:
        dependencies = [activities[index] for index in predecessors]
        activities.append(pm.add_activity(
            name, owner, duration, cost, start_week, dependencies))
    pm.update_activity_progress(activities[0], 100, 700_000)
    pm.update_activity_progress(activities[1], 55, 520_000)
    pm.update_activity_progress(activities[2], 45, 470_000)
    pm.add_defect("Appointment slot conflicts", "Concurrent bookings can claim the same slot.",
                  "Critical", "QA Engineer")
    pm.add_defect("Patient record validation failure", "Incomplete records bypass validation.",
                  "High", "Backend Developer 2")
    for title, criterion in [
        ("Appointment scheduling", "No overlapping reservations under concurrent use"),
        ("Patient records", "Required fields validated and access is traceable"),
        ("Billing", "Invoice totals reconcile with payments")]:
        pm.add_quality_check(title, criterion)
    pm.record_quality_result(1, "Fail", "Concurrency defect requires correction.")
    pm.add_risk("Critical defect delays deployment", "Appointment defects may extend system testing.",
                4, 5, "Run concurrency and regression suites on every build.",
                "Add focused fix sprint and re-sequence dependent release tasks.")
    pm.add_risk("Approved change pressure", "AI/mobile additions add cost and three weeks.",
                3, 4, "Use change control and reserve capacity.",
                "Reforecast baseline and obtain steering approval.")


def _state(pm):
    project = pm.get_project()
    if not project:
        return {
            "project": None, "dashboard": None, "requirements": [], "wbs": [],
            "change_requests": [], "activities": [], "team_members": pm.team_members(),
            "milestones": [], "defects": [], "quality_checks": [], "risks": [],
            "closures": [], "scope_report": "", "charter_report": ""
        }
    dashboard = pm.dashboard()
    return {
        "project": project, "dashboard": dashboard,
        "requirements": pm.requirements(), "wbs": pm.wbs_items(),
        "change_requests": pm.change_requests(), "activities": pm.activities(),
        "team_members": pm.team_members(), "milestones": pm.milestones(),
        "defects": pm.defects(), "quality_checks": pm.quality_checks(),
        "risks": pm.risks(), "closures": pm.rows("SELECT * FROM closure ORDER BY id DESC"),
        "scope_report": pm.scope_report(), "charter_report": pm.charter_report()
    }


def _dispatch(pm, action, data):
    if action == "sample":
        if pm.get_project():
            raise PMError("Sample data can only be loaded into an empty project database.")
        _sample_project(pm)
        return {"message": "Case-study project loaded."}
    if action == "create-charter":
        pm.create_charter(data["name"], data["objectives"], data["stakeholders"],
                          data["scope_in"], data["scope_out"], data["budget"],
                          data["deadline_weeks"], data["start_date"])
        return {"message": "Project charter created."}
    if action == "update-charter":
        pm.update_charter(**data)
        return {"message": "Project charter updated."}
    if action == "update-plan":
        pm.update_plan(data["scope"], data["schedule"], data["cost"], data["quality"])
        return {"message": "Project management plan saved."}
    if action == "set-status":
        pm.set_status(data["status"], data.get("note", "Updated from dashboard"))
        return {"message": "Project status updated."}
    if action == "add-milestone":
        pm.add_milestone(data["name"], data["due_week"], data["owner"])
        return {"message": "Milestone added."}
    if action == "achieve-milestone":
        pm.achieve_milestone(data["id"])
        return {"message": "Milestone marked achieved."}
    if action == "close-project":
        pm.close_project(data["summary"], data.get("lessons", ""))
        return {"message": "Project closure recorded."}
    if action == "add-requirement":
        pm.add_requirement(data["title"], data.get("description", ""), data["priority"])
        return {"message": "Requirement added as proposed."}
    if action == "update-requirement":
        pm.update_requirement(data["id"], title=data["title"],
                              description=data.get("description", ""), priority=data["priority"])
        return {"message": "Requirement updated."}
    if action == "decide-requirement":
        if data["decision"] == "approve":
            pm.approve_requirement(data["id"])
        else:
            pm.reject_requirement(data["id"])
        return {"message": "Requirement decision saved."}
    if action == "add-wbs":
        pm.add_wbs_item(data["name"], parent_id=data.get("parent_id"),
                        requirement_id=data.get("requirement_id"))
        return {"message": "WBS item added."}
    if action == "submit-change":
        pm.submit_change_request(data["title"], data["justification"], data.get("description", ""),
                                 data["priority"], data["cost_impact"], data["weeks_impact"])
        return {"message": "Change request submitted."}
    if action == "decide-change":
        if data["decision"] == "approve":
            result = pm.approve_change_request(data["id"], data.get("note", ""))
            return {"message": "Change approved; budget and deadline updated.", "result": result}
        pm.reject_change_request(data["id"], data.get("note", ""))
        return {"message": "Change request rejected."}
    if action == "add-member":
        pm.add_team_member(data["name"], data["role"])
        return {"message": "Team member added."}
    if action == "add-activity":
        pm.add_activity(data["name"], data["assigned_to"], data["duration_weeks"],
                        data["estimated_cost"], data.get("start_week", 1),
                        data.get("dependencies", []), data.get("wbs_id"))
        return {"message": "Activity added and schedule recalculated."}
    if action == "update-activity":
        pm.update_activity_progress(data["id"], data["percent_complete"], data["actual_cost"])
        return {"message": "Activity actuals updated."}
    if action == "set-dependencies":
        pm.set_activity_dependencies(data["id"], data["dependencies"])
        return {"message": "Dependencies saved and schedule recalculated."}
    if action == "add-defect":
        pm.add_defect(data["title"], data.get("description", ""),
                      data["severity"], data["assigned_to"])
        return {"message": "Defect recorded."}
    if action == "update-defect":
        pm.update_defect(data["id"], data["status"])
        return {"message": "Defect status updated."}
    if action == "add-quality-check":
        pm.add_quality_check(data["deliverable"], data["criterion"])
        return {"message": "Quality checklist item added."}
    if action == "record-quality":
        pm.record_quality_result(data["id"], data["result"], data.get("notes", ""))
        return {"message": "Inspection result saved."}
    if action == "add-risk":
        pm.add_risk(data["title"], data.get("description", ""), data["likelihood"],
                    data["impact"], data["preventive_action"], data["corrective_action"])
        return {"message": "Risk recorded and prioritized."}
    if action == "update-risk":
        pm.update_risk_status(data["id"], data["status"])
        return {"message": "Risk status updated."}
    if action == "export":
        return {"report": pm.scope_report() + "\n\n" + pm.charter_report()}
    raise PMError("Unknown dashboard action.")


def create_handler(pm):
    request_lock = threading.RLock()

    class DashboardHandler(BaseHTTPRequestHandler):
        def _json(self, status, payload):
            content = json.dumps(payload, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/api/state":
                try:
                    with request_lock:
                        result = _state(pm)
                    self._json(200, result)
                except (PMError, ValueError, TypeError) as exc:
                    self._json(400, {"error": str(exc)})
                return
            asset = STATIC_FILES.get(path)
            if not asset:
                self._json(404, {"error": "Page not found."})
                return
            filename, content_type = asset
            try:
                with open(os.path.join(WEB_ROOT, filename), "rb") as source:
                    content = source.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(content)
            except OSError as exc:
                self._json(500, {"error": f"Unable to read dashboard asset: {exc}"})

        def do_POST(self):
            path = urlparse(self.path).path
            if not path.startswith("/api/"):
                self._json(404, {"error": "API endpoint not found."})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size > 1_000_000:
                    self._json(413, {"error": "Request body is too large."})
                    return
                payload = json.loads(self.rfile.read(size) or b"{}")
                with request_lock:
                    result = _dispatch(pm, path.removeprefix("/api/"), payload)
                    state = _state(pm)
                self._json(200, {"ok": True, **result, "state": state})
            except (json.JSONDecodeError, KeyError, TypeError, ValueError, PMError) as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._json(500, {"ok": False, "error": f"Unexpected server error: {exc}"})

    return DashboardHandler


def main():
    database = os.path.join(HERE, "pm.db")
    pm = PM(database)
    server = ThreadingHTTPServer(("127.0.0.1", 8765), create_handler(pm))
    server.daemon_threads = True
    url = "http://127.0.0.1:8765/"
    print(f"Smart Healthcare PM dashboard: {url}")
    print(f"Database: {database}")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard.")
    finally:
        server.server_close()
        pm.db.close()


if __name__ == "__main__":
    main()
