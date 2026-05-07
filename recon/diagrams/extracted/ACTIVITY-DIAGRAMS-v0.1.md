# Bouračka — Activity Diagrams (extracted from `SUPIN_DEMO_Bouracka`)

> **Source.** 30 photos `IMG_1067..IMG_1096` placed by user in
> `analyticke vstupy/proto-activity diag sources/`. The source file is
> a draw.io / diagrams.net workbook titled `SUPIN_DEMO_Bouracka` (the
> `DEMO` is the file name; diagrams cover the whole wizard, not the
> tst.demo env).
>
> **What's in the source.** 18 swimlane activity diagrams (one per
> screen `D00 .. D17`), each split into `Uživatel | Systém` lanes,
> with decision diamonds at every branch. The proto-diagrams are not
> strictly UML 2.5-compliant — no fork/join bars, decision diamonds
> labelled with question text rather than guard expressions, no
> activity partitions per integration — but the structure is regular
> enough to convert mechanically into proper Mermaid `flowchart` form
> and (optionally) PlantUML.
>
> **Why this matters for tests.** Every decision diamond is a
> branch the test suite must cover. This document is the
> **completeness reference** for `02_TestCases` — the cross-check in
> `recon/COVERAGE-GAP-ANALYSIS.md` (sibling file) lists branches not
> yet wired to a TC.

---

## §0. Conventions used in the Mermaid blocks below

```
[ User node ]                  oval     fill #FFF2CC
( System node )                rounded  fill #BDD7EE
{ Decision diamond }           rhombus  fill #F4B084
(( Start / Screen entry ))     stadium  fill #1F4E79 (white text)
[[ Integration touchpoint ]]   subroutine
  - prefixed with INT-NNN code from recon/integrations/
```

CS labels preserved verbatim from the source diagrams; system actions
abbreviated where the source spilled across multiple boxes.

---

## §1. D00 — Homepage / Rozcestník

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D00_Homepage – Rozcestník<br/>zobrazí se po vstupu"]):::entry
    INT_GA[["INT-010 Google Analytics — iniciace"]]:::integ
    INT_RC[["INT-001 reCaptcha — iniciace"]]:::integ
    INT_OUT[["INT-009 Azure Blob — outage config check"]]:::integ
    SO{Outage active?}:::dec
    SOY(Aktuální odstávka — CTA disabled):::sys
    U1[Uživatel klikne na <b>VYPLNIT ZÁZNAM</b>]:::user
    Snext(Přesměrování na D01):::sys

    S0 --> INT_GA --> INT_RC --> INT_OUT --> SO
    SO -- ANO --> SOY
    SO -- NE --> U1 --> Snext --> END([→ D01_Potvrzení účastníků nehody])
```

**Branches → TCs:**
- happy path → TC-CP-001 (PING already at D01 step; D00 is pre-step)
- outage active → TC-CP-019

---

## §2. D01 — Potvrzení účastníků nehody

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D01_Potvrzení účastníků nehody"]):::entry
    U1[Uživatel klikne na <b>ROZUMÍM</b>]:::user
    INT_PING[["INT-002 SMS Gateway — PING"]]:::integ
    DPing{PING OK?}:::dec
    SE(ERROR Endpage<br/>SMS service nedostupná):::sys
    SDB(Aplikace založí ID hlášení<br/>accidentReportStatus = NEW<br/>uloží počet účastníků = 2):::sys
    SN(Přesměrování na D02):::sys

    S0 --> U1 --> INT_PING --> DPing
    DPing -- NE --> SE --> SBack([Návrat na D00])
    DPing -- ANO --> SDB --> SN --> END([→ D02_Ověření telefonních čísel])
```

**Branches → TCs:** PING-OK = TC-CP-001 · PING-NOK = TC-CP-002

---

