// Highlight paragraphs when navigating to anchors
function highlightTarget() {
    // Remove any existing highlights
    document.querySelectorAll('.editor-note-highlight').forEach(el => {
        el.classList.remove('editor-note-highlight');
        el.classList.remove('editor-note-highlight-fade');
    });
    
    const hash = window.location.hash;
    if (!hash) return;
    
    const target = document.querySelector(hash);
    if (!target) return;
    
    // Determine what to highlight based on the ID
    let elementToHighlight = null;
    const HIGHLIGHT_DURATION = 3000; // Stay at full color for 3 seconds
    const FADE_DURATION = 2000; // Fade for 2 seconds
    
    if (target.id.startsWith('editor-note-para')) {
        // Highlighting source paragraph - get parent element
        elementToHighlight = target.parentElement;
    } else if (target.id.startsWith('note-editor-note-para')) {
        // Highlighting aggregator entry - find the containing div
        elementToHighlight = target.closest('.editor-note-entry');
    }
    
    if (elementToHighlight) {
        elementToHighlight.classList.add('editor-note-highlight');
        setTimeout(() => {
            elementToHighlight.classList.add('editor-note-highlight-fade');
        }, HIGHLIGHT_DURATION);
        setTimeout(() => {
            elementToHighlight.classList.remove('editor-note-highlight');
            elementToHighlight.classList.remove('editor-note-highlight-fade');
        }, HIGHLIGHT_DURATION + FADE_DURATION);
        // Scroll to target
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Run on page load and hash change
window.addEventListener('load', highlightTarget);
window.addEventListener('hashchange', highlightTarget);
