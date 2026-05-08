/**
 * TC-CP-A1-MAIN-DEMO — Cypress port
 *
 * Source-of-truth: playwright/tests/a1-main-happy-day-demo.spec.ts
 *
 * Full E2E happy-day flow on DEMO Bouracka:
 *   Phase 0  (rozcestnik)      → click VYPLNIT ZÁZNAM
 *   Phase A  (intro)           → click Rozumím
 *   Phase 1  (verification)    → A: phone+OTP, B: phone+OTP, success
 *   Phase 2A (documents A)     → manual fallback, 8 fields, recap+email
 *   Phase 2B (documents B)     → same shape
 *   Phase 2.5 (witnesses)      → skip
 *   Phase 3A (vehicle A)       → photos skip, damage NONE, movement, SPZ+brand+insurer
 *   Phase 3B (vehicle B)       → same
 *   Phase 3  (circumstances)   → REAR_END_COLLISION + desc
 *   Phase 3  (situation)       → on-site=yes
 *   Phase 3  (location)        → free-text fallback
 *   Phase 3  (culprit)         → A
 *   Phase 4  (summary)         → checkbox + Podepsat
 *   Phase 4  (sign A + B)      → OTP sign
 *   Phase 4  (success)         → assert "Záznam byl odeslán"
 *
 * Drift guard: this.skip() on /error/timeout (Cíl 1 drift — expected SKIPPED).
 * Runtime: ~90 s (when NOT skipped). Timeout: 180 000 ms.
 * Tags: @demo, @e2e, @drift-aware
 *
 * Note: Playwright source had typo `abel(/Model vozidla/i)` — corrected to
 * `cy.get([aria-label...])` equivalent in this port.
 */
import { covers, dismissCookieBanner, navToVerificationOrSkip, setOtpDigits } from "../../support/nav-helpers";

const BASE =
  Cypress.env("BOURACKA_BASE") ??
  Cypress.env("baseUrl") ??
  "https://demo.bouracka.cz";

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Set textarea value via React native setter (controlled component). */
function setTextarea(value: string): void {
  cy.get("textarea").first().then(($ta) => {
    cy.window().then((win) => {
      const setter = Object.getOwnPropertyDescriptor(
        win.HTMLTextAreaElement.prototype,
        "value"
      )!.set!;
      setter.call($ta[0] as HTMLTextAreaElement, value);
      ($ta[0] as HTMLElement).dispatchEvent(new Event("input", { bubbles: true }));
      ($ta[0] as HTMLElement).dispatchEvent(new Event("blur", { bubbles: true }));
    });
  });
}

/** Fill the per-vehicle Phase 3 sub-flow (called twice — vehicle A then B). */
function fillVehicleSection(args: {
  spz: string;
  brand: string;
  model: string;
  insurer: string;
  desc: string;
}): void {
  // Photos — skip
  cy.url({ timeout: 15_000 }).should("match", /\/accident\/[0-9a-f-]{36}\/?$/);
  cy.contains("button", /POKRAČOVAT BEZ FOTOGRAFIÍ/i).click();

  // Damage — NONE + desc
  cy.url({ timeout: 15_000 }).should("match", /\/damage$/);
  setTextarea(args.desc);
  cy.contains("label", /Vozidlo nebylo poškozeno/i)
    .find('input[type="checkbox"]')
    .check();
  cy.contains("button", /Pokračovat/i).click();

  // Movement — "bylo v pohybu"
  cy.url({ timeout: 15_000 }).should("match", /\/movement$/);
  cy.contains("label", /bylo v pohybu/i)
    .find('input[type="checkbox"]')
    .check();
  cy.contains("button", /Pokračovat/i).click();

  // Vehicle data — SPZ + brand + model + insurer
  cy.url({ timeout: 15_000 }).should("match", /\/data$/);

  cy.get('input[aria-label*="SPZ"], input[id*="spz"], input[name*="spz"]')
    .first()
    .clear()
    .type(args.spz);

  // Brand autocomplete
  cy.get('[aria-label*="Značka"], [aria-label*="znacka"], label:contains("Značka vozidla") + input')
    .first()
    .click()
    .type(args.brand);
  cy.get('[role="listbox"] [role="option"]').first().click();

  // Model autocomplete (Playwright typo fix: corrected selector)
  cy.get('[aria-label*="Model"], [aria-label*="model"], label:contains("Model vozidla") + input')
    .first()
    .click()
    .type(args.model);
  cy.get('[role="listbox"] [role="option"]').first().click();

  cy.contains("button", /^Potvrdit$/).first().click();

  // Insurer
  cy.get('[aria-label*="Pojišťovna"], label:contains("Pojišťovna") + input')
    .first()
    .click();
  cy.get('[role="listbox"] [role="option"]')
    .filter(`:contains("${args.insurer.split(",")[0]}")`)
    .first()
    .click();

  cy.contains("button", /^Potvrdit$/).first().click();
  cy.contains("button", /^Potvrdit$/).last().click();
}

