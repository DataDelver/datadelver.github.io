"""MkDocs plugin that adds loading="lazy" to non-hero images.

Adds the loading="lazy" attribute to <img> tags that reference figure images
(non-hero/non-banner images) to improve page load performance by deferring
off-screen image loading.

Banner images (hero images) are excluded on post pages since they are above the fold,
but lazy-loaded on listing pages (homepage, archives, tags) where they appear as
thumbnails further down the page.
"""

import re
from mkdocs.plugins import BasePlugin, event_priority


class LazyImagesPlugin(BasePlugin):
    """Add loading="lazy" to non-hero <img> tags in rendered HTML."""

    @event_priority(50)  # Run after other content plugins
    def on_post_page(self, output: str, *, page, config):
        # Detect listing pages: homepage, blog archives, tag pages, category pages
        # These have post cards with banner thumbnails that should be lazy-loaded
        is_listing = _is_listing_page(page)
        return _add_lazy_loading(output, lazy_banners=is_listing)


def _is_listing_page(page) -> bool:
    """Check if the page is a listing page (homepage, archive, tags, etc.)."""
    # Blog listing pages have a 'posts' attribute from the blog plugin
    if hasattr(page, "posts"):
        return True
    # Check URL patterns for archive/tag/category pages
    url = getattr(page, "url", "") or ""
    if any(url.startswith(prefix) for prefix in ("tags", "category", "archive", "page")):
        return True
    # Homepage (empty URL or index.html)
    if url in ("", "index.html", "index"):
        return True
    return False


def _add_lazy_loading(html: str, lazy_banners: bool = False) -> str:
    """Add loading="lazy" to images, excluding banner/hero images unless lazy_banners is True."""

    def replace_img(match):
        tag = match.group(0)
        src = match.group(1)

        # Skip banner images on post pages (hero images are above the fold)
        # but lazy-load them on listing pages where they're thumbnails
        if "banners/" in src and not lazy_banners:
            return tag

        # Skip avatar images (usually visible in sidebar/header)
        if "avatar/" in src:
            return tag

        # Skip favicon (not a content image)
        if "favicon/" in src:
            return tag

        # Already has loading attribute
        if 'loading=' in tag:
            return tag

        # Add loading="lazy" after the opening <img
        return re.sub(r'<img(\s)', r'<img\1loading="lazy" ', tag)

    # Match <img tags with src attribute
    pattern = r'<img[^>]*src="([^"]*)"[^>]*/?>'
    return re.sub(pattern, replace_img, html)
