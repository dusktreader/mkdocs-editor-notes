from pathlib import Path
from unittest.mock import Mock

import pytest
from mkdocs.structure.pages import Page

from mkdocs_editor_notes.note import EditorNote
from mkdocs_editor_notes.manager import EditorNotesManager


def test_manager__init():
    manager = EditorNotesManager()
    assert manager.notes_map == {}
    assert manager.type_map == {}


def test_manager__key():
    key = EditorNotesManager.key("todo", "fix-bug")
    assert key == "todo:fix-bug"


def test_manager__add__single_note():
    manager = EditorNotesManager()
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug in the code",
        source_page=Path("index.md"),
        line_number=10,
    )

    manager.add(note)
    key = manager.key("todo", "fix-bug")

    assert manager.notes_map.get(key) == note
    assert manager.type_map.get("todo") == {key}


def test_manager__add__multiple_notes_same_type():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="todo",
        label="add-feature",
        text="Add new feature",
        source_page=Path("about.md"),
        line_number=20,
    )

    manager.add(note1)
    manager.add(note2)

    assert len(manager.notes_map) == 2
    assert "todo:fix-bug" in manager.notes_map
    assert "todo:add-feature" in manager.notes_map
    assert len(manager.type_map["todo"]) == 2


def test_manager__add__multiple_notes_different_types():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="note",
        label="important",
        text="Important note",
        source_page=Path("about.md"),
        line_number=20,
    )

    manager.add(note1)
    manager.add(note2)

    assert len(manager.notes_map) == 2
    assert len(manager.type_map) == 2
    assert "todo" in manager.type_map
    assert "note" in manager.type_map
    assert "todo:fix-bug" in manager.type_map["todo"]
    assert "note:important" in manager.type_map["note"]


def test_manager__add__raises_on_duplicate():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Original text",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Updated text",
        source_page=Path("about.md"),
        line_number=20,
    )

    manager.add(note1)

    with pytest.raises(ValueError, match=r"Note with key 'todo:fix-bug' already exists"):
        manager.add(note2)

    assert len(manager.notes_map) == 1
    assert manager.notes_map["todo:fix-bug"] == note1
    assert manager.notes_map["todo:fix-bug"].text == "Original text"


def test_manager__get__existing_note():
    manager = EditorNotesManager()
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    manager.add(note)
    assert manager.get("todo", "fix-bug") == note


def test_manager__get__nonexistent_note():
    manager = EditorNotesManager()
    assert manager.get("todo", "nonexistent") is None


def test_manager__get__multiple_notes():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="note",
        label="important",
        text="Important note",
        source_page=Path("about.md"),
        line_number=20,
    )

    manager.add(note1)
    manager.add(note2)

    assert manager.get("todo", "fix-bug") == note1
    assert manager.get("note", "important") == note2
    assert manager.get("todo", "important") is None
    assert manager.get("note", "fix-bug") is None


def test_manager__empty__when_initialized():
    manager = EditorNotesManager()
    assert manager.empty is True


def test_manager__empty__false_after_add():
    manager = EditorNotesManager()
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    manager.add(note)
    assert manager.empty is False


def test_manager__iter__empty():
    manager = EditorNotesManager()
    notes = list(manager)
    assert notes == []


def test_manager__iter__single_note():
    manager = EditorNotesManager()
    note = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    manager.add(note)

    notes = list(manager)
    assert len(notes) == 1
    assert notes[0] == note


def test_manager__iter__multiple_notes():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="note",
        label="important",
        text="Important note",
        source_page=Path("about.md"),
        line_number=20,
    )
    note3 = EditorNote(
        note_type="todo",
        label="add-feature",
        text="Add feature",
        source_page=Path("features.md"),
        line_number=30,
    )

    manager.add(note1)
    manager.add(note2)
    manager.add(note3)

    notes = list(manager)
    assert notes == [note1, note2, note3]


def test_manager__types__empty():
    manager = EditorNotesManager()
    types = list(manager.types)
    assert types == []


def test_manager__types__single_type():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="todo",
        label="add-feature",
        text="Add feature",
        source_page=Path("features.md"),
        line_number=20,
    )

    manager.add(note1)
    manager.add(note2)

    types = list(manager.types)
    assert len(types) == 1
    assert "todo" in types


def test_manager__types__multiple_types():
    manager = EditorNotesManager()
    note1 = EditorNote(
        note_type="todo",
        label="fix-bug",
        text="Fix the bug",
        source_page=Path("index.md"),
        line_number=10,
    )
    note2 = EditorNote(
        note_type="note",
        label="important",
        text="Important note",
        source_page=Path("about.md"),
        line_number=20,
    )
    note3 = EditorNote(
        note_type="warning",
        label="deprecated",
        text="This is deprecated",
        source_page=Path("api.md"),
        line_number=30,
    )

    manager.add(note1)
    manager.add(note2)
    manager.add(note3)

    types = list(manager.types)
    assert len(types) == 3
    assert "todo" in types
    assert "note" in types
    assert "warning" in types


