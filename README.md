# DataDelver

Repository for my personal blog: https://www.datadelver.com/

## About

DataDelver is a technical blog focused on Data Science, Machine Learning, and MLOps. The site is built using [MkDocs](https://www.mkdocs.org/) with the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

## Setup

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (fast Python package installer, recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DataDelver/datadelver.github.io.git
   cd datadelver.github.io
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install dependencies using uv (recommended):
   ```bash
   uv sync
   ```

   Alternatively, you can use pip:
   ```bash
   pip install -e .
   ```

## Usage

### Building the Site

You can use the `just` command runner for common tasks:

- **Build the site**:
  ```bash
  just doc
  ```
  This will generate static HTML files in the `site/` directory.

- **Serve the site locally** (with live reloading):
  ```bash
  just serve
  ```
  Access the site at `http://localhost:8000`

- **Clean the build**:
  ```bash
  just clean
  ```
  Removes the `site/` directory

Alternatively, you can use mkdocs directly:

- Build:
  ```bash
  mkdocs build
  ```

- Serve:
  ```bash
  mkdocs serve
  ```

### Writing Posts

Blog posts are written in Markdown format and should be placed in the root directory of the repository. Each post should include:

- Front matter with metadata (title, date, tags, etc.)
- A post excerpt (required)
- Content organized with appropriate headers

## Project Structure

```
.
├── docs/                  # MkDocs documentation (if any)
├── layouts/               # Theme layouts and templates
├── overrides/             # Theme overrides
├── site/                  # Generated static site (auto-created)
├── .cache/                # MkDocs cache
├── .github/               # GitHub workflows and configuration
├── .gitignore             # Git ignore rules
├── .python-version        # Python version requirement
├── justfile               # Just command recipes
├── mkdocs.yml             # MkDocs configuration
├── pyproject.toml         # Python project configuration
├── README.md              # This file
└── uv.lock                # UV dependency lock file
```

## Configuration

The site configuration is managed in `mkdocs.yml`. Key settings include:

- **Theme**: Material for MkDocs with custom color schemes
- **Plugins**: Blog, tags, search, social cards, RSS feed, and redirects
- **Markdown Extensions**: Syntax highlighting, admonitions, details, and more

## Contributing

While this is a personal blog, contributions and feedback are welcome! Feel free to open issues or pull requests with suggestions for improvements or additional content.

## License

Copyright &copy; 2023 - 2026 Chase Greco

All content is licensed under CC BY-SA 4.0 unless otherwise noted.
