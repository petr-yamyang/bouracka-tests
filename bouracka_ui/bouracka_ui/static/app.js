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

  // Verdict matrix
  const fws = env.frameworks;
  $('#results-matrix thead').innerHTML = `<tr>
    <th>TC</th>
    ${fws.map(f => `<th>${f}</th>`).join('')}
    <th>Parity</th>
    <th>File bug</th>
  </tr>`;
  $('#results-matrix tbody').innerHTML = env.results.map(r => `
    <tr>
      <td><code>${r.tc_code}</code></td>
      ${fws.map(f => {
        const v = r.verdicts[f] || 'missing';
        return `<td><span class="pill verdict-${v}">${v}</span></td>`;
      }).join('')}
      <td><span class="pill parity-${r.parity_status}">${r.parity_status}</span></td>
      <td>${anyFailed(r) ? `<a href="#/bugs?tc=${r.tc_code}&run=${env.run_id}" onclick="sessionStorage.setItem('bug-prefill', JSON.stringify({tc:'${r.tc_code}',run:'${env.run_id}',env:'${env.env}'}))">+ bug</a>` : ''}</td>
    </tr>
  `).join('');

  // Drift forensic
  if (env.drift_forensic && env.drift_forensic.active) {
    $('#results-drift').style.display = '';
    const df = env.drift_forensic;
    $('#results-drift-body').innerHTML = `
      <p><strong>Type:</strong> <code>${df.drift_type}</code></p>
      <p><strong>Affected TCs:</strong> ${df.affected_tcs.map(t => `<code>${t}</code>`).join(', ')}</p>
      <p><strong>Notes:</strong> ${df.notes || ''}</p>
      ${df.trigger_correlation ? `<p><strong>Correlation:</strong> <code>${df.trigger_correlation}</code></p>` : ''}
    `;
  }

  // Provenance
  $('#results-provenance').innerHTML = `
    schema_version: ${env.schema_version}<br>
    host: ${env.host.os} on ${env.host.host}<br>
    git: ${env.host.git_branch || '?'} @ ${env.host.git_commit || '?'}<br>
    reporter: ${env.reporter.command}<br>
    trigger: ${env.reporter.trigger}<br>
    operator: ${env.reporter.operator || '?'}
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
    tbody.innerHTML = rows.map(b => `
      <tr>
        <td><code>${b.code}</code></td>
        <td><span class="pill sev-${b.severity || 'X'}">${b.severity || '?'}</span></td>
        <td><span class="pill status-${b.status || 'open'}">${b.status || 'open'}</span></td>
        <td>${b.name_en || b.name_cs || ''}</td>
        <td><code>${b.env_where_present || ''}</code></td>
        <td>${b.linked_tc_ref ? `<code>${b.linked_tc_ref}</code>` : ''}</td>
      </tr>
    `).join('');
  }

  $('#bugs-status').addEventListener('change', load);
  $('#bugs-severity').addEventListener('change', load);
  $('#bugs-refresh').addEventListener('click', load);

  // New bug form
  const form = $('#bug-form');
  $('#bugs-new').addEventListener('click', async () => {
    form.style.display = '';
    // Pre-fill from sessionStorage if user came from a failed result row
    const prefill = sessionStorage.getItem('bug-prefill');
    if (prefill) {
      const p = JSON.parse(prefill);
      $('#bf-tc').value = p.tc || '';
      sessionStorage.removeItem('bug-prefill');
    }
    // Populate env dropdown
    const envs = await api('/api/envs');
    $('#bf-env').innerHTML = envs.map(e =>
      `<option value="${e.code}">${e.code} — ${e.name_en}</option>`
    ).join('');
  });
  $('#bf-cancel').addEventListener('click', () => { form.style.display = 'none'; $('#bf-msg').textContent = ''; });

  $('#bf-submit').addEventListener('click', async () => {
    const body = {
      name_en: $('#bf-name').value,
      severity: $('#bf-severity').value,
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
    try {
      const resp = await api('/api/bugs', { method: 'POST', body: JSON.stringify(body) });
      $('#bf-msg').innerHTML = `<span class="pill verdict-pass">filed: ${resp.code}</span>`;
      setTimeout(() => { form.style.display = 'none'; $('#bf-msg').textContent = ''; load(); }, 1200);
    } catch (e) {
      $('#bf-msg').innerHTML = `<span class="pill verdict-fail">${e.message}</span>`;
    }
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
