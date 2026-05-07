# MANIFEST -- bouracka-tests automatizace v0.2.0 -- CS

> Plná automatizační framework sada v0.2.0 (CP-SUPIN-03).
> Nově: Excel v0.2 (21 listů), spec-loader (R-CONTRACT-1),
> generate_tests.py + validate_workbook.py, Mockoon profile pro N8 SMS Gateway,
> TC-CP-005-SPEC.md, format-spec v0.2 dokumenty.

## Co dělat

Po extrakci → INSTALL-CS.md v kořeni; setup-from-zero.ps1 provede full install.

Pro plný R1 test run navíc:
  npm install -g @mockoon/cli
  mockoon-cli start --data .\mockoon\n8-sms-gateway.json --port 8025
  python tools\validate_workbook.py     # 10/10 zelený
  python tools\generate_tests.py        # vygeneruje playwright/tests/generated/

## Verze
| Verze | v0.2.0 |
| Stav | připraveno pro SecDev |