## §3. D02 — Ověření telefonních čísel

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D02_Ověření telefonních čísel"]):::entry
    U1[Uživatel zadá tel. číslo<br/>příslušného účastníka]:::user
    SVal(Systém zvaliduje<br/>zadané tel. číslo):::sys
    DOK{Číslo OK?}:::dec
    SBad(Inline error pod polem<br/>oprav vstup):::sys
    U2[Uživatel potvrdí check-box<br/>seznámil se ZOÚ]:::user
    DConsent{Potvrzeno?}:::dec
    U3[Uživatel klikne <b>ODESLAT KÓD</b>]:::user
    INT_SMS_OUT[["INT-002 SMS Gateway — issue OTP"]]:::integ
    DSmsOk{HTTP 422<br/>EX_CHYBA?}:::dec
    SInline(Inline error o nevalidním čísle<br/>zkontroluj limit zmíceních čísla):::sys
    SOTP(Systém zobrazí pole<br/>pro vložení kódu):::sys
    U4[Uživatel vyplní kód<br/>klikne <b>OVĚŘIT</b>]:::user
    INT_SMS_VAL[["INT-002 SMS Gateway — validate OTP"]]:::integ
    DOtpOk{Kód platný?}:::dec
    DAttempts{Pokusů > limit?}:::dec
    SError(ERROR Endpage<br/>accidentReportStatus = ERROR<br/>SMS_CODE_ATTEMPTS):::sys
    DRecaptcha{reCaptcha OK?}:::dec
    SDBPhone(Aplikace uloží tel. číslo do DB):::sys
    INT_DB_FREQ[["DB security — frequency check<br/>TELEPHONE_NUMBER_COUNT"]]:::integ
    DFreq{Číslo příliš často<br/>v DB?}:::dec
    SErrFreq(ERROR Endpage<br/>TELEPHONE_NUMBER_COUNT):::sys
    DMore{Další účastník<br/>k ověření?}:::dec
    SLoop(Smyčka pro účastníka N):::sys
    SQR(Systém vygeneruje QR kód<br/>+ Identifikační kód pro IZS<br/>accidentReportStatus = IN_PROGRESS_DRIVERS):::sys
    SN(Přesměrování na D03):::sys

    S0 --> U1 --> SVal --> DOK
    DOK -- NE --> SBad --> U1
    DOK -- ANO --> U2 --> DConsent
    DConsent -- NE --> U2
    DConsent -- ANO --> U3 --> INT_SMS_OUT --> DSmsOk
    DSmsOk -- ANO --> SInline --> U1
    DSmsOk -- NE --> SOTP --> U4 --> INT_SMS_VAL --> DRecaptcha
    DRecaptcha -- NE --> SInline
    DRecaptcha -- ANO --> DOtpOk
    DOtpOk -- NE --> DAttempts
    DAttempts -- ANO --> SError --> SBack([Konec])
    DAttempts -- NE --> SOTP
    DOtpOk -- ANO --> SDBPhone --> INT_DB_FREQ --> DFreq
    DFreq -- ANO --> SErrFreq --> SBack
    DFreq -- NE --> DMore
    DMore -- ANO --> SLoop --> U1
    DMore -- NE --> SQR --> SN --> END([→ D03_Nafocení OP])
```

**Branches → TCs:** happy = TC-CP-003 · OTP retry = TC-CP-007 · attempts exhausted = TC-CP-004 · TELEPHONE_NUMBER_COUNT = TC-CP-005 · HTTP 422 EX_CHYBA = TC-CP-006

---

## §4. D03 — Nafocení OP a Osobní údaje – účastník A

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D03_Nafocení OP a Osobní údaje – účastník A"]):::entry
    U1[Uživatel zvolí způsob<br/>nahrání OP]:::user
    DMode{Vyfotit nebo<br/>z galerie?}:::dec
    INT_WS[["INT-006 zenID WebSDK — kamera"]]:::integ
    DCam{Kamera povolena?}:::dec
    SCamErr(Chybová hláška<br/>Přístup k fotoaparátu zamítnut):::sys
    U2[Uživatel nahraje<br/>obě strany OP]:::user
    SDoubleSide(Systém ověří<br/>obě strany):::sys
    DBoth{Obě strany?}:::dec
    SAsk(Vyzve k doplnění):::sys
    INT_OCR[["INT-007 zenID API — OCR vytěžení"]]:::integ
    DOCR{OCR výsledek}:::dec
    SOK(OK / WARNING<br/>uloží data + fotky<br/>zamezí re-vytěžení):::sys
    SNok(NOK<br/>editing mode na D04):::sys
    U3[Uživatel klikne<br/>nemůže pořídit fotografie]:::user
    DMore{Další účastník<br/>nemá doklady?}:::dec
    SD05(Přesměrování na D05):::sys
    SD04(Přesměrování na D04):::sys

    S0 --> U1 --> DMode
    DMode -- vyfotit --> INT_WS --> DCam
    DCam -- NE --> SCamErr --> U1
    DCam -- ANO --> U2
    DMode -- galerie --> U2
    U2 --> SDoubleSide --> DBoth
    DBoth -- NE --> SAsk --> U2
    DBoth -- ANO --> INT_OCR --> DOCR
    DOCR -- OK/WARNING --> SOK --> DMore
    DOCR -- NOK --> SNok --> SD04
    U3 --> DMore
    DMore -- ANO --> SD05 --> END1([→ D05])
    DMore -- NE --> SD04 --> END2([→ D04])
```

