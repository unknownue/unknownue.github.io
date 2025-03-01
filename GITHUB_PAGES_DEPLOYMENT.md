# GitHub Pages 部署指南

本文档提供了将此 Zola 站点部署到 GitHub Pages 的具体步骤。

## 准备工作

1. 确保您有一个 GitHub 账户
2. 创建一个新的 GitHub 仓库或使用现有仓库
3. 将本地项目推送到 GitHub 仓库

## 配置 base_url

在部署之前，请确保 `config.toml` 文件中的 `base_url` 设置正确：

```toml
base_url = "https://你的用户名.github.io/仓库名称"
```

例如，如果您的 GitHub 用户名是 "johndoe"，仓库名称是 "blog"，则应设置为：

```toml
base_url = "https://johndoe.github.io/blog"
```

## 自动部署（推荐）

本项目已配置了 GitHub Actions 自动部署流程：

1. 将代码推送到 GitHub 仓库的 `main` 或 `master` 分支
2. GitHub Actions 会自动构建站点并部署到 `gh-pages` 分支
3. 首次部署后，需要在仓库设置中配置 GitHub Pages

### 配置 GitHub Pages

1. 在 GitHub 仓库页面，点击 "Settings"
2. 在左侧菜单中，点击 "Pages"
3. 在 "Build and deployment" 部分：
   - Source: 选择 "Deploy from a branch"
   - Branch: 选择 "gh-pages" 分支和 "/ (root)" 目录
4. 点击 "Save"

几分钟后，您的站点将在 `https://你的用户名.github.io/仓库名称` 上可用。

## 手动部署（备选方案）

如果您不想使用 GitHub Actions，也可以手动部署：

1. 在本地构建站点：
   ```bash
   zola build
   ```

2. 将 `public` 目录的内容推送到 `gh-pages` 分支：
   ```bash
   cd public
   git init
   git add .
   git commit -m "Deploy website"
   git remote add origin https://github.com/你的用户名/仓库名称.git
   git push -f origin master:gh-pages
   ```

3. 按照上述 "配置 GitHub Pages" 的步骤配置 GitHub Pages 设置。

## 故障排除

- 如果站点无法正常显示，请检查 GitHub Pages 设置和构建日志
- 确保 `config.toml` 中的 `base_url` 设置正确
- 检查 GitHub Actions 日志中是否有构建错误 