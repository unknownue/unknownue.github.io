#!/bin/bash
# Development server script with automatic _index.md generation

# Generate _index.md files
echo "Generating _index.md files..."
python3 scripts/generate_index_files.py

# Start Zola development server
echo "Starting Zola development server..."
zola serve 