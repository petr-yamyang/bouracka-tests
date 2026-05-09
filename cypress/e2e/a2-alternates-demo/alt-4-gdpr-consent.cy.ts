/**
 * TC-CP-A2-ALT-4 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-4 block, line ~118).
 *
 * Test: Phase 1 GDPR consent required for participant A.
 *   - Navigate to /verification (drift-skip guard active)
 *   - Fill phone "608400004" for participant A
 *   - Intentionally do NOT check the GDPR checkbox
 *   - Intercept any PUT /api/**reporter** calls before clicking Odeslat kód
 *   - Click "Odeslat kód"
 *   - Wait 2s
 *   - Assert no PUT /reporter call was fired (form blocked without GDPR)
 *
 * Drift guard: navToVerificationOrSkip() → this.skip() if SPA routes to
 * /error/timeout. Expected outcome on Cíl 1: SKIPPED.
 * Tags: @demo, @ui, @validation
 */
import { covers } from "../../support/data-loader";
import { navToVerificationOrSkip } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

describe("TC-CP-A2-ALT-4 — GDPR consent required [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-4 — no PUT /reporter fires without GDPR consent",
    function () {
      // IMPORTANT: arrow function banned — this.skip() requires Mocha context
      covers("TT-FUNC-gdprConsent");

      // Set up PUT /reporter intercept BEFORE navigation (must be registered first)
      let reporterPutFired = false;
      cy.intercept(
        { method: "PUT", url: /\/reporter/ },
        (req) => {
          reporterPutFired = true;
          req.continue();
        }
      ).as("reporterPut");

      navToVerificationOrSkip.call(this, BASE);

      // Fill phone for participant A
      cy.get('input[type="tel"]').first().clear().type("608400004");

      // Intentionally do NOT check the GDPR checkbox — this is the negative test

      // Click Odeslat kód
      cy.contains("button", /Odeslat kód/i).click();

      // Wait 2s — mirrors Playwright waitForTimeout
      // eslint-disable-next-line cypress/no-unnecessary-waiting
      cy.wait(2_000);

      // Assert PUT /reporter was NOT fired (form blocked without GDPR consent)
      cy.wrap(null).then(() => {
        expect(reporterPutFired, "PUT /reporter must not fire without GDPR consent").to.be.false;
      });
    }
  );
});
