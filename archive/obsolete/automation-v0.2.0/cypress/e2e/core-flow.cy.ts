/**
 * TC-CP-003 + TC-CP-004 — Cypress mirror skeleton (tst.* only).
 * Depth pending tst.* recon templates per OQ-CP-15 + reCAPTCHA posture
 * decision per OQ-CP-14. Until then specs skip with a reason.
 */

describe("TC-CP-003 — Wizard happy end-to-end (tst.*)", () => {
  beforeEach(function () {
    if (!Cypress.config("baseUrl")?.includes("tst.bouracka.cz")) {
      this.skip();
    }
  });

  it("Phones → docs → SPZ → location → SMS-OTP both → submit → e-mail dispatch", () => {
    cy.log("Skeleton — depth pending user-supplied tst.* recon (OQ-CP-15) and reCAPTCHA posture (OQ-CP-14).");
    this.skip?.();
  });
});

describe("TC-CP-004 — Wizard failure envelope (F1..F9) — skeleton", () => {
  ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"].forEach((variant) => {
    it(`${variant} — pending tst.* recon`, function () {
      this.skip();
    });
  });
});
