// Debug script for highlight.js and diff2html
// This script is temporarily disabled as it's no longer needed
// Uncomment if debugging is required in the future

/*
document.addEventListener('DOMContentLoaded', function() {
    // Check highlight.js availability
    if (typeof hljs !== 'undefined') {
        console.log('highlight.js is available');
        console.log('highlight.js version:', hljs.versionString);
        console.log('highlight.js languages:', hljs.listLanguages());
    } else {
        console.error('highlight.js is NOT available');
    }
    
    // Check diff2html availability
    if (typeof Diff2HtmlUI !== 'undefined') {
        console.log('diff2html is available');
    } else {
        console.error('diff2html is NOT available');
    }
    
    // Create a test element for highlight.js
    var testContainer = document.createElement('div');
    testContainer.style.display = 'none';
    testContainer.innerHTML = '<pre><code class="language-rust">fn main() { println!("Hello"); }</code></pre>';
    document.body.appendChild(testContainer);
    
    // Try highlighting the test element
    try {
        var codeBlock = testContainer.querySelector('code');
        hljs.highlightElement(codeBlock);
        console.log('Test highlighting successful');
        console.log('Highlighted HTML:', codeBlock.innerHTML);
    } catch (e) {
        console.error('Test highlighting failed:', e);
    }
    
    // Check for diff containers
    var diffContainers = document.querySelectorAll('.diff-container');
    console.log('Found', diffContainers.length, 'diff containers');
    
    // Manually try to highlight diff containers after a delay
    setTimeout(function() {
        document.querySelectorAll('.d2h-code-line-ctn').forEach(function(block, index) {
            console.log('Highlighting diff block', index);
            try {
                hljs.highlightElement(block);
                console.log('Success highlighting diff block', index);
            } catch (e) {
                console.error('Error highlighting diff block', index, e);
            }
        });
        
        // Look for specific language tokens after highlighting
        var keywords = document.querySelectorAll('.hljs-keyword, .token.keyword');
        var comments = document.querySelectorAll('.hljs-comment, .token.comment');
        console.log('Found', keywords.length, 'keywords and', comments.length, 'comments after highlighting');
    }, 2000);
});
*/ 