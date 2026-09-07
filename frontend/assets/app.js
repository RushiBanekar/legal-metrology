const API_BASE = "http://localhost:8000";

const FIELD_LABELS = {
  MRP: "Maximum Retail Price (MRP)",
  NET_QUANTITY: "Net quantity",
  MANUFACTURER: "Manufacturer / packer name",
  MFG_DATE: "Manufacturing date",
  COUNTRY_OF_ORIGIN: "Country of origin",
};

const VIEW_TYPES = [
  { key: "FRONT", label: "Front" },
  { key: "BACK", label: "Back" },
  { key: "LEFT_SIDE", label: "Left side" },
  { key: "RIGHT_SIDE", label: "Right side" },
  { key: "CLOSE_UP", label: "Close-up" },
];

let sessionId = null;
let selectedView = "FRONT";
let uploadedPhotos = [];

function goToStep(n) {
  [1, 2, 3].forEach(i => {
    const el = document.getElementById(`step-${i}`);
    if (el) el.classList.toggle("hidden", i !== n);
    const dot = document.getElementById(`dot-${i}`);
    if (dot) dot.classList.remove("active", "done");
  });
  const activeDot = document.getElementById(`dot-${n}`);
  if (activeDot) activeDot.classList.add("active");
  for (let i = 1; i < n; i++) {
    const d = document.getElementById(`dot-${i}`);
    if (d) d.classList.add("done");
  }
}

function showError(stepEl, msg) {
  const el = document.getElementById(stepEl);
  el.textContent = msg;
  el.classList.remove("hidden");
}
function hideError(stepEl) {
  document.getElementById(stepEl).classList.add("hidden");
}

