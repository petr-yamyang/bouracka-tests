/**
 * cypress/support/nav-helpers.ts — CP-SUPIN-05 navigation helpers
 *
 * Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §5.1.
 *
 * Drift guard pattern ported from Playwright a2-alternates-demo.spec.ts:43.
 * 2026-05-07 drift: POST /api/reports returns 403 (reCAPTCHA-v3 score < threshold
 * for HeadlessChrome UA) → SPA routes to /formular/error/timeout.
 *
 * Usage:
 *   import { dismissCookieBanner, navToVerificationOrSkip } from "../support/nav-helpers";
 *   navToVerificationOrSkip();   // inside an it() body
 */

const DRIFT_REASON =
  "DEMO drift 2026-05-07 v2: SPA routed to /formular/error/timeout after Rozumím. " +
  "Forensic root cause: POST /api/reports → 403 Forbidden despite valid x-captcha-token. " +
  "Hypothesis: reCAPTCHA v3 score < threshold for HeadlessChrome UA. " +
  "Per recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md.";

// ─── Cookie banner ────────────────────────────────────────────────────────────

/**
 * Best-effort dismiss of cookie modal. Safe to call even when banner is absent.
 */
export function dismissCookieBanner(): void {
  cy.get("body").then(($body) => {
    // Case-insensitive text match; banner may use either case on different envs
    const $reject = $body.find('button:contains("ODMÍTNOUT VŠE"), button:contains("Odmítnout vše")');
    if ($reject.length > 0) {
      cy.wrap($reject.first()).click();
      cy.wait(400);
    }
  });
}

// ─── Drift-aware navigation ───────────────────────────────────────────────────

/**
 * Navigate to /formular/, dismiss cookie banner, click VYPLNIT ZÁZNAM + Rozumím,
 * then POLL the URL for 30s:
 *   - /verification → happy path, continue
 *   - /error/timeout → DEMO drift detected → skip with rationale (Mocha this.skip())
 *
 * MUST be called inside a `function()` test (not arrow function) so that
 * Mocha's `this` context is available for skip. Cypress wraps the Mocha
 * context as `this` inside `function() { ... }` callbacks.
 *
 * @param baseUrl defaults to Cypress env BOURACKA_BASE or https://demo.bouracka.cz
 */
export function navToVerificationOrSkip(
  baseUrl?: string
): Cypress.Chainable<void> {
  const base =
    baseUrl ??
    Cypress.env("BOURACKA_BASE") ??
    "https://demo.bouracka.cz";

  cy.visit(`${base}/formular/`);
  dismissCookieBanner();

  // scrollIntoView: at 375px mobile viewport a MUI Typography <p> overlaps the button
  cy.contains("button", /vyplnit záznam/i, { timeout: 15_000 })
    .first()
    .scrollIntoView()
    .click();

  cy.contains("button", /Rozumím/i, { timeout: 15_000 }).click();

  // Poll URL — Cypress retry mechanism handles the 30s budget via timeout option.
  // We assert the URL matches /verification OR /error/timeout within 30s, then
  // branch on which one we landed on.
  return cy
    .url({ timeout: 30_000 })
    .then(function (this: Mocha.Context, url: string) {
      if (/\/error\/timeout/.test(url)) {
        cy.log(`[drift] ${DRIFT_REASON}`);
        cy.task("recordDrift", {
          url,
          tc: Cypress.currentTest?.titlePath?.join(" > ") ?? "unknown",
          reason: DRIFT_REASON,
        });
        // Mocha context skip — must use `function()` in the spec `it()` block
        this.skip();
      }
    })
    .then(() => {
      cy.url().should("match", /\/verification/);
    }) as Cypress.Chainable<void>;
}

// ─── React-controlled input setter ───────────────────────────────────────────

/**
 * Set OTP digits via React-aware native setter pattern.
 * Equivalent of Playwright page.evaluate() native setter pattern.
 *
 * @param selector CSS selector for the group of single-digit <input type="tel"> elements
 * @param digits   string of digits to fill, e.g. "1234"
 */
export function setOtpDigits(selector: string, digits: string): void {
  cy.get(selector).then(($inputs) => {
    cy.window().then((win) => {
      const setter = Object.getOwnPropertyDescriptor(
        win.HTMLInputElement.prototype,
        "value"
      )!.set!;
      [...digits].forEach((digit, i) => {
        if ($inputs[i]) {
          setter.call($inputs[i] as HTMLInputElement, digit);
          ($inputs[i] as HTMLElement).dispatchEvent(
            new Event("input", { bubbles: true })
          );
        }
      });
    });
  });
}
