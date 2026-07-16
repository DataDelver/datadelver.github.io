#!/usr/bin/env python3
"""Detect new blog posts and create a draft newsletter email via Buttondown API.

This script is designed to run in a GitHub Actions workflow on push to main.
It compares the latest commit against the previous one to find new .md files
added to docs/posts/, extracts metadata from frontmatter, composes an email,
and creates a draft in Buttondown for manual review before sending.

Usage:
    python scripts/newsletter_email.py

Environment variables:
    BUTTONDOWN_API_KEY  — Buttondown API token (required)
    GITHUB_SHA          — Current commit SHA (optional, defaults to HEAD)
    GITHUB_SHA_PREV     — Previous commit SHA (optional, defaults to HEAD~1)
    DRY_RUN             — If "true", print what would be sent without calling API
"""

import argparse
import os
import re
import subprocess
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

# Site configuration
SITE_URL = "https://www.datadelver.com"
POSTS_DIR = "docs/posts"
EXCERPT_SEPARATOR = "<!-- more -->"

# Regex patterns
DELVE_PREFIX = re.compile(r"^Delve\s*\d+:\s*", re.IGNORECASE)
YAML_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)^---\s*\n", re.MULTILINE | re.DOTALL)
MD_LEADING_BLOCKQUOTE = re.compile(r"(?:^>\s?.*\n?)+", re.MULTILINE)
MD_IMAGE = re.compile(r"!\[.*?\]\(.*?\)")
MD_LINK = re.compile(r"\[(.*?)\]\(.*?\)")
MD_BOLD = re.compile(r"\*\*(.*?)\*\*")
MD_ITALIC = re.compile(r"\*(.*?)\*")
MD_CODE = re.compile(r"`(.*?)`")
MD_HEADER = re.compile(r"^#{1,6}\s+(.*)", re.MULTILINE)
MD_BLOCKQUOTE = re.compile(r"^>\s?(.*)", re.MULTILINE)


def run_git(cmd: list[str]) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def find_new_posts(sha_prev: str, sha_curr: str) -> list[str]:
    """Find new .md files added to docs/posts/ between two commits."""
    # Handle the all-zeros SHA (first push to a branch)
    if sha_prev == "0" * 40:
        # Compare against the root commit
        diff_output = run_git(["ls-tree", "-r", "--name-only", sha_curr])
    else:
        diff_output = run_git(["diff", "--name-only", "--diff-filter=A", sha_prev, sha_curr])

    all_files = diff_output.split("\n") if diff_output else []

    new_posts = []
    for file in all_files:
        if file.startswith(POSTS_DIR + "/") and file.endswith(".md"):
            new_posts.append(file)

    return sorted(new_posts)


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug (lowercase, hyphenated)."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def extract_social_title(heading: str) -> str:
    """Extract a short title from an H1 heading.

    Strips the 'Delve N: ' prefix and takes text after the last comma if present.
    """
    title = DELVE_PREFIX.sub("", heading)
    if "," in title:
        title = title.rsplit(",", 1)[-1].strip()
    return title.strip()


