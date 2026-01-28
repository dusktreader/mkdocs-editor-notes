from pathlib import Path

from mkdocs_editor_notes.note import EditorNote


def test_note__properties():
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug in the code",
        source_page=Path("index.md"),
        source_url="",  # Empty URL for index page
        line_number=10,
    )

    assert note.note_type == "todo"
    assert note.label == "fix-bug"
    assert note.text == "Fix the bug in the code"
    assert note.source_page == Path("index.md")
    assert note.line_number == 10

    assert note.ref_id == "ref-todo-fix-bug"
    assert note.ref_url == "../#ref-todo-fix-bug"  # Relative path from aggregator
    assert note.agg_id == "agg-todo-fix-bug"
    assert note.hover_text == "todo: fix-bug"

    # Test with a non-index page
    note_with_url = EditorNote(
        note_type="ponder",
        label="question",
        text="Think about this",
        source_page=Path("features.md"),
        source_url="features/",
        line_number=20,
    )

    assert note_with_url.ref_url == "../features/#ref-ponder-question"
