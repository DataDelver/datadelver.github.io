"""MkDocs plugin that adds related posts to blog post pages based on shared tags.

Computes related posts by finding other blog posts that share tags with the current
post, weighted by the number of shared tags. Adds `related_posts` to the page context
so the blog-post.html template can render them.

Also collects posts filtered by a specific tag for series pages, exposed as
`series_posts` in the template context.

Excerpts are taken from `page.meta["description"]`, which is populated by the
`excerpt_description` plugin. This avoids all HTML parsing issues.
"""

import logging
from mkdocs.plugins import BasePlugin, event_priority
from html import unescape

log = logging.getLogger("mkdocs.plugins.related_posts")

SERIES_TAG = "Modern ML Microservices"


def _get_excerpt_description(page):
    """Get a clean excerpt description for a page.

    Uses the description set by the excerpt_description plugin (stored in
    page.meta["description"]), which is already stripped of title, banner,
    epigraph quote, and markdown formatting.
    """
    description = page.meta.get("description", "")
    if description:
        # The excerpt_description plugin HTML-escapes the description for
        # safe use in meta tags. Unescape it for display in the template.
        return unescape(description)
    return ""


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


def _collect_all_posts(context):
    """Collect all blog posts from the context pages list."""
    all_posts = []
    for file_item in context["pages"]:
        if hasattr(file_item, "page") and file_item.page is not None:
            p = file_item.page
            if hasattr(p, "excerpt") and p.excerpt is not None:
                all_posts.append(p)
    return all_posts


def _sort_posts_by_date(posts, reverse=True):
    """Sort posts by created date."""
    def date_key(post):
        if hasattr(post, "config") and hasattr(post.config, "date"):
            return post.config.date.created
        return ""
    return sorted(posts, key=date_key, reverse=reverse)


def _build_post_meta(post):
    """Build a post metadata dict for template rendering."""
    return {
        "page": post,
        "excerpt": _get_excerpt_description(post),
    }


class RelatedPostsPlugin(BasePlugin):
    """Add related posts to blog post pages based on shared tags."""

    @event_priority(-10)
    def on_page_context(self, context, *, page, config, nav):
        """Collect all blog posts and compute related posts for the current page."""
        all_posts = _collect_all_posts(context)

        # Always compute series posts for any page that might need them
        # Sort chronologically (oldest first) so readers follow the series in order
        series_posts = [
            _build_post_meta(post)
            for post in _sort_posts_by_date(all_posts, reverse=False)
            if SERIES_TAG in _get_tags(post)
        ]
        context["series_posts"] = series_posts

        # Only compute related posts for blog post pages
        if not hasattr(page, "excerpt") or page.excerpt is None:
            return

        # Get current page's tags
        current_tags = _get_tags(page)

        if not current_tags:
            context["related_posts"] = []
            return

        # Find related posts by shared tags
        related = []
        for post in all_posts:
            # Skip the current post
            if post.file.src_path == page.file.src_path:
                continue

            # Get post's tags
            post_tags = _get_tags(post)

            # Count shared tags
            shared = current_tags & post_tags
            if shared:
                related.append((len(shared), post))

        # Sort by date (descending), then by shared tag count (descending)
        # Python's sort is stable, so the second sort preserves date order for equal counts
        def date_key(item):
            post = item[1]
            if hasattr(post, "config") and hasattr(post.config, "date"):
                return post.config.date.created
            return ""

        related.sort(key=date_key, reverse=True)
        related.sort(key=lambda item: -item[0])

        # Limit to 5 related posts, and attach excerpt description to each
        context["related_posts"] = [_build_post_meta(post) for _, post in related[:5]]
