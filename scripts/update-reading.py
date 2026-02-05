#!/usr/bin/env python3
"""
update-reading.py - Update the "Reading Now" section of your website

Usage:
    1. Edit reading.yaml with your book details
    2. For the image field, you can either:
       - Provide a direct URL (e.g., "https://example.com/cover.jpg")
       - Provide a filename and place the image in assets/img/
    3. Run: python3 update-reading.py

Supports 1 or 2 books in the "Reading Now" card.
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
YAML_FILE = os.path.join(SCRIPT_DIR, "reading.yaml")
HTML_FILE = os.path.join(ROOT_DIR, "index.html")


def parse_yaml(filepath):
    """Simple YAML parser for our specific format."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    result = {"books": [], "summary": ""}

    # Extract summary - handle quoted or unquoted, including apostrophes
    summary_match = re.search(r'^summary:\s*"(.+)"$', content, re.MULTILINE)
    if not summary_match:
        # Try unquoted (rest of line after "summary: ")
        summary_match = re.search(r'^summary:\s*(.+)$', content, re.MULTILINE)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()

    # Extract books
    book_blocks = re.split(r'\n\s*-\s+title:', content)[1:]
    for block in book_blocks:
        book = {}
        # Add back "title:" that was used as delimiter
        block = "title:" + block

        # Parse each field - try double-quoted first, then unquoted
        for field in ["title", "author", "image", "buy_url", "buy_label", "description"]:
            # Try double-quoted value first (handles apostrophes)
            pattern = rf'{field}:\s*"(.+)"'
            match = re.search(pattern, block)
            if not match:
                # Fall back to unquoted (rest of line)
                pattern = rf'{field}:\s*(.+?)(?:\n|$)'
                match = re.search(pattern, block)
            if match:
                book[field] = match.group(1).strip()
            else:
                book[field] = ""

        result["books"].append(book)

    return result


def get_image_src(image_value):
    """Return the appropriate image src - direct URL if provided, otherwise local path."""
    if image_value.startswith(('http://', 'https://')):
        return image_value
    return f"/assets/img/{image_value}"


def generate_html(data):
    """Generate the Reading Now card HTML."""
    books = data["books"]
    summary = data["summary"]
    num_books = len(books)

    # Build image section
    if num_books == 1:
        image_src = get_image_src(books[0]['image'])
        image_html = f'''<img alt="{books[0]['title']}" src="{image_src}" style="width: 100%;"
                    class="activator">'''
    else:
        image_src_0 = get_image_src(books[0]['image'])
        image_src_1 = get_image_src(books[1]['image'])
        image_html = f'''<div style="display: flex; justify-content: space-between;">
                  <img alt="{books[0]['title']}" src="{image_src_0}" style="width: 48%;"
                    class="activator">
                  <img alt="{books[1]['title']}" src="{image_src_1}"
                    style="width: 48%;" class="activator">
                </div>'''

    # Build details list
    details_items = []
    for book in books:
        if book.get("author"):
            details_items.append(
                f"<li>{book['title']} ({book['author']}): {book['description']}</li>"
            )
        else:
            details_items.append(f"<li>{book['title']}: {book['description']}</li>")
    details_html = "\n                  ".join(details_items)

    # Build action buttons
    action_items = []
    for book in books:
        action_items.append(
            f'''<a aria-label="Find `{book['title']}` on {book['buy_label']}"
                    href="{book['buy_url']}" target="_blank"
                    data-position="top" data-tooltip="Find `{book['title']}` on {book['buy_label']}"
                    class="btn-floating btn-large waves-effect waves-light blue-grey tooltipped">
                    <i class="fa fa-book"></i>
                  </a>'''
        )
    actions_html = "\n                  ".join(action_items)

    # Full card HTML
    return f'''<!-- Reading Now -->
          <div class="col s12 m6 l4">
            <div class="card medium">
              <div class="card-image waves-effect waves-block waves-light">
                {image_html}
              </div>
              <div class="card-content">
                <span class="card-title activator teal-text hoverline">Reading Now
                  <i class="mdi-navigation-more-vert right"></i>
                </span>
                <p>
                  {summary}
                </p>
              </div>
              <div class="card-reveal">
                <span class="card-title grey-text">
                  <small>Details</small>
                  <i class="mdi-navigation-close right"></i>
                </span>
                <ul>
                  {details_html}
                </ul>
                <div class="card-action">
                  {actions_html}
                </div>
              </div>
            </div>
          </div>
          <!-- Latest Creative Work -->'''


def update_html(new_card_html):
    """Replace the Reading Now section in index.html."""
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Create backup
    backup_file = HTML_FILE + ".bak"
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Replace the section between markers
    pattern = r"<!-- Reading Now -->.*?<!-- Latest Creative Work -->"
    new_content = re.sub(pattern, new_card_html, html_content, flags=re.DOTALL)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    if not os.path.exists(YAML_FILE):
        print(f"Error: {YAML_FILE} not found")
        sys.exit(1)

    print(f"Reading configuration from {YAML_FILE}...")
    data = parse_yaml(YAML_FILE)

    num_books = len(data["books"])
    print(f"Found {num_books} book(s)")

    for i, book in enumerate(data["books"], 1):
        print(f"  {i}. {book['title']}")

    new_html = generate_html(data)
    update_html(new_html)

    print("\nUpdated index.html successfully!")
    print()
    print("Next steps:")
    print("  1. Review the changes: git diff index.html")
    print("  2. Test locally: serve .")
    title = data["books"][0]["title"] if data["books"] else "update"
    print(f'  3. Commit: git add . && git commit -m "Reading: {title}"')


if __name__ == "__main__":
    main()