**Branches → TCs:** happy zenID = TC-CP-008 · zenID NOK manual = TC-CP-009 · camera-denied = TC-CP-011

---

## §5. D04 — Osobní údaje – účastník A

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D04_Osobní údaje – účastník A"]):::entry
    DOCRprev{OCR předchozí výsledek}:::dec
    INT_AISPOV[["INT-004 AISPOV — driver-lookup<br/>(ROB + CRR)"]]:::integ
    DAispov{StatusVysledek}:::dec
    SOK(Form pre-filled<br/>uživatel může editovat):::sys
    SNFound(Form pre-filled částečně<br/>editing mode):::sys
    SEmpty(Empty editing mode<br/>NO further AISPOV calls):::sys
    U1[Uživatel klikne<br/>UPRAVIT]:::user
    U2[Uživatel upraví<br/>předvyplněné údaje]:::user
    U3[Uživatel vyplní e-mail<br/>+ ručně chybějící údaje]:::user
    INT_RUIAN[["INT-008 RUIAN — autocomplete"]]:::integ
    U4[Uživatel klikne<br/>NAČÍST z REGISTRU<br/>opt-in re-call AISPOV]:::user
    INT_AISPOV2[["INT-004 AISPOV — manual lookup<br/>limited per config"]]:::integ
    U5[Uživatel klikne ULOŽIT]:::user
    DMore{Další účastník?}:::dec
    SD05(Přesměrování na D05):::sys
    SD07(Přesměrování na D07):::sys

    S0 --> DOCRprev
    DOCRprev -- OK/WARNING --> INT_AISPOV --> DAispov
    DOCRprev -- NOK --> SEmpty
    DAispov -- OK --> SOK --> U1
    DAispov -- NENALEZENO ROB --> SNFound --> U2
    DAispov -- ERROR --> SEmpty
    SOK --> U2
    SEmpty --> U3
    SNFound --> U3
    U2 --> U3
    U3 --> INT_RUIAN
    INT_RUIAN --> U4
    U4 --> INT_AISPOV2 --> U5
    U3 --> U5
    U5 --> DMore
    DMore -- ANO --> SD05 --> END1([→ D05])
    DMore -- NE --> SD07 --> END2([→ D07_Svědci nehody])
```

**Branches → TCs:** AISPOV OK = TC-CP-008 · AISPOV NENALEZENO ROB = TC-CP-010 · manual + button = TC-CP-009

---

## §6. D05 — Nafocení OP – účastník N · §7. D06 — Osobní údaje – účastník N

**Identical flow to D03 + D04 respectively, but for participant N.**
The "no further AISPOV calls" branch from D04 is honoured — if the
first participant's AISPOV came back empty, D06 jumps straight to
empty editing mode without re-calling AISPOV.

Mermaid diagrams omitted (copy D03 / D04 with `účastník A → účastník N`).

**Branches → TCs:** all subsumed under TC-CP-008/009/010 — one execution per participant slot.

---

## §8. D07 — Svědci nehody

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF

    S0(["D07_Svědci nehody"]):::entry
    DAdd{Přidat svědka?}:::dec
    U1[Uživatel klikne<br/>PŘIDAT SVĚDKA NEHODY]:::user
    U2[Uživatel vyplní<br/>jméno, příjmení, telefon]:::user
    DPas{Spolujezdec?}:::dec
    U3[Uživatel zvolí<br/>k jakému účastníkovi patří]:::user
    DMax{Svědků <= 3?}:::dec
    U4[Uživatel klikne<br/>POKRAČOVAT BEZ SVĚDKŮ<br/>nebo POKRAČOVAT]:::user
    SDB(DB save: 'Svědci nebyli vyplněni' OR svědci<br/>accidentReportStatus = IN_PROGRESS_VEHICLES):::sys
    SD08(Přesměrování na D08):::sys

    S0 --> DAdd
    DAdd -- ANO --> U1 --> U2 --> DPas
    DPas -- ANO --> U3 --> DMax
    DPas -- NE --> DMax
    DMax -- limit --> DAdd
    DMax -- under --> DAdd
    DAdd -- NE --> U4 --> SDB --> SD08 --> END([→ D08])
```

