/**
 * cypress/support/data-loader.ts — CP-SUPIN-05 fixture loader
 *
 * Per _specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md §4.1.
 *
 * Usage in Cypress specs:
 *   import { loadFixture, covers } from "../support/data-loader";
 *
 *   it("my test", () => {
 *     covers("TT-FUNC-001", "TT-LOV-insuranceCompanies");
 *     loadFixture<Participants>("test-participants").then(data => {
 *       const phoneA = data.participants.A.phone;
 *       // ...
 *     });
 *   });
 *
 * The cy.task('loadFixture', name) is registered in cypress.config.ts
 * setupNodeEvents and reads from fixtures/test-data/ at project root.
 *
 * DO NOT load fixtures from cypress/fixtures/ — that directory is intentionally
 * empty; all test data lives in the shared fixtures/test-data/ tree.
 */

// ─── loadFixture ────────────────────────────────────────────────────────────

/**
 * Load a YAML fixture by base name (without .yaml extension).
 * Returns a Cypress Chainable that resolves to the parsed object.
 *
 * @example
 *   loadFixture<{participants: Participants}>("test-participants").then(d => { ... })
 */
export function loadFixture<T = any>(name: string): Cypress.Chainable<T> {
  return cy.task<T>("loadFixture", name);
}

// ─── covers() annotation ─────────────────────────────────────────────────────

/**
 * Metadata annotation — records which TestTarget (TT) codes are exercised.
 * Logs to Cypress runner output; no effect on pass/fail.
 *
 * Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §7.1 acceptance #2.
 *
 * @example
 *   covers("TT-LOV-vehicleBrands", "TT-SCRN-rozcestnik");
 */
export function covers(...ttCodes: string[]): void {
  Cypress.log({
    name: "covers",
    message: ttCodes.join(", "),
    consoleProps: () => ({ "TT codes": ttCodes }),
  });
}

// ─── Type exports (mirrors fixtures/test-data/*.yaml shapes) ─────────────────

export interface Participant {
  name: string;
  surname: string;
  op_number: string;
  rp_number?: string;
  birth_date: string;
  email: string;
  phone: string;
  phone_prefix: string;
  address_query: string;
  gdpr_consent: boolean;
  otp_code: string;
}

export interface Vehicle {
  spz: string;
  brand: string;
  model: string;
  insurer: string;
  color: string;
  desc: string;
}

export interface Participants {
  participants: Record<string, Participant>;
}

export interface Vehicles {
  vehicles: Record<string, Vehicle>;
}
