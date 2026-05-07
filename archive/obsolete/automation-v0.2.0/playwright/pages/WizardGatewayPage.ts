import { expect, type Locator } from "@playwright/test";
import { BasePage } from "./BasePage";

export class WizardGatewayPage extends BasePage {
  // data_collection_point — gateway H1 ("Stala se vám dopravní nehoda?…")
  gatewayH1(): Locator {
    return this.page.locator("h1").first();
  }

  // data_collection_point — primary "VYPLNIT ZÁZNAM" CTA on the gateway
  vyplnitZaznamButton(): Locator {
    return this.page.getByRole("button", { name: /Vyplnit záznam/i }).first();
  }

  // data_collection_point — police-call interlock heading
  policeCallCardHeading(): Locator {
    return this.page.getByRole("heading", { name: /Kdy volat Policii ČR/i });
  }

  // trigger_point — expand the police-call panel
  async openPoliceCallPanel() {
    await this.policeCallCardHeading().click();
  }

  // data_collection_point — list of 7 hard-stop conditions
  policeConditions(): Locator {
    return this.page
      .locator('[role="listitem"]')
      .filter({ hasText: /(zraněný|200 000|3\. osoby|prospěšné|plynulost|ujel|zvěř)/ });
  }

  // data_collection_point — tel:158 escape link
  policeCallLink158(): Locator {
    return this.page.getByRole("link", { name: /Volat Policii ČR/i });
  }

  // data_collection_point — reCAPTCHA badge
  recaptchaBadge(): Locator {
    return this.page.locator(".grecaptcha-badge, [data-recaptcha]");
  }

  // assertion — exactly 7 hard-stop conditions visible
  async expectSevenPoliceConditions() {
    await expect(this.policeConditions()).toHaveCount(7);
  }

  // assertion — tel:158 link present and href shape sane
  async expectPoliceLinkOk() {
    const lnk = this.policeCallLink158();
    await expect(lnk).toBeVisible();
    await expect(lnk).toHaveAttribute("href", /^tel:\s*158$/);
  }

  // assertion — wizard did NOT advance (URL still on /formular)
  async expectStillOnGateway() {
    await expect(this.page).toHaveURL(/\/formular(\?.*)?$/);
  }
}
