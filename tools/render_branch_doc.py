#!/usr/bin/env python3
"""
render_branch_doc.py — render a branch-specific view of a master MD doc.

Per CP-SUPIN-04 STEP 19. Slices a master MD by stripping sections that don't
apply to the chosen branch.

Markup convention (in master doc):

    Common content always rendered.

    <!-- B:DEMO -->
    Content shown only when --branch=demo
    <!-- /B -->

    <!-- B:PROD -->
    Content shown only when --branch=prod
    <!-- /B -->

    <!-- B:PRE_LIVE -->
    Content shown only when --branch=pre_live
    <!-- /B -->

Usage:
  python tools/render_branch_doc.py path/to/master.md --branch demo --out out.md
  python tools/render_branch_doc.py path/to/master.md --branch prod
  python tools/render_branch_doc.py path/to/master.md   # master view (all branches)

Multiple branches per block (alternation, optional):
  <!-- B:DEMO,PRE_LIVE -->
  Content shown when --branch is demo OR pre_live
  <!-- /B -->
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

BRANCH_MARKER = re.compile(
    r'<!--\s*B:([A-Z_,\s]+)\s*-->\s*?\n?(.*?)<!--\s*/B\s*-->\s*?\n?',
    re.DOTALL,
)


def render(master_text: str, branch: str | None) -> str:
    """If branch is None → keep all branch blocks (master view).
    Otherwise → keep only blocks whose tag-list contains branch (uppercase),
    and strip blocks that target other branches."""
    if branch is None:
        return master_text  # master = no filtering

    target = branch.upper().strip()

    def repl(m: re.Match) -> str:
        tags = [t.strip().upper() for t in m.group(1).split(',') if t.strip()]
        body = m.group(2)
        if target in tags:
            return body  # keep body, strip markers
        return ''  # strip whole block

    return BRANCH_MARKER.sub(repl, master_text)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('master', help='path to master MD doc')
    ap.add_argument('--branch', default=None,
                    help='branch tag to render (e.g. demo, prod, pre_live). Omit = master view.')
    ap.add_argument('--out', default=None, help='output path; default: <master>-<branch>.md')
    args = ap.parse_args()

    master_path = Path(args.master)
    if not master_path.exists():
        sys.exit(f"[FAIL] master not found: {master_path}")

    text = master_path.read_text(encoding='utf-8')
    rendered = render(text, args.branch)

    if args.out:
        out_path = Path(args.out)
    elif args.branch:
        out_path = master_path.with_name(
            f"{master_path.stem}-{args.branch.upper()}{master_path.suffix}"
        )
    else:
        out_path = master_path.with_name(f"{master_path.stem}-MASTER{master_path.suffix}")

    out_path.write_text(rendered, encoding='utf-8')
    print(f"[ok] rendered branch={args.branch or 'MASTER'} → {out_path}")
    print(f"     (master={len(text)} B → branch={len(rendered)} B; "
          f"saved {len(text) - len(rendered)} B)")


if __name__ == '__main__':
    main()
