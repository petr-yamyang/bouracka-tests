# Integration recon harness — D8WS / D5WS

**Verze.** v0.2.0 (2026-05-15).
**Pro.** Petra (HP Elite / ThinkPad / SUPIN VPN) NEBO SUPIN ops kolegu na serveru.
**Účel.** Aktivní recon SOAP endpointů SEDN (D8WS, D5WS) zevnitř SUPIN sítě.
                Bezpečný, jen-čte, žádné destruktivní operace.

---

## §1. Co to dělá

Harness probuje 11 endpointů (4× SOAP D8WS/D5WS + 7 internetových integrací z INT-001..009) a pro každý spustí sadu probe typů nakonfigurovanou v `targets.json`. SOAP targety dostávají tradiční 4 proby:

1. **TCP probe** — handshake na host:port. Říká: dosažitelný / firewall / refused?
2. **HTTP HEAD** — odpovídá vůbec HTTP na URL?
3. **WSDL GET** — `<url>?wsdl` → stáhne WSDL, parsuje `targetNamespace` a operace.
4. **SOAP fault elicit** — POST prázdné SOAP obálky → vyvolá strukturovanou fault response (zdravý SOAP service vždy vrátí HTTP 500 + `<Fault>`).

Z probe výsledků odvozuje verdikty na otevřené otázky:

| Otázka | Kde dokumentovaná | Co harness rozhoduje |
|--------|-------------------|----------------------|
| Q-INT-010-1 | INT-010 §2 | Je D8WS/D5WS port-inversion (3030/3031) skutečná, nebo překlep? — porovná WSDL targetNamespace každého portu. |
| Q-INT-010-2 | INT-010 §2 | Je 172.16.1.13:3030/3031 dosažitelný z tohoto hosta? — TCP probe na všechny 4 endpointy. |

---

## §2. Předpoklady

- **Python 3.8+** na PATH (jakákoli verze; ne Microsoft Store edice doporučená, ale funkční).
  - Stdlib only — žádné pip install nutné.
- **TCP reach** na `172.16.1.13:3030` a `172.16.1.13:3031` — t.j. SUPIN-internal síť / VPN aktivní.
- **Zápisové právo** do složky `recon-harness/outputs/` (výstupy se ukládají sem).

---

## §3. Jak spustit

### §3.1 Windows (PowerShell)

```powershell
cd <kam-rozbaleno>\recon-harness
.\Run-IntRecon.ps1                # interaktivní menu (doporučeno)
.\Run-IntRecon.ps1 -Mode all      # one-shot: probe vše, vygeneruj report, ukonči
.\Run-IntRecon.ps1 -Mode list     # vypiš cíle (smoke check konfigurace)
```

### §3.2 Linux / RHEL

```bash
cd <kam-rozbaleno>/recon-harness
chmod +x run-int-recon.sh
./run-int-recon.sh                # interaktivní menu
./run-int-recon.sh all            # one-shot
./run-int-recon.sh list           # smoke check
```

### §3.3 Přímo Python (bez wrapperu)

```bash
python int_recon.py menu          # menu
python int_recon.py probe-all     # vše
python int_recon.py probe --target D8WS-TST   # jeden cíl
python int_recon.py list          # výpis cílů
```

---

## §4. Probe-type matice (který probe běží na který cíl)

| Cíl | tcp | http_head | https_tls | http_get_json | wsdl_get | soap_fault |
|-----|:---:|:---------:|:---------:|:-------------:|:--------:|:----------:|
| D8WS-STD / D8WS-TST | ✓ | ✓ | | | ✓ | ✓ |
| D5WS-STD / D5WS-TST | ✓ | ✓ | | | ✓ | ✓ |
| INT-001 reCAPTCHA api.js | ✓ | ✓ | ✓ | | | |
| INT-001 reCAPTCHA siteverify | ✓ | | ✓ | | | |
| INT-006 Azure outage feed | ✓ | | ✓ | ✓ | | |
| INT-007 Google Maps JS | ✓ | ✓ | ✓ | | | |
| INT-008 internal /api (DEMO) | ✓ | ✓ | ✓ | | | |
| INT-009 RÚIAN suggest | ✓ | | ✓ | ✓ | | |
| INT-009 RÚIAN vyhledavaci | ✓ | | ✓ | ✓ | | |

**Poznámky k probe typům:**

- `tcp_connect` — TCP handshake (dosažitelnost na IP:port)
- `http_head` — HTTP HEAD (toleruje self-signed cert)
- `https_tls_verify` — HEAD se striktním TLS ověřením (odmítne self-signed; pro Google/Azure)
- `http_get_json` — GET + parsování JSON odpovědi + validace klíčů dle `expect_json_keys`
- `wsdl_get` — GET `?wsdl`, parsuje `targetNamespace` + operace
- `soap_fault_elicit` — POST prázdné SOAP obálky → vyvolá strukturovanou fault response

---

## §5. Chybějící endpointy — čeká se na SUPIN follow-up

