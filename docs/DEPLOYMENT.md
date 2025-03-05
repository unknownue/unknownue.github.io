# Deployment Guide

This document outlines the process for building and deploying the Zola-based blog to GitHub Pages.

## Prerequisites

- [Zola](https://www.getzola.org/) installed locally (version 0.17.0 or newer recommended)
- Git
- GitHub account with repository set up for GitHub Pages

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/unknownue/unknownue.github.io.git
   cd unknownue.github.io
   ```

2. Start the Zola development server:
   ```bash
   zola serve
   ```
   This will start a local server at `http://127.0.0.1:1111` with live reloading.

## Building the Site

To build the site locally:

```bash
zola build
```

This will generate the static site in the `public` directory.

## Deployment Options

### Manual Deployment

1. Build the site:
   ```bash
   zola build
   ```

2. Push the `public` directory contents to the `gh-pages` branch:
   ```bash
   cd public
   git init
   git add .
   git commit -m "Deploy website"
   git remote add origin https://github.com/unknownue/unknownue.github.io.git
   git push -f origin master:gh-pages
   ```

### GitHub Actions Automated Deployment

For automated deployments, you can use GitHub Actions. Create a file at `.github/workflows/build.yml` with the following content:

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          submodules: true

      - name: Build and Deploy
        uses: shalzz/zola-deploy-action@v0.20.0
        env:
          PAGES_BRANCH: gh-pages
          TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This workflow will automatically build and deploy your site to the `gh-pages` branch whenever you push to the `main` or `master` branch.

## GitHub Pages Configuration

1. Go to your repository settings on GitHub
2. Navigate to "Pages" section
3. Set the source to "Deploy from a branch"
4. Select the `gh-pages` branch and root directory
5. Save the settings

Your site will be available at `https://unknownue.github.io` (or your custom domain if configured).

## Custom Domain (Optional)

If you want to use a custom domain:

1. Add your domain in the GitHub Pages settings
2. Create a `CNAME` file in the `static` directory of your Zola project with your domain name
3. Update your DNS settings to point to GitHub Pages

## Automated Blog Updates

The repository includes a `publish.py` script that automates the process of generating index files and pushing changes to the remote repository. This is useful for keeping the blog updated on a regular schedule.

### How It Works

The `publish.py` script performs the following operations:
1. Executes the Python script to generate index files (`scripts/generate_index_files.py`)
2. Adds all changes to git
3. Commits the changes with a timestamp
4. Pushes the changes to the remote repository

The script includes robust error handling and will:
- Provide detailed error messages if any command fails
- Continue execution if there are no changes to commit
- Exit with appropriate error codes on failure

### Usage

You can run the script with different options:

```bash
# Run once and exit (default behavior)
./publish.py

# Explicitly run once and exit
./publish.py --once

# Run in schedule mode, publishing every 12 hours
./publish.py --schedule 12
```

The script supports the following command-line arguments:
- `--once`: Run the publish operation once and exit (this is the default behavior)
- `--schedule HOURS`: Run in schedule mode, publishing every HOURS hours

When running in schedule mode, the script will:
- Execute the publishing process immediately
- Sleep for the specified interval
- Repeat the process until interrupted (Ctrl+C)
- Display the next scheduled update time

### Setting Up Automated Updates

Run the script in schedule mode in a terminal session (consider using tools like `screen` or `tmux` to keep it running):

```bash
./publish.py --schedule 24  # Update every 24 hours
```

This will automatically update your blog on the specified schedule, triggering the GitHub Pages deployment process.

### Requirements

The script requires:
- Python 3.6 or newer
- Git installed and configured with appropriate remote repository access
- Proper permissions to execute the script (`chmod +x publish.py`)

## Troubleshooting

- If your site is not displaying correctly, check the GitHub Pages settings and ensure the build process completed successfully
- Verify that the `base_url` in your `config.toml` is set correctly
- Check GitHub Actions logs for any build errors 