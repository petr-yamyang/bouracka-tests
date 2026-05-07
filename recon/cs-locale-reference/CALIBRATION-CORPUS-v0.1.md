# CS-Locale Calibration Corpus — v0.1

> **Purpose.** Verbatim Czech-locale source strings from the analytical
> doc / email transcripts, kept as a calibration baseline for:
> 1. translation control — when EN-second labels need to be authored
>    (test reports, dashboards, summary docs), this is the reference
>    English-translators read alongside;
> 2. drift detection — every test that asserts a Czech CS string
>    matches its expected regex or literal pulls from this corpus
>    rather than re-typing the string and risking diacritic loss /
>    spelling drift;
> 3. authoritative ground-truth — if a screen recon (SCR-NNN.md) and
>    this corpus disagree on the CS spelling of a label, this corpus
>    wins (it's verbatim from the analytical doc / SUPIN-internal
>    email).
>
> **Status.** Append-only — when new email transcripts arrive, add
> a new section. Never edit prior sections except to fix a transcription
> typo (with a footnote noting the change).

---

## §1. LandingPage — analytical doc §3.3.2.1

> Source: SUPIN-internal email transcript, supplied 2026-05-05.
> Confirms what was inferred from photos IMG_1033..IMG_1035 (analytical
> doc pages 16–18/133). Calibrated against `recon/screens/SCR-001.md`.

### §1.1 POPIS

> Landing page slouží jako vstupní bod k online aplikaci. Cílem je,
> aby se uživatel hned na první obrazovce seznámil s tím, co aplikace
> dělá, jak aplikaci používat a na koho se v případě potřeby obrátit.
> Stránka je určeno pro širší veřejnost. **Aplikace hlášení začíná
> až vstupem na obrazovku 00_Homepage – Rozcestník.**

### §1.2 LandingPage je rozdělena na několik sekcí

#### Menu LandingPage — fixní pozice
- Logo aplikace
- Logo ČKP   *(corpus per analytical doc §3.3.2.1 footer; the bare-text "CKP" elsewhere in the email transcript is a diacritic-loss artefact — use "ČKP" everywhere)*
- Navigační tlačítko 1 — **Kdy** → Sekce 3 - Kdy
- Navigační tlačítko 2 — **Jak** → Sekce 4 - Jak
- Navigační tlačítko 3 — **Bezpečnost** → Sekce 5 - Bezpečnost
- Navigační tlačítko 4 — **Dotazy** → Sekce 6 - Dotazy
- Navigační tlačítko 5 — **Pro média** → Sekce 7 - Pro média
- Tlačítko **Vyplnit záznam** → obrazovka 00_Homepage – Rozcestník
  - V případě, že je aktuální datum a čas v rozmezí odstávkových
    atributů `From` a `To` (tzn aktuálně běží odstávka), tak tlačítko
    bude **neaktivní**.

#### Hamburger Menu — pouze při mobilním zobrazení
*(replikuje stejnou navigaci + Vyplnit záznam tlačítko se stejnou
outage-aware logikou)*

#### Sekce 1 — Primární business cíl stránky
- Textová pozice 1 — Nadpis stránky
- Textová pozice 2 — Základní informace
- Textová pozice 3 — Doplňující informace
- Bannerová pozice 1
- Tlačítko **Vyplnit záznam** → obrazovka 00_Homepage – Rozcestník
  *(stejná outage-aware logika)*
- **Odstávka aplikace** — pozice (zobrazena pouze pokud běží/plánovaná):
  - **Plánovaná odstávka (žlutý box)** — zobrazena ve window
    `Warning_before_hours .. From` z konfiguračního souboru.
    Obsah: datum a čas (From) + datum a čas (To). Během plánované
    odstávky JE možné přejít na 00_Homepage – Rozcestník.
  - **Aktuální odstávka (červený box)** — zobrazena pokud aktuální
    datum mezi atributy `From` a `To`. Obsah: datum a čas (From) +
    datum a čas (To). Během aktuální odstávky NENÍ možné přejít
    na 00_Homepage – Rozcestník.
