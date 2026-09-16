"""Markdown to HTML Converter: Line-by-line parser converting Markdown elements into HTML documents."""

import os
import re

CSS_STYLES = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 20px;
    color: #24292f;
    background-color: #ffffff;
}
h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}
h1 { border-bottom: 1px solid #d0d7de; padding-bottom: 8px; }
h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 6px; }
code {
    background-color: #f6f8fa;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 85%;
}
blockquote {
    border-left: 4px solid #d0d7de;
    margin: 0;
    padding: 0 16px;
    color: #57606a;
}
ul { padding-left: 24px; }
li { margin-bottom: 4px; }
hr { height: 2px; background-color: #d0d7de; border: none; margin: 24px 0; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
"""


def parse_inline_elements(text):
    """Parse inline formatting: bold, italic, inline code, and hyperlinks."""
    # Inline code: `code`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Bold: **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    # Italic: *text*
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

    # Links: [anchor](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    return text


def convert_markdown_lines(md_lines):
    """State-machine parser converting a list of markdown lines to HTML strings."""
    html_lines = []
    in_list = False

    for raw_line in md_lines:
        line = raw_line.rstrip()

        # Handle list items
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item_text = parse_inline_elements(line[2:].strip())
            html_lines.append(f"  <li>{item_text}</li>")
            continue
        elif in_list:
            html_lines.append("</ul>")
            in_list = False

        # Blank line
        if not line:
            continue

        # Horizontal rule
        if line == "***" or (len(line) >= 3 and set(line) == {"-"}):
            html_lines.append("<hr>")
            continue

        # Headings: # through ######
        if line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            if 1 <= hashes <= 6 and line[hashes : hashes + 1] == " ":
                content = parse_inline_elements(line[hashes + 1 :].strip())
                html_lines.append(f"<h{hashes}>{content}</h{hashes}>")
                continue

        # Blockquote: > text
        if line.startswith("> "):
            content = parse_inline_elements(line[2:].strip())
            html_lines.append(f"<blockquote><p>{content}</p></blockquote>")
            continue

        # Standard Paragraph
        content = parse_inline_elements(line)
        html_lines.append(f"<p>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    return html_lines


def generate_full_html_document(html_body, title="Converted Document"):
    """Wrap converted HTML lines in a clean, modern HTML5 boilerplate."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{CSS_STYLES}
    </style>
</head>
<body>
{chr(10).join(html_body)}
</body>
</html>
"""


def convert_file():
    """Read a Markdown file and write an HTML file."""
    print("\n=== Convert Markdown File to HTML ===")
    in_path = input("Enter path to input Markdown (.md) file: ").strip()

    if not os.path.isfile(in_path):
        print(f"Error: File '{in_path}' does not exist.")
        return

    out_path = input("Enter path for output HTML file (default 'output.html'): ").strip()
    if not out_path:
        out_path = "output.html"

    doc_title = input("Enter webpage title (default filename): ").strip()
    if not doc_title:
        doc_title = os.path.basename(in_path)

    try:
        with open(in_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        body_elements = convert_markdown_lines(lines)
        full_html = generate_full_html_document(body_elements, title=doc_title)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"\n[Success] Converted '{in_path}' -> '{out_path}' ({len(body_elements)} HTML tags generated).")
    except (OSError, UnicodeDecodeError) as error:
        print(f"\n[Error] Conversion failed: {error}")


def interactive_mode():
    """Allow typing markdown interactively and viewing HTML output."""
    print("\n=== Interactive Markdown Preview ===")
    print("Enter markdown text lines. Press Enter on an empty line when finished:\n")

    input_lines = []
    while True:
        line = input("> ")
        if line == "":
            break
        input_lines.append(line)

    if not input_lines:
        print("No text provided.")
        return

    converted = convert_markdown_lines(input_lines)
    print("\n" + "=" * 50)
    print("HTML OUTPUT:")
    print("=" * 50)
    for tag in converted:
        print(tag)
    print("=" * 50 + "\n")


def main():
    while True:
        print("=" * 45)
        print("    MARKDOWN TO HTML CONVERTER")
        print("=" * 45)
        print("1. Convert Markdown File to HTML")
        print("2. Interactive Line-by-Line Preview")
        print("3. Exit")
        print("=" * 45)

        choice = input("Select option (1-3): ").strip()

        if choice == "1":
            convert_file()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            print("\nExiting Markdown to HTML Converter. Goodbye!")
            break
        else:
            print("\nInvalid option. Please choose 1, 2, or 3.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