**Branches → TCs:** R2 (TT-CP-R2-WITNESS) — not in current R1 envelope.

---

## §9. D08 — Nafocení nehody + SPZ – informace o vozidle A

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D08_Nafocení nehody + SPZ — vozidlo A"]):::entry
    DSkip{Pokračovat<br/>bez fotografií?}:::dec
    DGal{Nahrát SPZ z galerie?}:::dec
    DCam{Vyfotit SPZ<br/>WebSDK?}:::dec
    INT_WS_SPZ[["INT-006 zenID WebSDK — SPZ"]]:::integ
    INT_API_SPZ[["INT-007 zenID API — SPZ"]]:::integ
    SPopupSPZ(Popup: Souhlasí načtená SPZ?):::sys
    DConfirm{Uživatel potvrdí?}:::dec
    SLoadOk(Aplikace uloží SPZ + fotku<br/>zamezí re-upload SPZ):::sys
    SLoadFail(Notifikace: SPZ nerozpoznána):::sys
    U1[Uživatel pokračuje<br/>v nahrávání fotek poškození]:::user
    U2[Uživatel označí<br/>poškozené části vozidla]:::user
    DDmg{Vozidlo<br/>poškozeno?}:::dec
    SUncheck(Vyresetuje předchozí značky):::sys
    SDmgErr(Chyba: musíš označit nebo zaškrtnout 'nepoškozeno'):::sys
    U3[Uživatel označí<br/>jak se vozidlo pohybovalo]:::user
    U4[Uživatel klikne POKRAČOVAT]:::user
    SDB(Uloží data + fotky k ID hlášení):::sys
    SD09(Přesměrování na D09):::sys

    S0 --> DSkip
    DSkip -- ANO --> U1
    DSkip -- NE --> DGal
    DGal -- ANO --> INT_API_SPZ --> SPopupSPZ
    DGal -- NE --> DCam
    DCam -- ANO --> INT_WS_SPZ --> SPopupSPZ
    SPopupSPZ --> DConfirm
    DConfirm -- ANO --> SLoadOk --> U1
    DConfirm -- NE --> SLoadFail --> DGal
    U1 --> U2 --> DDmg
    DDmg -- vozidlo nepoškozeno --> SUncheck --> U3
    DDmg -- označeno --> U3
    DDmg -- nic --> SDmgErr --> U2
    U3 --> U4 --> SDB --> SD09 --> END([→ D09_Údaje o vozidle A])
```

**Branches → TCs:** SPZ happy = TC-CP-012 · SPZ gallery fallback = TC-CP-013

---

## §10. D09 — Údaje o vozidle - vozidlo A

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D09_Údaje o vozidle - vozidlo A"]):::entry
    DSPZok{SPZ potvrzená<br/>+ AISPOV povoleno?}:::dec
    INT_AV[["INT-004 AISPOV — vehicle + insurance lookup"]]:::integ
    DAvOk{AISPOV výsledek}:::dec
    SOK(Form pre-filled):::sys
    SPart(Form pre-filled částečně<br/>bez Číslo smlouvy + Zelená karta):::sys
    SEmpty(Empty editing mode):::sys
    U1[Uživatel klikne<br/>UPRAVIT]:::user
    DChangeIns{Změnit Pojišťovnu?}:::dec
    SHide(Skryj Číslo smlouvy<br/>+ Zelená karta):::sys
    U2[Uživatel POTVRDÍ]:::user
    DMore{Další vozidlo?}:::dec
    SD10(Přesměrování na D10):::sys
    SDBSave(Uloží data + accidentReportStatus = IN_PROGRESS_CIRCUMSTANCES):::sys
    SD12(Přesměrování na D12_Okolnosti):::sys

    S0 --> DSPZok
    DSPZok -- ANO --> INT_AV --> DAvOk
    DSPZok -- NE --> SEmpty
    DAvOk -- OK --> SOK --> U1
    DAvOk -- partial/error --> SPart --> U1
    DAvOk -- "no contract data" --> SHide --> U1
    SEmpty --> U1
    U1 --> DChangeIns
    DChangeIns -- ANO --> SHide --> U1
    DChangeIns -- NE --> U2
    U2 --> DMore
    DMore -- ANO --> SD10 --> END1([→ D10])
    DMore -- NE --> SDBSave --> SD12 --> END2([→ D12])
```

