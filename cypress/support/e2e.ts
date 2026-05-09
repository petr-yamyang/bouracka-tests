/// <reference types="cypress" />

// Cypress support file — applies to all e2e specs.
// AMENDMENT 2 mobile-first: helper to drive the four binding viewports.
//
// CP-SUPIN-05 fix (2026-05-09):
// Pre-visit intercepts for external scripts that create permanent background
// connections under Cypress DevTools proxy (reCAPTCHA v3 + GTM + GA).
// Root cause: blockHosts blocks HTTP fetches but NOT the subsequent
// WebSocket upgrade that reCAPTCHA v3 initiates after its script executes.
// Fix: return empty JS body so the script executes as a no-op → no WS created
// → browser load event fires → cy.visit() unblocks in <10s.
//
// These intercepts are installed before every test (beforeEach fires before
// the test's own cy.visit() call), so the stubs are active on first request.

declare global {
  namespace Cypress {
    interface Chainable {
      /** Set viewport to one of the AMENDMENT 2 mobile-first profiles. */
      viewportPreset(name: "320" | "375" | "414" | "desktop"): Chainable<void>;
    }
  }
}

Cypress.Commands.add("viewportPreset", (name) => {
  switch (name) {
    case "320": cy.viewport(320, 568); break;
    case "375": cy.viewport(375, 667); break;
    case "414": cy.viewport(414, 896); break;
    case "desktop": cy.viewport(1280, 720); break;
  }
});

// ── Background-connection stubs ────────────────────────────────────────────
// Intercept external tracking/captcha scripts before every test's cy.visit().
// Returns a minimal valid JS string so the browser doesn't throw parse errors.
// POST collection endpoints return 204 to silence XHR error handlers in the SPA.
beforeEach(() => {
  // reCAPTCHA v3 — script fetch + badge iframe
  cy.intercept(/gstatic\.com/, { statusCode: 200, body: "/* blocked */", headers: { "Content-Type": "application/javascript" } });
  cy.intercept(/recaptcha\.net/, { statusCode: 200, body: "/* blocked */", headers: { "Content-Type": "application/javascript" } });
  // Google Tag Manager
  cy.intercept(/googletagmanager\.com/, { statusCode: 200, body: "/* blocked */", headers: { "Content-Type": "application/javascript" } });
  // Google Analytics (script + beacon POST)
  cy.intercept(/google-analytics\.com/, { statusCode: 204, body: "" });
  // Google APIs (fonts CSS + reCAPTCHA api.js)
  cy.intercept(/googleapis\.com/, { statusCode: 200, body: "/* blocked */", headers: { "Content-Type": "application/javascript" } });
  // Google Fonts files
  cy.intercept(/fonts\.gstatic\.com/, { statusCode: 204, body: "" });
  // Google Ads / DoubleClick
  cy.intercept(/doubleclick\.net/, { statusCode: 204, body: "" });
  // Common analytics / session recording
  cy.intercept(/hotjar\.com/, { statusCode: 200, body: "/* blocked */", headers: { "Content-Type": "application/javascript" } });
  cy.intercept(/clarity\.ms/, { statusCode: 200, body: "/* blocked */", headers: { "Content-Type": "application/javascript" } });
  cy.intercept(/sentry\.io/, { statusCode: 204, body: "" });
});

export {};