def strip_markdown(text: str) -> str:
    """Strip markdown formatting and return plain text."""
    text = MD_IMAGE.sub("", text)
    text = MD_LINK.sub(r"\1", text)
    text = MD_BOLD.sub(r"\1", text)
    text = MD_ITALIC.sub(r"\1", text)
    text = MD_CODE.sub(r"\1", text)
    text = MD_HEADER.sub(r"\1", text)
    text = MD_BLOCKQUOTE.sub(r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|>)])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_post(filepath: str) -> dict:
    """Parse a blog post file and extract metadata and excerpt."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract front matter
    fm_match = YAML_FRONT_MATTER.search(content)
    frontmatter = {}
    if fm_match:
        fm_text = fm_match.group(1)
        for line in fm_text.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip().strip('"\'')

    # Extract title from first H1 heading
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    full_title = h1_match.group(1) if h1_match else os.path.basename(filepath)
    short_title = extract_social_title(full_title)

    # Generate URL slug
    slug = slugify(short_title)
    post_url = f"{SITE_URL}/posts/{slug}/"

    # Extract excerpt (content before separator)
    if EXCERPT_SEPARATOR in content:
        excerpt_md = content.split(EXCERPT_SEPARATOR, 1)[0]
    else:
        excerpt_md = content

    # Strip front matter, title, banner image, and blockquote
    excerpt_md = YAML_FRONT_MATTER.sub("", excerpt_md)
    excerpt_md = re.sub(r"^#{1,6}\s+.*$", "", excerpt_md, count=1, flags=re.MULTILINE)
    excerpt_md = MD_IMAGE.sub("", excerpt_md)
    excerpt_md = MD_LEADING_BLOCKQUOTE.sub("", excerpt_md)

    # Convert to plain text and truncate
    excerpt_text = strip_markdown(excerpt_md)
    max_length = 320
    if len(excerpt_text) > max_length:
        excerpt_text = excerpt_text[:max_length].rsplit(" ", 1)[0] + "..."

    return {
        "filepath": filepath,
        "date": frontmatter.get("date", ""),
        "categories": frontmatter.get("categories", ""),
        "full_title": full_title,
        "short_title": short_title,
        "slug": slug,
        "url": post_url,
        "excerpt": excerpt_text,
    }


def compose_email(posts: list[dict]) -> tuple[str, str]:
    """Compose the email subject and body from post metadata.

    Returns (subject, body) where body is in Markdown format.
    """
    if len(posts) == 1:
        subject = f"New on DataDelver: {posts[0]['short_title']}"
    else:
        titles = " · ".join(p["short_title"] for p in posts)
        subject = f"New on DataDelver: {titles}"

    # Build email body in Markdown
    lines = []
    lines.append(f"# {'New Delve' if len(posts) == 1 else 'New Delves'} on DataDelver!\n")

    if len(posts) == 1:
        lines.append(
            f"A new post just went live. Here's a preview:\n"
        )
    else:
        lines.append(
            f"{len(posts)} new posts just went live. Here's what's new:\n"
        )

    for i, post in enumerate(posts):
        if len(posts) > 1:
            lines.append(f"---\n")
            lines.append(f"## {i+1}. {post['short_title']}\n")
        else:
            lines.append(f"## {post['short_title']}\n")

        if post["excerpt"]:
            lines.append(f"{post['excerpt']}\n")

        lines.append(f"[Read the full delve →]({post['url']})\n")

    lines.append("---\n")
    lines.append(
        f"*Get new delves in your inbox. "
        f"[Subscribe to the newsletter]({SITE_URL}) "
        f"or [visit the blog]({SITE_URL})*"
    )

    body = "\n".join(lines)
    return subject, body


def send_to_buttondown(subject: str, body: str, api_key: str) -> dict:
    """Create a draft email via the Buttondown API.

    Returns the API response as a dict.
    """
    import json

    url = "https://api.buttondown.com/v1/emails"
    payload = json.dumps({
        "subject": subject,
        "body": body,
        "status": "draft",
    })

    req = Request(
        url,
        data=payload.encode("utf-8"),
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            resp_data = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "body": json.loads(resp_data),
            }
    except URLError as e:
        if hasattr(e, "read"):
            error_body = e.read().decode("utf-8")
        else:
            error_body = str(e)
        return {
            "status": e.code if hasattr(e, "code") else 500,
            "error": error_body,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Create a draft newsletter email for new blog posts."
    )
    parser.add_argument(
        "--sha-prev",
        default=None,
        help="Previous commit SHA (default: HEAD~1)",
    )
    parser.add_argument(
        "--sha-curr",
        default="HEAD",
        help="Current commit SHA (default: HEAD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent without calling the API",
    )
    args = parser.parse_args()

    # Resolve commit SHAs
    sha_curr = args.sha_curr or os.environ.get("GITHUB_SHA", "HEAD")
    sha_prev = args.sha_prev or os.environ.get("GITHUB_SHA_PREV", "HEAD~1")

    # Find new posts
    print(f"Comparing {sha_prev}..{sha_curr}")
    new_posts = find_new_posts(sha_prev, sha_curr)

    if not new_posts:
        print("No new posts found. Exiting.")
        sys.exit(0)

    print(f"Found {len(new_posts)} new post(s):")
    for post_file in new_posts:
        print(f"  - {post_file}")

    # Parse posts
    posts = []
    for post_file in new_posts:
        try:
            post = parse_post(post_file)
            posts.append(post)
            print(f"  Parsed: {post['short_title']}")
        except Exception as e:
            print(f"  Warning: Failed to parse {post_file}: {e}", file=sys.stderr)

    if not posts:
        print("No posts could be parsed. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Compose email
    subject, body = compose_email(posts)
    print(f"\n--- Email Preview ---")
    print(f"Subject: {subject}")
    print(f"\nBody:\n{body}")
    print(f"--- End Preview ---\n")

    # Dry run mode
    if args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true":
        print("Dry run mode — skipping API call.")
        sys.exit(0)

    # Get API key
    api_key = os.environ.get("BUTTONDOWN_API_KEY", "")
    if not api_key:
        print(
            "Error: BUTTONDOWN_API_KEY environment variable not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Send to Buttondown
    print("Creating draft email in Buttondown...")
    result = send_to_buttondown(subject, body, api_key)

    if result.get("status") and 200 <= result["status"] < 300:
        email_id = result.get("body", {}).get("id", "unknown")
        print(f"Success! Draft email created with ID: {email_id}")
        print(
            f"Review and send it in your Buttondown dashboard: "
            f"https://buttondown.com/datadelver/app/emails"
        )
    else:
        print(f"Error: Buttondown API returned status {result.get('status')}", file=sys.stderr)
        if "error" in result:
            print(f"Response: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
