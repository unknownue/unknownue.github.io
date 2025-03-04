# Unknownue's Blog

This is a personal blog built with [Zola](https://www.getzola.org/) and the [Apollo](https://www.getzola.org/themes/apollo/) theme.

## Setup

### Prerequisites

- [Zola](https://www.getzola.org/documentation/getting-started/installation/) installed on your system
- Git
- Python 3 (for automatic index generation)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/unknownue/unknownue.github.io.git
   cd unknownue.github.io
   ```

2. Initialize and update the Apollo theme submodule:
   ```bash
   git submodule update --init --recursive
   ```

### Local Development

To start the development server with automatic index generation:

```bash
./serve.sh
```

Or, if you prefer to use Zola directly (without automatic index generation):

```bash
zola serve
```

This will start a local server at `http://127.0.0.1:1111`.

### Building the Site

To build the site for production with automatic index generation:

```bash
./build.sh
```

Or, if you prefer to use Zola directly (without automatic index generation):

```bash
zola build
```

The output will be in the `public` directory.

## Features

- Clean and minimalist design with Apollo theme
- Dark mode support
- Code syntax highlighting
- Math rendering with KaTeX
- Diagram support with Mermaid
- Chart visualization with Chart.js
- Pull request documentation system (see [PULL_REQUEST.md](./PULL_REQUEST.md))

## Content Structure

- `content/`: Contains all the blog posts and pages
  - `posts/`: Blog posts
  - `pull_request/`: Pull request documentation (see [PULL_REQUEST.md](./PULL_REQUEST.md))
  - `about/`: About page
- `static/`: Static files like images, CSS, JavaScript
- `templates/`: Custom templates (if any)
- `themes/apollo/`: The Apollo theme
- `scripts/`: Utility scripts
  - `generate_index_files.py`: Automatically generates index files for the pull request structure

## License

This blog is licensed under the MIT License - see the LICENSE file for details. 