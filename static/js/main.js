mmdElements = document.getElementsByClassName("mermaid");
const mmdHTML = [];
for (let i = 0; i < mmdElements.length; i++) {
	mmdHTML[i] = mmdElements[i].innerHTML;
}

function mermaidRender(theme) {
	if (theme == "dark") {
		initOptions = {
			startOnLoad: false,
			theme: "dark",
		};
	} else {
		initOptions = {
			startOnLoad: false,
			theme: "neutral",
		};
	}
	for (let i = 0; i < mmdElements.length; i++) {
		delete mmdElements[i].dataset.processed;
		mmdElements[i].innerHTML = mmdHTML[i];
	}
	mermaid.initialize(initOptions);
	mermaid.run();
}

document.addEventListener('DOMContentLoaded', function() {
	// Initialize Mermaid diagrams if they exist
	if (typeof mermaid !== 'undefined') {
		mermaid.initialize({
			startOnLoad: true,
			theme: document.body.classList.contains('dark') ? 'dark' : 'default',
			securityLevel: 'loose',
			flowchart: {
				useMaxWidth: true,
				htmlLabels: true
			}
		});
		
		// Convert Mermaid code blocks to diagrams
		convertMermaidCodeBlocks();
	}

	// Process emojis
	processEmojis();

	// Process superscript and subscript
	processSuperSubScript();
});

// Function to convert Mermaid code blocks to diagrams
function convertMermaidCodeBlocks() {
    // Find all code blocks with language 'mermaid'
    const codeBlocks = document.querySelectorAll('pre > code.language-mermaid');
    
    if (codeBlocks.length > 0) {
        codeBlocks.forEach(codeBlock => {
            // Get the parent pre element
            const preElement = codeBlock.parentElement;
            
            // Get the Mermaid diagram code
            const mermaidCode = codeBlock.textContent.trim();
            
            // Create a new div with class 'mermaid'
            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = mermaidCode;
            
            // Replace the pre element with the mermaid div
            if (preElement.parentElement) {
                preElement.parentElement.replaceChild(mermaidDiv, preElement);
            }
        });
        
        // Re-run Mermaid to render the new diagrams
        try {
            mermaid.contentLoaded();
        } catch (error) {
            console.error('Error rendering Mermaid diagrams:', error);
        }
    }
}

// Function to process emojis in text
function processEmojis() {
	// Replace emoji shortcodes with actual emojis
	const emojiMap = {
		':smile:': '😊',
		':heart:': '❤️',
		':thumbsup:': '👍',
		':rocket:': '🚀',
		':star:': '⭐',
		':fire:': '🔥',
		':warning:': '⚠️',
		':bulb:': '💡',
		':book:': '📚',
		':computer:': '💻',
		':check:': '✅',
		':x:': '❌'
	};

	// Find all text nodes in the document
	const walker = document.createTreeWalker(
		document.body,
		NodeFilter.SHOW_TEXT,
		null,
		false
	);

	const nodesToProcess = [];
	let node;
	while (node = walker.nextNode()) {
		// Skip script and style tags
		if (node.parentNode.tagName === 'SCRIPT' || node.parentNode.tagName === 'STYLE') {
			continue;
		}
		nodesToProcess.push(node);
	}

	// Process each text node
	nodesToProcess.forEach(textNode => {
		let content = textNode.nodeValue;
		let changed = false;

		// Replace emoji codes
		for (const [code, emoji] of Object.entries(emojiMap)) {
			if (content.includes(code)) {
				content = content.replace(new RegExp(code, 'g'), emoji);
				changed = true;
			}
		}

		if (changed) {
			textNode.nodeValue = content;
		}
	});
}

// Function to process superscript and subscript
function processSuperSubScript() {
	// Process superscript (x^2^)
	document.querySelectorAll('p, li').forEach(element => {
		const html = element.innerHTML;
		if (html.includes('^')) {
			element.innerHTML = html.replace(/(\S+)\^(\S+)\^/g, '<sup>$1$2</sup>');
		}
	});

	// Process subscript (H~2~O)
	document.querySelectorAll('p, li').forEach(element => {
		const html = element.innerHTML;
		if (html.includes('~')) {
			element.innerHTML = html.replace(/(\S+)~(\S+)~/g, '<sub>$1$2</sub>');
		}
	});
}
