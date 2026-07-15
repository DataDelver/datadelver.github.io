#!/usr/bin/env python3
"""Pre-commit hook: ensure post filename date matches front matter date."""

import re
import sys
from pathlib import Path

DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
YAML_DATE_PATTERN = re.compile(r"^---\s*\n(?:.*\n)*?^\s*date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def validate_post(filepath: Path) -> list[str]:
    errors = []
    filename = filepath.name

    # Extract date from filename
    filename_match = DATE_PATTERN.match(filename)
    if not filename_match:
        return errors  # Skip files that don't match the date-slug pattern

    filename_date = filename_match.group(1)

    # Extract date from front matter
    content = filepath.read_text(encoding="utf-8")
    frontmatter_match = YAML_DATE_PATTERN.match(content)

    if not frontmatter_match:
        errors.append(f"{filename}: no 'date' found in front matter (expected {filename_date})")
        return errors

    frontmatter_date = frontmatter_match.group(1)

    if filename_date != frontmatter_date:
        errors.append(
            f"{filename}: filename date ({filename_date}) != front matter date ({frontmatter_date})"
        )

    return errors


def main():
    # If called by pre-commit, filenames are passed as args
    # If called manually with no args, check all posts
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = list(Path("docs/posts").glob("*.md"))

    all_errors = []
    for filepath in files:
        all_errors.extend(validate_post(filepath))

    if all_errors:
        print("Date mismatch errors:", file=sys.stderr)
        for error in all_errors:
            print(f"  ❌ {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ All post dates match.")


if __name__ == "__main__":
    main()