- Slider s key features aplikace (3 pozice)

#### Sekce 2 — Branding a garance
- Brand pozice 1 — Popis
- Brand pozice 2 — Logo ČKP
- Brand pozice 3 — Logo ČKP

#### Sekce 3 — Kdy
- Textová pozice 1 — Nadpis sekce
- Textová pozice 2 — Jednotlivé podmínky použití
- Tlačítko **Nejsem si jistý, kdy volat policii** — kliknutím se
  vyvolá popup s vysvětlením kdy volat policii. Popup obsahuje:
  - Tlačítko **Volat policii** (kliknutím lze začít volat na
    tel.číslo: **158**)
  - Tlačítko pro zavření okna `X`
  - Popup okno lze zavřít i kliknutím mimo popup okno.

---

## §1b. Vocabulary / Slovník — analytical doc §2.2

> Source: SUPIN-internal email transcript, supplied 2026-05-05. Verbatim
> Czech-locale glossary; calibrates the Excel `10_Glossary` sheet built
> from photo IMG_1028+IMG_1029 (analytical doc pages 11–12/133).

| Pojem / Zkratka | Popis |
|------------------|-------|
| PS | Pojistná smlouva |
| DN | Dopravní nehoda |
| SUPIN s.r.o. | Servisní IT organizace ČAP |
| DB | Databáze |
| WS | Web service (webové služby) |
| ČKP | Česká kancelář pojistitelů |
| RPO | Hodnota RPO (Recovery Point Objective) říká, ke kterému bodu z minulosti lze obnovit data, respektive udává maximální dobu výpadku, a tedy i ztráty dat |
| RTO | Hodnota RTO (Recovery Time Objective) vyjadřuje maximální dobu, za kterou by mělo dojít k zotavení po výpadku |
| MTPD | Maximální akceptovatelná doba výpadku |
| MTDL | Maximální akceptovatelná ztráta dat |
| IP | Internetový protokol (zkratka IP) je v internetu a počítačových sítích používajících rodinu protokolů TCP/IP základním protokolem síťové vrstvy poskytující datagramovou službu |
| HTTP | Hypertext Transfer Protocol je internetový protokol určený pro komunikaci s WWW servery. |
| DoS | Denial-of-service (DoS) (česky odepření služby) je typ útoku na internetové služby nebo stránky, jehož cílem je cílovou službu znefunkčnit a znepřístupnit ostatním účastníkům |
| UC | Případ užití |
| CSV | CSV (Comma-separated values, hodnoty oddělené čárkami) je jednoduchý souborový formát určený pro výměnu tabulkových dat. |
| XML | Extensible Markup Language - je obecný značkovací jazyk |
| XSD | XML Schema je jedno z XML schémat, jazyků pro popis XML |
| WAF | Web application firewall (WAF) chrání webové aplikace před různými aplikačními vrstvami |
| BE | Vrstva aplikace operující s daty |
| FE | Prezentační vrstva aplikace |
| SW | Programové vybavení |
| HW | Fyzicky existující technické vybavení |
| SOAP | Protokol pro výměnu zpráv založených na XML přes síť, hlavně pomocí HTTP. |
| REST | Protokol pro výměnu zpráv založených primárně na JSON přes síť, hlavně pomocí HTTP. |
| **Účastník** | Osoba, která vyplňuje hlášení o dopravní nehodě. |
| **Ověřený účastník** | Účastník nehody, který v hlášení nehody již ověřil své tel. číslo. |
| WCAG | Web Content Accessibility Guidelines (WCAG) jsou mezinárodní standardy, jejichž cílem je zajistit, aby webové aplikace a obsah byly přístupné pro co nejširší spektrum účastníků, včetně osob se zdravotním postižením. |
| MVP | Minimum Viable Product (minimální životaschopný produkt). Je to nejjednodušší verze produktu, která obsahuje pouze klíčové funkce nezbytné pro to, aby se dala ověřit jeho hodnota pro zákazníky a získat jejich zpětná vazba. |
| IZS | Integrovaný záchranný systém (Hasičský záchranný sbor, Policie, Zdravotnická záchranná služba) |

