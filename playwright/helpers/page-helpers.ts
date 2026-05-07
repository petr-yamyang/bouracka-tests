/**
 * Page-level test helpers reusable across the suite.
 *
 * Per CP-SUPIN-04 STEP 23 — discovered cookie-banner-on-first-visit
 * blocks rozcestník H1 on fresh sessions.
 */
import { Page } from "@playwright/test";

/**
 * Dismiss the "Používáme cookies" modal that appears on first visit.
 *
 * Privacy-preserving default: clicks "ODMÍTNOUT VŠE" (reject all).
 * Per Claude user_privacy guidance + GDPR best practice.
 *
 * Returns true if banner was found and dismissed, false otherwise
 * (e.g., session already accepted, or banner not yet rendered).
 *
 * @param page Playwright Page object
 * @param timeoutMs Max wait for banner to appear; default 5_000
 * @param accept If true, click "POVOLIT VŠE" instead (use only for tests
 *               that explicitly need cookies set, e.g. analytics tracking
 *               assertions)
 */
export async function dismissCookieBanner(
  page: Page,
  timeoutMs = 5_000,
  accept = false
): Promise<boolean> {
  const buttonName = accept ? /povolit vše/i : /odmítnout vše/i;
  const button = page.getByRole("button", { name: buttonName });
  try {
    await button.waitFor({ state: "visible", timeout: timeoutMs });
    await button.click();
    // Wait for modal to fully unmount (otherwise subsequent clicks may catch
    // its tail-end fade-out animation)
    await page.waitForTimeout(500);
    return true;
  } catch {
    return false;
  }
}

/**
 * Wait for the SPA to fully hydrate. Simply waits for networkidle, but
 * with a longer-than-default timeout suitable for corp networks.
 */
export async function waitForSpaHydration(page: Page, timeoutMs = 30_000): Promise<void> {
  await page.waitForLoadState("networkidle", { timeout: timeoutMs });
}
