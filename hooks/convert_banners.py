#!/usr/bin/env python3
"""Pre-commit hook: Convert banner PNGs to WebP and update references."""

import sys
import os
import glob
import subprocess

def convert_banners():
    """Convert PNG banners to WebP and update file references."""
    banner_dir = "docs/assets/images/banners"
    png_files = glob.glob(os.path.join(banner_dir, "*.png"))
    
    if not png_files:
        return 0  # Nothing to do
    
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed - skipping banner conversion")
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
    result = subprocess.run(
        ["find", "docs/", "overrides/", "-type", "f", r"\(", "-name", "*.md", "-o", "-name", "*.html", r"\)",
         "-exec", "sed", "-i", "s|banners/\(.*\)\.png|banners/\1.webp|g", "{}", "+"],
        capture_output=True
    )
    
    # Stage all changes
    subprocess.run(["git", "add"] + [path for _, path in converted] + ["docs/", "overrides/"])
    
    # Remove original PNGs and stage deletions
    for png_path, _ in converted:
        os.remove(png_path)
        subprocess.run(["git", "add", png_path])
    
    print(f"Converted {len(converted)} banner(s) from PNG to WebP")
    return 0

if __name__ == "__main__":
    sys.exit(convert_banners())