**Calibration vs Excel `10_Glossary` (rev 1) + analytical-doc §2.2 capture in `recon/ANALYTICAL-DOC-INTELLIGENCE-v0.1.md` §2:**

| Term | Excel says | Corpus says | Action |
|------|-----------|-------------|--------|
| Účastník | Osoba, která vyplňuje hlášení o dopravní nehodě. | identical | ✓ aligned |
| Ověřený účastník | …již ověřil své tel. číslo. | identical | ✓ aligned |
| SUPIN s.r.o. | Servisní IT organizace ČAP | identical | ✓ aligned |
| RPO / RTO | abbreviated definition | corpus has full sentence | **promote corpus text into Excel `item_descr_cs`** in next Excel rev |
| MTPD / MTDL | abbreviated | corpus has full | same — promote |
| WCAG | "international accessibility standards" | corpus full sentence | promote |
| MVP | "Minimum Viable Product" | corpus full sentence with rationale | promote |
| IZS | "Integrovaný záchranný systém — HZS, Policie, ZZS" | identical | ✓ aligned |

Action: in CP-SUPIN-03's first Excel iteration, refresh `10_Glossary`
rows for `RPO / RTO / MTPD / MTDL / WCAG / MVP` with the full corpus
sentences. Other 22 terms are aligned; no edit needed.

---

## §1c. Souhrn procesu a obecné vlastnosti — analytical doc §3.1 + §3.2

> Source: SUPIN-internal email transcript, supplied 2026-05-05 (text
> arrived twice in the email body — duplicate ignored; one inline-image
> CID `15d78934-35e4-4c4f-a40a-d7c7dc32ef54` referenced but not pasted —
> matches the 12-step process diagram on page 13/133 we already
> captured from photo IMG_1030). Calibrates
> `recon/ANALYTICAL-DOC-INTELLIGENCE-v0.1.md` §3 + §4.

### §1c.1 Cíl procesu

> Hlavním cílem a myšlenkou celého procesu je maximalizace automatizace
> vyplňování potřebných údajů, a tedy ulehčení a zvýšení rychlosti
> průchodu účastníků.

Koncept formuláře je rozdělen do **4 základních oblastí**:

#### Oblast A — Informovanost a ověření telefonních čísel účastníků
- (1) Edukace účastníka o situaci a za jakých okolností jakým způsobem
  postupovat.
- (2) Nutnost ověření telefonních čísel účastníků pomocí autorizačních
  SMS. Slouží také jako bezpečnostní aspekt.

#### Oblast B — Informace o účastnících a svědcích nehody
- (3) Nafocení OP účastníků, OCR vytěžení jejich údajů.
- (4) Automatické předvyplnění údajů a řidičském oprávnění.
- (5) Zaevidování svědků nehody.

#### Oblast C — Nafocení vozidel a popis okolností nehody
- (6) Nafocení nabouraných vozidel a definice jejich poškození.
- (7) Automatické OCR vytěžení SPZ a předvyplnění informací o
  vozidlech a pojišťovně každého vozidla/účastníka.
- (8) Určení a popis okolností nehody.
- (9) Automatické předvyplnění polohy, data a času nehody.
- (10) Určení viníka nehody.

#### Oblast D — Souhrn a podpis
- (11) Shrnutí a kontrola dat. Podpis hlášení nehody účastníky pomocí
  autorizačních SMS.
- (12) Odeslání výsledného hlášení v PDF na emaily účastníků a emaily
  jejich pojišťoven. Možnost stažení výsledného PDF do zařízení
  telefonu (pro nevyplňující účastníky přes QR kód).

### §1c.2 Obecné vlastnosti chování celé aplikace

- Aplikace funguje **pouze online** a není ji tedy možné využívat bez
  internetového připojení.
