"""Shared text processing utilities for blog plugins and scripts.

Provides markdown stripping, title extraction, and slugification logic
used by multiple plugins (excerpt_description, social_card_title) and
standalone scripts (newsletter_email).

All functions are pure Python with no MkDocs dependencies.
"""

import re

# --- Regex constants ---

# YAML front matter (everything from --- to ---)
YAML_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)^---\s*\n", re.MULTILINE | re.DOTALL)

# "Delve N: " prefix at the start of a heading (e.g. "Delve 23: ")
DELVE_PREFIX = re.compile(r"^Delve\s+\d+:\s*", re.IGNORECASE)

# Leading blockquote lines (epigraph quotes)
MD_LEADING_BLOCKQUOTE = re.compile(r"(?:^>\s?.*\n?)+", re.MULTILINE)

# Markdown formatting patterns
MD_BOLD = re.compile(r"\*\*(.*?)\*\*")
MD_ITALIC = re.compile(r"\*(.*?)\*")
MD_CODE = re.compile(r"`(.*?)`")
MD_LINK = re.compile(r"\[(.*?)\]\(.*?\)")
MD_IMAGE = re.compile(r"!\[.*?\]\(.*?\)")
MD_HEADER = re.compile(r"^#{1,6}\s+(.*)", re.MULTILINE)
MD_HRULE = re.compile(r"^\s*(?:---|\*\*\*|___)\s*$", re.MULTILINE)
MD_BLOCKQUOTE = re.compile(r"^>\s?(.*)", re.MULTILINE)
MD_LIST = re.compile(r"^[\s]*[-*+]\s+(.*)", re.MULTILINE)
MD_ORDERED_LIST = re.compile(r"^[\s]*\d+\.\s+(.*)", re.MULTILINE)


def strip_markdown(text: str) -> str:
    """Strip markdown formatting from text and return plain text.

    Handles images, links, bold, italic, code, headers, blockquotes,
    lists, horizontal rules, HTML tags, and escape characters.
    """
    # Remove images first (before links, since images contain brackets too)
    text = MD_IMAGE.sub("", text)
    # Replace links with their text
    text = MD_LINK.sub(r"\1", text)
    # Remove bold/italic markers
    text = MD_BOLD.sub(r"\1", text)
    text = MD_ITALIC.sub(r"\1", text)
    # Remove inline code markers
    text = MD_CODE.sub(r"\1", text)
    # Remove header markers (keep the text)
    text = MD_HEADER.sub(r"\1", text)
    # Remove blockquote markers
    text = MD_BLOCKQUOTE.sub(r"\1", text)
    # Remove list markers
    text = MD_LIST.sub(r"\1", text)
    text = MD_ORDERED_LIST.sub(r"\1", text)
    # Remove horizontal rules
    text = MD_HRULE.sub("", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Strip markdown escape characters (e.g. \* -> *)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|>)])", r"\1", text)
    # Normalize whitespace: collapse multiple spaces/newlines into single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_social_title(heading: str) -> str:
    """Extract a short, clean title from an H1 heading.

    Strategy:
      1. Strip the 'Delve N: ' prefix if present.
      2. If a comma remains (series subtitle separator), take text after the last comma.
      3. Otherwise return the remaining text as-is.
    """
    title = DELVE_PREFIX.sub("", heading)

    if "," in title:
        title = title.rsplit(",", 1)[-1].strip()

    return title.strip()


def slugify(text: str, sep: str = "-") -> str:
    """Convert text to a URL-friendly slug (lowercase, hyphenated).

    Pure Python implementation — no external dependencies.
    """
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", sep, slug)
    slug = slug.strip(sep)
    return slug
