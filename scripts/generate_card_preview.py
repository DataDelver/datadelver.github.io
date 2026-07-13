#!/usr/bin/env python3
"""Generate an HTML page to preview all social cards."""

import glob
import os


def main():
    social_dir = "site/assets/images/social"
    cards = []

    # Collect all card images (PNG files)
    for path in glob.glob(os.path.join(social_dir, "**", "*.png"), recursive=True):
        # Extract relative path from social dir
        rel = os.path.relpath(path, social_dir)
        parts = rel.replace(os.sep, "/").split("/")
        if len(parts) >= 3:
            year, month, day = parts[0], parts[1], parts[2]
            filename = parts[3] if len(parts) > 3 else parts[2]
            date_str = f"{year}-{month}-{day}"
        elif len(parts) == 2:
            year, month = parts[0], parts[1]
            filename = parts[1]
            date_str = f"{year}-{month}"
        else:
            date_str = "root"
            filename = parts[0]

        cards.append({
            "path": f"site/assets/images/social/{rel}",
            "date": date_str,
            "filename": filename,
        })

    # Sort by date descending
    cards.sort(key=lambda c: c["date"], reverse=True)

    # Generate HTML
    cards_html = ""
    for card in cards:
        cards_html += f"""        <div class="card">
            <img src="{card['path']}" alt="{card['filename']}">
            <div class="card-info">
                <span class="date">{card['date']}</span>
            </div>
        </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Cards Preview</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            padding: 2rem;
        }}
        h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }}
        .subtitle {{
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: #16213e;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #2a2a4a;
        }}
        .card img {{
            width: 100%;
            display: block;
        }}
        .card-info {{
            padding: 0.75rem 1rem;
            font-size: 0.75rem;
            color: #888;
        }}
        .card-info .date {{
            color: #526cfe;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <h1>Social Cards Preview</h1>
    <p class="subtitle">{len(cards)} cards found</p>
    <div class="grid">
{cards_html}    </div>
</body>
</html>
"""

    with open("card_preview.html", "w") as f:
        f.write(html)

    print(f"Generated card_preview.html with {len(cards)} cards")


if __name__ == "__main__":
    main()
