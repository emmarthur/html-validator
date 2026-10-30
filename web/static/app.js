const manifestSelect = document.getElementById("manifest");
const htmlInput = document.getElementById("html-input");
const btnAnalyze = document.getElementById("btn-analyze");
const btnValid = document.getElementById("btn-valid");
const btnInvalid = document.getElementById("btn-invalid");
const errorEl = document.getElementById("error-text");
const statusPanel = document.getElementById("status-panel");
const statusLine = document.getElementById("status-line");
const catalogPanel = document.getElementById("catalog-panel");
const catalogOut = document.getElementById("catalog-out");
const problemsPanel = document.getElementById("problems-panel");
const problemsOut = document.getElementById("problems-out");

const SESSION_KEY = "html-validator-v1";

function persist() {
  AppSession.save(SESSION_KEY, {
    html: htmlInput.value,
    manifestId: manifestSelect.value,
  });
}

function restore() {
  const saved = AppSession.load(SESSION_KEY);
  if (!saved) return;
  if (saved.html) htmlInput.value = saved.html;
  if (saved.manifestId) manifestSelect.value = saved.manifestId;
}

AppSession.wireHelpSave(SESSION_KEY, () => ({
  html: htmlInput.value,
  manifestId: manifestSelect.value,
}));

function setError(msg) {
  errorEl.hidden = !msg;
  errorEl.textContent = msg || "";
}

function formatMap(obj) {
  if (!obj || Object.keys(obj).length === 0) {
    return "(none)";
  }
  return Object.entries(obj)
    .map(([tag, kids]) => `${tag}: ${kids.join(", ")}`)
    .join("\n");
}

function showResult(data) {
  statusPanel.hidden = false;
  statusLine.textContent = data.ok
    ? "Structure matches the manifest."
    : "Structure has disallowed child tags.";
  statusLine.className = data.ok ? "status-line ok" : "status-line bad";

  catalogPanel.hidden = false;
  catalogOut.textContent = formatMap(data.catalog);

  problemsPanel.hidden = false;
  problemsOut.textContent = data.ok ? "(no violations)" : formatMap(data.problems);
  persist();
}

async function loadManifests() {
  const res = await fetch("/api/manifests");
  const data = await res.json();
  manifestSelect.innerHTML = "";
  for (const m of data.manifests) {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = m.name;
    manifestSelect.appendChild(opt);
  }
}

async function loadSample(id) {
  const res = await fetch(`/api/samples/${id}`);
  if (!res.ok) {
    setError("Could not load sample.");
    return;
  }
  const data = await res.json();
  htmlInput.value = data.html;
  setError("");
  persist();
}

async function analyze() {
  setError("");
  btnAnalyze.disabled = true;
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        html: htmlInput.value,
        manifest_id: manifestSelect.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail || "Analysis failed.");
      return;
    }
    showResult(data);
  } catch {
    setError("Network error.");
  } finally {
    btnAnalyze.disabled = false;
  }
}

btnAnalyze.addEventListener("click", analyze);
btnValid.addEventListener("click", () => loadSample("valid-report"));
btnInvalid.addEventListener("click", () => loadSample("invalid-structure"));
manifestSelect.addEventListener("change", persist);
htmlInput.addEventListener("input", persist);

loadManifests().then(() => {
  restore();
  if (!htmlInput.value) {
    loadSample("invalid-structure");
  }
});
