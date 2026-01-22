"""MkDocs plugin for aggregating editor notes."""

import hashlib
import re
from pathlib import Path
from typing import Any

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page

from mkdocs_editor_notes.markdown_extension import EditorNotesExtension
from mkdocs_editor_notes.models import EditorNote


# Fixed note types with default emojis
FIXED_NOTE_TYPES = {
    'todo': '✅',
    'ponder': '⏳',
    'improve': '🛠️',
    'research': '🔍',
}

# Default emoji for custom note types
DEFAULT_CUSTOM_EMOJI = '❗'


class EditorNotesPluginConfig(Config):
    """Configuration for the EditorNotes plugin."""

    show_markers = config_options.Type(bool, default=False)
    note_type_emojis = config_options.Type(dict, default={})
    aggregator_page = config_options.Type(str, default='editor-notes.md')


class EditorNotesPlugin(BasePlugin[EditorNotesPluginConfig]):
    """MkDocs plugin to aggregate editor notes from documentation."""

    def __init__(self) -> None:
        super().__init__()
        self.notes: list[EditorNote] = []
        self.paragraph_counter = 0
        self.note_type_emojis: dict[str, str] = {}

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Setup configuration and emoji mappings."""
        # Build complete emoji map (defaults + user overrides)
        self.note_type_emojis = FIXED_NOTE_TYPES.copy()
        self.note_type_emojis.update(self.config.get('note_type_emojis', {}))
        
        # Create placeholder aggregator file if it doesn't exist
        if 'docs_dir' in config:
            docs_dir = Path(config['docs_dir'])
            aggregator_file = docs_dir / self.config['aggregator_page']
            if not aggregator_file.exists():
                aggregator_file.write_text('# Editor Notes\n\nThis page will be generated during the build.\n')
        
        return config
    
    def _is_fixed_type(self, note_type: str) -> bool:
        """Check if note type is a fixed/built-in type."""
        return note_type in FIXED_NOTE_TYPES
    
    def _get_emoji(self, note_type: str) -> str:
        """Get emoji for a note type."""
        # Check if user has specified an emoji
        if note_type in self.note_type_emojis:
            return self.note_type_emojis[note_type]
        # Use default for custom types
        return DEFAULT_CUSTOM_EMOJI

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
        """Process markdown to extract editor notes."""
        import re
        
        # Pattern for note definitions
        note_def_pattern = re.compile(r'^\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]:\s+(.+)$', re.MULTILINE)
        
        # Pattern for note references
        note_ref_pattern = re.compile(r'\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]')
        
        # Store mapping of note refs to paragraph IDs
        note_to_paragraph = {}
        
        # Protect code blocks by temporarily replacing them
        code_block_pattern = re.compile(r'(```[\s\S]*?```|~~~[\s\S]*?~~~)', re.MULTILINE)
        code_blocks = []
        
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"<<<CODE_BLOCK_{len(code_blocks)-1}>>>"
        
        markdown_protected = code_block_pattern.sub(save_code_block, markdown)
        
        # Find all note definitions and extract them
        for match in note_def_pattern.finditer(markdown_protected):
            note_type = match.group(1)
            note_label = match.group(2)
            note_text = match.group(3)
            
            # Create a key for this note
            note_key = f"{note_type}:{note_label}" if note_label else note_type
            
            # Create EditorNote object (we'll set paragraph_id later)
            note = EditorNote(
                note_type=note_type,
                label=note_label,
                text=note_text,
                source_page=page.file.src_uri,
                paragraph_id="",  # Will be set below
            )
            
            note_to_paragraph[note_key] = note
        
        # Process line by line to find note references and add anchors
        lines = markdown_protected.split('\n')
        processed_lines = []
        
        for line in lines:
            # Skip note definition lines (they'll be removed later)
            if note_def_pattern.match(line):
                processed_lines.append(line)
                continue
            
            # Check if this line has a note reference
            ref_match = note_ref_pattern.search(line)
            if ref_match:
                note_type = ref_match.group(1)
                note_label = ref_match.group(2)
                note_key = f"{note_type}:{note_label}" if note_label else note_type
                
                # Generate paragraph ID for this note
                self.paragraph_counter += 1
                paragraph_id = f"editor-note-para-{self.paragraph_counter}"
                
                # Set the paragraph ID and line number for the note
                if note_key in note_to_paragraph:
                    note_to_paragraph[note_key].paragraph_id = paragraph_id
                    # Store line number (approximate, based on position in file)
                    note_to_paragraph[note_key].line_number = len(processed_lines) + 1
                
                # Add anchor span at the start of the line
                if '<span id=' not in line:
                    line = f'<span id="{paragraph_id}"></span>{line}'
            
            processed_lines.append(line)
        
        markdown = '\n'.join(processed_lines)
        
        # Add notes to collection
        for note in note_to_paragraph.values():
            if note.paragraph_id:  # Only add if we found a reference
                self.notes.append(note)
        
        # Always remove note definitions from markdown (including the newline)
        markdown = note_def_pattern.sub('', markdown)
        # Clean up any double newlines left behind
        markdown = re.sub(r'\n\n\n+', '\n\n', markdown)
        
        # Remove note references if show_markers is False
        if not self.config['show_markers']:
            markdown = note_ref_pattern.sub('', markdown)
        else:
            # Replace with clickable markers linking to aggregator
            def replace_ref(match):
                note_type = match.group(1)
                note_label = match.group(2)
                note_key = f"{note_type}:{note_label}" if note_label else note_type
                
                # Generate a unique ID for this note for linking to aggregator
                if note_key in note_to_paragraph and note_to_paragraph[note_key].paragraph_id:
                    note_id = f"note-{note_to_paragraph[note_key].paragraph_id}"
                    paragraph_id = note_to_paragraph[note_key].paragraph_id
                    # Use matching emoji for this note type
                    marker_symbol = self._get_emoji(note_type)
                    # Create hover text with type and label
                    hover_text = f"{note_type}"
                    if note_label:
                        hover_text += f": {note_label}"
                    # Link to aggregator page using markdown format
                    aggregator_path = self.config.get('aggregator_page', 'editor-notes.md')
                    # Use markdown link format which MkDocs will handle correctly
                    return f'<sup class="editor-note-marker"><a href="{aggregator_path}#{note_id}" title="{hover_text}">{marker_symbol}</a></sup>'
                return ''
            markdown = note_ref_pattern.sub(replace_ref, markdown)
        
        # Restore code blocks
        for i, code_block in enumerate(code_blocks):
            markdown = markdown.replace(f"<<<CODE_BLOCK_{i}>>>", code_block)
        
        return markdown

    def on_env(self, env, config: MkDocsConfig, files: Files):
        """Write aggregator markdown file after pages are processed but before rendering."""
        # This runs after on_page_markdown for all pages, so we have all notes
        if self.notes:
            # Generate the aggregator page as markdown
            aggregator_md = self._generate_aggregator_markdown()
            
            # Write markdown file to docs directory
            docs_dir = Path(config['docs_dir'])
            aggregator_file = docs_dir / self.config['aggregator_page']
            aggregator_file.write_text(aggregator_md)
        
        return env

    def on_post_page(self, output: str, page, config: MkDocsConfig) -> str:
        """Inject CSS and fix marker links."""
        # Fix marker links to point to proper URLs (remove .md extension)
        aggregator_page = self.config.get('aggregator_page', 'editor-notes.md')
        aggregator_url = aggregator_page.replace('.md', '/')
        output = output.replace(f'href="{aggregator_page}#', f'href="{aggregator_url}#')
        
        # Add CSS for fast tooltips and paragraph highlighting
        css = """
