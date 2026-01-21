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


class EditorNotesPluginConfig(Config):
    """Configuration for the EditorNotes plugin."""

    show_markers = config_options.Type(bool, default=False)
    note_types = config_options.Type(list, default=['todo', 'ponder', 'improve', 'research'])
    aggregator_page = config_options.Type(str, default='editor-notes.md')
    enable_highlighting = config_options.Type(bool, default=True)


class EditorNotesPlugin(BasePlugin[EditorNotesPluginConfig]):
    """MkDocs plugin to aggregate editor notes from documentation."""

    def __init__(self) -> None:
        super().__init__()
        self.notes: list[EditorNote] = []
        self.paragraph_counter = 0
        self.aggregator_file_added = False

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """Add the aggregator page to the files collection."""
        # We'll generate the content later in on_post_page
        # For now, just mark that we want to create it
        return files

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Add the markdown extension to the config."""
        # Don't manually add the extension - let users do this or use on_page_markdown
        return config

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
            # Replace with styled markers
            def replace_ref(match):
                note_type = match.group(1)
                note_label = match.group(2)
                label_text = f":{note_label}" if note_label else ""
                return f'<sup class="editor-note-marker editor-note-{note_type}">[{note_type}{label_text}]</sup>'
            markdown = note_ref_pattern.sub(replace_ref, markdown)
        
        return markdown

    def on_post_build(self, config: MkDocsConfig) -> None:
        """Generate the aggregator page markdown file."""
        if not self.notes:
            return
        
        # Generate the aggregator page as markdown
        aggregator_md = self._generate_aggregator_markdown()
        
        # Write the markdown file to site directory as HTML (manually rendered)
        site_dir = Path(config['site_dir'])
        aggregator_html_file = site_dir / self.config['aggregator_page'].replace('.md', '/index.html')
        aggregator_html_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Wrap in basic HTML template (will be themed on next build if added to nav)
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editor Notes - {config['site_name']}</title>
    <link rel="stylesheet" href="../assets/stylesheets/main.css">
    <style>
{self._get_inline_css()}
    </style>
</head>
<body>
<div class="md-content" data-md-component="content">
<article class="md-content__inner md-typeset">
{self._markdown_to_html(aggregator_md)}
</article>
</div>
</body>
</html>"""
        
        aggregator_html_file.write_text(html_content)

    def _generate_aggregator_markdown(self) -> str:
        """Generate markdown content for the aggregator page."""
        # Group notes by type
        notes_by_type: dict[str, list[EditorNote]] = {}
        for note in self.notes:
            notes_by_type.setdefault(note.note_type, []).append(note)
        
        # Build markdown content
        md_parts = [
            '# Editor Notes',
            '',
            'This page aggregates all editor notes found throughout the documentation.',
            '',
        ]
        
        # Add notes grouped by type
        for note_type in sorted(notes_by_type.keys()):
            notes = notes_by_type[note_type]
            md_parts.append(f'## {note_type.capitalize()} ({len(notes)})')
            md_parts.append('')
            
            for note in notes:
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
