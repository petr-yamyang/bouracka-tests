/**
 * TC-CP-A2-ALT-5 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-5 block, line ~134).
 *
 * Test: Slovak +421 phone-prefix selectable from Předvolba dropdown.
 *   - Navigate through to /verification (drift-skip guard active)
 *   - Click first "Předvolba" labelled element
 *   - Assert "+421" option is visible in dropdown
 *
 * Drift guard: navToVerificationOrSkip() will this.skip() if SPA routes to
 * /error/timeout (POST /api/reports 403 reCAPTCHA drift — 2026-05-07).
 * Tags: @demo, @ui
 */
import { covers, navToVerificationOrSkip } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

describe("TC-CP-A2-ALT-5 — Slovak +421 Předvolba dropdown [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-5 — +421 option visible in phone prefix dropdown",
    function () {
      // IMPORTANT: arrow function banned — this.skip() requires Mocha context
      covers("TT-SCRN-predvolba421");

      navToVerificationOrSkip.call(this, BASE);

      // Click the Předvolba (country code) dropdown — first occurrence
      cy.contains(/Předvolba/i)
        .first()
        .click();

      // Assert +421 (Slovakia) is visible in the opened dropdown
      cy.contains("+421").first().should("be.visible");
    }
  );
});
