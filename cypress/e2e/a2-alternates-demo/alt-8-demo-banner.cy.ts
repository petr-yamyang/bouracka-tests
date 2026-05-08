/**
 * TC-CP-A2-ALT-8 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-8 block, line ~179).
 *
 * Test: DEMO banner present on /formular/ rozcestnik (Δ11 + Δ22 confirmation).
 * - "Nacházíte se v DEMO VERZI aplikace" visible
 * - "Vhodné pro malé nehody bez zranění a škody do 200 000 Kč" visible
 *
 * DEMO-only: skip if BASE is not demo.bouracka.cz.
 * Tags: @demo, @ui
 */
import { covers, dismissCookieBanner } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

describe("TC-CP-A2-ALT-8 — DEMO banner present [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-8 — DEMO banner visible (Δ11 + Δ22 confirmation)",
    function () {
      if (!BASE.includes("demo.bouracka.cz")) {
        this.skip(); // DEMO-only test — mirrors Playwright test.skip() guard
      }

      // Import covers here to avoid circular reference issue in module scope
      Cypress.log({ name: "covers", message: "TT-SCRN-demoBanner" });

      cy.visit(`${BASE}/formular/`);
      dismissCookieBanner();

      cy.contains("Nacházíte se v DEMO VERZI aplikace").should("be.visible");
      cy.contains(
        "Vhodné pro malé nehody bez zranění a škody do 200 000 Kč"
      ).should("be.visible");
    }
  );
});
