// Initialize highlight.js
document.addEventListener('DOMContentLoaded', function() {
    // Check if highlight.js is loaded
    if (typeof hljs !== 'undefined') {
        // Configure highlight.js
        hljs.configure({
            tabReplace: '    ', // 4 spaces
            languages: ['rust', 'javascript', 'python', 'cpp', 'go', 'typescript'],
            ignoreUnescapedHTML: true
        });
        
        // Initialize all <pre><code> blocks
        document.querySelectorAll('pre code').forEach(function(block) {
            hljs.highlightElement(block);
        });
        
        // Initial highlighting for diff blocks
        highlightDiffBlocks();
        
        // Re-run highlight on diff blocks after a delay to ensure they're fully rendered
        setTimeout(highlightDiffBlocks, 500);
        
        console.log('Highlight.js initialized successfully');
    } else {
        console.error('Highlight.js not loaded');
    }
    
    // Function to highlight diff blocks
    function highlightDiffBlocks() {
        try {
            // Target diff code containers
            document.querySelectorAll('.d2h-code-line-ctn').forEach(function(block) {
                hljs.highlightElement(block);
            });
            
            // Also try to highlight specific code parts
            document.querySelectorAll('.d2h-code-side-line .d2h-code-line-ctn').forEach(function(block) {
                hljs.highlightElement(block);
            });
            
            // Try direct content highlighting too
            document.querySelectorAll('.d2h-code-line-ctn code').forEach(function(block) {
                hljs.highlightElement(block);
            });
            
            console.log('Diff blocks highlighted');
        } catch (e) {
            console.error('Error highlighting diff blocks:', e);
        }
    }
}); 