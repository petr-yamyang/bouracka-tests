import { expect, type Locator } from "@playwright/test";
import { BasePage } from "./BasePage";

export class LandingPage extends BasePage {
  // data_collection_point — heading H1
  h1(): Locator {
    return this.page.locator("h1").first();
  }

  // data_collection_point — anchor links of in-page nav (only on landing)
  anchorLink(anchor: "kdy" | "jak" | "bezpecnost" | "dotazy" | "pro-media"): Locator {
    return this.page.locator(`a[href="#${anchor}"]`);
  }

  // assertion — landing renders + primary CTA leads to /formular
  async expectLandingRenders() {
    await expect(this).toBeOnLanding();
  }
}

// custom matcher hook — keeps assertions tidy
declare module "@playwright/test" {
  interface Matchers<R> {
    toBeOnLanding(): Promise<R>;
  }
}
