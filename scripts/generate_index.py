#!/usr/bin/env python3
"""
Generate index.html for GitHub Pages site by scanning subfolders in site/
"""

import os
import re
from pathlib import Path

SITE_DIR = Path("site")

def parse_markdown(md_path: Path) -> dict:
    """Extract title and description from a markdown file."""
    content = md_path.read_text(encoding="utf-8")

    # Extract title from first H1 heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_path.parent.name

    # Extract description (first paragraph after title)
    lines = content.split("\n")
    description_lines = []
    in_description = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if in_description:
                break
            in_description = True
            continue
        if in_description and stripped:
            description_lines.append(stripped)
        elif in_description and not stripped and description_lines:
            break

    description = " ".join(description_lines) if description_lines else ""

    return {"title": title, "description": description}


def get_subfolders() -> list[dict]:
    """Scan site/ directory for subfolders with content."""
    entries = []

    if not SITE_DIR.exists():
        return entries

    for item in sorted(SITE_DIR.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue

        # Look for markdown file (README.md or description.md)
        md_file = None
        for md_name in ["README.md", "description.md", "index.md"]:
            candidate = item / md_name
            if candidate.exists():
                md_file = candidate
                break

        if md_file:
            info = parse_markdown(md_file)
        else:
            info = {"title": item.name, "description": ""}

        info["folder"] = item.name
        entries.append(info)

    return entries


def generate_html(entries: list[dict]) -> str:
    """Generate the index.html content."""

    entries_html = ""
    for entry in entries:
        desc_html = f'<p class="description">{entry["description"]}</p>' if entry["description"] else ""
        entries_html += f"""
        <li class="entry">
            <a href="{entry['folder']}/index.html">
                <h2>{entry['title']}</h2>
                {desc_html}
            </a>
        </li>
"""

    if not entries:
        entries_html = '<li class="empty">No content yet.</li>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Published Content</title>
    <style>
        :root {{
            --bg-color: #f5f5f5;
            --text-color: #333;
            --link-color: #0066cc;
            --card-bg: #fff;
            --border-color: #ddd;
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1a1a1a;
                --text-color: #e0e0e0;
                --link-color: #6db3f2;
                --card-bg: #2d2d2d;
                --border-color: #444;
            }}
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        h1 {{
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        .entry {{
            margin: 1rem 0;
            padding: 1rem;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            transition: box-shadow 0.2s;
        }}
        .entry:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .entry a {{
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .entry h2 {{
            margin: 0 0 0.5rem 0;
            color: var(--link-color);
            font-size: 1.25rem;
        }}
        .description {{
            margin: 0;
            color: var(--text-color);
            opacity: 0.8;
        }}
        .empty {{
            color: var(--text-color);
            opacity: 0.6;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1>Published Content</h1>
    <ul>
{entries_html}
    </ul>
</body>
</html>
"""
    return html


def main():
    entries = get_subfolders()
    html = generate_html(entries)

    output_path = SITE_DIR / "index.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Generated {output_path} with {len(entries)} entries")


if __name__ == "__main__":
    main()
