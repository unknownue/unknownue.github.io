document.addEventListener('DOMContentLoaded', function() {
    // Check if this is a MD content page (contains article with class md-content-page)
    const isMdContentPage = document.querySelector('article.md-content-page') !== null;
    
    // Check if URL suggests this is a MD file
    const currentUrl = window.location.pathname;
    const urlSuggestsMdFile = currentUrl.endsWith('.md') || 
                             currentUrl.includes('/posts/') || 
                             (currentUrl.includes('/pull_request/') && currentUrl.split('/').length > 2) || 
                             (currentUrl.split('/').pop() && !currentUrl.split('/').pop().includes('.'));
    
    // Skip list pages and section pages - don't try to detect patch files on them
    const isListPage = document.querySelector('.pr-list') !== null || 
                       document.querySelector('.pull-request-content > h2') !== null ||
                       document.querySelector('.projects-content') !== null ||
                       document.querySelector('.project-section-content') !== null ||
                       document.querySelector('.project-list') !== null ||
                       document.querySelector('.project-content-list') !== null;
    
    // Display button only on MD content pages and not on list pages
    if ((isMdContentPage || urlSuggestsMdFile) && !isListPage) {
        // Check if patch info element exists
        const patchInfoElement = document.getElementById('patch-info');
        
        if (patchInfoElement) {
            // Get patch path from page element if available, otherwise use default path strategy
            let patchRelativePath = patchInfoElement.getAttribute('data-patch-path');
            
            // Create Diff button regardless of patch file existence check
            createDiffButton(patchRelativePath || buildDefaultPatchPath(currentUrl));
            
            // Try to find appropriate patch file if path not explicitly specified
            if (!patchRelativePath) {
                detectPatchFile(currentUrl);
            } else {
                // Still verify the patch file exists
                checkPatchFile(patchRelativePath);
            }
        } else {
            // No patch info element, use URL-based detection
            detectPatchFile(currentUrl);
        }
    }
    
    // Build default patch path based on current URL
    function buildDefaultPatchPath(url) {
        // Remove trailing slash
        if (url.endsWith('/')) {
            url = url.slice(0, -1);
        }
        
        // Get the last part of the URL as article name (without .html or .md)
        const articleName = url.split('/').pop().replace(/\.(html|md)$/, '');
        
        // Try to extract PR number if it's a PR page
        // Example: pr_16427_en_20250319 -> extract 16427
        if (articleName.startsWith('pr_')) {
            const parts = articleName.split('_');
            if (parts.length >= 2) {
                const prNumber = parts[1];
                return `/patches/pr_${prNumber}.patch`;
            }
        }
        
        // Return a default path
        return `/patches/${articleName}.patch`;
    }
    
    // Try to detect the patch file based on URL
    function detectPatchFile(url) {
        // Remove trailing slash
        if (url.endsWith('/')) {
            url = url.slice(0, -1);
        }
        
        // Get the last part of the URL as article name (without .html or .md)
        const articleName = url.split('/').pop().replace(/\.(html|md)$/, '');
        
        // Try to extract PR number if it's a PR page
        let prNumber = null;
        if (articleName.startsWith('pr_')) {
            const parts = articleName.split('_');
            if (parts.length >= 2) {
                prNumber = parts[1];
            }
        }
        
        // Build possible paths for patch file
        const possiblePatchPaths = [];
        
        if (prNumber) {
            // If PR number was found, prioritize these paths
            possiblePatchPaths.push(
                `/pr_${prNumber}.patch`,
                `/patches/pr_${prNumber}.patch`,
                `/pull_request/pr_${prNumber}.patch`,
                `/content/pull_request/pr_${prNumber}.patch`,
                `/static/patches/pr_${prNumber}.patch`
            );
        }
        
        // Add standard paths as fallback
        possiblePatchPaths.push(
            `/${articleName}.patch`,                      // /article-name.patch
            `/posts/${articleName}.patch`,                // /posts/article-name.patch
            `/content/posts/${articleName}.patch`,        // /content/posts/article-name.patch 
            `/patches/${articleName}.patch`,              // /patches/article-name.patch
            `/static/patches/${articleName}.patch`        // /static/patches/article-name.patch
        );
        
        // Check if patch file exists in any location
        checkMultiplePatchPaths(possiblePatchPaths, function(patchExists, patchPath) {
            if (patchExists) {
                // Update the button's patch path if it exists
                const diffButton = document.querySelector('.diff-button');
                if (diffButton) {
                    diffButton.setAttribute('data-patch-path', patchPath);
                } else {
                    // Button doesn't exist yet, create it
                    createDiffButton(patchPath);
                }
            }
        });
    }
    
    // Check a single patch file
    function checkPatchFile(patchRelativePath) {
        // If path already starts with slash, don't add another one
        const normalizedPath = patchRelativePath.startsWith('/') ? 
                              patchRelativePath : 
                              `/${patchRelativePath}`;
        
        // Build possible full paths
        const possiblePaths = [
            normalizedPath,
            `/content${normalizedPath}`,
            `/static/patches/${normalizedPath.split('/').pop()}`
        ];
        
        // If it's a PR patch, add PR-specific paths
        if (normalizedPath.includes('pr_')) {
            const patchFilename = normalizedPath.split('/').pop();
            possiblePaths.push(
                `/patches/${patchFilename}`,
                `/pull_request/${patchFilename}`
            );
        }
        
        checkMultiplePatchPaths(possiblePaths, function(patchExists, patchPath) {
            if (patchExists) {
                // Update the button's patch path if it exists
                const diffButton = document.querySelector('.diff-button');
                if (diffButton) {
                    diffButton.setAttribute('data-patch-path', patchPath);
                }
            }
        });
    }
    
    // Check multiple paths for patch file existence
    function checkMultiplePatchPaths(paths, callback, index = 0) {
        // If we've checked all paths and found nothing, return false
        if (index >= paths.length) {
            callback(false, null);
            return;
        }
        
        // Check current path
        fetch(paths[index])
            .then(response => {
                if (response.ok) {
                    // File exists, return
                    callback(true, paths[index]);
                } else {
                    // Check next path
                    checkMultiplePatchPaths(paths, callback, index + 1);
                }
            })
            .catch((error) => {
                // Error occurred, check next path
                checkMultiplePatchPaths(paths, callback, index + 1);
            });
    }
    
    // Create Diff button and sidebar
    function createDiffButton(patchPath) {
        if (!checkDocumentBody()) return;
        // Don't create button if it already exists
        if (document.querySelector('.diff-button')) {
            return;
        }
        
        // Create the diff button
        const diffButton = document.createElement('button');
        diffButton.className = 'diff-button';
        diffButton.textContent = 'View Diff';
        diffButton.title = 'View diff for this article';
        diffButton.setAttribute('aria-label', 'Show diff sidebar');
        diffButton.setAttribute('data-patch-path', patchPath);
        
        // Adjust button position to prevent overlap with top bar
        diffButton.style.top = '80px';
        
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
        splitViewButton.textContent = 'Split View';
        splitViewButton.title = 'Switch to split view';
        
        const unifiedViewButton = document.createElement('button');
        unifiedViewButton.id = 'diff-unified-view';
        unifiedViewButton.className = 'diff-view-button';
        unifiedViewButton.textContent = 'Unified View';
        unifiedViewButton.title = 'Switch to unified view';
        
        viewControls.appendChild(splitViewButton);
        viewControls.appendChild(unifiedViewButton);
        
        sidebarHeader.appendChild(viewControls);
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'diff-close-button';
        closeButton.textContent = '×';
        closeButton.title = 'Close diff view';
        closeButton.setAttribute('aria-label', 'Close diff sidebar');
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
        loadingIndicator.innerHTML = '<div class="loader"></div><p>Loading diff content...</p>';
        diffContent.appendChild(loadingIndicator);
        
        diffSidebar.appendChild(diffContent);
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'diff-overlay';
        
        // Add elements to body
        if (checkDocumentBody()) {
            document.body.appendChild(diffSidebar);
            document.body.appendChild(overlay);
        }
        
        // Initial view mode
        let currentViewMode = 'side-by-side'; // Default split view
        let diffInstance = null;
        let patchContent = null;
        
        // Toggle sidebar function
        function toggleSidebar() {
            if (!checkDocumentBody()) return;
            
            const isOpening = !diffSidebar.classList.contains('open');
            
            diffSidebar.classList.toggle('open');
            overlay.classList.toggle('open');
            
            // Update button text
            if (diffSidebar.classList.contains('open')) {
                diffButton.textContent = 'Hide Diff';
                document.body.style.overflow = 'hidden';
                
                // Load patch content (if first time opening)
                if (isOpening && !patchContent) {
                    loadPatchContent(patchPath);
                }
            } else {
                diffButton.textContent = 'View Diff';
                document.body.style.overflow = '';
                // Reset sidebar width, ensure complete hiding when closed
                diffSidebar.style.width = '90%';
            }
        }
        
        // Load Patch file content
        function loadPatchContent(url) {
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
                    renderDiff(patchContent, currentViewMode);
                })
                .catch(error => {
                    diffContainer.innerHTML = `
                        <div class="diff-error">
                            <h3>Failed to load diff file</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                    loadingIndicator.style.display = 'none';
                    diffContainer.style.display = 'block';
                });
        }
        
        // Render diff content using diff2html
        function renderDiff(diffText, outputFormat) {
            // Clear previous content
            diffContainer.innerHTML = '';
            
            try {
                // Create diff2html configuration
                const configuration = {
                    drawFileList: true,
                    matching: 'lines',
                    outputFormat: outputFormat,
                    highlight: true,
                    renderNothingWhenEmpty: true
                };
                
                // Initialize diff2html UI
                diffInstance = new Diff2HtmlUI(diffContainer, diffText, configuration);
                diffInstance.draw();
                
                // Set container class to distinguish unified and split views
                diffContainer.classList.remove('d2h-inline-file', 'side-by-side-file-diff');
                if (outputFormat === 'line-by-line') {
                    diffContainer.classList.add('d2h-inline-file');
                } else {
                    diffContainer.classList.add('side-by-side-file-diff');
                }
                
                // Apply custom styling and highlighting
                setTimeout(applyCustomHighlighting, 100);
                
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                diffContainer.style.display = 'block';
            } catch (error) {
                diffContainer.innerHTML = `
                    <div class="diff-error">
                        <h3>Failed to render diff content</h3>
                        <p>${error.message}</p>
                    </div>
                `;
                loadingIndicator.style.display = 'none';
                diffContainer.style.display = 'block';
            }
        }
        
        // Apply custom syntax highlighting
        function applyCustomHighlighting() {
            const codeContainers = document.querySelectorAll('#diff-container .d2h-code-line-ctn');
            
            codeContainers.forEach(function(container) {
                let html = container.innerHTML;
                
                // Skip already highlighted content
                if (html.includes('class="hljs') || html.includes('class="deleted"') || html.includes('class="added"')) {
                    return;
                }
                
                // Detect current file type
                const fileElem = container.closest('.d2h-file-wrapper');
                const fileName = fileElem ? fileElem.querySelector('.d2h-file-name').textContent.trim() : '';
                const fileExt = fileName.split('.').pop().toLowerCase();
                
                // Apply different highlighting rules for different file types
                if (container.innerHTML.startsWith('+')) {
                    html = html.replace(/^(\+)(.*)$/, '$1<span class="added">$2</span>');
                } else if (container.innerHTML.startsWith('-')) {
                    html = html.replace(/^(-)(.*)$/, '$1<span class="deleted">$2</span>');
                }
                
                container.innerHTML = html;
            });
        }
        
        // View switching button events
        splitViewButton.addEventListener('click', function() {
            if (currentViewMode !== 'side-by-side') {
                splitViewButton.classList.add('active');
                unifiedViewButton.classList.remove('active');
                currentViewMode = 'side-by-side';
                
                // Immediately update container class
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
                
                // Immediately update container class
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
        
        // Add manual resize functionality
        let isResizing = false;
        let startX, startWidth;
        
        resizeHandle.addEventListener('mousedown', function(e) {
            isResizing = true;
            startX = e.clientX;
            startWidth = parseInt(window.getComputedStyle(diffSidebar).width, 10);
            document.documentElement.style.cursor = 'ew-resize';
            diffSidebar.classList.add('resizing'); // Add resizing class
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            const width = startWidth + (e.clientX - startX);
            // Set minimum and maximum width limits
            if (width > 300 && width < window.innerWidth * 0.98) {
                diffSidebar.style.width = width + 'px';
                
                // Update content layout in real-time
                if (diffInstance) {
                    // Adjust DOM element sizes to match new container width
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
                diffSidebar.classList.remove('resizing'); // Remove resizing class
            }
        });
        
        // Keyboard event handling
        document.addEventListener('keydown', function(e) {
            // Close sidebar when ESC key is pressed
            if (e.key === 'Escape' && diffSidebar.classList.contains('open')) {
                toggleSidebar();
            }
        });
        
        // Add touch event support
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
                
                // Update content layout in real-time
                if (diffInstance) {
                    const diffContainerElements = diffContainer.querySelectorAll('.d2h-file-diff');
                    diffContainerElements.forEach(el => {
                        el.style.width = '100%';
                    });
                }
            }
            e.preventDefault(); // Prevent page scrolling
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
    
    // 添加document.body存在性检查的函数
    function checkDocumentBody() {
        return document.body !== null;
    }
}); 