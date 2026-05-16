// bouracka-ui frontend — vanilla JS SPA
// Hash routing: #/run, #/runs, #/results/:rid, #/bugs, #/about
// Reference: _config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md §3.2

const API = '';  // same origin
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const fmt = {
  ts: s => s ? new Date(s).toLocaleString() : '',
  pct: n => (n == null ? 'n/a' : (n * 100).toFixed(0) + '%'),
};

// Minimal HTML escape for content we render verbatim (log tails, error msgs, ...).
function escapeHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// On the results page we hide the matrix + drift cards and reuse the
// "Provenance" card as a log-tail panel during in-flight + dispatch-failed
// states. Without retitling the card header, users see "Provenance" above
// log lines — confusing. This helper renames the header in lockstep with
// what the panel actually contains.
function retitleProvCard(newTitle) {
  const provBody = document.querySelector('#results-provenance');
  if (!provBody) return;
  const card = provBody.closest('.card');
  if (!card) return;
  const h2 = card.querySelector('h2');
  if (h2) h2.textContent = newTitle;
}

// ──────────────────────────────────────────────────────────────────────────
// Router
// ──────────────────────────────────────────────────────────────────────────
const routes = {
  '/run':     renderRun,
  '/runs':    renderRunsList,
  '/results': renderResults,   // /results/:rid
  '/bugs':    renderBugs,
  '/about':   renderAbout,
};

function route() {
  const hash = window.location.hash.replace(/^#/, '') || '/run';
  const [path, ...args] = hash.split('/').filter(Boolean);
  const key = '/' + (path || 'run');
  const handler = routes[key] || routes['/run'];
  // Update active nav
  $$('#main-nav a').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === '#' + key);
  });
  handler(args);
}

window.addEventListener('hashchange', route);
window.addEventListener('DOMContentLoaded', () => {
  route();
  // BUG-BUI-004: wire the in-app Back button. Uses SPA history so the UX is
  // identical across browsers and predictable inside hash routing. The button
  // is disabled when there's nowhere to go back to (first page in history).
  const backBtn = document.getElementById('back-btn');
  if (backBtn) {
    backBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.history.back();
    });
    // Initial enabled state — best-effort; history.length > 1 means we have
    // at least one prior entry. Not perfect (length includes the current
    // entry + any in-tab navigations) but good enough to grey out on first
    // load.
    backBtn.disabled = (window.history.length <= 1);
  }
});

// Keep Back-button enabled-state in sync as the user navigates.
window.addEventListener('hashchange', () => {
  const backBtn = document.getElementById('back-btn');
  if (backBtn) backBtn.disabled = (window.history.length <= 1);
});

function renderTemplate(id) {
  const tpl = $('#' + id);
  const main = $('#app');
  main.innerHTML = '';
  main.appendChild(tpl.content.cloneNode(true));
}

