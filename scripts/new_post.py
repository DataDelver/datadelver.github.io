#!/usr/bin/env python3
"""Scaffold a new blog post with front matter."""

import argparse
import datetime
import os
import re
import sys


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")
    return slug


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
