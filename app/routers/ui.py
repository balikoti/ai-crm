from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"])

@router.get("/", response_class=HTMLResponse)
async def ui_home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>AI CRM — Sheets</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; color-scheme: light dark; }
    body { margin: 16px; }
    h1 { margin: 0 0 16px; }
    .bar { display:flex; gap:10px; align-items:center; flex-wrap: wrap; margin-bottom:12px; }
    .bar input[type="text"] { flex: 1 1 420px; padding:12px; border:1px solid #cbd5e1; border-radius:10px; }
    .btn { padding:10px 12px; border:1px solid #0ea5e9; background:#0ea5e9; color:#fff; border-radius:10px; cursor:pointer; }
    .btn.secondary { background:#fff; color:#0ea5e9; }
    .muted { color:#6b7280; font-size:12px; }
    .ok { color:#22c55e; }
    .err { color:#ef4444; white-space:pre-wrap; }

    /* Collapsible sections */
    .section { border:1px solid #e5e7eb; border-radius:12px; margin:12px 0; overflow:hidden; }
    .section h2 { margin:0; padding:14px 16px; background:#f8fafc; cursor:pointer; user-select:none; display:flex; align-items:center; justify-content:space-between; }
    .section .content { padding:12px 12px 16px; display:none; background:#fff; }
    .section.open .content { display:block; }
    .caret { margin-right:8px; font-weight:600; }

    /* Add Row bar */
    .addrow { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
    .addrow input, .addrow select, .addrow textarea { padding:8px; border:1px solid #cbd5e1; border-radius:8px; }
    .addrow textarea { width:100%; max-width:100%; min-width:240px; height:40px; }
    .addrow .btn { white-space:nowrap; }

    /* Spreadsheet table */
    .sheet { overflow:auto; border:1px solid #e5e7eb; border-radius:8px; }
    table { width:100%; border-collapse:separate; border-spacing:0; min-width:720px; }
    thead th { position:sticky; top:0; background:#f3f4f6; border-bottom:1px solid #e5e7eb; text-align:left; padding:10px; font-size:14px; }
    tbody td { border-top:1px solid #e5e7eb; padding:8px 10px; vertical-align:top; font-size:14px; }
    code.attrs { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; background:#f8fafc; padding:2px 6px; border-radius:6px; display:inline-block; }

    /* Pills (ingest answers) */
    .pill { display:inline-block; padding:6px 10px; border:1px solid #e5e7eb; border-radius:999px; margin-right:8px; cursor:pointer; background:#fff; }
    .pill:hover { background:#f1f5f9; }
  </style>
</head>
<body>
  <h1>AI CRM — Sheets</h1>

  <!-- Smart Bar -->
  <div class="bar">
    <input id="smart_input" type="text" placeholder='Type or speak… e.g., "John Doe john@x.com 416-555-1234 new"'>
    <button id="mic_btn" class="btn" title="Voice to text">🎤</button>
    <button id="submit_btn" class="btn" title="Submit">↩︎ Submit</button>
  </div>
  <div id="status" class="muted">Connecting…</div>
  <div id="ingest_ui" class="muted" style="margin:6px 0 14px;"></div>

  <!-- Contacts -->
  <div class="section open" id="sec_contacts">
    <h2><span><span class="caret">▼</span>Contacts</span><span class="muted" id="count_contacts"></span></h2>
    <div class="content">
      <div class="addrow">
        <input id="c_first" placeholder="First" />
        <input id="c_last" placeholder="Last" />
        <input id="c_email" placeholder="Email" />
        <input id="c_phone" placeholder="Phone" />
        <input id="c_status" placeholder="Status (new/warm/...)" />
        <input id="c_attrs" placeholder='Attrs JSON (optional)' style="min-width:220px;" />
        <button class="btn" onclick="addContact()">+ Add Row</button>
        <button class="btn secondary" onclick="loadContacts()">Refresh</button>
      </div>
      <div class="sheet"><table>
        <thead><tr>
          <th style="width:64px;">ID</th><th>First</th><th>Last</th><th>Email</th><th>Phone</th><th>Status</th><th>Attrs</th>
        </tr></thead>
        <tbody id="tbl_contacts"></tbody>
      </table></div>
    </div>
  </div>

  <!-- Properties -->
  <div class="section" id="sec_properties">
    <h2><span><span class="caret">►</span>Properties</span><span class="muted" id="count_properties"></span></h2>
    <div class="content">
      <div class="addrow">
        <input id="p_address" placeholder="Address" style="min-width:260px;" />
        <input id="p_city" placeholder="City" />
        <input id="p_state" placeholder="State/Province" />
        <input id="p_country" placeholder="Country (default Canada)" />
        <input id="p_status" placeholder="Status (prospect/active/...)" />
        <input id="p_attrs" placeholder='Attrs JSON (optional)' style="min-width:220px;" />
        <button class="btn" onclick="addProperty()">+ Add Row</button>
        <button class="btn secondary" onclick="loadProperties()">Refresh</button>
      </div>
      <div class="sheet"><table>
        <thead><tr>
          <th style="width:64px;">ID</th><th>Address</th><th>City</th><th>State/Prov</th><th>Country</th><th>Status</th><th>Attrs</th>
        </tr></thead>
        <tbody id="tbl_properties"></tbody>
      </table></div>
    </div>
  </div>

  <!-- Transactions -->
  <div class="section" id="sec_transactions">
    <h2><span><span class="caret">►</span>Transactions</span><span class="muted" id="count_transactions"></span></h2>
    <div class="content">
      <div class="addrow">
        <input id="t_contact_id" placeholder="Contact ID" />
        <input id="t_property_id" placeholder="Property ID" />
        <select id="t_side">
          <option value="buy">buy</option><option value="sell">sell</option><option value="lease">lease</option>
        </select>
        <input id="t_stage" placeholder="Stage (lead/showing/offer/...)" />
        <input id="t_offer" placeholder="Offer (optional)" />
        <input id="t_close" placeholder="Close (optional)" />
        <input id="t_attrs" placeholder='Attrs JSON (optional)' style="min-width:220px;" />
        <button class="btn" onclick="addTransaction()">+ Add Row</button>
        <button class="btn secondary" onclick="loadTransactions()">Refresh</button>
      </div>
      <div class="sheet"><table>
        <thead><tr>
          <th style="width:64px;">ID</th><th>Contact</th><th>Property</th><th>Side</th><th>Stage</th><th>Offer</th><th>Close</th><th>Attrs</th>
        </tr></thead>
        <tbody id="tbl_transactions"></tbody>
      </table></div>
    </div>
  </div>

  <!-- Documents -->
  <div class="section" id="sec_documents">
    <h2><span><span class="caret">►</span>Documents</span><span class="muted" id="count_documents"></span></h2>
    <div class="content">
      <div class="addrow">
        <input id="d_contact_id" type="number" placeholder="Contact ID (opt)" />
        <input id="d_property_id" type="number" placeholder="Property ID (opt)" />
        <input id="d_transaction_id" type="number" placeholder="Transaction ID (opt)" />
        <input id="d_attrs" placeholder='Attrs JSON (opt)' style="min-width:220px;" />
        <input id="d_file" type="file" />
        <button class="btn" onclick="uploadDocument()">Upload</button>
        <button class="btn secondary" onclick="loadDocuments()">Refresh</button>
      </div>
      <div class="sheet"><table>
        <thead><tr>
          <th style="width:64px;">ID</th><th>File Name</th><th>Type</th><th>Size</th><th>Linked To</th><th>Download</th>
        </tr></thead>
        <tbody id="tbl_documents"></tbody>
      </table></div>
    </div>
  </div>

  <script>
    // --- Helpers ---
    const $ = (id) => document.getElementById(id);
    const statusEl = $("status");
    const ingestUI = $("ingest_ui");
    let lastDraft = null;

    function asAttrs(v) {
      if (v === null || v === undefined) return "";
      if (typeof v === "object") return `<code class="attrs">${JSON.stringify(v)}</code>`;
      return v;
    }
    function safeJSON(text) {
      if (!text || !text.trim()) return {};
      try { return JSON.parse(text); } catch { alert("Attrs must be valid JSON"); throw new Error("bad json"); }
    }

    // --- Collapsible behavior ---
    document.querySelectorAll(".section h2").forEach(h2 => {
      h2.onclick = () => {
        const sec = h2.parentElement;
        const caret = h2.querySelector(".caret");
        const open = sec.classList.toggle("open");
        caret.textContent = open ? "▼" : "►";
      };
    });

    // --- Smart bar: ping + enter + mic + submit ---
    async function ping() {
      try {
        const res = await fetch("/health");
        statusEl.innerHTML = res.ok ? '<span class="ok">Connected</span>' : '<span class="err">Health failed</span>';
      } catch {
        statusEl.innerHTML = '<span class="err">Unable to reach backend</span>';
      }
    }
    $("smart_input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); submitIngest(); }
    });
    $("submit_btn").onclick = submitIngest;

    (function setupMic(){
      const btn = $("mic_btn"), input = $("smart_input");
      if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
        btn.disabled = true; btn.title = "Voice not supported by this browser"; return;
      }
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SR(); rec.lang = "en-US"; rec.interimResults = false; rec.maxAlternatives = 1;
      let listening = false;
      btn.onclick = () => { if (listening) { rec.stop(); return; } rec.start(); listening = true; btn.textContent = "⏹️"; };
      rec.onresult = (e) => { input.value = e.results[0][0].transcript; submitIngest(); };
      rec.onend = () => { listening = false; btn.textContent = "🎤"; };
      rec.onerror = () => { listening = false; btn.textContent = "🎤"; };
    })();

    async function submitIngest() {
      const text = $("smart_input").value.trim();
      if (!text) return;
      ingestUI.textContent = "Thinking…";
      lastDraft = null;
      try {
        const res = await fetch("/ingest", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify({ text }) });
        const data = await res.json();
        handleIngestResponse(data);
      } catch { ingestUI.innerHTML = '<span class="err">Failed to ingest</span>'; }
    }
    function handleIngestResponse(data) {
      if (data.status === "created") {
        ingestUI.innerHTML = `<span class="ok">Created ${data.entity} #${data.id}</span>`;
        refreshAll(); $("smart_input").value = ""; lastDraft = null; return;
      }
      if (data.status === "ask") {
        lastDraft = data.draft || null;
        const options = (data.options || []).map(opt => `<span class="pill" onclick="confirmIngest('${opt}')">${opt}</span>`).join("");
        ingestUI.innerHTML = `<strong>${data.question}</strong><div style="margin-top:8px;">${options}</div>`;
        return;
      }
      ingestUI.textContent = "Unexpected response.";
    }
    async function confirmIngest(choice) {
      if (choice === "cancel") { ingestUI.textContent = "Cancelled."; lastDraft = null; return; }
      if (!lastDraft) { ingestUI.textContent = "No draft to confirm."; return; }
      if (choice === "transaction" && (!lastDraft.contact_id || !lastDraft.property_id)) {
        const c = prompt("Transaction needs contact_id. Enter number:"); const p = prompt("Transaction needs property_id. Enter number:");
        if (!c || !p) { ingestUI.textContent = "Missing IDs. Cancelled."; return; }
        lastDraft.contact_id = Number(c); lastDraft.property_id = Number(p);
      }
      try {
        const res = await fetch("/ingest/confirm", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify({ choice, draft: lastDraft }) });
        const data = await res.json();
        if (data.status === "created") { ingestUI.innerHTML = `<span class="ok">Created ${data.entity} #${data.id}</span>`; refreshAll(); $("smart_input").value = ""; lastDraft = null; }
        else if (data.status === "cancelled") { ingestUI.textContent = "Cancelled."; lastDraft = null; }
        else { ingestUI.innerHTML = '<span class="err">Could not create item.</span>'; }
      } catch { ingestUI.innerHTML = '<span class="err">Confirm failed.</span>'; }
    }

    // --- Loaders + Add Row for each sheet ---
    async function loadContacts() {
      try {
        const res = await fetch("/contacts/"); const rows = await res.json();
        $("count_contacts").textContent = rows.length ? rows.length + " rows" : "";
        $("tbl_contacts").innerHTML = rows.map(r=>`
          <tr><td>${r.id}</td><td>${r.first_name||""}</td><td>${r.last_name||""}</td>
          <td>${r.email||""}</td><td>${r.phone||""}</td><td>${r.status||""}</td><td>${asAttrs(r.attrs)}</td></tr>`).join("");
      } catch (e) { $("tbl_contacts").innerHTML = `<tr><td colspan="7" class="err">${e}</td></tr>`; }
    }
    async function addContact() {
      try {
        const payload = {
          first_name: $("c_first").value, last_name: $("c_last").value,
          email: $("c_email").value || null, phone: $("c_phone").value || null,
          status: $("c_status").value || "new", attrs: safeJSON($("c_attrs").value || "{}")
        };
        const res = await fetch("/contacts/", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) { alert("Failed to add contact"); return; }
        $("c_first").value=$("c_last").value=$("c_email").value=$("c_phone").value=$("c_status").value=$("c_attrs").value="";
        await loadContacts();
      } catch {}
    }

    async function loadProperties() {
      try {
        const res = await fetch("/properties/"); const rows = await res.json();
        $("count_properties").textContent = rows.length ? rows.length + " rows" : "";
        $("tbl_properties").innerHTML = rows.map(r=>`
          <tr><td>${r.id}</td><td>${r.address||""}</td><td>${r.city||""}</td>
          <td>${r.state_province||""}</td><td>${r.country||""}</td><td>${r.status||""}</td><td>${asAttrs(r.attrs)}</td></tr>`).join("");
      } catch (e) { $("tbl_properties").innerHTML = `<tr><td colspan="7" class="err">${e}</td></tr>`; }
    }
    async function addProperty() {
      try {
        const payload = {
          address: $("p_address").value, city: $("p_city").value || null,
          state_province: $("p_state").value || null, country: $("p_country").value || "Canada",
          status: $("p_status").value || "prospect", attrs: safeJSON($("p_attrs").value || "{}")
        };
        const res = await resFetch("/properties/", payload);
        if (!res.ok) { alert("Failed to add property"); return; }
        $("p_address").value=$("p_city").value=$("p_state").value=$("p_country").value=$("p_status").value=$("p_attrs").value="";
        await loadProperties();
      } catch {}
    }

    async function loadTransactions() {
      try {
        const res = await fetch("/transactions/"); const rows = await res.json();
        $("count_transactions").textContent = rows.length ? rows.length + " rows" : "";
        $("tbl_transactions").innerHTML = rows.map(r=>`
          <tr><td>${r.id}</td><td>${r.contact_id}</td><td>${r.property_id}</td>
          <td>${r.side}</td><td>${r.stage}</td><td>${r.offer_price ?? ""}</td><td>${r.close_price ?? ""}</td><td>${asAttrs(r.attrs)}</td></tr>`).join("");
      } catch (e) { $("tbl_transactions").innerHTML = `<tr><td colspan="8" class="err">${e}</td></tr>`; }
    }
    async function addTransaction() {
      try {
        const payload = {
          contact_id: Number($("t_contact_id").value), property_id: Number($("t_property_id").value),
          side: $("t_side").value || "buy", stage: $("t_stage").value || "lead",
          offer_price: $("t_offer").value ? Number($("t_offer").value) : null,
          close_price: $("t_close").value ? Number($("t_close").value) : null,
          attrs: safeJSON($("t_attrs").value || "{}")
        };
        const res = await resFetch("/transactions/", payload);
        if (!res.ok) { alert("Failed to add transaction"); return; }
        $("t_contact_id").value=$("t_property_id").value=$("t_side").value="buy";$("t_stage").value=$("t_offer").value=$("t_close").value=$("t_attrs").value="";
        await loadTransactions();
      } catch {}
    }

    async function loadDocuments() {
      try {
        const res = await fetch("/documents/"); const rows = await res.json();
        $("count_documents").textContent = rows.length ? rows.length + " rows" : "";
        $("tbl_documents").innerHTML = rows.map(d=>`
          <tr><td>${d.id}</td><td>${d.filename}</td><td>${d.mime_type||""}</td><td>${d.size||""}</td>
          <td>${["contact:"+ (d.contact_id||""), "property:"+ (d.property_id||""), "transaction:"+ (d.transaction_id||"")].join(" ")}</td>
          <td>${d.download_url ? `<a href="${d.download_url}">download</a>` : ""}</td></tr>`).join("");
      } catch (e) { $("tbl_documents").innerHTML = `<tr><td colspan="6" class="err">${e}</td></tr>`; }
    }
    async function uploadDocument() {
      const f = $("d_file").files[0]; if (!f) { alert("Choose a file first"); return; }
      const fd = new FormData();
      fd.append("file", f);
      const c=$("d_contact_id").value, p=$("d_property_id").value, t=$("d_transaction_id").value, extra=$("d_attrs").value;
      if (c) fd.append("contact_id", c); if (p) fd.append("property_id", p); if (t) fd.append("transaction_id", t); if (extra) fd.append("attrs", extra);
      try {
        const res = await fetch("/documents/upload", { method:"POST", body: fd });
        if (!res.ok) { alert("Upload failed"); return; }
        $("d_contact_id").value=$("d_property_id").value=$("d_transaction_id").value=$("d_attrs").value=""; $("d_file").value="";
        await loadDocuments();
      } catch {}
    }

    // small helper to POST JSON
    async function resFetch(path, payload) {
      return fetch(path, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
    }

    function refreshAll(){ loadContacts(); loadProperties(); loadTransactions(); loadDocuments(); }

    // Init
    ping();
    refreshAll();
  </script>
</body>
</html>
"""
