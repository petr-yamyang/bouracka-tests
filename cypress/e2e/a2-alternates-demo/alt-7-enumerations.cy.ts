/**
 * TC-CP-A2-ALT-7 — Cypress port
 *
 * Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §2 (port order: ALT-7 first).
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-7 block, line ~158).
 *
 * Test: public enumerations return expected counts; protected return 403.
 * - /api/enumerations/insuranceCompanies → 200, ≥10 entries, ALLIANZ present
 * - /api/enumerations/vehicleBrands      → 200, ≥200 entries, ŠKODA present
 * - 8 protected endpoints                → 403 each
 *
 * This is a pure API test — no UI navigation required.
 * Cypress: uses cy.request() (no browser visit needed).
 *
 * Fixture: fixtures/test-data/codelists-live-2026-05-06.yaml (reference counts)
 * Tags: @demo, @api
 */
import { loadFixture, covers } from "../../support/data-loader";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

const PROTECTED_ENDPOINTS = [
  "licenseCategories",
  "damageZones",
  "movementTypes",
  "accidentCauses",
  "accidentCategories",
  "vehicleCategories",
  "documentTypes",
  "witnessTypes",
];

describe("TC-CP-A2-ALT-7 — public enumerations + protected 403 [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-7 — insuranceCompanies ≥10 + ALLIANZ; vehicleBrands ≥200 + ŠKODA; 8 protected → 403",
    function () {
      covers("TT-LOV-insuranceCompanies", "TT-LOV-vehicleBrands", "TT-ACTV-enumProtection");

      // ── insuranceCompanies ─────────────────────────────────────────────────
      cy.request({
        method: "GET",
        url: `${BASE}/api/enumerations/insuranceCompanies`,
        failOnStatusCode: true,
      }).then((res) => {
        expect(res.status).to.eq(200);
        const body: any[] = res.body;
        expect(body.length, "insuranceCompanies count").to.be.gte(10);
        const allianz = body.find((x: any) => x.code === "ALLIANZ");
        expect(allianz, "ALLIANZ entry").to.exist;
      });

      // ── vehicleBrands ──────────────────────────────────────────────────────
      cy.request({
        method: "GET",
        url: `${BASE}/api/enumerations/vehicleBrands`,
        failOnStatusCode: true,
      }).then((res) => {
        expect(res.status).to.eq(200);
        const body: any[] = res.body;
        expect(body.length, "vehicleBrands count").to.be.gte(200);
        const skoda = body.find((x: any) => x.name === "ŠKODA");
        expect(skoda, "ŠKODA entry").to.exist;
      });

      // ── Protected endpoints → 403 ──────────────────────────────────────────
      for (const name of PROTECTED_ENDPOINTS) {
        cy.request({
          method: "GET",
          url: `${BASE}/api/enumerations/${name}`,
          failOnStatusCode: false,
        }).then((res) => {
          expect(res.status, `${name} should be 403`).to.eq(403);
        });
      }
    }
  );
});
