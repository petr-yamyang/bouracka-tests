/**
 * BRING-UP-SMOKE — pipeline alive against DEMO Bouracka rozcestník
 *
 * Per CP-SUPIN-04. Targets demo.bouracka.cz/formular/ directly — the
 * rozcestnik (gateway) where VYPLNIT ZÁZNAM CTA is rendered.
 *
 * Earlier v0.3 version targeted www.bouracka.cz/ (marketing landing),
 * which on mobile hides the CTA behind a hamburger menu, causing
 * boundingBox() timeouts.
 *
 * GREEN  → kit alive; CP-SUPIN-04 work can proceed.
 * RED    → environment problem (proxy / firewall / browser binary).
 *
 * Override target via BOURACKA_BASE env var:
 *   $env:BOURACKA_BASE = "https://tst.demo.bouracka.cz"   # firewall twin
 *   $env:BOURACKA_BASE = "https://bouracka.cz"            # PROD (different rozcestník UX)
 */
import { test, expect } from "@playwright/test";
import { dismissCookieBanner } from "../helpers/page-helpers";

const BASE = process.env.BOURACKA_BASE ?? "https://demo.bouracka.cz";

test.use({
  viewport: { width: 375, height: 667 },
  locale: "cs-CZ",
  timezoneId: "Europe/Prague",
});

test.describe("BRING-UP-SMOKE — pipeline alive against DEMO Bouracka", () => {
  test("Open /formular/ rozcestnik → CTA visible + clickable → navigate to /informations", async ({ page }, testInfo) => {
    // STEP 1 — navigate directly to rozcestnik
    await page.goto(`${BASE}/formular/`, { waitUntil: "domcontentloaded" });

    // STEP 1b — dismiss cookie banner (privacy-default: REJECT ALL)
    await dismissCookieBanner(page);

    // STEP 2 — title sanity
    await expect(page).toHaveTitle(/Bouračka/);

    // STEP 3 — page identity heading (key copy that anchors R1 scope)
    await expect(
      page.getByRole("heading", { name: /Stala se vám dopravní nehoda/i })
    ).toBeVisible();

    // STEP 4 — locate primary CTA
    const cta = page
      .getByRole("button", { name: /vyplnit záznam/i })
      .or(page.getByRole("link", { name: /vyplnit záznam/i }))
      .first();
    await expect(cta).toBeVisible({ timeout: 10_000 });

    // STEP 5 — WCAG 2.2 AA touch target ≥ 44×44 px (mobile-only viewport)
    const box = await cta.boundingBox();
    expect(box, "CTA bounding box must exist").not.toBeNull();
    if (box) {
      expect(box.width,  `CTA width ${box.width} px < 44`).toBeGreaterThanOrEqual(44);
      expect(box.height, `CTA height ${box.height} px < 44`).toBeGreaterThanOrEqual(44);
    }

    // STEP 6 — click CTA
    await cta.click();

    // STEP 7 — SPA navigates to /formular/informations (intro) on DEMO
    await expect(page).toHaveURL(/\/formular\/informations\/?$/, { timeout: 15_000 });

    // STEP 8 — intro screen heading is visible
    await expect(page.getByRole("heading", { name: /Co vás čeká/i })).toBeVisible();

    // STEP 9 — breadcrumb (for Excel reporter wired in CP-SUPIN-05)
    await testInfo.attach("bring-up-breadcrumb.json", {
      body: JSON.stringify(
        {
          test: "BRING-UP-SMOKE",
          when: new Date().toISOString(),
          host: BASE,
          viewport: { width: 375, height: 667 },
          status: "green",
        },
        null,
        2
      ),
      contentType: "application/json",
    });
  });
});
