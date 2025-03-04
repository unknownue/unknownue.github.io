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

def ensure_front_matter(md_file_path):
    """Ensure Markdown file has front matter"""
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if file already has front matter
    if content.startswith("+++"):
        # Fix existing front matter if needed
        front_matter_match = re.match(r'\+\+\+(.*?)\+\+\+', content, re.DOTALL)
        if front_matter_match:
            front_matter = front_matter_match.group(1)
            # Fix draft field if it's a string instead of boolean
            draft_match = re.search(r'draft\s*=\s*"(true|false)"', front_matter)
            if draft_match:
                draft_value = draft_match.group(1)
                fixed_front_matter = re.sub(
                    r'draft\s*=\s*"(true|false)"', 
                    f'draft = {draft_value}', 
                    front_matter
                )
                content = content.replace(front_matter, fixed_front_matter)
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed front matter in: {md_file_path}")
        return
    
    # Extract information from filename
    filename = os.path.basename(md_file_path)
    # Look for PR number and datetime in format: pr_18143_zh-cn_20250303_215251.md
    # This matches PR number and datetime with optional time component
    match = re.search(r'pr_(\d+).*?(\d{8})(?:_(\d{6}))?', filename)
    
    title = "Pull Request"
    if match:
        pr_number = match.group(1)
        date_str = match.group(2)
        time_str = match.group(3) if match.group(3) else "000000"  # Default to midnight if no time
        
        title = f"PR #{pr_number}"
        
        # Try to extract a better title from content
        # Look for "**标题**:" pattern which contains the PR title in Chinese docs
        title_match = re.search(r'\*\*标题\*\*:\s*`?(.*?)`?(?:\r?\n|\*\*)', content)
        if title_match:
            title = title_match.group(1).strip()
        
        # Format date (YYYYMMDD_HHMMSS -> YYYY-MM-DD HH:MM)
        date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
    else:
        # Use current date and time if can't extract from filename
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    # Create front matter - note: draft is a boolean, not a string
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