Tyto integrace jsou zdokumentované v INT-002..INT-005, ale endpoint URL dosud není znám.
**Kontakt: Michal Ciberej (SUPIN, SEDN správce)** — vyžádat konkrétní URL před dalším reconem.

| INT | Integrace | Co chybí |
|-----|-----------|----------|
| INT-002 | SMS gateway | URL endpointu (SUPIN-internal nebo cloud?) |
| INT-003 | SMTP relay | URL / hostname mail serveru |
| INT-004 | AISPOV — rejstřík vozidel/řidičů | URL (pravděpodobně SUPIN-internal, stejná síť jako D8WS) |
| INT-005 | Geocoder pro místo nehody | URL (možný overlap s INT-007 / INT-009 RÚIAN) |

---

## §6. Co se vygeneruje

Po každém probe-all (nebo probe-one) vznikne dvojice souborů v `outputs/`:

```
outputs/
├── RECON-<hostname>-<YYYYMMDD-HHMMSS>.json    # machine-parseable, pro Claude
└── RECON-<hostname>-<YYYYMMDD-HHMMSS>.md      # human-readable, pro Petra
```

JSON obsahuje:

- `recon_id` (UUID), timestampy startu/konce
- `host_env` (hostname, IP, OS, Python verze, SUPIN-internal indikátor)
- `targets[].probes[]` s úplným detailem (HTTP status, response excerpts, SHA256, WSDL ops, SOAP fault detaily)
- `questions_answered.Q-INT-010-1` + `Q-INT-010-2` s verdikty a evidencí

MD report je čistý markdown:

- §1 Verdikty otázek (vrchol pyramidy — co Petr potřebuje vědět)
- §2 Per-target tabulky probe výsledků + ukázky WSDL/SOAP fault

---

## §7. Co s reportem dál

**Petrovi:** pošli zpět **JSON soubor** (ten je strojově parseovatelný). Claude session
ho prokousne a integruje do integration recon dokumentů (INT-010, INT-011). Alternativně
zkopíruj/nalep **MD soubor** přímo do chatu — Claude pochopí obojí.

Příklad:

```
Hi Claude, here's the recon output from <hostname>:

<paste JSON contents>

Pls integrate findings into INT-010 / INT-011 and update Q-INT-010-1 verdict.
```

---

## §8. Bezpečnost a omezení

- **Žádné credentials.** Harness neposílá auth, neposílá payload. Probe SOAP envelope
  má prázdné body — vyvolá fault, ne data create/update.
- **Žádné TLS validation.** SUPIN-internal certy mohou být self-signed; harness
  toleruje (logováno).
- **Žádný retry / backoff.** Jeden pokus na probe; pokud selže, info v reportu.
- **Timeouts.** TCP 5s, HTTP 10s — pokud SUPIN síť pomalejší, uprav v `int_recon.py`
  konstanty `TCP_TIMEOUT_S` / `HTTP_TIMEOUT_S`.

---

## §9. Když něco nejde

| Symptom | Pravděpodobná příčina | Co dělat |
|---------|------------------------|----------|
| TCP probe všude FAIL | Mimo SUPIN síť / VPN neaktivní | Aktivuj SUPIN VPN, retry |
| TCP OK, HTTP HEAD FAIL | Reverse proxy / IIS / authentik vrstva | Zkontroluj `Run-IntRecon.ps1` výstup, zda 172.16.1.13:3030 reaguje na curl/Invoke-WebRequest |
| WSDL fetch 404 | URL path nebo handler špatně | Otevři URL v prohlížeči ručně, zkus `?wsdl=`, `?WSDL`, `/sedn-ws-d8?wsdl` |
| SOAP fault elicit HTTP 415 | Service očekává specifický `SOAPAction` header | Normální — služba žije; report označí INCONCLUSIVE |
| WSDL parsuje, ale `wsdl_operations=[]` | WSDL používá `import` na další schémata, ne inline | OK pro recon; pro úplný kontrakt zkus zachytit i imported XSD ručně |
| Python `ModuleNotFoundError` | Nepravděpodobné — stdlib only | Zkus jiný Python; minimum 3.8 |

---

## §10. Soubory v balíčku

```
recon-harness/
├── README-CS.md           # tento soubor
├── int_recon.py           # Python recon engine (stdlib only)
├── targets.json           # konfigurace cílů (11 endpointů — 4 SOAP + 7 internet)
├── Run-IntRecon.ps1       # Windows wrapper
├── run-int-recon.sh       # Linux wrapper
└── outputs/               # report výstupy (vznikne po prvním běhu)
```

---

## §11. Roadmap (NOT v této verzi)

- v0.2 — autenticated probes (Basic auth / WS-Security header) až SUPIN dodá credentials
- v0.2 — `D5GetDN` reálný read pro konkrétní `KodDN` (read-only, ale s payloadem)
- v0.3 — recon-as-a-bouracka-ui-plugin (button v UI, ne CLI)
- v0.3 — schedule-driven recon (každé ráno + diff vůči předchozímu — detekce změn API)
