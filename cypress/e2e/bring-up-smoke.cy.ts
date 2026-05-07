/**
 * BRING-UP-SMOKE — Cypress port
 *
 * Per CP-SUPIN-04 STEP 26. Cypress equivalent of the Playwright bring-up
 * smoke test (TC-CP-001). Same SUT, same assertions, different framework.
 * Used in CP-SUPIN-05 multi-framework comparison (decide which framework
 * is most ergonomic for the Bouracka test suite long-term).
 *
 * Differences from Playwright version:
 *   - Cypress runs commands inside a Cypress-managed iframe
 *   - Cypress doesn't have built-in role-based selectors (use cy.contains)
 *   - Cypress retries assertions automatically (no need for .toBeVisible({timeout}))
 *   - Cookie banner dismiss uses cy.contains() with .click()
 */

const BASE = Cypress.env("BOURACKA_BASE") ?? "https://demo.bouracka.cz";

describe("BRING-UP-SMOKE — Cypress port — DEMO Bouracka rozcestnik", () => {
  beforeEach(() => {
    cy.viewport(375, 667);
  });

  it("Open /formular/ → dismiss cookies → CTA visible + clickable", () => {
    cy.visit(`${BASE}/formular/`);

    cy.title().should("match", /Bouračka/);

    // Dismiss cookie banner if visible (privacy-preserving)
    cy.get("body").then(($body) => {
      const $reject = $body.find('button:contains("ODMÍTNOUT VŠE")');
      if ($reject.length) {
        cy.contains("button", "ODMÍTNOUT VŠE").click();
        cy.wait(500);
      }
    });

    // Page identity heading visible
    cy.contains("h1", /Stala se vám dopravní nehoda/i).should("be.visible");

    // Primary CTA visible
    cy.contains("button", /vyplnit záznam/i).first().as("cta");
    cy.get("@cta").should("be.visible");

    // WCAG 2.2 AA — touch target ≥ 44x44 px
    cy.get("@cta").then(($el) => {
      const rect = $el[0].getBoundingClientRect();
      expect(rect.width, "CTA width").to.be.gte(44);
      expect(rect.height, "CTA height").to.be.gte(44);
    });

    // Click CTA → SPA routes to /informations
    cy.get("@cta").click();
    cy.url().should("match", /\/formular\/informations\/?$/);
    cy.contains("h1", /Co vás čeká/i).should("be.visible");
  });
});
