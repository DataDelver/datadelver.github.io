#!/usr/bin/env python3
"""Scaffold a new blog post with front matter."""

import argparse
import datetime
import os
import sys

# Add project root to path so we can import from plugins/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from plugins.text_utils import slugify  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Create a new blog post scaffold.")
    parser.add_argument("title", help="Title of the blog post")
    parser.add_argument(
        "--date",
        "-d",
        default=datetime.date.today().isoformat(),
        help="Post date (YYYY-MM-DD, default: today)",
    )
    args = parser.parse_args()

    slug = slugify(args.title)
    filename = f"docs/posts/{args.date}-{slug}.md"

    if os.path.exists(filename):
        print(f"Error: {filename} already exists.", file=sys.stderr)
        sys.exit(1)

    content = f"""---
date: {args.date}
categories:
  -
tags:
  -
---

# TODO: Add title

![Banner](../assets/images/banners/TODO.webp)

> "TODO: Add epigraph quote" - Author

<!-- more -->

"""

    with open(filename, "w") as f:
        f.write(content)

    print(f"Created: {filename}")


if __name__ == "__main__":
    main()
