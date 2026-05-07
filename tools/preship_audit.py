#!/usr/bin/env python3
"""
preship_audit.py — verify a built ZIP is safe to email-ship.

Per CP-SUPIN-04 EMAIL-DELIVERABILITY-RULES spec. Before any email release
MUST run with PASS:
    py tools/preship_audit.py path/to/bouracka-tests-vX.Y.Z.zip

Checks:
  1. No forbidden file extensions inside the ZIP
  2. No high-IOC strings inside any text file in the ZIP
  3. ZIP integrity (every entry uncompresses cleanly)
  4. Total size under 5 MB

IOC patterns are constructed at runtime from char-code concatenation so this
source file itself doesn't contain the literal IOC strings (would otherwise
cause this script to flag itself).
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path


# Forbidden file extensions — auto-block by Gmail / Office365 / Active24
FORBIDDEN_EXT = (
    ".cmd", ".bat", ".ps1", ".psm1", ".psd1", ".psc1",
    ".vbs", ".vbe", ".wsf", ".wsh",
    ".exe", ".dll", ".scr", ".com", ".pif",
    ".msi", ".msp", ".hta", ".lnk", ".reg", ".jar",
    ".docm", ".xlsm", ".pptm",
    ".iso", ".vhd", ".vhdx",
)


def _make_iocs():
    """Build IOC pattern list at runtime via chr/concat to keep this source clean.

    Pattern labels (P1-P9) describe categories without spelling the IOC literal.
    See _specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md for the human-readable list.
    """
    p1 = (chr(45) + "Execu" + "tion" + "Pol" + "icy" + r"\s+" + "By" + "pass")
    p2 = r"\bInvoke" + chr(45) + "Expr" + "ession\b"
    p3 = r"\b" + chr(73) + chr(69) + chr(88) + r"\b"
    p4 = r"\bDownload" + "Str" + "ing\b|\bDownload" + "Fi" + "le\b"
    p5 = r"\bWeb" + "Cli" + "ent\b|\bInvoke" + chr(45) + "Web" + "Req" + "uest\b|\biwr\b"
    p6 = chr(45) + "Win" + "dow" + "Style" + r"\s+" + "Hid" + "den"
    p7 = r"\bFromBase" + chr(54) + chr(52) + "Str" + "ing\b|\bEnco" + "ded" + "Comm" + "and\b"
    p8 = r"po" + "wer" + r"shell\.exe\s+.+\-F" + "ile"
    p9 = r"cm" + r"d\.exe\s+/c\b"
    return [
        (p1, "P1-policy-bypass"),
        (p2, "P2-remote-eval"),
        (p3, "P3-eval-alias"),
        (p4, "P4-http-download"),
        (p5, "P5-http-client"),
        (p6, "P6-hidden-window"),
        (p7, "P7-base64-obfuscation"),
        (p8, "P8-shell-launcher"),
        (p9, "P9-shell-spawn"),
    ]


def audit_zip(zip_path: Path, max_mb: float = 5.0) -> int:
    if not zip_path.exists():
        print(f"[preship] not found: {zip_path}")
        return 4

    sz_mb = zip_path.stat().st_size / 1_048_576
    if sz_mb > max_mb:
        print(f"[preship] WARN size {sz_mb:.2f} MB > recommended {max_mb} MB")

    iocs = _make_iocs()
    errors = 0
    warnings = 0

    with zipfile.ZipFile(zip_path) as zf:
        # Integrity
        bad = zf.testzip()
        if bad:
            print(f"[preship] FAIL integrity: corrupt entry {bad}")
            return 5

        names = zf.namelist()
        print(f"[preship] {zip_path.name} — {len(names)} entries, {sz_mb:.1f} MB")

        # Forbidden extensions
        for name in names:
            lower = name.lower()
            for ext in FORBIDDEN_EXT:
                if lower.endswith(ext):
                    print(f"  FAIL forbidden ext: {name}")
                    errors += 1
                    break

        # IOC content scan (skip binary types)
        binary_ext = (".png", ".jpg", ".jpeg", ".gif", ".heic", ".pdf",
                      ".xlsx", ".zip", ".tar.gz", ".pyc", ".woff", ".woff2",
                      ".ttf", ".webm", ".mp4", ".webp", ".ico")
        for name in names:
            if any(name.lower().endswith(b) for b in binary_ext):
                continue
            try:
                data = zf.read(name).decode("utf-8", errors="ignore")
            except Exception:
                continue
            for pat, label in iocs:
                for m in re.finditer(pat, data, re.IGNORECASE):
                    print(f"  FAIL IOC '{label}' in {name}: '{m.group(0)[:60]}'")
                    errors += 1
                    break  # one per file per pattern enough

    if errors == 0:
        print(f"[preship] PASS — safe to email")
        return 0
    print(f"[preship] FAIL — {errors} issue(s); do not ship via email")
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("zip_path", type=Path, help="Path to ZIP to audit")
    ap.add_argument("--max-mb", type=float, default=5.0,
                    help="Soft size cap (warning, not failure)")
    args = ap.parse_args()
    sys.exit(audit_zip(args.zip_path, args.max_mb))
