# Justfile for the DataDelver blog

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