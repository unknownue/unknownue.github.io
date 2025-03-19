document.addEventListener('DOMContentLoaded', function() {
    console.log('Diff sidebar script loaded');
    
    // 只在文章页面显示按钮
    // 检查是否是文章页面（页面上有article元素）
    const isPostPage = document.querySelector('article') !== null;
    console.log('Is post page:', isPostPage);
    
    if (isPostPage) {
        // 检查是否存在patch信息元素
        const patchInfoElement = document.getElementById('patch-info');
        
        // 从文章URL提取信息
        const currentUrl = window.location.pathname;
        const isArticlePage = currentUrl.includes('/posts/') || currentUrl.includes('/pull_request/');
        
        console.log('Current URL:', currentUrl);
        console.log('Patch info element exists:', !!patchInfoElement);
        
        if (patchInfoElement && patchInfoElement.getAttribute('data-patch-exists') === 'true') {
            // 从页面元素获取patch路径
            const patchRelativePath = patchInfoElement.getAttribute('data-patch-path');
            
            console.log('Patch relative path from page element:', patchRelativePath);
            
            if (patchRelativePath) {
                // 检查patch文件是否存在
                checkPatchFile(patchRelativePath);
            }
        } else if (isArticlePage) {
            // 回退机制：如果页面中没有patch信息元素，使用URL检测
            console.log('Using URL-based patch detection');
            
            // 从URL中提取文章名
            let articlePath = currentUrl;
            
            // 移除尾部的斜杠（如果有）
            if (articlePath.endsWith('/')) {
                articlePath = articlePath.slice(0, -1);
            }
            
            // 获取URL的最后一部分作为文章名（不包含.html）
            const articleName = articlePath.split('/').pop().replace('.html', '');
            console.log('Article name from URL:', articleName);
            
            // 构建patch文件的可能路径
            // 使用数组存储所有可能的路径位置
            const possiblePatchPaths = [
                `/${articleName}.patch`,                      // /article-name.patch
                `/posts/${articleName}.patch`,                // /posts/article-name.patch
                `/content/posts/${articleName}.patch`,        // /content/posts/article-name.patch 
                `/patches/${articleName}.patch`,              // /patches/article-name.patch
                `/static/patches/${articleName}.patch`        // /static/patches/article-name.patch
            ];
            
            console.log('Checking possible patch paths:', possiblePatchPaths);
            
            // 检查patch文件是否存在于任一位置
            checkMultiplePatchPaths(possiblePatchPaths, function(patchExists, patchPath) {
                console.log('Patch exists:', patchExists, 'Path:', patchPath);
                if (patchExists) {
                    // Patch文件存在，创建按钮
                    createDiffButton(patchPath);
                }
                // 如果patch文件不存在，不显示按钮
            });
        }
    }
    
    // 检查单个patch文件
    function checkPatchFile(patchRelativePath) {
        // 构建可能的完整路径
        const possiblePaths = [
            `/${patchRelativePath}`,
            `/content/${patchRelativePath}`,
            `/static/patches/${patchRelativePath.split('/').pop()}`,
            `/posts/${patchRelativePath.split('/').pop()}`
        ];
        
        console.log('Checking possible paths for file:', possiblePaths);
        
        checkMultiplePatchPaths(possiblePaths, function(patchExists, patchPath) {
            if (patchExists) {
                // Patch文件存在，创建按钮
                createDiffButton(patchPath);
                console.log('已找到patch文件:', patchPath);
            } else {
                console.log('未找到patch文件:', patchRelativePath);
            }
        });
    }
    
    // 检查多个路径中是否存在patch文件
    function checkMultiplePatchPaths(paths, callback, index = 0) {
        // 如果已经检查了所有路径还没找到，则返回不存在
        if (index >= paths.length) {
            console.log('No patch file found after checking all paths');
            callback(false, null);
            return;
        }
        
        console.log(`Checking path (${index + 1}/${paths.length}):`, paths[index]);
        
        // 检查当前路径
        fetch(paths[index])
            .then(response => {
                console.log('Fetch response for', paths[index], ':', response.status);
                if (response.ok) {
                    // 文件存在，返回
                    console.log('Patch file found at:', paths[index]);
                    callback(true, paths[index]);
                } else {
                    // 检查下一个路径
                    checkMultiplePatchPaths(paths, callback, index + 1);
                }
            })
            .catch((error) => {
                // 发生错误，检查下一个路径
                console.log('Error fetching', paths[index], ':', error);
                checkMultiplePatchPaths(paths, callback, index + 1);
            });
    }
    
    // 创建Diff按钮和侧边栏
    function createDiffButton(patchPath) {
        console.log('Creating diff button for path:', patchPath);
        
        // Create the diff button
        const diffButton = document.createElement('button');
        diffButton.className = 'diff-button';
        diffButton.textContent = 'View Diff';
        diffButton.title = '查看此文章的差异';
        diffButton.setAttribute('aria-label', '显示差异侧边栏');
        diffButton.setAttribute('data-patch-path', patchPath);
        document.body.appendChild(diffButton);
    
        // Create diff sidebar
        const diffSidebar = document.createElement('div');
        diffSidebar.className = 'diff-sidebar';
        
        // Create resize handle
        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'diff-resize-handle';
        diffSidebar.appendChild(resizeHandle);
        
        // Create sidebar header
        const sidebarHeader = document.createElement('div');
        sidebarHeader.className = 'diff-sidebar-header';
        
        // Create title
        const sidebarTitle = document.createElement('h2');
        sidebarTitle.textContent = 'Diff View';
        sidebarHeader.appendChild(sidebarTitle);
        
        // Create view control buttons
        const viewControls = document.createElement('div');
        viewControls.className = 'diff-view-controls';
        
        const splitViewButton = document.createElement('button');
        splitViewButton.id = 'diff-split-view';
        splitViewButton.className = 'diff-view-button active';
        splitViewButton.textContent = '并排视图';
        splitViewButton.title = '切换到并排视图';
        
        const unifiedViewButton = document.createElement('button');
        unifiedViewButton.id = 'diff-unified-view';
        unifiedViewButton.className = 'diff-view-button';
        unifiedViewButton.textContent = '统一视图';
        unifiedViewButton.title = '切换到统一视图';
        
        viewControls.appendChild(splitViewButton);
        viewControls.appendChild(unifiedViewButton);
        
        sidebarHeader.appendChild(viewControls);
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'diff-close-button';
        closeButton.textContent = '×';
        closeButton.title = '关闭差异视图';
        closeButton.setAttribute('aria-label', '关闭差异侧边栏');
        sidebarHeader.appendChild(closeButton);
        
        diffSidebar.appendChild(sidebarHeader);
        
        // Create content container
        const diffContent = document.createElement('div');
        diffContent.className = 'diff-content';
        
        // Create diff container
        const diffContainer = document.createElement('div');
        diffContainer.id = 'diff-container';
        diffContainer.className = 'diff-container';
        diffContent.appendChild(diffContainer);
        
        // Add loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'diff-loading';
        loadingIndicator.innerHTML = '<div class="loader"></div><p>加载差异内容...</p>';
        diffContent.appendChild(loadingIndicator);
        
        diffSidebar.appendChild(diffContent);
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'diff-overlay';
        
        // Add elements to body
        document.body.appendChild(diffSidebar);
        document.body.appendChild(overlay);
        
        // Initial view mode
        let currentViewMode = 'side-by-side'; // 默认并排视图
        let diffInstance = null;
        let patchContent = null;
        
        // Toggle sidebar function
        function toggleSidebar() {
            const isOpening = !diffSidebar.classList.contains('open');
            
            diffSidebar.classList.toggle('open');
            overlay.classList.toggle('open');
            
            // 更新按钮文本
            if (diffSidebar.classList.contains('open')) {
                diffButton.textContent = 'Hide Diff';
                document.body.style.overflow = 'hidden';
                
                // 加载patch内容（如果是首次打开）
                if (isOpening && !patchContent) {
                    loadPatchContent(patchPath);
                }
            } else {
                diffButton.textContent = 'View Diff';
                document.body.style.overflow = '';
            }
        }
        
        // 加载Patch文件内容
        function loadPatchContent(url) {
            console.log('Loading patch content from:', url);
            loadingIndicator.style.display = 'block';
            diffContainer.style.display = 'none';
            
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to load patch file');
                    }
                    return response.text();
                })
                .then(text => {
                    patchContent = text;
                    console.log('Patch content loaded, length:', patchContent.length);
                    renderDiff(patchContent, currentViewMode);
                })
                .catch(error => {
                    console.error('Error loading patch file:', error);
                    diffContainer.innerHTML = `
                        <div class="diff-error">
                            <h3>加载差异文件失败</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                    loadingIndicator.style.display = 'none';
                    diffContainer.style.display = 'block';
                });
        }
        
        // 使用diff2html渲染差异内容
        function renderDiff(diffText, outputFormat) {
            console.log('Rendering diff with format:', outputFormat);
            
            // 清空之前的内容
            diffContainer.innerHTML = '';
            
            try {
                // 创建diff2html配置
                const configuration = {
                    drawFileList: true,
                    matching: 'lines',
                    outputFormat: outputFormat,
                    highlight: true,
                    renderNothingWhenEmpty: true
                };
                
                // 初始化diff2html UI
                diffInstance = new Diff2HtmlUI(diffContainer, diffText, configuration);
                diffInstance.draw();
                
                // 设置容器的类，区分统一视图和并排视图
                diffContainer.classList.remove('d2h-inline-file', 'side-by-side-file-diff');
                if (outputFormat === 'line-by-line') {
                    diffContainer.classList.add('d2h-inline-file');
                } else {
                    diffContainer.classList.add('side-by-side-file-diff');
                }
                
                // 应用自定义样式和高亮
                setTimeout(applyCustomHighlighting, 100);
                
                // 隐藏加载指示器
                loadingIndicator.style.display = 'none';
                diffContainer.style.display = 'block';
            } catch (error) {
                console.error('Error rendering diff:', error);
                diffContainer.innerHTML = `
                    <div class="diff-error">
                        <h3>渲染差异内容失败</h3>
                        <p>${error.message}</p>
                    </div>
                `;
                loadingIndicator.style.display = 'none';
                diffContainer.style.display = 'block';
            }
        }
        
        // 应用自定义语法高亮
        function applyCustomHighlighting() {
            const codeContainers = document.querySelectorAll('#diff-container .d2h-code-line-ctn');
            
            codeContainers.forEach(function(container) {
                let html = container.innerHTML;
                
                // 跳过已高亮的内容
                if (html.includes('class="hljs') || html.includes('class="deleted"') || html.includes('class="added"')) {
                    return;
                }
                
                // 检测当前文件类型
                const fileElem = container.closest('.d2h-file-wrapper');
                const fileName = fileElem ? fileElem.querySelector('.d2h-file-name').textContent.trim() : '';
                const fileExt = fileName.split('.').pop().toLowerCase();
                
                // 为不同文件类型应用不同的高亮规则
                if (container.innerHTML.startsWith('+')) {
                    html = html.replace(/^(\+)(.*)$/, '$1<span class="added">$2</span>');
                } else if (container.innerHTML.startsWith('-')) {
                    html = html.replace(/^(-)(.*)$/, '$1<span class="deleted">$2</span>');
                }
                
                container.innerHTML = html;
            });
        }
        
        // 视图切换按钮事件
        splitViewButton.addEventListener('click', function() {
            if (currentViewMode !== 'side-by-side') {
                splitViewButton.classList.add('active');
                unifiedViewButton.classList.remove('active');
                currentViewMode = 'side-by-side';
                
                // 立即更新容器类名
                diffContainer.classList.remove('d2h-inline-file');
                diffContainer.classList.add('side-by-side-file-diff');
                
                if (patchContent) {
                    renderDiff(patchContent, currentViewMode);
                }
            }
        });
        
        unifiedViewButton.addEventListener('click', function() {
            if (currentViewMode !== 'line-by-line') {
                unifiedViewButton.classList.add('active');
                splitViewButton.classList.remove('active');
                currentViewMode = 'line-by-line';
                
                // 立即更新容器类名
                diffContainer.classList.add('d2h-inline-file');
                diffContainer.classList.remove('side-by-side-file-diff');
                
                if (patchContent) {
                    renderDiff(patchContent, currentViewMode);
                }
            }
        });
        
        // Event listeners
        diffButton.addEventListener('click', toggleSidebar);
        closeButton.addEventListener('click', toggleSidebar);
        overlay.addEventListener('click', toggleSidebar);
        
        // 添加手动调整大小功能
        let isResizing = false;
        let startX, startWidth;
        
        resizeHandle.addEventListener('mousedown', function(e) {
            isResizing = true;
            startX = e.clientX;
            startWidth = parseInt(window.getComputedStyle(diffSidebar).width, 10);
            document.documentElement.style.cursor = 'ew-resize';
            diffSidebar.classList.add('resizing'); // 添加调整大小的类
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            const width = startWidth + (e.clientX - startX);
            // 设置最小和最大宽度限制
            if (width > 300 && width < window.innerWidth * 0.98) {
                diffSidebar.style.width = width + 'px';
                
                // 实时更新内容布局
                if (diffInstance) {
                    // 调整DOM元素的大小，使其符合新的容器宽度
                    const diffContainerElements = diffContainer.querySelectorAll('.d2h-file-diff');
                    diffContainerElements.forEach(el => {
                        el.style.width = '100%';
                    });
                }
            }
        });
        
        document.addEventListener('mouseup', function() {
            if (isResizing) {
                isResizing = false;
                document.documentElement.style.cursor = '';
                diffSidebar.classList.remove('resizing'); // 移除调整大小的类
            }
        });
        
        // 键盘事件处理
        document.addEventListener('keydown', function(e) {
            // 当按ESC键时关闭侧边栏
            if (e.key === 'Escape' && diffSidebar.classList.contains('open')) {
                toggleSidebar();
            }
        });
        
        // 添加触摸事件支持
        resizeHandle.addEventListener('touchstart', function(e) {
            if (e.touches.length === 1) {
                isResizing = true;
                startX = e.touches[0].clientX;
                startWidth = parseInt(window.getComputedStyle(diffSidebar).width, 10);
                diffSidebar.classList.add('resizing');
                e.preventDefault();
            }
        });
        
        document.addEventListener('touchmove', function(e) {
            if (!isResizing || e.touches.length !== 1) return;
            const width = startWidth + (e.touches[0].clientX - startX);
            if (width > 300 && width < window.innerWidth * 0.98) {
                diffSidebar.style.width = width + 'px';
                
                // 实时更新内容布局
                if (diffInstance) {
                    const diffContainerElements = diffContainer.querySelectorAll('.d2h-file-diff');
                    diffContainerElements.forEach(el => {
                        el.style.width = '100%';
                    });
                }
            }
            e.preventDefault(); // 防止页面滚动
        });
        
        document.addEventListener('touchend', function() {
            if (isResizing) {
                isResizing = false;
                diffSidebar.classList.remove('resizing');
            }
        });
        
        document.addEventListener('touchcancel', function() {
            if (isResizing) {
                isResizing = false;
                diffSidebar.classList.remove('resizing');
            }
        });
    }
}); 