class TestGetAggregatorUrl:
    """Test the get_aggregator_url static method."""

    def test_root_page_empty_url(self):
        """Root page with empty URL should return aggregator URL without prefix."""
        page = Mock(spec=Page)
        page.url = ""

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "editor-notes"

    def test_root_page_none_url(self):
        """Root page with None URL should return aggregator URL without prefix."""
        page = Mock(spec=Page)
        page.url = None

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "editor-notes"

    def test_single_level_page(self):
        """Single level page should return one level up."""
        page = Mock(spec=Page)
        page.url = "features/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../editor-notes"

    def test_two_level_page(self):
        """Two level page should return two levels up."""
        page = Mock(spec=Page)
        page.url = "guide/advanced/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../../editor-notes"

    def test_three_level_page(self):
        """Three level page should return three levels up."""
        page = Mock(spec=Page)
        page.url = "api/endpoints/authentication/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../../../editor-notes"

    def test_url_with_trailing_slash(self):
        """URL with trailing slash should be handled correctly."""
        page = Mock(spec=Page)
        page.url = "features/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../editor-notes"

    def test_url_without_trailing_slash(self):
        """URL without trailing slash should be handled correctly."""
        page = Mock(spec=Page)
        page.url = "features"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../editor-notes"

    def test_custom_aggregator_filename(self):
        """Custom aggregator filename should be used."""
        page = Mock(spec=Page)
        page.url = "guide/"

        result = EditorNotesManager.get_aggregator_url(page, "todos.md")

        assert result == "../todos"

    def test_custom_aggregator_with_subdirectory(self):
        """Aggregator in subdirectory should use only the stem."""
        page = Mock(spec=Page)
        page.url = "guide/"

        result = EditorNotesManager.get_aggregator_url(page, "internal/notes.md")

        assert result == "../notes"

    def test_url_with_only_slashes(self):
        """URL with only slashes should be treated as root."""
        page = Mock(spec=Page)
        page.url = "/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "editor-notes"

    def test_url_with_multiple_slashes(self):
        """URL with multiple slashes should be handled correctly."""
        page = Mock(spec=Page)
        page.url = "api//endpoints/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        # Two non-empty parts: "api" and "endpoints"
        assert result == "../../editor-notes"

    def test_deeply_nested_page(self):
        """Very deeply nested page should return correct prefix."""
        page = Mock(spec=Page)
        page.url = "a/b/c/d/e/f/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        # Six levels: a, b, c, d, e, f
        assert result == "../../../../../../editor-notes"

    def test_aggregator_with_extension(self):
        """Aggregator file extensions should be stripped."""
        page = Mock(spec=Page)
        page.url = "features/"

        result = EditorNotesManager.get_aggregator_url(page, "my-notes.markdown")

        assert result == "../my-notes"

    def test_aggregator_without_extension(self):
        """Aggregator without extension should work."""
        page = Mock(spec=Page)
        page.url = "features/"

        result = EditorNotesManager.get_aggregator_url(page, "notes")

        assert result == "../notes"


class TestGetAggregatorUrlEdgeCases:
    """Test edge cases for get_aggregator_url."""

    def test_page_url_with_special_characters(self):
        """URL with special characters (properly URL encoded path)."""
        page = Mock(spec=Page)
        page.url = "my-feature/sub-page/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../../editor-notes"

    def test_single_character_url_parts(self):
        """URL with single character parts."""
        page = Mock(spec=Page)
        page.url = "a/b/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        assert result == "../../editor-notes"

    def test_empty_url_parts_filtered(self):
        """Empty URL parts should be filtered out."""
        page = Mock(spec=Page)
        # This would create empty parts when split
        page.url = "feature//nested/"

        result = EditorNotesManager.get_aggregator_url(page, "editor-notes.md")

        # Only "feature" and "nested" are non-empty
        assert result == "../../editor-notes"

    def test_aggregator_path_with_dots(self):
        """Aggregator filename with dots should use correct stem."""
        page = Mock(spec=Page)
        page.url = "features/"

        result = EditorNotesManager.get_aggregator_url(page, "editor.notes.md")

        # Path.stem of "editor.notes.md" is "editor.notes"
        assert result == "../editor.notes"

    def test_aggregator_path_with_multiple_extensions(self):
        """Aggregator with multiple extensions uses correct stem."""
        page = Mock(spec=Page)
        page.url = "features/"

        result = EditorNotesManager.get_aggregator_url(page, "notes.backup.md")

        # Path.stem removes only the last extension
        assert result == "../notes.backup"
