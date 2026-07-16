"""MkDocs plugin that auto-generates social card titles from the page H1 heading.

When a blog post does not have an explicit social.cards_layout_options.title in its
front matter, this plugin extracts a short, clean title from the H1 heading by:

1. Stripping the "Delve N: " prefix (if present).
2. If a comma exists (series subtitle separator), taking the text after the last comma.

The plugin runs on on_page_markdown with priority -55, which is after the blog
plugin's on_page_markdown (priority -50) but before the social plugin renders cards.

Additionally exports `post_slugify` for use as the blog plugin's `post_slugify` config
option to generate SEO-friendly URLs from the extracted social title.
"""

import re
from pymdownx.slugs import slugify as _pymdownx_slugify
from mkdocs.plugins import BasePlugin, event_priority

from .text_utils import extract_social_title

# Default pymdownx slugify instance (lowercase, matches Material default)
_default_slugify = _pymdownx_slugify(case="lower")


def post_slugify(text: str, sep: str = "-") -> str:
    """Custom slugify function for the blog plugin.

    Extracts the social title from the full H1 heading and slugifies it,
    producing clean SEO-friendly URLs like 'the-data-layer' instead of
    'delve-7-lets-build-a-modern-ml-microservice-application---part-2-the-data-layer'.

    This is designed to be used as the `post_slugify` config option in the blog plugin.
    """
    title = extract_social_title(text)
    return _default_slugify(title, sep)


class SocialCardTitlePlugin(BasePlugin):
    """Auto-set social card title from H1 heading when not explicitly provided."""

    @event_priority(-55)
    def on_page_markdown(self, markdown, *, page, config, files):
        # Only process blog posts (those with an excerpt attribute set by the blog plugin)
        if not hasattr(page, "excerpt") or page.excerpt is None:
            return

        # Skip if social card title is already explicitly set in front matter
        existing = page.meta.get("social", {}).get("cards_layout_options", {}).get("title")
        if existing:
            return

        # Find the H1 heading in the markdown
        h1_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        if not h1_match:
            return

        heading = h1_match.group(1).strip()
        social_title = extract_social_title(heading)

        if social_title:
            # Ensure page.meta["social"] and nested dict exist
            if "social" not in page.meta:
                page.meta["social"] = {}
            if "cards_layout_options" not in page.meta["social"]:
                page.meta["social"]["cards_layout_options"] = {}
            page.meta["social"]["cards_layout_options"]["title"] = social_title
