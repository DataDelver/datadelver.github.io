"""MkDocs plugin that adds related posts to blog post pages based on shared tags.

Computes related posts by finding other blog posts that share tags with the current
post, weighted by the number of shared tags. Adds `related_posts` to the page context
so the blog-post.html template can render them.

Excerpts are taken from `page.meta["description"]`, which is populated by the
`excerpt_description` plugin. This avoids all HTML parsing issues.
"""

import logging
from mkdocs.plugins import BasePlugin, event_priority
from html import unescape

log = logging.getLogger("mkdocs.plugins.related_posts")


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


class RelatedPostsPlugin(BasePlugin):
    """Add related posts to blog post pages based on shared tags."""

    @event_priority(-10)
    def on_page_context(self, context, *, page, config, nav):
        """Collect all blog posts and compute related posts for the current page."""
        # Only process blog post pages
        if not hasattr(page, "excerpt") or page.excerpt is None:
            return

        # Collect all blog posts from the pages list
        # context["pages"] contains File objects, so we access file.page
        all_posts = []
        for file_item in context["pages"]:
            if hasattr(file_item, "page") and file_item.page is not None:
                p = file_item.page
                if hasattr(p, "excerpt") and p.excerpt is not None:
                    all_posts.append(p)

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

        # Sort by number of shared tags (descending), then by date (descending)
        def sort_key(item):
            count, post = item
            date_str = ""
            if hasattr(post, "config") and hasattr(post.config, "date"):
                date_str = post.config.date.created
            return (-count, date_str)

        related.sort(key=sort_key)

        # Limit to 5 related posts, and attach excerpt description to each
        context["related_posts"] = []
        for _, post in related[:5]:
            post_meta = {
                "page": post,
                "excerpt": _get_excerpt_description(post),
            }
            context["related_posts"].append(post_meta)
