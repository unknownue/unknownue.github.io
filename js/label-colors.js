// Color palette for label backgrounds
const labelColors = [
    "#0366d6", "#28a745", "#d73a49", "#6f42c1",
    "#e36209", "#f66a0a", "#ffb366", "#2ea44f",
    "#1b1f23", "#005cc5", "#032f62", "#d15704",
    "#b31d28", "#5a32a3", "#6a737d", "#cb2431",
    "#44b4a1", "#8b008b", "#008080", "#9acd32",
    "#ff6347", "#663399", "#4682b4", "#ff8c00",
    "#20b2aa", "#9370db", "#3cb371", "#cd5c5c",
    "#4169e1", "#008b8b", "#bc8f8f", "#ff4500",
    "#6b8e23", "#483d8b", "#191970", "#556b2f",
    "#7b68ee", "#800000", "#a0522d", "#8fbc8f"
];

// Simple hash function to generate consistent index for each label
function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
}

// Label filtering functionality
function setupLabelFiltering() {
    const labels = document.querySelectorAll('.pr-label.clickable');
    const prItems = document.querySelectorAll('.pr-item');
    const clearFiltersBtn = document.getElementById('clear-filters');
    
    // Exit early if required elements don't exist (not a PR page)
    if (!clearFiltersBtn || labels.length === 0 || prItems.length === 0) {
        console.log('Not a PR page or filtering elements not found, skipping label filtering setup');
        return;
    }
    
    const labelsContainer = document.querySelector('.pr-labels-list');
    
    // Track selected labels
    let selectedLabels = [];
    
    // Toggle label selection
    labels.forEach(label => {
        label.addEventListener('click', () => {
            const labelText = label.getAttribute('data-label');
            const isSelected = label.classList.toggle('selected');
            
            if (isSelected) {
                // Add to selected labels
                selectedLabels.push(labelText);
            } else {
                // Remove from selected labels
                selectedLabels = selectedLabels.filter(l => l !== labelText);
            }
            
            // Apply filtering
            applyFilters();
        });
    });
    
    // Clear all filters
    clearFiltersBtn.addEventListener('click', () => {
        selectedLabels = [];
        labels.forEach(label => label.classList.remove('selected'));
        resetAllFilters();
    });
    
    // Function to completely reset all filtering
    function resetAllFilters() {
        // Hide clear filters button
        clearFiltersBtn.style.display = 'none';
        
        // Remove filtering-active class
        labelsContainer.classList.remove('filtering-active');
        
        // Show all PR items
        prItems.forEach(item => {
            item.classList.remove('filtered');
        });
        
        // Show all date groups
        const dateGroups = document.querySelectorAll('.pr-date-group');
        dateGroups.forEach(group => {
            group.style.display = '';
        });
    }
    
    // Apply filtering based on selected labels
    function applyFilters() {
        // If no labels selected, reset all filters
        if (selectedLabels.length === 0) {
            resetAllFilters();
            return;
        }
        
        // Show clear filters button
        clearFiltersBtn.style.display = 'block';
        
        // Add filtering-active class
        labelsContainer.classList.add('filtering-active');
        
        // Filter PR items
        prItems.forEach(item => {
            const itemLabels = Array.from(item.querySelectorAll('.pr-label'))
                .map(label => label.getAttribute('data-label'));
            
            // Check if the item has at least one of the selected labels
            const hasSelectedLabel = selectedLabels.some(selectedLabel => 
                itemLabels.includes(selectedLabel)
            );
            
            if (hasSelectedLabel) {
                item.classList.remove('filtered');
            } else {
                item.classList.add('filtered');
            }
        });
        
        // Check if any date groups are now empty and hide them
        const dateGroups = document.querySelectorAll('.pr-date-group');
        dateGroups.forEach(group => {
            const visibleItems = group.querySelectorAll('.pr-item:not(.filtered)');
            if (visibleItems.length === 0) {
                group.style.display = 'none';
            } else {
                group.style.display = '';  // Use default display instead of 'block'
            }
        });
    }
}

// Initialize on document load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Label colors script loaded');
    
    // Apply colors to all labels
    const labels = document.querySelectorAll('.pr-label');
    console.log(`Found ${labels.length} labels to color`);
    
    labels.forEach(label => {
        const labelText = label.getAttribute('data-label');
        const colorIndex = hashString(labelText) % labelColors.length;
        label.style.backgroundColor = labelColors[colorIndex];
    });
    
    // Setup label filtering
    setupLabelFiltering();
    
    // Add debug click handler to clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        const originalClickHandler = clearFiltersBtn.onclick;
        clearFiltersBtn.addEventListener('click', function() {
            console.log('Clear filters button clicked');
            console.log('PR items before reset:', document.querySelectorAll('.pr-item:not(.filtered)').length);
            // Original handler will be called by the event propagation
            setTimeout(() => {
                console.log('PR items after reset:', document.querySelectorAll('.pr-item:not(.filtered)').length);
                console.log('Date groups visibility:', Array.from(document.querySelectorAll('.pr-date-group')).map(g => g.style.display));
            }, 10);
        });
    }
}); 