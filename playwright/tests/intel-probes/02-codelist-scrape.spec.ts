/**
 * intel-probes/02-codelist-scrape.spec.ts
 *
 * Per CP-SUPIN-04 STEP 14. The protected enumerations (8× 403) are loaded
 * by the SPA itself and rendered into MUI Autocomplete dropdowns. This
 * probe drives the wizard to surface each dropdown, scrapes the option
 * list via DOM, and writes the codelist values to fixtures.
 *
 * Output: fixtures/intel-2026-MM-DD/codelists-from-dom/*.json
 *
 * Operator note: this DOES create a report (POST /api/reports).
 * Set INTEL_PROBE_CREATE_REPORT=1 to enable.
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const ENV_BASE = process.env.BOURACKA_BASE ?? 'https://demo.bouracka.cz';
const TODAY = new Date().toISOString().slice(0, 10);
const OUT_DIR = path.join('fixtures', `intel-${TODAY}`, 'codelists-from-dom');

test.skip(
  !process.env.INTEL_PROBE_CREATE_REPORT,
  'set INTEL_PROBE_CREATE_REPORT=1 to enable scrape (creates a report)',
);

test.beforeAll(() => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
});

async function scrapeListbox(page: any, label: string): Promise<string[]> {
  const opts = await page.locator('[role="listbox"] [role="option"]').allTextContents();
  fs.writeFileSync(
    path.join(OUT_DIR, `${label}.json`),
    JSON.stringify(opts.map((s: string) => s.trim()), null, 2),
    'utf-8',
  );
  return opts;
}

test('TC-CP-INTEL-006 — License categories codelist (DOM scrape)', async ({ page }) => {
  await page.goto(`${ENV_BASE}/formular/`);
  await page.getByRole('button', { name: /Vyplnit záznam/i }).click();
  await page.getByRole('button', { name: /Rozumím/i }).click();
  // Phase 1 form for A — fill phone, submit, OTP, submit
  await page.locator('input[type="tel"]').first().fill('608000001');
  await page.getByRole('checkbox').first().check();
  await page.getByRole('button', { name: /Odeslat kód/i }).click();
  // OTP — DEMO accepts any 4-digit
  const otpInputs = await page.locator('input[type="tel"]').all();
  for (let i = 0; i < otpInputs.length; i++) {
    await otpInputs[i].fill(String((i + 1) % 10));
  }
  await page.getByRole('button', { name: /Ověřit/i }).click();
  // Now form for B
  await page.locator('input[type="tel"]').first().fill('608000002');
  await page.getByRole('button', { name: /Odeslat kód/i }).click();
  for (let i = 0; i < 4; i++) {
    await page.locator('input[type="tel"]').nth(i).fill(String((i + 5) % 10));
  }
  await page.getByRole('button', { name: /Ověřit/i }).click();
  // Verification success → click Přejít
  await page.getByRole('button', { name: /Přejít na informace/i }).click();
  // Phase 2 — click Vyplnit údaje ručně
  await page.getByRole('button', { name: /Vyplnit údaje ručně/i }).click();
  // Open the license-categories combobox
  await page.locator('[aria-label*="Skupiny řidičských oprávnění"], input[role="combobox"]')
    .last()
    .click();
  // Wait for listbox + scrape
  await page.waitForSelector('[role="listbox"] [role="option"]');
  const opts = await scrapeListbox(page, 'license-categories');
  expect(opts.length).toBeGreaterThanOrEqual(15);
  console.log(`[ok] license categories: ${opts.length} entries`);
});

test('TC-CP-INTEL-007 — Movement codelist (DOM scrape, requires deeper walk)', async ({ page }) => {
  // Alternative: use deep-link if the report has been provisioned
  test.skip(true, 'requires Phase 3 reach; implement after Phase 2 happy path is parametrised');
});

test('TC-CP-INTEL-008 — Damage zones codelist (DOM scrape)', async ({ page }) => {
  test.skip(true, 'requires Phase 3 reach; implement after Phase 2 happy path is parametrised');
});

test('TC-CP-INTEL-009 — Accident-type codelist (DOM scrape)', async ({ page }) => {
  test.skip(true, 'requires shared circumstances reach');
});
