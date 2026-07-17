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


# --- Excerpt extraction ---

# Default excerpt separator comment tag
EXCERPT_SEPARATOR = "<!-- more -->"


def extract_excerpt(
    markdown: str,
    separator: str = EXCERPT_SEPARATOR,
    strip_images: bool = True,
    to_plain_text: bool = True,
) -> str:
    """Extract the excerpt portion of a blog post's markdown.

    Splits on the excerpt separator, then strips front matter, the title
    heading, banner images (optional), and leading blockquotes. Optionally
    converts to plain text via strip_markdown().

    Args:
        markdown: Full post markdown content.
        separator: The excerpt separator tag (default: "<!-- more -->").
        strip_images: If True, remove banner/hero images (default: True).
        to_plain_text: If True, run strip_markdown() on the result.

    Returns:
        Clean excerpt text (plain text if to_plain_text, else markdown).
    """
    # Split on separator
    if separator in markdown:
        excerpt_md = markdown.split(separator, 1)[0]
    else:
        excerpt_md = markdown

    # Strip YAML front matter
    excerpt_md = YAML_FRONT_MATTER.sub("", excerpt_md)

    # Strip the first heading (title) if present
    excerpt_md = re.sub(r"^#{1,6}\s+.*$", "", excerpt_md, count=1, flags=re.MULTILINE)

    # Strip banner/hero image
    if strip_images:
        excerpt_md = MD_IMAGE.sub("", excerpt_md)

    # Strip leading blockquote (epigraph quote)
    excerpt_md = MD_LEADING_BLOCKQUOTE.sub("", excerpt_md)

    # Clean up whitespace
    excerpt_md = re.sub(r"\n{3,}", "\n\n", excerpt_md).strip()

    if to_plain_text:
        return strip_markdown(excerpt_md)
    return excerpt_md


# --- Post URL generation ---

# Matches the blog plugin's default URL configuration:
# post_url_format = "{date}/{slug}"
# post_url_date_format = "yyyy/MM/dd"
# See: material/plugins/blog/config.py
DEFAULT_POST_URL_FORMAT = "{date}/{slug}"
DEFAULT_POST_URL_DATE_FORMAT = "yyyy/MM/dd"


def build_post_url(
    site_url: str,
    slug: str,
    post_date: str,
    url_format: str = DEFAULT_POST_URL_FORMAT,
    date_format: str = DEFAULT_POST_URL_DATE_FORMAT,
) -> str:
    """Build a post URL matching the blog plugin's URL format.

    Replicates the blog plugin's URL generation logic so that scripts
    running outside MkDocs (e.g. newsletter_email.py) can produce
    identical URLs.

    Args:
        site_url: Base site URL (e.g. "https://www.datadelver.com").
        slug: URL slug for the post.
        post_date: ISO date string (e.g. "2025-10-07").
        url_format: URL format template with {date} and {slug} placeholders.
        date_format: Date format pattern using yyyy/MM/dd tokens.

    Returns:
        Full post URL (e.g. "https://www.datadelver.com/2025/10/07/my-post.html").
    """
    # Parse date components from ISO date
    year = month = day = ""
    if post_date and len(post_date) >= 10:
        try:
            year = post_date[:4]
            month = post_date[5:7]
            day = post_date[8:10]
        except (IndexError, ValueError):
            pass

    # Replace date format tokens with actual values
    date_str = date_format
    date_str = date_str.replace("yyyy", year).replace("MM", month).replace("dd", day)

    # Build path from URL format
    path = url_format.replace("{date}", date_str).replace("{slug}", slug)

    # Remove leading slash if present, then combine with site URL
    path = path.lstrip("/")
    return f"{site_url}/{path}.html"
