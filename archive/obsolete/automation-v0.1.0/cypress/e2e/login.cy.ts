/**
 * TC-CP-001 + TC-CP-002 — Cypress mirror of the Playwright spec.
 *
 * Filename retains "login" for traceability with CLIENT-PILOT-SUPIN §4.1
 * placeholders; actual scope per recon is "wizard-entry happy" + "police-call
 * branch failure" (re-scoped per OQ-CP-12).
 *
 * R-CAST-2 — every step labelled with kind in inline comments.
 * AMENDMENT 2 mobile-first — viewport sweep is exercised below.
 */

const VIEWPORTS = ["320", "375", "414", "desktop"] as const;

VIEWPORTS.forEach((vp) => {
  describe(`TC-CP-001 [${vp}] — Vstup do formuláře — happy`, () => {
    beforeEach(() => {
      cy.viewportPreset(vp);
    });

    it("Open landing → click VYPLNIT ZÁZNAM → reach gateway", () => {
      // STEP 1 — trigger_point: navigate to landing
      cy.visit("/");

      // STEP 2 — assertion: title carries Bouračka
      cy.title().should("match", /Bouračka/);

      // STEP 3 — data_collection_point: locate primary CTA
      cy.contains("button", /VYPLNIT ZÁZNAM/i).first().as("cta");

      // STEP 4 — assertion: CTA visible + parent <a> href into /formular
      cy.get("@cta").should("be.visible");
      cy.get("@cta").parent("a").should("have.attr", "href").and("match", /\/formular/);

      // STEP 5 — assertion: mobile-only — touch-target ≥ 44×44
      if (vp !== "desktop") {
        cy.get("@cta").then(($el) => {
          const rect = $el[0].getBoundingClientRect();
          expect(rect.width, "touch-target width").to.be.gte(44);
          expect(rect.height, "touch-target height").to.be.gte(44);
        });
      }

      // STEP 6 — trigger_point: click CTA
      cy.get("@cta").click();

      // STEP 7 — control_point: branch on URL — accept either /formular variants
      cy.url().should("match", /\/formular(\?.*)?$/);

      // STEP 8 — data_collection_point: capture gateway H1
      cy.get("h1").first().invoke("text").as("gatewayH1");

      // STEP 9 — assertion: gateway H1 + reCAPTCHA badge attached
      cy.get("@gatewayH1").should("match", /dopravní nehoda/i);
      cy.get(".grecaptcha-badge, [data-recaptcha]", { timeout: 15000 }).should("exist");
    });
  });

  describe(`TC-CP-002 [${vp}] — Větvení Policie ČR (failure pair)`, () => {
    beforeEach(() => {
      cy.viewportPreset(vp);
    });

    it("Police-call interlock — 7 conditions + tel:158 + wizard does NOT advance", () => {
      // STEP 1 — trigger_point: navigate directly to /formular
      cy.visit("/formular");

      // STEP 2 — data_collection_point: locate police-call card heading
      cy.contains(/Kdy volat Policii ČR/i).should("be.visible").as("policeCard");

      // STEP 3 — trigger_point: expand the panel
      cy.get("@policeCard").click();

      // STEP 4 — assertion: 7 hard-stop conditions listed
      cy.get('[role="listitem"]')
        .filter(":contains('zraněný'), :contains('200 000'), :contains('3. osoby'), :contains('prospěšné'), :contains('plynulost'), :contains('ujel'), :contains('zvěř')")
        .should("have.length", 7);

      // STEP 5 — control_point: branch on test variant — happy = call police
      // (the alternate branch is the F1 failure mode in FLW-002)

      // STEP 6 — assertion: tel:158 link present + href shape sane
      cy.contains("a", /Volat Policii ČR/i)
        .should("be.visible")
        .invoke("attr", "href")
        .should("match", /^tel:\s*158$/);

      // STEP 7 — data_collection_point + STEP 8 — assertion: URL still /formular
      cy.url().should("match", /\/formular(\?.*)?$/);
    });
  });
});