**Branches → TCs:** vehicle happy = TC-CP-012 · vehicle missing = TC-CP-014

---

## §11. D10 / D11 — Vehicle / vehicle data for participant N

Same shape as D08 + D09 for participant N's vehicle. R2-deferred
(TT-CP-R2-VEHICLE-N) but exercised by TC-CP-018 E2E orchestration.

---

## §12. D12 — Okolnosti nehody

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF

    S0(["D12_Okolnosti nehody"]):::entry
    U1[Uživatel zvolí jednu z možností<br/>jak se nehoda stala]:::user
    DSwap{Změnit pořadí<br/>vozidel na obrázku?}:::dec
    U2[Uživatel klikne<br/>ZMĚNIT POŘADÍ]:::user
    SShow(Systém zobrazí obrázky<br/>s prohozeným pořadím):::sys
    DOk{Vyhovuje?}:::dec
    U3[Uživatel vyplní<br/>slovní popis nehody]:::user
    U4[Uživatel klikne POKRAČOVAT]:::user
    SD13(Přesměrování na D13):::sys

    S0 --> U1 --> DSwap
    DSwap -- ANO --> U2 --> SShow --> DOk
    DOk -- ANO --> U3
    DOk -- NE --> U2
    DSwap -- NE --> U3 --> U4 --> SD13 --> END([→ D13_Datum, čas a místo nehody])
```

---

## §13. D13 — Datum, čas a místo nehody

(Pattern: GPS or manual address; map vs RUIAN autocomplete; two
date-pickers; continue → D14.)

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D13_Datum, čas a místo nehody"]):::entry
    U1[Uživatel zvolí datum + čas<br/>defaultně předvyplněno]:::user
    DGPS{GPS nebo<br/>manuálně?}:::dec
    INT_GM[["INT-005 Google Maps — geolocation"]]:::integ
    INT_R[["INT-008 RUIAN — autocomplete"]]:::integ
    U2[Uživatel zadá adresu<br/>našeptávač]:::user
    U3[Uživatel klikne POKRAČOVAT]:::user
    SD14(Přesměrování na D14):::sys

    S0 --> U1 --> DGPS
    DGPS -- GPS --> INT_GM --> U3
    DGPS -- adresa --> INT_R --> U2 --> U3
    U3 --> SD14 --> END([→ D14_Určení viníka nehody])
```

---

## §14. D14 — Určení viníka nehody

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF

    S0(["D14_Určení viníka nehody"]):::entry
    U1[Uživatel zvolí viníka nehody<br/>radio: účastník A, N, žádný, neurčeno]:::user
    U2[Uživatel klikne POKRAČOVAT]:::user
    SD15(Přesměrování na D15):::sys

    S0 --> U1 --> U2 --> SD15 --> END([→ D15_Souhrn])
```

---

## §15. D15 — Souhrn a potvrzení zadaných údajů

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF

    S0(["D15_Souhrn a potvrzení zadaných údajů"]):::entry
    DSign{Podepsat záznam o nehodě?}:::dec
    DShare{Načíst sdílený záznam?}:::dec
    U1[Uživatel zaškrtne checkbox<br/>potvrzuji pravdivost informací]:::user
    U2[Uživatel načte sdílený záznam<br/>prostřednictvím QR kódu]:::user
    SShared(Systém zaeviduje<br/>že došlo k načtení sdíleného záznamu):::sys
    DChanged{Došlo od doby načtení k úpravě?}:::dec
    SRegen(Systém přegeneruje QR kód<br/>chybová hláška o znovu-načtení):::sys
    U3[Uživatel klikne<br/>PODEPSAT ZÁZNAM O NEHODĚ]:::user
    SD16(Přesměrování na D16):::sys

    S0 --> DSign
    DSign -- NE --> DShare
    DShare -- NE --> SBack([Vrátí se na editaci])
    DShare -- ANO --> U2 --> SShared --> DChanged
    DChanged -- ANO --> SRegen --> U2
    DChanged -- NE --> U1
    DSign -- ANO --> U1 --> U3 --> SD16 --> END([→ D16_Podpis])
```

