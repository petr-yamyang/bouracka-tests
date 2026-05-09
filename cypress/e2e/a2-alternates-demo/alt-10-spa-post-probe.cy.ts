/**
 * TC-CP-A2-ALT-10 — Cypress port
 *
 * Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-10 block, line ~211).
 * Note: Playwright source truncated at line 228; behaviour reconstructed from spec +
 * partial source. See _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §3.2.
 *
 * Test: SPA-driven POST /api/reports network capture (drift probe).
 *   - Intercept POST /api/reports before navigation starts
 *   - Navigate through the full SPA click chain (/formular/ → VYPLNIT ZÁZNAM → Rozumím)
 *   - Capture intercepted request: url, method, request body, response status
 *   - If SPA routes to /error/timeout before POST fires → drift-skip (same guard as navToVerification)
 *   - Write captured payload to runs/alt10-cypress-probe.json via cy.task
 *
 * Acceptance: produces alt10 probe artefact; GREEN regardless of 200/403 response.
 * Tags: @demo, @ui, @drift-aware
 */
import { covers } from "../../support/data-loader";
import { dismissCookieBanner } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

describe("TC-CP-A2-ALT-10 — SPA POST /api/reports network capture [Cypress]", () => {
  it(
    "TC-CP-A2-ALT-10 — SPA-driven POST /api/reports captured (drift probe)",
    function () {
      // IMPORTANT: arrow function banned — this.skip() requires Mocha context
      covers("TT-ACTV-spaPostProbe");

      const captured: {
        url: string;
        method: string;
        requestBody: string | null;
        responseStatus: number | null;
        responseBody: string | null;
      }[] = [];

      // Set up intercept BEFORE navigation — mirrors Playwright page.on('request')
      cy.intercept(
        { method: "POST", url: /\/api\/reports(\?|$|\/)/ },
        (req) => {
          const entry: (typeof captured)[number] = {
            url: req.url,
            method: req.method,
            requestBody:
              typeof req.body === "string"
                ? req.body
                : JSON.stringify(req.body),
            responseStatus: null,
            responseBody: null,
          };
          captured.push(entry);

          req.continue((res) => {
            entry.responseStatus = res.statusCode;
            entry.responseBody =
              typeof res.body === "string"
                ? res.body.slice(0, 500)
                : JSON.stringify(res.body).slice(0, 500);
          });
        }
      ).as("reportsPost");

      cy.visit(`${BASE}/formular/`);
      dismissCookieBanner();

      cy.contains(/vyplnit záznam/i)
        .first()
        .click();
      cy.contains(/Rozumím/i).click();

      // Poll URL for up to 30 s — drift guard mirrors navToVerification
      const deadline = Date.now() + 30_000;
      const pollUrl = (): Cypress.Chainable => {
        return cy.url().then((url) => {
          if (/\/verification/.test(url)) return; // happy path — proceed
          if (/\/error\/timeout/.test(url)) {
            const reason =
              `DEMO drift: SPA routed to /error/timeout after Rozumím. ` +
              `POST /api/reports → 403 reCAPTCHA gate (2026-05-07). URL: ${url}`;
            cy.task("recordDrift", { tc: "ALT-10", url, ts: new Date().toISOString() });
            this.skip(); // Mocha context skip — requires function() not arrow
          }
          if (Date.now() < deadline) {
            // eslint-disable-next-line cypress/no-unnecessary-waiting
            return cy.wait(500).then(pollUrl);
          }
          // Deadline passed — if POST was captured anyway, that's the probe data we need
        });
      };

      cy.wrap(null).then(pollUrl);

      // At this point either we are on /verification or we have captured a POST
      // (even a 403). Write whatever was captured as probe artefact.
      cy.then(() => {
        cy.task("recordDrift", {
          tc: "ALT-10",
          captured,
          ts: new Date().toISOString(),
        });
        // The probe succeeds if at least one POST was captured OR if we reached /verification
        // (POST may have been intercepted before URL resolved)
        cy.url().then((url) => {
          const reachedVerification = /\/verification/.test(url);
          const postWasCaptured = captured.length > 0;
          expect(
            reachedVerification || postWasCaptured,
            "Either reached /verification or POST /api/reports was captured"
          ).to.be.true;
          if (postWasCaptured) {
            const first = captured[0];
            expect(first.url).to.match(/\/api\/reports/);
            expect(first.method).to.eq("POST");
            expect([200, 403]).to.include(
              first.responseStatus,
              `Unexpected response status: ${first.responseStatus}`
            );
          }
        });
      });
    }
  );
});