async function startSession() {
  hideError("error-1");
  const inspector_id = document.getElementById("inspector").value.trim();
  const location = document.getElementById("location").value.trim();
  const category = document.getElementById("category").value;
  const product_identifier = document.getElementById("product").value.trim();

  if (!inspector_id || !location || !product_identifier) {
    showError("error-1", "Please fill in all fields before starting.");
    return;
  }

  const btn = document.getElementById("btn-start");
  btn.disabled = true;
  document.getElementById("btn-start-label").innerHTML = '<span class="spinner"></span>';

  try {
    const res = await fetch(`${API_BASE}/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ inspector_id, location, category, product_identifier })
    });
    if (!res.ok) throw new Error("Could not start the inspection. Please try again.");
    const data = await res.json();
    sessionId = data.session_id;
    renderViewChips();
    goToStep(2);
  } catch (err) {
    showError("error-1", err.message || "Something went wrong. Check your connection and try again.");
  } finally {
    btn.disabled = false;
    document.getElementById("btn-start-label").textContent = "Start inspection";
  }
}

function renderViewChips() {
  const row = document.getElementById("view-chips");
  row.innerHTML = "";
  VIEW_TYPES.forEach(v => {
    const chip = document.createElement("div");
    chip.className = "view-chip" + (v.key === selectedView ? " selected" : "");
    chip.textContent = v.label;
    chip.onclick = () => {
      selectedView = v.key;
      document.getElementById("selected-view-label").textContent = v.label;
      renderViewChips();
    };
    row.appendChild(chip);
  });
}

async function uploadPhoto() {
  hideError("error-2");
  const input = document.getElementById("photo-input");
  const file = input.files[0];
  if (!file) return;

  const thumbUrl = URL.createObjectURL(file);
  const rowIndex = uploadedPhotos.length;
  uploadedPhotos.push({ view: selectedView, accepted: null, reason: null, thumbUrl, pending: true });
  renderPhotoList();

  const form = new FormData();
  form.append("file", file);
  form.append("view_type", selectedView);

  try {
    const res = await fetch(`${API_BASE}/session/${sessionId}/photo`, { method: "POST", body: form });
    if (!res.ok) throw new Error("Upload failed. Please try again.");
    const data = await res.json();
    uploadedPhotos[rowIndex].accepted = data.accepted;
    uploadedPhotos[rowIndex].reason = data.reason;
    uploadedPhotos[rowIndex].pending = false;
  } catch (err) {
    uploadedPhotos[rowIndex].accepted = false;
    uploadedPhotos[rowIndex].reason = "Upload failed — check your connection.";
    uploadedPhotos[rowIndex].pending = false;
  }
  renderPhotoList();
  input.value = "";
}

function renderPhotoList() {
  const list = document.getElementById("photo-list");
  list.innerHTML = "";
  let anyAccepted = false;

  uploadedPhotos.forEach(p => {
    if (p.accepted) anyAccepted = true;
    const row = document.createElement("div");
    row.className = "photo-row";

    const img = document.createElement("img");
    img.className = "photo-thumb";
    img.src = p.thumbUrl;
    row.appendChild(img);

    const meta = document.createElement("div");
    meta.className = "photo-meta";

    const viewName = VIEW_TYPES.find(v => v.key === p.view)?.label || p.view;
    const viewEl = document.createElement("div");
    viewEl.className = "photo-view";
    viewEl.textContent = viewName;
    meta.appendChild(viewEl);

    const statusEl = document.createElement("div");
    if (p.pending) {
      statusEl.className = "photo-status status-pending";
      statusEl.innerHTML = '<span class="badge-dot dot-pending"></span>Checking photo quality…';
      meta.appendChild(statusEl);
    } else if (p.accepted) {
      statusEl.className = "photo-status status-ok";
      statusEl.innerHTML = '<span class="badge-dot dot-ok"></span>Accepted';
      meta.appendChild(statusEl);
    } else {
      statusEl.className = "photo-status status-bad";
      statusEl.innerHTML = '<span class="badge-dot dot-bad"></span>Retake needed';
      meta.appendChild(statusEl);
      const tip = document.createElement("div");
      tip.className = "retake-tip";
      tip.textContent = p.reason || "Photo quality too low.";
      meta.appendChild(tip);
    }
    row.appendChild(meta);
    list.appendChild(row);
  });

  document.getElementById("btn-evaluate").disabled = !anyAccepted;
}

async function evaluateSession() {
  hideError("error-2");
  const btn = document.getElementById("btn-evaluate");
  btn.disabled = true;
  document.getElementById("btn-evaluate-label").innerHTML = '<span class="spinner"></span>';

  try {
    const res = await fetch(`${API_BASE}/session/${sessionId}/evaluate`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not evaluate yet — capture at least one clear photo.");
    renderResults(data);
    goToStep(3);
  } catch (err) {
    showError("error-2", err.message);
  } finally {
    btn.disabled = false;
    document.getElementById("btn-evaluate-label").textContent = "Review findings";
  }
}

function renderResults(data) {
  const banner = document.getElementById("verdict-banner");
  const title = document.getElementById("verdict-title");
  const desc = document.getElementById("verdict-desc");

  banner.className = "verdict-banner";
  if (data.verdict === "COMPLIANT") {
    banner.classList.add("compliant");
    title.textContent = "Compliant";
    desc.textContent = "All required declarations were found and meet requirements based on the evidence captured.";
  } else if (data.verdict === "POTENTIAL_NON_COMPLIANCE") {
    banner.classList.add("noncompliant");
    title.textContent = "Potential non-compliance";
    desc.textContent = "At least one requirement appears to be violated based on the evidence captured. Review the details below.";
  } else {
    banner.classList.add("inconclusive");
    title.textContent = "Needs more evidence";
    desc.textContent = data.verdict_reason || "Some required declarations could not be confirmed yet. Capture the photos suggested below.";
  }

  const list = document.getElementById("requirements-list");
  list.innerHTML = "";
  const missingByField = {};
  (data.missing_evidence || []).forEach(m => missingByField[m.field] = m);

  Object.entries(data.coverage || {}).forEach(([field, status]) => {
    const row = document.createElement("div");
    row.className = "req-row";

    const icon = document.createElement("div");
    const found = status === "FOUND";
    icon.className = "req-icon " + (found ? "found" : "missing");
    icon.textContent = found ? "✓" : "!";
    row.appendChild(icon);

    const body = document.createElement("div");
    body.className = "req-body";

    const name = document.createElement("div");
    name.className = "req-name";
    name.textContent = FIELD_LABELS[field] || field;
    body.appendChild(name);

    const detail = document.createElement("div");
    detail.className = "req-detail";
    detail.textContent = found ? "Found and captured." :
      (status === "CONFLICT" ? "Different photos show conflicting values — needs manual review." :
        status === "UNCLEAR" ? "Detected but not clearly readable." : "Not yet captured.");
    body.appendChild(detail);

    if (!found && missingByField[field]) {
      const action = document.createElement("div");
      action.className = "req-action";
      const viewLabel = VIEW_TYPES.find(v => v.key === missingByField[field].recommended_view)?.label || "another angle";
      action.textContent = `Suggested: photograph the ${viewLabel.toLowerCase()} panel`;
      body.appendChild(action);
    }

    row.appendChild(body);
    list.appendChild(row);
  });

  document.getElementById("rule-version").textContent = data.rule_version || "—";
  document.getElementById("evidence-hash").textContent = data.evidence_hash || "—";

  saveToDashboard(data);
}

function saveToDashboard(data) {
  const record = {
    session_id: data.session_id,
    verdict: data.verdict,
    evaluated_at: data.evaluated_at,
    product: document.getElementById("product") ? document.getElementById("product").value : "",
  };
  const existing = JSON.parse(localStorage.getItem("lm_inspections") || "[]");
  existing.unshift(record);
  localStorage.setItem("lm_inspections", JSON.stringify(existing.slice(0, 50)));
}

function startOver() {
  sessionId = null;
  uploadedPhotos = [];
  selectedView = "FRONT";
  const productEl = document.getElementById("product");
  if (productEl) productEl.value = "";
  const listEl = document.getElementById("photo-list");
  if (listEl) listEl.innerHTML = "";
  goToStep(1);
}