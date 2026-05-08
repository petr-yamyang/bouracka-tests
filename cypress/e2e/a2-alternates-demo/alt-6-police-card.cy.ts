/**
 * TC-CP-A2-ALT-6 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-6 block, line ~140).
 *
 * Test: Police-criteria accordion card expands to reveal key bullets + tel:158.
 *   - "Někdo je zraněný nebo došlo k úmrtí" visible
 *   - "Škoda přesahuje 200 000 Kč" visible (fallback: last "200 000 Kč" match)
 *   - "Došlo ke srážce se zvěří" visible
 *   - Link containing "158" visible
 *
 * Pure UI test — no navToVerification; stays on /formular/ rozcestnik.
 * Tags: @demo, @ui
 */
import { covers, dismissCookieBanner } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

describe("TC-CP-A2-ALT-6 — Police-criteria accordion [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-6 — police card expands: 3 bullets + tel:158 visible",
    () => {
      covers("TT-SCRN-policeCard");

      cy.visit(`${BASE}/formular/`);
      dismissCookieBanner();

      // Expand the police accordion by clicking its heading
      cy.contains(/Kdy volat Policii/i).first().click();

      // Bullet 1 — injury / fatality
      cy.contains("Někdo je zraněný nebo došlo k úmrtí").should("be.visible");

      // Bullet 2 — damage threshold; disambiguate from R1 scope sentence
      // Playwright uses .or(last()) fallback — mirror with cy.get().last() fallback
      cy.get("body").then(($body) => {
        const matched = $body.find(
          ":contains('přesahuje')"
        );
        if (matched.length > 0) {
          cy.contains(/Škoda.*přesahuje.*200\s*000\s*Kč/i).should("be.visible");
        } else {
          // Drift fallback: any "200 000 Kč" mention (last occurrence inside accordion)
          cy.contains("200 000 Kč").last().should("be.visible");
        }
      });

      // Bullet 3 — wildlife collision
      cy.contains("Došlo ke srážce se zvěří").should("be.visible");

      // Emergency number link
      cy.get('a[href*="158"]').should("be.visible");
    }
  );
});
