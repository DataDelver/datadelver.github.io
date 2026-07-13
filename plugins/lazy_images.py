"""MkDocs plugin that adds loading=\"lazy\" to non-hero images.

Adds the loading=\"lazy\" attribute to <img> tags that reference figure images
(non-hero/non-banner images) to improve page load performance by deferring
off-screen image loading.

Banner images (hero images) are excluded since they are typically above the fold.
"""

import re
from mkdocs.plugins import BasePlugin, event_priority


class LazyImagesPlugin(BasePlugin):
    """Add loading=\"lazy\" to non-hero <img> tags in rendered HTML."""

    @event_priority(50)  # Run after other content plugins
    def on_post_page(self, output: str, *, page, config):
        return _add_lazy_loading(output)


def _add_lazy_loading(html: str) -> str:
    """Add loading=\"lazy\" to figure images, excluding banner/hero images."""

    def replace_img(match):
        tag = match.group(0)
        src = match.group(1)

        # Skip banner images (hero images are typically above the fold)
        if "banners/" in src:
            return tag

        # Skip avatar images (usually visible in sidebar)
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
