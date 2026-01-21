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
    'ponder': '💭',
    'improve': '⚡',
    'research': '🔍',
}

# Default emoji for custom note types
DEFAULT_CUSTOM_EMOJI = '❗'


class EditorNotesPluginConfig(Config):
    """Configuration for the EditorNotes plugin."""

    show_markers = config_options.Type(bool, default=False)
    marker_symbol = config_options.Type(str, default='🔍')
    note_type_emojis = config_options.Type(dict, default={})
    aggregator_page = config_options.Type(str, default='editor-notes.md')
    enable_highlighting = config_options.Type(bool, default=True)


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
        
        # Find all note definitions and extract them
        for match in note_def_pattern.finditer(markdown):
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
        lines = markdown.split('\n')
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
                
                # Generate paragraph ID
                self.paragraph_counter += 1
                paragraph_id = f"editor-note-para-{self.paragraph_counter}"
                
                # Set the paragraph ID for the note
                if note_key in note_to_paragraph:
                    note_to_paragraph[note_key].paragraph_id = paragraph_id
                
                # Add anchor to line if highlighting is enabled
                if self.config['enable_highlighting'] and '<span id=' not in line:
                    line = f'<span id="{paragraph_id}"></span>' + line
            
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
                    # Create clickable marker with link to aggregator
                    marker_symbol = self.config.get('marker_symbol', '🔍')
                    aggregator_path = self.config.get('aggregator_page', 'editor-notes.md').replace('.md', '/')
                    return f'<sup class="editor-note-marker"><a href="/{aggregator_path}#{note_id}" title="{note_type}: {note_label or ""}">{marker_symbol}</a></sup>'
                return ''
            markdown = note_ref_pattern.sub(replace_ref, markdown)
        
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
        
        # Build markdown content
        md_parts = [
            '# Editor Notes',
            '',
            'This page aggregates all editor notes found throughout the documentation.',
            '',
        ]
        
        # Add fixed note types first
        for note_type in fixed_types:
            notes = notes_by_type[note_type]
            emoji = self._get_emoji(note_type)
            md_parts.append(f'## {emoji} {note_type.capitalize()} ({len(notes)})')
            md_parts.append('')
            
            for note in notes:
                # Add anchor for linking from markers
                note_id = f"note-{note.paragraph_id}"
                md_parts.append(f'<span id="{note_id}"></span>')
                md_parts.append('<div class="editor-note-item">')
                
                if note.label:
                    md_parts.append(f'<div class="editor-note-label">{note.label}</div>')
                
                md_parts.append(f'<div class="editor-note-text">{note.text}</div>')
                
                # Add link back to source
                source_path = note.source_page
                if source_path.endswith('.md'):
                    source_path = source_path[:-3] + '.html'
                # Handle directory-style URLs (mkdocs default)
                if source_path.endswith('.html'):
                    if source_path == 'index.html':
                        source_link = f'../'
                    else:
                        source_link = f'../{source_path[:-5]}/'  # Remove .html, add /
                else:
                    source_link = f'../{source_path}'
                
                source_link += f'#{note.paragraph_id}'
                
                md_parts.append(
                    f'<div class="editor-note-source">Source: <a href="{source_link}">{note.source_page}</a></div>'
                )
                md_parts.append('</div>')
                md_parts.append('')
            
            md_parts.append('')
        
        # Add custom note types at the bottom
        if custom_types:
            md_parts.append('## Custom Notes')
            md_parts.append('')
            
            for note_type in custom_types:
                notes = notes_by_type[note_type]
                emoji = self._get_emoji(note_type)
                md_parts.append(f'### {emoji} {note_type} ({len(notes)})')
                md_parts.append('')
                
                for note in notes:
                    # Add anchor for linking from markers
                    note_id = f"note-{note.paragraph_id}"
                    md_parts.append(f'<span id="{note_id}"></span>')
                    md_parts.append('<div class="editor-note-item">')
                    
                    if note.label:
                        md_parts.append(f'<div class="editor-note-label">{note.label}</div>')
                    
                    md_parts.append(f'<div class="editor-note-text">{note.text}</div>')
                    
                    # Add link back to source
                    source_path = note.source_page
                    if source_path.endswith('.md'):
                        source_path = source_path[:-3] + '.html'
                    if source_path.endswith('.html'):
                        if source_path == 'index.html':
                            source_link = f'../'
                        else:
                            source_link = f'../{source_path[:-5]}/'
                    else:
                        source_link = f'../{source_path}'
                    
                    source_link += f'#{note.paragraph_id}'
                    
                    md_parts.append(
                        f'<div class="editor-note-source">Source: <a href="{source_link}">{note.source_page}</a></div>'
                    )
                    md_parts.append('</div>')
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
