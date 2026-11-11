"""HTTP integration tests for the browser dashboard and its project API."""
import json
import threading
import urllib.error
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from pm_core import PM
from web_app import create_handler


pm = PM(":memory:")
server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(pm))
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f"http://127.0.0.1:{server.server_port}"


def get(path):
    with urlopen(base + path, timeout=5) as response:
        return response.status, response.headers.get_content_type(), response.read()


def post(path, payload):
    request = Request(
        base + path, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read())


try:
    assert get("/")[1] == "text/html"
    assert get("/styles.css")[1] == "text/css"
    assert get("/app.js")[0] == 200
    assert get("/favicon.svg")[1] == "image/svg+xml"
    initial = json.loads(get("/api/state")[2])
    assert initial["project"] is None

    sample = post("/api/sample", {})["state"]
    assert sample["project"]["budget"] == 5_800_000
    assert sample["project"]["deadline_weeks"] == 19
    assert len(sample["activities"]) == 7
    assert len(sample["milestones"]) == 5
    assert len(sample["defects"]) == 2
    assert sample["dashboard"]["evm"]["pv"] >= 0

    requirement_result = post("/api/add-requirement", {
        "title": "Patient portal security", "description": "Protect patient data", "priority": "High"
    })["state"]
    requirement_id = next(r["id"] for r in requirement_result["requirements"]
                         if r["title"] == "Patient portal security")
    try:
        post("/api/add-wbs", {"name": "Unapproved work", "requirement_id": requirement_id})
    except urllib.error.HTTPError as exc:
        assert exc.code == 400
    else:
        raise AssertionError("Unapproved requirement entered the WBS.")
    post("/api/decide-requirement", {"id": requirement_id, "decision": "approve"})
    post("/api/add-wbs", {"name": "Patient portal security", "requirement_id": requirement_id})

    members = sample["team_members"]
    state = post("/api/add-activity", {
        "name": "API integration test activity", "assigned_to": members[0]["name"],
        "duration_weeks": 2, "estimated_cost": 25_000, "start_week": 1
    })["state"]
    activity_one = next(a["id"] for a in state["activities"] if a["name"] == "API integration test activity")
    state = post("/api/add-activity", {
        "name": "API dependent test activity", "assigned_to": members[1]["name"],
        "duration_weeks": 1, "estimated_cost": 10_000, "start_week": 1,
        "dependencies": [activity_one]
    })["state"]
    activity_two = next(a["id"] for a in state["activities"] if a["name"] == "API dependent test activity")
    state = post("/api/update-activity", {
        "id": activity_one, "percent_complete": 50, "actual_cost": 20_000
    })["state"]
    assert next(a for a in state["activities"] if a["id"] == activity_two)["start_week"] == 3
    assert state["dashboard"]["evm"]["ac"] == 1_710_000

    change_id = post("/api/submit-change", {
        "title": "Additional triage workflow", "justification": "Hospital request",
        "description": "Triage", "priority": "Medium", "cost_impact": 10_000, "weeks_impact": 1
    })["state"]["change_requests"][-1]["id"]
    approved = post("/api/decide-change", {
        "id": change_id, "decision": "approve", "note": "Approved during test"
    })["state"]
    assert approved["project"]["budget"] == 5_810_000
    assert approved["project"]["deadline_weeks"] == 20

    rejected_id = post("/api/submit-change", {
        "title": "Out-of-scope pharmacy change", "justification": "Test rejection",
        "description": "Not included", "priority": "Low", "cost_impact": 0, "weeks_impact": 0
    })["state"]["change_requests"][-1]["id"]
    rejected = post("/api/decide-change", {
        "id": rejected_id, "decision": "reject", "note": "Out of scope"
    })["state"]
    assert next(c for c in rejected["change_requests"] if c["id"] == rejected_id)["status"] == "Rejected"

    state = post("/api/add-defect", {
        "title": "API integration defect", "description": "Test defect",
        "severity": "Critical", "assigned_to": "QA Engineer"
    })["state"]
    defect_id = next(d["id"] for d in state["defects"] if d["title"] == "API integration defect")
    assert next(d for d in post("/api/update-defect", {
        "id": defect_id, "status": "Resolved"
    })["state"]["defects"] if d["id"] == defect_id)["status"] == "Resolved"

    state = post("/api/add-quality-check", {
        "deliverable": "API integration test", "criterion": "Endpoint returns expected data"
    })["state"]
    quality_id = next(q["id"] for q in state["quality_checks"] if q["deliverable"] == "API integration test")
    assert next(q for q in post("/api/record-quality", {
        "id": quality_id, "result": "Pass", "notes": "Verified"
    })["state"]["quality_checks"] if q["id"] == quality_id)["result"] == "Pass"

    state = post("/api/add-risk", {
        "title": "API integration test risk", "description": "Test risk",
        "likelihood": 2, "impact": 4, "preventive_action": "Test",
        "corrective_action": "Respond"
    })["state"]
    risk_id = next(r["id"] for r in state["risks"] if r["title"] == "API integration test risk")
    risks = post("/api/update-risk", {"id": risk_id, "status": "Mitigated"})["state"]["risks"]
    assert next(r for r in risks if r["id"] == risk_id)["status"] == "Mitigated"

    state = post("/api/add-milestone", {
        "name": "API integration test milestone", "due_week": 19, "owner": members[0]["name"]
    })["state"]
    milestone_id = next(m["id"] for m in state["milestones"] if m["name"] == "API integration test milestone")
    post("/api/achieve-milestone", {"id": milestone_id})
    assert "PROJECT CHARTER" in post("/api/export", {})["report"]
    current_state = json.loads(get("/api/state")[2])
    for milestone in current_state["milestones"]:
        if milestone["status"] == "Pending":
            post("/api/achieve-milestone", {"id": milestone["id"]})
    closed = post("/api/close-project", {
        "summary": "API test completed", "lessons": "Regression test passed"
    })["state"]["project"]
    assert closed["status"] == "Closed"

    try:
        post("/api/add-requirement", {"title": " ", "priority": "High"})
    except urllib.error.HTTPError as exc:
        assert exc.code == 400
    else:
        raise AssertionError("Invalid requirement data was not rejected.")
    print("Browser dashboard HTTP/API regression: PASS")
finally:
    server.shutdown()
    server.server_close()
    pm.db.close()
    thread.join(timeout=3)
