# Newsletter Setup

This blog uses [Buttondown](https://buttondown.com/) for newsletter delivery. When a new post is published, a draft email is automatically created via the Buttondown API so you can review and send it manually.

## How It Works

1. **Push to `main`** — When new `.md` files are added to `docs/posts/`, the `newsletter-email` GitHub Actions workflow triggers.

1. **Detect new posts** — The workflow compares the new commit(s) against the previous state to find newly added post files.

1. **Compose email** — For each new post, the script extracts the title, excerpt, and URL from the markdown file and composes a formatted email.

1. **Create draft** — The email is sent to Buttondown's API with `status: "draft"`, which creates a draft in your Buttondown dashboard without sending it.

1. **Review and send** — Visit your [Buttondown dashboard](https://buttondown.com/datadelver/app/emails) to review, edit, and send the draft when ready.

## Configuration

### GitHub Repository Secret

Set the following secret in your GitHub repository settings:

| Secret               | Description                                         |
| -------------------- | --------------------------------------------------- |
| `BUTTONDOWN_API_KEY` | Your Buttondown API token (found in Settings → API) |

### Creating an API Token

1. Log in to your [Buttondown dashboard](https://buttondown.com/datadelver/app)
1. Go to **Settings** → **API**
1. Click **Create API key**
1. Give it a label (e.g., "GitHub Actions")
1. Copy the token and add it as a GitHub secret

## Local Testing

Preview what the newsletter email would look like without calling the API:

```bash
# Preview for the last commit
just newsletter-draft 1

# Preview for the last 3 commits
just newsletter-draft 3
```

Or run the script directly:

```bash
python3 scripts/newsletter_email.py --sha-prev HEAD~1 --sha-curr HEAD --dry-run
```

## Email Format

The generated email uses Markdown formatting and includes:

- **Subject**: `New on DataDelver: {post title}` (single post) or `New on DataDelver: {title1} · {title2}` (multiple posts)
- **Body**:
    - Heading with post count
    - For each post: title, excerpt (first ~320 chars before `<!-- more -->`), and "Read more" link
    - Footer with subscription link

## Workflow File

The workflow is defined in [`.github/workflows/newsletter-email.yml`](.github/workflows/newsletter-email.yml) and triggers on:

- Push to `main` branch
- Only when files in `docs/posts/` are modified

## Troubleshooting

### Draft not created

1. Check the [GitHub Actions](https://github.com/DataDelver/datadelver.github.io/actions) tab for the `newsletter-email` workflow
1. Verify the `BUTTONDOWN_API_KEY` secret is set correctly
1. Check that the push included new files in `docs/posts/`

### Wrong excerpt

The excerpt is extracted from content before the `<!-- more -->` separator. Ensure your posts have this separator after the introduction paragraph.

### API errors

Common Buttondown API errors:

- `401 Unauthorized` — Invalid API key
- `400 Bad Request` — Malformed request (check script output)
- `429 Too Many Requests` — Rate limited (wait and retry)
