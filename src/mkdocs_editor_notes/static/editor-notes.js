function clearAllHighlights() {
    document.querySelectorAll('.editor-note-highlight').forEach(el => {
        el.classList.remove('editor-note-highlight');
        el.classList.remove('editor-note-highlight-fade');
    });
}

function highlightTarget() {
    clearAllHighlights();

    const hash = window.location.hash;
    if (!hash) return;

    const target = document.querySelector(hash);
    if (!target) {
        console.warn(`[editor-notes] Target element not found for hash: ${hash}`);
        return;
    }

    let elementToHighlight = null;

    const config = window.EDITOR_NOTES_CONFIG || {};
    const HIGHLIGHT_DURATION = config.highlightDuration || 3000; // Stay at full color for 3 seconds
    const FADE_DURATION = config.highlightFadeDuration || 2000; // Fade for 2 seconds

    if (target.id.startsWith('ref-')) {
        elementToHighlight = target.parentElement;
    } else if (target.id.startsWith('agg-')) {
        elementToHighlight = target.closest('.editor-note-entry');
    } else {
        console.warn(`[editor-notes] Unrecognized target ID format: ${target.id} (expected 'ref-*' or 'agg-*')`);
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
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

window.addEventListener('load', highlightTarget);
window.addEventListener('hashchange', highlightTarget);
