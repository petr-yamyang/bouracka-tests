# Bouračka — Lessons learned pro testery — v0.1 CS

> **Audience.** Testeři + QA inženýři, kteří budou psát další TC pro Bouračku
> nad existujícím Playwright kitem. Předpokládá se základní znalost
> Playwright + TypeScript + DEMO Bouračky stack-u (Vite + React + Zod +
> TanStack Query).
>
> **Cíl.** Sdílet konkrétní lessons learned z prvního zeleného CP-SUPIN-04
> kola, aby další iterace TC nezakopávaly stejné gotchas.

---

## §1. Stack a architektura — TLDR

| Aspekt | Hodnota |
|--------|---------|
| Frontend framework | React 18+ + Vite (per-route lazy chunks) |
| UI primitives | Material UI (FormCheckbox, FormRadioGroup, MenuItem, Autocomplete) |
| Validace | **Zod** (mirror client-side + server-side; identické schémy) |
| State / data | TanStack Query (`useIsFetching` hook detekuje pending fetch) |
| API base | `https://demo.bouracka.cz/api/` (nebo `tst.demo.bouracka.cz/api/`, `bouracka.cz/api/`, `tst.bouracka.cz/api/`) |
| Address autocomplete | ČÚZK RUIAN ArcGIS REST (přímo z prohlížeče, ne přes backend) |
| Map | Google Maps JS API + Static Maps (key v bundle) |
| Captcha | reCAPTCHA v3 invisible (site-key v bundle) |
| Mocked na DEMO | N8 SMS Gateway, AISPOV registry, zenID OCR, e-mail dispatch |

## §2. Lessons learned z install/setup

(Plný detail v `_install/INSTALL-FROM-ZERO-v0.4-CS.md`. Stručný shrn:)

1. **Vždy `py`, ne `python`** — Windows MS Store stub redirectuje
   `python.exe` do Microsoft Store. `py.exe` launcher to obchází.
2. **Vždy `py -m pip`, ne `pip`** — `pip.exe` v `Scripts\` není na PATH.
3. **`Set-ExecutionPolicy CurrentUser RemoteSigned`** — Windows defaultně
   blokuje `.ps1` scripts (i `npm.ps1`).
4. **Po každém `winget install` zavřít/otevřít PowerShell** — PATH se
   neaktualizuje v aktuální session.
5. **`winget source reset --force`** pred prvním winget install — fresh
   Windows často selže.

Tyto 5 gotchas dohromady stojí prvního operátora ~45 minut. Sanity-check
script `scripts\sanity-check.ps1` ověří 7 komponent na 30 vteřin.

## §3. Lessons learned z autorování TC

### §3.1 Cookie banner blokuje rozcestník na fresh session

**Symptom:** `getByRole("heading", { name: /Stala se vám dopravní nehoda/i })`
selže s `toBeVisible()` timeout, i když rozcestník vidíte na screenshot.

**Příčina:** Modal "Používáme cookies" sedí na top z-indexu na fresh
sessions a vizuálně překrývá H1.

**Řešení:** v každém TC, který běží proti čerstvé browser session,
volat `dismissCookieBanner(page)` jako STEP 0:

```typescript
import { dismissCookieBanner } from "../helpers/page-helpers";

