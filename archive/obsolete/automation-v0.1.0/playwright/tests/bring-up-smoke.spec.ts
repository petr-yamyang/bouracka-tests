/**
 * BRING-UP-SMOKE — public bouracka.cz landing → /formular → CTA visible
 *
 * Purpose: validate the install + framework + tester pipeline (NOT the SUT).
 * Runs against PUBLIC bouracka.cz so it's reachable from any laptop —
 * no SUPIN intranet, no test creds, no integration mocks needed.
 *
 * If this test goes red on a fresh laptop:
 *   - failure is in the environment (Node missing, Playwright not
 *     installed, browser binary not downloaded, corp-proxy CA not
 *     configured, firewall blocking www.bouracka.cz);
 *   - it is NOT a bouracka.cz regression.
 *
 * If this test goes green:
 *   - the kit is alive; CP-SUPIN-03 R1 work can begin.
 *
 * R-CAST-2 — every step typed (control_point | trigger_point |
 *   data_collection_point | assertion).
 *
 * Mobile-only viewport per AMENDMENT 2 + analytical doc §3.2 binding.
 */
import { test, expect } from "@playwright/test";

// AMENDMENT 2 mobile-only — bring-up runs at 375×667 (median mobile).
test.use({
  viewport: { width: 375, height: 667 },
  locale: "cs-CZ",
  timezoneId: "Europe/Prague",
});

test.describe("BRING-UP-SMOKE — pipeline alive against public bouracka.cz", () => {
  test("Open landing → click VYPLNIT ZÁZNAM → reach /formular gateway", async ({ page }, testInfo) => {
    // STEP 1 — trigger_point: navigate to public landing
    await page.goto("https://www.bouracka.cz/", { waitUntil: "domcontentloaded" });

    // STEP 2 — assertion: page title contains 'Bouračka'
    await expect(page).toHaveTitle(/Bouračka/);

    // STEP 3 — data_collection_point: locate the primary CTA
    const cta = page
      .getByRole("button", { name: /VYPLNIT ZÁZNAM/i })
      .or(page.getByRole("link", { name: /VYPLNIT ZÁZNAM/i }))
      .first();

    // STEP 4 — assertion: CTA visible
    await expect(cta).toBeVisible({ timeout: 10_000 });

    // STEP 5 — assertion: mobile-only — touch target ≥ 44×44 px (WCAG 2.2 AA)
    const box = await cta.boundingBox();
    expect(box, "CTA bounding box must exist").not.toBeNull();
    if (box) {
      expect(box.width, `CTA width ${box.width} px < 44`).toBeGreaterThanOrEqual(44);
      expect(box.height, `CTA height ${box.height} px < 44`).toBeGreaterThanOrEqual(44);
    }

    // STEP 6 — trigger_point: click CTA
    await cta.click();

    // STEP 7 — control_point: branch on URL — /formular or /formular?utm…
    await expect(page).toHaveURL(/\/formular(\?.*)?$/, { timeout: 10_000 });

    // STEP 8 — data_collection_point: capture gateway H1
    const gatewayH1 = page.locator("h1").first();

    // STEP 9 — assertion: gateway H1 references "dopravní nehoda"
    await expect(gatewayH1).toBeVisible();
    const h1text = await gatewayH1.innerText();
    expect(h1text).toMatch(/dopravní nehoda/i);

    // STEP 10 — assertion: reCAPTCHA badge attached (verifies the SUT
    //          loaded its bot-defence script — proxy + JS pipeline OK)
    await expect(
      page.locator(".grecaptcha-badge, [data-recaptcha]")
    ).toBeAttached({ timeout: 15_000 });

    // STEP 11 — data_collection_point: write a tiny breadcrumb so the
    //          Excel reporter (when wired in CP-SUPIN-03) can pick it up
    await testInfo.attach("bring-up-breadcrumb.json", {
      body: JSON.stringify(
        {
          test: "BRING-UP-SMOKE",
          when: new Date().toISOString(),
          host: "www.bouracka.cz",
          viewport: { width: 375, height: 667 },
          gateway_h1: h1text,
          status: "green",
        },
        null,
        2
      ),
      contentType: "application/json",
    });
  });
});
