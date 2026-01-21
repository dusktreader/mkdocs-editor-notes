"""Markdown extension for parsing editor notes."""

import re
from typing import Any
from xml.etree import ElementTree as etree

from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor


# Pattern for editor note reference: [^type:label] or [^type]
EDITOR_NOTE_REF_RE = r'\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]'

# Pattern for editor note definition: [^type:label]: note text or [^type]: note text
EDITOR_NOTE_DEF_RE = r'^\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]:\s+(.+)'


class EditorNoteInlineProcessor(InlineProcessor):
    """Process inline editor note references like [^todo:label]."""

    def __init__(self, pattern: str, md: Markdown, config: dict[str, Any]):
        super().__init__(pattern, md)
        self.config = config
        self.notes_found: list[tuple[str, str | None]] = []

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | None, int, int]:
        """Handle a matched editor note reference."""
        note_type = m.group(1)
        note_label = m.group(2) if m.group(2) else None
        
        # Store reference for later processing
        self.notes_found.append((note_type, note_label))
        
        # Create a marker element (can be hidden via CSS if configured)
        if self.config.get('show_markers', False):
            el = etree.Element('sup')
            el.set('class', f'editor-note-marker editor-note-{note_type}')
            el.text = f'[{note_type}{":" + note_label if note_label else ""}]'
            return el, m.start(0), m.end(0)
        else:
            # Return empty element that won't be rendered
            el = etree.Element('span')
            el.set('class', 'editor-note-invisible')
            return el, m.start(0), m.end(0)


class EditorNoteDefinitionProcessor(BlockProcessor):
    """Process editor note definitions like [^todo:label]: Note text."""

    def __init__(self, parser: Any, md: Markdown):
        super().__init__(parser)
        self.md = md
        self.pattern = re.compile(EDITOR_NOTE_DEF_RE)

    def test(self, parent: etree.Element, block: str) -> bool:
        """Test if block is an editor note definition."""
        return bool(self.pattern.match(block))

    def run(self, parent: etree.Element, blocks: list[str]) -> bool:
        """Process the editor note definition."""
        block = blocks.pop(0)
        m = self.pattern.match(block)
        
        if m:
            note_type = m.group(1)
            note_label = m.group(2) if m.group(2) else None
            note_text = m.group(3)
            
            # Store the note definition in the markdown instance
            if not hasattr(self.md, 'editor_notes'):
                self.md.editor_notes = []
            
            self.md.editor_notes.append({
                'type': note_type,
                'label': note_label,
                'text': note_text,
            })
            
            return True
        
        return False


class EditorNotesExtension(Extension):
    """Markdown extension for editor notes."""

    def __init__(self, **kwargs: Any):
        self.config = {
            'show_markers': [False, 'Show editor note markers in rendered output'],
            'note_types': [
                ['todo', 'ponder', 'improve', 'research'],
                'List of valid note types',
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        """Register the extension with markdown."""
        # Initialize storage for notes
        md.editor_notes = []
        
        # Register inline processor for note references
        inline_processor = EditorNoteInlineProcessor(
            EDITOR_NOTE_REF_RE, md, self.getConfigs()
        )
        md.inlinePatterns.register(inline_processor, 'editor_note_ref', 175)
        
        # Register block processor for note definitions
        definition_processor = EditorNoteDefinitionProcessor(md.parser, md)
        md.parser.blockprocessors.register(
            definition_processor, 'editor_note_def', 105
        )


def makeExtension(**kwargs: Any) -> EditorNotesExtension:
    """Create the extension."""
    return EditorNotesExtension(**kwargs)