- V **MVP Fázi implementace aplikace (release 07/2025)** se počítá
  s workflow pro situaci **se dvěma účastníky** nehody. Celá
  implementace však již nyní počítá s **budoucí rozšiřitelností**,
  což umožní snadné přidání dalších pracovních postupů. Tyto mohou
  zahrnovat například situace s jedním účastníkem nebo scénáře
  s více než dvěma účastníky nehody.
- Validace polí se provádí **vždy při ztrátě focusu** na daném poli,
  případně **při kliku na tlačítko pro pokračování**.
- Všechna pole aplikace je možné **vyplnit manuálně** pro dokončení
  procesu — není tedy nutné fotit nehodu, doklad ani SPZ pro dokončení
  hlášení nehody.
- Po automatickém dotažení údajů je vždy možné veškerá pole **editovat**.
  Aplikace uchovává informaci o **zdroji údaje** (automatické dotažení
  / manuální vyplnění).
- Logika, vlastnosti a povinnosti jednotlivých polí formulářů jsou
  popsány v **definičním excelu zde** *(→ extracted into
  `fixtures/field-definitions.yaml`)*.
- Veškeré chování účastníků je zaznamenáváno pomocí nástroje **Google
  analytics**, popis zde.
- Veškeré chování účastníků je logováno v rámci **aplikačního logu**,
  detailní popis zde.
- Aplikace umožňuje **ověřenému účastníkovi**, kdykoliv během
  vyplňování záznamu o nehodě, zobrazit **QR kód** neboli **ID hlášení
  DN pro IZS**.
- Aplikace je realizována formou designu **pouze pro mobilní
  zobrazení**.
- **Podporované verze prohlížečů:**
  - Chromium based **od verze +121**
  - Safari **+16**
- Při využití **ZenId WebSDK** aplikace **neukládá OP účastníků na
  zařízení účastníka**.

### §1c.3 Cross-check vs existing recon

| Property | Corpus says | My recon says | Drift? |
|----------|-------------|---------------|:------:|
| 4 process areas | A / B / C / D matching analytical-doc-intelligence-v0.1.md §4 | identical (Areas A/B/C/D mapped to TT-CP-R1-A2/B/C/D) | ✓ none |
| 12 numbered process steps | 1..12 | identical (FLW-003 STEPs 1..24 expand each) | ✓ none |
| MVP release | **07/2025** | not previously captured | ✦ NEW: confirms release date is **July 2025** — analytical doc was written for that target; field-definitions.yaml is canonical for the v1 workflow |
| MVP scope | 2-driver workflow | identical | ✓ aligned (R1 covers exactly this; 1-driver and 3+-driver are R3+ extensibility) |
| Validation timing | blur + continue-click | identical | ✓ aligned (L-ARCH per LESSONS-LEARNED §3) |
| Manual fallback | every field optional-photo | identical | ✓ aligned |
| Source-of-data tracking | auto-fill vs manual | identical (per F-NNN.notes — "data_source" annotation) | ✓ aligned |
| Mobile-only | "pouze pro mobilní zobrazení" | identical (L-ARCH-4 in lessons learned) | ✓ aligned |
| Browser support | Chromium ≥ 121 + Safari ≥ 16 | identical | ✓ aligned |
| zenID privacy posture | "neukládá OP účastníků na zařízení účastníka" | identical | ✓ aligned (INT-006 zenID WebSDK recon) |
| GA + app-log behaviour | both active | identical (INT-010 GA recon) | ✓ aligned |
| QR for IZS | "ověřený účastník may toggle QR" | identical (TC-CP-015 acceptance addendum from coverage gap) | ✓ aligned |
| Definiční excel referenced | "zde" (link in source) | extracted to fixtures/field-definitions.yaml v0.1 | ✓ aligned |

**One new fact**: **MVP release date = July 2025**. Add to the project
context as `_specs/RELEASE-CONTEXT.md` or similar in CP-SUPIN-03; the
sub-text is that the analytical doc was authored ~mid-2025 for that
release and our test campaign therefore is aligned with the
post-launch tst.* baseline (not pre-launch).