// ──────────────────────────────────────────────────────────────────────────
// API helpers
// ──────────────────────────────────────────────────────────────────────────
async function api(path, opts = {}) {
  const r = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}: ${path}`);
  return r.json();
}

// Like api() but returns {status, body, ok} without throwing — used for
// endpoints that intentionally return non-200 status (202 in-flight, 404 NF).
// BUG-BUI-002: GET /api/runs/{rid} can return 202 (run in flight) which is
// not an error — caller needs to inspect status code, not just .ok.
async function apiRaw(path, opts = {}) {
  const r = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  let body = null;
  try { body = await r.json(); } catch (_) { /* non-JSON body */ }
  return { status: r.status, ok: r.ok, body };
}

// ──────────────────────────────────────────────────────────────────────────
// /run page
// ──────────────────────────────────────────────────────────────────────────
async function renderRun() {
  renderTemplate('tpl-run');

  const envSelect = $('#env-select');
  const fwSelect  = $('#fw-select');
  const tcGrid    = $('#tc-grid');
  const runBtn    = $('#run-btn');
  const tcCount   = $('#tc-count');

  // Load envs
  const envs = await api('/api/envs');
  envSelect.innerHTML = envs.map(e =>
    `<option value="${e.schema_env}" data-code="${e.code}" data-url="${e.base_url || ''}">${e.code} — ${e.name_en}</option>`
  ).join('');
  envSelect.addEventListener('change', updateEnvMeta);
  updateEnvMeta();

  function updateEnvMeta() {
    const opt = envSelect.selectedOptions[0];
    $('#env-meta').textContent =
      `Schema env: ${envSelect.value}  ·  base URL: ${opt.dataset.url}`;
    loadTcs();
  }

  // Load TCs
  async function loadTcs() {
    tcGrid.innerHTML = '<div class="loading">Loading TCs…</div>';
    const env = envSelect.value;
    const fw = fwSelect.value === 'all' ? '' : fwSelect.value;
    const qs = new URLSearchParams({ env, ...(fw && { framework: fw }) });
    const tcs = await api(`/api/tcs?${qs}`);
    if (tcs.length === 0) {
      tcGrid.innerHTML = '<div class="empty">No TCs match the filter.</div>';
      return;
    }
    tcGrid.innerHTML = tcs.map(tc => `
      <label class="tc-grid__item">
        <div><input type="checkbox" value="${tc.code}" data-tc> <span class="tc-grid__code">${tc.code}</span></div>
        <div class="tc-grid__name">${tc.name_en || tc.name_cs || ''}</div>
        <div class="tc-grid__meta">
          <span class="pill sev-${tc.severity || 'X'}">${tc.severity || '?'}</span>
          <span class="pill" style="background: var(--c-ink-5); color: var(--c-ink-2);">${tc.priority || ''}</span>
        </div>
      </label>
    `).join('');
    $$('input[data-tc]', tcGrid).forEach(cb => cb.addEventListener('change', updateRunBtn));
    updateRunBtn();
  }

  fwSelect.addEventListener('change', loadTcs);

  function updateRunBtn() {
    const sel = $$('input[data-tc]:checked', tcGrid).map(i => i.value);
    runBtn.disabled = sel.length === 0;
    tcCount.textContent = `${sel.length} selected`;
    return sel;
  }

  $('#select-all-btn').addEventListener('click', () => {
    $$('input[data-tc]', tcGrid).forEach(cb => cb.checked = true);
    updateRunBtn();
  });
  $('#select-none-btn').addEventListener('click', () => {
    $$('input[data-tc]', tcGrid).forEach(cb => cb.checked = false);
    updateRunBtn();
  });

  // Run trigger
  runBtn.addEventListener('click', async () => {
    const tcs = updateRunBtn();
    const env = envSelect.value;
    const fw = fwSelect.value;
    runBtn.disabled = true;
    $('#run-status').textContent = 'Triggering…';

    const resp = await api('/api/runs', {
      method: 'POST',
      body: JSON.stringify({
        env,
        tcs,
        frameworks: [fw],
      }),
    });
    const rid = resp.run_id;
    $('#run-status').innerHTML = `Run started: <code>${rid}</code>`;
    $('#log-card').style.display = '';
    streamLog(rid);
  });
}

function streamLog(rid) {
  const stream = $('#log-stream');
  stream.innerHTML = '';
  const es = new EventSource(`/api/runs/${rid}/log`);
  es.addEventListener('stdout', e => {
    const line = document.createElement('div');
    line.className = 'log-line';
    if (e.data.startsWith('===')) line.classList.add('cmd');
    if (e.data.includes('[cypress]'))    line.classList.add('fw-cypress');
    if (e.data.includes('[playwright]')) line.classList.add('fw-playwright');
    if (e.data.includes('[selenium]'))   line.classList.add('fw-selenium');
    line.textContent = e.data;
    stream.appendChild(line);
    stream.scrollTop = stream.scrollHeight;
  });
  es.addEventListener('done', e => {
    const data = JSON.parse(e.data);
    es.close();
    setTimeout(() => { window.location.hash = '#/results/' + rid; }, 700);
  });
  es.addEventListener('error', e => {
    const line = document.createElement('div');
    line.className = 'log-line';
    line.style.color = 'var(--c-sev-A)';
    line.textContent = '[bouracka-ui] stream error';
    stream.appendChild(line);
    es.close();
  });
}

// ──────────────────────────────────────────────────────────────────────────
// /runs page (past runs list)
// ──────────────────────────────────────────────────────────────────────────
async function renderRunsList() {
  renderTemplate('tpl-runs');

  // Populate env filter from envs
  const envs = await api('/api/envs');
  $('#runs-env-filter').innerHTML = '<option value="">(all)</option>' +
    envs.map(e => `<option value="${e.schema_env}">${e.code}</option>`).join('');

  async function load() {
    const env = $('#runs-env-filter').value;
    const limit = $('#runs-limit').value;
    const qs = new URLSearchParams({ limit, ...(env && { env }) });
    const rows = await api(`/api/runs?${qs}`);
    const tbody = $('#runs-table tbody');
    if (rows.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="empty">No runs yet — kick one off via <a href="#/run">/run</a>.</td></tr>';
      return;
    }
    tbody.innerHTML = rows.map(r => `
      <tr style="cursor: pointer" onclick="window.location.hash='#/results/${r.run_id}'">
        <td>${fmt.ts(r.started_at)}</td>
        <td><code>${r.env}</code></td>
        <td>${r.total_tcs}</td>
        <td><span class="pill verdict-pass">${r.passed}</span></td>
        <td>${r.failed > 0 ? `<span class="pill verdict-fail">${r.failed}</span>` : r.failed}</td>
        <td>${r.skipped > 0 ? `<span class="pill verdict-skip-drift">${r.skipped}</span>` : 0}</td>
        <td>${r.parity_divergence_count > 0 ? `<span class="pill parity-divergence">${r.parity_divergence_count}</span>` : 0}</td>
        <td><code>${r.run_id}</code></td>
      </tr>
    `).join('');
  }

  $('#runs-env-filter').addEventListener('change', load);
  $('#runs-limit').addEventListener('change', load);
  $('#runs-refresh').addEventListener('click', load);

  // Bundle import (HP Elite air-gap)
  $('#bundle-import-btn').addEventListener('click', () => $('#bundle-file-input').click());
  $('#bundle-file-input').addEventListener('change', async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const fd = new FormData();
    fd.append('file', f);
    try {
      const resp = await fetch('/api/bundles/import', { method: 'POST', body: fd });
      if (!resp.ok) {
        const err = await resp.text();
        alert(`Import failed: ${err}`);
        return;
      }
      const info = await resp.json();
      window.location.hash = '#/results/' + info.run_id;
    } catch (err) {
      alert('Import failed: ' + err.message);
    }
  });

  load();
}

// ──────────────────────────────────────────────────────────────────────────
// Results-page helpers (F-01..F-06 from TES-GAP-ANALYSIS v0.1.3)
// ──────────────────────────────────────────────────────────────────────────

// F-06: toggle the per-TC drill-down detail row (accordion)
function toggleTcDetail(tcCode) {
  const detail = document.querySelector(`tr.tc-detail[data-tc="${CSS.escape(tcCode)}"]`);
  if (!detail) return;
  detail.style.display = (detail.style.display === 'none' || !detail.style.display) ? '' : 'none';
}
window.toggleTcDetail = toggleTcDetail;

// F-04: client-side filter on the verdict matrix
function applyMatrixFilter(filterKind) {
  const rows = document.querySelectorAll('#results-matrix tbody tr.tc-row');
  rows.forEach(row => {
    let show = true;
    if (filterKind === 'fail')    show = row.dataset.hasFail === '1';
    if (filterKind === 'skip')    show = row.dataset.allSkip === '1';
    if (filterKind === 'diverge') show = row.dataset.parity === 'divergence';
    // 'all' = show everything
    row.style.display = show ? '' : 'none';
    // Hide the corresponding detail row too if its parent is hidden
    const detail = row.nextElementSibling;
    if (detail && detail.classList.contains('tc-detail')) {
      if (!show) detail.style.display = 'none';
      // If showing the parent, leave detail at whatever state user toggled it to
      // (keeps user's drill-down choices stable across filter changes)
    }
  });
}
window.applyMatrixFilter = applyMatrixFilter;

// F-04: client-side sort of the verdict matrix
function applyMatrixSort(sortKey) {
  const tbody = document.querySelector('#results-matrix tbody');
  if (!tbody) return;
  // Capture rows as pairs (tc-row, tc-detail) so detail follows its parent.
  const pairs = [];
  let current = null;
  tbody.querySelectorAll('tr').forEach(tr => {
    if (tr.classList.contains('tc-row')) {
      if (current) pairs.push(current);
      current = { row: tr, detail: null };
    } else if (tr.classList.contains('tc-detail') && current) {
      current.detail = tr;
    }
  });
  if (current) pairs.push(current);

  pairs.sort((a, b) => {
    if (sortKey === 'tc') {
      return a.row.dataset.tc.localeCompare(b.row.dataset.tc);
    }
    if (sortKey === 'verdict') {
      // Failures first (data-has-fail=1), then skips, then everything else.
      const score = (r) => (r.dataset.hasFail === '1' ? 0 : (r.dataset.allSkip === '1' ? 2 : 1));
      const sa = score(a.row), sb = score(b.row);
      if (sa !== sb) return sa - sb;
      return a.row.dataset.tc.localeCompare(b.row.dataset.tc);
    }
    if (sortKey === 'parity') {
      // divergence first, then not-applicable, then agree.
      const order = { 'divergence': 0, 'not-applicable': 1, 'agree': 2 };
      const oa = order[a.row.dataset.parity] ?? 9;
      const ob = order[b.row.dataset.parity] ?? 9;
      if (oa !== ob) return oa - ob;
      return a.row.dataset.tc.localeCompare(b.row.dataset.tc);
    }
    return 0;
  });

  // Re-attach in sorted order
  const frag = document.createDocumentFragment();
  pairs.forEach(p => {
    frag.appendChild(p.row);
    if (p.detail) frag.appendChild(p.detail);
  });
  tbody.appendChild(frag);
}
window.applyMatrixSort = applyMatrixSort;

// F-02: copy an evidence path to clipboard so the operator can open the file
// via file explorer. v0.1.4 plans to wire a streaming endpoint.
function copyEvidencePath(ev) {
  ev.preventDefault();
  const path = ev.currentTarget.dataset.path;
  if (!path) return;
  // Try modern clipboard API; fall back to a textarea trick if unavailable.
  try {
    navigator.clipboard.writeText(path).then(() => {
      _flashCopyToast(ev.currentTarget, 'copied: ' + path);
    }, () => {
      _legacyCopy(path, ev.currentTarget);
    });
  } catch (_) {
    _legacyCopy(path, ev.currentTarget);
  }
}
window.copyEvidencePath = copyEvidencePath;

function _legacyCopy(text, anchor) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); _flashCopyToast(anchor, 'copied: ' + text); }
  catch (_) { _flashCopyToast(anchor, 'copy failed'); }
  document.body.removeChild(ta);
}

function _flashCopyToast(anchor, msg) {
  const toast = document.createElement('div');
  toast.textContent = msg;
  toast.style.cssText = 'position:fixed; bottom: 1em; right: 1em; padding: 0.5em 1em; background: var(--c-ink-2, #1f2937); color: white; border-radius: 4px; font-size: var(--fs-sm); z-index: 9999;';
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 1800);
}

// ──────────────────────────────────────────────────────────────────────────
// /results/:rid page
// ──────────────────────────────────────────────────────────────────────────
// Module-level poller handle so navigation away stops the loop cleanly.
let _resultsPollTimer = null;

async function renderResults(args) {
  renderTemplate('tpl-results');
  // Cancel any pre-existing poller (e.g. user navigated to another results page)
  if (_resultsPollTimer) { clearTimeout(_resultsPollTimer); _resultsPollTimer = null; }
  const rid = args.join('/');
  if (!rid) {
    $('#app').innerHTML = '<div class="empty">No run_id in URL.</div>';
    return;
  }
  // Stop polling when the route changes (user clicks Run / Bugs / etc.)
  const stopPollOnHashChange = () => {
    if (_resultsPollTimer) { clearTimeout(_resultsPollTimer); _resultsPollTimer = null; }
    window.removeEventListener('hashchange', stopPollOnHashChange);
  };
  window.addEventListener('hashchange', stopPollOnHashChange);

  await loadAndRenderResults(rid);
}

// Single iteration: fetch /api/runs/{rid}, dispatch to one of three render modes
// (in-flight, dispatch-failed, full-envelope), schedule next poll if needed.
// BUG-BUI-002: 202 = run in flight → poll; 200 with status field = dispatch
// failed; 200 with results = render full; 404 = not found.
async function loadAndRenderResults(rid) {
  const r = await apiRaw('/api/runs/' + rid);
  if (r.status === 404) {
    $('#app').innerHTML = `<div class="empty">Run not found: <code>${rid}</code>.<br>
      <small>If you just kicked this run off, give it a moment — it may still be spinning up. <a href="#/results/${rid}">Reload</a>.</small></div>`;
    return;
  }
  if (!r.body) {
    $('#app').innerHTML = `<div class="empty">Server returned HTTP ${r.status} with no JSON body. <a href="#/results/${rid}">Reload</a>.</div>`;
    return;
  }
  // 202 → run in flight; render progress view and schedule next poll
  if (r.status === 202) {
    renderResultsInFlight(rid, r.body);
    _resultsPollTimer = setTimeout(() => loadAndRenderResults(rid), 2000);
    return;
  }
  // 200 with status field but no results → dispatch finished without producing envelope
  if (r.body.status && !r.body.results) {
    renderResultsDispatchFailed(rid, r.body);
    return;
  }
  // 200 with full envelope → normal render
  renderResultsFullEnvelope(rid, r.body);
}

function renderResultsInFlight(rid, body) {
  $('#results-title').innerHTML = `Run <code>${rid}</code> &nbsp; <span class="pill" style="background: var(--c-warn, #f59e0b); color: #fff;">${body.status}</span>`;
  // Hide cards that need the full envelope until it's ready
  const matrixCard = $('#results-matrix')?.closest('.card');
  if (matrixCard) matrixCard.style.display = 'none';
  if ($('#results-drift')) $('#results-drift').style.display = 'none';
  // Hide bundle-export buttons until envelope exists
  if ($('#bundle-export-btn')) $('#bundle-export-btn').style.visibility = 'hidden';
  if ($('#bundle-export-full-btn')) $('#bundle-export-full-btn').style.visibility = 'hidden';
  // Re-title the provenance card as "Live log" while in flight (the panel's
  // contents are log lines, not git/host provenance).
  retitleProvCard('Live log');

  const fwList = (body.frameworks || []).join(' · ');
  const tcList = (body.tcs || []).map(t => `<code>${t}</code>`).join(', ');
  $('#results-summary').innerHTML = `
    <p>
      <span class="pill verdict-pass">env: ${body.env}</span>
      <span class="pill" style="background: var(--c-ink-5); color: var(--c-ink-2);">${fwList}</span>
      &nbsp; started ${fmt.ts(body.started_at)}
    </p>
    <p><strong>Test cases:</strong> ${tcList}</p>
    <p><strong>Status:</strong> ${body.status} — polling every 2 s until the envelope is written. You can navigate away; results stay accessible via the Runs page.</p>
  `;
  // Re-use #results-provenance card as a log-tail panel during in-flight phase
  const logTail = (body.log_tail || []).slice(-30).join('\n');
  $('#results-provenance').innerHTML = `<div class="log-stream" style="max-height: 280px; overflow:auto; white-space: pre-wrap;">${escapeHtml(logTail) || '(awaiting first log lines…)'}</div>`;
}

function renderResultsDispatchFailed(rid, body) {
  $('#results-title').innerHTML = `Run <code>${rid}</code> &nbsp; <span class="pill verdict-fail">dispatch failed</span>`;
  const matrixCard = $('#results-matrix')?.closest('.card');
  if (matrixCard) matrixCard.style.display = 'none';
  if ($('#results-drift')) $('#results-drift').style.display = 'none';
  if ($('#bundle-export-btn')) $('#bundle-export-btn').style.visibility = 'hidden';
  if ($('#bundle-export-full-btn')) $('#bundle-export-full-btn').style.visibility = 'hidden';
  retitleProvCard('Dispatch log');
  $('#results-summary').innerHTML = `
    <p><span class="pill verdict-fail">no envelope produced</span> &nbsp; status: ${body.status} &nbsp; exit_code: ${body.exit_code}</p>
    <p>The run finished but <code>tools/consolidate_results.py</code> didn't produce a v0.1 envelope file at <code>${body.envelope_path || 'runs/cross-framework-*.json'}</code>. Inspect the log below to identify which of the following applies:</p>
    <ul style="margin-left: var(--sp-6); line-height: 1.6;">
      <li><strong>Framework binary missing on PATH</strong> — <code>npx</code> / <code>cypress</code> / <code>playwright</code> not installed or not in PATH on this machine. Symptom: <code>tooling not found: [WinError 2]</code> in log.</li>
      <li><strong>pytest plugin missing</strong> — <code>pytest-json-report</code> not installed in this venv. Symptom: <code>unrecognized arguments: --json-report</code> from selenium suite. Fix: <code>pip install pytest-json-report</code> (auto-installed in v0.1.0+).</li>
      <li><strong>Repo root mis-detected</strong> — bouracka-ui couldn't locate <code>tools/consolidate_results.py</code> relative to where it's running. Symptom: log shows consolidator path inside <code>.venv/</code> or a parent. Fix: set <code>BOURACKA_UI_REPO_ROOT</code> env var to the bouracka-tests directory.</li>
      <li><strong>No test specs matched</strong> — TC selection produced a glob that didn't resolve to any spec files. Symptom: framework exits 0 but with no test output.</li>
    </ul>
    <p style="margin-top: var(--sp-3);">Tool availability snapshot is on the <a href="#/about">About</a> page.</p>
  `;
  const logTail = (body.log_tail || []).join('\n');
  $('#results-provenance').innerHTML = `<div class="log-stream" style="max-height: 480px; overflow:auto; white-space: pre-wrap;">${escapeHtml(logTail) || '(no log)'}</div>`;
}

function renderResultsFullEnvelope(rid, env) {
  // Reset visibility (in case we transitioned from in-flight view)
  const matrixCard = $('#results-matrix')?.closest('.card');
  if (matrixCard) matrixCard.style.display = '';
  if ($('#bundle-export-btn')) $('#bundle-export-btn').style.visibility = '';
  if ($('#bundle-export-full-btn')) $('#bundle-export-full-btn').style.visibility = '';
  // Restore the provenance card's title (we may have retitled it during a
  // prior in-flight or dispatch-failed render).
  retitleProvCard('Provenance');

  $('#results-title').innerHTML = `Run <code>${rid}</code>`;

  // Wire bundle-export hrefs (HP Elite workflow)
  $('#bundle-export-btn').setAttribute('href', `/api/runs/${rid}/bundle?full=false`);
  $('#bundle-export-full-btn').setAttribute('href', `/api/runs/${rid}/bundle?full=true`);

  const s = env.summary;
  $('#results-summary').innerHTML = `
    <div class="chip-strip">
      <div class="chip"><div class="chip__num">${s.total_tcs}</div><div class="chip__label">TCs</div></div>
      <div class="chip"><div class="chip__num">${s.passed}</div><div class="chip__label">Pass</div></div>
      <div class="chip fail"><div class="chip__num">${s.failed}</div><div class="chip__label">Fail</div></div>
      <div class="chip skip"><div class="chip__num">${s.skipped}</div><div class="chip__label">Skip</div></div>
      <div class="chip soft"><div class="chip__num">${s.soft_passed}</div><div class="chip__label">Soft</div></div>
      <div class="chip"><div class="chip__num">${fmt.pct(s.pass_rate_strict)}</div><div class="chip__label">Strict</div></div>
      <div class="chip"><div class="chip__num">${fmt.pct(s.pass_rate_drift_aware)}</div><div class="chip__label">Drift-aware</div></div>
      <div class="chip"><div class="chip__num">${s.parity_divergence_count}</div><div class="chip__label">Diverge</div></div>
    </div>
    <p>
      <span class="pill verdict-pass">env: ${env.env}</span>
      <span class="pill" style="background: var(--c-ink-5); color: var(--c-ink-2);">${env.frameworks.join(' · ')}</span>
      &nbsp; ${fmt.ts(env.started_at)} → ${fmt.ts(env.ended_at)} (${env.duration_ms} ms)
    </p>
  `;

  // Verdict matrix — F-01..F-04, F-06 from TES-GAP-ANALYSIS v0.1.3
  const fws = env.frameworks;

  // F-04: Filter/sort toolbar above the matrix
  // (Inserted into the matrix card so it stays visually grouped)
  let toolbar = $('#matrix-toolbar');
  if (!toolbar) {
    toolbar = document.createElement('div');
    toolbar.id = 'matrix-toolbar';
    toolbar.className = 'filter-row';
    toolbar.style.marginBottom = 'var(--sp-2)';
    const matrixHeader = matrixCard.querySelector('h2');
    if (matrixHeader) matrixHeader.insertAdjacentElement('afterend', toolbar);
    else matrixCard.insertBefore(toolbar, matrixCard.firstChild);
  }
  toolbar.innerHTML = `
    <span style="color: var(--c-ink-3); font-size: var(--fs-sm);">Filter:</span>
    <button class="matrix-filter active" data-filter="all">All (${env.results.length})</button>
    <button class="matrix-filter" data-filter="fail">Failures (${env.results.filter(r => anyFailed(r)).length})</button>
    <button class="matrix-filter" data-filter="skip">Skips (${env.results.filter(r => Object.values(r.verdicts).every(v => v === 'skip-drift' || v === 'skip-other' || v === 'missing')).length})</button>
    <button class="matrix-filter" data-filter="diverge">Divergence (${env.results.filter(r => r.parity_status === 'divergence').length})</button>
    <span style="margin-left: auto; color: var(--c-ink-3); font-size: var(--fs-sm);">Sort:</span>
    <select id="matrix-sort">
      <option value="tc">by TC code</option>
      <option value="verdict">by verdict (failures first)</option>
      <option value="parity">by parity</option>
    </select>
  `;

  // F-01 + F-03: cell tooltip with per-fw duration + error message
  // F-02: evidence icons per cell (📷 screenshot, 🎥 video, 📦 trace)
  function cellHtml(r, f) {
    const v = r.verdicts[f] || 'missing';
    const dur = (r.duration_ms || {})[f];
    const err = (r.error_messages || {})[f];
    const ev = (r.evidence || {})[f] || {};
    const tooltipBits = [];
    if (dur != null) tooltipBits.push(`${f}: ${dur} ms`);
    if (err) tooltipBits.push(`error: ${err.slice(0, 200)}`);
    const tooltip = tooltipBits.length ? ` title="${escapeHtml(tooltipBits.join('\n'))}"` : '';
    // Evidence icons (F-02) — click copies path to clipboard for now;
    // v0.1.4 will wire a /api/runs/{rid}/evidence/{fw}/{kind} endpoint.
    const evIcons = [];
    if (ev.screenshot_ref) evIcons.push(`<a href="#" class="ev-icon" title="screenshot: ${escapeHtml(ev.screenshot_ref)}" data-path="${escapeHtml(ev.screenshot_ref)}" onclick="copyEvidencePath(event)">&#128247;</a>`);
    if (ev.video_ref) evIcons.push(`<a href="#" class="ev-icon" title="video: ${escapeHtml(ev.video_ref)}" data-path="${escapeHtml(ev.video_ref)}" onclick="copyEvidencePath(event)">&#127909;</a>`);
    if (ev.trace_ref) evIcons.push(`<a href="#" class="ev-icon" title="trace: ${escapeHtml(ev.trace_ref)}" data-path="${escapeHtml(ev.trace_ref)}" onclick="copyEvidencePath(event)">&#128230;</a>`);
    return `<td${tooltip}><span class="pill verdict-${v}">${v}</span> ${evIcons.join(' ')}</td>`;
  }

  // F-06: per-TC drill-down accordion — each TC row gets a hidden detail row
  // beneath it; click TC code to toggle.
  function detailRowHtml(r) {
    const detailParts = [];
    if (r.covered_tt && r.covered_tt.length) {
      detailParts.push(`<div><strong>Covered TestTargets:</strong> ${r.covered_tt.map(t => `<code>${escapeHtml(t)}</code>`).join(', ')}</div>`);
    }
    if (r.viewport) detailParts.push(`<div><strong>Viewport:</strong> <code>${escapeHtml(r.viewport)}</code></div>`);
    if (r.bug_ref) detailParts.push(`<div><strong>Linked bug:</strong> <code>${escapeHtml(r.bug_ref)}</code></div>`);
    if (r.soft_pass_reason) detailParts.push(`<div><strong>Soft-pass reason:</strong> ${escapeHtml(r.soft_pass_reason)}</div>`);
    // Per-fw breakdown
    detailParts.push('<div style="margin-top: var(--sp-2);"><strong>Per-framework detail:</strong></div>');
    const fwRows = fws.map(f => {
      const v = r.verdicts[f] || 'missing';
      const dur = (r.duration_ms || {})[f];
      const note = (r.framework_specific_notes || {})[f];
      const err = (r.error_messages || {})[f];
      const ev = (r.evidence || {})[f] || {};
      const evList = [];
      if (ev.screenshot_ref) evList.push(`screenshot: <code>${escapeHtml(ev.screenshot_ref)}</code>`);
      if (ev.video_ref) evList.push(`video: <code>${escapeHtml(ev.video_ref)}</code>`);
      if (ev.trace_ref) evList.push(`trace: <code>${escapeHtml(ev.trace_ref)}</code>`);
      return `
        <div style="margin-left: var(--sp-3); margin-top: 0.3em; padding: 0.3em 0.5em; background: var(--c-ink-6, #f9fafb); border-left: 2px solid var(--c-ink-5, #e5e7eb);">
          <strong>${escapeHtml(f)}</strong>:
          <span class="pill verdict-${v}">${v}</span>
          ${dur != null ? `<span style="color: var(--c-ink-3); font-size: var(--fs-sm);">${dur} ms</span>` : ''}
          ${note ? `<br><small>raw: <code>${escapeHtml(note)}</code></small>` : ''}
          ${err ? `<div style="margin-top: 0.3em; padding: 0.4em; background: var(--c-fail-bg, #fee2e2); border-left: 2px solid var(--c-fail, #ef4444); font-family: var(--f-mono); font-size: var(--fs-sm); white-space: pre-wrap; max-height: 200px; overflow:auto;">${escapeHtml(err)}</div>` : ''}
          ${evList.length ? `<div style="margin-top: 0.3em; font-size: var(--fs-sm);">${evList.join(' &middot; ')}</div>` : ''}
        </div>
      `;
    }).join('');
    detailParts.push(fwRows);
    return `<tr class="tc-detail" data-tc="${escapeHtml(r.tc_code)}" style="display:none;">
      <td colspan="${fws.length + 3}" style="background: var(--c-ink-6, #f9fafb); padding: var(--sp-3);">
        ${detailParts.join('')}
      </td>
    </tr>`;
  }

  $('#results-matrix thead').innerHTML = `<tr>
    <th>TC</th>
    ${fws.map(f => `<th>${escapeHtml(f)}</th>`).join('')}
    <th>Parity</th>
    <th>File bug</th>
  </tr>`;
  $('#results-matrix tbody').innerHTML = env.results.map(r => `
    <tr class="tc-row" data-tc="${escapeHtml(r.tc_code)}" data-has-fail="${anyFailed(r) ? '1' : '0'}" data-all-skip="${Object.values(r.verdicts).every(v => v === 'skip-drift' || v === 'skip-other' || v === 'missing') ? '1' : '0'}" data-parity="${escapeHtml(r.parity_status)}">
      <td><code class="tc-code-clickable" style="cursor: pointer; text-decoration: underline dotted;" onclick="toggleTcDetail('${escapeHtml(r.tc_code)}')" title="Click to expand detail">${escapeHtml(r.tc_code)}</code></td>
      ${fws.map(f => cellHtml(r, f)).join('')}
      <td><span class="pill parity-${r.parity_status}">${r.parity_status}</span></td>
      <td>${anyFailed(r) ? `<a href="#/bugs?tc=${r.tc_code}&run=${env.run_id}" onclick="sessionStorage.setItem('bug-prefill', JSON.stringify({tc:'${r.tc_code}',run:'${env.run_id}',env:'${env.env}',error:${JSON.stringify(Object.entries(r.error_messages||{}).filter(([k,v])=>v).map(([k,v])=>k+': '+v).join('\\n'))}}))">+ bug</a>` : ''}</td>
    </tr>
    ${detailRowHtml(r)}
  `).join('');

  // Wire filter buttons + sort dropdown (F-04)
  $$('.matrix-filter', toolbar).forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.matrix-filter', toolbar).forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyMatrixFilter(btn.dataset.filter);
    });
  });
  $('#matrix-sort').addEventListener('change', (e) => applyMatrixSort(e.target.value));

  // Drift forensic — F-05 enriched card
  if (env.drift_forensic && env.drift_forensic.active) {
    $('#results-drift').style.display = '';
    const df = env.drift_forensic;
    // Drift-type narrative templates (F-05)
    const driftNarratives = {
      'recaptcha-v3': 'Score-based bot detection on demo/tst-demo environments. SPA routes traversing POST /api/reports trigger 403 responses without correlation context. Resolves at Cíl-2 baseline (tst.demo with bypass token).',
      'recaptcha-v2': 'Challenge-based bot detection. Requires manual CAPTCHA solving; not automatable. SKIP via drift guard until bypass token is provisioned.',
      'rate-limit': 'Per-IP request quota exceeded. SUPIN-internal IPs typically have higher quotas; verify your tester laptop is on SUPIN VPN if drift persists.',
      'ipc-114-renderer-kill': 'BUG-CY-001 — Chromium renderer process killed via bad_message reason 114 on Cypress headed-mode launch. Affects same-origin SPA tests that establish persistent connections. Workaround: use Selenium for affected ALT-* tests until BUG-CY-001 Round-5 fix lands.',
      'same-origin-pool': 'HTTP connection-pool exhaustion on same-origin persistent connections. Symptoms include test timeouts after first successful navigation. Related to BUG-CY-001 hypothesis.',
      'other-401-403': 'Authentication rejection drift. Verify test credentials are current and the env has not rotated its auth provider.',
    };
    const narrative = driftNarratives[df.drift_type] || '<em>(no narrative for this drift type yet)</em>';
    $('#results-drift-body').innerHTML = `
      <div style="display: grid; grid-template-columns: max-content 1fr; gap: 0.4em 1em; margin-bottom: var(--sp-3);">
        <strong>Type:</strong>           <code>${escapeHtml(df.drift_type)}</code>
        <strong>Guard policy:</strong>   <code>${escapeHtml(df.guard_policy || 'skip-on-drift')}</code>
        <strong>Affected TCs:</strong>   <span>${df.affected_tcs.map(t => `<code>${escapeHtml(t)}</code>`).join(', ')} <small style="color: var(--c-ink-3);">(${df.affected_tcs.length})</small></span>
        ${df.trigger_correlation ? `<strong>Correlation:</strong>    <code style="word-break: break-all;">${escapeHtml(df.trigger_correlation)}</code>` : ''}
        <strong>Notes:</strong>          <span>${escapeHtml(df.notes || '')}</span>
      </div>
      <div style="padding: var(--sp-2); background: var(--c-warn-bg, #fef3c7); border-left: 3px solid var(--c-warn, #f59e0b);">
        <strong>About this drift type:</strong> ${narrative}
      </div>
    `;
  } else {
    $('#results-drift').style.display = 'none';
  }

  // Provenance — grouped sections (F-09 from TES-GAP-ANALYSIS 2026-05-12 night).
  // Three groups: Schema · Host · Reporter. tool_versions rendered when present
  // (B-04 forward-compat).
  const tv = (env.host && env.host.tool_versions) || null;
  const tvLines = tv
    ? Object.entries(tv).map(([k, v]) => `${k}: ${v}`).join(' &middot; ')
    : '(not captured)';
  const parseWarnings = env.parse_warnings || [];   // B-08 forward-compat
  const warningsBlock = parseWarnings.length > 0
    ? `<div style="margin-top: 0.5em; padding: 0.5em; background: var(--c-warn-bg, #fef3c7); border-left: 3px solid var(--c-warn, #f59e0b);">
         <strong>Parse warnings (${parseWarnings.length}):</strong><br>
         ${parseWarnings.map(w => `<code style="display:block; font-size:.85em;">${escapeHtml(w)}</code>`).join('')}
       </div>`
    : '';
  $('#results-provenance').innerHTML = `
    <div class="prov-group">
      <strong>Schema</strong><br>
      version: <code>${env.schema_version}</code>
    </div>
    <div class="prov-group" style="margin-top: 0.6em;">
      <strong>Host</strong><br>
      <code>${env.host.os}</code> on <code>${env.host.host}</code><br>
      git: <code>${env.host.git_branch || '?'}</code> @ <code>${env.host.git_commit || '?'}</code><br>
      tools: <small>${tvLines}</small>
    </div>
    <div class="prov-group" style="margin-top: 0.6em;">
      <strong>Reporter</strong><br>
      command: <code>${escapeHtml(env.reporter.command)}</code><br>
      trigger: <code>${env.reporter.trigger}</code> &nbsp;
      operator: <code>${env.reporter.operator || '?'}</code>
      ${env.reporter.ci_run_id ? `<br>ci_run_id: <code>${escapeHtml(env.reporter.ci_run_id)}</code>` : ''}
    </div>
    ${warningsBlock}
  `;
}

