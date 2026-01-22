"""Tests for the editor notes plugin."""

import pytest
import re

from mkdocs_editor_notes.constants import NOTE_DEF_PATTERN, NOTE_REF_PATTERN
from mkdocs_editor_notes.plugin import EditorNotesPlugin
from mkdocs_editor_notes.models import EditorNote


def test_editor_note_model():
    """Test EditorNote dataclass."""
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug in the code",
        source_page="index.md",
        paragraph_id="para-1",
    )
    
    assert note.note_type == "todo"
    assert note.label == "fix-bug"
    assert note.note_id == "todo-fix-bug"
    assert note.display_label == "fix-bug"


def test_editor_note_without_label():
    """Test EditorNote without label."""
    note = EditorNote(
        note_type="ponder",
        label=None,
        text="Think about this",
        source_page="index.md",
        paragraph_id="para-2",
    )
    
    assert note.label is None
    assert note.note_id == "ponder-para-2"
    assert note.display_label == "ponder"


def test_plugin_initialization():
    """Test plugin initializes correctly."""
    plugin = EditorNotesPlugin()
    
    assert plugin.notes == []
    assert plugin.paragraph_counter == 0


def test_plugin_config():
    """Test plugin configuration."""
    plugin = EditorNotesPlugin()
    plugin.load_config({
        'show_markers': True,
        'note_types': ['todo', 'ponder'],
        'enable_highlighting': False,
    })
    
    assert plugin.config['show_markers'] is True
    assert plugin.config['note_types'] == ['todo', 'ponder']
    assert plugin.config['enable_highlighting'] is False


def test_note_pattern_matching():
    """Test regex patterns for note extraction."""
    # Test definition pattern
    text1 = "[^todo:test-note]: This is a test note"
    match1 = NOTE_DEF_PATTERN.match(text1)
    assert match1
    assert match1.group('type') == "todo"
    assert match1.group('label') == "test-note"
    assert match1.group('text') == "This is a test note"
    
    text2 = "[^ponder]: Think about this"
    match2 = NOTE_DEF_PATTERN.match(text2)
    assert match2
    assert match2.group('type') == "ponder"
    assert match2.group('label') is None
    assert match2.group('text') == "Think about this"
    
    # Test reference pattern
    text3 = "Some text[^todo:label] more text"
    match3 = NOTE_REF_PATTERN.search(text3)
    assert match3
    assert match3.group('type') == "todo"
    assert match3.group('label') == "label"


def test_note_definition_removal():
    """Test that note definitions are removed from markdown."""
    markdown = """
Test paragraph.[^todo:test]

[^todo:test]: Test note
Another paragraph.
"""
    
    def_pattern = re.compile(r'^\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]:\s+(.+)$', re.MULTILINE)
    result = def_pattern.sub('', markdown)
    
    assert "[^todo:test]: Test note" not in result
    assert "Test paragraph" in result
    assert "Another paragraph" in result


def test_note_reference_removal():
    """Test that note references can be removed."""
    markdown = "Test paragraph.[^todo:test] More text."
    
    ref_pattern = re.compile(r'\[\^([a-z]+)(?::([a-z0-9\-_]+))?\]')
    result = ref_pattern.sub('', markdown)
    
    assert "[^todo:test]" not in result
    assert "Test paragraph" in result
    assert "More text" in result


def test_note_reference_replacement():
    """Test that note references can be replaced with HTML."""
    markdown = "Test paragraph.[^todo:test] More text."
    
    def replace_ref(match):
        note_type = match.group('type')
        note_label = match.group('label')
        label_text = f":{note_label}" if note_label else ""
        return f'<sup class="editor-note-marker editor-note-{note_type}">[{note_type}{label_text}]</sup>'
    
    result = NOTE_REF_PATTERN.sub(replace_ref, markdown)
    
    assert 'editor-note-marker' in result
    assert 'todo:test' in result


def test_aggregator_markdown_generation():
    """Test aggregator markdown generation."""
    plugin = EditorNotesPlugin()
    plugin.config = {'note_type_emojis': {}}
    plugin.on_config({})  # Initialize emojis
    
    # Add some test notes
    plugin.notes = [
        EditorNote("todo", "fix-bug", "Fix the bug", "index.md", "para-1"),
        EditorNote("ponder", "question", "Think about this", "features.md", "para-2"),
        EditorNote("todo", "improve", "Make it better", "index.md", "para-3"),
    ]
    
    md = plugin._generate_aggregator_markdown()
    
    assert "# Editor Notes" in md
    assert "## ✅ Todo" in md  # Check for section header
    assert "## ⏳ Ponder" in md
    assert "fix-bug" in md
    assert "question" in md
    assert "Fix the bug" in md
    assert "Think about this" in md