---

## §2. Cross-check vs existing recon

| Label | Corpus says | `recon/screens/SCR-001.md` says | Drift? |
|-------|-------------|--------------------------------|:------:|
| Nav buttons CS | "Kdy / Jak / Bezpečnost / Dotazy / Pro média" | identical | ✓ none |
| Primary CTA | "VYPLNIT ZÁZNAM" (uppercase in UI; "Vyplnit záznam" in doc body) | identical | ✓ none |
| Outage attributes | `From`, `To`, `Warning_before_hours` | identical (from `recon/integrations/INT-009-azure-blob.md`) | ✓ none |
| Outage box colours | žlutý (planned) / červený (active) | identical | ✓ none |
| Police-call button label | "Nejsem si jistý, kdy volat policii" | identical | ✓ none |
| Police-call popup tel-uri | `tel:158` | identical (from FLW-002) | ✓ none |
| Logo ČKP | with diacritic | inconsistent in source: "Logo CKP" in nav reference; "Logo ČKP" in branding section | ⚠ source-side typo — corpus normalises to ČKP everywhere |

**Result:** SCR-001 and the integration recons are correctly aligned.
No SCR-NNN edits needed. This corpus simply confirms it.

## §3. How tests should consume this corpus

### §3.1 As regex assertion source

Per `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` §3.7, the `expected:` field
of an assertion step can reference an entry here:

```yaml
- id: TC-CP-001-S-09
  kind: assertion
  expected: |
    page.getByRole('heading').first() innerText matches /Bouračka/i
    AND
    a primary CTA exists with normalised text contained in
    [recon/cs-locale-reference/CALIBRATION-CORPUS-v0.1.md §1.2 → "Vyplnit záznam"]
```

The framework code dereferences the corpus reference at test build time
to a literal — the assertion code only knows the resolved literal,
the spec MD records the canonical link.

### §3.2 As fuzzy-match guard for content-regression smoke

For TT-CP-R2-LANDING (R2 deferred), the smoke-test pattern uses the
corpus's section-1 strings as a "must-be-present" set:

```js
const required = [
  "Vyplnit záznam",
  "Nejsem si jistý, kdy volat policii",
  "Odstávka aplikace",     // appears only when outage; skip if absent
  "Logo ČKP",
];
for (const s of required) expect(pageText).toContain(s);
```

### §3.3 As EN-translation source

When a colleague needs to author the English mirror of a TC name or
SPEC title, they use this corpus's CS string as the English-translation
input — never their memory of what they thought the SUT said.

## §4. Append guide for future email transcripts

When new SUPIN-internal email text arrives:

1. Append a new top-level section here
   (`§N. <screen / topic> — <source>`).
2. Quote-block the verbatim CS source (with original punctuation,
   diacritics, casing).
3. Run a quick cross-check vs the corresponding SCR-NNN / FLW-NNN /
   INT-NNN file; record any drift in §2-style table.
4. If drift is found, edit the SCR/FLW/INT — the corpus is ground
   truth.

## §5. Status

| Item | Value |
|------|-------|
| Document | `recon/cs-locale-reference/CALIBRATION-CORPUS-v0.1.md` |
| Sections corpus-captured | 3 (LandingPage §3.3.2.1 + Slovník §2.2 + Souhrn procesu §3.1+§3.2) |
| Terms catalogued (slovník) | 28 |
| Process areas catalogued | 4 (A/B/C/D) + 12 numbered steps + 12 general-behaviour properties |
| Cross-checks performed | 7 LandingPage strings + 28 glossary terms + 13 process+behaviour properties |
| New facts surfaced | MVP release date = **07/2025** (not previously captured) |
| Drift found | 0 critical; 6 Excel glossary rows to refresh with full corpus text in next rev |
| Source format | Email transcripts (long-text replies from SUPIN colleagues) |
| Confidentiality | OK to commit — content matches publicly-derivable analytical-doc structure |
| Status | v0.1 — append-only as new transcripts arrive |