<style>
/* Fast tooltip display */
.editor-note-marker a {
    position: relative;
}
.editor-note-marker a[title]:hover::after {
    content: attr(title);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 4px 8px;
    background: #333;
    color: white;
    font-size: 12px;
    white-space: nowrap;
    border-radius: 4px;
    z-index: 1000;
    margin-bottom: 4px;
    transition: none;
    animation: none;
}
/* Remove default tooltip */
.editor-note-marker a[title] {
    position: relative;
}
/* Highlight targeted paragraphs */
span[id^="editor-note-para"]:target {
    display: inline;
}
/* Highlight parent of targeted anchor */
span[id^="editor-note-para"]:target,
span[id^="note-editor-note-para"]:target {
    animation: none;
}
.editor-note-highlight {
    background-color: #fffde7;
    padding: 4px 8px;
    margin: -4px -8px;
    border-radius: 4px;
    transition: background-color 2s ease-out;
}
.editor-note-highlight-fade {
    background-color: transparent;
}
@keyframes highlight-fade {
    0% { background-color: #ffeb3b; }
    100% { background-color: transparent; }
}
</style>
<script>
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
        // Highlighting aggregator section
        // The structure is: <p><span id="..."></span></p> <h4>...</h4> <p>content</p>
        // Find the H4 that comes after the span's parent
        let current = target.parentElement.nextElementSibling;
        const elements = [];
        
        // Add the H4 itself
        if (current && current.matches('h4')) {
            elements.push(current);
            current = current.nextElementSibling;
        }
        
        // Add all content until the next H4, H3, or H2
        while (current && !current.matches('h2, h3, h4, p > span[id^="note-editor-note-para"]')) {
            // Skip empty paragraphs with just spans
            if (current.matches('p') && current.querySelector('span[id^="note-editor-note-para"]')) {
                break;
            }
            if (current.matches('p, ul, ol, pre, blockquote, div')) {
                elements.push(current);
            }
            current = current.nextElementSibling;
        }
        
        // Apply highlight to all elements in the section
        elements.forEach(el => {
            el.classList.add('editor-note-highlight');
            setTimeout(() => {
                el.classList.add('editor-note-highlight-fade');
            }, HIGHLIGHT_DURATION);
            setTimeout(() => {
                el.classList.remove('editor-note-highlight');
                el.classList.remove('editor-note-highlight-fade');
            }, HIGHLIGHT_DURATION + FADE_DURATION);
        });
        
        // Scroll to target
        if (elements.length > 0) {
            elements[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
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
</script>
"""
        # Inject before </head>
        if '</head>' in output:
            output = output.replace('</head>', f'{css}</head>')
        return output

    def on_post_build(self, config: MkDocsConfig) -> None:
        """Cleanup after build."""
        pass

    def _generate_aggregator_markdown(self) -> str:
        """Generate markdown content for the aggregator page."""
        # Group notes by type
        notes_by_type: dict[str, list[EditorNote]] = {}
        for note in self.notes:
            notes_by_type.setdefault(note.note_type, []).append(note)
        
        # Separate fixed and custom types
        fixed_types = [t for t in sorted(notes_by_type.keys()) if self._is_fixed_type(t)]
        custom_types = [t for t in sorted(notes_by_type.keys()) if not self._is_fixed_type(t)]
        
        # Build markdown content with front matter to configure TOC
        md_parts = [
            '---',
            'toc_depth: 2',
            '---',
            '',
            '# Editor Notes',
            '',
            'This page aggregates all editor notes found throughout the documentation.',
            '',
        ]
        
        # Add fixed note types first
        for note_type in fixed_types:
            notes = notes_by_type[note_type]
            emoji = self._get_emoji(note_type)
            md_parts.append(f'## {emoji} {note_type.capitalize()}')
            md_parts.append('')
            
            for note in notes:
                # Add anchor for linking from markers
                note_id = f"note-{note.paragraph_id}"
                
                # Format identifier as H4 with source link
                identifier = note.label if note.label else note_type
                source_file = note.source_page
                line_num = note.line_number or 0
                
                # MkDocs wants links to .md files, not rendered paths
                # Link to the specific paragraph anchor in the source file
                link_path = f"{source_file}#{note.paragraph_id}"
                
                # Format: #### identifier (source-file:line-number)
                # Don't hyperlink the identifier, only the file reference
                md_parts.append(f'<span id="{note_id}"></span>')
                md_parts.append(f'#### {identifier} ([{source_file}:{line_num}]({link_path}))')
                md_parts.append('')
                md_parts.append(note.text)
                md_parts.append('')
            
            md_parts.append('')
        
        # Add custom note types at the bottom
        if custom_types:
            md_parts.append('## Custom Notes')
            md_parts.append('')
            
            for note_type in custom_types:
                notes = notes_by_type[note_type]
                emoji = self._get_emoji(note_type)
                md_parts.append(f'### {emoji} {note_type}')
                md_parts.append('')
                
                for note in notes:
                    # Add anchor for linking from markers
                    note_id = f"note-{note.paragraph_id}"
                    
                    # Format identifier as H4 with source link
                    identifier = note.label if note.label else note_type
                    source_file = note.source_page
                    line_num = note.line_number or 0
                    
                    # Link to the specific paragraph anchor in the source file
                    link_path = f"{source_file}#{note.paragraph_id}"
                    
                    # Format: #### identifier (source-file:line-number)
                    # Don't hyperlink the identifier, only the file reference
                    md_parts.append(f'<span id="{note_id}"></span>')
                    md_parts.append(f'#### {identifier} ([{source_file}:{line_num}]({link_path}))')
                    md_parts.append('')
                    md_parts.append(note.text)
                    md_parts.append('')
                
                md_parts.append('')
        
        return '\n'.join(md_parts)

    def _get_inline_css(self) -> str:
        """Get inline CSS for the aggregator page."""
        return """
.editor-note-item {
    margin: 15px 0;
    padding: 12px;
    border-left: 4px solid #2196F3;
    background: #f5f9ff;
    border-radius: 4px;
}
.editor-note-label {
    font-weight: 600;
    color: #1976D2;
    margin-bottom: 4px;
    font-size: 1.1em;
}
.editor-note-text {
    margin: 8px 0;
    line-height: 1.6;
}
.editor-note-source {
    font-size: 0.9em;
    color: #666;
    margin-top: 8px;
}
.editor-note-source a {
    color: #1976D2;
    text-decoration: none;
}
.editor-note-source a:hover {
    text-decoration: underline;
}
:target {
    background-color: #ffffcc !important;
    animation: highlight-fade 3s ease-out;
    padding: 8px;
    margin: -8px;
    border-radius: 4px;
}
@keyframes highlight-fade {
    from { background-color: #ffff99; }
    50% { background-color: #ffffcc; }
    to { background-color: transparent; }
}
.editor-note-marker {
    font-size: 0.75em;
    color: #1976D2;
    margin-left: 2px;
    padding: 2px 4px;
    background: #e3f2fd;
    border-radius: 3px;
}
"""

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML (simple implementation)."""
        import re
        
        html = markdown_text
        
        # Convert headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Convert paragraphs (simple)
        lines = html.split('\n')
        result = []
        in_div = False
        
        for line in lines:
            if '<div class="editor-note-item">' in line:
                in_div = True
                result.append(line)
            elif '</div>' in line and in_div:
                result.append(line)
                # Check if this closes the note item
                if line.strip() == '</div>':
                    in_div = False
            elif line.startswith('<'):
                result.append(line)
            elif line.strip() and not in_div:
                result.append(f'<p>{line}</p>')
            else:
                result.append(line)
        
        return '\n'.join(result)
