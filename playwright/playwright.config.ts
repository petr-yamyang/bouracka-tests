/**
 * Playwright config — bouracka-tests CP-SUPIN-03 prep
 *
 * Per CLIENT-PILOT-SUPIN-V0.1.md §8 + AMENDMENT 2 (mobile-first):
 * - Three projects: tst / tst-demo / public(dev-time only)
 * - Each project carries the AMENDMENT 2 viewport sweep — desktop +
 *   320 / 375 / 414 px mobile profiles.
 * - Reporters: HTML (out-of-box) + custom Excel row-writer that pushes
 *   into BOURACKA-TESTPLAN-v0.1.xlsx → 07_TestRunResults sheet.
 */
import { defineConfig, devices } from "@playwright/test";

const PUBLIC = "https://www.bouracka.cz";
const TST = "https://tst.bouracka.cz";
const TST_DEMO = "https://tst.demo.bouracka.cz";

const mobileViewports = [
  { name: "mobile-320", viewport: { width: 320, height: 568 } },
  { name: "mobile-375", viewport: { width: 375, height: 667 } },
  { name: "mobile-414", viewport: { width: 414, height: 896 } },
];

const projectFor = (envName: string, baseURL: string) => [
  {
    name: `${envName}-desktop`,
    use: { ...devices["Desktop Chrome"], baseURL, locale: "cs-CZ" },
  },
  ...mobileViewports.map((mv) => ({
    name: `${envName}-${mv.name}`,
    use: {
      ...devices["Desktop Chrome"], // Chromium engine; we override viewport
      baseURL,
      locale: "cs-CZ",
      viewport: mv.viewport,
      isMobile: true,
      hasTouch: true,
    },
  })),
];

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  retries: process.env.CI ? 2 : 0,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "../playwright-report" }],
    ["./reporters/excel-row-writer.ts"],
  ],
  use: {
    locale: "cs-CZ",
    timezoneId: "Europe/Prague",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },
  projects: [
    ...projectFor("tst", TST),
    ...projectFor("tst-demo", TST_DEMO),
    ...projectFor("public", PUBLIC),
    // Single mobile project for the bring-up smoke (cheaper to invoke explicitly):
    {
      name: "public-mobile-375",
      use: { ...devices["Desktop Chrome"], baseURL: PUBLIC, locale: "cs-CZ",
             viewport: { width: 375, height: 667 }, isMobile: true, hasTouch: true },
    },
  ],
});
