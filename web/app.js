const state = {
  data: null,
  page: "dashboard",
  search: "",
  filters: {},
  collapse: new Set()
};

const icons = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  briefcase: '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path dm3 12 9 5 9-5M3 16l9 5 9-5"/>',
  tree: '<rect x="8" y="3" width="8" height="5" rx="1"/><rect x="2" y="16" width="7" height="5" rx="1"/><rect x="15" y="16" width="7" height="5" rx="1"/><path d="M12 8v4M5.5 16v-3h13v3"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  wallet: '<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 9h18M16 14h2M7 5V3h11"/>',
  chart: '<path d="M3 3v18h18"/><path d="m8 14 4-4 4 3 5-7"/>',
  shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/>',
  triangle: '<path d="m10.3 4.3-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-2.7l-8-14a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  arrows: '<path d="M17 3h4v4M3 17v4h4M21 3l-7 7M3 21l7-7M14 3h-4a7 7 0 0 0-7 7v1M10 21h4a7 7 0 0 0 7-7v-1"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>'
};
document.querySelectorAll("[data-icon]").forEach(node => {
  node.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[node.dataset.icon] || ""}</svg>`;
});

const pageNames = {
  dashboard: "Overview", charter: "Project charter", scope: "Scope & requirements",
  wbs: "Work breakdown structure", schedule: "Project schedule", resources: "Team & resources",
  cost: "Cost management", evm: "Earned value analysis", quality: "Quality & defects",
  risks: "Risk register", changes: "Change requests", reports: "Reports"
};
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));
const money = value => `PKR ${Number(value || 0).toLocaleString("en-PK", {maximumFractionDigits: 0})}`;
const fmtDate = value => value ? new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {day:"2-digit",month:"short",year:"numeric"}) : "—";
const initials = value => String(value || "?").split(/\s+/).slice(0,2).map(part => part[0]).join("").toUpperCase();
const pct = value => `${Math.round(Number(value || 0))}%`;
const badge = (label, color = "gray") => `<span class="badge badge-${color}">${esc(label)}</span>`;
const priorityBadge = value => `<span class="badge priority-${String(value || "low").toLowerCase()}">${esc(value || "—")}</span>`;
const severityBadge = value => `<span class="badge severity-${String(value || "low").toLowerCase()}">${esc(value || "—")}</span>`;
const pageHeading = (title, subtitle, actions = "") =>
  `<div class="page-heading"><div><h1>${title}</h1><p>${subtitle}</p></div><div class="heading-actions">${actions}</div></div>`;
const button = (label, action, primary = false, icon = "") =>
  `<button class="button ${primary ? "button-primary" : ""}" data-action="${action}">${icon}${label}</button>`;
const empty = (title, description, action = "") =>
  `<div class="notice-empty"><div><span class="empty-icon">✦</span><strong>${title}</strong><p>${description}</p>${action}</div></div>`;
const panel = (title, subtitle, content, action = "") =>
  `<section class="panel"><div class="panel-header"><div><h2>${title}</h2>${subtitle ? `<p>${subtitle}</p>` : ""}</div>${action}</div>${content}</section>`;
const table = (headers, rows, emptyTitle = "Nothing here yet", emptyText = "Add a record to get started.") =>
  `<div class="table-scroll"><table class="data-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows || `<tr><td colspan="${headers.length}" class="empty-row">${emptyTitle} — ${emptyText}</td></tr>`}</tbody></table></div>`;
const actionButton = (action, id, title, glyph = "⋯") =>
  `<button class="icon-action" data-action="${action}" data-id="${id}" title="${esc(title)}">${glyph}</button>`;
const searchToolbar = (placeholder = "Search records...", filters = "") =>
  `<div class="toolbar"><div class="toolbar-left"><label class="search-box">⌕ <input data-search placeholder="${placeholder}" value="${esc(state.search)}"></label>${filters}</div><div class="toolbar-right"><span class="subtle text-small" data-result-count></span></div></div>`;

async function api(action, payload = {}) {
  const response = await fetch(`/api/${action}`, {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
  });
  const result = await response.json();
  if (!response.ok || !result.ok) throw new Error(result.error || "Request failed.");
  if (result.state) state.data = result.state;
  toast(result.message || "Saved successfully.");
  render();
  return result;
}
async function refresh(showToast = false) {
  try {
    const response = await fetch("/api/state", {cache:"no-store"});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to load project data.");
    state.data = result;
    render();
    $("#last-updated").textContent = `Updated ${new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}`;
    if (showToast) toast("Project data refreshed.");
  } catch (error) {
    toast(error.message, true);
  }
}
function toast(message, error = false) {
  const item = document.createElement("div");
  item.className = `toast${error ? " error" : ""}`;
  item.innerHTML = `<span class="toast-icon">${error ? "!" : "✓"}</span><span>${esc(message)}</span>`;
  $("#toast-region").append(item);
  setTimeout(() => item.remove(), 3800);
}
function navigate(page) {
  state.page = page;
  state.search = "";
  state.collapse.clear();
  document.querySelectorAll(".nav-item").forEach(item => item.classList.toggle("active", item.dataset.page === page));
  $("#breadcrumb-title").textContent = pageNames[page] || "Overview";
  $("#sidebar").classList.remove("open");
  render();
}
function render() {
  const data = state.data;
  if (!data) {
    $("#main-content").innerHTML = `<div class="notice-empty"><span class="loading"><i class="spinner"></i>Loading project workspace…</span></div>`;
    return;
  }
  $("#breadcrumb-title").textContent = pageNames[state.page] || "Overview";
  $("#top-project-name").textContent = data.project?.name || "";
  $("#top-project-status").innerHTML = data.project ? badge(data.project.status,statusColor(data.project.status)) : "";
  const delayCount = data.dashboard?.delayed_activities?.length || 0;
  $("#delay-count").textContent = delayCount;
  $("#defect-count").textContent = data.dashboard?.critical_defects?.length || 0;
  $("#change-count").textContent = data.dashboard?.pending_change_requests || 0;
  const renderers = {
    dashboard: renderDashboard, charter: renderCharter, scope: renderScope, wbs: renderWbs,
    schedule: renderSchedule, resources: renderResources, cost: renderCost,
    evm: renderEvm, quality: renderQuality, risks: renderRisks,
    changes: renderChanges, reports: renderReports
  };
  $("#main-content").innerHTML = renderers[state.page]();
  bindPage();
  if (state.page === "dashboard" || state.page === "evm") drawValueChart();
}
function renderDashboard() {
  const {project, dashboard} = state.data;
  if (!project) return `${pageHeading("Good morning", "Your healthcare project workspace is ready.")}<section class="welcome-card"><div><span class="eyebrow">SMART HEALTHCARE PROJECT</span><h2>Bring your project into focus.</h2><p>Load the complete five-hospital case study or set up a project charter to get started.</p><div class="heading-actions" style="margin-top:14px">${button("Load case-study project","sample",true)}${button("Create a charter","create-charter")}</div></div><div class="welcome-art">✚</div></section>${empty("A clear view of every project milestone","Your dashboard will display project health, EVM, delivery progress, quality and scope once project data is available.")}`;
  const evm = dashboard.evm;
  const progress = dashboard.progress_pct;
  const critical = dashboard.critical_defects.length;
  const openChanges = dashboard.pending_change_requests;
  const approvedChanges = state.data.change_requests.filter(change => change.status === "Approved");
  const baseline = project.budget - approvedChanges.reduce((sum, change) => sum + change.cost_impact, 0);
  const baselineWeeks = project.deadline_weeks - approvedChanges.reduce((sum, change) => sum + change.weeks_impact, 0);
  const forecast = dashboard.schedule_forecast;
  const health = projectHealth(dashboard, state.data);
  const cards = [
    ["Progress", pct(progress), "Overall completion", "◉", "", progress],
    ["Approved budget", money(project.budget), `${money(baseline)} original baseline`, "$", "blue", Math.min(100, evm.ac / Math.max(project.budget,1) * 100)],
    ["Project duration", `${project.deadline_weeks} weeks`, `${baselineWeeks} weeks baseline · ${forecast.deadline_variance_weeks ? `${forecast.deadline_variance_weeks}w forecast overrun` : "within deadline"}`, "◷", "amber", Math.min(100, Math.max(0, 100 - forecast.deadline_variance_weeks * 5))],
    ["Critical defects", String(critical), `${dashboard.unresolved_defect_count} unresolved in total`, "⚑", "red", null],
    ["Change requests", String(openChanges), `${approvedChanges.length} approved and in scope`, "⇄", "purple", null]
  ];
  const cardsHtml = cards.map(([label,value,caption,icon,color,width]) => `<article class="metric-card"><div class="metric-top"><span class="metric-label">${label}</span><span class="metric-icon ${color}">${icon}</span></div><div class="metric-value ${String(value).length > 13 ? "compact" : ""}">${esc(value)}</div><div class="metric-caption">${esc(caption)}</div>${width !== null ? `<div class="mini-progress"><span style="width:${width}%"></span></div>` : ""}</article>`).join("");
  const changes = state.data.change_requests.slice(0,4).map(change => `<tr><td><strong>CR-${change.id}</strong></td><td><strong>${esc(change.title)}</strong><span class="table-subtext">${esc(change.justification)}</span></td><td class="currency">${money(change.cost_impact)}</td><td>${change.weeks_impact} wk</td><td>${badge(change.status,statusColor(change.status))}</td></tr>`).join("");
  const activityRows = dashboard.activities.slice(0,5).map(activity => `<div class="schedule-preview-row"><span class="schedule-name">${esc(activity.name)}</span><div class="schedule-bar"><span class="${activity.end_week < evm.week && activity.percent_complete < 100 ? "delayed" : ""}" style="width:${Math.max(3,activity.percent_complete)}%"></span></div><span class="schedule-pct">${pct(activity.percent_complete)}</span></div>`).join("");
  const warnings = evm.warnings.length ? `<div class="warning-list">${evm.warnings.map(text => `<div class="warning ${text.includes("CPI") || text.includes("budget") ? "critical" : ""}"><span>⚠</span>${esc(text)}</div>`).join("")}</div>` : "";
  return `${pageHeading("Project overview", "A live view of delivery health across scope, schedule, cost and quality.", `${button("Refresh data","refresh")}${button("Add update","update-activity",true,"＋ ")}`)}
    <div class="kpi-grid">${cardsHtml}</div>
    <div class="dashboard-grid">
      ${panel("Project progress", "Delivery status against the approved plan", `<div class="panel-body"><div class="project-summary"><div class="project-mark">✚</div><div><strong>${esc(project.name)}</strong><small>Started ${fmtDate(project.start_date)} · ${dashboard.activities.length} scheduled activities</small></div><span style="margin-left:auto">${badge(project.status,statusColor(project.status))}</span></div><div class="progress-row"><span>Overall completion</span><strong>${progress}%</strong></div><div class="progress-track"><span style="width:${progress}%"></span></div><div class="phase-row"><span class="done">Initiation</span><span class="${progress > 10 ? "done" : ""}">Planning</span><span class="${progress > 30 ? "done" : ""}">Execution</span><span>Delivery</span></div><div class="section-title"><h2>Earned value trend</h2><div class="chart-legend"><span><i class="legend-dot"></i>PV</span><span><i class="legend-dot blue"></i>EV</span><span><i class="legend-dot amber"></i>AC</span></div></div><div class="chart-wrap"><canvas class="chart" id="value-chart"></canvas></div></div>`)}
      ${panel("Project health", "Live indicators based on current records", `<div class="panel-body"><div class="health-list">${Object.entries(health).map(([name,value])=>`<div class="health-item"><span class="health-name">${name}</span><span class="health-state ${value.tone}"><i class="health-dot"></i>${value.label}</span></div>`).join("")}</div><div style="margin-top:13px;padding-top:12px;border-top:1px solid #edf1f4"><span class="eyebrow">CURRENT FORECAST</span><div style="margin-top:6px;color:#43566b;font-size:11px;font-weight:600">Week ${forecast.projected_end_week} <span class="subtle">of ${project.deadline_weeks}</span></div><span class="table-subtext">${forecast.deadline_variance_weeks ? `${forecast.deadline_variance_weeks} week forecast variance` : "Forecast finish remains within approved deadline"}</span></div></div>`)}
    </div>
    <div class="dashboard-lower">
      ${panel("Delivery schedule", "Activity completion at a glance", `<div class="panel-body"><div class="schedule-preview">${activityRows || `<span class="subtle text-small">No scheduled activities yet.</span>`}</div></div>`, `<button class="panel-link" data-page="schedule">View schedule →</button>`)}
      ${panel("Recent change requests", "Scope, budget and timeline decisions", table(["CHANGE","COST IMPACT","SCHEDULE","STATUS"],changes,"No change requests","Submitted change requests will appear here."), `<button class="panel-link" data-page="changes">View all →</button>`)}
    </div>${warnings}`;
}
function projectHealth(dashboard, data) {
  const evm = dashboard.evm, forecast = dashboard.schedule_forecast;
  const openCritical = dashboard.critical_defects.length;
  const openRisks = data.risks.filter(risk => risk.status === "Open" && risk.score >= 15).length;
  const delayed = dashboard.delayed_activities.length;
  const criticalHealth = forecast.deadline_variance_weeks > 0 || evm.cost_overrun || openCritical > 0;
  const atRiskHealth = delayed > 0 || openRisks > 0 ||
    (evm.cpi !== null && evm.cpi < .9) || (evm.spi !== null && evm.spi < .9);
  return {
    "Overall project": {label:criticalHealth ? "Critical" : atRiskHealth ? "At risk" : "On track",
      tone:criticalHealth ? "critical" : atRiskHealth ? "at-risk" : ""},
    "Scope control": {label:`${data.requirements.filter(r=>r.status==="Approved").length} approved`,tone:""},
    "Schedule": {label:forecast.deadline_variance_weeks ? `${forecast.deadline_variance_weeks}w forecast delay` : delayed ? `${delayed} delayed activities` : "On track",tone:forecast.deadline_variance_weeks ? "critical" : delayed ? "at-risk" : ""},
    "Cost performance": {label:evm.cost_overrun ? "Over budget" : evm.cpi !== null && evm.cpi < .9 ? "At risk" : "On track",tone:evm.cost_overrun ? "critical" : evm.cpi !== null && evm.cpi < .9 ? "at-risk" : ""},
    "Quality": {label:openCritical ? `${openCritical} critical defect${openCritical > 1 ? "s" : ""}` : "No critical defects",tone:openCritical ? "critical" : ""},
    "Risk exposure": {label:openRisks ? `${openRisks} high-risk item${openRisks > 1 ? "s" : ""}` : "Controlled",tone:openRisks ? "at-risk" : ""}
  };
}
function renderCharter() {
  const {project} = state.data;
  if (!project) return `${pageHeading("Project charter","Define objectives, boundaries, budget and governance.",button("Create project charter","create-charter",true,"＋ "))}${empty("No project charter yet","Create a charter to establish the approved baseline and project governance.",button("Create charter","create-charter",true))}`;
  const detail = (label,value,span=false) => `<div class="detail-card ${span?"span-2":""}"><label>${label}</label><p>${esc(value || "Not provided")}</p></div>`;
  const statusOptions = ["Initiating","Planning","Executing","Monitoring"].map(status=>`<option ${project.status===status?"selected":""}>${status}</option>`).join("");
  return `${pageHeading("Project charter","Project definition, approved baselines and governance.",`${button("Edit charter","edit-charter")}${button("Edit management plan","edit-plan",true)}`)}
    <div class="grid-two">
      <div class="stack">${panel("Project information","Approved project baseline",`<div class="panel-body"><div class="charter-grid">
        ${detail("Project name",project.name,true)}${detail("Project status",project.status)}${detail("Start date",fmtDate(project.start_date))}${detail("Approved budget",money(project.budget))}${detail("Project duration",`${project.deadline_weeks} weeks`)}${detail("Original baseline",`${money(state.data.change_requests.filter(c=>c.status==="Approved").reduce((s,c)=>s+c.cost_impact,0) ? project.budget-state.data.change_requests.filter(c=>c.status==="Approved").reduce((s,c)=>s+c.cost_impact,0) : project.budget)} · ${project.deadline_weeks-state.data.change_requests.filter(c=>c.status==="Approved").reduce((s,c)=>s+c.weeks_impact,0)} weeks`)}
        ${detail("Project objectives",project.objectives,true)}${detail("Stakeholders",project.stakeholders,true)}${detail("In scope",project.scope_in,true)}${detail("Out of scope",project.scope_out,true)}</div></div>`)}
      ${panel("Project management plan","Scope, schedule, cost and quality approach",`<div class="panel-body"><div class="charter-grid">${detail("Scope management",project.plan_scope,true)}${detail("Schedule approach",project.plan_schedule,true)}${detail("Cost management",project.plan_cost,true)}${detail("Quality approach",project.plan_quality,true)}</div></div>`)}
      </div>
      <div class="stack">${panel("Project status","Advance through the project lifecycle",`<div class="panel-body"><div class="field"><label>Current project status</label><select id="project-status">${statusOptions}</select></div><button class="button button-primary" style="margin-top:11px" data-action="change-project-status">Save project status</button></div>`)}
      ${panel("Milestones & responsibilities","Named checkpoints and accountable owners",`${searchToolbar("Search milestones...")}${table(["MILESTONE","DUE WEEK","OWNER","STATUS","ACTION"],state.data.milestones.map(m=>`<tr data-search-row><td><strong>${esc(m.name)}</strong></td><td>Week ${m.due_week}</td><td>${esc(m.owner)}</td><td>${badge(m.status,m.status==="Achieved"?"green":"gray")}</td><td>${m.status==="Pending"?actionButton("achieve-milestone",m.id,"Mark achieved","✓"):"—"}</td></tr>`).join(""),"No milestones","Add milestone checkpoints to track delivery.")}`,button("Add milestone","add-milestone",false,"＋ "))}
      ${panel("Project closure","Record final outcomes and lessons learned",`<div class="panel-body">${state.data.closures.length?`<div class="detail-card"><label>Closed ${esc(state.data.closures[0].closed_on)}</label><p>${esc(state.data.closures[0].summary)}</p><span class="table-subtext">${esc(state.data.closures[0].lessons||"")}</span></div>`:`<p class="subtle text-small">Closure becomes available after all milestones are achieved.</p>`}<button class="button ${project.status==="Closed"?"button-quiet":"button-primary"}" style="margin-top:11px" data-action="close-project" ${project.status==="Closed"?"disabled":""}>Record project closure</button></div>`)}
      </div></div>`;
}
function renderScope() {
  const requirements = state.data.requirements;
  const rows = filterRows(requirements, r=>`${r.id} ${r.title} ${r.description} ${r.priority} ${r.status}`).map(r=>`<tr data-search-row><td><strong>REQ-${String(r.id).padStart(3,"0")}</strong></td><td><div class="table-primary"><span class="table-avatar teal">${initials(r.title)}</span><span><strong>${esc(r.title)}</strong><span class="table-subtext">${esc(r.description||"No description")}</span></span></div></td><td>${priorityBadge(r.priority)}</td><td>${badge(r.status,statusColor(r.status))}</td><td>${r.source==="Change Request"?badge("Change request","purple"):badge("Original scope","gray")}</td><td><div class="table-actions">${r.status==="Proposed"&&r.source!=="Change Request"?`${actionButton("edit-requirement",r.id,"Edit","✎")}${actionButton("requirement-approve",r.id,"Approve","✓")}${actionButton("requirement-reject",r.id,"Reject","×")}`:"—"}</div></td></tr>`).join("");
  return `${pageHeading("Scope & requirements","Maintain the approved scope baseline and control requirement changes.",`${button("New requirement","add-requirement",false,"＋ ")}${button("Submit change request","add-change",true,"⇄ ")}`)}
    <div class="grid-three" style="margin-bottom:14px">${summaryCard("Total requirements",requirements.length,"Tracked project requirements","blue")}${summaryCard("Approved scope",requirements.filter(r=>r.status==="Approved").length,"Eligible for WBS delivery","green")}${summaryCard("Awaiting decision",requirements.filter(r=>r.status==="Proposed").length,"Proposed and change-linked","amber")}</div>
    ${panel("Requirements register","Prioritized scope with explicit approval control",`${searchToolbar("Search requirements…",`<select class="select-control" data-filter="requirement-status"><option value="">All statuses</option><option>Approved</option><option>Proposed</option><option>Rejected</option></select><select class="select-control" data-filter="requirement-priority"><option value="">All priorities</option><option>High</option><option>Medium</option><option>Low</option></select>`)}${table(["REQUIREMENT ID","REQUIREMENT","PRIORITY","APPROVAL STATUS","SOURCE","ACTIONS"],rows,"No matching requirements","Add a requirement or adjust your filters.")}`,`<span class="subtle text-small">${requirements.length} records</span>`)}`;
}
function summaryCard(label,value,caption,color="blue") {
  const symbol = color==="green"?"✓":color==="amber"?"◷":color==="red"?"!":"◈";
  return `<article class="metric-card"><div class="metric-top"><span class="metric-label">${label}</span><span class="metric-icon ${color==="red"?"red":color==="amber"?"amber":color==="green"?"":"blue"}">${symbol}</span></div><div class="metric-value">${esc(value)}</div><div class="metric-caption">${caption}</div></article>`;
}
function buildWbsTree(items) {
  const nodes = new Map(items.map(item=>[item.id,{...item,children:[]}]));
  const roots=[];
  nodes.forEach(node=>{ if(node.parent_id && nodes.has(node.parent_id)) nodes.get(node.parent_id).children.push(node); else roots.push(node);});
  const draw=(node,depth)=>`<div class="tree-row" data-search-row style="padding-left:${depth*15}px">${node.children.length?`<button class="tree-toggle" data-action="toggle-wbs" data-id="${node.id}">${state.collapse.has(node.id)?"›":"⌄"}</button>`:`<span class="tree-spacer"></span>`}<span class="tree-code">${esc(node.code)}</span><span class="tree-name" style="${depth===0?"font-weight:600;color:#31465c":""}">${esc(node.name)}</span><span class="tree-req">${node.type==="Deliverable"?"Deliverable":node.type||"Work package"}</span>${actionButton("add-child-wbs",node.id,"Add child item","＋")}</div>${!state.collapse.has(node.id)?node.children.map(child=>draw(child,depth+1)).join(""):""}`;
  return roots.map(root=>draw(root,0)).join("")||`<div class="notice-empty">No WBS items yet. Link top-level deliverables to approved requirements.</div>`;
}
function renderWbs() {
  return `${pageHeading("Work breakdown structure","Explore the approved project scope from deliverables to work packages.",button("Add WBS item","add-wbs",true,"＋ "))}
    ${panel("Hierarchical WBS","Expand a deliverable to view its child work packages.",`<div class="toolbar"><span class="subtle text-small">${state.data.wbs.length} scope items · only approved requirements can enter the WBS</span><label class="search-box">⌕ <input data-search placeholder="Search WBS…" value="${esc(state.search)}"></label></div><div class="tree-list" id="wbs-tree">${buildWbsTree(state.data.wbs)}</div>`)}`;
}
function renderSchedule() {
  const forecast=state.data.dashboard?.schedule_forecast;
  const rows=filterRows(state.data.activities,a=>`${a.id} ${a.name} ${a.assigned_to} ${a.dependency_names}`).map(a=>{
    const delayed=forecast?.activities.find(item=>item.id===a.id)?.delayed;
    const status=a.percent_complete>=100?["Complete","green"]:delayed?["Delayed","red"]:a.percent_complete>0?["In progress","yellow"]:["Upcoming","gray"];
    return `<tr data-search-row><td><strong>ACT-${String(a.id).padStart(3,"0")}</strong></td><td><div class="table-primary"><span class="table-avatar">${initials(a.name)}</span><span><strong>${esc(a.name)}</strong><span class="table-subtext">${esc(a.dependency_names||"No predecessors")}</span></span></div></td><td>${esc(a.assigned_to)}</td><td>${a.duration_weeks} weeks</td><td>${fmtDate(a.start_date)}</td><td>${fmtDate(a.end_date)}</td><td><div class="inline-progress"><span class="progress-track"><span style="width:${a.percent_complete}%"></span></span><small>${pct(a.percent_complete)}</small></div></td><td>${badge(status[0],status[1])}</td><td class="table-actions">${actionButton("update-activity",a.id,"Update progress","✎")}${actionButton("dependencies",a.id,"Edit dependencies","↗")}</td></tr>`;
  }).join("");
  const forecastHtml=forecast?`<span class="badge ${forecast.deadline_variance_weeks?"badge-red":"badge-green"}">Forecast week ${forecast.projected_end_week} · ${forecast.deadline_variance_weeks?`${forecast.deadline_variance_weeks} week variance`:"within deadline"}</span>`:"";
  return `${pageHeading("Schedule & delivery","Dependency-driven activity dates, ownership and delivery forecast.",`${forecastHtml}${button("Add activity","add-activity",true,"＋ ")}`)}
    <div class="grid-three" style="margin-bottom:14px">${summaryCard("Activities",state.data.activities.length,"Scheduled project work","blue")}${summaryCard("Delayed activities",forecast?.delayed.length||0,"Unfinished work past baseline","red")}${summaryCard("Team members",state.data.team_members.length,"Assigned project resources","green")}</div>
    ${panel("Project timeline","Activity duration is measured from the project start date.",`<div class="panel-body"><div class="timeline">${state.data.activities.length?state.data.activities.map(a=>{const projected=forecast?.activities.find(x=>x.id===a.id);const late=projected?.delayed||projected?.delay_weeks>0;const tone=a.percent_complete===100?"status-done":late?"status-delayed":a.percent_complete>0?"status-active":"status-pending";return `<div class="timeline-item ${tone}"><div><strong>${esc(a.name)}</strong><small>${esc(a.assigned_to)} · ${a.duration_weeks} wk · ${esc(a.dependency_names||"No dependencies")}</small></div><div class="timeline-track"><span class="${tone}" style="left:${Math.max(0,(a.start_week-1)/(Math.max(1,forecast?.projected_end_week||1))*100)}%;width:${Math.max(3,(a.duration_weeks/Math.max(1,forecast?.projected_end_week||1))*100)}%"></span></div><div class="timeline-dates">${fmtDate(a.start_date)} — ${fmtDate(a.end_date)}<small>${pct(a.percent_complete)} · Forecast ${projected?.forecast_end_week?`wk ${projected.forecast_end_week}`:"—"}</small></div></div>`}).join(""):empty("No activities scheduled","Create activities and link predecessor work to generate the timeline.")}</div></div>`)}
    <div class="section-title"><div><h2>Activity register</h2><p>Filter work, owners, dependencies and actual delivery progress.</p></div><div class="heading-actions">${button("Add team member","add-member")}${button("Add activity","add-activity",true,"＋ ")}</div></div>
    ${panel("Scheduled activities",`${state.data.activities.length} activities in the current delivery plan`,`${searchToolbar("Search activities or team members…")}${table(["ACTIVITY","OWNER","DURATION","START DATE","END DATE","PROGRESS","STATUS","ACTIONS"],rows,"No matching activities","Adjust your search or create a scheduled activity.")}`)}`;
}
function renderResources() {
  const members=filterRows(state.data.team_members,m=>`${m.name} ${m.role}`).map(m=>`<tr data-search-row><td><div class="table-primary"><span class="table-avatar teal">${initials(m.name)}</span><strong>${esc(m.name)}</strong></div></td><td>${esc(m.role)}</td><td>${state.data.activities.filter(a=>a.assigned_to.toLowerCase()===m.name.toLowerCase()).length} activities</td><td>${money(state.data.activities.filter(a=>a.assigned_to.toLowerCase()===m.name.toLowerCase()).reduce((s,a)=>s+a.estimated_cost,0))}</td></tr>`).join("");
  return `${pageHeading("Team & resources","Project roles, assigned work and estimated activity investment.",button("Add team member","add-member",true,"＋ "))}<div class="grid-three" style="margin-bottom:14px">${summaryCard("Team members",state.data.team_members.length,"Project delivery team","blue")}${summaryCard("Assigned activities",state.data.activities.length,"Across the project schedule","green")}${summaryCard("Estimated activity cost",money(state.data.activities.reduce((s,a)=>s+a.estimated_cost,0)),"Sum of current task estimates","amber")}</div>${panel("Project team","Delivery capacity and work ownership",`${searchToolbar("Search team members or roles…")}${table(["TEAM MEMBER","ROLE","ASSIGNED WORK","ACTIVITY ESTIMATE"],members,"No team members","Add team members to assign work.")}`)}`;
}
function renderCost() {
  const project=state.data.project, evm=state.data.dashboard?.evm;
  if(!project)return `${pageHeading("Cost management","Monitor approved budget, activity estimates and actual spend.")}${empty("No project cost baseline","Create a project charter to define an approved budget.")}`;
  const rows=state.data.activities.map(a=>`<tr data-search-row><td><strong>${esc(a.name)}</strong><span class="table-subtext">Owner: ${esc(a.assigned_to)}</span></td><td class="currency">${money(a.estimated_cost)}</td><td class="currency">${money(a.actual_cost)}</td><td>${money(a.estimated_cost-a.actual_cost)}</td><td><div class="inline-progress"><span class="progress-track"><span style="width:${Math.min(100,a.actual_cost/Math.max(a.estimated_cost,1)*100)}"></span></span><small>${Math.round(a.actual_cost/Math.max(a.estimated_cost,1)*100)}%</small></div></td><td>${actionButton("update-activity",a.id,"Update actual expenditure","✎")}</td></tr>`).join("");
  return `${pageHeading("Cost management","Review the approved budget against task-level estimates and actual expenditure.",button("Update activity actuals","update-activity",true,"✎ "))}
    <div class="grid-three" style="margin-bottom:14px">${summaryCard("Approved budget",money(project.budget),"Includes approved changes","blue")}${summaryCard("Planned activity cost",money(evm.planned_budget),"Current activity estimates",evm.cost_overrun?"red":"green")}${summaryCard("Actual expenditure",money(evm.ac),`Budget remaining ${money(evm.budget_variance)}`,evm.ac>project.budget?"red":"amber")}</div>
    ${evm.warnings.length?`<div class="warning-list">${evm.warnings.map(x=>`<div class="warning critical">⚠ ${esc(x)}</div>`).join("")}</div>`:""}
    ${panel("Activity cost register","Estimated and actual cost data flows directly into earned value analysis.",`${searchToolbar("Search activities or owners…")}${table(["ACTIVITY","ESTIMATED COST","ACTUAL COST","VARIANCE","COST UTILIZATION","ACTIONS"],rows,"No costed activities","Add scheduled activities and record their actual expenditure.")}`)}`;
}
function renderEvm() {
  const evm=state.data.dashboard?.evm;
  if(!evm)return `${pageHeading("Earned value analysis","Programmatic cost and schedule performance indicators.")}${empty("Earned value is ready when a project is created","Create project activities and update completion and actual cost to calculate PV, EV, AC, CPI and SPI.")}`;
  const cards=[["Planned value · PV",money(evm.pv),"Budgeted work scheduled by report week","blue"],["Earned value · EV",money(evm.ev),"Budgeted value of completed work",""],["Actual cost · AC",money(evm.ac),"Actual expenditure to date","amber"],["Cost index · CPI",evm.cpi===null?"—":evm.cpi.toFixed(2),"EV ÷ AC · target ≥ 0.90",evm.cpi!==null&&evm.cpi<.9?"red":""],["Schedule index · SPI",evm.spi===null?"—":evm.spi.toFixed(2),"EV ÷ PV · target ≥ 0.90",evm.spi!==null&&evm.spi<.9?"red":""]];
  const activityRows=state.data.activities.map(a=>`<tr data-search-row><td><strong>${esc(a.name)}</strong></td><td class="currency">${money(valueForActivity(a,evm.week,"pv"))}</td><td class="currency">${money(a.estimated_cost*a.percent_complete/100)}</td><td class="currency">${money(a.actual_cost)}</td><td>${pct(a.percent_complete)}</td></tr>`).join("");
  return `${pageHeading("Earned value analysis","Performance indicators are recalculated from activity estimates, completion and actuals.",`${button("Update activity actuals","update-activity")}${button("Refresh values","refresh",true,"↻ ")}`)}
    ${evm.warnings.length?`<div class="warning-list">${evm.warnings.map(text=>`<div class="warning ${text.includes("CPI")?"critical":""}">⚠ ${esc(text)}</div>`).join("")}</div>`:`<div class="warning" style="background:#eaf7f0;color:#348062;margin-bottom:13px">✓ Cost and schedule indicators are within the configured performance threshold.</div>`}
    <div class="evm-kpis">${cards.map(([title,value,caption,color])=>`<article class="evm-card"><small>${title}</small><strong class="${color}">${value}</strong><span>${caption}</span></article>`).join("")}</div>
    <div class="grid-two" style="margin-bottom:15px">${panel("Performance comparison",`Reporting week ${evm.week} · PV / EV / AC`, `<div class="panel-body"><div class="chart-wrap" style="height:230px"><canvas class="chart" id="value-chart"></canvas></div><div class="chart-legend"><span><i class="legend-dot"></i>PV</span><span><i class="legend-dot blue"></i>EV</span><span><i class="legend-dot amber"></i>AC</span></div></div>`)}
    ${panel("Budget control","Approved project budget compared with estimates and actual spend",`<div class="panel-body"><div class="progress-row"><span>Actual cost vs approved budget</span><strong>${money(evm.ac)} / ${money(evm.approved_budget)}</strong></div><div class="progress-track"><span style="width:${Math.min(100,evm.ac/Math.max(evm.approved_budget,1)*100)}%;background:${evm.ac>evm.approved_budget?"#db6469":"#25aa96"}"></span></div><div class="section-title"><h2>Activity estimate</h2><span class="currency">${money(evm.planned_budget)}</span></div><div class="progress-row"><span>Budget variance</span><strong style="color:${evm.budget_variance<0?"#c54d53":"#238260"}">${money(evm.budget_variance)}</strong></div><span class="table-subtext">Budget variance = approved budget − actual cost.</span></div>`)}</div>
    ${panel("Activity-level earned value","PV is time-phased across each activity; EV is based on reported completion.",`${searchToolbar("Search activities…")}${table(["ACTIVITY","PLANNED VALUE","EARNED VALUE","ACTUAL COST","COMPLETE"],activityRows,"No activities","Create scheduled activities to calculate earned value.")}`)}`;
}
function valueForActivity(activity,week,which){if(which!=="pv")return 0;const elapsed=Math.max(0,Math.min(activity.duration_weeks,week-activity.start_week+1));return activity.estimated_cost*elapsed/activity.duration_weeks;}
function renderQuality() {
  const defects=state.data.defects;
  const rows=filterRows(defects,d=>`${d.id} ${d.title} ${d.severity} ${d.assigned_to} ${d.status} ${d.description}`).map(d=>`<tr data-search-row><td><strong>DEF-${String(d.id).padStart(3,"0")}</strong></td><td><strong>${esc(d.title)}</strong><span class="table-subtext">${esc(d.description||"No description")}</span></td><td>${severityBadge(d.severity)}</td><td>${esc(d.assigned_to)}</td><td>${badge(d.status,d.status==="Resolved"?"green":d.status==="In Progress"?"yellow":"red")}</td><td>${fmtDate(d.created_on?.slice(0,10))}</td><td>${actionButton("update-defect",d.id,"Update defect status","✎")}</td></tr>`).join("");
  const checks=state.data.quality_checks.map(check=>`<tr data-search-row><td><strong>${esc(check.deliverable)}</strong></td><td>${esc(check.criterion)}</td><td>${badge(check.result,check.result==="Pass"?"green":check.result==="Fail"?"red":"gray")}</td><td>${esc(check.notes||"—")}</td><td>${actionButton("record-quality",check.id,"Record inspection","✎")}</td></tr>`).join("");
  return `${pageHeading("Quality & defects","Track software defects, delivery inspections and release readiness.",button("Record defect","add-defect",true,"＋ "))}
    <div class="grid-three" style="margin-bottom:14px">${summaryCard("Total defects",defects.length,"Recorded quality issues","blue")}${summaryCard("Open defects",defects.filter(d=>d.status!=="Resolved").length,"Require investigation or a fix","amber")}${summaryCard("Critical defects",defects.filter(d=>d.severity==="Critical"&&d.status!=="Resolved").length,"Unresolved release blockers","red")}</div>
    <div class="grid-two"><div class="stack">${panel("Defect register","Severity, ownership and current resolution status",`${searchToolbar("Search defects…")}${table(["DEFECT","TITLE & DESCRIPTION","SEVERITY","ASSIGNED TO","STATUS","REPORTED","ACTIONS"],rows,"No defects recorded","Create a defect to begin quality tracking.")}`)}
    ${panel("Deliverable inspections","Record acceptance checks and test results",`${searchToolbar("Search quality checklist…")}${table(["DELIVERABLE","INSPECTION CRITERION","RESULT","NOTES","ACTION"],checks,"No inspections configured","Add deliverables and quality acceptance criteria.")}`,button("Add checklist item","add-quality-check",false,"＋ "))}</div>
    <div>${panel("Quality release signals","Aggregate quality evidence for project health",`<div class="panel-body">${qualityScoreCard("Critical defects",defects.filter(d=>d.severity==="Critical"&&d.status!=="Resolved").length?"Release attention required":"No open critical defects",defects.filter(d=>d.severity==="Critical"&&d.status!=="Resolved").length?"critical":"green")}${qualityScoreCard("Inspection failures",state.data.quality_checks.filter(q=>q.result==="Fail").length?`${state.data.quality_checks.filter(q=>q.result==="Fail").length} deliverables failed checks`:"No recorded failures",state.data.quality_checks.some(q=>q.result==="Fail")?"critical":"green")}${qualityScoreCard("Resolved defects",`${defects.filter(d=>d.status==="Resolved").length} of ${defects.length} resolved`,"blue")}</div>`)}
    ${panel("Test readiness","Acceptance checks that must pass before release",`<div class="panel-body"><div class="progress-row"><span>Passing checklist items</span><strong>${state.data.quality_checks.filter(q=>q.result==="Pass").length} / ${state.data.quality_checks.length}</strong></div><div class="progress-track"><span style="width:${state.data.quality_checks.length?state.data.quality_checks.filter(q=>q.result==="Pass").length/state.data.quality_checks.length*100:0}%"></span></div></div>`)}</div></div>`;
}
function qualityScoreCard(title,value,tone){return `<div class="health-item"><span class="health-name">${title}</span><span class="health-state ${tone==="critical"?"critical":tone==="amber"?"at-risk":""}"><i class="health-dot"></i>${esc(value)}</span></div>`;}
function renderRisks() {
  const risks=state.data.risks;
  const rows=filterRows(risks,r=>`${r.id} ${r.title} ${r.description} ${r.status} ${r.preventive_action} ${r.corrective_action}`).map(r=>`<tr data-search-row><td><strong>RSK-${String(r.id).padStart(3,"0")}</strong></td><td><strong>${esc(r.title)}</strong><span class="table-subtext">${esc(r.description)}</span></td><td>${r.likelihood} / 5</td><td>${r.impact} / 5</td><td><strong>${r.score}</strong></td><td>${badge(r.score>=20?"Critical":r.score>=15?"High":r.score>=8?"Moderate":"Low",r.score>=20?"red":r.score>=15?"yellow":r.score>=8?"blue":"green")}</td><td><span class="table-subtext">Prevent: ${esc(r.preventive_action)}</span><span class="table-subtext">Respond: ${esc(r.corrective_action)}</span></td><td>${badge(r.status,r.status==="Open"?"yellow":"green")}</td><td>${actionButton("update-risk",r.id,"Update risk status","✎")}</td></tr>`).join("");
  const matrix=`<span class="risk-label">L / I</span>${[1,2,3,4,5].map(i=>`<span class="risk-label">${i}</span>`).join("")}${[5,4,3,2,1].map(likelihood=>`<span class="risk-label">${likelihood}</span>${[1,2,3,4,5].map(impact=>{const cell=risks.filter(r=>r.likelihood===likelihood&&r.impact===impact);const score=likelihood*impact,tone=score>=20?"critical":score>=12?"high":score>=6?"medium":"low";return `<div class="risk-cell ${tone}" title="Likelihood ${likelihood} × impact ${impact}">${cell.map((r,i)=>`<span class="${r.score<15?"medium":""}" style="transform:translate(${(i%2)*9}px,${Math.floor(i/2)*9}px)">${r.id}</span>`).join("")}</div>`}).join("")}`).join("")}`;
  return `${pageHeading("Risk management","Assess exposure by likelihood and impact, then track response plans.",button("Add risk","add-risk",true,"＋ "))}
    <div class="grid-three" style="margin-bottom:14px">${summaryCard("Open risks",risks.filter(r=>r.status==="Open").length,"Active risks requiring monitoring","amber")}${summaryCard("High exposure",risks.filter(r=>r.score>=15&&r.status==="Open").length,"Risk score 15 or higher","red")}${summaryCard("Highest risk score",risks.length?Math.max(...risks.map(r=>r.score)):"—","Likelihood × impact (1–25)","blue")}</div>
    <div class="grid-two" style="margin-bottom:15px">${panel("Risk matrix","Likelihood (vertical) × impact (horizontal)",`<div class="panel-body"><div class="risk-matrix"><span class="risk-label">L / I</span>${[1,2,3,4,5].map(i=>`<span class="risk-label">${i}</span>`).join("")}${matrix}${[1,2,3,4,5].map(i=>`<span class="risk-label">${6-i}</span>${[1,2,3,4,5].map(j=>{const score=(6-i)*j;return `<span class="risk-label">${score}</span>`}).join("")}`).join("")}</div><div class="chart-legend" style="margin-top:12px"><span><i class="legend-dot" style="background:#e8f3ec"></i>Low</span><span><i class="legend-dot" style="background:#fff2d8"></i>Moderate</span><span><i class="legend-dot" style="background:#fce2d4"></i>High</span><span><i class="legend-dot" style="background:#f6d7d9"></i>Critical</span></div></div>`)}
    ${panel("Response planning","Preventive and corrective actions for active exposure",`<div class="panel-body">${risks.length?risks.slice(0,4).map(r=>`<div class="detail-card" style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;gap:8px"><strong>${esc(r.title)}</strong>${badge(`Score ${r.score}`,r.score>=15?"red":"yellow")}</div><p style="margin-top:8px"><span class="subtle">Prevent</span> ${esc(r.preventive_action)}</p><p style="margin-top:5px"><span class="subtle">Respond</span> ${esc(r.corrective_action)}</p></div>`).join(""):empty("No risks recorded","Create a risk to define its preventive and corrective response.")}</div>`)}</div>
    ${panel("Risk register","Sorted by calculated likelihood × impact score.",`${searchToolbar("Search risks or responses…")}${table(["RISK","DESCRIPTION","LIKELIHOOD","IMPACT","SCORE","PRIORITY","RESPONSE PLAN","STATUS","ACTION"],rows,"No risks recorded","Add risks to populate the matrix and response plan.")}`)}`;
}
function renderChanges() {
  const rows=filterRows(state.data.change_requests,c=>`${c.id} ${c.title} ${c.justification} ${c.status}`).map(c=>`<tr data-search-row><td><strong>CR-${String(c.id).padStart(3,"0")}</strong></td><td><strong>${esc(c.title)}</strong><span class="table-subtext">${esc(c.justification)}</span></td><td class="currency">${money(c.cost_impact)}</td><td>${c.weeks_impact} weeks</td><td>${badge(c.status,statusColor(c.status))}</td><td>${c.status==="Approved"?`<span class="table-subtext">${money(c.budget_before)} → ${money(c.budget_after)}<br>${c.weeks_before} → ${c.weeks_after} weeks</span>`:"Awaiting decision"}</td><td>${c.status==="Pending"?`${actionButton("change-approve",c.id,"Approve change","✓")}${actionButton("change-reject",c.id,"Reject change","×")}`:"—"}</td></tr>`).join("");
  const approved=state.data.change_requests.filter(c=>c.status==="Approved");
  const project=state.data.project;
  return `${pageHeading("Change control","Review justification and approved scope, cost and duration impacts.",button("Submit change request","add-change",true,"＋ "))}
    ${project?`<div class="welcome-card" style="margin-bottom:14px"><div><span class="eyebrow">APPROVED BASELINE CHANGE</span><h2>${money(project.budget-approved.reduce((s,c)=>s+c.cost_impact,0))} <span class="subtle">→</span> ${money(project.budget)}</h2><p>${project.deadline_weeks-approved.reduce((s,c)=>s+c.weeks_impact,0)}-week baseline <span class="subtle">→</span> ${project.deadline_weeks}-week revised duration · ${money(approved.reduce((s,c)=>s+c.cost_impact,0))} and ${approved.reduce((s,c)=>s+c.weeks_impact,0)} weeks of approved changes.</p></div><div class="welcome-art">⇄</div></div>`:""}
    <div class="grid-three" style="margin-bottom:14px">${summaryCard("Pending requests",state.data.change_requests.filter(c=>c.status==="Pending").length,"Awaiting an approval decision","amber")}${summaryCard("Approved requests",approved.length,"Included in approved scope","green")}${summaryCard("Approved cost impact",money(approved.reduce((s,c)=>s+c.cost_impact,0)),`${approved.reduce((s,c)=>s+c.weeks_impact,0)} schedule weeks approved`,"blue")}</div>
    ${panel("Change request register","Approving a request updates the requirement status, project budget and deadline atomically.",`${searchToolbar("Search changes or justifications…")}${table(["REQUEST ID","CHANGE & JUSTIFICATION","COST IMPACT","SCHEDULE","STATUS","APPROVED BASELINE","ACTIONS"],rows,"No change requests","Proposed scope changes will appear here.")}`)}`;
}
function renderReports() {
  const project=state.data.project, d=state.data.dashboard;
  const reports=[
    ["Project summary","Charter, project health, current progress and status","report-summary"],
    ["Budget report","Approved baseline, cost impacts, estimates and actual expenditure","report-budget"],
    ["Schedule report","Activity dates, dependencies, completion and delay forecast","report-schedule"],
    ["Earned value report","PV, EV, AC, CPI and SPI for the reporting week","report-evm"],
    ["Quality report","Defect severity, inspection outcomes and open critical issues","report-quality"],
    ["Risk report","Prioritized risk register, matrix and response actions","report-risks"],
    ["Change request report","Justifications, impacts, approval decisions and baseline changes","report-changes"]
  ];
  return `${pageHeading("Reports & exports","Project reporting assembled from live workspace data.",button("Print report","print",true,"⎙ "))}
    <div class="grid-three" style="margin-bottom:15px">${summaryCard("Current status",project?.status||"Not started","Project governance","blue")}${summaryCard("Delivery progress",d?pct(d.progress_pct):"—","Schedule-weighted activity view","green")}${summaryCard("Budget health",project?money(project.budget):"—","Approved budget baseline","amber")}</div>
    <div class="grid-two">${reports.map(([title,description,action])=>`<article class="panel" style="padding:15px;display:flex;gap:12px;align-items:flex-start"><div class="metric-icon blue">▤</div><div style="flex:1"><strong style="color:#364a60;font-size:11px">${title}</strong><p class="subtle text-small" style="line-height:1.6;margin:5px 0 10px">${description}</p><button class="button button-small" data-action="${action}">View report <span>→</span></button></div></article>`).join("")}</div>
    <div class="section-title"><div><h2>Export</h2><p>Export a text project summary or print the current report.</p></div></div>
    <div class="panel"><div class="panel-body heading-actions">${button("Download project summary","export")}${button("Print this page","print")}</div></div>`;
}
function statusColor(status) {
  if(["Approved","Achieved","Resolved","Closed","Executing","Monitoring"].includes(status))return "green";
  if(["Pending","Proposed","Planning","In Progress"].includes(status))return "yellow";
  if(["Rejected","Critical"].includes(status))return "red";
  return "gray";
}
function filterRows(rows, textFor) {
  const query=state.search.trim().toLowerCase();
  return rows.filter(row=> !query || textFor(row).toLowerCase().includes(query));
}
function field(name,label,type="text",value="",options=[],full=false,required=true) {
  const base=`class="field${full?" full":""}"`;
  let control;
  if(type==="select") control=`<select name="${name}" ${required?"required":""}>${options.map(option=>`<option value="${esc(option.value??option)}" ${String(option.value??option)===String(value)?"selected":""}>${esc(option.label??option)}</option>`).join("")}</select>`;
  else if(type==="textarea") control=`<textarea name="${name}" ${required?"required":""}>${esc(value)}</textarea>`;
  else control=`<input name="${name}" type="${type}" value="${esc(value)}" ${required?"required":""} ${type==="number"?'step="any"':""}>`;
  return `<div ${base}><label>${label}</label>${control}</div>`;
}
function openForm(title, fields, submitLabel="Save changes", submitClass="button-primary") {
  const dialog=$("#modal"), form=$("#modal-form");
  $("#modal-title").textContent=title;
  $("#modal-fields").innerHTML=`<div class="form-grid">${fields.join("")}</div>`;
  $("#modal-submit").textContent=submitLabel;
  $("#modal-submit").className=`button ${submitClass}`;
  form.onsubmit=async event=>{
    event.preventDefault();
    const buttonElement=$("#modal-submit"); buttonElement.disabled=true;
    const payload=Object.fromEntries(new FormData(form).entries());
    try { await form.submitAction(payload); dialog.close(); }
    catch(error){toast(error.message,true);}
    finally{buttonElement.disabled=false;}
  };
  dialog.showModal();
}
function dataAction(id) { return state.data?.[id] || []; }
function recordById(collection,id) { return dataAction(collection).find(item=>Number(item.id)===Number(id)); }
function memberOptions() { return state.data.team_members.map(member=>({value:member.name,label:`${member.name} · ${member.role}`})); }
function requirementOptions() { return state.data.requirements.filter(req=>req.status==="Approved").map(req=>({value:req.id,label:`REQ-${req.id} · ${req.title}`})); }
function wbsOptions() { return state.data.wbs.map(item=>({value:item.id,label:`${item.code} · ${item.name}`})); }
function activityOptions(exclude) { return state.data.activities.filter(a=>Number(a.id)!==Number(exclude)).map(a=>({value:a.id,label:`ACT-${a.id} · ${a.name}`})); }
function selectedIds(name) { return [...document.querySelectorAll(`[name="${name}"]:checked`)].map(el=>Number(el.value)); }
function openActivityUpdate(id) {
  const activity=recordById("activities",id); if(!activity)return;
  openForm(`Update actuals · ${activity.name}`,[
    field("percent_complete","Percent complete","number",activity.percent_complete),
    field("actual_cost","Actual cost to date (PKR)","number",activity.actual_cost)
  ]);
  $("#modal-form").submitAction=values=>api("update-activity",{id:Number(id),percent_complete:Number(values.percent_complete),actual_cost:Number(values.actual_cost)});
}
function openAction(action,id) {
  const itemId=Number(id);
  if(action==="create-charter"||action==="edit-charter"){
    const p=state.data.project||{};
    const update=action==="edit-charter"&&Boolean(p.id);
    openForm(update?"Update project charter":"Create project charter",[
      field("name","Project name","text",p.name||"Smart Healthcare Project Management and Monitoring System",[],true),
      field("objectives","Project objectives","textarea",p.objectives||"Manage healthcare services for the five-hospital network.",[],true),
      field("stakeholders","Stakeholders","textarea",p.stakeholders||"Hospital management, doctors, patients and billing staff",[],true),
      field("scope_in","In scope","textarea",p.scope_in||"Appointments, lab reports, doctor schedules, consultations and billing",[],true),
      field("scope_out","Out of scope","textarea",p.scope_out||"Pharmacy inventory, insurance claims",[],true),
      field("budget","Approved budget (PKR)","number",p.budget||5000000),
      field("deadline_weeks","Duration (weeks)","number",p.deadline_weeks||16),
      field("start_date","Project start date","date",p.start_date||"2026-09-01")
    ]);
    $("#modal-form").submitAction=values=>api(update?"update-charter":"create-charter",{
      ...values,budget:Number(values.budget),deadline_weeks:Number(values.deadline_weeks)
    });
    return;
  }
  if(action==="edit-plan"){
    const p=state.data.project||{};
    openForm("Project management plan",[
      field("scope","Scope management approach","textarea",p.plan_scope||"Approved scope only; manage all new features through formal change control.",[],true),
      field("schedule","Schedule management approach","textarea",p.plan_schedule||"Dependency-based schedule; review milestones weekly.",[],true),
      field("cost","Cost management approach","textarea",p.plan_cost||"Track planned and actual costs using weekly EVM reviews.",[],true),
      field("quality","Quality management approach","textarea",p.plan_quality||"Inspect deliverables and resolve critical defects before release.",[],true)
    ]);
    $("#modal-form").submitAction=values=>api("update-plan",values); return;
  }
  if(action==="sample"){
    if(!confirm("Load the realistic five-hospital case-study records into this empty project database?"))return;
    api("sample").catch(error=>toast(error.message,true)); return;
  }
  if(action==="add-requirement"){
    openForm("Add project requirement",[
      field("title","Requirement name"),field("priority","Priority","select","High",["High","Medium","Low"]),
      field("description","Description","textarea","",[],true,false)
    ]);
    $("#modal-form").submitAction=values=>api("add-requirement",values);return;
  }
  if(action==="edit-requirement"){
    const req=recordById("requirements",itemId);if(!req)return;
    openForm(`Edit requirement · REQ-${req.id}`,[
      field("title","Requirement name","text",req.title),
      field("priority","Priority","select",req.priority,["High","Medium","Low"]),
      field("description","Description","textarea",req.description,[],true,false)
    ]);
    $("#modal-form").submitAction=values=>api("update-requirement",{id:itemId,...values});return;
  }
  if(action==="requirement-approve"||action==="requirement-reject"){
    const decision=action.endsWith("approve")?"approve":"reject";
    if(!confirm(`Are you sure you want to ${decision} this requirement?`))return;
    api("decide-requirement",{id:itemId,decision}).catch(error=>toast(error.message,true));return;
  }
  if(action==="add-wbs"||action==="add-child-wbs"){
    const parent=action==="add-child-wbs"?itemId:null;
    const fields=[field("name","WBS item name")];
    if(parent) fields.push(field("parent_id","Parent WBS item","select",String(parent),wbsOptions()));
    else{
      fields.push(field("requirement_id","Approved requirement","select","",requirementOptions()));
      if(state.data.wbs.length)fields.push(field("parent_id","Parent item (optional)","select","",[{value:"",label:"Top-level deliverable"},...wbsOptions()],true,false));
    }
    openForm(parent?"Add child WBS item":"Add work breakdown item",fields);
    $("#modal-form").submitAction=values=>api("add-wbs",{
      name:values.name,
      parent_id:values.parent_id?Number(values.parent_id):null,
      requirement_id:values.requirement_id?Number(values.requirement_id):null
    });return;
  }
  if(action==="add-change"){
    openForm("Submit scope change request",[
      field("title","Change title"),
      field("priority","Requirement priority","select","High",["High","Medium","Low"]),
      field("justification","Business justification","textarea","",[],true),
      field("description","Requested scope / feature","textarea","",[],true,false),
      field("cost_impact","Estimated cost impact (PKR)","number",0),
      field("weeks_impact","Schedule impact (weeks)","number",0)
    ]);
    $("#modal-form").submitAction=values=>api("submit-change",{...values,cost_impact:Number(values.cost_impact),weeks_impact:Number(values.weeks_impact)});return;
  }
  if(action==="change-approve"||action==="change-reject"){
    const change=recordById("change_requests",itemId), decision=action==="change-approve"?"approve":"reject";
    const msg=decision==="approve"?`Approve “${change?.title}”? This will update the approved scope, project budget and deadline.`:`Reject “${change?.title}”? Its requirement will remain out of project scope.`;
    if(!confirm(msg))return;
    openForm(`${decision==="approve"?"Approve":"Reject"} change request · CR-${itemId}`,[
      field("note","Decision note","textarea",decision==="approve"?"Approved by steering committee":"",[],true,false)
    ],decision==="approve"?"Approve change":"Reject request",decision==="approve"?"button-primary":"button-danger");
    $("#modal-form").submitAction=values=>api("decide-change",{id:itemId,decision,...values});return;
  }
  if(action==="add-member"){
    openForm("Add project team member",[field("name","Team member name"),field("role","Project role")]);
    $("#modal-form").submitAction=values=>api("add-member",values);return;
  }
  if(action==="add-activity"){
    openForm("Add scheduled activity",[
      field("name","Activity name"),
      field("assigned_to","Assigned team member","select",state.data.team_members[0]?.name||"",memberOptions()),
      field("duration_weeks","Duration (weeks)","number",1),
      field("estimated_cost","Estimated cost (PKR)","number",0),
      field("start_week","Earliest start week","number",1),
      field("wbs_id","Linked approved WBS item","select","",[{value:"",label:"No WBS link"},...wbsOptions()],true,false),
      `<div class="field full"><label>Predecessor activities</label><div class="table-scroll" style="max-height:140px;border:1px solid #e1e8ed;border-radius:7px;padding:7px">${activityOptions(null).map(a=>`<label style="display:flex;gap:8px;align-items:center;padding:5px"><input name="dependencies" type="checkbox" value="${a.value}"><span>${esc(a.label)}</span></label>`).join("")||"No activities yet"}</div></div>`
    ]);
    $("#modal-form").submitAction=values=>api("add-activity",{
      ...values,duration_weeks:Number(values.duration_weeks),estimated_cost:Number(values.estimated_cost),
      start_week:Number(values.start_week),wbs_id:values.wbs_id?Number(values.wbs_id):null,
      dependencies:selectedIds("dependencies")
    });return;
  }
  if(action==="update-activity"||action==="dependencies"){
    if(action==="update-activity"&&id===undefined){
      if(!state.data.activities.length){toast("Add an activity before recording actuals.",true);return;}
      openForm("Update activity actuals",[
        field("id","Project activity","select","",state.data.activities.map(a=>({value:a.id,label:`ACT-${a.id} · ${a.name}`}))),
        field("percent_complete","Percent complete","number",0),
        field("actual_cost","Actual cost to date (PKR)","number",0)
      ]);
      $("#modal-form").submitAction=values=>{
        return api("update-activity",{
          id:Number(values.id),percent_complete:Number(values.percent_complete),actual_cost:Number(values.actual_cost)
        });
      };
      return;
    }
    const activity=recordById("activities",itemId);if(!activity)return;
    if(action==="update-activity"){openActivityUpdate(itemId);return;}
    const selectedNames=new Set((activity.dependency_names||"").split(", "));
    const selected=new Set(state.data.activities.filter(a=>selectedNames.has(a.name)).map(a=>a.id));
    openForm(`Dependencies · ${activity.name}`,[
      `<div class="field full"><label>Select predecessor activities</label><div class="table-scroll" style="max-height:210px;border:1px solid #e1e8ed;border-radius:7px;padding:7px">${activityOptions(itemId).map(a=>`<label style="display:flex;gap:8px;align-items:center;padding:6px"><input name="dependencies" type="checkbox" value="${a.value}" ${selected.has(Number(a.value))?"checked":""}><span>${esc(a.label)}</span></label>`).join("")||"No other activities available"}</div></div>`
    ]);
    $("#modal-form").submitAction=()=>api("set-dependencies",{id:itemId,dependencies:selectedIds("dependencies")});return;
  }
  if(action==="add-defect"){
    openForm("Record quality defect",[
      field("title","Defect title"),field("severity","Severity","select","Critical",["Critical","High","Medium","Low"]),
      field("assigned_to","Assigned owner","select",state.data.team_members.find(m=>m.role==="Quality Assurance")?.name||"",memberOptions()),
      field("description","Issue description","textarea","",[],true,false)
    ]);
    $("#modal-form").submitAction=values=>api("add-defect",values);return;
  }
  if(action==="update-defect"){
    const defect=recordById("defects",itemId);if(!defect)return;
    openForm(`Update defect · DEF-${itemId}`,[
      field("status","Resolution status","select",defect.status,["Open","In Progress","Resolved"])
    ]);
    $("#modal-form").submitAction=values=>api("update-defect",{id:itemId,...values});return;
  }
  if(action==="add-quality-check"){
    openForm("Add deliverable quality check",[
      field("deliverable","Deliverable name"),field("criterion","Inspection / acceptance criterion","textarea","",[],true)
    ]);
    $("#modal-form").submitAction=values=>api("add-quality-check",values);return;
  }
  if(action==="record-quality"){
    const check=recordById("quality_checks",itemId);if(!check)return;
    openForm(`Record inspection · ${check.deliverable}`,[
      field("result","Inspection result","select",check.result,["Not Tested","Pass","Fail"]),
      field("notes","Test evidence / notes","textarea",check.notes||"",[],true,false)
    ]);
    $("#modal-form").submitAction=values=>api("record-quality",{id:itemId,...values});return;
  }
  if(action==="add-risk"){
    openForm("Add project risk and response",[
      field("title","Risk / potential issue"),field("likelihood","Likelihood (1–5)","number",3),
      field("impact","Impact (1–5)","number",3),
      field("description","Risk description","textarea","",[],true,false),
      field("preventive_action","Preventive action","textarea","",[],true),
      field("corrective_action","Corrective response","textarea","",[],true)
    ]);
    $("#modal-form").submitAction=values=>api("add-risk",{...values,likelihood:Number(values.likelihood),impact:Number(values.impact)});return;
  }
  if(action==="update-risk"){
    const risk=recordById("risks",itemId);if(!risk)return;
    openForm(`Update risk · RSK-${itemId}`,[
      field("status","Risk status","select",risk.status,["Open","Mitigated","Closed"])
    ]);
    $("#modal-form").submitAction=values=>api("update-risk",{id:itemId,...values});return;
  }
  if(action==="add-milestone"){
    openForm("Add project milestone",[
      field("name","Milestone name"),field("due_week","Due week","number",1),
      field("owner","Accountable owner","select",state.data.team_members[0]?.name||"",memberOptions())
    ]);
    $("#modal-form").submitAction=values=>api("add-milestone",{...values,due_week:Number(values.due_week)});return;
  }
  if(action==="achieve-milestone"){
    if(confirm("Mark this milestone as achieved?"))api("achieve-milestone",{id:itemId}).catch(error=>toast(error.message,true));return;
  }
  if(action==="change-project-status"){
    const status=$("#project-status").value;
    if(status===state.data.project.status){toast(`Project is already ${status}.`);return;}
    if(confirm(`Update the project status to ${status}?`))api("set-status",{status,note:"Updated from CarePlan dashboard"}).catch(error=>toast(error.message,true));return;
  }
  if(action==="close-project"){
    if(state.data.milestones.some(m=>m.status!=="Achieved")){toast("Achieve all project milestones before recording closure.",true);return;}
    openForm("Record project closure",[
      field("summary","Closure summary","textarea","",[],true),
      field("lessons","Lessons learned","textarea","",[],true,false)
    ],"Close project","button-danger");
    $("#modal-form").submitAction=values=>api("close-project",values);return;
  }
  if(action==="refresh"){refresh(true);return;}
  if(action==="print"){window.print();return;}
  if(action==="export"){exportReport();return;}
  if(action.startsWith("report-")){showReport(action);return;}
  if(action==="toggle-wbs"){
    if(state.collapse.has(itemId))state.collapse.delete(itemId);else state.collapse.add(itemId);
    $("#wbs-tree").innerHTML=buildWbsTree(state.data.wbs);return;
  }
}
async function exportReport() {
  try{
    const result=await fetch("/api/export",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});
    const payload=await result.json();if(!result.ok)throw new Error(payload.error||"Export failed.");
    const blob=new Blob([payload.report],{type:"text/plain;charset=utf-8"});
    const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="healthcare-project-summary.txt";link.click();URL.revokeObjectURL(link.href);toast("Project summary downloaded.");
  }catch(error){toast(error.message,true);}
}
function showReport(action) {
  const page=action.slice(7), project=state.data.project, d=state.data.dashboard;
  let report="";
  if(!project)report="No project charter has been created.";
  else if(page==="summary")report=`${state.data.charter_report}\n\nPROJECT HEALTH\nProgress: ${d.progress_pct}%\nDelayed activities: ${d.delayed_activities.map(a=>a.name).join(", ")||"None"}\nPending changes: ${d.pending_change_requests}\nCritical defects: ${d.critical_defects.length}`;
  else if(page==="budget")report=`BUDGET REPORT\nBaseline budget: ${money(project.budget-state.data.change_requests.filter(c=>c.status==="Approved").reduce((s,c)=>s+c.cost_impact,0))}\nApproved changes: ${money(state.data.change_requests.filter(c=>c.status==="Approved").reduce((s,c)=>s+c.cost_impact,0))}\nRevised budget: ${money(project.budget)}\nPlanned activity estimates: ${money(d.evm.planned_budget)}\nActual expenditure: ${money(d.evm.ac)}\nBudget variance: ${money(d.evm.budget_variance)}`;
  else if(page==="schedule")report=`SCHEDULE REPORT\n${d.schedule_forecast.activities.map(a=>`${a.name}: ${fmtDate(a.start_date)} – ${fmtDate(a.end_date)} · ${pct(a.percent_complete)} · forecast week ${a.forecast_end_week} · dependencies ${a.dependency_names||"none"}`).join("\n")}\n\nForecast completion week ${d.schedule_forecast.projected_end_week}; deadline week ${project.deadline_weeks}.`;
  else if(page==="evm")report=`EARNED VALUE REPORT · Week ${d.evm.week}\nPV ${money(d.evm.pv)}\nEV ${money(d.evm.ev)}\nAC ${money(d.evm.ac)}\nCPI ${d.evm.cpi?.toFixed(2)??"N/A"}\nSPI ${d.evm.spi?.toFixed(2)??"N/A"}\n${d.evm.warnings.join("\n")}`;
  else if(page==="quality")report=`QUALITY REPORT\n${state.data.defects.map(x=>`${x.title} · ${x.severity} · ${x.status} · ${x.assigned_to}`).join("\n")}\n\nINSPECTIONS\n${state.data.quality_checks.map(x=>`${x.deliverable} · ${x.result} · ${x.criterion}`).join("\n")}`;
  else if(page==="risks")report=state.data.risks.map(x=>`RSK-${x.id} · ${x.title} · Likelihood ${x.likelihood} × Impact ${x.impact} = ${x.score} · ${x.status}\nPrevent: ${x.preventive_action}\nRespond: ${x.corrective_action}`).join("\n\n");
  else if(page==="changes")report=state.data.scope_report;
  $("#modal-title").textContent=`${pageNames[page]||"Project"} report`;
  $("#modal-fields").innerHTML=`<pre class="report-content">${esc(report)}</pre>`;
  $("#modal-submit").hidden=true;
  $("#modal-form").onsubmit=event=>event.preventDefault();
  $("#modal").showModal();
  $("#modal").addEventListener("close",()=>{$("#modal-submit").hidden=false;},{once:true});
}
function bindPage() {
  const content=$("#main-content");
  content.querySelectorAll("[data-page]").forEach(node=>node.addEventListener("click",()=>navigate(node.dataset.page)));
  content.querySelectorAll("[data-action]").forEach(node=>node.addEventListener("click",()=>openAction(node.dataset.action,node.dataset.id)));
  content.querySelectorAll("[data-search]").forEach(input=>input.addEventListener("input",()=>{
    state.search=input.value;applyTableFilters();
  }));
  content.querySelectorAll("[data-filter]").forEach(select=>select.addEventListener("change",()=>{
    state.filters[select.dataset.filter]=select.value;applyTableFilters();
  }));
  applyTableFilters();
}
function applyTableFilters() {
  const status=state.filters["requirement-status"]||"";
  const priority=state.filters["requirement-priority"]||"";
  let total=0,shown=0;
  document.querySelectorAll("#main-content [data-search-row]").forEach(row=>{
    total++;
    let visible=!state.search||row.textContent.toLowerCase().includes(state.search.toLowerCase());
    if(status)visible=visible&&row.children[3]?.textContent.trim()===status;
    if(priority)visible=visible&&row.children[2]?.textContent.trim()===priority;
    row.style.display=visible?"":"none";if(visible)shown++;
  });
  const count=$("[data-result-count]");if(count)count.textContent=state.search||status||priority?`${shown} of ${total} records`:"";
}
function drawValueChart() {
  const canvas=$("#value-chart");if(!canvas||!state.data.dashboard)return;
  const context=canvas.getContext("2d"),rect=canvas.getBoundingClientRect(),ratio=window.devicePixelRatio||1;
  canvas.width=Math.max(1,Math.round(rect.width*ratio));canvas.height=Math.max(1,Math.round(rect.height*ratio));
  context.scale(ratio,ratio);
  const width=rect.width,height=rect.height,pad={top:12,right:14,bottom:25,left:42};
  const plotW=width-pad.left-pad.right,plotH=height-pad.top-pad.bottom;
  const activities=state.data.activities,d=state.data.dashboard,maximum=Math.max(1,d.evm.pv,d.evm.ev,d.evm.ac,...activities.map(a=>a.estimated_cost));
  context.font="9px Aptos, 'Segoe UI Variable', 'Segoe UI', sans-serif";context.textAlign="right";
  for(let i=0;i<=4;i++){
    const y=pad.top+plotH*i/4,value=maximum*(1-i/4);
    context.strokeStyle="#edf1f4";context.beginPath();context.moveTo(pad.left,y);context.lineTo(width-pad.right,y);context.stroke();
    context.fillStyle="#93a0ae";context.fillText(value>=1_000_000?`${(value/1_000_000).toFixed(1)}m`:`${Math.round(value/1000)}k`,pad.left-7,y+3);
  }
  const steps=Math.max(activities.length,2);
  const values=activities.length?activities.map((a,i)=>({
    x:pad.left+plotW*i/(steps-1),
    pv:activities.slice(0,i+1).reduce((s,item)=>s+valueForActivity(item,d.evm.week,"pv"),0),
    ev:activities.slice(0,i+1).reduce((s,item)=>s+item.estimated_cost*item.percent_complete/100,0),
    ac:activities.slice(0,i+1).reduce((s,item)=>s+item.actual_cost,0)
  })):[{x:pad.left,pv:0,ev:0,ac:0},{x:pad.left+plotW,pv:d.evm.pv,ev:d.evm.ev,ac:d.evm.ac}];
  const scaleY=value=>pad.top+plotH-(value/maximum)*plotH;
  [["pv","#24ab9b"],["ev","#6288dd"],["ac","#e0a549"]].forEach(([key,color])=>{
    context.beginPath();context.strokeStyle=color;context.lineWidth=2;
    values.forEach((point,index)=>{const x=point.x,y=scaleY(point[key]);if(index===0)context.moveTo(x,y);else context.lineTo(x,y);});
    context.stroke();
    values.forEach(point=>{context.beginPath();context.fillStyle=color;context.arc(point.x,scaleY(point[key]),2.2,0,Math.PI*2);context.fill();});
  });
  context.fillStyle="#8c99a8";context.textAlign="center";
  [0,1,2,3,4].forEach(index=>context.fillText(`W${Math.max(1,d.evm.week-4+index)}`,pad.left+plotW*index/4,height-5));
}
document.querySelectorAll(".nav-item").forEach(node=>node.addEventListener("click",()=>navigate(node.dataset.page)));
document.querySelectorAll(".brand[data-page]").forEach(node=>node.addEventListener("click",event=>{event.preventDefault();navigate(node.dataset.page)}));
$("#mobile-menu").addEventListener("click",()=>$("#sidebar").classList.toggle("open"));
$("#refresh-button").addEventListener("click",()=>refresh(true));
$("#notification-button").addEventListener("click",()=>{
  const count=state.data?.dashboard?.critical_defects?.length||0;
  toast(count?`${count} unresolved critical defect${count===1?"":"s"} need attention.`:"No new critical project alerts.");
});
$("#settings-button").addEventListener("click",()=>{
  const compact=localStorage.getItem("careplan-compact-tables")==="true";
  openForm("Workspace preferences",[
    field("compact","Data table density","select",compact?"compact":"comfortable",[
      {value:"comfortable",label:"Comfortable spacing"},
      {value:"compact",label:"Compact rows"}
    ],true)
  ],"Save preferences");
  $("#modal-form").submitAction=values=>{
    localStorage.setItem("careplan-compact-tables",String(values.compact==="compact"));
    document.body.classList.toggle("compact-tables",values.compact==="compact");
    toast("Workspace preferences saved.");
  };
});
$("#modal-form").addEventListener("click",event=>{
  if(event.target.value==="cancel")$("#modal").close();
});
$("#modal").addEventListener("close",()=>$("#modal-submit").hidden=false);
window.addEventListener("resize",()=>{if(state.page==="dashboard"||state.page==="evm")drawValueChart();});
window.addEventListener("keydown",event=>{
  if(event.key==="Escape")$("#sidebar").classList.remove("open");
  if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="k"){
    event.preventDefault();const input=$("[data-search]");if(input)input.focus();
  }
});
refresh();
document.body.classList.toggle("compact-tables",localStorage.getItem("careplan-compact-tables")==="true");
