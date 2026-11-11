"""step2_demo.py - requirements, WBS and change requests with the case study."""
import os
from pm_core import PM, PMError

if os.path.exists("demo2.db"):
    os.remove("demo2.db")
pm = PM("demo2.db")
pm.create_charter("Smart Healthcare Project Management and Monitoring System",
                  "Manage appointments, lab reports, schedules, consultations and billing.",
                  "Hospital management, doctors, patients, billing staff",
                  "Appointments, lab reports, doctor schedules, online consultations, billing",
                  "Pharmacy inventory, insurance claims", 5_000_000, 16, "2026-09-01")


def show(title):
    print(f"\n=== {title} ===")


def attempt(label, action):
    try:
        action()
        print(f"  {label}: allowed")
    except PMError as e:
        print(f"  {label}: BLOCKED -> {e}")


show("1. Requirements (original five approved)")
plan = [("Patient appointment management", "Book, reschedule, cancel", "High",
         "Appointment Management", ["Design appointment module", "Develop scheduling engine", "Test appointment module"]),
        ("Laboratory reports", "Upload and view lab results", "High",
         "Laboratory Reports", ["Develop report upload", "Develop report viewer"]),
        ("Doctor schedules", "Manage doctor availability", "High",
         "Doctor Schedules", ["Develop roster screen", "Develop availability rules"]),
        ("Online consultations", "Video consultations", "Medium",
         "Online Consultations", ["Develop video session", "Develop consultation notes"]),
        ("Hospital billing", "Invoices and payments", "High",
         "Hospital Billing", ["Develop invoicing", "Develop payment tracking"])]
req_ids = []
for title, desc, pri, _, _ in plan:
    rid = pm.add_requirement(title, desc, pri)
    pm.approve_requirement(rid)
    req_ids.append(rid)
sms = pm.add_requirement("SMS appointment reminders", "Text reminders", "Low")
print(f"  5 requirements approved; 'SMS appointment reminders' left as {pm.get_requirement(sms)['status']}")

show("2. Scope control: unapproved requirement cannot enter the WBS")
attempt("Add 'SMS reminders' to WBS", lambda: pm.add_wbs_item("SMS reminders", requirement_id=sms))

show("3. Hierarchical WBS")
for rid, (_, _, _, name, packages) in zip(req_ids, plan):
    deliverable = pm.add_wbs_item(name, requirement_id=rid)
    wp = [pm.add_wbs_item(p, parent_id=deliverable) for p in packages]
    if name == "Appointment Management":
        pm.add_wbs_item("Slot-conflict checking", parent_id=wp[1])
        pm.add_wbs_item("Doctor availability lookup", parent_id=wp[1])
print(pm.wbs_text())

show("4. Hospital management requests two new features (change requests)")
cr_ai = pm.submit_change_request("AI-based preliminary diagnosis",
                                 "Hospital management wants faster patient triage",
                                 "Suggests a preliminary diagnosis from symptoms", "High", 500_000, 2)
cr_mob = pm.submit_change_request("Mobile application",
                                  "Patients need access from their phones",
                                  "Patient mobile app", "Medium", 300_000, 1)
ai_req = pm.change_requests()[0]["requirement_id"]
print(f"  Pending change requests: {pm.pending_change_requests()}")
attempt("Add AI module to WBS before approval", lambda: pm.add_wbs_item("AI module", requirement_id=ai_req))
attempt("Approve AI requirement directly", lambda: pm.approve_requirement(ai_req))

show("5. Approving change requests changes scope, budget and schedule")
for cr in (cr_ai, cr_mob):
    r = pm.approve_change_request(cr, "Approved by steering committee")
    print(f"  CR{cr} approved: PKR {r['budget_before']:,.0f} -> {r['budget_after']:,.0f} | "
          f"{r['weeks_before']} -> {r['weeks_after']} weeks")
d_ai = pm.add_wbs_item("AI Diagnosis Module", requirement_id=ai_req)
pm.add_wbs_item("Develop symptom analysis model", parent_id=d_ai)
d_mob = pm.add_wbs_item("Mobile Application", requirement_id=pm.change_requests()[1]["requirement_id"])
pm.add_wbs_item("Develop mobile screens", parent_id=d_mob)
print("  Both requirements are now Approved and their deliverables are in the WBS.")

show("6. A rejected change request leaves everything unchanged")
cr_ph = pm.submit_change_request("Pharmacy inventory integration", "Requested by one hospital",
                                 "Outside charter scope", "Low", 900_000, 4)
pm.reject_change_request(cr_ph, "Out of scope per charter")
print(f"  Budget still PKR {pm.get_project()['budget']:,.0f}, deadline {pm.get_project()['deadline_weeks']} weeks")

print("\n" + pm.scope_report())
