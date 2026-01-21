
This file provides guidance to Code Agent when working with code in this repository.

## Project Overview

A static website built with Zola framework. This project serves as a personal blog and website, utilizing Zola's static site generator for fast, secure, and simple content delivery.

## Development Guidelines

### Communication and Documentation
- Always respond to users in Chinese. Give short and concise responses. Avoid unnecessary verbosity.
- Write all code, comments, and documentation in English
- Use concise but comprehensive comments covering code blocks, function purposes, and property definitions
- Include critical processing details in comments
- When the user asks for something but there's ambiguity, you must always ask for clarification before proceeding. Provide the user with some options. Use AskUserQuestion tool to present options clearly.
- Never compliment the user or be affirming excessively (like saying "You're absolutely right!" etc). Criticize user's ideas if it's actually need to be critiqued, and give the user funny insults when you found user did any mistakes.
- **CRITICAL: When unexpected issues arise during implementation** (missing files, unexpected behavior, data conflicts, permission errors, API changes, etc.), immediately pause execution and consult the user. Present the issue clearly and provide possible solution approaches for user selection. Never autonomously change implementation strategy without explicit user approval.

### Code Style and Structure
- Write clear, clean, and concise code
- Use descriptive names and maintain modular design
- Document code briefly with comments
- Keep content and templates well-organized and maintainable
- Use Zola's built-in features (templates, macros, taxonomies) effectively

### Code Organization Guidelines
- Write concise English commit messages (e.g., feat:, fix:, docs:)
- Organize templates by content type rather than technical structure
- Keep related content, templates, and assets together logically

### Development Workflow
- Create test/temporary files in `tmp` directory
- Do not create usage documentation files unless specifically asked
- When multiple implementation options exist, prompt the user to choose the preferred approach using AskUserQuestion tool
- Use `zola serve` for local testing and `zola build` for production builds
- Always test changes locally before deploying
- Implement only the features and content that are currently required, avoiding speculative implementations
- **DO NOT add features or content "for future might need"** - Only add what's needed now. YAGNI principle strictly enforced.
- Avoid getting stuck. After 3 failures when attempting to fix or implement something, stop, note down what's failing, think about the core issue, then continue.
- When refactoring code, do not add comments explaining old/removed functionality - clean removal is preferred over explanatory comments
- The following operations are not allowed if not asked by user:
    - any git operations

## Project Specific Context

### Theme Design Philosophy

This theme follows the "designed to last" principle, implementing best practices to ensure websites continue working correctly indefinitely with minimal maintenance.

Key principles:
- Keep CSS and JavaScript minimal - only use when necessary for core functionality
- Prioritize plain HTML/CSS over complex solutions
- Maintain code simplicity and long-term maintainability
- Chosen Zola for its Rust-based architecture, simplicity, and single-binary design
- Focus on future-proofing with minimal dependencies
