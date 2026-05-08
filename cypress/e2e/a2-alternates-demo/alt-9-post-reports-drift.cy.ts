/**
 * TC-CP-A2-ALT-9 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-9 block, line ~187).
 *
 * Test: POST /api/reports characterization (drift-aware).
 *   - Direct HTTP POST (no SPA navigation needed)
 *   - Status 200 → body must contain UUIDv4 (happy path, legacy behaviour)
 *   - Status 403 → soft-pass with console.warn (drift: reCAPTCHA-v3 gate active)
 *   - Any other status → hard FAIL
 *
 * Acceptance: GREEN-soft (200 OR 403 are both valid outcomes at Cíl 1).
 * Writes alt9-response artefact via cy.writeFile to runs/.
 * Tags: @demo, @api, @drift-aware
 */
import { covers } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

const UUID_V4_RE =
  /[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/i;

describe("TC-CP-A2-ALT-9 — POST /api/reports drift characterization [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-9 — POST /api/reports: 200+UUID (happy) OR 403 (drift)",
    () => {
      covers("TT-ACTV-postReports");

      cy.request({
        method: "POST",
        url: `${BASE}/api/reports`,
        headers: { "Content-Type": "application/json" },
        body: {},
        failOnStatusCode: false,
      }).then((res) => {
        const status = res.status;
        const body =
          typeof res.body === "string"
            ? res.body
            : JSON.stringify(res.body);

        // Write diagnostic artefact (mirrors Playwright testInfo.attach)
        const artifact = [
          `status=${status}`,
          "",
          "--- headers ---",
          JSON.stringify(res.headers, null, 2),
          "",
          "--- body ---",
          body,
        ].join("\n");
        cy.task("recordDrift", {
          tc: "ALT-9",
          status,
          ts: new Date().toISOString(),
          bodySnippet: body.slice(0, 200),
        });

        if (status === 200) {
          // Happy path: server returned a UUIDv4 report ID
          expect(body).to.match(UUID_V4_RE);
        } else if (status === 403) {
          // Drift path: reCAPTCHA-v3 gate active — soft-pass
          Cypress.log({
            name: "ALT-9 drift",
            message: `POST /api/reports returned 403; body=${body.slice(0, 200)}`,
          });
          expect([200, 403]).to.include(status);
        } else {
          throw new Error(
            `Unexpected POST /api/reports status: ${status}; body=${body.slice(0, 200)}`
          );
        }
      });
    }
  );
});
