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
# Configuration file
CONFIG_FILE = os.path.join(ROOT_DIR, "config.toml")

def load_filtered_labels():
    """Load filtered labels from config.toml using regex parsing"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find filtered_labels array using regex
        match = re.search(r'filtered_labels\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            labels_str = match.group(1)
            # Extract each label string from the array
            labels = re.findall(r'"([^"]*)"', labels_str)
            return labels
        
        return []
    except Exception as e:
        print(f"Error loading filtered labels from config: {e}")
        return []

FILTERED_LABELS = load_filtered_labels()

def escape_toml_string(s):
    """Escape special characters in a TOML string"""
    # Replace backslashes first to avoid double escaping
    s = s.replace('\\', '\\\\')
    # Replace double quotes with escaped double quotes
    s = s.replace('"', '\\"')
    # Escape other special characters if needed
    return s

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
    # Escape the title for TOML
    escaped_title = escape_toml_string(title)
    
    # Create _index.md content
    content = f"""+++
title = "{escaped_title}"
sort_by = "date"
template = "pull_request.html"
+++
"""
    
    # Write to file
    with open(index_path, "w") as f:
        f.write(content)
    
    print(f"Created: {index_path}")

def collect_section_labels(dir_path):
    """Collect all labels from PR files in the directory and update the _index.md file"""
    index_path = os.path.join(dir_path, "_index.md")
    
    # Skip if file doesn't exist
    if not os.path.exists(index_path):
        return
    
    # Collect all labels from markdown files in this directory and subdirectories
    all_labels = set()
    
    # Process current directory
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if file.endswith(".md") and file != "_index.md" and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    labels = extract_labels(content)
                    # Filter out unwanted labels
                    labels = [label for label in labels if label not in FILTERED_LABELS]
                    all_labels.update(labels)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    
    # Process subdirectories
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            for file in os.listdir(item_path):
                if file.endswith(".md") and file != "_index.md":
                    file_path = os.path.join(item_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            labels = extract_labels(content)
                            # Filter out unwanted labels
                            labels = [label for label in labels if label not in FILTERED_LABELS]
                            all_labels.update(labels)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
    
    # Skip if no labels found
    if not all_labels:
        return
    
    # Sort labels alphabetically
    sorted_labels = sorted(list(all_labels))
    
    # Format labels as TOML array
    labels_str = "all_labels = ["
    for label in sorted_labels:
        escaped_label = escape_toml_string(label)
        labels_str += f'"{escaped_label}", '
    labels_str = labels_str.rstrip(", ") + "]"
    
    # Read the current index file
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the file has front matter
    if not content.startswith("+++"):
        return
    
    # Extract front matter and content after it
    front_matter_match = re.match(r'\+\+\+(.*?)\+\+\+', content, re.DOTALL)
    if not front_matter_match:
        return
        
    front_matter = front_matter_match.group(1)
    content_after_front_matter = content[front_matter_match.end():].lstrip('\r\n')
    
    # Create fresh front matter without any all_labels entries
    new_front_matter = ""
    
    # Check if there's an [extra] section
    extra_section_match = re.search(r'\[extra\](.*?)(?=\[|\Z)', front_matter, re.DOTALL)
    
    if extra_section_match:
        # Get the lines from extra section
        extra_content = extra_section_match.group(1)
        # Remove all all_labels lines
        cleaned_lines = []
        for line in extra_content.split('\n'):
            if not line.strip().startswith('all_labels'):
                cleaned_lines.append(line)
        
        # Create new extra content with our labels
        new_extra_content = '\n'.join(cleaned_lines).rstrip() + "\n" + labels_str
        
        # Replace entire front matter
        sections = re.split(r'\[(\w+)\]', front_matter)
        new_sections = []
        
        # Process sections
        i = 0
        while i < len(sections):
            if i == 0:  # Root section
                new_sections.append(sections[i])
                i += 1
            elif sections[i] == "extra":  # Extra section - replace with our new one
                new_sections.append("[extra]")
                new_sections.append(new_extra_content)
                i += 2  # Skip the original extra content
            else:  # Other sections - keep as is
                new_sections.append("[" + sections[i] + "]")
                if i + 1 < len(sections):
                    new_sections.append(sections[i+1])
                i += 2
        
        new_front_matter = ''.join(new_sections)
    else:
        # No [extra] section, add one
        new_front_matter = front_matter.rstrip() + "\n\n[extra]\n" + labels_str
    
    # Clean up any consecutive empty lines in the front matter
    new_front_matter = re.sub(r'\n\s*\n\s*\n', '\n\n', new_front_matter)
    
    # Update the file
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("+++" + new_front_matter + "\n+++\n")
        if content_after_front_matter:
            f.write("\n" + content_after_front_matter)
    
    print(f"Updated labels in index file: {index_path}")

def process_directory(dir_path):
    """Process directory and its subdirectories"""
    # Create _index.md for current directory
    create_index_file(dir_path)
    
    # Process subdirectories
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            process_directory(item_path)
    
    # After processing all subdirectories, collect labels
    # Only collect labels for month-level directories (YYYY-MM format)
    dir_name = os.path.basename(dir_path)
    if re.match(r'\d{4}-\d{2}', dir_name):
        collect_section_labels(dir_path)

def get_language_name(lang_code):
    """Return the full name of a language based on its code"""
    language_names = {
        "en": "English",
        "zh-cn": "中文",
        "fr": "Français",
        # Add more languages as needed
    }
    return language_names.get(lang_code, lang_code)

def extract_labels(content):
    """Extract PR labels from the Basic Information section"""
    # Try to find the Basic Information section
    basic_info_match = re.search(r'## Basic Information(.*?)(?:##|\Z)', content, re.DOTALL)
    if basic_info_match:
        basic_info_content = basic_info_match.group(1)
        # Look for the Labels field
        labels_match = re.search(r'\*\*Labels\*\*:\s*(.*?)(?:\r?\n|$)', basic_info_content)
        if labels_match:
            labels_str = labels_match.group(1).strip()
            # Check if labels are "None" or empty
            if labels_str.lower() == "none" or not labels_str:
                return []
            # Split by comma and strip whitespace
            labels = [label.strip() for label in labels_str.split(',')]
            # Remove backtick characters from each label
            labels = [label.replace('`', '') for label in labels]
            return labels
    return []

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
    
    # Initialize title with PR number
    title = "Pull Request"
    language_code = "en"  # Default language
    
    if match:
        pr_number = match.group(1)
        # Extract language code if present, otherwise default to "en"
        language_code = match.group(2) if match.group(2) else "en"
        date_str = match.group(3)
        # Time part is now optional and ignored for processing
        
        # Initialize title with PR number
        title = f"#{pr_number}"
        
        # Try multiple patterns to extract a better title from content
        title_found = False
        
        # Pattern 1: Look for "# Title: XXX" at the beginning of the document
        title_match = re.search(r'# Title: (.*?)(?:\r?\n)', content)
        if title_match:
            title = f"#{pr_number} {title_match.group(1).strip()}"
            title_found = True
        
        # Pattern 2: Look for "**Title**: XXX" in the Basic Information section
        if not title_found:
            # First try to find the Basic Information section
            basic_info_match = re.search(r'## Basic Information(.*?)(?:##|\Z)', content, re.DOTALL)
            if basic_info_match:
                basic_info_content = basic_info_match.group(1)
                # Then look for the title within that section
                title_in_section_match = re.search(r'\*\*Title\*\*: (.*?)(?:\r?\n)', basic_info_content)
                if title_in_section_match:
                    title = f"#{pr_number} {title_in_section_match.group(1).strip()}"
                    title_found = True
        
        # Pattern 3: Look for "**标题**: XXX" pattern in Chinese docs
        if not title_found:
            title_match = re.search(r'\*\*标题\*\*:\s*`?(.*?)`?(?:\r?\n|\*\*)', content)
            if title_match:
                title = f"#{pr_number} {title_match.group(1).strip()}"
                title_found = True
        
        # Escape the title for TOML
        escaped_title = escape_toml_string(title)
        
        # Format date (YYYYMMDD -> YYYY-MM-DD 00:00)
        date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T00:00:00"
        
        # Extract PR labels
        labels = extract_labels(content)
        
        # Filter out unwanted labels
        labels = [label for label in labels if label not in FILTERED_LABELS]
        
        # Find other language versions of the same PR
        available_languages = find_language_versions(md_file_path, pr_number)
        
        # Format available languages as TOML table
        languages_toml = "{"
        for lang, info in available_languages.items():
            lang_name = escape_toml_string(info["name"])
            lang_url = escape_toml_string(info["url"])
            languages_toml += f'"{lang}" = {{ name = "{lang_name}", url = "{lang_url}" }}, '
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
                
                # Remove leading newlines to prevent accumulating empty lines
                content_after_front_matter = content_after_front_matter.lstrip('\r\n')
                
                # Parse existing front matter to extract all sections and fields
                front_matter_content = front_matter_match.group(1)
                sections = {}
                current_section = "root"
                sections[current_section] = {}
                
                # Process front matter line by line
                lines = front_matter_content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    # Check for section headers like [extra] or [taxonomies]
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]  # Remove brackets
                        if current_section not in sections:
                            sections[current_section] = {}
                        continue
                    
                    # Parse key-value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        sections[current_section][key] = value
                
                # Update base fields
                sections["root"]["title"] = f'"{escaped_title}"'
                sections["root"]["date"] = f'"{date}"'
                sections["root"]["draft"] = "false"
                sections["root"]["template"] = '"pull_request_page.html"'
                sections["root"]["in_search_index"] = str(in_search_index).lower()
                
                # Update taxonomies section
                if language_code == "en":
                    if "taxonomies" not in sections:
                        sections["taxonomies"] = {}
                    sections["taxonomies"]["list_display"] = '["show"]'
                
                # Update extra section
                if "extra" not in sections:
                    sections["extra"] = {}
                
                sections["extra"]["current_language"] = f'"{language_code}"'
                sections["extra"]["available_languages"] = languages_toml
                
                # Add labels if available
                if labels:
                    labels_value = "["
                    for label in labels:
                        escaped_label = escape_toml_string(label)
                        labels_value += f'"{escaped_label}", '
                    labels_value = labels_value.rstrip(", ") + "]"
                    sections["extra"]["labels"] = labels_value
                
                # Reconstruct front matter in a clean format
                new_front_matter = "+++\n"
                
                # Root section first (title, sort_by, etc.)
                for key, value in sections.get('root', {}).items():
                    new_front_matter += f"{key} = {value}\n"
                
                # Then other sections
                for section_name, section_data in sections.items():
                    if section_name != 'root' and section_data:  # Skip empty sections and root
                        new_front_matter += f"\n[{section_name}]\n"
                        for key, value in section_data.items():
                            new_front_matter += f"{key} = {value}\n"
                
                new_front_matter += "+++"
                
                # Update file with new front matter
                with open(md_file_path, "w", encoding="utf-8") as f:
                    # Ensure exactly one newline between front matter and content
                    if not content_after_front_matter.startswith('\n') and not content_after_front_matter.startswith('\r\n'):
                        f.write(new_front_matter + "\n\n" + content_after_front_matter)
                    else:
                        f.write(new_front_matter + "\n" + content_after_front_matter)
                
                print(f"Updated front matter: {md_file_path}")
                return
        else:
            # Create sections structure for front matter
            sections = {}
            
            # Root section - basic metadata
            sections["root"] = {
                "title": f'"{escaped_title}"',
                "date": f'"{date}"',
                "draft": "false",
                "template": '"pull_request_page.html"',
                "in_search_index": str(in_search_index).lower()
            }
            
            # Taxonomies section for English version
            if language_code == "en":
                sections["taxonomies"] = {
                    "list_display": '["show"]'
                }
            
            # Extra section - language info and labels
            sections["extra"] = {
                "current_language": f'"{language_code}"',
                "available_languages": languages_toml
            }
            
            # Add labels if available
            if labels:
                labels_value = "["
                for label in labels:
                    escaped_label = escape_toml_string(label)
                    labels_value += f'"{escaped_label}", '
                labels_value = labels_value.rstrip(", ") + "]"
                sections["extra"]["labels"] = labels_value
            
            # Reconstruct front matter in a clean format
            front_matter = "+++\n"
            
            # Root section first (title, sort_by, etc.)
            for key, value in sections.get('root', {}).items():
                front_matter += f"{key} = {value}\n"
            
            # Then other sections
            for section_name, section_data in sections.items():
                if section_name != 'root' and section_data:  # Skip empty sections and root
                    front_matter += f"\n[{section_name}]\n"
                    for key, value in section_data.items():
                        front_matter += f"{key} = {value}\n"
            
            front_matter += "+++"
    else:
        # Use current date and time if can't extract from filename
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Escape the title for TOML
        escaped_title = escape_toml_string(title)
        
        # Create sections structure for front matter
        sections = {}
        sections["root"] = {
            "title": f'"{escaped_title}"',
            "date": f'"{date}"',
            "draft": "false",
            "template": '"pull_request_page.html"'
        }
        
        # Reconstruct front matter in a clean format
        front_matter = "+++\n"
        
        # Root section first (title, sort_by, etc.)
        for key, value in sections.get('root', {}).items():
            front_matter += f"{key} = {value}\n"
        
        # Then other sections
        for section_name, section_data in sections.items():
            if section_name != 'root' and section_data:  # Skip empty sections and root
                front_matter += f"\n[{section_name}]\n"
                for key, value in section_data.items():
                    front_matter += f"{key} = {value}\n"
        
        front_matter += "+++"
    
    # Add front matter to file
    with open(md_file_path, "w", encoding="utf-8") as f:
        # Check if content already starts with newlines to avoid duplicate empty lines
        if content.startswith('\n') or content.startswith('\r\n'):
            # Content already has leading newlines, so just add front matter
            f.write(front_matter + "\n" + content.lstrip('\r\n'))
        else:
            # No leading newlines in content, add a separator
            f.write(front_matter + "\n\n" + content)
    
    # print(f"Added front matter: {md_file_path}")

def process_markdown_files(dir_path, force_update=False):
    """Process all Markdown files in the directory"""
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".md") and file != "_index.md":
                md_file_path = os.path.join(root, file)
                if force_update:
                    # Force update by reading the file, removing front matter, and then ensuring front matter
                    with open(md_file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Remove existing front matter if present
                    if content.startswith("+++"):
                        front_matter_match = re.match(r'\+\+\+(.*?)\+\+\+', content, re.DOTALL)
                        if front_matter_match:
                            content = content[front_matter_match.end():].lstrip('\r\n')
                            
                            # Write content without front matter
                            with open(md_file_path, "w", encoding="utf-8") as f:
                                f.write(content)
                
                # Now ensure front matter (it will be added since we removed it)
                ensure_front_matter(md_file_path)

def main():
    """Main function"""
    # Ensure directory exists
    if not os.path.exists(CONTENT_DIR):
        os.makedirs(CONTENT_DIR)
        print(f"Created directory: {CONTENT_DIR}")
    
    # Process directory structure
    process_directory(CONTENT_DIR)
    
    # Process Markdown files with force update
    process_markdown_files(CONTENT_DIR, force_update=True)
    
    print("Done!")

def test_escape_toml():
    """Test the TOML string escaping function"""
    test_cases = [
        'Normal title',
        'Title with "quotes"',
        'Title with both "quotes" and \\backslashes\\',
        'Multi-line\ntitle',
        'Title with "embedded "nested" quotes"'
    ]
    
    print("\nTesting TOML string escaping:")
    for test_case in test_cases:
        escaped = escape_toml_string(test_case)
        print(f'Original: "{test_case}"')
        print(f'Escaped:  "{escaped}"')
        print(f'TOML:     title = "{escaped}"')
        print("---")

if __name__ == "__main__":
    # Uncomment to run tests
    # test_escape_toml()
    
    main() 