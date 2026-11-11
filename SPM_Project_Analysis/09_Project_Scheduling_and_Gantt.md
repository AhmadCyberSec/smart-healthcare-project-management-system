# Chapter 6 support: Project Scheduling, Milestones, and Gantt Data

## What the repository establishes

`pm_core.py` schedules activity records from durations, requested start weeks, and predecessor links. It derives dates from project start date, reports delayed activities, and computes a forecast. The database and seed files provide illustrative week numbers but not a verified historical schedule.

### Sample milestone inconsistency

`sample_data.sql` lists requirements sign-off at week 3, design at 5, development at 12, testing at 15, and go-live at 16, while also showing approved changes that extend duration to 19 weeks. The runtime sample in `web_app.py` instead places testing at week 18 and go-live at week 19. The current `pm.db` contains no milestones. Confirm the authoritative plan before reporting schedule performance.

## Proposed schedule baseline (planning example only)

The following 19-week outline reconciles the 16-week original sample duration and 3 weeks of sample change impact. It is a proposed sequencing model, not an actual or approved schedule. No calendar/resource leveling has been confirmed.

| ID | Phase/activity | Start week | Duration | Finish week | Predecessor | Checkpoint / exit evidence |
|---|---|---:|---:|---:|---|---|
| S1 | Requirements and scope confirmation | 1 | 3 | 3 | — | Requirements accepted |
| S2 | Architecture/design | 4 | 2 | 5 | S1 | Design review approved |
| S3 | Project-management core/dashboard implementation | 6 | 6 | 11 | S2 | Feature-complete build |
| S4 | System, integration, and regression testing | 12 | 3 | 14 | S3 | Critical defects resolved; test evidence |
| S5 | UAT, release readiness, deployment preparation | 15 | 2 | 16 | S4 | Stakeholder acceptance and go/no-go |
| S6 | Sample AI/mobile change implementation | 17 | 3 | 19 | S5 | Only if actual scope, feasibility, and safety are approved |

The project’s operational healthcare requirements are not implemented; S3 above refers to the project-management software evidenced by this workspace, not a completed patient-care product. S6 is only a case-study change label and requires separate feasibility/design work.

## Gantt chart data (proposed week-based model)

`█` = scheduled work; `·` = no scheduled work. W01–W19 denote weeks, not dates.

```text
Activity / week     01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19
Requirements        ██ ██ ██ ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
Architecture/design ·  ·  ·  ██ ██ ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
Core/dashboard      ·  ·  ·  ·  ·  ██ ██ ██ ██ ██ ██ ·  ·  ·  ·  ·  ·  ·  ·
System test         ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ██ ·  ·  ·  ·  ·
UAT/release prep    ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ·  ·  ·
AI/mobile change    ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ██
```

## Monitoring rules proposed

1. Maintain approved baseline separately from forecast; never silently rebaseline after a delay.
2. Report actual start/finish, remaining duration, percent complete, cost actuals, dependency changes, and forecast variance weekly.
3. Escalate critical-path slip, a forecast beyond week 19, any critical open defect, and change impacts without approval.
4. Record milestone acceptance evidence and decision owner, not status alone.
5. Reconcile activity estimates with approved budget; the current sample activities total PKR 5,000,000 while the revised charter is PKR 5,800,000, leaving PKR 800,000 not allocated to the listed activity estimates.

## Schedule calculation caveat

In the current forecast algorithm, unfinished activities whose planned start week is already reached use a start based on the reporting week, while the dependency-based predecessor forecast is calculated separately. Verify whether such in-progress dependent work should also be constrained by a delayed predecessor; add a focused regression case before relying on forecast dates. This is a code-review observation, not a verified production incident.
