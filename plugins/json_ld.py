"""MkDocs plugin that injects JSON-LD structured data (schema.org BlogPosting) into blog posts.

Injects a <script type="application/ld+json"> block into the <head> of each blog
post page with structured data for search engines (Google, Bing, etc.).

Runs on on_post_page so that all metadata (including description from
excerpt_description plugin) is already available.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any

from mkdocs.plugins import BasePlugin, event_priority


def _to_iso_date(value) -> str | None:
    """Convert a date value to ISO 8601 format (YYYY-MM-DD)."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        # Try parsing common date formats
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None


class JsonLdPlugin(BasePlugin):
    """Inject JSON-LD BlogPosting structured data into blog post pages."""

    @event_priority(10)
    def on_post_page(self, output: str, *, page, config):
        # Only process blog posts (those with an excerpt attribute)
        if not hasattr(page, "excerpt") or page.excerpt is None:
            return

        # Build the BlogPosting schema
        site_url = config.site_url or ""
        post_url = f"{site_url.rstrip('/')}/{page.url}"

        # Get description from meta (set by excerpt_description plugin)
        description = page.meta.get("description", "")

        # Get date from post config - blog plugin stores date as a DateDict
        # with "created" key (and optionally "updated", etc.)
        date_published = None
        date_modified = None
        if hasattr(page, "config") and hasattr(page.config, "date"):
            post_date = page.config.date
            if hasattr(post_date, "get"):
                created = post_date.get("created")
                date_published = _to_iso_date(created)
                updated = post_date.get("updated")
                if updated:
                    date_modified = _to_iso_date(updated)

        # Use file modification time as dateModified if different from published
        try:
            mtime = os.path.getmtime(page.file.abs_src_path)
            file_date = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
            date_modified = file_date
        except OSError:
            pass

        # If no separate modification date, use published date
        if not date_modified and date_published:
            date_modified = date_published

        # Get authors
        authors = []
        if hasattr(page, "authors") and page.authors:
            for author in page.authors:
                author_data: dict[str, Any] = {
                    "@type": "Person",
                    "name": author.name,
                }
                if author.url:
                    author_data["@id"] = author.url
                authors.append(author_data)

        # If no authors from blog plugin, use site author
        if not authors and config.site_author:
            authors = [{"@type": "Person", "name": config.site_author}]

        # Get image URL (og:image from social plugin, or construct expected path)
        image_url = None
        # Try to extract og:image from the HTML output
        og_image_start = output.find('property="og:image"')
        if og_image_start != -1:
            content_start = output.find('content="', og_image_start)
            if content_start != -1:
                content_start += len('content="')
                content_end = output.find('"', content_start)
                if content_end != -1:
                    image_url = output[content_start:content_end]

        # Build the schema
        schema: dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": page.title,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": post_url,
            },
            "url": post_url,
        }

        if description:
            schema["description"] = description

        if date_published:
            schema["datePublished"] = date_published

        if date_modified:
            schema["dateModified"] = date_modified

        if authors:
            schema["author"] = authors if len(authors) > 1 else authors[0]

        # Publisher (organization)
        if config.site_name:
            logo_url = f"{site_url.rstrip('/')}/assets/images/social/{config.theme.get('name', 'material')}.png"
            schema["publisher"] = {
                "@type": "Organization",
                "name": config.site_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": logo_url,
                },
            }

        if image_url:
            schema["image"] = [image_url]

        # Categories as articleSection
        if hasattr(page, "categories") and page.categories:
            schema["articleSection"] = [
                cat.name if hasattr(cat, "name") else str(cat)
                for cat in page.categories
            ]

        # Read time as timeRequired (approximate)
        if hasattr(page, "config") and hasattr(page.config, "readtime"):
            if page.config.readtime:
                schema["timeRequired"] = f"PT{page.config.readtime}M"

        # Serialize to JSON
        json_ld = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))

        # Inject before </head>
        head_end = output.find("</head>")
        if head_end != -1:
            script = f'\n<script type="application/ld+json">{json_ld}</script>'
            return output[:head_end] + script + output[head_end:]

        return output
