#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Workflow version of automated publishing script
Generic WASM project publisher for any Rust project with WASM binaries
"""

import os
import sys
import shutil
import subprocess
import datetime
import configparser
import toml
import re

class GitHubAutoPublisher:
    def __init__(self, config_path="build_config.ini"):
        """Initialize the auto publisher with configuration"""
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration file"""
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')
        return config
    
    def load_publish_config(self):
        """Load wasm_publish.toml configuration from source repository"""
        source_repo = self.config['PATHS']['source_repo']
        publish_config_path = os.path.join(source_repo, 'wasm_publish.toml')
        
        if not os.path.exists(publish_config_path):
            print("⚠ wasm_publish.toml not found at {}".format(publish_config_path))
            print("  Falling back to auto-discovery mode")
            return None
            
        try:
            with open(publish_config_path, 'r', encoding='utf-8') as f:
                publish_config = toml.load(f)
            
            binaries = publish_config.get('publish', {}).get('binaries', [])
            print("✓ Loaded publish configuration: {} binaries specified".format(len(binaries)))
            return binaries
        except Exception as e:
            print("✗ Error loading wasm_publish.toml: {}".format(e))
            print("  Falling back to auto-discovery mode")
            return None

    def parse_cargo_toml(self, specified_binaries=None):
        """Parse Cargo.toml to extract binary information"""
        source_repo = self.config['PATHS']['source_repo']
        cargo_path = os.path.join(source_repo, 'Cargo.toml')
        
        with open(cargo_path, 'r', encoding='utf-8') as f:
            cargo_data = toml.load(f)
        
        binaries = []
        bin_configs = cargo_data.get('bin', [])
        
        # Filter binaries based on specified list if provided
        if specified_binaries:
            bin_configs = [b for b in bin_configs if b['name'] in specified_binaries]
            
            # Check for missing binaries
            found_names = {b['name'] for b in bin_configs}
            missing = set(specified_binaries) - found_names
            if missing:
                print("⚠ Binary programs not found in Cargo.toml: {}".format(', '.join(missing)))
        
        for bin_config in bin_configs:
            binary_name = bin_config['name']
            metadata = cargo_data.get('package', {}).get('metadata', {}).get('app', {}).get(binary_name, {})
            
            binary_info = {
                'name': binary_name,
                'path': bin_config['path'],
                'display_name': metadata.get('name', binary_name.replace('_', ' ').title()),
                'description': metadata.get('description', '{} application'.format(binary_name)),
                'tags': self.generate_tags(binary_name, metadata)
            }
            binaries.append(binary_info)
        
        mode = "specified" if specified_binaries else "auto-discovered"
        print("✓ Found {} {} binary programs".format(len(binaries), mode))
        return binaries
    
    def generate_tags(self, binary_name, metadata):
        """Generate tags for a binary - generic approach"""
        # Start with base tags
        tags = ['wasm', 'bevy', 'rust']
        
        # Add tags from metadata if available
        if 'tags' in metadata:
            if isinstance(metadata['tags'], list):
                tags.extend(metadata['tags'])
            elif isinstance(metadata['tags'], str):
                # Split comma-separated tags
                additional_tags = [tag.strip() for tag in metadata['tags'].split(',')]
                tags.extend(additional_tags)
        
        # If no metadata tags, try to infer from binary name (very basic)
        if len(tags) == 3:  # Only base tags
            name_lower = binary_name.lower()
            
            # Basic pattern detection based on common naming conventions
            if 'game' in name_lower or 'prototype' in name_lower:
                tags.append('game')
            if 'pattern' in name_lower or 'shader' in name_lower:
                tags.append('graphics')
            if 'interactive' in name_lower or 'ui' in name_lower:
                tags.append('interactive')
            if 'demo' in name_lower or 'example' in name_lower:
                tags.append('demo')
            if 'paint' in name_lower or 'draw' in name_lower:
                tags.append('graphics')
            if 'puzzle' in name_lower or 'connect' in name_lower:
                tags.append('puzzle')
                
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
                
        return unique_tags
    
    def build_wasm(self, binary_name):
        """Build WASM for a specific binary"""
        source_repo = self.config['PATHS']['source_repo']
        print("  Building WASM: {}".format(binary_name))
        
        original_cwd = os.getcwd()
        os.chdir(source_repo)
        
        try:
            result = subprocess.run([
                'bash', 'wasm/build_serve.sh', binary_name, '--build-only'
            ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            
            if result.returncode != 0:
                print("    ✗ Build failed: {}".format(result.stderr))
                return False
            
            output_dir = "wasm/output/{}".format(binary_name)
            if not os.path.exists(output_dir):
                print("    ✗ Output directory does not exist: {}".format(output_dir))
                return False
                
            print("    ✓ Build successful")
            return True
            
        except subprocess.TimeoutExpired:
            print("    ✗ Build timeout")
            return False
        except Exception as e:
            print("    ✗ Build error: {}".format(e))
            return False
        finally:
            os.chdir(original_cwd)
    
    def create_project_structure(self, binary_info):
        """Create project directory structure for a binary"""
        target_repo = self.config['PATHS']['target_repo']
        binary_name = binary_info['name']
        
        project_dir = os.path.join(target_repo, 'content', 'projects', binary_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create _index.md
        index_content = '''+++
title = "{}"
description = "{}"
sort_by = "date"
template = "project_section.html"
+++

'''.format(binary_info['display_name'], binary_info['description'])
        
        with open(os.path.join(project_dir, '_index.md'), 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # Create content.md
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        tags_str = ', '.join(['"{}"'.format(tag) for tag in binary_info['tags']])
        
        content_md = '''+++
title = "{}"
date = {}
description = "{}"
draft = false

[taxonomies]
tags = [{}]
+++

## {}

{}

{{{{ wasm_viewer(path="app.js", id="{}-demo") }}}} 

'''.format(
            binary_info['display_name'],
            current_date,
            binary_info['description'],
            tags_str,
            binary_info['display_name'],
            binary_info['description'],
            binary_name
        )
        
        with open(os.path.join(project_dir, 'content.md'), 'w', encoding='utf-8') as f:
            f.write(content_md)
            
        print("    ✓ Created project structure: {}".format(project_dir))
        return project_dir
    
    def copy_wasm_files(self, binary_name, project_dir):
        """Copy WASM files to project directory"""
        source_repo = self.config['PATHS']['source_repo']
        wasm_output_dir = os.path.join(source_repo, 'wasm', 'output', binary_name)
        
        wasm_files = [
            'app.js',
            'app.d.ts', 
            '{}_bg.wasm'.format(binary_name),
            '{}_bg.wasm.d.ts'.format(binary_name)
        ]
        
        for filename in wasm_files:
            src_path = os.path.join(wasm_output_dir, filename)
            if os.path.exists(src_path):
                dst_path = os.path.join(project_dir, filename)
                shutil.copy2(src_path, dst_path)
                print("      Copied: {}".format(filename))
            else:
                print("      ⚠ File not found: {}".format(filename))
    
    def copy_assets(self):
        """Copy assets to target repository"""
        source_repo = self.config['PATHS']['source_repo']
        target_repo = self.config['PATHS']['target_repo']
        
        source_assets = os.path.join(source_repo, 'assets')
        target_assets = os.path.join(target_repo, 'static', 'assets')
        
        if not os.path.exists(source_assets):
            print("    ⚠ Source assets directory does not exist: {}".format(source_assets))
            return
            
        os.makedirs(target_assets, exist_ok=True)
        
        def ignore_patterns(dir, files):
            return [f for f in files if f.startswith('.git') or f.endswith('.gitkeep')]
        
        for item in os.listdir(source_assets):
            src_item = os.path.join(source_assets, item)
            dst_item = os.path.join(target_assets, item)
            
            if os.path.isdir(src_item):
                if os.path.exists(dst_item):
                    shutil.rmtree(dst_item)
                shutil.copytree(src_item, dst_item, ignore=ignore_patterns)
            else:
                shutil.copy2(src_item, dst_item)
        
        print("    ✓ Copied assets to: {}".format(target_assets))
    
    def publish_binary(self, binary_info):
        """Publish a single binary"""
        binary_name = binary_info['name']
        print("\n📦 Publishing {} ({})".format(binary_name, binary_info['display_name']))
        
        if not self.build_wasm(binary_name):
            print("  ✗ Skipping {}: Build failed".format(binary_name))
            return False
        
        project_dir = self.create_project_structure(binary_info)
        print("    Copying WASM files...")
        self.copy_wasm_files(binary_name, project_dir)
        print("  ✓ Successfully published {}".format(binary_name))
        return True
    
    def publish_all(self, specific_binary=None):
        """Publish all binaries or a specific one"""
        print("🚀 Starting automated publishing process\n")
        
        # Try to load publish configuration first
        specified_binaries = self.load_publish_config()
        
        # Parse Cargo.toml with or without binary filtering
        binaries = self.parse_cargo_toml(specified_binaries)
        
        # Handle specific binary request
        if specific_binary:
            binaries = [b for b in binaries if b['name'] == specific_binary]
            if not binaries:
                print("✗ Binary not found: {}".format(specific_binary))
                return False
            print("📌 Publishing only: {}".format(specific_binary))
        
        # Skip if no binaries to publish
        if not binaries:
            print("✗ No binaries to publish")
            return False
        
        print("\n📁 Copying assets...")
        self.copy_assets()
        
        successful = 0
        failed = 0
        
        for binary_info in binaries:
            if self.publish_binary(binary_info):
                successful += 1
            else:
                failed += 1
        
        print("\n✅ Publishing completed!")
        print("  Successful: {}".format(successful))
        print("  Failed: {}".format(failed))
        print("  Total: {}".format(len(binaries)))
        
        return failed == 0

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("""
GitHub Auto Publisher for WASM Projects

Usage: python3 github_auto_publisher.py [binary_name]

Arguments:
  binary_name    Optional, specify a single binary program name to publish
  --help, -h     Show this help message

Configuration:
  Expects build_config.ini with [PATHS] section defining:
  - source_repo: Path to source repository
  - target_repo: Path to target repository

Binary Selection:
  Create wasm_publish.toml in the source repository to specify which binaries to publish:
  
  [publish]
  binaries = ["binary1", "binary2", "binary3"]
  
  If wasm_publish.toml is not found, all binaries in Cargo.toml will be published.

Tags Configuration:
  Tags can be specified in Cargo.toml metadata:
  
  [package.metadata.app.your_binary]
  name = "Display Name"
  description = "Description"
  tags = ["tag1", "tag2", "tag3"]
  
  or as comma-separated string:
  tags = "tag1, tag2, tag3"
        """)
        return
    
    specific_binary = sys.argv[1] if len(sys.argv) > 1 else None
    publisher = GitHubAutoPublisher()
    success = publisher.publish_all(specific_binary)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 