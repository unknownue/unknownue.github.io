# Unknownue's Blog - Project Introduction

This document provides an overview of the blog architecture and components.

## Project Overview

Unknownue's Blog is a personal blog built using [Zola](https://www.getzola.org/), a fast static site generator written in Rust. The blog utilizes the [Apollo](https://www.getzola.org/themes/apollo/) theme with custom modifications to provide a clean, responsive, and feature-rich reading experience.

## Architecture

The project follows Zola's standard architecture with several customizations:

### Project Tree Structure

```
unknownue.github.io/
├── .github/                # GitHub workflows and CI/CD
├── .git/                   # Git repository
├── content/                # All blog content in Markdown
│   ├── posts/              # Blog posts
│   ├── pull_request/       # Pull request documentation
│   ├── empty-posts/        # Template/placeholder posts
│   ├── _index.md           # Landing page content
│   └── about.md            # About page content
├── docs/                   # Project documentation
│   ├── INTRODUCTION.md     # This file
│   ├── DEPLOYMENT.md       # Deployment instructions
│   ├── PULL_REQUEST.md     # PR system documentation
│   └── README.md           # Project overview
├── sass/                   # SASS/SCSS styling
├── scripts/                # Utility scripts
├── static/                 # Static assets (images, CSS, JS)
├── syntaxes/               # Custom syntax highlighting
├── templates/              # HTML templates
│   ├── macros/             # Reusable template components
│   ├── partials/           # Partial templates
│   ├── shortcodes/         # Custom shortcodes
│   ├── pull_request.html   # PR list template
│   ├── pull_request_page.html # PR page template
│   ├── base.html           # Base layout template
│   ├── home.html           # Home page template
│   ├── posts.html          # Posts page template
│   └── ... other templates
├── themes/                 # Apollo theme (submodule)
│   └── apollo/             # Theme files
├── .gitignore              # Git ignore file
├── .gitmodules             # Git submodules
├── config.toml             # Zola configuration
├── create_soft_links.sh    # Utility script
├── publish.py              # Publishing script
├── README.md               # Repository README
├── serve.sh                # Development server script
└── zola_server.log         # Server logs
```

### Deployment and Automation

1. **Scripts**
   - `scripts/`: Utility scripts for site maintenance
     - `generate_index_files.py`: Automatically generates `_index.md` files for content directories, updates front matter in Markdown files, processes PR labels (removing backticks), and manages multi-language content relationships
   - `serve.sh`: Script to run the local development server
   - `publish.py`: Python script for publishing the site

2. **CI/CD**
   - `.github/`: GitHub workflows for continuous integration and deployment

## Site Pages and Structure

The blog consists of the following main pages and sections:

1. **Home Page (/)** 
   - Landing page with introduction
   - Recent posts

2. **Posts Section (/posts)**
   - Blog posts listing page
   - Individual post pages at `/posts/{slug}`
   - Posts are organized by date and can be filtered by tags/categories

3. **About Page (/about)**
   - Personal information and site description

4. **Pull Request Documentation (/pull_request)**
   - Custom documentation system organized like GitHub pull requests
   - List of all PR documentation entries
   - Individual PR pages at `/pull_request/{slug}`

5. **Taxonomy Pages**
   - Tags listing at `/tags`
   - Individual tag pages at `/tags/{tag-name}`
   - Categories listing at `/categories`
   - Individual category pages at `/categories/{category-name}`

6. **Other Utility Pages**
   - 404 error page
   - RSS feed at `/atom.xml`
   - Search functionality

Each page follows a consistent template structure while adapting to the specific content type. The site navigation is controlled by the menu items defined in `config.toml`.

## Features

The blog includes several advanced features:

1. **Content Features**
   - Markdown with extended syntax support
   - Code syntax highlighting with the Ayu Light theme
   - Math rendering with MathJax
   - Diagrams with Mermaid
   - Emoji support
   - Custom shortcodes for enhanced content

2. **Design Features**
   - Responsive design for mobile and desktop
   - Light/dark mode toggle
   - Table of contents generation
   - Custom CSS for enhanced styling

3. **Technical Features**
   - Search functionality with Elasticlunr
   - RSS feed generation
   - Taxonomy system (tags, categories)
   - Pull request style documentation system

## Customizations

The blog extends the Apollo theme with several custom features:

1. Custom templates for specialized content types
2. Additional shortcodes for enhanced markdown functionality
3. CSS customizations for styling and layout
4. Pull request documentation system
5. Extended syntax highlighting support

## Development Workflow

1. Content is written in Markdown in the `content/` directory
2. Local development is done using `serve.sh` which runs Zola's built-in server
3. The site is built using Zola's build system with custom pre/post-processing
4. Deployment is handled through GitHub Pages or other static hosting

## Conclusion

This blog platform combines the speed and simplicity of Zola with custom extensions to create a feature-rich personal blog. The architecture balances maintainability, performance, and extensibility while maintaining a clean and minimalist design.
