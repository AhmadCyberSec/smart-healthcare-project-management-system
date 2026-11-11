"""test_step2.py - Step 2 test cases with expected vs actual results.
Run:  python test_step2.py"""
import sys
from pm_core import PM, PMError

results = []


def check(tc, description, expected, actual):
    ok = str(expected) in str(actual)
    results.append((tc, description, str(expected), str(actual), "PASS" if ok else "FAIL"))


def error_of(action):
    try:
        action()
        return "No error raised"
    except PMError as e:
        return str(e)


def code_of(pm, item_id):
    return [i for i in pm.wbs_items() if i["id"] == item_id][0]["code"]


def item(pm, item_id):
    return [i for i in pm.wbs_items() if i["id"] == item_id][0]


pm = PM(":memory:")
pm.create_charter("Healthcare PMS", "Manage hospitals", "Management",
                  "Five modules", "Pharmacy", 5_000_000, 16, "2026-09-01")

# ---- Requirements ----
r1 = pm.add_requirement("Patient appointments", "Book and cancel", "High")
check("TC01", "New requirement starts as Proposed", "Proposed", pm.get_requirement(r1)["status"])
check("TC02", "Empty requirement title", "Requirement title cannot be empty.",
      error_of(lambda: pm.add_requirement(" ", "", "High")))
check("TC03", "Invalid priority", "Priority must be one of",
      error_of(lambda: pm.add_requirement("X", "", "Urgent")))
check("TC04", "Duplicate title (case-insensitive)", "already exists",
      error_of(lambda: pm.add_requirement("PATIENT APPOINTMENTS", "", "High")))
pm.update_requirement(r1, priority="Medium")
check("TC05", "Update priority", "Medium", pm.get_requirement(r1)["priority"])
check("TC06", "Status cannot be edited directly", "cannot be updated",
      error_of(lambda: pm.update_requirement(r1, status="Approved")))
pm.approve_requirement(r1)
check("TC07", "Approve requirement", "Approved", pm.get_requirement(r1)["status"])
r2 = pm.add_requirement("Lab reports", "", "Low")
pm.reject_requirement(r2)
check("TC08", "Reject requirement", "Rejected", pm.get_requirement(r2)["status"])
check("TC09", "Rejected requirement cannot be edited", "rejected requirement cannot be edited",
      error_of(lambda: pm.update_requirement(r2, priority="High")))
check("TC10", "Cannot approve a rejected requirement", "Only proposed",
      error_of(lambda: pm.approve_requirement(r2)))
r3 = pm.add_requirement("Billing", "", "High")
pm.approve_requirement(r3)
check("TC11", "Requirements sorted by priority", "Billing", pm.requirements()[0]["title"])

# ---- WBS and scope control ----
r4 = pm.add_requirement("Unapproved idea", "", "High")
check("TC12", "Unapproved requirement blocked from WBS", "not approved",
      error_of(lambda: pm.add_wbs_item("Idea", requirement_id=r4)))
check("TC13", "Top-level item needs a requirement", "must be linked",
      error_of(lambda: pm.add_wbs_item("Orphan")))
d1 = pm.add_wbs_item("Appointment module", requirement_id=r1)
check("TC14", "First deliverable code", "1", code_of(pm, d1))
c1 = pm.add_wbs_item("Design", parent_id=d1)
check("TC15", "Child code", "1.1", code_of(pm, c1))
g1 = pm.add_wbs_item("UI mockups", parent_id=c1)
check("TC16", "Grandchild code", "1.1.1", code_of(pm, g1))
d2 = pm.add_wbs_item("Billing module", requirement_id=r3)
check("TC17", "Second deliverable code", "2", code_of(pm, d2))
check("TC18", "Child inherits requirement", r1, item(pm, c1)["requirement_id"])
check("TC19", "Leaf item is a Work Package", "Work Package", item(pm, g1)["type"])
check("TC20", "Top item is a Deliverable", "Deliverable", item(pm, d1)["type"])
check("TC21", "Missing parent", "Parent WBS item not found",
      error_of(lambda: pm.add_wbs_item("X", parent_id=999)))

