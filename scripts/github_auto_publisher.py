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
import time

class GitHubAutoPublisher:
    def __init__(self, config_path="build_config.ini"):
        """Initialize the auto publisher with configuration"""
        self.config_path = config_path
        self.config = self.load_config()
        self.start_time = time.time()
        self.step_times = {}
        
    def log_step(self, step_name, message=""):
        """Log a step with timestamp and elapsed time"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        if message:
            print("[{}] [+{:.1f}s] {}: {}".format(timestamp, elapsed, step_name, message))
        else:
            print("[{}] [+{:.1f}s] {}".format(timestamp, elapsed, step_name))
        
        self.step_times[step_name] = current_time
        
    def log_progress(self, current, total, operation):
        """Log progress for multi-step operations"""
        percentage = (current / total) * 100 if total > 0 else 0
        elapsed = time.time() - self.start_time
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        print("[{}] [+{:.1f}s] Progress: {}/{} ({:.1f}%) - {}".format(
            timestamp, elapsed, current, total, percentage, operation))
        
    def load_config(self):
        """Load configuration file"""
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')
        return config
    
    def load_publish_config(self):
        """Load wasm_publish.toml configuration from source repository"""
        self.log_step("LOAD_CONFIG", "Loading wasm_publish.toml configuration")
        
        source_repo = self.config['PATHS']['source_repo']
        publish_config_path = os.path.join(source_repo, 'wasm_publish.toml')
        
        self.log_step("CONFIG_CHECK", "Checking {}".format(publish_config_path))
        
        if not os.path.exists(publish_config_path):
            self.log_step("CONFIG_MISSING", "wasm_publish.toml not found, using auto-discovery")
            return None
            
        try:
            self.log_step("CONFIG_PARSE", "Parsing TOML configuration")
            with open(publish_config_path, 'r', encoding='utf-8') as f:
                publish_config = toml.load(f)
            
            binaries = publish_config.get('publish', {}).get('binaries', [])
            self.log_step("CONFIG_SUCCESS", "Loaded {} specified binaries".format(len(binaries)))
            return binaries
        except Exception as e:
            self.log_step("CONFIG_ERROR", "Failed to parse config: {}".format(e))
            return None

    def parse_cargo_toml(self, specified_binaries=None):
        """Parse Cargo.toml to extract binary information"""
        self.log_step("PARSE_CARGO", "Parsing Cargo.toml for binary information")
        
        source_repo = self.config['PATHS']['source_repo']
        cargo_path = os.path.join(source_repo, 'Cargo.toml')
        
        self.log_step("CARGO_READ", "Reading {}".format(cargo_path))
        with open(cargo_path, 'r', encoding='utf-8') as f:
            cargo_data = toml.load(f)
        
        binaries = []
        bin_configs = cargo_data.get('bin', [])
        total_bins = len(bin_configs)
        
        self.log_step("CARGO_FOUND", "Found {} binary configurations".format(total_bins))
        
        # Filter binaries based on specified list if provided
        if specified_binaries:
            self.log_step("CARGO_FILTER", "Filtering for specified binaries: {}".format(', '.join(specified_binaries)))
            bin_configs = [b for b in bin_configs if b['name'] in specified_binaries]
            
            # Check for missing binaries
            found_names = {b['name'] for b in bin_configs}
            missing = set(specified_binaries) - found_names
            if missing:
                self.log_step("CARGO_MISSING", "Binaries not found: {}".format(', '.join(missing)))
        
        self.log_step("CARGO_PROCESS", "Processing {} binaries".format(len(bin_configs)))
        
        for i, bin_config in enumerate(bin_configs, 1):
            binary_name = bin_config['name']
            self.log_progress(i, len(bin_configs), "Processing binary: {}".format(binary_name))
            
            metadata = cargo_data.get('package', {}).get('metadata', {}).get('app', {}).get(binary_name, {})
            
            binary_info = {
                'name': binary_name,
                'path': bin_config['path'],
                'display_name': metadata.get('name', binary_name.replace('_', ' ').title()),
                'description': metadata.get('description', '{} application'.format(binary_name)),
                'tags': self.generate_tags(binary_name, metadata),
                'readme': metadata.get('readme')  # Get readme path from metadata
            }
            binaries.append(binary_info)
        
        mode = "specified" if specified_binaries else "auto-discovered"
        self.log_step("CARGO_COMPLETE", "Loaded {} {} binary programs".format(len(binaries), mode))
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
        build_start = time.time()
        self.log_step("BUILD_START", "Building WASM for: {}".format(binary_name))
        
        source_repo = self.config['PATHS']['source_repo']
        original_cwd = os.getcwd()
        
        self.log_step("BUILD_CHDIR", "Changing to source directory: {}".format(source_repo))
        os.chdir(source_repo)
        
        try:
            command = ['bash', 'wasm/build_serve.sh', binary_name, '--build-only']
            self.log_step("BUILD_EXEC", "Executing: {}".format(' '.join(command)))
            
            # Start the build process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Monitor the process with periodic updates
            timeout = 600  # 10 minutes
            poll_interval = 10  # 10 seconds
            elapsed = 0
            
            while process.poll() is None and elapsed < timeout:
                time.sleep(poll_interval)
                elapsed += poll_interval
                self.log_step("BUILD_PROGRESS", "Building {} for {:.0f}s...".format(binary_name, elapsed))
            
            if process.poll() is None:
                # Timeout reached
                process.terminate()
                self.log_step("BUILD_TIMEOUT", "Build timeout after {}s".format(timeout))
                return False
            
            # Get the results
            stdout, stderr = process.communicate()
            build_time = time.time() - build_start
            
            if process.returncode != 0:
                self.log_step("BUILD_FAILED", "Build failed in {:.1f}s".format(build_time))
                # Print last few lines of stderr for debugging
                if stderr:
                    error_lines = stderr.strip().split('\n')[-5:]
                    for line in error_lines:
                        print("    ERROR: {}".format(line))
                return False
            
            # Check output directory
            output_dir = "wasm/output/{}".format(binary_name)
            self.log_step("BUILD_CHECK", "Checking output directory: {}".format(output_dir))
            
            if not os.path.exists(output_dir):
                self.log_step("BUILD_NO_OUTPUT", "Output directory missing: {}".format(output_dir))
                return False
            
            # List generated files
            files = os.listdir(output_dir)
            self.log_step("BUILD_SUCCESS", "Build completed in {:.1f}s, {} files generated".format(build_time, len(files)))
            
            # Log generated files for verification
            wasm_files = [f for f in files if f.endswith('.wasm') or f.endswith('.js')]
            if wasm_files:
                self.log_step("BUILD_FILES", "Key files: {}".format(', '.join(wasm_files)))
            
            return True
            
        except Exception as e:
            build_time = time.time() - build_start
            self.log_step("BUILD_ERROR", "Build error after {:.1f}s: {}".format(build_time, e))
            return False
        finally:
            os.chdir(original_cwd)
            self.log_step("BUILD_RESTORE", "Restored working directory")
    
    def load_readme_content(self, binary_info):
        """Load README.md content for a binary"""
        binary_name = binary_info['name']
        self.log_step("README_LOAD", "Loading README for {}".format(binary_name))
        
        source_repo = self.config['PATHS']['source_repo']
        binary_path = binary_info['path']
        
        # Try different possible README locations
        readme_paths = []
        
        # First priority: check if readme path is specified in metadata
        if binary_info.get('readme'):
            readme_paths.append(os.path.join(source_repo, binary_info['readme']))
            self.log_step("README_CONFIG", "Using configured path: {}".format(binary_info['readme']))
        
        # Fallback: Get the directory containing the binary file
        binary_dir = os.path.dirname(binary_path)
        if binary_dir:
            readme_paths.append(os.path.join(source_repo, binary_dir, 'README.md'))
        
        # Fallback: Try app directory with binary name
        readme_paths.append(os.path.join(source_repo, 'app', binary_name, 'README.md'))
        
        self.log_step("README_SEARCH", "Searching {} possible locations".format(len(readme_paths)))
        
        for readme_path in readme_paths:
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:  # Only return if content is not empty
                        rel_path = os.path.relpath(readme_path, source_repo)
                        self.log_step("README_FOUND", "Loaded README from: {} ({} chars)".format(rel_path, len(content)))
                        return content
                except Exception as e:
                    self.log_step("README_ERROR", "Error reading {}: {}".format(readme_path, e))
        
        self.log_step("README_DEFAULT", "No README found for {}, using default".format(binary_name))
        return None

    def create_project_structure(self, binary_info):
        """Create project directory structure for a binary"""
        binary_name = binary_info['name']
        self.log_step("STRUCTURE_START", "Creating project structure for {}".format(binary_name))
        
        target_repo = self.config['PATHS']['target_repo']
        project_dir = os.path.join(target_repo, 'content', 'projects', binary_name)
        
        self.log_step("STRUCTURE_DIR", "Creating directory: {}".format(project_dir))
        os.makedirs(project_dir, exist_ok=True)
        
        # Load README content
        readme_content = self.load_readme_content(binary_info)
        
        # Create _index.md
        self.log_step("STRUCTURE_INDEX", "Creating _index.md")
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
        self.log_step("STRUCTURE_CONTENT", "Creating content.md")
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        tags_str = ', '.join(['"{}"'.format(tag) for tag in binary_info['tags']])
        
        # Use README content if available, otherwise use description
        if readme_content:
            content_text = readme_content
            self.log_step("STRUCTURE_README", "Using README content ({} chars)".format(len(content_text)))
        else:
            content_text = "## {}\n\n{}".format(binary_info['display_name'], binary_info['description'])
            self.log_step("STRUCTURE_DEFAULT", "Using default description")
        
        content_md = '''+++
title = "{}"
date = {}
description = "{}"
draft = false

[taxonomies]
tags = [{}]
+++

{}

{{{{ wasm_viewer(path="app.js", id="{}-demo") }}}} 

'''.format(
            binary_info['display_name'],
            current_date,
            binary_info['description'],
            tags_str,
            content_text,
            binary_name
        )
        
        with open(os.path.join(project_dir, 'content.md'), 'w', encoding='utf-8') as f:
            f.write(content_md)
            
        self.log_step("STRUCTURE_COMPLETE", "Project structure created: {}".format(project_dir))
        return project_dir
    
    def copy_wasm_files(self, binary_name, project_dir):
        """Copy WASM files to project directory"""
        self.log_step("WASM_COPY_START", "Copying WASM files for {}".format(binary_name))
        
        source_repo = self.config['PATHS']['source_repo']
        wasm_output_dir = os.path.join(source_repo, 'wasm', 'output', binary_name)
        
        self.log_step("WASM_SOURCE", "Source: {}".format(wasm_output_dir))
        
        wasm_files = [
            'app.js',
            'app.d.ts', 
            '{}_bg.wasm'.format(binary_name),
            '{}_bg.wasm.d.ts'.format(binary_name)
        ]
        
        copied_files = []
        missing_files = []
        
        for i, filename in enumerate(wasm_files, 1):
            self.log_progress(i, len(wasm_files), "Copying: {}".format(filename))
            
            src_path = os.path.join(wasm_output_dir, filename)
            if os.path.exists(src_path):
                dst_path = os.path.join(project_dir, filename)
                shutil.copy2(src_path, dst_path)
                file_size = os.path.getsize(src_path)
                self.log_step("WASM_FILE", "Copied {} ({:.1f}KB)".format(filename, file_size/1024))
                copied_files.append(filename)
            else:
                self.log_step("WASM_MISSING", "File not found: {}".format(filename))
                missing_files.append(filename)
        
        self.log_step("WASM_COPY_COMPLETE", "Copied {}/{} files".format(len(copied_files), len(wasm_files)))
        
        if missing_files:
            self.log_step("WASM_COPY_WARNINGS", "Missing files: {}".format(', '.join(missing_files)))
    
    def copy_assets(self):
        """Copy assets to target repository"""
        self.log_step("ASSETS_START", "Copying assets to target repository")
        
        source_repo = self.config['PATHS']['source_repo']
        target_repo = self.config['PATHS']['target_repo']
        
        source_assets = os.path.join(source_repo, 'assets')
        target_assets = os.path.join(target_repo, 'static', 'assets')
        
        self.log_step("ASSETS_CHECK", "Source: {} → Target: {}".format(source_assets, target_assets))
        
        if not os.path.exists(source_assets):
            self.log_step("ASSETS_MISSING", "Source assets directory does not exist")
            return
            
        os.makedirs(target_assets, exist_ok=True)
        self.log_step("ASSETS_TARGET", "Created target directory")
        
        def ignore_patterns(dir, files):
            return [f for f in files if f.startswith('.git') or f.endswith('.gitkeep')]
        
        items = os.listdir(source_assets)
        total_items = len(items)
        self.log_step("ASSETS_SCAN", "Found {} items to copy".format(total_items))
        
        for i, item in enumerate(items, 1):
            self.log_progress(i, total_items, "Copying: {}".format(item))
            
            src_item = os.path.join(source_assets, item)
            dst_item = os.path.join(target_assets, item)
            
            if os.path.isdir(src_item):
                if os.path.exists(dst_item):
                    shutil.rmtree(dst_item)
                shutil.copytree(src_item, dst_item, ignore=ignore_patterns)
                self.log_step("ASSETS_DIR", "Copied directory: {}".format(item))
            else:
                shutil.copy2(src_item, dst_item)
                self.log_step("ASSETS_FILE", "Copied file: {}".format(item))
        
        self.log_step("ASSETS_COMPLETE", "Assets copied successfully")
    
    def publish_binary(self, binary_info):
        """Publish a single binary"""
        binary_name = binary_info['name']
        binary_start = time.time()
        
        self.log_step("BINARY_START", "Publishing {} ({})".format(binary_name, binary_info['display_name']))
        
        # Step 1: Build WASM
        if not self.build_wasm(binary_name):
            self.log_step("BINARY_SKIP", "Skipping {}: Build failed".format(binary_name))
            return False
        
        # Step 2: Create project structure and load README
        self.log_step("BINARY_STRUCTURE", "Creating project structure for {}".format(binary_name))
        project_dir = self.create_project_structure(binary_info)
        
        # Step 3: Copy WASM files
        self.log_step("BINARY_COPY", "Copying WASM files for {}".format(binary_name))
        self.copy_wasm_files(binary_name, project_dir)
        
        binary_time = time.time() - binary_start
        self.log_step("BINARY_COMPLETE", "Successfully published {} in {:.1f}s".format(binary_name, binary_time))
        return True
    
    def publish_all(self, specific_binary=None):
        """Publish all binaries or a specific one"""
        self.log_step("PUBLISH_START", "Starting automated publishing process")
        
        # Try to load publish configuration first
        specified_binaries = self.load_publish_config()
        
        # Parse Cargo.toml with or without binary filtering
        binaries = self.parse_cargo_toml(specified_binaries)
        
        # Handle specific binary request
        if specific_binary:
            self.log_step("PUBLISH_FILTER", "Filtering for specific binary: {}".format(specific_binary))
            binaries = [b for b in binaries if b['name'] == specific_binary]
            if not binaries:
                self.log_step("PUBLISH_NOT_FOUND", "Binary not found: {}".format(specific_binary))
                return False
            self.log_step("PUBLISH_SPECIFIC", "Publishing only: {}".format(specific_binary))
        
        # Skip if no binaries to publish
        if not binaries:
            self.log_step("PUBLISH_EMPTY", "No binaries to publish")
            return False
        
        self.log_step("PUBLISH_PLAN", "Publishing {} binaries: {}".format(
            len(binaries), ', '.join([b['name'] for b in binaries])))
        
        # Copy assets first
        self.copy_assets()
        
        successful = 0
        failed = 0
        failed_binaries = []
        
        self.log_step("PUBLISH_BINARIES", "Starting binary publication process")
        
        for i, binary_info in enumerate(binaries, 1):
            self.log_progress(i, len(binaries), "Publishing: {}".format(binary_info['name']))
            
            if self.publish_binary(binary_info):
                successful += 1
                self.log_step("PUBLISH_SUCCESS", "{} published successfully".format(binary_info['name']))
            else:
                failed += 1
                failed_binaries.append(binary_info['name'])
                self.log_step("PUBLISH_FAILED", "{} publication failed".format(binary_info['name']))
        
        # Final summary
        total_time = time.time() - self.start_time
        self.log_step("PUBLISH_COMPLETE", "Publishing completed in {:.1f}s".format(total_time))
        self.log_step("PUBLISH_STATS", "Successful: {} | Failed: {} | Total: {}".format(
            successful, failed, len(binaries)))
        
        if failed_binaries:
            self.log_step("PUBLISH_FAILURES", "Failed binaries: {}".format(', '.join(failed_binaries)))
        
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
    
    print("=" * 80)
    print("GitHub Auto Publisher for WASM Projects")
    print("=" * 80)
    
    specific_binary = sys.argv[1] if len(sys.argv) > 1 else None
    
    if specific_binary:
        print("Target Binary: {}".format(specific_binary))
    else:
        print("Target: All binaries")
    
    print("Start Time: {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("-" * 80)
    
    publisher = GitHubAutoPublisher()
    success = publisher.publish_all(specific_binary)
    
    print("-" * 80)
    print("Exit Code: {}".format(0 if success else 1))
    print("=" * 80)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 