**Branches → TCs:** sign = TC-CP-015 · shared-record = TT-CP-R2-SHARED · re-edit reset = R2

---

## §16. D16 — Podpis účastníků pomocí SMS

(Mirrors D02 phone-OTP flow but for the *sign* step. Same retry logic,
same exhaustion → ERROR, but with different sub-reason `SIGN_OTP_ATTEMPTS`.)

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D16_Podpis účastníků pomocí SMS"]):::entry
    INT_SMS[["INT-002 SMS Gateway — sign-OTP issue"]]:::integ
    U1[Uživatel A vyplní<br/>autorizační kód]:::user
    INT_VAL[["INT-002 SMS Gateway — validate"]]:::integ
    DOK{Kód platný?}:::dec
    DAttempts{Pokusů > limit?}:::dec
    SError(ERROR<br/>SIGN_OTP_ATTEMPTS):::sys
    SDateA(Ulož datum a čas podpisu A):::sys
    DMore{Účastník N<br/>má podepsat?}:::dec
    SLoop(Smyčka pro účastníka N):::sys
    SAllSigned(Všichni podepsali<br/>accidentReportStatus = TO_SIGN → FINISHED):::sys
    SD17(Přesměrování na D17):::sys

    S0 --> INT_SMS --> U1 --> INT_VAL --> DOK
    DOK -- NE --> DAttempts
    DAttempts -- ANO --> SError --> SBack([Konec])
    DAttempts -- NE --> U1
    DOK -- ANO --> SDateA --> DMore
    DMore -- ANO --> SLoop --> U1
    DMore -- NE --> SAllSigned --> SD17 --> END([→ D17])
```

**Branches → TCs:** happy = TC-CP-015 · exhaustion = TC-CP-016 · timeout retry = TC-CP-017

---

## §17. D17 — Potvrzení a odeslání na email

```mermaid
flowchart TB
    classDef user fill:#FFF2CC,stroke:#1F4E79,color:#1F4E79
    classDef sys  fill:#BDD7EE,stroke:#1F4E79,color:#1F4E79
    classDef dec  fill:#F4B084,stroke:#C00000,color:#1F4E79
    classDef entry fill:#1F4E79,stroke:#1F4E79,color:#FFFFFF
    classDef integ fill:#C6E0B4,stroke:#1F4E79,color:#1F4E79

    S0(["D17_Potvrzení a odeslání na email"]):::entry
    INT_PDF[["Systém vygeneruje PDF<br/>s QR + Identifikační kód"]]:::integ
    INT_SMTP[["INT-003 SMTP — dispatch dvěma řidičům + pojišťovnám"]]:::integ
    DDownload{Stáhnout PDF<br/>do vlastního zařízení?}:::dec
    U1[Uživatel klikne STÁHNOUT PDF ZÁZNAM]:::user
    DScan{Stáhnout PDF<br/>prostřednictvím QR?}:::dec
    U2[Uživatel naskenuje QR kód<br/>z jiného zařízení]:::user
    DCall{Zavolat asistenční službu pojišťovny?}:::dec
    SAssist(Systém zobrazí tlačítko VOLAT<br/>pro pojišťovnu řidiče):::sys
    U3[Uživatel klikne VOLAT]:::user
    DBack{Přejít na hlavní obrazovku?}:::dec
    U4[Uživatel klikne PŘEJÍT NA HLAVNÍ OBRAZOVKU]:::user
    SD00(Přesměrování na D00):::sys

    S0 --> INT_PDF --> INT_SMTP --> DDownload
    DDownload -- ANO --> U1 --> DScan
    DDownload -- NE --> DScan
    DScan -- ANO --> U2 --> DCall
    DScan -- NE --> DCall
    DCall -- ANO --> SAssist --> U3 --> DBack
    DCall -- NE --> DBack
    DBack -- ANO --> U4 --> SD00 --> END([→ D00 zpět])
    DBack -- NE --> SStay(Stane na D17)
