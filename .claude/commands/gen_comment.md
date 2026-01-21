---
allowed-tools: [Bash, Read, Write, Edit]
description: "Generate git commit message from staged changes and conversation history, output to git-commit.txt"
---

Generate git commit message based on staged changes and recent conversation history.

## Task Requirements

### Phase 1: Analyze Staged Changes
1. Check git status to identify staged files
2. **Early Exit**: If no staged changes are found, stop execution and inform the user to stage their changes first
3. Review staged changes using git diff --cached
4. Analyze the nature and scope of changes

### Phase 2: Generate Conventional Commit Message
Follow conventional commit format:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Commit Types:**
- `feat:` - new feature (MINOR in Semantic Versioning)
- `fix:` - bug fix (PATCH in Semantic Versioning)
- `docs:` - documentation changes
- `style:` - formatting, missing semicolons, etc.
- `refactor:` - code refactoring
- `perf:` - performance improvements
- `test:` - adding tests
- `build:` - build system changes
- `ci:` - CI configuration changes
- `chore:` - maintenance tasks

**Message Requirements:**
1. Keep description under 60 characters
2. Use all lowercase letters for description
3. Focus on most important change if multiple changes exist
4. Determine the most appropriate commit type
5. Use optional scope in lowercase if applicable
6. **Content Accuracy**: Commit message must reflect only actual staged changes, not historical modifications or conversation context that don't exist in the staged content
7. **Language Requirement**: Commit message MUST be written in English only. Do not use any other languages.
8. **Body and Footer Guidelines:**
   - For simple commits: Only use the description line, omit body and footer
   - For complex commits: Add body with detailed explanation
   - Add footer only for breaking changes or issue references
   - Judge complexity based on scope and impact of changes

### Phase 3: Output to File
1. Write the generated commit message to tmp/git-commit.txt
2. Overwrite existing file if it exists
3. Do NOT execute git commit command

**Note**: This command analyzes staged changes and generates commit messages but does not perform actual commits.

Please generate commit message for the current staged changes.