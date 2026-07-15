"""MkDocs plugin that replaces generic 'Banner' alt text with descriptive text.

On blog post pages, uses the page title. On listing pages (homepage, archives,
tags), parses post card structures to map banner images to their post titles.

This improves accessibility and SEO without requiring manual alt text in every
post's markdown.
"""

import logging
import re

from mkdocs.plugins import BasePlugin, event_priority

log = logging.getLogger("mkdocs.plugins.banner_alt")


class BannerAltPlugin(BasePlugin):
    """Replace generic 'Banner' alt text with descriptive text."""

    @event_priority(55)  # Run after lazy_images (priority 50)
    def on_post_page(self, output: str, *, page, config) -> str:
        site_name = config.get("site_name", "")

        # Blog post pages: use the page title
        if hasattr(page, "excerpt") and page.excerpt is not None:
            title = getattr(page, "title", None)
            if title:
                output = _replace_single_banner(output, title, site_name)

        # Listing pages: parse post cards to map banners to titles
        elif _is_listing_page(page):
            output = _replace_listing_banners(output, site_name)

        return output


def _is_listing_page(page) -> bool:
    """Check if the page is a listing page."""
    if hasattr(page, "posts"):
        return True
    url = getattr(page, "url", "") or ""
    if any(url.startswith(prefix) for prefix in ("tags", "category", "archive", "page")):
        return True
    if url in ("", "index.html", "index"):
        return True
    return False


def _clean_title(title: str) -> str:
    """Remove 'Delve N: ' prefix from title."""
    clean = re.sub(r"^Delve\s*\d+:\s*", "", title, flags=re.IGNORECASE)
    clean = re.sub(r"^Delve\s*\d+\s*-\s*", "", clean, flags=re.IGNORECASE)
    return clean.strip()


def _replace_single_banner(html: str, title: str, site_name: str) -> str:
    """Replace alt='Banner' with descriptive text on a post page."""
    clean_title = _clean_title(title)
    alt_text = f"{clean_title} — {site_name}"

    def replace(match):
        tag = match.group(0)
        src_match = re.search(r'src="([^"]*)"', tag)
        if src_match and "banners/" in src_match.group(1):
            return re.sub(r'alt="Banner"', f'alt="{alt_text}"', tag)
        return tag

    return re.sub(r'<img[^>]*alt="Banner"[^>]*/?>', replace, html)


def _replace_listing_banners(html: str, site_name: str) -> str:
    """Replace generic banner alt text on listing pages.

    On listing pages, each post card has this structure:
      <h2 id="..."><a class="toclink" href="...">Delve N: Title</a></h2>
      <p><img loading="lazy" alt="Banner" src="...banners/..." /></p>

    The h2 heading comes BEFORE the banner image.
    """
    # Find all h2 headings containing post title links
    # Pattern: <h2 ...><a ...>Title</a></h2>
    title_pattern = re.compile(
        r'<h2[^>]*>\s*<a[^>]*href="[^"]*delve-\d+[^"]*"[^>]*>(.*?)</a>\s*</h2>',
        re.DOTALL | re.IGNORECASE,
    )

    # Find all banner images with generic alt text
    # The image may have loading="lazy" before alt="Banner"
    banner_pattern = re.compile(
        r'<img[^>]*alt="Banner"[^>]*src="[^"]*banners/[^"]*"[^>]*/?>',
        re.DOTALL | re.IGNORECASE,
    )

    # Collect titles with their end positions
    titles = []
    for match in title_pattern.finditer(html):
        title_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        clean_title = _clean_title(title_text)
        alt_text = f"{clean_title} — {site_name}"
        titles.append((match.end(), alt_text))

    # Collect banner images with their start positions
    banners = list(banner_pattern.finditer(html))

    if not banners or not titles:
        return html

    # Map each banner to the most recent title that came before it
    replacements = []
    current_title = None
    title_idx = 0

    for banner in banners:
        banner_pos = banner.start()
        # Advance title_idx to find the last title before this banner
        while title_idx < len(titles) and titles[title_idx][0] <= banner_pos:
            current_title = titles[title_idx][1]
            title_idx += 1
        if current_title:
            replacements.append((banner, current_title))

    # Apply replacements in reverse order to preserve positions
    result = html
    for banner_match, alt_text in reversed(replacements):
        old_tag = banner_match.group(0)
        new_tag = re.sub(r'alt="Banner"', f'alt="{alt_text}"', old_tag)
        result = result[:banner_match.start()] + new_tag + result[banner_match.end():]

    if replacements:
        log.debug(f"banner_alt: replaced {len(replacements)} banner alt texts on listing page")

    return result