// ─────────────────────────────────────────────────────────────────────────────
// Test
// ─────────────────────────────────────────────────────────────────────────────

describe("TC-CP-A1-MAIN-DEMO — full happy-day E2E [Cypress]", () => {
  it(
    "TC-CP-A1-MAIN-DEMO — Phase 0→A→1→2→2.5→3→4→/success",
    {
      defaultCommandTimeout: 15_000,
      responseTimeout: 30_000,
      pageLoadTimeout: 30_000,
    },
    function () {
      // IMPORTANT: arrow function banned — this.skip() requires Mocha context
      covers("TT-E2E-fullHappyDay");

      // ── Phase 0: rozcestnik ───────────────────────────────────────────────
      cy.visit(`${BASE}/formular/`);
      dismissCookieBanner();
      cy.contains(/Stala se vám dopravní nehoda/i).should("be.visible");
      cy.contains("button", /vyplnit záznam/i).first().click();

      // ── Phase A: intro ────────────────────────────────────────────────────
      cy.url().should("match", /\/formular\/informations\/?$/);
      cy.contains(/Co vás čeká/i).should("be.visible");
      cy.contains("button", /Rozumím/i).click();

      // ── Drift guard — SKIP on /error/timeout (Cíl 1 drift) ───────────────
      navToVerificationOrSkip.call(this, BASE);

      // ── Phase 1: verification A ───────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/verification/);
      cy.contains(/Ověřte účastníky/i).should("be.visible");

      cy.get('input[type="tel"]').first().clear().type("608000001");
      cy.get('input[type="checkbox"]').first().check();
      cy.contains("button", /Odeslat kód/i).click();

      cy.contains(/Zadejte ověřovací kód/i, { timeout: 10_000 }).should("be.visible");
      setOtpDigits('input[type="tel"]', "1234");
      cy.contains("button", /Ověřit/i).click();

      // ── Phase 1: verification B ───────────────────────────────────────────
      cy.contains(/Účastník B/i, { timeout: 10_000 }).should("be.visible");
      cy.get('input[type="tel"]').first().clear().type("608000002");
      cy.contains("button", /Odeslat kód/i).click();

      cy.contains(/Zadejte ověřovací kód/i, { timeout: 10_000 }).should("be.visible");
      setOtpDigits('input[type="tel"]', "5678");
      cy.contains("button", /Ověřit/i).click();

      // ── Phase 1: success → info ───────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/verification\/success/);
      cy.contains("button", /Přejít na informace o nehodě/i).click();

      // ── Phase 2-A: documents A (manual fallback) ──────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/documents\/[0-9a-f-]{36}\/?$/);
      cy.contains("button", /Vyplnit údaje ručně/i).click();
      cy.url().should("match", /manual\?validate=false$/);

      cy.get('input[aria-label*="Jméno"], input[name*="firstName"]').first().clear().type("Adam Test");
      cy.get('input[aria-label*="Příjmení"], input[name*="lastName"]').first().clear().type("Demoversen");
      cy.get('input[aria-label*="Číslo OP"], input[name*="opNumber"]').first().clear().type("123456789");
      cy.get('input[type="date"], input[aria-label*="Datum"]').first().clear().type("1990-01-01");
      cy.get('input[type="email"], input[aria-label*="E-mail"]').first().clear().type("demo-test-A@example.com");

      cy.get('input[aria-label*="adresa"], input[placeholder*="adresa"]').first().click().type("Václavské");
      cy.get('[role="listbox"] [role="option"]', { timeout: 10_000 }).first().click();

      cy.get('input[aria-label*="řidičského"], input[name*="rp"]').first().clear().type("AB 123456");
      cy.get('input[aria-label*="oprávnění"], input[name*="licenseCategory"]').first().click();
      cy.get('[role="listbox"] [role="option"]').contains(/^B$/).first().click();

      cy.contains("button", /Potvrdit/i).click();

      cy.url({ timeout: 15_000 }).should("match", /recap$/);
      cy.get('input[type="email"]').first().clear().type("demo-test-A@example.com");
      cy.contains("button", /Uložit/i).click();

      // ── Phase 2-B: documents B ────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/documents\/[0-9a-f-]{36}\/?$/);
      cy.contains("button", /Vyplnit údaje ručně/i).click();
      cy.url().should("match", /manual\?validate=false$/);

      cy.get('input[aria-label*="Jméno"], input[name*="firstName"]').first().clear().type("Beata");
      cy.get('input[aria-label*="Příjmení"], input[name*="lastName"]').first().clear().type("Druhá");
      cy.get('input[aria-label*="Číslo OP"], input[name*="opNumber"]').first().clear().type("987654321");
      cy.get('input[type="date"], input[aria-label*="Datum"]').first().clear().type("1985-06-15");
      cy.get('input[type="email"], input[aria-label*="E-mail"]').first().clear().type("demo-test-B@example.com");

      cy.get('input[aria-label*="adresa"], input[placeholder*="adresa"]').first().click().type("Karlovo");
      cy.get('[role="listbox"] [role="option"]', { timeout: 10_000 }).first().click();

      cy.get('input[aria-label*="řidičského"], input[name*="rp"]').first().clear().type("CD 654321");
      cy.get('input[aria-label*="oprávnění"], input[name*="licenseCategory"]').first().click();
      cy.get('[role="listbox"] [role="option"]').contains(/^B$/).first().click();

      cy.contains("button", /Potvrdit/i).click();
      cy.url({ timeout: 15_000 }).should("match", /recap$/);
      cy.get('input[type="email"]').first().clear().type("demo-test-B@example.com");
      cy.contains("button", /Uložit/i).click();

      // ── Phase 2.5: witnesses (skip) ───────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/witness$/);
      cy.contains("button", /Pokračovat bez svědků/i).click();

      // ── Phase 3-A: vehicle A ──────────────────────────────────────────────
      fillVehicleSection({
        spz: "1AB1234",
        brand: "ŠKODA",
        model: "OCTAVIA",
        insurer: "Allianz pojišťovna, a. s.",
        desc: "Demoverze popis: vozidlo A bez poskozeni - testovaci scenar",
      });

      // ── Phase 3-B: vehicle B ──────────────────────────────────────────────
      fillVehicleSection({
        spz: "2BC5678",
        brand: "BMW",
        model: "3 SERIES",
        insurer: "Kooperativa pojišťovna, a. s., Vienna Insurance Group",
        desc: "Demoverze popis: vozidlo B bez poskozeni - testovaci scenar",
      });

      // ── Phase 3: circumstances ────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/circumstances$/);
      cy.get('input[type="radio"][value="REAR_END_COLLISION"]').check();
      setTextarea("Demoverze: testovaci scenar A1 - naraz zezadu pri jizde stejnym smerem");
      cy.contains("button", /Pokračovat/i).click();

      // ── Phase 3: situation ────────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/situation$/);
      cy.get('input[type="radio"]').filter(":visible").first().check();
      cy.contains("button", /Pokračovat/i).click();

      // ── Phase 3: location ─────────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/location\/manual$/);
      cy.get("body").then(($b) => {
        if ($b.find('[role="alert"] button').length) {
          cy.get('[role="alert"] button').first().click();
        }
      });
      cy.get("textarea").then(($ta) => {
        if ($ta.length) {
          setTextarea("Demoverze: krizovatka Vaclavske namesti / Stepanska, Praha 1");
        }
      });
      cy.contains("button", /Pokračovat/i).click();

      // ── Phase 3: culprit ──────────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/culprit$/);
      cy.get('input[type="radio"]').first().check();
      cy.contains("button", /Pokračovat/i).click();

      // ── Phase 4: summary ──────────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/summary$/);
      cy.contains(/Shrnutí záznamu/i).should("be.visible");
      cy.get('input[type="checkbox"]').last().check();
      cy.contains("button", /Podepsat záznam o nehodě/i).click();

      // ── Phase 4: sign A ───────────────────────────────────────────────────
      cy.url({ timeout: 15_000 }).should("match", /\/sign-report$/);
      cy.contains("button", /Odeslat kód do sms/i).click();
      cy.contains(/Zadejte ověřovací kód/i, { timeout: 10_000 }).should("be.visible");
      setOtpDigits('input[type="tel"]', "9876");
      cy.contains("button", /Podepsat/i).click();

      // ── Phase 4: sign B ───────────────────────────────────────────────────
      cy.contains(/Účastník B/i, { timeout: 10_000 }).should("be.visible");
      cy.contains("button", /Odeslat kód do sms/i).click();
      cy.contains(/Zadejte ověřovací kód/i, { timeout: 10_000 }).should("be.visible");
      setOtpDigits('input[type="tel"]', "1234");
      cy.contains("button", /Podepsat/i).click();

      // ── Phase 4: success ──────────────────────────────────────────────────
      cy.url({ timeout: 30_000 }).should("match", /\/success$/);
      cy.contains(/Záznam byl odeslán/i).should("be.visible");
      cy.contains("button", /Stáhnout PDF záznam/i).should("be.visible");
    }
  );
});
