# Justfile for the DataDelver blog

# Build the site with mkdocs
doc:
    #!/usr/bin/env bash
    mkdocs build

# Serve the site with live reloading
serve:
    #!/usr/bin/env bash
    mkdocs serve

# Clean the site build
clean:
    #!/usr/bin/env bash
    rm -rf site