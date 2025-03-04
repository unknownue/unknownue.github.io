# Pull Request Documentation

This document explains how to use the `pull_request` directory structure for organizing and displaying pull request documentation on the blog.

## Directory Structure

The `pull_request` directory follows this structure:

```
content/
└── pull_request/
    └── repo_name/
        └── year-month/
            └── pr_number_lang_date_time.md
```

For example:
```
content/
└── pull_request/
    ├── bevy/
    │   └── 2025-03/
    │       └── pr_18143_zh-cn_20250303_215251.md
    └── rust/
        └── 2025-04/
            └── pr_12345_zh-cn_20250410_123456.md
```

## Automatic Front Matter Generation

The blog includes a script that automatically generates:

1. `_index.md` files for each directory in the `pull_request` structure
2. Front matter for PR Markdown files that don't have it

### How It Works

The `scripts/generate_index_files.py` script:

1. Scans the `content/pull_request` directory and its subdirectories
2. Creates `_index.md` files with appropriate titles:
   - Repository names are capitalized (e.g., "Bevy", "Rust")
   - Year-month directories are formatted as "Month Year" (e.g., "March 2025")
3. Adds front matter to PR Markdown files, extracting:
   - Title from the PR content
   - Date from the filename or PR creation date

### Usage

Instead of using `zola serve` or `zola build` directly, use the provided scripts:

- For development: `./serve.sh`
- For building: `./build.sh`

These scripts automatically run the `generate_index_files.py` script before starting Zola.

### Adding New PR Documentation

1. Create the appropriate directory structure if it doesn't exist:
   ```bash
   mkdir -p content/pull_request/repo_name/year-month/
   ```

2. Create a new Markdown file with the naming convention:
   ```
   pr_number_lang_date_time.md
   ```
   For example: `pr_12345_zh-cn_20250410_123456.md`

3. Add the content following the format described above (without front matter)

4. Run `./serve.sh` or `./build.sh` - the script will automatically:
   - Create any missing `_index.md` files
   - Add front matter to your PR Markdown file

## Troubleshooting

If you encounter issues with the automatic generation:

1. Ensure the Python script has execution permissions:
   ```bash
   chmod +x scripts/generate_index_files.py
   ```

2. Check that the PR Markdown file follows the expected format
   
3. Run the script manually to see any error messages:
   ```bash
   python3 scripts/generate_index_files.py
   ``` 