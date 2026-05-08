/**
 * TC-CP-A2-ALT-1 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-1 block, line ~75).
 *
 * Test: Phase 2 ŘP (Řidičský průkaz) regex rejects malformed input.
 *   - Full SPA navigation through verification (participant A + B OTP)
 *   - Reaches /manual?validate=false
 *   - Fills ŘP field with "INVALID_FORMAT_123"
 *   - Clicks Potvrdit; waits 2s
 *   - Asserts URL does NOT end with /recap (form rejected malformed ŘP)
 *
 * Drift guard: navToVerificationOrSkip() → this.skip() if SPA routes to
 * /error/timeout. Expected outcome on Cíl 1: SKIPPED.
 * Tags: @demo, @ui, @validation
 */
import { covers, dismissCookieBanner, navToVerificationOrSkip, setOtpDigits } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

describe("TC-CP-A2-ALT-1 — ŘP regex validation [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-1 — malformed ŘP rejected; URL stays off /recap",
    function () {
      // IMPORTANT: arrow function banned — this.skip() requires Mocha context
      covers("TT-FUNC-rpRegex");

      navToVerificationOrSkip.call(this, BASE);

      // ── Participant A — phone + GDPR + OTP ─────────────────────────────────
      cy.get('input[type="tel"]').first().clear().type("608100001");
      cy.get('input[type="checkbox"]').first().check();
      cy.contains("button", /Odeslat kód/i).click();

      // OTP digits 1,2,3,4 via native setter (React-controlled inputs)
      setOtpDigits('input[type="tel"]', "1234");
      cy.contains("button", /Ověřit/i).click();

      // ── Participant B — phone + OTP ────────────────────────────────────────
      cy.get('input[type="tel"]').first().clear().type("608100002");
      cy.contains("button", /Odeslat kód/i).click();

      setOtpDigits('input[type="tel"]', "5678");
      cy.contains("button", /Ověřit/i).click();

      // ── Navigate to manual entry ───────────────────────────────────────────
      cy.contains("button", /Přejít na informace/i).click();
      cy.contains("button", /Vyplnit údaje ručně/i).click();
      cy.url({ timeout: 15_000 }).should("match", /manual\?validate=false$/);

      // ── Bad ŘP — should be rejected ───────────────────────────────────────
      cy.get('input[id*="rp"], input[name*="rp"], input[aria-label*="idičského"]')
        .first()
        .clear()
        .type("INVALID_FORMAT_123");
      cy.contains("button", /Potvrdit/i).click();

      // Wait 2s (mirrors Playwright waitForTimeout — gives SPA time to react)
      // eslint-disable-next-line cypress/no-unnecessary-waiting
      cy.wait(2_000);

      // ŘP regex rejected → should NOT have navigated to /recap
      cy.url().should("not.match", /recap$/);
    }
  );
});
