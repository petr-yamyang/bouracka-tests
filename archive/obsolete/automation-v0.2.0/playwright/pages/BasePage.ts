/**
 * BasePage — page-object base.
 *
 * Per R-CAST-2 — every step in subclasses MUST be commented with one of:
 *   trigger_point | data_collection_point | control_point | assertion
 */
import { expect, type Page, type Locator } from "@playwright/test";

export class BasePage {
  constructor(public readonly page: Page) {}

  // trigger_point — primary nav (envURL is per-project from config)
  async open(path = "/") {
    await this.page.goto(path);
  }

  // data_collection_point — title for smoke
  async title() {
    return this.page.title();
  }

  // assertion — page title regex
  async expectTitleMatches(regex: RegExp) {
    await expect(this.page).toHaveTitle(regex);
  }

  // data_collection_point — the persistent header CTA
  primaryCTA(): Locator {
    return this.page
      .getByRole("link", { name: /VYPLNIT ZÁZNAM/i })
      .or(this.page.getByRole("button", { name: /VYPLNIT ZÁZNAM/i }))
      .first();
  }

  // assertion — touch-target ≥ 44×44 (WCAG 2.2 AA target-size)
  async expectTouchTargetAtLeast(loc: Locator, w = 44, h = 44) {
    const box = await loc.boundingBox();
    expect(box, "bounding box must exist").not.toBeNull();
    expect(box!.width, `touch-target width ${box!.width} < ${w}`).toBeGreaterThanOrEqual(w);
    expect(box!.height, `touch-target height ${box!.height} < ${h}`).toBeGreaterThanOrEqual(h);
  }
}
