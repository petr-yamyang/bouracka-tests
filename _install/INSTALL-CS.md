# Instalační průvodce — bouracka-tests automatizace v0.1.0 — CS

> **Pro koho.** SecOps (firewall + politiky) a SecDev (vlastní instalace
> na notebook). Příručka je úmyslně samostatná — dokáže provést celou
> instalaci od čistého notebooku po zelený smoke test bez odkazů na
> jiné dokumenty.
>
> **Cíl notebooku.** HP EliteBook G11-class, Windows 11 Enterprise
> 25H2, doménově-připojený do `int-ckp.cz`, **bez admin práv** pro
> uživatele.
>
> **Doba instalace** na zdravém notebooku: cca 8–12 minut.

---

## §1. Předpoklady (SecOps zařídí předem)

### §1.1 Síťový allowlist

Pro instalaci (jednorázově) povolte HTTPS odchozí spojení na tyto
hostitele z notebooků <test-runner-host>/002/003:

| Host | Účel | Port |
|------|------|------|
| `nodejs.org` | Node.js installer (jednorázově) | 443 |
| `registry.npmjs.org` | npm balíčky | 443 |
| `cdn.playwright.dev` | Playwright Chromium binárka | 443 |
| `playwright.azureedge.net` | Playwright CDN (legacy) | 443 |
| `playwright.download.prss.microsoft.com` | Playwright CDN (Microsoft) | 443 |
| `github.com` | někteří npm balíčky publikují tarbally na GH | 443 |
| `objects.githubusercontent.com` | totéž | 443 |

Pro **provoz** (trvale) navíc povolte:

| Host | Účel |
|------|------|
| `tst.bouracka.cz`, `tst.demo.bouracka.cz` | testovací prostředí |
| `*.supin.cz`, `*.ckp.cz` | CDN + integrace |
| `www.google.com/recaptcha/*` + `www.gstatic.com/recaptcha/*` | reCAPTCHA |

### §1.2 Politika pro AppLocker / WDAC

Pokud má notebook deny-by-default AppLocker, přidejte tato pravidla
(ve výchozím stavu obvykle stačí path-based publisher whitelist):

- `%LOCALAPPDATA%\nodejs\*` → publisher `OpenJS Foundation`
- `%LOCALAPPDATA%\ms-playwright\*` → publisher `Microsoft Corporation`

### §1.3 Defender vyloučení (doporučeno)

Antivirus by jinak skenoval ~30 000 drobných souborů v `node_modules\`:

- `%USERPROFILE%\bouracka-tests\node_modules` (excluded)
- `%USERPROFILE%\bouracka-tests\runs\*` (excluded — volitelné, kvůli
  velikosti reportů)

### §1.4 Korporátní proxy + TLS inspection

Pokud `int-ckp.cz` provádí TLS-inspection s vlastní root CA, dodejte
SecDev cestu k PEM bundle (`C:\corp\ckp-root-ca.pem`). Skript
`scripts/setup-npm-proxy.ps1` to nakonfiguruje pro npm.

---

## §2. Stažení a rozbalení (SecDev)

Soubory dostanete e-mailem rozdělené na ZIP díly ≤ 5 MB.

### Možnost A — pomocí skriptu

```powershell
# 1. Uložte všechny díly + PART-INDEX.txt do jedné složky
# 2. Otevřete PowerShell v té složce a spusťte:
.\extract-email-volumes.ps1 `
  -SourceDir "C:\Users\$env:USERNAME\Downloads\bouracka-incoming" `
  -DestDir   "C:\Users\$env:USERNAME\bouracka-tests"
