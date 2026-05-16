"""bouracka-ui CLI — entry point for the `bouracka-ui` console script.

Per `_config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md` §6.6.
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# v0.1.4 — force stdout/stderr to UTF-8 so non-ASCII characters in our
# startup banner don't crash Python on Czech Windows (cp1250 default
# console encoding) when stdout is redirected to a file via Start-Process
# -RedirectStandardOutput. Without this, `print('⚠ …')` raises
# UnicodeEncodeError and the process dies before uvicorn binds the port —
# verified on Pete's ThinkPad 2026-05-13.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    # Python < 3.7 or non-text stream — best-effort; we ASCII-ify the
    # specific prints below as the belt-and-suspenders fallback.
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bouracka-ui",
        description="Local presentation-layer UI for Bouračka test suite.",
    )
    parser.add_argument("--port", type=int, default=8424,
                        help="port to listen on (default: 8424)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="host to bind (default: 127.0.0.1)")
    parser.add_argument("--workbook", type=Path, default=None,
                        help="path to BOURACKA-TESTPLAN-*.xlsx (auto-detect if omitted)")
    parser.add_argument("--runs-dir", type=Path, default=None,
                        help="path to runs/ directory (default: <repo>/runs)")
    parser.add_argument("--no-browser", action="store_true",
                        help="do not auto-open browser on startup")
    parser.add_argument("--reload", action="store_true",
                        help="dev mode — auto-reload on code change")
    args = parser.parse_args(argv)

    # Pass overrides to server module via env vars (read at import time)
    if args.workbook:
        os.environ["BOURACKA_UI_WORKBOOK"] = str(args.workbook.resolve())
    if args.runs_dir:
        os.environ["BOURACKA_UI_RUNS_DIR"] = str(args.runs_dir.resolve())

    url = f"http://{args.host}:{args.port}/"
    print(f"[bouracka-ui] starting on {url}")

    # BUG-K-003 fix (2026-05-13 Kate Round-1): make the workbook path Kate
    # actually opens VERY visible at startup. Previously the resolved workbook
    # path lived only in /api/health → /about page; testers who didn't check
    # /about could open the wrong file and think their bugs vanished.
    #
    # We pre-resolve here (best-effort) so the message shows the actual file
    # the server will use, not just "auto-detect". If pre-resolution fails
    # (e.g., import-time dependency), we fall back to the env-var hint.
    workbook_msg = os.environ.get('BOURACKA_UI_WORKBOOK')
    if not workbook_msg:
        try:
            # Late import to avoid circular at module top
            from .server import WORKBOOK_PATH, REPO_ROOT
            workbook_msg = str(WORKBOOK_PATH)
            print(f"[bouracka-ui] repo root:  {REPO_ROOT}")
        except Exception:
            workbook_msg = "(auto-detect at server startup)"
    print(f"[bouracka-ui] workbook:   {workbook_msg}")
    # ASCII-only for cp1250 safety even after the UTF-8 reconfigure above.
    print(f"[bouracka-ui] WARNING: open ONLY this workbook in Excel for bug review;")
    print(f"[bouracka-ui]          other BOURACKA-TESTPLAN-*.xlsx copies are reference only.")
    print(f"[bouracka-ui] press Ctrl+C to stop.")

    if not args.no_browser:
        # Open browser after a brief delay so server has time to bind
        def _open():
            time.sleep(0.8)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    # Defer uvicorn import until after env vars are set
    import uvicorn
    uvicorn.run(
        "bouracka_ui.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
