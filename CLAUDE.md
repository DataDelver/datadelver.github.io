# Claude Instructions for DataDelver Blog

## Python Package Management

**Always use `uv`** for Python package management — never use `pip` directly.

```bash
# Sync the environment with pyproject.toml (install project + dependencies)
uv sync

# Add a dependency
uv add <package>

# Remove a dependency
uv remove <package>
```

The project requires Python >= 3.13. The virtual environment lives in `.venv/`.

## Local MkDocs Plugins

Custom MkDocs plugins are registered via entry points in `pyproject.toml` under `[project.entry-points."mkdocs.plugins"]`. After adding or modifying a plugin, you **must** re-sync the environment for changes to take effect:

```bash
uv sync
```

Current custom plugins (in `plugins/`):

| Plugin                | File                                                     | Purpose                                        |
| --------------------- | -------------------------------------------------------- | ---------------------------------------------- |
| `excerpt_description` | [excerpt_description.py](plugins/excerpt_description.py) | Generates excerpt-based descriptions for posts |
| `json_ld`             | [json_ld.py](plugins/json_ld.py)                         | Injects JSON-LD structured data                |
| `lazy_images`         | [lazy_images.py](plugins/lazy_images.py)                 | Adds `loading="lazy"` to non-hero images       |
| `related_posts`       | [related_posts.py](plugins/related_posts.py)             | Shows related posts sidebar                    |
| `series_nav`          | [series_nav.py](plugins/series_nav.py)                   | Auto-generates series nav from shared tags     |

## Pre-commit Hooks

A pre-commit hook converts new PNG images to WebP automatically. Install it with:

```bash
pre-commit install
```

The hook is configured in [.pre-commit-config.yaml](.pre-commit-config.yaml) and calls [hooks/convert_images.py](hooks/convert_images.py), which handles `banners/`, `figures/`, `favicon/`, and `avatar/` directories.

## Just Commands

Run `just` to see all available commands:

| Command                   | Description                         |
| ------------------------- | ----------------------------------- |
| `just doc`                | Build the site with MkDocs          |
| `just serve`              | Serve the site with live reloading  |
| `just pre-commit-install` | Install pre-commit hooks            |
| `just lint`               | Check markdown formatting (dry run) |
| `just lint-fix`           | Fix markdown formatting in place    |
| `just clean`              | Remove the `site/` build directory  |

See [Justfile](Justfile) for the full list.
