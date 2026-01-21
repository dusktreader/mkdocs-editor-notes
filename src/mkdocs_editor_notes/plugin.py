"""MkDocs plugin for aggregating editor notes."""

import hashlib
import re
from pathlib import Path
from typing import Any

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
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

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Add the markdown extension to the config."""
        # Don't manually add the extension - let users do this or use on_page_markdown
        return config

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
        """Process markdown to extract editor notes."""
        # Extract notes using regex directly on the markdown source
        import re
        
        # Pattern for note definitions
        note_def_pattern = re.compile(r'^\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]:\s+(.+)$', re.MULTILINE)
        
        # Find all note definitions
        for match in note_def_pattern.finditer(markdown):
            note_type = match.group(1)
            note_label = match.group(2)
            note_text = match.group(3)
            
            # Generate a unique paragraph ID
            self.paragraph_counter += 1
            paragraph_id = f"editor-note-para-{self.paragraph_counter}"
            
            # Create EditorNote object
            note = EditorNote(
                note_type=note_type,
                label=note_label,
                text=note_text,
                source_page=page.file.src_uri,
                paragraph_id=paragraph_id,
            )
            
            self.notes.append(note)
        
        # Remove note definitions from markdown if show_markers is False
        if not self.config['show_markers']:
            markdown = note_def_pattern.sub('', markdown)
        
        # Add paragraph IDs for highlighting support
        if self.config['enable_highlighting']:
            markdown = self._add_paragraph_anchors(markdown)
        
        return markdown

    def _add_paragraph_anchors(self, markdown: str) -> str:
        """Add anchor IDs to paragraphs containing editor notes."""
        # Find lines with editor note references
        lines = markdown.split('\n')
        result = []
        
        for line in lines:
            # Check if line contains an editor note reference
            if re.search(r'\[\^[a-z]+(?::[a-z0-9\-_]+)?\]', line):
                # Add an anchor span if not already present
                if '<span id=' not in line:
                    self.paragraph_counter += 1
                    anchor_id = f"editor-note-para-{self.paragraph_counter}"
                    # Prepend anchor to the line
                    line = f'<span id="{anchor_id}"></span>{line}'
            result.append(line)
        
        return '\n'.join(result)

    def on_post_build(self, config: MkDocsConfig) -> None:
        """Generate the aggregator page after the build."""
        if not self.notes:
            return
        
        # Generate the aggregator page content
        aggregator_content = self._generate_aggregator_page()
        
        # Write the aggregator page
        site_dir = Path(config['site_dir'])
        aggregator_file = site_dir / self.config['aggregator_page'].replace('.md', '.html')
        aggregator_file.parent.mkdir(parents=True, exist_ok=True)
        
        # For now, write as HTML (we'll improve this later)
        aggregator_file.write_text(aggregator_content)

    def _generate_aggregator_page(self) -> str:
        """Generate the content for the aggregator page."""
        # Group notes by type
        notes_by_type: dict[str, list[EditorNote]] = {}
        for note in self.notes:
            notes_by_type.setdefault(note.note_type, []).append(note)
        
        # Build HTML content
        html_parts = [
            '<html>',
            '<head>',
            '<title>Editor Notes</title>',
            '<style>',
            '.editor-notes { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }',
            '.note-section { margin: 30px 0; }',
            '.note-type-header { font-size: 24px; font-weight: bold; margin-bottom: 15px; text-transform: capitalize; }',
            '.note-item { margin: 15px 0; padding: 10px; border-left: 3px solid #ccc; background: #f5f5f5; }',
            '.note-label { font-weight: bold; color: #333; }',
            '.note-text { margin: 5px 0; }',
            '.note-source { font-size: 12px; color: #666; margin-top: 5px; }',
            ':target { background-color: #ffffcc; animation: highlight 2s ease-out; }',
            '@keyframes highlight { from { background-color: #ffff99; } to { background-color: transparent; } }',
            '</style>',
            '</head>',
            '<body>',
            '<div class="editor-notes">',
            '<h1>Editor Notes</h1>',
        ]
        
        # Add notes grouped by type
        for note_type in sorted(notes_by_type.keys()):
            notes = notes_by_type[note_type]
            html_parts.append(f'<div class="note-section">')
            html_parts.append(f'<div class="note-type-header">{note_type} ({len(notes)})</div>')
            
            for note in notes:
                html_parts.append('<div class="note-item">')
                if note.label:
                    html_parts.append(f'<div class="note-label">{note.label}</div>')
                html_parts.append(f'<div class="note-text">{note.text}</div>')
                
                # Add link back to source
                # Convert .md to .html and handle directory URLs
                source_path = note.source_page
                if source_path.endswith('.md'):
                    source_path = source_path[:-3] + '.html'
                source_link = f'{source_path}#{note.paragraph_id}'
                html_parts.append(
                    f'<div class="note-source">Source: <a href="{source_link}">{note.source_page}</a></div>'
                )
                html_parts.append('</div>')
            
            html_parts.append('</div>')
        
        html_parts.extend(['</div>', '</body>', '</html>'])
        
        return '\n'.join(html_parts)