```

### Možnost B — Průzkumník Windows

Pravým tlačítkem na každý ZIP díl → "Extrahovat vše..." → cílová
složka **stejná pro všechny díly** (např. `C:\Users\<vy>\bouracka-tests\..`).
Díly mají společný kořen, takže se obsah automaticky sloučí.

Po rozbalení byste měli vidět složku `bouracka-tests\` s tímto obsahem:

```
bouracka-tests\
├── README-CS.md
├── INSTALL-CS.md                 ← tato příručka
├── package.json
├── package-lock.json
├── BOURACKA-TESTPLAN-v0.1.xlsx
├── env\
├── fixtures\
├── playwright\
├── cypress\
├── testcafe\
├── scripts\
├── tools\
├── _install\
├── _specs\
└── specs\
```

---

## §3. Instalace — jednou jednou rukou (SecDev)

### §3.1 Předpoklad — Node.js 20 LTS

Pokud notebook **ještě nemá** Node.js, nainstalujte ho **per-user**
(bez admin):

**Možnost A — winget (pokud je povolen):**
```powershell
winget install OpenJS.NodeJS.LTS --scope user --silent --accept-package-agreements --accept-source-agreements
```

**Možnost B — MSI:**
```powershell
# SecOps předem stáhne node-v20.18.1-x64.msi z https://nodejs.org/dist/v20.18.1/
msiexec /i "C:\path\to\node-v20.18.1-x64.msi" /qn ALLUSERS=2 INSTALLDIR="$env:LOCALAPPDATA\nodejs"
```

**Po instalaci**: zavřete a znovu otevřete PowerShell, aby se
PATH refreshoval. Ověřte:

```powershell
node --version    # očekáváno: ≥ v20.18
npm --version     # očekáváno: ≥ 10
```

### §3.2 Konfigurace npm pro korporátní proxy (pokud je potřeba)

Jen pokud `int-ckp.cz` má TLS-inspection (SecOps Vám předá CA bundle):

```powershell
cd C:\Users\$env:USERNAME\bouracka-tests
.\scripts\setup-npm-proxy.ps1 -ProxyUrl "http://proxy.int-ckp.cz:8080" -CaFile "C:\corp\ckp-root-ca.pem"
```

### §3.3 Hlavní instalace — JEDEN PŘÍKAZ

```powershell
cd C:\Users\$env:USERNAME\bouracka-tests
.\scripts\setup-from-zero.ps1
```

Skript provede:
1. Ověří, že Node.js + npm jsou na PATH.
2. `npm ci` — reprodukovatelná instalace závislostí podle
   `package-lock.json` (odlišné od `npm install` — instaluje přesně
   verze v lock souboru).
3. `npx playwright install chromium` — stáhne Playwright Chromium
   binárku (~600 MB do `%LOCALAPPDATA%\ms-playwright\`).
4. Spustí `validate-install.ps1` — ověří všechny komponenty.
5. Spustí `run-bring-up-smoke.ps1` — jeden Playwright test proti
   **veřejné** `bouracka.cz` (cca 30 s).

### §3.4 Očekávaný výstup

```
[setup-from-zero] cwd = C:\Users\…\bouracka-tests
[setup-from-zero] node = v20.18.1
[setup-from-zero] running 'npm ci' (≈ 2–5 min)…
[setup-from-zero] running 'npx playwright install chromium' (≈ 1–2 min)…
[setup-from-zero] running validate-install.ps1…
[OK] all checks pass
[setup-from-zero] running bring-up-smoke…
[OK] bring-up-smoke green — kit is alive.

[OK] sada je nainstalována a otestována; můžete předat testerovi.
```

Pokud vidíte `[OK] bring-up-smoke green`, instalace je hotová.

---

## §4. Co dělat při chybě

| Chyba | Příčina | Oprava |
|-------|---------|--------|
| `Node.js not found on PATH` | Node neinstalovaný nebo PATH neaktualizován | §3.1; po MSI restartujte shell |
| `npm ci` selhává s `UNABLE_TO_VERIFY_LEAF_SIGNATURE` | Korporátní TLS-inspection bez CA | §3.2 — nakonfigurujte CA bundle |
| `npm ci` timeout | Firewall blokuje `registry.npmjs.org` | §1.1 — SecOps doplní allowlist |
| `npx playwright install` 403/timeout | Firewall blokuje `cdn.playwright.dev` | §1.1 — SecOps doplní allowlist |
| `bring-up-smoke` red | Síť k `bouracka.cz` neexistuje, nebo browser binárka chybí | spusťte `npx playwright show-report ..\playwright-report` pro trace |
| `Cannot be loaded because running scripts is disabled` | PowerShell ExecutionPolicy = Restricted | spusťte `powershell -ExecutionPolicy Bypass -File .\scripts\setup-from-zero.ps1` |
| `Path is too long` | Cesta > 260 znaků | rozbalte do kratší cesty (např. `C:\bt\`) |

Detailnější diagnostika: `_install/INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md`
(uvnitř balíčku) má rozšířený troubleshooting + offline alternativy
+ profil-specifické scénáře.

---

## §5. Co dělá testerova první spuštění

Po instalaci se může uživatel notebooku (tester) podívat do
`README-CS.md` (kořen balíčku). Hlavní příkazy:

```powershell
cd C:\Users\$env:USERNAME\bouracka-tests
.\scripts\run-bring-up-smoke.ps1     # smoke proti veřejné bouracka.cz
.\scripts\run-playwright.ps1 -Env tst # ostré R1 testy proti tst.* (po doplnění creds)
.\scripts\package-results.ps1 -Tester "<příjmení>"  # zip výsledků
```

---

## §6. Odinstalace (rollback)

```powershell
cd C:\Users\$env:USERNAME
Remove-Item -Recurse -Force bouracka-tests
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\ms-playwright"
# Volitelně, pokud chcete odstranit i Node.js:
winget uninstall OpenJS.NodeJS.LTS --scope user
# nebo: msiexec /x {Node-MSI-product-code} /qn
```

Uvolní cca 880 MB. Žádné registry artefakty, žádné služby, žádné
naplánované úlohy.

---

## §7. Kontakt + reportování problémů

E-mail: `petr.yamyang@gmail.com`
Subjekt: `[BOURACKA-TESTS INSTAL] <konkrétní problém>`

Při hlášení problému přiložte:
- výstup `setup-from-zero.ps1` (zkopírujte z PowerShellu)
- výstup `validate-install.ps1` (vytváří JSON v `runs\`)
- jméno notebooku (`<test-runner-host>` apod.)

## §8. Status

| Položka | Hodnota |
|---------|---------|
| Dokument | `_install/INSTALL-CS.md` |
| Verze | v0.1 |
| Cíl | <test-runner-host> + SUPNB002 + SUPNB003 (HP EliteBook G11, Win 11 Enterprise 25H2) |
| Doba instalace | 8–12 min na zdravém notebooku |
| Admin práva | NE (vše per-user) |
| Footprint na disku | ~880 MB |
| Stav | v0.1 — připraveno pro SecDev |
