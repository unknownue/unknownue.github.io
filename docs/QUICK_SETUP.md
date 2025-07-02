# Quick Setup Guide for Automated WASM Builds

## 🚀 5-Minute Setup

### Step 1: Create GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` and `workflow`
4. Copy the generated token

### Step 2: Configure Source Repository
1. Go to `bevy_prototype_codex` repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `DISPATCH_TOKEN`
5. Value: Your GitHub token from Step 1

### Step 2.5: Configure Target Repository  
1. Go to `unknownue.github.io` repository
2. Settings → Secrets and variables → Actions
3. Add the same `DISPATCH_TOKEN` secret
4. Go to Settings → Pages
5. Under "Source", select "Deploy from a branch"
6. Select "gh-pages" branch and "/ (root)" folder

### Step 3: Test the Setup
1. Go to `bevy_prototype_codex` → Actions tab
2. Select "Trigger WASM Build" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait for completion (green checkmark)

### Step 4: Verify Results
1. Go to `unknownue.github.io` → Actions tab
2. You should see "Auto Build and Deploy WASM Projects" running
3. Check the workflow summary for deployment status and generated files

## ✅ You're Done!

The system is now fully automated:

- **Push code** to `bevy_prototype_codex` → Automatic WASM build and deploy via Zola
- **Update blog content** (`content/posts/`, `content/pull_request/`) → Automatic blog rebuild with WASM projects
- **Manual trigger** → Run workflows manually for both WASM and blog
- **Weekly builds** → Automatic WASM updates every Sunday
- **No main branch pollution** → Generated files are deployed to gh-pages branch only

## 🔄 Workflow Trigger Logic

The system uses two separate workflows that complement each other:

### WASM Build Workflow (`build_bevy_prototype_codex.yml`)
- **Triggered by**: External `wasm-build-trigger` event, manual trigger, weekly schedule
- **Generates**: `content/projects/` and `static/assets/` files 
- **Deployment**: Direct to gh-pages branch via Zola

### Blog Build Workflow (`build_blog.yml`)  
- **Triggered by**: Changes to `content/posts/`, `content/pull_request/`, templates, styles
- **Restores**: Existing WASM projects from gh-pages before building
- **Deployment**: Complete site rebuild including preserved WASM files

This ensures both workflows can run independently without conflicting.

## 🔧 Common Issues

### "Repository not found" error
- Check if your GitHub token has access to both repositories
- Verify the token has `repo` and `workflow` permissions
- For private repositories, ensure `DISPATCH_TOKEN` is configured correctly

### Build timeouts
- Rust compilation can take 10+ minutes initially
- Subsequent builds are faster due to caching

### No changes detected
- The system only commits if files actually changed
- Check the workflow logs for details

## 📊 Monitoring

- **Build status**: Check Actions tabs in both repositories
- **Build logs**: Click on workflow runs for detailed information
- **Deployment status**: Check workflow summary and gh-pages branch
- **Generated files**: Files are deployed to gh-pages branch (not in main branch)

## 🎯 Next Steps

1. **Customize triggers**: Edit `paths` in trigger workflow to monitor different files
2. **Add notifications**: Configure GitHub notifications for build status
3. **Optimize builds**: Add caching for faster compilation times

For detailed configuration, see [AUTOMATED_WASM_BUILD.md](./AUTOMATED_WASM_BUILD.md) 