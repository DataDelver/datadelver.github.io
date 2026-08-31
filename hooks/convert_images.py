#!/usr/bin/env python3
"""Pre-commit hook: Convert PNG images (banners, figures, avatar) to WebP and update references."""

import sys
import os
import glob
import re

# Directories to scan for PNG files (relative to repo root)
# Note: favicon/ is excluded - RSS feeds require PNG/JPEG/GIF, not WebP
IMAGE_DIRS = [
    "docs/assets/images/banners",
    "docs/assets/images/figures",
    "docs/assets/images/avatar",
]

# Directory subpath prefixes whose .png references should be rewritten to .webp
REFERENCE_PREFIXES = ["banners/", "figures/", "avatar/"]

# Directories scanned for reference files (plus root config files)
REFERENCE_DIRS = ["docs", "overrides"]
REFERENCE_ROOT_FILES = ["mkdocs.yml"]
REFERENCE_EXTS = {".md", ".html", ".yml", ".yaml", ".css"}


def find_png_files():
    """Find all PNG files in the configured image directories."""
    png_files = []
    for image_dir in IMAGE_DIRS:
        if os.path.isdir(image_dir):
            # ** matches zero or more subdirectories, so this covers flat files too
            pattern = os.path.join(image_dir, "**", "*.png")
            png_files.extend(glob.glob(pattern, recursive=True))
    return sorted(set(png_files))


def find_reference_files():
    """Find markdown, HTML, config, and CSS files that may reference images."""
    files = []
    for ref_dir in REFERENCE_DIRS:
        if not os.path.isdir(ref_dir):
            continue
        for root, _, names in os.walk(ref_dir):
            for name in names:
                if os.path.splitext(name)[1].lower() in REFERENCE_EXTS:
                    files.append(os.path.join(root, name))
    for root_file in REFERENCE_ROOT_FILES:
        if os.path.isfile(root_file):
            files.append(root_file)
    return files


def update_references():
    """Rewrite .png references under image dirs to .webp. Returns list of changed files."""
    changed = []
    for prefix in REFERENCE_PREFIXES:
        # Exclude ), whitespace, and quotes from the filename capture so that
        # multiple references on one line are each replaced correctly.
        pattern = re.compile(re.escape(prefix) + r"([^)\s\"']*)\.png")
        replacement = prefix + r"\1.webp"
        for path in find_reference_files():
            try:
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            new_content = pattern.sub(replacement, content)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new_content)
                changed.append(path)
    return changed


def convert_images():
    """Convert PNG images to WebP and update file references."""
    png_files = find_png_files()

    if not png_files:
        return 0  # Nothing to do

    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed - skipping image conversion")
        return 0

    converted = []
    for png_path in png_files:
        try:
            img = Image.open(png_path)
            if img.mode in ("P", "LA"):
                img = img.convert("RGBA")

            webp_path = png_path.replace(".png", ".webp")
            img.save(webp_path, "WEBP", quality=82, method=4)
            converted.append((png_path, webp_path))
        except Exception as e:
            print(f"Warning: Failed to convert {png_path}: {e}")

    if not converted:
        return 0

    # Update references in markdown, HTML, config, and CSS files
    changed_files = update_references()

    # Stage converted WebPs, updated references, and remove the original PNGs
    import subprocess
    subprocess.run(["git", "add"] + [webp for _, webp in converted] + changed_files)
    for png_path, _ in converted:
        os.remove(png_path)
        subprocess.run(["git", "add", png_path])

    print(f"Converted {len(converted)} image(s) from PNG to WebP")
    if changed_files:
        print(f"Updated references in {len(set(changed_files))} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(convert_images())
