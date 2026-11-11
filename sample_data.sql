-- Sample data for the complete Smart Healthcare case study
-- Load with:  sqlite3 pm.db < sample_data.sql   (after schema.sql has been applied)

INSERT INTO project(id,name,objectives,stakeholders,scope_in,scope_out,budget,
                    deadline_weeks,start_date,status,plan_scope,plan_schedule,plan_cost,plan_quality)
VALUES (1,
 'Smart Healthcare Project Management and Monitoring System',
 'Manage appointments, lab reports, doctor schedules, online consultations and billing for a network of five hospitals.',
 'Hospital management, doctors, patients, billing staff, development company',
 'Appointments, lab reports, doctor schedules, online consultations, billing',
 'Pharmacy inventory, insurance claims, hardware procurement',
 5800000, 19, '2026-09-01', 'Executing',
 'Five modules as listed in the charter; changes only via approved change requests.',
 '16 weeks: requirements, design, development, testing, deployment.',
 'Approved baseline PKR 5,000,000 plus PKR 800,000 in approved changes; review EVM weekly.',
 'Inspect each deliverable; resolve critical defects before release.');

INSERT INTO milestones(name,due_week,owner,status) VALUES
 ('Requirements signed off', 3, 'Project Manager',   'Pending'),
 ('Design completed',        5, 'Backend Developer', 'Pending'),
 ('Development complete',   12, 'Backend Developer', 'Pending'),
 ('Testing complete',       15, 'QA Engineer',       'Pending'),
 ('Go-live',                16, 'Project Manager',   'Pending');

INSERT INTO status_log(status,note) VALUES
 ('Initiating','Charter created'),
 ('Planning','Plan approved, moving to planning'),
 ('Executing','Development started');

 -- ===================== Step 2 sample data =====================

INSERT INTO requirements(id,title,description,priority,status,source) VALUES
 (1,'Patient appointment management','Book, reschedule and cancel appointments','High','Approved','Original'),
 (2,'Laboratory reports','Upload and view lab results','High','Approved','Original'),
 (3,'Doctor schedules','Manage doctor availability','High','Approved','Original'),
 (4,'Online consultations','Video consultations','Medium','Approved','Original'),
 (5,'Hospital billing','Invoices and payments','High','Approved','Original'),
 (6,'AI-based preliminary diagnosis','Suggests a preliminary diagnosis from symptoms','High','Approved','Change Request'),
 (7,'Mobile application','Patient mobile app for appointments and reports','Medium','Approved','Change Request');

INSERT INTO wbs(id,parent_id,code,name,requirement_id) VALUES
 (1,NULL,'1','Appointment Management',1),(2,1,'1.1','Design appointment module',1),(3,1,'1.2','Develop scheduling engine',1),
 (4,NULL,'2','Laboratory Reports',2),(5,4,'2.1','Develop report upload',2),(6,4,'2.2','Develop report viewer',2),
 (7,NULL,'3','Doctor Schedules',3),(8,7,'3.1','Develop roster screen',3),(9,7,'3.2','Develop availability rules',3),
 (10,NULL,'4','Online Consultations',4),(11,10,'4.1','Develop video session',4),(12,10,'4.2','Develop consultation notes',4),
 (13,NULL,'5','Hospital Billing',5),(14,13,'5.1','Develop invoicing',5),(15,13,'5.2','Develop payment tracking',5),
 (16,NULL,'6','AI Diagnosis Module',6),(17,NULL,'7','Mobile Application',7);

INSERT INTO change_requests(id,title,justification,requirement_id,cost_impact,weeks_impact,status,
                            decision_note,budget_before,budget_after,weeks_before,weeks_after) VALUES
 (1,'AI-based preliminary diagnosis','Hospital management wants faster patient triage',6,500000,2,
  'Approved','Approved by steering committee',5000000,5500000,16,18),
 (2,'Mobile application','Patients need access from their phones',7,300000,1,
  'Approved','Approved by steering committee',5500000,5800000,18,19);

INSERT INTO team_members(id,name,role) VALUES
 (1,'Project Manager','Project Manager'),
 (2,'Backend Developer 1','Backend Developer'),
 (3,'Backend Developer 2','Backend Developer'),
 (4,'Frontend Developer 1','Frontend Developer'),
 (5,'Frontend Developer 2','Frontend Developer'),
 (6,'Database Developer','Database Developer'),
 (7,'QA Engineer','Quality Assurance');

INSERT INTO activities(id,name,assigned_to,duration_weeks,estimated_cost,actual_cost,
                       percent_complete,requested_start_week,start_week,end_week,wbs_id) VALUES
 (1,'Requirements and design','Project Manager',3,700000,700000,100,1,1,3,2),
 (2,'Appointment scheduling module','Backend Developer 1',4,900000,520000,55,4,4,7,3),
 (3,'Patient records and reports','Backend Developer 2',4,800000,470000,45,4,4,7,5),
 (4,'Frontend screens','Frontend Developer 1',5,700000,250000,30,5,5,9,8),
 (5,'Database integration','Database Developer',3,500000,180000,20,5,5,7,9),
 (6,'System and defect testing','QA Engineer',3,600000,0,0,12,12,14,11),
 (7,'AI and mobile enhancements','Backend Developer 1',3,800000,0,0,17,17,19,16);

INSERT INTO activity_dependencies(activity_id,depends_on_id) VALUES
 (2,1),(3,1),(4,1),(5,1),(6,2),(6,3),(6,4),(6,5),(7,6);

INSERT INTO defects(title,description,severity,assigned_to,status) VALUES
 ('Appointment slot conflicts','Concurrent bookings can claim the same slot.','Critical','QA Engineer','Open'),
 ('Patient record validation failure','Incomplete records bypass validation.','High','Backend Developer 2','Open');

INSERT INTO quality_checks(deliverable,criterion,result,notes,inspected_on) VALUES
 ('Appointment scheduling','No overlapping reservations under concurrent use','Fail',
  'Concurrency defect requires correction.',datetime('now')),
 ('Patient records','Required fields validated and access is traceable','Not Tested','',NULL),
 ('Billing','Invoice totals reconcile with payments','Not Tested','',NULL);

INSERT INTO risks(title,description,likelihood,impact,preventive_action,corrective_action,status) VALUES
 ('Critical defect delays deployment','Appointment defects may extend system testing.',4,5,
  'Run concurrency and regression suites on every build.',
  'Add focused fix sprint and re-sequence dependent release tasks.','Open'),
 ('Approved change pressure','AI/mobile additions add cost and three weeks.',3,4,
  'Use change control and reserve capacity.',
  'Reforecast baseline and obtain steering approval.','Open');