function anyFailed(r) {
  return Object.values(r.verdicts).some(v => v === 'fail' || v === 'error');
}

// ──────────────────────────────────────────────────────────────────────────
// /bugs page
// ──────────────────────────────────────────────────────────────────────────
async function renderBugs() {
  renderTemplate('tpl-bugs');

  // Cache envs once for the form dropdown reuse
  let envCache = null;
  async function getEnvs() {
    if (!envCache) envCache = await api('/api/envs');
    return envCache;
  }

  async function load() {
    const status = $('#bugs-status').value;
    const severity = $('#bugs-severity').value;
    const qs = new URLSearchParams({
      ...(status && { status }),
      ...(severity && { severity }),
    });
    const rows = await api(`/api/bugs?${qs}`);
    const tbody = $('#bugs-table tbody');
    if (rows.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty">No bugs match the filter.</td></tr>';
      return;
    }
    // Bug rows are clickable — opens the edit form (v0.1.3 Block 2).
    tbody.innerHTML = rows.map(b => `
      <tr class="bug-row" style="cursor:pointer;" data-code="${escapeHtml(b.code)}" title="Click to edit / retest">
        <td><code>${escapeHtml(b.code)}</code></td>
        <td><span class="pill sev-${b.severity || 'X'}">${b.severity || '?'}</span></td>
        <td><span class="pill status-${b.status || 'open'}">${b.status || 'open'}</span></td>
        <td>${escapeHtml(b.name_en || b.name_cs || '')}</td>
        <td><code>${escapeHtml(b.env_where_present || '')}</code></td>
        <td>${b.linked_tc_ref ? `<code>${escapeHtml(b.linked_tc_ref)}</code>` : ''}</td>
      </tr>
    `).join('');
    // Wire row clicks → edit
    $$('.bug-row', tbody).forEach(row => {
      row.addEventListener('click', () => openEditForm(row.dataset.code));
    });
  }

  $('#bugs-status').addEventListener('change', load);
  $('#bugs-severity').addEventListener('change', load);
  $('#bugs-refresh').addEventListener('click', load);

  const form = $('#bug-form');

  // ── Open form in CREATE mode ─────────────────────────────────────────
  $('#bugs-new').addEventListener('click', async () => {
    form.style.display = '';
    form.dataset.mode = 'create';
    form.dataset.code = '';
    $('#bf-heading').textContent = '+ New Bug';
    $('#bf-submit').textContent = 'File bug';
    $('#bf-retest').style.display = 'none';
    // Reset all fields
    $('#bf-name').value = '';
    $('#bf-status').value = 'open';
    $('#bf-severity').value = 'B';
    $('#bf-urgency').value = 'B';
    $('#bf-priority').value = 'P3-medium';
    $('#bf-tc').value = '';
    $('#bf-repro').value = '';
    $('#bf-expected').value = '';
    $('#bf-actual').value = '';
    $('#bf-msg').textContent = '';
    // Prefill from sessionStorage if user came from a failed result row
    const prefill = sessionStorage.getItem('bug-prefill');
    if (prefill) {
      const p = JSON.parse(prefill);
      $('#bf-tc').value = p.tc || '';
      if (p.error) $('#bf-actual').value = p.error;
      sessionStorage.removeItem('bug-prefill');
    }
    const envs = await getEnvs();
    $('#bf-env').innerHTML = envs.map(e =>
      `<option value="${e.code}">${e.code} — ${e.name_en}</option>`
    ).join('');
  });

  // ── Open form in EDIT mode (called when bug row is clicked) ───────────
  async function openEditForm(code) {
    form.style.display = '';
    form.dataset.mode = 'edit';
    form.dataset.code = code;
    $('#bf-heading').innerHTML = `Edit bug <code>${escapeHtml(code)}</code>`;
    $('#bf-submit').textContent = 'Save changes';
    $('#bf-msg').textContent = 'loading…';
    try {
      const bug = await api(`/api/bugs/${encodeURIComponent(code)}`);
      const envs = await getEnvs();
      $('#bf-env').innerHTML = envs.map(e =>
        `<option value="${e.code}" ${e.code === bug.env_where_present ? 'selected' : ''}>${e.code} — ${e.name_en}</option>`
      ).join('');
      $('#bf-name').value = bug.name_en || bug.name_cs || '';
      $('#bf-status').value = bug.status || 'open';
      $('#bf-severity').value = bug.severity || 'B';
      $('#bf-urgency').value = bug.urgency || 'B';
      $('#bf-priority').value = bug.priority || 'P3-medium';
      $('#bf-tc').value = bug.linked_tc_ref || '';
      $('#bf-repro').value = bug.repro_steps || '';
      $('#bf-expected').value = bug.expected || '';
      $('#bf-actual').value = bug.actual || '';
      $('#bf-msg').textContent = '';
      // Show retest button if there's a linked TC and status is anywhere
      // workflow-relevant (open / investigating / fixed / reopened).
      const retestable = bug.linked_tc_ref &&
        ['open', 'investigating', 'fixed', 'reopened'].includes(bug.status || 'open');
      $('#bf-retest').style.display = retestable ? '' : 'none';
      $('#bf-retest').dataset.code = code;
      $('#bf-retest').dataset.tc = bug.linked_tc_ref || '';
    } catch (e) {
      $('#bf-msg').innerHTML = `<span class="pill verdict-fail">${escapeHtml(e.message)}</span>`;
    }
  }

  $('#bf-cancel').addEventListener('click', () => {
    form.style.display = 'none';
    $('#bf-msg').textContent = '';
  });

  // ── Submit (create or update depending on mode) ───────────────────────
  $('#bf-submit').addEventListener('click', async () => {
    const body = {
      name_en: $('#bf-name').value,
      status: $('#bf-status').value,
      severity: $('#bf-severity').value,
      urgency: $('#bf-urgency').value,
      priority: $('#bf-priority').value,
      env_where_present: $('#bf-env').value,
      linked_tc_ref: $('#bf-tc').value || null,
      repro_steps: $('#bf-repro').value,
      expected: $('#bf-expected').value,
      actual: $('#bf-actual').value,
    };
    if (!body.name_en) {
      $('#bf-msg').innerHTML = '<span class="pill verdict-fail">title required</span>';
      return;
    }
    const mode = form.dataset.mode || 'create';
    const code = form.dataset.code || '';
    try {
      if (mode === 'edit') {
        await api(`/api/bugs/${encodeURIComponent(code)}`,
                  { method: 'PUT', body: JSON.stringify(body) });
        $('#bf-msg').innerHTML = `<span class="pill verdict-pass">updated: ${escapeHtml(code)}</span>`;
      } else {
        const resp = await api('/api/bugs',
                               { method: 'POST', body: JSON.stringify(body) });
        $('#bf-msg').innerHTML = `<span class="pill verdict-pass">filed: ${escapeHtml(resp.code)}</span>`;
      }
      setTimeout(() => { form.style.display = 'none'; $('#bf-msg').textContent = ''; load(); }, 1200);
    } catch (e) {
      $('#bf-msg').innerHTML = `<span class="pill verdict-fail">${escapeHtml(e.message)}</span>`;
    }
  });

  // ── Retest workflow (conservative — operator confirms status change) ──
  $('#bf-retest').addEventListener('click', async () => {
    const code = $('#bf-retest').dataset.code;
    const tc = $('#bf-retest').dataset.tc;
    if (!code || !tc) return;
    $('#bf-msg').innerHTML = `<span class="pill verdict-skip-other">launching retest…</span>`;
    try {
      const resp = await api(`/api/bugs/${encodeURIComponent(code)}/retest`,
                             { method: 'POST', body: '{}' });
      $('#bf-msg').innerHTML =
        `<span class="pill verdict-pass">retest launched: <code>${escapeHtml(resp.run_id)}</code></span>`;
      // Poll the run; on completion, show the retest-result banner.
      _watchRetest(code, tc, resp.run_id);
    } catch (e) {
      $('#bf-msg').innerHTML = `<span class="pill verdict-fail">${escapeHtml(e.message)}</span>`;
    }
  });

  function _watchRetest(bugCode, tcCode, runId) {
    const banner = $('#retest-result-banner');
    banner.style.display = '';
    $('#rr-heading').innerHTML =
      `Retest in progress for <code>${escapeHtml(bugCode)}</code> (TC: <code>${escapeHtml(tcCode)}</code>)`;
    $('#rr-body').innerHTML = `Run <code>${escapeHtml(runId)}</code> dispatched. Watching for completion…`;
    $('#rr-verify').style.display = 'none';
    $('#rr-reopen').style.display = 'none';
    $('#rr-run-link').href = `#/results/${runId}`;

    let attempts = 0;
    const maxAttempts = 90;   // 90 * 2s = 3 min
    const poll = setInterval(async () => {
      attempts++;
      try {
        const env = await api(`/api/runs/${encodeURIComponent(runId)}`);
        // The full envelope has `results[]` once consolidation finishes.
        if (env && env.results && Array.isArray(env.results)) {
          clearInterval(poll);
          _renderRetestResult(bugCode, tcCode, runId, env);
        }
      } catch (_) { /* keep polling */ }
      if (attempts >= maxAttempts) {
        clearInterval(poll);
        $('#rr-body').innerHTML =
          `Retest did not complete within 3 minutes. <a href="#/results/${runId}">Check the run page</a> for status.`;
      }
    }, 2000);
  }

  function _renderRetestResult(bugCode, tcCode, runId, env) {
    const r = (env.results || []).find(x => x.tc_code === tcCode);
    if (!r) {
      $('#rr-body').innerHTML =
        `Run completed but the TC <code>${escapeHtml(tcCode)}</code> was not found in the result set. <a href="#/results/${runId}">View run</a>.`;
      return;
    }
    const verdicts = Object.values(r.verdicts || {}).filter(v => v !== 'missing');
    const allPass = verdicts.length > 0 && verdicts.every(v => v === 'pass' || v === 'soft-pass');
    const anyFail = verdicts.some(v => v === 'fail' || v === 'error');
    let summary = '';
    if (allPass) {
      summary = `<span class="pill verdict-pass">retest PASSED</span> — the TC now passes across ${verdicts.length} framework(s).`;
    } else if (anyFail) {
      summary = `<span class="pill verdict-fail">retest FAILED</span> — the TC still fails. Verdicts: ${verdicts.join(', ')}.`;
    } else {
      summary = `<span class="pill verdict-skip-drift">retest SKIPPED</span> — TC was skipped (drift?). Verdicts: ${verdicts.join(', ')}.`;
    }
    $('#rr-heading').innerHTML =
      `Retest result for <code>${escapeHtml(bugCode)}</code>`;
    $('#rr-body').innerHTML = `
      ${summary}<br>
      <small style="color: var(--c-ink-3);">Per conservative-retest policy you confirm the status change manually.</small>
    `;
    // Conservative: show whichever confirmation matches the verdict
    if (allPass) $('#rr-verify').style.display = '';
    if (anyFail) $('#rr-reopen').style.display = '';
  }

  $('#rr-verify').addEventListener('click', async () => {
    const code = form.dataset.code;
    if (!code) return;
    try {
      await api(`/api/bugs/${encodeURIComponent(code)}`,
                { method: 'PUT', body: JSON.stringify({ status: 'verified-fixed' }) });
      $('#retest-result-banner').style.display = 'none';
      load();
    } catch (e) {
      $('#rr-body').insertAdjacentHTML('beforeend',
        `<br><span class="pill verdict-fail">status flip failed: ${escapeHtml(e.message)}</span>`);
    }
  });

  $('#rr-reopen').addEventListener('click', async () => {
    const code = form.dataset.code;
    if (!code) return;
    try {
      await api(`/api/bugs/${encodeURIComponent(code)}`,
                { method: 'PUT', body: JSON.stringify({ status: 'reopened' }) });
      $('#retest-result-banner').style.display = 'none';
      load();
    } catch (e) {
      $('#rr-body').insertAdjacentHTML('beforeend',
        `<br><span class="pill verdict-fail">status flip failed: ${escapeHtml(e.message)}</span>`);
    }
  });

  $('#rr-keep').addEventListener('click', () => {
    $('#retest-result-banner').style.display = 'none';
  });

  load();
}

