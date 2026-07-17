#!/usr/bin/env python3
"""Detect a new blog post and create a draft newsletter email via Buttondown API.

This script is designed to run in a GitHub Actions workflow on push to main.
It compares the latest commit against the previous one to find a new .md file
added to docs/posts/, extracts metadata from frontmatter, composes an email,
and creates a draft in Buttondown for manual review before sending.

Expects exactly one new post per run. Multiple posts in a single push will
trigger separate workflow runs via the concurrency group.

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

# Add project root to path so we can import from plugins/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from plugins.text_utils import (  # noqa: E402
    YAML_FRONT_MATTER,
    build_post_url,
    extract_excerpt,
    extract_social_title,
    slugify,
)

# Site configuration
SITE_URL = "https://www.datadelver.com"
POSTS_DIR = "docs/posts"


def run_git(cmd: list[str]) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def find_new_post(sha_prev: str, sha_curr: str) -> str:
    """Find the new .md file added to docs/posts/ between two commits.

    Returns the filepath of a single new post, or empty string if none found.
    Exits with error if more than one new post is detected.
    """
    if sha_prev == "0" * 40:
        diff_output = run_git(["ls-tree", "-r", "--name-only", sha_curr])
    else:
        diff_output = run_git([
            "diff",
            "--name-only",
            "--diff-filter=A",
            sha_prev,
            sha_curr,
        ])

    all_files = diff_output.split("\n") if diff_output else []
    new_posts = [
        f for f in all_files if f.startswith(POSTS_DIR + "/") and f.endswith(".md")
    ]

    if not new_posts:
        return ""
    if len(new_posts) > 1:
        print(
            f"Error: {len(new_posts)} new posts found. Expected exactly one. Exiting.",
            file=sys.stderr,
        )
        for post in new_posts:
            print(f"  - {post}", file=sys.stderr)
        sys.exit(1)

    return new_posts[0]


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
                frontmatter[key.strip()] = value.strip().strip("\"'")

    # Extract title from first H1 heading
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    full_title = h1_match.group(1) if h1_match else os.path.basename(filepath)
    short_title = extract_social_title(full_title)

    # Generate URL slug
    slug = slugify(short_title)

    # Parse post date
    post_date = frontmatter.get("date", "")

    # Build post URL using shared utility (matches blog plugin's URL format)
    post_url = build_post_url(SITE_URL, slug, post_date)

    # Generate social card URL from date and slug
    # Pattern: /assets/images/social/YYYY/MM/DD/slug.png
    social_card_url = None
    if post_date and len(post_date) >= 10:
        try:
            year = post_date[:4]
            month = post_date[5:7]
            day = post_date[8:10]
            social_card_url = (
                f"{SITE_URL}/assets/images/social/{year}/{month}/{day}/{slug}.png"
            )
        except (IndexError, ValueError):
            pass

    # Extract excerpt using shared utility
    excerpt_text = extract_excerpt(content)

    return {
        "filepath": filepath,
        "date": post_date,
        "categories": frontmatter.get("categories", ""),
        "full_title": full_title,
        "short_title": short_title,
        "slug": slug,
        "url": post_url,
        "excerpt": excerpt_text,
        "social_card_url": social_card_url,
    }


def compose_email(post: dict) -> tuple[str, str]:
    """Compose the email subject and body from a single post.

    Returns (subject, body) where body is in Markdown format.
    """
    subject = f"New on DataDelver: {post['short_title']}"

    lines = []
    lines.append("# New Delve on DataDelver!\n")
    lines.append("A new post just went live. Here's a preview:\n")

    # Embed social card image (linked to post)
    if post.get("social_card_url"):
        lines.append(
            f"[![{post['short_title']}]({post['social_card_url']})]({post['url']})\n"
        )

    if post["excerpt"]:
        lines.append(f"{post['excerpt']}\n")

    # Link to full post
    lines.append(f"[Read the full post →]({post['url']})\n")

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
        description="Create a draft newsletter email for a new blog post."
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

    # Find new post
    print(f"Comparing {sha_prev}..{sha_curr}")
    post_file = find_new_post(sha_prev, sha_curr)

    if not post_file:
        print("No new post found. Exiting.")
        sys.exit(0)

    print(f"Found new post: {post_file}")

    # Parse post
    try:
        post = parse_post(post_file)
        print(f"  Parsed: {post['short_title']}")
    except Exception as e:
        print(f"Error: Failed to parse {post_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Compose email
    subject, body = compose_email(post)
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
        print(f"Open in dashboard: https://buttondown.com/emails/{email_id}")
    else:
        print(
            f"Error: Buttondown API returned status {result.get('status')}",
            file=sys.stderr,
        )
        if "error" in result:
            print(f"Response: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
