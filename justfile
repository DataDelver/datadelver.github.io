# Justfile for the DataDelver blog

# Default command: List all available commands
default:
    @just --list

# Build the site with mkdocs
doc:
    #!/usr/bin/env bash
    mkdocs build

# Serve the site with live reloading
serve:
    #!/usr/bin/env bash
    mkdocs serve

# Install pre-commit hook
pre-commit-install:
    pre-commit install

# Check markdown formatting (dry run)
lint:
    mdformat --check docs/

# Fix markdown formatting in place
lint-fix:
    mdformat docs/

# Clean the site build
clean:
    #!/usr/bin/env bash
    rm -rf site

# Preview generated social cards in the browser
preview-cards:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -d "site/assets/images/social" ]; then
        echo "No social cards found. Run 'just doc' first."
        exit 1
    fi
    python3 scripts/generate_card_preview.py
    xdg-open card_preview.html

# Scaffold a new blog post
## Usage: just new-post "My Post Title"
new-post title:
    python3 scripts/new_post.py "{{title}}"
