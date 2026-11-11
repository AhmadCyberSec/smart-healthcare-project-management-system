"""test_step1.py - test cases for Step 1 with expected vs actual results.
Run:  python test_step1.py"""
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


def fresh(with_charter=True):
    pm = PM(":memory:")
    if with_charter:
        pm.create_charter("Healthcare PMS", "Manage hospitals", "Management",
                          "Five modules", "Pharmacy", 5_000_000, 16, "2026-09-01")
    return pm


# TC01-TC06: charter creation and validation
pm = fresh()
check("TC01", "Create valid charter: status", "Initiating", pm.get_project()["status"])
check("TC02", "Create valid charter: budget", "5000000.0", pm.get_project()["budget"])
check("TC03", "Empty project name",
      "Name cannot be empty.",
      error_of(lambda: fresh(False).create_charter(" ", "o", "s", "i", "x", 1, 1, "2026-09-01")))
check("TC04", "Budget of zero", "Budget must be greater than zero.",
      error_of(lambda: fresh(False).create_charter("n", "o", "s", "i", "x", 0, 16, "2026-09-01")))
check("TC05", "Wrong date format", "YYYY-MM-DD",
      error_of(lambda: fresh(False).create_charter("n", "o", "s", "i", "x", 1, 16, "01-09-2026")))
check("TC06", "Second charter rejected", "already exists",
      error_of(lambda: pm.create_charter("n", "o", "s", "i", "x", 1, 16, "2026-09-01")))

# TC07-TC08: charter update and plan
pm.update_charter(budget=5_800_000, deadline_weeks=19)
check("TC07", "Update budget and deadline", "5800000.0 19",
      f"{pm.get_project()['budget']} {pm.get_project()['deadline_weeks']}")
pm.update_plan("scope", "schedule", "cost", "quality")
check("TC08", "Saving plan moves status", "Planning", pm.get_project()["status"])

# TC09-TC12: status workflow
check("TC09", "Illegal status jump", "Cannot move from Planning to Monitoring",
      error_of(lambda: pm.set_status("Monitoring")))
check("TC10", "Close directly via set_status", "Use close_project()",
      error_of(lambda: pm.set_status("Closed")))
check("TC11", "Unknown status", "Status must be one of",
      error_of(lambda: pm.set_status("Finished")))
pm.set_status("Executing", "Started")
check("TC12", "Valid move to Executing", "Executing", pm.get_project()["status"])

# TC13-TC17: milestones
pm.add_milestone("Design done", 5, "Backend Dev")
pm.add_milestone("Go-live", 19, "Project Manager")
check("TC13", "Milestone after deadline", "between 1 and 19",
      error_of(lambda: pm.add_milestone("Late", 30, "PM")))
check("TC14", "Duplicate milestone", "already exists",
      error_of(lambda: pm.add_milestone("design DONE", 6, "PM")))
check("TC15", "Deadline cut below a milestone", "fall after the new deadline",
      error_of(lambda: pm.update_charter(deadline_weeks=10)))
check("TC16", "Initial milestone progress (%)", "0", pm.milestone_progress()["pct"])
pm.achieve_milestone(pm.milestones()[0]["id"])
check("TC17", "Progress after 1 of 2 achieved (%)", "50", pm.milestone_progress()["pct"])

# TC18-TC20: closure
check("TC18", "Close with pending milestone", "Pending milestones: Go-live",
      error_of(lambda: pm.close_project("Done")))
pm.achieve_milestone(pm.milestones()[1]["id"])
pm.close_project("Delivered", "Lessons")
check("TC19", "Close after all achieved", "Closed", pm.get_project()["status"])
check("TC20", "Edit after closure blocked", "project is closed",
      error_of(lambda: pm.update_charter(budget=1)))

# ---- print results table ----
print(f"{'ID':<5}{'Test case':<38}{'Expected':<38}{'Actual':<38}Result")
print("-" * 125)
for tc, desc, exp, act, res in results:
    cut = lambda s, n: s if len(s) <= n else s[:n - 3] + "..."
    print(f"{tc:<5}{cut(desc,36):<38}{cut(exp,36):<38}{cut(act,36):<38}{res}")
passed = sum(r[4] == "PASS" for r in results)
print(f"\n{passed}/{len(results)} test cases passed")
sys.exit(0 if passed == len(results) else 1)
