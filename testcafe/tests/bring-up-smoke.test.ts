/**
 * BRING-UP-SMOKE — TestCafe port
 *
 * Per CP-SUPIN-04 STEP 26. TestCafe equivalent of the Playwright bring-up
 * smoke test (TC-CP-001). Same SUT, same assertions.
 *
 * Differences from Playwright version:
 *   - TestCafe uses Selector and ClientFunction abstractions
 *   - Built-in retries on selector resolution
 *   - No native page.goto — uses test fixture's page() and t.navigateTo()
 *   - Cookie dismiss requires Selector.exists check before click
 */
import { Selector, ClientFunction } from "testcafe";

const BASE = process.env.BOURACKA_BASE ?? "https://demo.bouracka.cz";

const setViewport = ClientFunction(() => {
  // TestCafe configures viewport via .meta or the runner; this is a no-op
  // here but documents intent.
});

fixture("BRING-UP-SMOKE — TestCafe port — DEMO Bouracka rozcestnik")
  .page(`${BASE}/formular/`)
  .meta("viewport", "375x667");

test("Open /formular/ → dismiss cookies → CTA visible + clickable", async (t) => {
  await t.resizeWindow(375, 667);

  // Title sanity
  await t.expect(Selector("title").innerText).match(/Bouračka/);

  // Dismiss cookie banner (privacy-preserving — click ODMÍTNOUT VŠE)
  const cookieReject = Selector("button").withText(/odmítnout vše/i);
  if (await cookieReject.exists) {
    await t.click(cookieReject).wait(500);
  }

  // Page identity heading
  const heading = Selector("h1").withText(/Stala se vám dopravní nehoda/i);
  await t.expect(heading.visible).ok({ timeout: 10_000 });

  // Primary CTA visible + clickable
  const cta = Selector("button").withText(/vyplnit záznam/i).nth(0);
  await t.expect(cta.visible).ok();

  // WCAG 2.2 AA touch target ≥ 44×44 px
  const box = await cta.boundingClientRect;
  await t.expect(box.width).gte(44, `CTA width ${box.width}px < 44`);
  await t.expect(box.height).gte(44, `CTA height ${box.height}px < 44`);

  // Click CTA → SPA routes to /informations
  await t.click(cta);
  await t.expect(ClientFunction(() => location.href)()).match(/\/formular\/informations\/?$/);
  await t.expect(Selector("h1").withText(/Co vás čeká/i).visible).ok();
});
