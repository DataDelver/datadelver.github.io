#!/usr/bin/env python3
"""Patch mkdocs-rss-plugin template to fix RSS validation errors.

Run this before `mkdocs build` to apply fixes. Idempotent - safe to run repeatedly.

Fixes:
1. <author> -> <dc:creator> (RSS spec requires <author> to be an email address)
2. Skip <enclosure> when length is None or non-positive (remote image 404)
3. Fix double-encoded HTML entities in title (MkDocs pre-escapes, |e escapes again)

Usage:
    python fix_rss_template.py
    mkdocs build
"""
import sys
from pathlib import Path

# Patched template content - full replacement for reliability
PATCHED_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    {# Mandatory elements #}
    {% if feed.title is not none %}<title>{{ feed.title|e }}</title>{% endif %}
    {% if feed.description is not none %}<description>{{ feed.description|e }}</description>{% endif %}
    {% if feed.html_url is not none %}<link>{{ feed.html_url }}</link>{% endif %}
    {% if feed.rss_url is not none %}<atom:link href="{{ feed.rss_url }}" rel="self" type="application/rss+xml" />{% endif %}

    {# Optional elements #}
    {% if feed.author is not none %}<managingEditor>{{ feed.author | e }}</managingEditor>{% endif %}
    {% if feed.repo_url is not none %}<docs>{{ feed.repo_url }}</docs>{% endif %}
    {% if feed.language is not none %}<language>{{ feed.language }}</language>{% endif %}

    {# Timestamps and frequency #}
    <pubDate>{{ feed.pubDate }}</pubDate>
    <lastBuildDate>{{ feed.buildDate }}</lastBuildDate>
    <ttl>{{ feed.ttl }}</ttl>

    {# Credits #}
    <generator>{{ feed.generator }}</generator>

    {# Feed illustration #}
    {% if feed.logo_url is defined %}
    <image>
      <url>{{ feed.logo_url }}</url>
      <title>{{ feed.title }}</title>
      {% if feed.html_url is not none %}<link>{{ feed.html_url }}</link>{% endif %}
    </image>
    {% endif %}

    {# Entries #}
    {% for item in feed.entries %}
    <item>
      <title>{{ item.title|e|replace('&amp;amp;', '&amp;')|replace('&amp;lt;', '&lt;')|replace('&amp;gt;', '&gt;') }}</title>
      {# Authors loop - use dc:creator for names (RSS <author> requires email) #}
      {% if item.authors is not none %}
        {% for author in item.authors %}
      <dc:creator>{{ author }}</dc:creator>
        {% endfor %}
      {% endif %}
      {# Categories loop #}
      {% if item.categories is not none %}
        {% for categorie in item.categories %}
      <category>{{ categorie }}</category>
        {% endfor %}
      {% endif %}
      <description>{{ item.description|e|replace('&amp;amp;', '&amp;')|replace('&amp;lt;', '&lt;')|replace('&amp;gt;', '&gt;') }}</description>
      {% if item.link is not none %}<link>{{ item.link|e }}</link>{% endif %}
      <pubDate>{{ item.pub_date }}</pubDate>
      {% if item.link is not none %}<source url="{{ feed.rss_url }}">{{ feed.title }}</source>{% endif %}
      {% if item.comments_url is not none %}<comments>{{ item.comments_url|e }}</comments>{% endif %}
      {% if item.guid is not none %}<guid isPermaLink="true">{{ item.guid }}</guid>{% endif %}
      {% if item.image is not none and item.image[2] is not none and item.image[2] > 0 %}
      <enclosure url="{{ item.image[0] }}" type="{{ item.image[1] }}" length="{{ item.image[2] }}" />
      {% endif %}
    </item>
    {% endfor %}
  </channel>
</rss>
'''

def find_template_path():
    """Find the mkdocs-rss-plugin template file dynamically."""
    # Method 1: Import the plugin module
    try:
        import mkdocs_rss_plugin
        plugin_dir = Path(mkdocs_rss_plugin.__file__).parent
        template_path = plugin_dir / "templates" / "rss.xml.jinja2"
        if template_path.exists():
            return template_path
    except ImportError:
        pass

    # Method 2: Search common virtualenv locations
    base = Path(__file__).parent
    for python_ver in ("python3.13", "python3.12", "python3.11", "python3.10"):
        candidate = base / ".venv" / "lib" / python_ver / "site-packages" / "mkdocs_rss_plugin" / "templates" / "rss.xml.jinja2"
        if candidate.exists():
            return candidate

    return None

def main():
    template_path = find_template_path()

    if template_path is None:
        print("ERROR: Could not find mkdocs-rss-plugin template.", file=sys.stderr)
        print("Make sure the virtualenv is activated or the plugin is installed.", file=sys.stderr)
        sys.exit(1)

    current_content = template_path.read_text()

    # Normalize whitespace for comparison (template may be minified or reformatted)
    if PATCHED_TEMPLATE.strip() == current_content.strip():
        print(f"Already patched: {template_path}")
        sys.exit(0)

    template_path.write_text(PATCHED_TEMPLATE)
    print(f"Patched: {template_path}")
    print("  - <author> -> <dc:creator> (RSS 2.0 compliance)")
    print("  - enclosure length guard added (handles None values)")
    print("  - fixed double-encoded HTML entities in title")

if __name__ == "__main__":
    main()
