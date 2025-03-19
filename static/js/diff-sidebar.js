document.addEventListener('DOMContentLoaded', function() {
    // 只在文章页面显示按钮
    // 检查是否是文章页面（页面上有article元素）
    const isPostPage = document.querySelector('article') !== null;
    
    if (isPostPage) {
        // Create the diff button
        const diffButton = document.createElement('button');
        diffButton.className = 'diff-button';
        diffButton.textContent = 'View Diff';
        diffButton.title = '查看此文章的差异';
        diffButton.setAttribute('aria-label', '显示差异侧边栏');
        document.body.appendChild(diffButton);
    
        // Create diff sidebar
        const diffSidebar = document.createElement('div');
        diffSidebar.className = 'diff-sidebar';
        
        // Create sidebar header
        const sidebarHeader = document.createElement('div');
        sidebarHeader.className = 'diff-sidebar-header';
        
        // Create title
        const sidebarTitle = document.createElement('h2');
        sidebarTitle.textContent = 'Diff View';
        sidebarHeader.appendChild(sidebarTitle);
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'diff-close-button';
        closeButton.textContent = '×';
        closeButton.title = '关闭差异视图';
        closeButton.setAttribute('aria-label', '关闭差异侧边栏');
        sidebarHeader.appendChild(closeButton);
        
        diffSidebar.appendChild(sidebarHeader);
        
        // Create content container with sample content
        const diffContent = document.createElement('div');
        diffContent.className = 'diff-content';
        
        // 添加一些示例内容，并高亮显示diff语法
        const sampleContent = `
            <div class="diff-info">
                <p>这是差异视图的示例内容，用于测试侧边栏的显示效果。</p>
                <p>未来将在这里显示实际的patch文件内容。</p>
            </div>
            <div class="diff-sample">
                <pre>diff --git a/example.md b/example.md
index 1234567..89abcdef 100644
--- a/example.md
+++ b/example.md
@@ -1,5 +1,7 @@
 # 示例文档
 
-<span class="deleted">这是原始内容。</span>
+<span class="added">这是更新后的内容。</span>
+
+<span class="added">这是新增的一行。</span>
 
 ## 文档小节</pre>
            </div>
        `;
        
        diffContent.innerHTML = sampleContent;
        diffSidebar.appendChild(diffContent);
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'diff-overlay';
        
        // Add elements to body
        document.body.appendChild(diffSidebar);
        document.body.appendChild(overlay);
        
        // Toggle sidebar function
        function toggleSidebar() {
            diffSidebar.classList.toggle('open');
            overlay.classList.toggle('open');
            
            // 更新按钮文本
            if (diffSidebar.classList.contains('open')) {
                diffButton.textContent = 'Hide Diff';
                document.body.style.overflow = 'hidden';
            } else {
                diffButton.textContent = 'View Diff';
                document.body.style.overflow = '';
            }
        }
        
        // Event listeners
        diffButton.addEventListener('click', toggleSidebar);
        closeButton.addEventListener('click', toggleSidebar);
        overlay.addEventListener('click', toggleSidebar);
        
        // 键盘事件处理
        document.addEventListener('keydown', function(e) {
            // 当按ESC键时关闭侧边栏
            if (e.key === 'Escape' && diffSidebar.classList.contains('open')) {
                toggleSidebar();
            }
        });
    }
}); 