// ──────────────────────────────────────────────────────────────────────────
// /about page
// ──────────────────────────────────────────────────────────────────────────
async function renderAbout() {
  renderTemplate('tpl-about');
  try {
    const h = await api('/api/health');
    $('#health-status').innerHTML = `
      schema_version: <code>${h.schema_version}</code><br>
      server_version: <code>${h.server_version}</code><br>
      workbook: <code>${h.workbook_path}</code> ${h.workbook_exists ? '<span class="pill verdict-pass">found</span>' : '<span class="pill verdict-fail">missing</span>'}<br>
      runs_dir:  <code>${h.runs_dir}</code> ${h.runs_dir_exists ? '<span class="pill verdict-pass">ok</span>' : '<span class="pill verdict-skip-drift">empty</span>'}<br>
      tools:
        npx ${h.tools.npx ? '<span class="pill verdict-pass">ok</span>' : '<span class="pill verdict-fail">missing</span>'}
        python ${h.tools.python ? '<span class="pill verdict-pass">ok</span>' : '<span class="pill verdict-fail">missing</span>'}
        consolidator ${h.tools.consolidate_results ? '<span class="pill verdict-pass">ok</span>' : '<span class="pill verdict-fail">missing</span>'}
    `;
  } catch (e) {
    $('#health-status').innerHTML = `<span class="pill verdict-fail">/api/health unreachable</span>`;
  }
}
