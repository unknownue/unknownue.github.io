# Personal Blog

This is a personal blog built with [Zola](https://www.getzola.org/), a fast static site generator written in Rust.

The site is designed to render markdown content and is published to GitHub Pages.

## Quick Start

1. Install Zola by following the [installation instructions](https://www.getzola.org/documentation/getting-started/installation/).

2. Run the development server:
   ```bash
   zola serve
   ```

3. Visit `http://127.0.0.1:1111` in your browser to see the "Hello World" page.

4. To build the site for production:
   ```bash
   zola build
   ```
   
   This will generate the static site in the `public` directory.

## Project Structure

```
.
├── config.toml              # Site configuration
├── content                  # Content directory
│   └── _index.md            # Home page content
├── themes                   # Themes directory
│   └── simple               # Simple theme
│       ├── static           # Static assets
│       │   └── style.css    # CSS styles
│       ├── templates        # Templates
│       │   ├── base.html    # Base template
│       │   ├── index.html   # Index template
│       │   ├── page.html    # Page template
│       │   └── section.html # Section template
│       └── theme.toml       # Theme configuration
└── static                   # Global static assets
```

For more information on how to use Zola, refer to the [Zola documentation](https://www.getzola.org/documentation/). 