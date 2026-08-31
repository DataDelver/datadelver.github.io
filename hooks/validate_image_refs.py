#!/usr/bin/env python3
"""Pre-commit hook: ensure image references in Markdown resolve to real files.

Catches broken banner/figure links like `![...](../assets/.../missing.webp)`
before they reach the built site.
"""

import re
import sys
from pathlib import Path

# Markdown image syntax: ![alt](src)
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def validate_markdown(filepath: Path) -> list[str]:
    errors = []
    content = filepath.read_text(encoding="utf-8")

    for match in IMAGE_PATTERN.finditer(content):
        src = match.group(1).strip()

        # Skip external URLs and data URIs
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", src):
            continue

        # Strip anchor fragments (e.g. image.png#anchor)
        path_part = src.split("#", 1)[0]
        if not path_part:
            continue

        # Resolve relative to the Markdown file's directory
        target = (filepath.parent / path_part).resolve()
        if not target.is_file():
            errors.append(f"{filepath}: image not found: {src}")

    return errors


def main():
    # If called by pre-commit, filenames are passed as args
    # If called manually with no args, check all Markdown under docs/
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = list(Path("docs").rglob("*.md"))

    all_errors = []
    for filepath in files:
        if filepath.is_file():
            all_errors.extend(validate_markdown(filepath))

    if all_errors:
        print("Broken image references:", file=sys.stderr)
        for error in all_errors:
            print(f"  ❌ {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ All image references resolve.")


if __name__ == "__main__":
    main()
