#!/usr/bin/env python3
"""Pre-commit hook: Convert PNG images (banners, figures, favicon, avatar) to WebP and update references."""

import sys
import os
import glob
import subprocess

# Directories to scan for PNG files (relative to repo root)
IMAGE_DIRS = [
    "docs/assets/images/banners",
    "docs/assets/images/figures",
    "docs/assets/images/favicon",
    "docs/assets/images/avatar",
]

# Subdirectory names used in references (for sed replacement patterns)
REFERENCE_PATTERNS = [
    ("banners/", "WEBP"),      # banners always converted
    ("figures/", "WEBP"),      # figures always converted
    ("favicon/", "WEBP"),      # favicon converted
    ("avatar/", "WEBP"),       # avatar converted
]


def find_png_files():
    """Find all PNG files in the configured image directories."""
    png_files = []
    for image_dir in IMAGE_DIRS:
        if os.path.isdir(image_dir):
            # Handle both flat dirs and subdirectories (figures has subdirs)
            pattern = os.path.join(image_dir, "**", "*.png")
            png_files.extend(glob.glob(pattern, recursive=True))
            # Also check flat pattern for dirs without subdirs
            flat_pattern = os.path.join(image_dir, "*.png")
            png_files.extend(glob.glob(flat_pattern))
    return sorted(set(png_files))


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
            if img.mode in ('P', 'LA'):
                img = img.convert('RGB')
            elif img.mode == 'LA':
                img = img.convert('RGBA')

            webp_path = png_path.replace('.png', '.webp')
            img.save(webp_path, 'WEBP', quality=82, method=4)
            converted.append((png_path, webp_path))
        except Exception as e:
            print(f"Warning: Failed to convert {png_path}: {e}")

    if not converted:
        return 0

    # Update references in markdown and HTML files
    for pattern, _ in REFERENCE_PATTERNS:
        result = subprocess.run(
            ["find", "docs/", "overrides/", "-type", "f", r"\(", "-name", "*.md", "-o", "-name", "*.html", r"\)",
             "-name", "*.yml", "-name", "*.yaml", r"\)",
             "-exec", "sed", "-i", f"s|{pattern}\\(.*\\)\\.png|{pattern}\\1.webp|g", "{}", "+"],
            capture_output=True
        )

    # Stage all changes
    subprocess.run(["git", "add"] + [path for _, path in converted] + ["docs/", "overrides/"])

    # Remove original PNGs and stage deletions
    for png_path, _ in converted:
        os.remove(png_path)
        subprocess.run(["git", "add", png_path])

    print(f"Converted {len(converted)} image(s) from PNG to WebP")
    return 0

if __name__ == "__main__":
    sys.exit(convert_images())
