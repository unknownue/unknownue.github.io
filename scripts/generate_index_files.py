#!/usr/bin/env python3
"""
Automatically generate _index.md files for content/pull_request directory and its subdirectories.
Also adds front matter to Markdown files that don't have it.
"""

import os
import re
from datetime import datetime

# Project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Target directory to process
CONTENT_DIR = os.path.join(ROOT_DIR, "content", "pull_request")

def format_title(dir_name):
    """Format directory name as a title"""
    # Handle year-month format (e.g., 2025-03)
    year_month_match = re.match(r'(\d{4})-(\d{2})', dir_name)
    if year_month_match:
        year, month = year_month_match.groups()
        month_name = datetime.strptime(month, "%m").strftime("%B")
        return f"{month_name} {year}"
    
    # Handle regular directory names (e.g., bevy)
    return dir_name.replace("_", " ").title()

def create_index_file(dir_path):
    """Create _index.md file for the specified directory"""
    index_path = os.path.join(dir_path, "_index.md")
    
    # Skip if file already exists
    if os.path.exists(index_path):
        print(f"Skipping existing file: {index_path}")
        return
    
    # Get directory name
    dir_name = os.path.basename(dir_path)
    title = format_title(dir_name)
    
    # Create _index.md content
    content = f"""+++
title = "{title}"
sort_by = "date"
template = "pull_request.html"
+++
"""
    
    # Write to file
    with open(index_path, "w") as f:
        f.write(content)
    
    print(f"Created: {index_path}")

def process_directory(dir_path):
    """Process directory and its subdirectories"""
    # Create _index.md for current directory
    create_index_file(dir_path)
    
    # Process subdirectories
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            process_directory(item_path)

def get_language_name(lang_code):
    """Return the full name of a language based on its code"""
    language_names = {
        "en": "English",
        "zh-cn": "中文",
        "fr": "Français",
        # Add more languages as needed
    }
    return language_names.get(lang_code, lang_code)

def find_language_versions(file_path, pr_number):
    """Find all language versions of a PR and return them as a dictionary"""
    dir_path = os.path.dirname(file_path)
    available_languages = {}
    
    # Get all files in the same directory
    for file in os.listdir(dir_path):
        if file.endswith(".md") and file != "_index.md":
            # Look for PR number and language code in filename
            # Updated to handle both formats: pr_18143_zh-cn_20250303.md and pr_18143_zh-cn_20250303_215251.md
            match = re.search(r'pr_(\d+)(?:_([a-z]{2}(?:-[a-z]{2})?))?_', file)
            if match and match.group(1) == pr_number:
                # Extract language code or default to "en"
                lang_code = match.group(2) if match.group(2) else "en"
                lang_name = get_language_name(lang_code)
                
                # Create relative URL for this language version
                # Replace underscores with hyphens to match Zola's URL generation rules
                # Do not include .html suffix as Zola generates clean URLs
                file_name_without_ext = os.path.splitext(file)[0]
                file_name_with_hyphens = file_name_without_ext.replace('_', '-')
                rel_dir_path = os.path.relpath(dir_path, CONTENT_DIR)
                url = f"/pull_request/{rel_dir_path}/{file_name_with_hyphens}"
                url = url.replace(os.sep, '/')
                
                available_languages[lang_code] = {
                    "name": lang_name,
                    "url": url
                }
    
    return available_languages

def ensure_front_matter(md_file_path):
    """Ensure Markdown file has front matter"""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract information from filename
    filename = os.path.basename(md_file_path)
    # Look for PR number, language code, and datetime in format: pr_18143_zh-cn_20250303_215251.md
    # Updated to handle both formats: pr_18143_zh-cn_20250303.md and pr_18143_zh-cn_20250303_215251.md
    match = re.search(r'pr_(\d+)(?:_([a-z]{2}(?:-[a-z]{2})?))?_(\d{8})(?:_\d{6})?', filename)
    
    title = "Pull Request"
    language_code = "en"  # Default language
    
    if match:
        pr_number = match.group(1)
        # Extract language code if present, otherwise default to "en"
        language_code = match.group(2) if match.group(2) else "en"
        date_str = match.group(3)
        # Time part is now optional and ignored for processing
        
        title = f"PR #{pr_number}"
        
        # Try to extract a better title from content
        # Look for "**标题**:" pattern which contains the PR title in Chinese docs
        title_match = re.search(r'\*\*标题\*\*:\s*`?(.*?)`?(?:\r?\n|\*\*)', content)
        if title_match:
            title = title_match.group(1).strip()
        
        # Format date (YYYYMMDD -> YYYY-MM-DD 00:00)
        date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T00:00:00"
        
        # Find other language versions of the same PR
        available_languages = find_language_versions(md_file_path, pr_number)
        
        # Format available languages as TOML table
        languages_toml = "{"
        for lang, info in available_languages.items():
            languages_toml += f'"{lang}" = {{ name = "{info["name"]}", url = "{info["url"]}" }}, '
        languages_toml = languages_toml.rstrip(", ") + "}"
        
        # Determine if this file should be included in search index
        # Only include English version in search index and PR list
        in_search_index = language_code == "en"
        
        # Check if file already has front matter
        if content.startswith("+++"):
            # Extract existing front matter and content
            front_matter_match = re.match(r'\+\+\+(.*?)\+\+\+', content, re.DOTALL)
            if front_matter_match:
                # Extract content after front matter
                content_after_front_matter = content[front_matter_match.end():]
                
                # Create new front matter with language information
                new_front_matter = f"""+++
title = "{title}"
date = "{date}"
draft = false
template = "pull_request_page.html"
in_search_index = {str(in_search_index).lower()}
"""

                # Add taxonomies for English version to make it show in the list
                if language_code == "en":
                    new_front_matter += """
[taxonomies]
list_display = ["show"]
"""

                new_front_matter += f"""
[extra]
current_language = "{language_code}"
available_languages = {languages_toml}
+++
"""
                
                # Update file with new front matter
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(new_front_matter + content_after_front_matter)
                
                print(f"Updated front matter: {md_file_path}")
                return
        
        # Create front matter with language information
        front_matter = f"""+++
title = "{title}"
date = "{date}"
draft = false
template = "pull_request_page.html"
in_search_index = {str(in_search_index).lower()}
"""

        # Add taxonomies for English version to make it show in the list
        if language_code == "en":
            front_matter += """
[taxonomies]
list_display = ["show"]
"""

        front_matter += f"""
[extra]
current_language = "{language_code}"
available_languages = {languages_toml}
+++

"""
    else:
        # Use current date and time if can't extract from filename
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Create basic front matter without language information
        front_matter = f"""+++
title = "{title}"
date = "{date}"
draft = false
template = "pull_request_page.html"
+++

"""
    
    # Add front matter to file
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    
    print(f"Added front matter: {md_file_path}")

def process_markdown_files(dir_path):
    """Process all Markdown files in the directory"""
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".md") and file != "_index.md":
                md_file_path = os.path.join(root, file)
                ensure_front_matter(md_file_path)

def main():
    """Main function"""
    # Ensure directory exists
    if not os.path.exists(CONTENT_DIR):
        os.makedirs(CONTENT_DIR)
        print(f"Created directory: {CONTENT_DIR}")
    
    # Process directory structure
    process_directory(CONTENT_DIR)
    
    # Process Markdown files
    process_markdown_files(CONTENT_DIR)
    
    print("Done!")

if __name__ == "__main__":
    main() 