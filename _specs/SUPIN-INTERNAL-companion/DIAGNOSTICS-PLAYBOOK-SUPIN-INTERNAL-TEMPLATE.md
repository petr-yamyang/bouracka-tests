# Bouračka UI — Diagnostics Playbook — SUPIN-INTERNAL companion (TEMPLATE)

```
╔══════════════════════════════════════════════════════════════════════════╗
║  THIS FILE IS A TEMPLATE.                                                ║
║  Sister of: delivery/bouracka-ui-hp-elite-v0.1.0-EN/DIAGNOSTICS-PLAYBOOK ║
║                                                                          ║
║  RULES:                                                                  ║
║    1. Populate the <FILL-IN-INTERNAL: ...> placeholders ONCE on the      ║
║       maintainer's machine (Pete's ThinkPad, in a working copy).         ║
║    2. Save the populated version as DIAGNOSTICS-PLAYBOOK-SUPIN-          ║
║       INTERNAL.md (drop the -TEMPLATE suffix).                           ║
║    3. The populated copy must NEVER:                                     ║
║         - be committed to git in the populated state                     ║
║         - be packaged into bouracka-ui-hp-elite-v*.zip                   ║
║         - be sent via external email relay                               ║
║         - leave SUPIN-controlled custody                                 ║
║    4. Distribute the populated copy via:                                 ║
║         - direct handoff (USB drive, in person)                          ║
║         - encrypted USB drive                                            ║
║         - SUPIN-internal email (not external relay)                      ║
║       …to each tester's HP Elite, once per tester per major env change.  ║
║    5. The TEMPLATE (this file, with placeholders) MAY live in the repo   ║
║       because it carries no SUPIN data. The POPULATED version MUST       ║
║       NOT.                                                               ║
║                                                                          ║
║  SAFEGUARDS already in place:                                            ║
║    - This template lives at _specs/SUPIN-INTERNAL-companion/, OUTSIDE    ║
║      the gitignored delivery/ folder. The packager script only zips     ║
║      delivery/bouracka-ui-hp-elite-v0.1.0-{EN,CS}/, so this file is     ║
║      never shipped to testers via the public ZIP route.                  ║
║    - .gitignore has an explicit entry for the POPULATED filename        ║
║      (DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL.md without -TEMPLATE) so       ║
║      `git add` won't silently include the populated copy.                ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Version:** v0.1 (2026-05-11)
**Maintained by:** Pete (`petr.yamyang@gmail.com`)
**Audience:** SUPIN-trusted operators only

---

## §1. SUPIN intranet baseline

| Item | Value | Notes |
|------|-------|-------|
| SUPIN LAN subnet(s) | `<FILL-IN-INTERNAL: 10.x.x.0/24 etc>` | Used to verify "am I on the right network?" |
| SUPIN VPN endpoint | `<FILL-IN-INTERNAL: vpn.supin.lan or similar>` | VPN profile name + how to connect |
| Internal DNS server | `<FILL-IN-INTERNAL: 10.x.x.x>` | If tester laptop bypasses, tst.* resolution fails |
| Default proxy (if any) | `<FILL-IN-INTERNAL: proxy.supin.lan:3128 or NONE>` | Set in HTTP(S)_PROXY env vars if required |
| Time source (NTP) | `<FILL-IN-INTERNAL: ntp.supin.lan or similar>` | Cert-validity windows depend on correct time |

---

## §2. Network reachability — internal hostnames (cross-reference with public §2)

Match the row numbers and `<FILL-IN-LOCAL>` placeholders to the public playbook's §2 table. Populate the real values here.

| # | Public placeholder | Real hostname / IP | Port | Cert CN expected | Notes |
|---|--------------------|---------------------|------|------------------|-------|
| 1 | TST `tst.bouracka.cz` | `<FILL-IN-INTERNAL: actual host or VIP>` | 443 | `<FILL-IN: CN>` | If different from public DNS, populate hosts file |
| 2 | TST IS ČKP API host | `<FILL-IN-INTERNAL>` | 443 | `<FILL-IN: CN>` | |
| 3 | TST AISPOV API host | `<FILL-IN-INTERNAL>` | 443 | `<FILL-IN: CN>` | |
| 4 | TST zenID host | `<FILL-IN-INTERNAL>` | 443 | `<FILL-IN: CN>` | |
| 5 | TST N8 SMS gateway | `<FILL-IN-INTERNAL>` | `<FILL-IN: port>` | `<FILL-IN: CN>` | |
| 6 | UAT `<each row>` | `<FILL-IN-INTERNAL>` | — | — | Same structure as TST when UAT comes online |

---

## §3. Cert chain — SUPIN-issued certificates

| Item | Value |
|------|-------|
| Root CA name in Windows cert store | `<FILL-IN-INTERNAL: SUPIN Root CA or similar>` |
| Intermediate CA names | `<FILL-IN-INTERNAL>` |
| Where to install on a new HP Elite | `<FILL-IN-INTERNAL: SUPIN IT runbook reference or steps>` |
| Browser-trust check command | `<FILL-IN-INTERNAL: e.g. certutil -store Root>` |

---

## §4. Integration contract specifics — TST and UAT live endpoints

For each integration named in public §3, the SUPIN-internal authoritative endpoint + auth pattern:

### §4.1 IS ČKP
| Field | Value |
|-------|-------|
| TST base URL | `<FILL-IN-INTERNAL>` |
| Auth method | `<FILL-IN-INTERNAL: bearer / mTLS / IP-allowlist / etc.>` |
| Test credentials location | `<FILL-IN-INTERNAL: path on HP Elite, encrypted file, etc.>` |
| Sample valid payload | `<FILL-IN-INTERNAL: JSON snippet or reference>` |
| Sample invalid payload (for negative tests) | `<FILL-IN-INTERNAL>` |
| Schema doc | `<FILL-IN-INTERNAL: doc reference>` |

### §4.2 AISPOV
| Field | Value |
|-------|-------|
| TST base URL | `<FILL-IN-INTERNAL>` |
| Auth method | `<FILL-IN-INTERNAL>` |
| Test driver IDs known to be valid | `<FILL-IN-INTERNAL: list>` |
| Test driver IDs known to be invalid | `<FILL-IN-INTERNAL: list>` |
| Schema doc | `<FILL-IN-INTERNAL>` |

### §4.3 zenID
| Field | Value |
|-------|-------|
| TST base URL | `<FILL-IN-INTERNAL>` |
| Auth method | `<FILL-IN-INTERNAL>` |
| Test ID document images (path on HP Elite) | `<FILL-IN-INTERNAL>` |
| Expected OCR fields per sample | `<FILL-IN-INTERNAL>` |
| Schema doc | `<FILL-IN-INTERNAL>` |

### §4.4 N8 SMS gateway
| Field | Value |
|-------|-------|
| TST endpoint | `<FILL-IN-INTERNAL>` |
| Auth method | `<FILL-IN-INTERNAL>` |
| Test SIM cards / phone numbers | `<FILL-IN-INTERNAL: store separately; do NOT inline real numbers>` |
| SMS retrieval mechanism | `<FILL-IN-INTERNAL: which TST phones, who reads them, how>` |
| Schema doc | `<FILL-IN-INTERNAL>` |

### §4.5 Mockoon (DEMO mode only)
| Field | Value |
|-------|-------|
| Mockoon environment file location | `<FILL-IN-INTERNAL: path in repo, version, who maintains>` |
| Ports used | `<FILL-IN-INTERNAL: typically :3000 :3001>` |
| Start command | `<FILL-IN-INTERNAL: e.g. mockoon-cli start --data ...>` |

---

## §5. Drift catalogue — SUPIN-internal extensions

Drift patterns specific to SUPIN-internal infrastructure (extends public §4):

| # | Drift name | Internal symptom | Root cause | Fix or workaround |
|---|------------|-------------------|------------|--------------------|
| 1 | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` |
| 2 | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` |
| ... | (add rows as drift gets discovered) | | | |

---

## §6. Escalation contacts — populated

Populate from the public §8 escalation matrix's `<FILL-IN: role>` placeholders. Single source of truth lives here.

| Role | Primary contact | Backup | Notes |
|------|-----------------|--------|-------|
| Pete (project owner / UI maintainer) | `petr.yamyang@gmail.com` | — | Default escalation |
| SUPIN SecOps | `<FILL-IN-INTERNAL: name + email + phone>` | `<FILL-IN-INTERNAL>` | Cert / network / proxy issues |
| ČKP API ops | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | Real backend failures (5xx, 503) |
| AISPOV ops | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | Driver-lookup backend down |
| zenID ops | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | OCR backend down |
| N8 / telco ops | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | SMS gateway down |
| SUPIN IT (HP Elite hardware/OS) | `<FILL-IN-INTERNAL>` | `<FILL-IN-INTERNAL>` | Won't boot, pip fails, etc. |

---

## §7. After-action: DELTA-REPORT integration

When a tester ships back a DELTA-REPORT (public §7.2) that exposes a SUPIN-internal gap (new drift pattern, new mock-vs-real surprise, new endpoint), the maintainer's loop:

1. Read DELTA-REPORT + attachments on ThinkPad
2. If finding affects SUPIN-internal structure (new hostname, new auth pattern, new fixture, new drift), update this internal companion's relevant §
3. Re-distribute updated companion to all active testers via SUPIN-controlled channel
4. If finding affects public structure (new tester-facing diagnostic, new symptom-to-cause mapping), update the public DIAGNOSTICS-PLAYBOOK + re-ship ZIPs to all testers
5. If finding is a real Bouračka bug (not drift, not config), file BUG-* and route to dev session

The internal companion's version number bumps independently of the public doc — they're sister docs, not lock-stepped.

---

## §8. Population procedure (for Pete on ThinkPad)

When you first populate this template:

1. Copy `_specs/SUPIN-INTERNAL-companion/DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL-TEMPLATE.md` to `_specs/SUPIN-INTERNAL-companion/DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL.md` (drop `-TEMPLATE`)
2. Open the new file
3. Walk through every `<FILL-IN-INTERNAL: ...>` placeholder; fill in real values
4. Save
5. **Verify** the populated file is in `.gitignore` by running:
   ```powershell
   git check-ignore -v _specs/SUPIN-INTERNAL-companion/DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL.md
   ```
   Output should match a `.gitignore` rule. If not, ADD the rule before doing anything else.
6. Copy the populated file via secure channel (USB / SUPIN-controlled email) to each active HP Elite
7. Make sure the tester knows it sits next to the public playbook and is the source of truth for `<FILL-IN-LOCAL>` resolution

When you update the populated file (new drift, new endpoint, etc.):

1. Edit the populated copy on ThinkPad
2. Bump the version line at the top
3. Re-distribute via secure channel
4. Optionally: update this TEMPLATE in git to add new placeholder rows when the structure (not just data) changes — that way new testers get the updated structure

End of DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL-TEMPLATE.md
