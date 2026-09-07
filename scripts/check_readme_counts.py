#!/usr/bin/env python3
"""Keep the README's type counts honest by deriving them from the tree.

WHY THIS EXISTS. The README-GEN block looks machine-generated, and it is
not: nothing in this repo or in ubiquex ever regenerated it. It was
written by hand once and the marker made it look maintained.

So it went stale and nothing said. On 2026-08-27 the repo really did hold
116 data source types. On 2026-09-04 a regeneration took that to 75, and
the README still said 116 a week later (UBI-241). The count was the only
thing that disagreed with reality; the tree and a fresh schema dump
agreed with each other exactly.

Deriving from the tree rather than rewriting by hand is what stops it
happening again. `--check` in CI fails on drift; `--write` updates the
block after a regeneration.

IT ALSO CATCHES A PARTIAL REGENERATION. All three language trees are
counted, not just Go. If a regeneration updated Go and left Python
behind, the counts disagree between languages and this says so, which
nothing else in the repo currently would.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- README-GEN:BEGIN -->"
END = "<!-- README-GEN:END -->"

# Per language: (root, file suffix, filenames that are not a type).
# doc.go / doc.ts / __init__.py are package scaffolding, one per service
# package, and counting them would inflate every number by the number of
# services.
LANGUAGES = {
    "go": (ROOT / "sdk/go/kubernetes", ".go", {"doc.go"}),
    "typescript": (ROOT / "sdk/typescript/kubernetes", ".ts", {"doc.ts", "index.ts", "mod.ts"}),
    "python": (ROOT / "sdk/python/ubx/kubernetes", ".py", {"__init__.py"}),
}


def count(root: Path, suffix: str, skip: set[str]) -> tuple[int, int]:
    """Returns (resources, data sources) under one language tree.

    A data source lives under the tree's own data/ directory; everything
    else is a resource. That is the layout ubx sdk gen emits, and the
    same rule the ticket's own manual count used.
    """
    if not root.is_dir():
        return (0, 0)
    resources = data_sources = 0
    for p in root.rglob(f"*{suffix}"):
        if p.name in skip:
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] == "data":
            data_sources += 1
        else:
            resources += 1
    return (resources, data_sources)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="update the README instead of checking it")
    args = ap.parse_args()

    counts = {lang: count(*spec) for lang, spec in LANGUAGES.items()}
    present = {lang: c for lang, c in counts.items() if c != (0, 0)}
    if not present:
        # Never pass by finding nothing. An empty tree means the checkout
        # is wrong or the layout moved, and a green check would be a lie.
        print("no generated SDK files found under any language tree", file=sys.stderr)
        return 1

    distinct = set(present.values())
    if len(distinct) > 1:
        print("language trees disagree, which means a partial regeneration:", file=sys.stderr)
        for lang, (r, d) in sorted(present.items()):
            print(f"  {lang:<11} {r} resource types, {d} data source types", file=sys.stderr)
        print("\nRegenerate every language together rather than reconciling by hand.", file=sys.stderr)
        return 1

    resources, data_sources = distinct.pop()
    sentence = (
        f"**Real, current counts** (`ubx sdk gen --dump-ir`): "
        f"{resources} resource types, {data_sources} data source types."
    )

    readme = ROOT / "README.md"
    text = readme.read_text()
    if BEGIN not in text or END not in text:
        print(f"README.md has no {BEGIN} / {END} block", file=sys.stderr)
        return 1

    pattern = re.compile(r"\*\*Real, current counts\*\*[^\n]*")
    if not pattern.search(text):
        print("README.md's generated block has no counts line to check", file=sys.stderr)
        return 1

    current = pattern.search(text).group(0)
    if current == sentence:
        print(f"ok: README matches the tree, {resources} resource types, {data_sources} data source types")
        return 0

    if args.write:
        readme.write_text(pattern.sub(sentence, text, count=1))
        print(f"updated: {current}\n     ->  {sentence}")
        return 0

    print("README's counts disagree with the tree.", file=sys.stderr)
    print(f"  README: {current}", file=sys.stderr)
    print(f"  tree:   {sentence}", file=sys.stderr)
    print("\nRun scripts/check_readme_counts.py --write after a regeneration.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
