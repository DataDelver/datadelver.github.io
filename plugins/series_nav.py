"""MkDocs plugin that auto-generates series navigation from shared tags.

Instead of manually maintaining `links:` in front matter for each post in a series,
this plugin detects which posts belong to a series based on shared tags and generates
navigation links automatically.

Series tags are defined centrally in `plugins.SERIES_TAGS`. The plugin uses
those as defaults, but they can be overridden or extended in mkdocs.yml:

    plugins:
      - series_nav:
          series_tags:
            - "Modern ML Microservices"
            - "Raspberry Pi Fullscreen"

For each blog post that belongs to a configured series, the plugin adds
`series_nav` to the page context with previous/next navigation and a full
list of series posts sorted chronologically.
"""

import logging
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin, event_priority

from plugins import SERIES_TAGS

log = logging.getLogger("mkdocs.plugins.series_nav")


def _get_tags(page):
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


def _get_date(post):
    """Get the created date of a post for sorting."""
    if hasattr(post, "config") and hasattr(post.config, "date"):
        return post.config.date.created
    return ""


def _collect_all_posts(context):
    """Collect all blog posts from the context pages list."""
    all_posts = []
    for file_item in context["pages"]:
        if hasattr(file_item, "page") and file_item.page is not None:
            p = file_item.page
            if hasattr(p, "excerpt") and p.excerpt is not None:
                all_posts.append(p)
    return all_posts


def _build_series_nav(series_tag, series_posts, current_page):
    """Build series navigation data for the current page.

    Returns a dict with:
      - series_name: name of the series
      - posts: list of all posts in the series (sorted chronologically)
      - current_index: 0-based index of current post
      - has_previous / has_next: boolean flags
      - previous / next: adjacent posts (or None)
    """
    # Sort chronologically (oldest first)
    sorted_posts = sorted(series_posts, key=_get_date)

    # Find current post index
    current_index = None
    for i, post in enumerate(sorted_posts):
        if post.file.src_path == current_page.file.src_path:
            current_index = i
            break

    if current_index is None:
        return None

    has_previous = current_index > 0
    has_next = current_index < len(sorted_posts) - 1
    previous = sorted_posts[current_index - 1] if has_previous else None
    next_post = sorted_posts[current_index + 1] if has_next else None

    return {
        "series_name": series_tag,
        "posts": sorted_posts,
        "current_index": current_index,
        "has_previous": has_previous,
        "has_next": has_next,
        "previous": previous,
        "next": next_post,
    }


class SeriesNavPlugin(BasePlugin):
    """Auto-generate series navigation from shared tags."""

    config_scheme = (
        ("series_tags", config_options.Type(list, default=SERIES_TAGS)),
    )

    def on_config(self, config):
        """Log configured series tags."""
        series_tags = self.config.get("series_tags", [])
        if not series_tags:
            log.warning("series_nav plugin: no series_tags configured")
        else:
            log.info(f"series_nav plugin: watching for series tags: {series_tags}")
        return config

    @event_priority(-5)
    def on_page_context(self, context, *, page, config, nav):
        """Add series_nav to page context for blog posts that belong to a series."""
        all_posts = _collect_all_posts(context)
        current_tags = _get_tags(page)

        # Only process blog posts
        if not hasattr(page, "excerpt") or page.excerpt is None:
            return

        # Check if this post belongs to any configured series
        series_tags = self.config.get("series_tags", [])
        for series_tag in series_tags:
            if series_tag in current_tags:
                # Collect all posts with this series tag
                series_posts = [
                    post
                    for post in all_posts
                    if series_tag in _get_tags(post)
                ]

                if len(series_posts) < 2:
                    # Not a series if there's only one post
                    continue

                series_nav = _build_series_nav(series_tag, series_posts, page)
                if series_nav:
                    context["series_nav"] = series_nav
                    log.debug(
                        f"series_nav: '{series_tag}' series nav added for "
                        f"{page.file.src_path} (index {series_nav['current_index']})"
                    )
                break  # Only handle the first matching series tag
