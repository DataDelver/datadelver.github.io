"""Shared MkDocs page utilities for blog plugins.

Provides page-type detection, tag extraction, and post collection logic
used by multiple plugins (banner_alt, lazy_images, related_posts, series_nav).

Contains MkDocs dependencies — for pure-Python utilities see text_utils.py.
"""


def is_listing_page(page) -> bool:
    """Check if the page is a listing page (homepage, archive, tags, etc.)."""
    if hasattr(page, "posts"):
        return True
    url = getattr(page, "url", "") or ""
    if any(url.startswith(prefix) for prefix in ("tags", "category", "archive", "page")):
        return True
    if url in ("", "index.html", "index"):
        return True
    return False


def get_tags(page) -> set[str]:
    """Extract tags from a page's meta and/or config."""
    tags = set()
    if hasattr(page, "meta") and page.meta:
        page_tags = page.meta.get("tags", [])
        if page_tags:
            if isinstance(page_tags, str):
                tags.add(page_tags)
            else:
                tags.update(str(t) for t in page_tags)
    if hasattr(page, "config") and hasattr(page.config, "tags"):
        page_tags = page.config.tags
        if page_tags:
            if isinstance(page_tags, str):
                tags.add(page_tags)
            else:
                tags.update(str(t) for t in page_tags)
    return tags


def collect_all_posts(context) -> list:
    """Collect all blog posts from the context pages list."""
    all_posts = []
    for file_item in context["pages"]:
        if hasattr(file_item, "page") and file_item.page is not None:
            p = file_item.page
            if hasattr(p, "excerpt") and p.excerpt is not None:
                all_posts.append(p)
    return all_posts