test("...", async ({ page }) => {
  await page.goto(`${BASE}/formular/`);
  await dismissCookieBanner(page);   // privacy default: ODMITNOUT VSE
  // ...rest of test
});
```

### §3.2 OTP inputs jsou React-controlled — `fill()` nestačí

**Symptom:** `await page.locator('input[type="tel"]').nth(0).fill("1")` se
provede, ale `--reporter=list` ukazuje že OTP submit se chová jako kdyby
pole bylo prázdné. Server vrátí 400 nebo timeout.

**Příčina:** MUI Autocomplete + Zod-validated controlled inputs — `fill()`
nedispatch-uje React-aware `input` event proto state-management hook
nedostane notifikaci.

**Řešení:** použijte React-aware native setter helper:

```typescript
async function setOtpDigits(page, digits: string) {
  await page.evaluate((d) => {
    const inputs = document.querySelectorAll('input[type="tel"]');
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")!.set!;
    for (let i = 0; i < d.length; i++) {
      const input = inputs[i] as HTMLInputElement;
      setter.call(input, d[i]);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }, digits);
}
```

Stejný pattern platí pro `<textarea>` (popis poškození / popis nehody / místo).

### §3.3 DEMO akceptuje libovolný 4-místný OTP

**Důsledek:** v testech proti DEMO POUŽÍVEJTE konstantní OTP `"1234"`.
NEpolľujte server. NA PROD platí Δ1 — reálný N8 SMS dispatch + reálný
kód z SMS.

### §3.4 `?validate=false` deep-link parametr na Phase 2 manual

Phase 2 manual fallback URL je `/formular/report/{r}/documents/{p}/manual?validate=false`.
Tento `validate=false` query parametr je **automatizační hook** —
deaktivuje OCR-data validaci. **Ale** required-field validaci NEdeaktivuje
(`Toto pole je povinné` se stále kontroluje).

### §3.5 Ručně řízené kombobox-y vyžadují `[role="listbox"]` + `[role="option"]`

MUI Autocomplete pattern:

```typescript
// Otevřít dropdown
await page.getByLabel(/Značka vozidla/i).click();
await page.getByLabel(/Značka vozidla/i).fill("ŠKODA");

// Počkat na listbox a vybrat option
await page.locator('[role="listbox"] [role="option"]')
  .filter({ hasText: /^ŠKODA$/ }).first().click();
```

### §3.6 Adresy přes RUIAN ČÚZK — minimum 3 znaky pro autocomplete

```typescript
await page.getByLabel(/Vaše adresa/i).fill("Václavské");   // 3+ chars triggers
await page.locator('[role="listbox"] [role="option"]').first().waitFor();
await page.locator('[role="listbox"] [role="option"]').first().click();
```

### §3.7 Geolocation timeout na automation context

Phase 3 location screen requestuje `navigator.geolocation`. V automation
context (Chromium headless) geolocation API nenavrátí žádnou hodnotu →
SPA shows "Určení polohy trvá příliš dlouho" alert.

**Řešení:** dismiss alert + použít free-text fallback:

```typescript
await page.locator('[role="alert"] button').first().click().catch(() => {});
await setTextarea(page, "Demoverze: krizovatka XYZ");
```

NEBO grant geolocation permission na začátku TC:

```typescript
test.use({
  permissions: ["geolocation"],
  geolocation: { latitude: 50.0755, longitude: 14.4378 }, // Praha
});
```

### §3.8 Bug naming convention

Per `_specs/BUG-NAMING-CONVENTION-v0.1.md`:

```
BUG-CP-{TC_CODE}-{ASSERT_CODE}
```

Same TC + same failed assertion = SAME bug ID. Multiple failures bump
`occurrences` counter, never create duplicate rows. ID je primary key
v `08_Bugs` listu Excel sešitu.

## §4. Lessons learned z testování — výkon

### §4.1 Časové budgety (na běžném laptopu, DEMO)

| Test | Doba |
|------|------|
| Bring-up smoke (TC-CP-001) | 8 s |
| Phase 1 verifikace A+B (cookie + OTP×2) | 15 s |
| Phase 2 documents A (manual + recap) | 25 s |
| Phase 2 documents B (manual + recap) | 25 s |
| Phase 3 vehicle A (damage + movement + vehicle + insurer) | 20 s |
| Phase 3 vehicle B | 20 s |
| Phase 3 shared (circumstances + datetime + location + culprit) | 15 s |
| Phase 4 sign A + B + success | 25 s |
| **Full A1 main happy day** | **~150 s** |

→ Doporučení: full E2E test má `test.setTimeout(180_000)` (3 min).
→ Per-test workflow + helper = 8-10 jednodušších tests místo 1 mega test.

### §4.2 Retry handling

Playwright defaultně `retries: process.env.CI ? 2 : 0`. **NEpoužívejte**
retry pro DEMO testy — pokud test selže, je to legitimate bug nebo
SUT instabilita; retries jen maskují problém.

Výjimka: testy závislé na ČÚZK / Google Maps externích službách —
povolte retry=1 jen pro síťovou flake.

### §4.3 Parallel execution

DEMO Bouračka **toleruje paralelní reporty** (každý request mintuje
nový UUID). V Playwright konfiguraci stačí `fullyParallel: true`
pokud testy nesdílejí state.

ALE: rate-limit na `POST /api/reports` neznámý — pokud rozjedete 10+
paralel, můžete dostat 429. Doporučení: max 4 workers.

## §5. Lessons learned z reverzní analýzy SUT

### §5.1 SPA hydration: `waitUntil: "networkidle"` není volitelné

```typescript
// Špatně:
await page.goto(`${BASE}/formular/`, { waitUntil: "domcontentloaded" });
// → React hydration ještě neprobehlá → assertions selžou
// Dobře:
await page.goto(`${BASE}/formular/`, { waitUntil: "networkidle", timeout: 30_000 });
// → počkat na všechny assets + Azure outage feed + Google Maps
```

### §5.2 Per-route lazy chunks — bundle URLs jako test fixtures

V `intel-probes/` testech kontrolujeme přítomnost konkrétních lazy
chunks per phase. Pokud Vite build změní hash, naše assertions
musí být na **route name part**, ne celý hash:

```typescript
// Špatně:
const chunkExists = response.url().includes("informations-D1Jrhrhq.js");
// Dobře:
const chunkExists = response.url().match(/\/formular\/assets\/informations-[A-Za-z0-9_-]+\.js$/);
```

### §5.3 Codelist surface — selektivní 200/403

`/api/enumerations/insuranceCompanies` a `/api/enumerations/vehicleBrands`
jsou **veřejné** (200). Ostatní (licenseCategories, damageZones, movementTypes,
accidentCauses, accidentCategories, vehicleCategories, documentTypes,
witnessTypes) vrací **403** — codelist je v JS bundle.

Pro DOM-scrape protected enums viz `playwright/tests/intel-probes/02-codelist-scrape.spec.ts`.

### §5.4 Δ matice DEMO vs PROD — když to selže na PROD a passnut na DEMO

Pokud váš test passes na DEMO ale selže na PROD, **nejdřív zkontrolujte
Δ matrix** (`recon/DELTA-DEMO-vs-PROD-v0.1.md`). 8 potvrzených delt
(N8 SMS, zenID OCR, branding, cookie banner, intro screen, hint banners,
Maps locale, email dispatch) jsou očekávané rozdíly, ne bugy.

## §6. Templates a shared helpers

| Helper | Lokace | Co dělá |
|--------|--------|---------|
| `dismissCookieBanner(page)` | `playwright/helpers/page-helpers.ts` | dismiss "Používáme cookies" modal |
| `waitForSpaHydration(page)` | totéž | wait pro `networkidle` s 30s timeoutem |
| `setOtpDigits(page, digits)` | inline ve většině TC | React-aware native setter pro 4 OTP boxy |
| `setTextarea(page, value)` | totéž | React-aware native setter pro `<textarea>` |
| `fillVehicleSection(page, args)` | inline v `a1-main-happy-day-demo.spec.ts` | Phase 3 sub-flow per účastník |

Doporučení pro CP-SUPIN-05: extrahovat všechny helpery do `playwright/helpers/`
a publikovat jako npm-style module reusable napříč TCs.

## §7. Doporučení pro autorování dalších TC

1. **Začněte s template** `bring-up-smoke.spec.ts` — má cookie dismiss + ověření
2. **Přidejte tag** `{ tag: ["@demo"] }` nebo `["@prod"]` nebo `["@cross-branch"]`
3. **Reuse helpery** — neimplementujte cookie dismiss a OTP helper podruhé
4. **Sledujte Δ matrix** — pokud test má per-branch chování, zaznamenejte to
5. **Run-once test budgeting** — 1 minute = ~3 simple TC, 1 full E2E
6. **Po failu** — zkontrolujte screenshot v `test-results/.../test-failed-1.png`
   PŘED debug v kódu

## §8. Common pitfalls — checklista

| Symptom | Pravděpodobná příčina | Fix |
|---------|------------------------|-----|
| `toBeVisible()` timeout na heading | Cookie banner blokuje | `dismissCookieBanner()` STEP 0 |
| `boundingBox()` returns null | Element je v hamburger menu (mobile) | navigujte na `/formular/`, ne `/` |
| OTP submit returns 400 | `fill()` nedispatchuje onChange | použijte `setOtpDigits()` helper |
| `waitForURL()` timeout | SPA pomalý | zvyšte timeout NA 15s+ |
| RUIAN autocomplete prázdný | Méně než 3 znaky | typujte 3+ znaky pred listbox waitForem |
| Geolocation alert blokuje | Headless nemá GPS | grant permission nebo dismiss alert |
| Test passes na DEMO, fails na PROD | Δ matrix item | zkontrolujte recon/DELTA-DEMO-vs-PROD-v0.1.md |
| `404` na `/api/enumerations/{name}` | Codelist je protected | použijte DOM scrape, ne API |

## §9. Lessons learned z e-mailové delivery (2026-05-07)

**Trigger.** v0.4.9 ZIP zablokován Gmail/Active24 jako "obsahuje virus code".
Forensic root cause: 22× `.ps1` + 2× `.cmd` + 6× literál `-Execution`Policy By`pass`
(top IOC pro ransomware loadery).

### §9.1 Železná pravidla pro e-mailem-shipped ZIPy

1. **NIKDY** nezahrnovat `.cmd`, `.bat`, `.ps1