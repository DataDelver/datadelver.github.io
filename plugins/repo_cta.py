"""MkDocs plugin that injects a GitHub repo CTA button after the post excerpt.

For posts with a `repo` field in their front matter, this plugin inserts
a styled "View the Code on GitHub" button right after the `<!-- more -->`
tag, giving readers immediate access to the associated code repository.
The button is placed after the excerpt to avoid appearing in meta descriptions.

Usage in front matter:
    ---
    date: 2025-01-26
    repo: https://github.com/DataDelver/modern-ml-microservices/tree/part-one
    ---
"""

import logging
import re
from mkdocs.plugins import BasePlugin, event_priority

log = logging.getLogger("mkdocs.plugins.repo_cta")


class RepoCtaPlugin(BasePlugin):
    """Inject a GitHub repo CTA button after the `<!-- more -->` tag"""

    @event_priority(-55)
    def on_page_markdown(self, markdown, *, page, config, files):
        # Only process pages that have a 'repo' field in front matter
        repo_url = page.meta.get("repo")
        if not repo_url:
            return

        try:
            # Find the <!-- more --> tag to insert after it (excludes button from excerpt)
            more_match = re.search(r"<!--\s*more\s*-->\n?", markdown)
            if not more_match:
                # No more tag found - insert at end of first paragraph after banner
                banner_match = re.search(r"(!\[Banner\]\([^)]+\)\n)", markdown)
                if not banner_match:
                    return
                # Find first heading after banner and insert after it
                after_banner = markdown[banner_match.end() :]
                first_heading = re.search(
                    r"(^#{1,6}\s?.*\n?)", after_banner, re.MULTILINE
                )
                if not first_heading:
                    return
                insert_pos = banner_match.end() + first_heading.end()
            else:
                # Insert right after the <!-- more --> tag
                insert_pos = more_match.end()

            button = (
                f"\n[:fontawesome-brands-github: View the Code on GitHub]({repo_url})"
                f"{{ .md-button .md-button--primary }}\n"
            )

            return markdown[:insert_pos] + button + markdown[insert_pos:]
        except Exception as e:
            log.error(f"repo_cta: error processing {page.file.src_path}: {e}")
            return markdown
