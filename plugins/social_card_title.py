"""MkDocs plugin that auto-generates social card titles from the page H1 heading.

When a blog post does not have an explicit social.cards_layout_options.title in its
front matter, this plugin extracts a short, clean title from the H1 heading by:

1. Stripping the "Delve N: " prefix (if present).
2. If a comma exists (series subtitle separator), taking the text after the last comma.

The plugin runs on on_page_markdown with priority -55, which is after the blog
plugin's on_page_markdown (priority -50) but before the social plugin renders cards.
"""

import re
from mkdocs.plugins import BasePlugin, event_priority

# Matches "Delve N: " at the start of a heading (e.g. "Delve 23: ")
DELVE_PREFIX = re.compile(r"^Delve\s+\d+:\s*", re.IGNORECASE)


def extract_social_title(heading: str) -> str:
    """Extract a short social card title from an H1 heading.

    Strategy:
      1. Strip the 'Delve N: ' prefix if present.
      2. If a comma remains (series subtitle separator), take the text after the last comma.
      3. Otherwise return the remaining text as-is.
    """
    # Strip "Delve N: " prefix
    title = DELVE_PREFIX.sub("", heading)

    # If there's a comma, take the part after the last comma
    if "," in title:
        title = title.rsplit(",", 1)[-1].strip()

    return title.strip()


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
