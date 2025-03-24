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

// Apply colors to all labels
document.addEventListener('DOMContentLoaded', function() {
    const labels = document.querySelectorAll('.pr-label');
    labels.forEach(label => {
        const labelText = label.getAttribute('data-label');
        const colorIndex = hashString(labelText) % labelColors.length;
        label.style.backgroundColor = labelColors[colorIndex];
    });
}); 