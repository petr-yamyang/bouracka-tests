/**
 * Cypress config — bouracka-tests CP-SUPIN-04 prep
 *
 * Per CLIENT-PILOT-SUPIN-V0.1.md §8 + AMENDMENT 2:
 *   env blocks: tst / tstDemo / public(dev-time)
 *   viewport sweep is exercised at the spec level via cy.viewport().
 *
 * Reporters: Mocha JUnit + custom Excel row-writer (excel-row-writer.ts);
 * the Excel writer is a Cypress plugin task that buffers results in
 * runs/<date>-<tester>/results.jsonl exactly like the Playwright reporter.
 */
import { defineConfig } from "cypress";

const TST = "https://tst.bouracka.cz";
const TST_DEMO = "https://tst.demo.bouracka.cz";
const PUBLIC = "https://www.bouracka.cz";

const env = (process.env.BOURACKA_ENV ?? "public").toLowerCase();
const baseUrl =
  env === "tst" ? TST :
  env === "tst-demo" ? TST_DEMO :
  PUBLIC;

export default defineConfig({
  e2e: {
    baseUrl,
    specPattern: "cypress/e2e/**/*.cy.ts",
    supportFile: "cypress/support/e2e.ts",
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10_000,
    pageLoadTimeout: 30_000,
    video: true,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, _config) {
      // CP-SUPIN-04 — wire excel-row-writer here as a task
      // on('task', { 'excel:writeRow': require('./reporters/excel-row-writer').writeRow });
      return _config;
    },
    env: {
      LANG: "cs-CZ",
      ENV: env,
    },
  },
});
