"""step1_demo.py - run this to see Step 1 working with the case study data."""
import os
from pm_core import PM, PMError

if os.path.exists("demo.db"):
    os.remove("demo.db")
pm = PM("demo.db")

pm.create_charter(
    name="Smart Healthcare Project Management and Monitoring System",
    objectives="Manage appointments, lab reports, doctor schedules, online "
               "consultations and billing for a network of five hospitals.",
    stakeholders="Hospital management, doctors, patients, billing staff, development company",
    scope_in="Appointments, lab reports, doctor schedules, online consultations, billing",
    scope_out="Pharmacy inventory, insurance claims, hardware procurement",
    budget=5_000_000, deadline_weeks=16, start_date="2026-09-01")

pm.update_plan(
    scope="Five modules as listed in the charter; changes only via approved change requests.",
    schedule="16 weeks: requirements, design, development, testing, deployment.",
    cost="Approved budget PKR 5,000,000; Earned Value reviewed weekly.",
    quality="Every deliverable inspected; no critical defects at release.")

for name, week, owner in [("Requirements signed off", 3, "Project Manager"),
                          ("Design completed", 5, "Backend Developer"),
                          ("Development complete", 12, "Backend Developer"),
                          ("Testing complete", 15, "QA Engineer"),
                          ("Go-live", 16, "Project Manager")]:
    pm.add_milestone(name, week, owner)
pm.set_status("Executing", "Development started")

print(pm.charter_report())

print("\nVALIDATION CHECKS")
checks = [
    ("Close with pending milestones", lambda: pm.close_project("Done")),
    ("Milestone after deadline", lambda: pm.add_milestone("Late", 40, "PM")),
    ("Duplicate milestone", lambda: pm.add_milestone("Go-live", 16, "PM")),
    ("Invalid status", lambda: pm.set_status("Finished")),
    ("Illegal status jump", lambda: pm.set_status("Initiating")),
    ("Zero budget", lambda: pm.update_charter(budget=0)),
]
for label, action in checks:
    try:
        action()
        print(f"  {label}: NOT blocked (problem!)")
    except PMError as e:
        print(f"  {label}: blocked -> {e}")

for m in pm.milestones():
    pm.achieve_milestone(m["id"])
pm.close_project("Delivered to all five hospitals.", "Freeze scope earlier.")
print("\nSTATUS HISTORY")
for s in pm.rows("SELECT logged_on, status, note FROM status_log"):
    print(f"  {s['status']:<11} {s['note']}")
