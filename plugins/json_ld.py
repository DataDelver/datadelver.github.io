"""MkDocs plugin that injects JSON-LD structured data into pages.

Injects <script type="application/ld+json"> blocks into the <head> of pages
with structured data for search engines (Google, Bing, etc.).

Schemas:
  - BlogPosting: on blog post pages
  - WebSite with SearchAction: on every page
  - BreadcrumbList: on every page (skips home and date-only segments)
  - Person: on the about page
"""

import html
import json
import os
import re
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
    """Inject JSON-LD structured data (BlogPosting, WebSite, BreadcrumbList, Person) into pages."""

    @event_priority(10)
    def on_post_page(self, output: str, *, page, config):
        """Inject JSON-LD schemas into page <head>.

        BlogPosting: on blog post pages only.
        WebSite + SearchAction: on every page.
        BreadcrumbList: on every page.
        Person: on the about page only.
        """
        site_url = config.site_url or ""
        scripts = []

        # --- BlogPosting schema (blog posts only) ---
        if hasattr(page, "excerpt") and page.excerpt is not None:
            blog_schema = _build_blog_posting_schema(page, config, site_url, output)
            if blog_schema:
                scripts.append(blog_schema)

        # --- WebSite schema with SearchAction (every page) ---
        if site_url and config.site_name:
            website_schema: dict[str, Any] = {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": config.site_name,
                "url": site_url,
            }
            if config.site_description:
                website_schema["description"] = config.site_description
            website_schema["potentialAction"] = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{site_url.rstrip('/')}/?q={{search_term_string}}",
                },
                "query-input": "required name=search_term_string",
            }
            scripts.append(website_schema)

        # --- BreadcrumbList schema (every page) ---
        breadcrumbs = _build_breadcrumbs(page, site_url)
        if len(breadcrumbs) > 1:
            breadcrumb_schema: dict[str, Any] = {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": breadcrumbs,
            }
            scripts.append(breadcrumb_schema)

        # --- Person schema (about page only) ---
        if _is_about_page(page):
            person_schema = _build_person_schema(config, site_url)
            if person_schema:
                scripts.append(person_schema)

        # Inject all scripts before </head>
        if scripts:
            head_end = output.find("</head>")
            if head_end != -1:
                injected = ""
                for schema in scripts:
                    json_ld = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
                    injected += f'\n<script type="application/ld+json">{json_ld}</script>'
                return output[:head_end] + injected + output[head_end:]

        return output


def _build_blog_posting_schema(page, config, site_url: str, output: str) -> dict[str, Any] | None:
    """Build BlogPosting schema for a blog post page."""
    post_url = f"{site_url.rstrip('/')}/{page.url}"

    description = html.unescape(page.meta.get("description", ""))

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

    try:
        mtime = os.path.getmtime(page.file.abs_src_path)
        file_date = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        date_modified = file_date
    except OSError:
        pass

    if not date_modified and date_published:
        date_modified = date_published

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

    if not authors and config.site_author:
        authors = [{"@type": "Person", "name": config.site_author}]

    image_url = None
    og_image_start = output.find('property="og:image"')
    if og_image_start != -1:
        content_start = output.find('content="', og_image_start)
        if content_start != -1:
            content_start += len('content="')
            content_end = output.find('"', content_start)
            if content_end != -1:
                image_url = output[content_start:content_end]

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

    if hasattr(page, "categories") and page.categories:
        schema["articleSection"] = [
            cat.name if hasattr(cat, "name") else str(cat)
            for cat in page.categories
        ]

    if hasattr(page, "config") and hasattr(page.config, "readtime"):
        if page.config.readtime:
            schema["timeRequired"] = f"PT{page.config.readtime}M"

    return schema


def _build_breadcrumbs(page, site_url: str) -> list[dict[str, Any]]:
    """Build breadcrumb list items from page URL."""
    breadcrumbs: list[dict[str, Any]] = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": site_url.rstrip("/"),
        }
    ]

    # Derive breadcrumb path from page URL
    url_path = page.url
    if url_path.endswith(".html"):
        url_path = url_path[:-5]
    url_path = url_path.rstrip("/")

    if not url_path:
        return breadcrumbs

    parts = [p for p in url_path.split("/") if p and p.lower() != "index"]

    # Skip date-like segments (YYYY/MM/DD patterns) but keep the last segment
    _date_pattern = re.compile(r"^\d{1,4}$")
    meaningful_parts = []
    for part in parts:
        # Keep the last part (always the page name), skip date-like intermediates
        if part == parts[-1] or not _date_pattern.match(part):
            meaningful_parts.append(part)

    for i, part in enumerate(meaningful_parts, start=2):
        name = re.sub(r"\.\w+$", "", part).replace("-", " ").title()
        cumulative = "/".join(parts[: parts.index(part) + 1])
        item_url = f"{site_url.rstrip('/')}/{cumulative}" if cumulative else site_url.rstrip("/")
        breadcrumbs.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": item_url,
        })

    return breadcrumbs


def _is_about_page(page) -> bool:
    """Check if the page is the about page."""
    src_path = getattr(page.file, "src_path", "")
    title = getattr(page, "title", "")
    return src_path.endswith("about.md") or title.lower() == "about"


def _build_person_schema(config, site_url: str) -> dict[str, Any] | None:
    """Build Person schema for the about page."""
    author_name = config.get("site_author", "")
    if not author_name:
        return None

    person: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": author_name,
        "url": site_url.rstrip("/"),
        "jobTitle": "Machine Learning Engineer",
    }

    # Add sameAs links from extra.social
    social_links = config.get("extra", {}).get("social", [])
    same_as = []
    for entry in social_links:
        if isinstance(entry, dict) and entry.get("link"):
            same_as.append(entry["link"])
    if same_as:
        person["sameAs"] = same_as

    # Add image if avatar exists
    avatar_url = f"{site_url.rstrip('/')}/assets/images/avatar/avatar.webp"
    person["image"] = avatar_url

    return person
