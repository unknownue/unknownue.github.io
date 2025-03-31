// WASM viewer initialization and management
function initWasmViewer(idValue, wasmPath) {
    // Setup container ID
    var containerId = "wasm-container-" + idValue;
    var container = document.getElementById(containerId);

    // Intercept appendChild calls to redirect canvas to our container
    var originalAppendChild = document.body.appendChild;
    document.body.appendChild = function(element) {
        if (element.tagName === 'CANVAS') {
            // Clear container before adding new canvas
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
            return container.appendChild(element);
        }
        return originalAppendChild.call(this, element);
    };

    // Override fetch to redirect asset requests
    var originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && url.startsWith('assets/')) {
            var newUrl = '/assets/' + url.substring(7);
            console.log('Redirecting asset request from', url, 'to', newUrl);
            return originalFetch(newUrl, options);
        }
        return originalFetch(url, options);
    };

    // Load WASM module
    function loadWasm() {
        var script = document.createElement('script');
        script.type = 'module';
        
        // Determine correct path based on URL
        var basePath = window.location.pathname.includes('/content/') ? '../' : './';
        var wasmImportPath = basePath + wasmPath;
        
        script.textContent = 
            "import init from '" + wasmImportPath + "';\n" +
            "init();\n";
        document.body.appendChild(script);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadWasm);
    } else {
        loadWasm();
    }
} 