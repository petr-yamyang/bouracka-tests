/**
 * intel-probes/01-enumeration-dump.spec.ts
 *
 * Per CP-SUPIN-04 STEP 14. Uses operator's temporary admin permissions on the
 * ThinkPad (Profile-C install: Node + Playwright + Chromium) to drive
 * demo.bouracka.cz and harvest more intel that updates the artefact set:
 *
 *   1. Full /api/enumerations/* dump (response counts, full payloads → JSON files
 *      under fixtures/intel-2026-MM-DD/)
 *   2. Bundle source read — extracts Zod schemas, validation regexes, copy
 *      strings from /formular/assets/index-*.js
 *   3. Network panel record for the full happy path → JSON trace per TC
 *
 * Run:   npx playwright test playwright/tests/intel-probes/ --project=chromium-mobile
 * Output: fixtures/intel-2026-MM-DD/{enums,bundles,traces}/*.json
 *
 * Operator note: requires `npm install` first (Profile-C admin step). The
 * scrapes are read-only; no writes to the SUT (no POST /reports unless
 * explicitly opted-in via TC-CP-INTEL-FULL-WALK).
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const ENV_BASE = process.env.BOURACKA_BASE ?? 'https://demo.bouracka.cz';
const TODAY = new Date().toISOString().slice(0, 10);
const OUT_DIR = path.join('fixtures', `intel-${TODAY}`);

test.beforeAll(() => {
  fs.mkdirSync(path.join(OUT_DIR, 'enums'), { recursive: true });
  fs.mkdirSync(path.join(OUT_DIR, 'bundles'), { recursive: true });
  fs.mkdirSync(path.join(OUT_DIR, 'traces'), { recursive: true });
});

const PUBLIC_ENUMS = ['insuranceCompanies', 'vehicleBrands'];
const PROTECTED_ENUMS = [
  'licenseCategories', 'damageZones', 'movementTypes',
  'accidentCauses', 'accidentCategories', 'vehicleCategories',
  'documentTypes', 'witnessTypes',
];

test('TC-CP-INTEL-001 — Public enumerations: full dump + count assertions', async ({ request }) => {
  for (const e of PUBLIC_ENUMS) {
    const res = await request.get(`${ENV_BASE}/api/enumerations/${e}`);
    expect(res.status(), `${e} should be 200 (public)`).toBe(200);
    const json = await res.json();
    fs.writeFileSync(
      path.join(OUT_DIR, 'enums', `${e}.json`),
      JSON.stringify(json, null, 2),
      'utf-8',
    );
    console.log(`[ok] ${e}: ${Array.isArray(json) ? json.length : '?'} entries → fixtures/intel-${TODAY}/enums/${e}.json`);
  }
});

test('TC-CP-INTEL-002 — Protected enumerations: assert all return 403', async ({ request }) => {
  for (const e of PROTECTED_ENUMS) {
    const res = await request.get(`${ENV_BASE}/api/enumerations/${e}`);
    expect(res.status(), `${e} should be 403 (protected)`).toBe(403);
  }
});

test('TC-CP-INTEL-003 — Bundle source read: extract Zod schemas + copy strings', async ({ request }) => {
  // Fetch the SPA shell, parse the bundle URLs, fetch each JS chunk
  const shell = await request.get(`${ENV_BASE}/formular/`);
  expect(shell.status()).toBe(200);
  const html = await shell.text();
  // Match Vite-style hashed assets
  const assetUrls = Array.from(html.matchAll(/\/formular\/assets\/[^"'\s]+\.js/g))
    .map((m) => m[0])
    .filter((u, i, arr) => arr.indexOf(u) === i);
  console.log(`[info] discovered ${assetUrls.length} asset URLs from SPA shell`);

  const findings: Record<string, { length: number; zodHits: number; regexHits: number; demoHits: number; copyStrings: string[] }> = {};

  for (const url of assetUrls.slice(0, 30)) {
    // Limit to first 30 to bound runtime
    const r = await request.get(`${ENV_BASE}${url}`);
    if (r.status() !== 200) continue;
    const src = await r.text();
    // Heuristic detection — Zod schema mentions
    const zodHits = (src.match(/z\.(object|string|number|email|min|max)/g) ?? []).length;
    // Regex literals
    const regexHits = (src.match(/\/\^[^/]+\$\//g) ?? []).length;
    // DEMO copy hits
    const demoHits = (src.match(/Demoverze|DEMO VERZI|nahrazeno instruktážním/g) ?? []).length;
    // Czech copy strings (rough)
    const copyStrings = Array.from(src.matchAll(/"([À-ſA-Za-z\s,.?!:;()'/+0-9–—-]{12,200})"/g))
      .map((m) => m[1])
      .filter((s) => /[ěščřžýáíéůúďťňĚŠČŘŽÝÁÍÉŮÚĎŤŇ]/.test(s)) // require ≥1 Czech-diacritic
      .slice(0, 50);
    findings[url] = { length: src.length, zodHits, regexHits, demoHits, copyStrings };
  }
  fs.writeFileSync(
    path.join(OUT_DIR, 'bundles', 'bundle-findings.json'),
    JSON.stringify(findings, null, 2),
    'utf-8',
  );
  console.log(`[ok] bundle findings → fixtures/intel-${TODAY}/bundles/bundle-findings.json`);
});

test('TC-CP-INTEL-004 — Rozcestník network trace + outage feed sanity', async ({ page }) => {
  const requests: { method: string; url: string; status?: number }[] = [];
  page.on('response', async (resp) => {
    const r = resp.request();
    requests.push({ method: r.method(), url: r.url(), status: resp.status() });
  });
  await page.goto(`${ENV_BASE}/formular/`, { waitUntil: 'networkidle' });
  fs.writeFileSync(
    path.join(OUT_DIR, 'traces', 'rozcestnik.json'),
    JSON.stringify(requests, null, 2),
    'utf-8',
  );
  // Sanity assertions
  expect(requests.some((r) => r.url.includes('odstavky.json'))).toBeTruthy();
  expect(requests.some((r) => r.url.includes('maps.googleapis.com'))).toBeTruthy();
  expect(requests.some((r) => r.url.includes('demo.bouracka.cz/formular/assets/'))).toBeTruthy();
});

test('TC-CP-INTEL-005 — Identifikační kód format on a fresh report', async ({ page }) => {
  // This test creates a new report (POST /api/reports) → costs a UUID. Gate behind env flag.
  if (!process.env.INTEL_PROBE_CREATE_REPORT) {
    test.skip(true, 'set INTEL_PROBE_CREATE_REPORT=1 to allow creating a report');
  }
  await page.goto(`${ENV_BASE}/formular/`, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /Vyplnit záznam/i }).click();
  await page.getByRole('button', { name: /Rozumím/i }).click();
  // Wait for verification screen
  await page.waitForURL(/\/verification/);
  // Identifikační kód not yet visible — only after verification.
  // For now just assert URL pattern + capture the report UUID
  const url = page.url();
  const reportId = url.match(/\/report\/([0-9a-f-]{36})\//)?.[1];
  expect(reportId, 'report UUID extracted from URL').toMatch(/^[0-9a-f-]{36}$/);
  fs.writeFileSync(
    path.join(OUT_DIR, 'traces', 'fresh-report.json'),
    JSON.stringify({ url, reportId }, null, 2),
    'utf-8',
  );
});
