/**
 * TC-CP-001 + TC-CP-002 — TestCafe mirror (fallback framework per Gate 1).
 *
 * Held in scope only as a contingency per CLIENT-PILOT-SUPIN-V0.1.md §3.3.
 * If Gate 1 (install policy) and Gate 2 (first scenario green) confirm
 * Cypress + Playwright are sufficient, this folder is dropped per
 * R-STRUCT-1 (REPLACED block in the close notes).
 */
import { Selector, ClientFunction } from "testcafe";

const PUBLIC = "https://www.bouracka.cz";
const env = (process.env.BOURACKA_ENV || "public").toLowerCase();
const baseUrl =
  env === "tst" ? "https://tst.bouracka.cz" :
  env === "tst-demo" ? "https://tst.demo.bouracka.cz" :
  PUBLIC;

const getURL = ClientFunction(() => window.location.href);

fixture("TC-CP-001/002 — Wizard entry smoke + police-call branch")
  .page(`${baseUrl}/`);

test("TC-CP-001 — Open landing → click CTA → reach gateway", async (t) => {
  // STEP 1 — trigger_point: implicit via fixture .page()
  // STEP 2 — assertion: title carries Bouračka
  await t.expect(Selector("title").innerText).match(/Bouračka/);

  // STEP 3 — data_collection_point: locate primary CTA
  const cta = Selector("button").withText(/VYPLNIT ZÁZNAM/i).nth(0);

  // STEP 4 — assertion: visible
  await t.expect(cta.visible).ok();

  // STEP 6 — trigger_point: click
  await t.click(cta);

  // STEP 7 — control_point + STEP 9 — assertion: URL on /formular
  await t.expect(getURL()).match(/\/formular(\?.*)?$/);

  // STEP 9 (cont.) — assertion: gateway H1
  const h1 = Selector("h1").nth(0);
  await t.expect(h1.innerText).match(/dopravní nehoda/i);
});

test("TC-CP-002 — Police-call interlock — 7 conditions + tel:158 + no advance", async (t) => {
  // STEP 1 — trigger_point: navigate to /formular
  await t.navigateTo(`${baseUrl}/formular`);

  // STEP 2 — data_collection_point: police-call card heading
  const heading = Selector("h2,h3,h4").withText(/Kdy volat Policii ČR/i).nth(0);
  await t.expect(heading.visible).ok();

  // STEP 3 — trigger_point: expand
  await t.click(heading);

  // STEP 4 — assertion: 7 listitems matching the regulatory keywords
  const conditions = Selector('[role="listitem"]').withText(
    /zraněný|200 000|3\. osoby|prospěšné|plynulost|ujel|zvěř/
  );
  await t.expect(conditions.count).eql(7);

  // STEP 6 — assertion: tel:158 link
  const policeLink = Selector("a").withText(/Volat Policii ČR/i);
  await t.expect(policeLink.getAttribute("href")).match(/^tel:\s*158$/);

  // STEP 8 — assertion: URL still /formular
  await t.expect(getURL()).match(/\/formular(\?.*)?$/);
});
