#!/usr/bin/env python3
import sys
import glob
import os
import re
from pathlib import Path
import markdown
from typing import List, Tuple
from unidecode import unidecode

def find_replace_patterns(content: str) -> List[Tuple[str, str, str]]:
    """
    Find all file references in the format {{ path_to_file.ext }}
    Returns list of tuples (full_pattern, path, ext)
    """
    pattern = r'\{\{\s*([^\}]+\.(md|py|html))\s*\}\}'
    matches = re.finditer(pattern, content)
    return [(match.group(0), match.group(1).strip(), match.group(2).strip()) for match in matches]

def convert_markdown_to_html(md_path: str) -> str:
    """
    Read markdown file and convert it to HTML
    Returns empty string if file doesn't exist
    """
    if not os.path.exists(md_path):
        print(f"Warning: Markdown file not found: {md_path}")
        return ""

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['smarty', 'md_in_html'])
    return html_content

def insert_python_output(py_path: str) -> str:
    """
    Execute python file and capture its output
    """
    if not os.path.exists(py_path):
        print(f"Warning: Python file not found: {py_path}")
        return ""

    # Execute the python file
    output = os.popen(f"python {py_path}").read()
    return output

def insert_html(html_path: str) -> str:
    """
    Copy the content of an HTML file
    """

    if not os.path.exists(html_path):
        print(f"Warning: HTML file not found: {html_path}")
        return ""

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return html_content

def add_table_of_contents(html_content: str) -> str:
    """
    Check if the HTML contains the {{toc}} pattern.
    If it does, replace it with the table of contents.
    To do so, add an id to each heading and create a list of links.
    """
    # Find all headings of level 2, 3, and 4
    headings = re.findall(r'<h(2|3|4)>([^<]+)</h(2|3|4)>', html_content)

    # Create a list of links
    toc = "<ul>"
    prev_level = 2
    for level, title, _ in headings:
        level = int(level)

        # Add an id to the heading
        heading_id = re.sub(r'[^a-z ]', '', unidecode(title.lower())).replace(' ', '-')
        html_content = html_content.replace(f'<h{level}>{title}</h{level}>', f'<h{level} id="{heading_id}">{title}</h{level}>')

        # If the heading level is higher than the previous one, add a nested list
        if level > prev_level:
            toc += "<ul>"
        # If the heading level is lower than the previous one, close the nested list(s) until the correct level
        elif level < prev_level:
            toc += "</ul>" * (prev_level - level)
        prev_level = level

        # Add the link to the table of contents
        toc += f'<li><a href="#{heading_id}">{title}</a></li>'
    toc += "</ul>"

    # Replace the {{toc}} pattern with the table of contents
    return html_content.replace("{{toc}}", toc)


def process_html_file(src_path: str, dest_dir: str) -> None:
    """
    Process a single HTML file, replacing markdown references with HTML content
    """
    # Read the source HTML file
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all markdown patterns
    patterns = find_replace_patterns(content)

    ext_parser = {
        "md": convert_markdown_to_html,
        "py": insert_python_output,
        "html": insert_html
    }

    # Process each pattern
    for full_pattern, path, ext in patterns:
        # Convert markdown to HTML
        html_content = ext_parser[ext](path)
        # Replace the pattern with HTML content
        content = content.replace(full_pattern, html_content)

    # Add table of contents
    content = add_table_of_contents(content)

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Save the processed file to destination
    dest_path = os.path.join(dest_dir, os.path.basename(src_path))
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Processed: {src_path} -> {dest_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: build.py path_to_source(s).html dest_dir/")
        sys.exit(1)

    src_pattern = sys.argv[1]
    dest_dir = sys.argv[2]

    # Remove trailing slash from dest_dir if present
    dest_dir = dest_dir.rstrip('/')

    # Get list of source files using glob
    src_files = glob.glob(src_pattern)

    if not src_files:
        print(f"No files found matching pattern: {src_pattern}")
        sys.exit(1)

    # Process each source file
    for src_file in src_files:
        process_html_file(src_file, dest_dir)

    # copy the static folder to the destination using system command
    os.system(f"cp -r static {dest_dir}")


if __name__ == '__main__':
    main()