```

**Branches → TCs:** PDF dispatch = TC-CP-015 happy continuation · all post-sign branches = R2 (TT-CP-R2-SHARED)

---

## §18. Cross-cutting flows

These appear inline in multiple D-screens rather than as standalone
diagrams:

| Flow | Where it appears | Mapped to TC |
|------|------------------|--------------|
| Outage active (red box, CTA disabled) | D00 | TC-CP-019 |
| Outage warning (yellow box) | D00 | R2 (TT-CP-R2-OUTAGE-WARN) |
| Cookie banner (first visit) | D00 + LandingPage | R2 (TT-CP-R2-COOKIE) |
| Sdílený záznam (link/QR for participant N) | D15, D16 | R2 (TT-CP-R2-SHARED) |
| In-app sidebar Menu navigation + Začít znovu confirmation | every D-screen | R2 (TT-CP-R2-MENU) |
| Mid-wizard police-call self-disclosure (interlock fires) | D12 / D14 | TC-CP-020 |

---

## §19. Coverage check (extracted from §1–§17 + §18)

Every decision diamond in every diagram is a branch the test suite
must cover. Cross-check against `02_TestCases` lives in
`recon/COVERAGE-GAP-ANALYSIS.md` (sibling). Summary:

| Branch class | Diagram | Mapped TC | R-coverage |
|--------------|---------|-----------|:----------:|
| Outage check | D00 | TC-CP-019 | R1 |
| PING gate | D01 | TC-CP-001 / 002 | R1 |
| Phone validation | D02 | TC-CP-003 / 004 / 005 / 006 / 007 | R1 |
| OP camera vs gallery | D03 / D05 | TC-CP-008 / 009 / 011 | R1 |
| zenID OCR outcome | D03 / D05 | TC-CP-008 / 009 | R1 |
| AISPOV ROB outcome | D04 / D06 | TC-CP-008 / 009 / 010 | R1 |
| Witness add | D07 | (R2 TT-CP-R2-WITNESS) | R2 |
| SPZ camera vs gallery | D08 / D10 | TC-CP-012 / 013 | R1 |
| AISPOV vehicle outcome | D09 / D11 | TC-CP-012 / 014 | R1 |
| Damage marking | D08 / D10 | TC-CP-012 (sub-step) | R1 |
| Vehicle order swap | D12 | NOT YET COVERED | **gap** → TC-CP-021 cand. |
| GPS vs address | D13 | TC-CP-018 (E2E) only | gap → TC-CP-022 cand. |
| Fault attribution | D14 | TC-CP-018 (E2E) only | gap → TC-CP-023 cand. |
| Confirmation checkbox | D15 | TC-CP-015 | R1 |
| Shared-record load | D15 | (R2 TT-CP-R2-SHARED) | R2 |
| SMS sign retry | D16 | TC-CP-016 / 017 | R1 |
| PDF dispatch | D17 | TC-CP-015 | R1 |
| QR scan / asistence call / hlavní obrazovka | D17 | (post-FINISHED — R2) | R2 |

**Gaps surfaced for CP-SUPIN-03 to address:**
- TC-CP-021 — D12 vehicle-order-swap branch
- TC-CP-022 — D13 GPS vs manual-address branch (currently only inside E2E)
- TC-CP-023 — D14 fault-attribution radio (currently only inside E2E)

These three become the **first new TCs in the next iteration** —
already declarable in Excel even before the SPECs are authored.

---

## §20. Status

| Item | Value |
|------|-------|
| Document | `recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md` |
| Source | 30 photos `IMG_1067..IMG_1096` of `SUPIN_DEMO_Bouracka` draw.io workbook |
| Diagrams extracted | 18 swimlanes (D00..D17) + 6 cross-cutting flows |
| Format | Mermaid `flowchart TB` (renders in any Markdown viewer with Mermaid support; GitHub, VS Code, MkDocs all OK) |
| Coverage gaps surfaced | 3 (TC-CP-021..023 candidates) |
| Coverage report | `recon/COVERAGE-GAP-ANALYSIS.md` (next file) |
| Status | v0.1 — review + use for TC revision in CP-SUPIN-03 |
