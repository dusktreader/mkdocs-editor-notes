from pathlib import Path

import snick

from mkdocs_editor_notes.constants import NOTE_DEF_PATTERN, NOTE_REF_PATTERN
from mkdocs_editor_notes.plugin import EditorNotesPlugin
from mkdocs_editor_notes.models import EditorNote


def test_editor_note_model():
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug in the code",
        source_page=Path("index.md"),
        ref_id="para-1",
    )

    assert note.note_type == "todo"
    assert note.label == "fix-bug"
    assert note.note_id == "todo-fix-bug"



def test_plugin_initialization():
    plugin = EditorNotesPlugin()

    assert plugin.notes == []


def test_plugin_config():
    plugin = EditorNotesPlugin()
    plugin.load_config(
        dict(
            show_markers=True,
            aggregator_page="jawa/ewok.md",
            note_type_emojis=dict(
                jawa="🥷",
                ewok="🐻",
            ),
        )
    )

    assert plugin.config.show_markers is True
    assert plugin.config.aggregator_page == "jawa/ewok.md"
    assert plugin.config.note_type_emojis == dict(
        jawa="🥷",
        ewok="🐻",
    )


def test_note_pattern_matching__single_line():
    text = "[^todo:test-note]: This is a test note"
    match = NOTE_DEF_PATTERN.match(text)
    assert match
    assert match.group("type") == "todo"
    assert match.group("label") == "test-note"
    assert match.group("text").strip() == "This is a test note"


def test_note_pattern_matching__skip_unlabeled_notes():
    text = "[^ponder]: Think about this"
    match = NOTE_DEF_PATTERN.match(text)
    assert match is None


def test_note_pattern_matching__multiline_note_definition():
    text = snick.dedent(
        """
        [^improve:multiline]:
        This is line one.
        This is line two.
        This is line three.

        This should not be captured.
        """
    )
    match = NOTE_DEF_PATTERN.search(text)
    assert match
    assert match.group("type") == "improve"
    assert match.group("label") == "multiline"
    text = match.group("text").strip()
    assert text == snick.dedent(
        """
        This is line one.
        This is line two.
        This is line three.
        """
    )


def test_note_pattern_matching__reference_pattern():
    text = "Some text[^todo:label] more text"
    match = NOTE_REF_PATTERN.search(text)
    assert match
    assert match.group("type") == "todo"
    assert match.group("label") == "label"

def test_note_pattern_matching__skip_unlabeled_references():
    text = "Some text[^todo] more text"
    match = NOTE_REF_PATTERN.search(text)
    assert match is None


def test_aggregator_markdown_generation(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    plugin = EditorNotesPlugin()
    plugin.load_config(
        dict(
            docs_dir=str(docs_dir),
            show_markers=True,
            aggregator_page="jawa/ewok.md",
            note_type_emojis=dict(
                jawa="🥷",
                ewok="🐻",
            ),
        )
    )

    plugin.notes = [
        EditorNote(
            note_type="todo",
            label="fix-bug",
            text="Fix the bug",
            source_page=Path("index.md"),
            ref_id="para-1",
        ),
        EditorNote(
            note_type="ponder",
            label="question",
            text="Think about this",
            source_page=Path("features.md"),
            ref_id="para-2"
        ),
        EditorNote(
            note_type="todo",
            label="improve",
            text="Make it better",
            source_page=Path("index.md"),
            ref_id="para-3"
        ),
    ]

    plugin.build_aggregator_markdown()

    assert plugin.aggregator_path.read_text() == snick.dedent(
        """
        We want to test against the actual doc, muthafucka!
        """
    )
    # assert "# Editor Notes" in md
    # assert "## ✅ Todo" in md  # Check for section header
    # assert "## ⏳ Ponder" in md
    # assert "fix-bug" in md
    # assert "question" in md
    # assert "Fix the bug" in md
    # assert "Think about this" in md