# ---- Change requests ----
cr1 = pm.submit_change_request("AI diagnosis module", "Hospital request", "AI triage", "High", 500_000, 2)
cr = pm.change_requests()[0]
check("TC22", "Change request starts Pending", "Pending", cr["status"])
check("TC23", "Its requirement starts Proposed", "Proposed", pm.get_requirement(cr["requirement_id"])["status"])
check("TC24", "Negative cost rejected", "must be zero or greater",
      error_of(lambda: pm.submit_change_request("Neg cost CR", "why", "", "Low", -5, 1)))
check("TC25", "Missing justification", "Justification cannot be empty.",
      error_of(lambda: pm.submit_change_request("No reason CR", " ", "", "Low", 1, 1)))
check("TC26", "Failed submission leaves no requirement", "0",
      len([r for r in pm.requirements() if r["title"] in ("Neg cost CR", "No reason CR")]))
ai = cr["requirement_id"]
check("TC27", "Approve CR requirement directly blocked", "change request",
      error_of(lambda: pm.approve_requirement(ai)))
check("TC28", "AI module blocked from WBS before approval", "not approved",
      error_of(lambda: pm.add_wbs_item("AI module", requirement_id=ai)))
res = pm.approve_change_request(cr1, "Approved")
check("TC29", "Approval raises budget", "5500000.0", pm.get_project()["budget"])
check("TC30", "Approval extends deadline (weeks)", "18", pm.get_project()["deadline_weeks"])
check("TC31", "Approval approves the requirement", "Approved", pm.get_requirement(ai)["status"])
d3 = pm.add_wbs_item("AI module", requirement_id=ai)
check("TC32", "Approved CR requirement enters the WBS", "3", code_of(pm, d3))
check("TC33", "Approve twice blocked", "already Approved",
      error_of(lambda: pm.approve_change_request(cr1)))
cr2 = pm.submit_change_request("Mobile application", "Patient access", "App", "Medium", 300_000, 1)
pm.approve_change_request(cr2)
check("TC34", "Case study totals (budget, weeks)", "5800000.0 19",
      f"{pm.get_project()['budget']} {pm.get_project()['deadline_weeks']}")
check("TC35", "Baseline budget preserved", "5000000.0", pm.baseline()["budget"])
check("TC36", "Baseline deadline preserved (weeks)", "16", pm.baseline()["deadline_weeks"])
cr3 = pm.submit_change_request("Pharmacy inventory", "One hospital asked", "", "Low", 900_000, 4)
pm.reject_change_request(cr3, "Out of scope")
rej = [c for c in pm.change_requests() if c["id"] == cr3][0]
check("TC37", "Rejected CR and requirement", "Rejected Rejected",
      f"{rej['status']} {pm.get_requirement(rej['requirement_id'])['status']}")
check("TC38", "Rejection leaves budget unchanged", "5800000.0", pm.get_project()["budget"])
check("TC39", "Rejected CR cannot be approved", "already Rejected",
      error_of(lambda: pm.approve_change_request(cr3)))
pm.submit_change_request("Another idea", "Reason", "", "Low", 1000, 0)
check("TC40", "Pending change request count", "1", pm.pending_change_requests())

# ---- results ----
print(f"{'ID':<5}{'Test case':<44}{'Expected':<34}{'Actual':<34}Result")
print("-" * 125)
cut = lambda s, n: s if len(s) <= n else s[:n - 3] + "..."
for tc, desc, exp, act, res in results:
    print(f"{tc:<5}{cut(desc, 42):<44}{cut(exp, 32):<34}{cut(act, 32):<34}{res}")
passed = sum(r[4] == "PASS" for r in results)
print(f"\n{passed}/{len(results)} test cases passed")
sys.exit(0 if passed == len(results) else 1)
