"""Focused regression tests for schedule, cost, quality and risk modules."""
import sys
from pm_core import PM, PMError


def expect_error(action, text):
    try:
        action()
    except PMError as exc:
        assert text.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"Expected PMError containing {text!r}")


pm = PM(":memory:")
pm.create_charter("Healthcare PMS", "Manage hospitals", "Management",
                  "Healthcare modules", "Pharmacy", 5_000_000, 16, "2026-09-01")
requirement = pm.add_requirement("Appointments", "Bookings", "High")
pm.approve_requirement(requirement)
wbs = pm.add_wbs_item("Appointment module", requirement_id=requirement)
team = [member["name"] for member in pm.team_members()]

first = pm.add_activity("Design", team[0], 2, 200, 1, wbs_id=wbs)
second = pm.add_activity("Build", team[1], 3, 300, 1, [first], wbs_id=wbs)
third = pm.add_activity("Review", team[2], 1, 100, 1, [second], wbs_id=wbs)
activities = {activity["id"]: activity for activity in pm.activities()}
assert (activities[first]["start_week"], activities[first]["end_week"]) == (1, 2)
assert (activities[second]["start_week"], activities[second]["end_week"]) == (3, 5)
expect_error(lambda: pm.set_activity_dependencies(first, [second]), "cycle")
activities = {activity["id"]: activity for activity in pm.activities()}
assert (activities[first]["start_week"], activities[first]["end_week"]) == (1, 2)
assert activities[second]["dependency_names"] == "Design"
forecast = {activity["id"]: activity for activity in pm.schedule_forecast(4)["activities"]}
assert forecast[second]["forecast_end_week"] == 6
assert forecast[third]["forecast_start_week"] == 7 and forecast[third]["delay_weeks"] == 1
expect_error(lambda: pm.add_activity("Bad assignee", "Unknown", 1, 10), "not in the project team")
expect_error(lambda: pm.update_activity_progress(first, 101, 200), "between 0 and 100")

pm.update_activity_progress(first, 50, 150)
evm = pm.earned_value(current_week=1)
assert (evm["pv"], evm["ev"], evm["ac"]) == (100, 100, 150)
assert round(evm["cpi"], 2) == 0.67 and round(evm["spi"], 2) == 1.0
assert any("CPI" in warning for warning in evm["warnings"])

defect = pm.add_defect("Slot conflict", "Concurrent bookings overlap", "Critical", "QA Engineer")
assert pm.defects(unresolved_only=True)[0]["id"] == defect
pm.update_defect(defect, "Resolved")
assert not pm.defects(unresolved_only=True)
check = pm.add_quality_check("Appointments", "No conflicting slots")
pm.record_quality_result(check, "Fail", "Race condition found")
assert pm.quality_checks()[0]["result"] == "Fail"
risk = pm.add_risk("Schedule delay", "Defects delay QA", 4, 5,
                   "Run automated tests", "Add a defect-fix sprint")
assert pm.risks()[0]["id"] == risk and pm.risks()[0]["score"] == 20
dashboard = pm.dashboard()
assert dashboard["unresolved_defect_count"] == 0
assert dashboard["evm"]["ac"] == 150

closed = PM(":memory:")
closed.create_charter("Closed project", "Test reporting", "Team", "Scope", "None",
                      1000, 2, "2026-09-01")
closed.close_project("Complete")
assert closed.dashboard()["project"]["status"] == "Closed"

print("Schedule, cycle validation, EVM, defects, inspections, risk matrix and dashboard: PASS")
pm.db.close()
closed.db.close()
sys.exit(0)
