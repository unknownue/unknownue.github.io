// WASM viewer initialization and management with lazy loading

// Setup function to prepare lazy loading
function setupWasmViewer(idValue, wasmPath) {
    var containerId = "wasm-container-" + idValue;
    var container = document.getElementById(containerId);
    
    if (!container) {
        console.error("WASM container not found:", containerId);
        return;
    }

    // Add click event listener for lazy loading
    container.addEventListener('click', function() {
        if (container.dataset.loaded === 'true') {
            return; // Already loaded
        }
        
        container.dataset.loaded = 'true';
        loadWasmModule(idValue, wasmPath);
    });
}

// Load WASM module when requested
function loadWasmModule(idValue, wasmPath) {
    var containerId = "wasm-container-" + idValue;
    var container = document.getElementById(containerId);
    
    if (!container) {
        console.error("WASM container not found:", containerId);
        return;
    }

    // Show loading state
    var placeholder = container.querySelector('.wasm-placeholder');
    var loading = container.querySelector('.wasm-loading');
    
    if (placeholder) placeholder.style.display = 'none';
    if (loading) loading.style.display = 'block';

    // Initialize WASM viewer
    initWasmViewer(idValue, wasmPath, function(success) {
        if (loading) loading.style.display = 'none';
        
        if (!success) {
            // Show error state
            container.innerHTML = '<div class="wasm-error"><p>Failed to load WebAssembly demo</p></div>';
        }
    });
}

// Original WASM viewer initialization function (modified to support callback)
function initWasmViewer(idValue, wasmPath, callback) {
    callback = callback || function() {};
    
    // Check if document.body exists
    if (!document.body) {
        console.error("document.body is null, cannot initialize WASM viewer");
        callback(false);
        return;
    }

    // Setup container ID
    var containerId = "wasm-container-" + idValue;
    var container = document.getElementById(containerId);

    if (!container) {
        console.error("WASM container not found:", containerId);
        callback(false);
        return;
    }

    // Intercept appendChild calls to redirect canvas to our container
    var originalAppendChild = document.body.appendChild;
    document.body.appendChild = function(element) {
        if (element.tagName === 'CANVAS') {
            // Clear container content before adding new canvas
            container.innerHTML = '';
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
        // Check if document.body exists
        if (!document.body) {
            console.error("document.body is null, cannot load WASM");
            callback(false);
            return;
        }

        try {
            var script = document.createElement('script');
            script.type = 'module';
            
            // Determine correct path based on URL
            var basePath = window.location.pathname.includes('/content/') ? '../' : './';
            var wasmImportPath = basePath + wasmPath;
            
            script.textContent = 
                "import init from '" + wasmImportPath + "';\n" +
                "init().then(() => {\n" +
                "    console.log('WASM module loaded successfully');\n" +
                "}).catch((error) => {\n" +
                "    console.error('Failed to load WASM module:', error);\n" +
                "});\n";
            
            script.onload = function() {
                callback(true);
            };
            
            script.onerror = function() {
                console.error('Failed to load WASM script');
                callback(false);
            };
            
            document.body.appendChild(script);
        } catch (error) {
            console.error('Error loading WASM:', error);
            callback(false);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadWasm);
    } else {
        loadWasm();
    }
} 