/**
 * TC-CP-001 + TC-CP-002 — wizard-entry smoke (re-scoped per OQ-CP-12).
 *
 * Filename retains "login" for traceability with CLIENT-PILOT-SUPIN §4.1
 * placeholders; actual scope per recon is "wizard-entry happy" + "police-call
 * branch failure". Both pair under R-FAIL-1.
 *
 * R-CAST-2 — every step labelled with kind in inline comments:
 *   trigger_point | data_collection_point | control_point | assertion
 *
 * AMENDMENT 2 mobile-first — viewport projects in playwright.config.ts
 * cover desktop + 320/375/414 px. Each test below runs once per project.
 */
import { test, expect } from "@playwright/test";
import { LandingPage } from "../pages/LandingPage";
import { WizardGatewayPage } from "../pages/WizardGatewayPage";

test.describe("TC-CP-001 — Vstup do formuláře — happy", () => {
  test("Open landing → click VYPLNIT ZÁZNAM → reach gateway", async ({ page }, testInfo) => {
    const landing = new LandingPage(page);
    const gateway = new WizardGatewayPage(page);

    // STEP 1 — trigger_point: navigate to landing
    await landing.open("/");

    // STEP 2 — assertion: page title carries Bouračka
    await landing.expectTitleMatches(/Bouračka/);

    // STEP 3 — data_collection_point: locate primary CTA
    const cta = landing.primaryCTA();

    // STEP 4 — assertion: CTA visible + href into /formular
    await expect(cta).toBeVisible();
    // CTA may itself be a <button> wrapped in <a>; assert the ancestor anchor's href
    const anchorHref = await cta.evaluate((el) => {
      const anchor = el.closest("a");
      return anchor?.getAttribute("href") ?? "";
    });
    expect(anchorHref).toMatch(/\/formular/);

    // STEP 5 — assertion: mobile-only — touch-target ≥ 44×44
    if (testInfo.project.name.includes("mobile")) {
      await landing.expectTouchTargetAtLeast(cta);
    }

    // STEP 6 — trigger_point: click CTA
    await cta.click();

    // STEP 7 — control_point: branch on URL — accept either /formular or /formular?...
    await expect(page).toHaveURL(/\/formular(\?.*)?$/);

    // STEP 8 — data_collection_point: capture gateway H1
    const gatewayH1Text = await gateway.gatewayH1().innerText();

    // STEP 9 — assertion: gateway H1 + primary CTA + reCAPTCHA badge
    expect(gatewayH1Text).toMatch(/dopravní nehoda/i);
    await expect(gateway.vyplnitZaznamButton()).toBeVisible();
    // reCAPTCHA badge is loaded async — give it a moment
    await expect(gateway.recaptchaBadge()).toBeAttached({ timeout: 15_000 });
  });
});

test.describe("TC-CP-002 — Vstup do formuláře — větvení Policie ČR (failure pair)", () => {
  test("Police-call interlock — 7 conditions + tel:158 + wizard does NOT advance", async ({ page }) => {
    const gateway = new WizardGatewayPage(page);

    // STEP 1 — trigger_point: navigate directly to /formular
    await gateway.open("/formular");

    // STEP 2 — data_collection_point: locate the police-call card heading
    const heading = gateway.policeCallCardHeading();
    await expect(heading).toBeVisible();

    // STEP 3 — trigger_point: expand the police-call panel
    await gateway.openPoliceCallPanel();

    // STEP 4 — assertion: exactly 7 hard-stop conditions listed
    await gateway.expectSevenPoliceConditions();

    // STEP 5 — control_point: branch on test variant (happy = call police)
    //   This test exercises the happy variant only; the alternative branch
    //   (user clicks "Vyplnit záznam o nehodě" inside the panel) is the
    //   F1 failure mode in FLW-002 — covered in a separate spec when DEMO
    //   relaxation rules land.

    // STEP 6 — assertion: tel:158 link present and well-formed
    await gateway.expectPoliceLinkOk();

    // STEP 7 — data_collection_point: capture URL to confirm non-advance
    const urlNow = page.url();

    // STEP 8 — assertion: URL still /formular — wizard did NOT advance
    expect(urlNow).toMatch(/\/formular(\?.*)?$/);
    await gateway.expectStillOnGateway();
  });
});
