/// <reference types="cypress" />

// Cypress support file — applies to all e2e specs.
// AMENDMENT 2 mobile-first: helper to drive the four binding viewports.

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

export {};
