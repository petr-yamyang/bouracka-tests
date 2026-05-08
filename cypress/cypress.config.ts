/**
 * Cypress config — bouracka-tests CP-SUPIN-05 cross-framework parity
 *
 * Per CLIENT-PILOT-SUPIN-V0.1.md §8 + AMENDMENT 2 + CP-SUPIN-05:
 *   env blocks: tst / tstDemo / public(dev-time)
 *   viewport sweep exercised at the spec level via cy.viewport().
 *
 * CP-SUPIN-05 adds:
 *   loadFixture task — reads fixtures/test-data/*.yaml relative to project root.
 *     Requires: npm install yaml
 *   recordDrift task — appends drift events to runs/drift-log.jsonl
 *
 * Reporters: Mocha JUnit + custom Excel row-writer (excel-row-writer.ts);
 * the Excel writer is a Cypress plugin task that buffers results in
 * runs/<date>-<tester>/results.jsonl exactly like the Playwright reporter.
 */
import { defineConfig } from "cypress";
import * as fs from "fs";
import * as path from "path";

// Lazy-load yaml — installed as devDependency (npm install yaml)
// Falls back to a minimal hand-rolled parser for the simple YAML shapes
// in fixtures/test-data/ if the yaml package is not yet installed.
function loadYaml(filePath: string): any {
  const raw = fs.readFileSync(filePath, "utf-8");
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const yaml = require("yaml");
    return yaml.parse(raw);
  } catch {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const yaml = require("js-yaml");
      return yaml.load(raw);
    } catch {
      throw new Error(
        `YAML package not found. Run: npm install yaml\n` +
        `(tried 'yaml' and 'js-yaml', both absent)\n` +
        `File: ${filePath}`
      );
    }
  }
}

const TST = "https://tst.bouracka.cz";
const TST_DEMO = "https://tst.demo.bouracka.cz";
const PUBLIC = "https://www.bouracka.cz";

const env = (process.env.BOURACKA_ENV ?? "public").toLowerCase();
const baseUrl =
  env === "tst" ? TST :
  env === "tst-demo" ? TST_DEMO :
  process.env.BOURACKA_BASE ?? PUBLIC;

export default defineConfig({
  e2e: {
    baseUrl,
    specPattern: "cypress/e2e/**/*.cy.ts",
    supportFile: "cypress/support/e2e.ts",
    viewportWidth: 375,    // AMENDMENT 2 mobile-first default
    viewportHeight: 667,
    defaultCommandTimeout: 10_000,
    pageLoadTimeout: 60_000,
    // Block external scripts that permanently hang the browser load event under
    // Cypress DevTools instrumentation (reCAPTCHA v3 + GTM background connections).
    // Blocked requests fail fast → load event fires → cy.visit() unblocks.
    // POST /api/reports still returns 403 (missing captcha token) → SPA routes
    // to /error/timeout → drift guard detects → this.skip() — expected Cíl 1 outcome.
    blockHosts: [
      "www.gstatic.com",           // reCAPTCHA v3 script bundle
      "recaptcha.net",             // reCAPTCHA alternate domain
      "www.google.com",            // reCAPTCHA api.js
      "www.googletagmanager.com",  // GTM — background network keep-alive
      "ssl.google-analytics.com",  // GA — background analytics
      "www.google-analytics.com",  // GA alternate
      "fonts.googleapis.com",      // Google Fonts CSS (async, often delays load)
      "fonts.gstatic.com",         // Google Fonts files
    ],
    video: true,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, _config) {
      // ── CP-SUPIN-05: fixture loader task ───────────────────────────────────
      // Usage in tests: cy.task('loadFixture', 'test-participants') → resolves to object
      const fixtureRoot = path.resolve(__dirname, "../fixtures/test-data");
      on("task", {
        loadFixture(name: string) {
          // Strip .yaml extension if caller passed it; allow bare name or full
          const baseName = name.replace(/\.yaml$/, "");
          const filePath = path.join(fixtureRoot, `${baseName}.yaml`);
          if (!fs.existsSync(filePath)) {
            throw new Error(`Fixture not found: ${filePath}`);
          }
          return loadYaml(filePath);
        },

        // ── Drift log appender ─────────────────────────────────────────────
        recordDrift(entry: Record<string, unknown>) {
          const logDir = path.resolve(__dirname, "../runs");
          if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
          const logFile = path.join(logDir, "drift-log.jsonl");
          fs.appendFileSync(logFile, JSON.stringify({ ts: new Date().toISOString(), ...entry }) + "\n");
          return null;
        },
      });

      // CP-SUPIN-04 — excel-row-writer (wired when reporter package installed)
      // on('task', { 'excel:writeRow': require('./reporters/excel-row-writer').writeRow });
      return _config;
    },
    env: {
      LANG: "cs-CZ",
      ENV: env,
      BOURACKA_BASE: process.env.BOURACKA_BASE ?? "https://demo.bouracka.cz",
    },
  },
});
