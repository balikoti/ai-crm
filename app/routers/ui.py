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
  <title>AI CRM — Mini UI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; }
    body { margin: 16px; }
    h1 { margin: 0 0 12px; }
    nav { display:flex; gap:12px; align-items:center; margin:12px 0 16px; flex-wrap: wrap; }
    .micline { display:flex; gap:8px; flex: 1 1 420px; }
    input[type="text"] { flex:1; padding:10px; border:1px solid #cbd5e1; border-radius:10px; }
    button { padding:10px 12px; border:1px solid #0ea5e9; background:#0ea5e9; color:#fff; border-radius:10px; cursor:pointer; }
    a.btn { padding:10px 12px; border:1px solid #e5e7eb; background:#fff; border-radius:10px; text-decoration:none; color:#111827; }
    .grid { display:grid; gap:16px; grid-template-columns: repeat(auto-fit,minmax(320px,1fr)); }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
    .row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
    textarea, select, input[type="number"] { width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:8px; }
    table { width:100%; border-collapse:collapse; }
    th, td { border-top:1px solid #e5e7eb; padding:8px; text-align:left; vertical-align:top; }
    .muted { color:#6b7280; font-size:12px; }
    .attrs { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; background:#f8fafc; padding:4px 6px; border-radius:6px; }
    .ok { color:#22c55e; }
    .err { color:#ef4444; white-space:pre-wrap; }
  </style>
</head>
<body>
  <h1>AI CRM — Mini UI</h1>

  <nav>
    <div class="micline">
      <input id="voice_input" type="text" placeholder="Speak or type notes…">
      <button id="mic_btn" title="Voice to text">🎤</button>
    </div>
    <a class="btn" href="#contacts">Contacts</a>
    <a class="btn" href="#properties">Properties</a>
    <a class="btn" href="#transactions">Transactions</a>
    <a class="btn" href="#documents">Documents</a>
  </nav>

  <div id="status" class="muted" style="margin-bottom:12px;"></div>

  <div class="grid">
    <!-- Contacts -->
    <div class="card" id="contacts">
      <h2>Contacts</h2>
      <div class="row">
        <input id="c_first" placeholder="First name" />
        <input id="c_last" placeholder="Last name" />
      </div>
      <div class="row">
        <input id="c_email" placeholder="Email (optional)" />
        <input id="c_phone" placeholder="Phone (optional)" />
      </div>
      <div class="row">
        <input id="c_status" placeholder="Status (e.g., new, warm)" />
      </div>
      <div class="row">
        <textarea id="c_attrs" rows="3" placeholder='Attrs JSON (e.g., {"note": "first contact"})'></textarea>
      </div>
      <div class="row">
        <button onclick="createContact()">Add Contact</button>
        <button class="secondary" onclick="loadContacts()">Refresh</button>
      </div>
      <div id="contacts_table" style="margin-top:12px;"></div>
    </div>

    <!-- Properties -->
    <div class="card" id="properties">
      <h2>Properties</h2>
      <div class="row">
        <input id="p_address" placeholder="Address" />
      </div>
      <div class="row">
        <input id="p_city" placeholder="City" />
        <input id="p_state" placeholder "State/Province" />
      </div>
      <div class="row">
        <input id="p_country" placeholder="Country (default Canada)" />
        <input id="p_status" placeholder="Status (prospect/active/...)" />
      </div>
      <div class="row">
        <textarea id="p_attrs" rows="3" placeholder='Attrs JSON (e.g., {"bed":3,"bath":2,"list_price":950000})'></textarea>
      </div>
      <div class="row">
        <button onclick="createProperty()">Add Property</button>
        <button class="secondary" onclick="loadProperties()">Refresh</button>
      </div>
      <div id="properties_table" style="margin-top:12px;"></div>
    </div>

    <!-- Transactions -->
    <div class="card" id="transactions">
      <h2>Transactions</h2>
      <div class="row">
        <input id="t_contact_id" placeholder="Contact ID" />
        <input id="t_property_id" placeholder="Property ID" />
      </div>
      <div class="row">
        <select id="t_side">
          <option value="buy">buy</option>
          <option value="sell">sell</option>
          <option value="lease">lease</option>
        </select>
        <input id="t_stage" placeholder="Stage (lead/showing/offer/...)" />
      </div>
      <div class="row">
        <input id="t_offer" placeholder="Offer price (optional)" />
        <input id="t_close" placeholder="Close price (optional)" />
      </div>
      <div class="row">
        <textarea id="t_attrs" rows="3" placeholder='Attrs JSON (e.g., {"agent":"Alex","notes":"Hot lead"})'></textarea>
      </div>
      <div class="row">
        <button onclick="createTransaction()">Add Transaction</button>
        <button class="secondary" onclick="loadTransactions()">Refresh</button>
      </div>
      <div id="transactions_table" style="margin-top:12px;"></div>
    </div>

    <!-- Documents -->
    <div class="card" id="documents">
      <h2>Documents</h2>
      <div class="row">
        <input id="d_contact_id" type="number" placeholder="Contact ID (optional)" />
        <input id="d_property_id" type="number" placeholder="Property ID (optional)" />
        <input id="d_transaction_id" type="number" placeholder="Transaction ID (optional)" />
      </div>
      <div class="row">
        <input id="d_file" type="file" />
      </div>
      <div class="row">
        <textarea id="d_attrs" rows="2" placeholder='Attrs JSON (optional, e.g., {"tag":"offer"})'></textarea>
      </div>
      <div class="row">
        <button onclick="uploadDocument()">Upload File</button>
        <button class="secondary" onclick="loadDocuments()">Refresh</button>
      </div>
      <div id="documents_table" style="margin-top:12px;"></div>
    </div>
  </div>

  <script>
    const $ = (id) => document.getElementById(id);
    const statusEl = $("status");

    async function ping() {
      try {
        const res = await fetch("/health");
        statusEl.innerHTML = res.ok ? '<span class="ok">Connected</span>' : '<span class="err">Health failed</span>';
      } catch (e) {
        statusEl.innerHTML = '<span class="err">Unable to reach backend</span>';
      }
    }

    // Voice to Text (Web Speech API)
    (function setupMic(){
      const btn = $("mic_btn");
      if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
        btn.disabled = true; btn.title = "Voice not supported by this browser";
        return;
      }
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SR();
      rec.lang = "en-US";
      rec.interimResults = false;
      rec.maxAlternatives = 1;

      let listening = false;
      btn.onclick = () => {
        if (listening) { rec.stop(); return; }
        rec.start(); listening = true; btn.textContent = "⏹️";
      };
      rec.onresult = (e) => {
        const text = e.results[0][0].transcript;
        $("voice_input").value = text;
      };
      rec.onend = () => { listening = false; btn.textContent = "🎤"; };
      rec.onerror = () => { listening = false; btn.textContent = "🎤"; };
    })();

    function safeJSON(text) {
      if (!text || !text.trim()) return {};
      try { return JSON.parse(text); } catch (e) { alert("Attrs must be valid JSON"); throw e; }
    }

    function tbl(rows, headers) {
      if (!rows.length) return '<div class="muted">No rows</div>';
      let thead = "<tr>" + headers.map(h=>`<th>${h}</th>`).join("") + "</tr>";
      let body = rows.map(r => {
        return "<tr>" + headers.map(h => {
          let v = r[h];
          if (typeof v === "object" && v !== null) v = `<span class="attrs">${JSON.stringify(v)}</span>`;
          return `<td>${v ?? ""}</td>`;
        }).join("") + "</tr>";
      }).join("");
      return `<table><thead>${thead}</thead><tbody>${body}</tbody></table>`;
    }

    // Contacts
    async function loadContacts() {
      try {
        const res = await fetch("/contacts/");
        const data = await res.json();
        $("contacts_table").innerHTML = tbl(data, ["id","first_name","last_name","email","phone","status","attrs"]);
      } catch (e) { $("contacts_table").innerHTML = '<div class="err">'+e+'</div>'; }
    }
    async function createContact() {
      const payload = {
        first_name: $("c_first").value,
        last_name: $("c_last").value,
        email: $("c_email").value || null,
        phone: $("c_phone").value || null,
        status: $("c_status").value || "new",
        attrs: safeJSON($("c_attrs").value || '{}')
      };
      const res = await fetch("/contacts/", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { alert("Failed to add contact"); return; }
      await loadContacts();
    }

    // Properties
    async function loadProperties() {
      try {
        const res = await fetch("/properties/");
        const data = await res.json();
        $("properties_table").innerHTML = tbl(data, ["id","address","city","state_province","country","status","attrs"]);
      } catch (e) { $("properties_table").innerHTML = '<div class="err">'+e+'</div>'; }
    }
    async function createProperty() {
      const payload = {
        address: $("p_address").value,
        city: $("p_city").value || null,
        state_province: $("p_state").value || null,
        country: $("p_country").value || "Canada",
        status: $("p_status").value || "prospect",
        attrs: safeJSON($("p_attrs").value || '{}')
      };
      const res = await fetch("/properties/", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { alert("Failed to add property"); return; }
      await loadProperties();
    }

    // Transactions
    async function loadTransactions() {
      try {
        const res = await fetch("/transactions/");
        const data = await res.json();
        $("transactions_table").innerHTML = tbl(data, ["id","contact_id","property_id","side","stage","offer_price","close_price","attrs"]);
      } catch (e) { $("transactions_table").innerHTML = '<div class="err">'+e+'</div>'; }
    }
    async function createTransaction() {
      const payload = {
        contact_id: Number($("t_contact_id").value),
        property_id: Number($("t_property_id").value),
        side: $("t_side").value || "buy",
        stage: $("t_stage").value || "lead",
        offer_price: $("t_offer").value ? Number($("t_offer").value) : null,
        close_price: $("t_close").value ? Number($("t_close").value) : null,
        attrs: safeJSON($("t_attrs").value || '{}')
      };
      const res = await fetch("/transactions/", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { alert("Failed to add transaction"); return; }
      await loadTransactions();
    }

    // Documents
    async function loadDocuments() {
      try {
        const res = await fetch("/documents/");
        const data = await res.json();
        const rows = data.map(d => ({
          id: d.id,
          filename: d.filename,
          mime_type: d.mime_type,
          size: d.size,
          links: `<a href="${d.download_url}">download</a>`,
          contact_id: d.contact_id,
          property_id: d.property_id,
          transaction_id: d.transaction_id
        }));
        $("documents_table").innerHTML = tbl(rows, ["id","filename","mime_type","size","links","contact_id","property_id","transaction_id"]);
      } catch (e) { $("documents_table").innerHTML = '<div class="err">'+e+'</div>'; }
    }
    async function uploadDocument() {
      const f = $("d_file").files[0];
      if (!f) { alert("Pick a file first"); return; }
      const fd = new FormData();
      fd.append("file", f);
      const c = $("d_contact_id").value; if (c) fd.append("contact_id", c);
      const p = $("d_property_id").value; if (p) fd.append("property_id", p);
      const t = $("d_transaction_id").value; if (t) fd.append("transaction_id", t);
      const extra = $("d_attrs").value; if (extra) fd.append("attrs", extra);

      const res = await fetch("/documents/upload", { method:"POST", body: fd });
      if (!res.ok) { alert("Upload failed"); return; }
      await loadDocuments();
    }

    // Init
    ping();
    loadContacts();
    loadProperties();
    loadTransactions();
    loadDocuments();
  </script>
</body>
</html>
"""
