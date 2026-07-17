"""MkDocs plugin that injects a newsletter signup form at the end of blog posts.

For pages that are blog posts (identified by having an excerpt from the
mkdocs-blog plugin), this plugin appends a Buttondown newsletter signup
form just before the closing </article> tag.

The newsletter HTML is read from overrides/partials/newsletter.html so
there's a single source of truth shared with the homepage and any other
template that includes the partial.

Usage in mkdocs.yml:
    plugins:
      - newsletter_embed:
          enabled: true
"""

import logging
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin, event_priority

log = logging.getLogger("mkdocs.plugins.newsletter_embed")


class NewsletterEmbedPlugin(BasePlugin):
    """Inject newsletter signup form at the end of blog posts."""

    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
    )

    def __init__(self):
        super().__init__()
        self._newsletter_html = ""

    def on_config(self, config):
        """Read and render the newsletter partial from overrides."""
        if not self.config.get("enabled", True):
            return config

        theme = config["theme"]
        env = theme.get_env()

        try:
            template = env.get_template("partials/newsletter.html")
            self._newsletter_html = template.render(**env.globals)
        except Exception as e:
            log.warning("Failed to load newsletter partial: %s", e)
            self._newsletter_html = ""

        return config

    @event_priority(60)  # Run after all content plugins
    def on_post_page(self, output: str, *, page, config):
        if not self.config.get("enabled", True):
            return output

        if not self._newsletter_html:
            return output

        # Only inject on blog post pages (identified by having an excerpt)
        if not hasattr(page, "excerpt") or page.excerpt is None:
            return output

        # Find the closing </article> tag and inject before it
        article_end = output.rfind("</article>")
        if article_end != -1:
            return output[:article_end] + self._newsletter_html + output[article_end:]

        # Fallback: inject before </body>
        body_end = output.rfind("</body>")
        if body_end != -1:
            return output[:body_end] + self._newsletter_html + output[body_end:]

        return output
