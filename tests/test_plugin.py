from pathlib import Path

import pytest
import snick

from mkdocs_editor_notes.constants import NOTE_DEF_PATTERN, NOTE_REF_PATTERN
from mkdocs_editor_notes.plugin import EditorNotesPlugin
from mkdocs_editor_notes.note import EditorNote


def test_plugin_initialization():
    plugin = EditorNotesPlugin()

    assert plugin.note_manager.empty is True


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
            show_markers=True,
            aggregator_page="jawa/ewok.md",
            note_type_emojis=dict(
                jawa="🥷",
                ewok="🐻",
            ),
        )
    )

    notes = [
        EditorNote(
            note_type="jawa",
            label="desert-rat",
            text="Utinni!",
            source_page=Path("index.md"),
            source_url="",
            line_number=13,
        ),
        EditorNote(
            note_type="ponder",
            label="question",
            text="Think about this",
            source_page=Path("features.md"),
            source_url="features/",
            line_number=21,
        ),
        EditorNote(
            note_type="todo",
            label="improve",
            text="Make it better",
            source_page=Path("index.md"),
            source_url="",
            line_number=34,
        ),
        EditorNote(
            note_type="ewok",
            label="forest-bear",
            text="Yub nub!",
            source_page=Path("reference.md"),
            source_url="reference/",
            line_number=71,
        ),
        EditorNote(
            note_type="todo",
            label="chill",
            text="Now, rest",
            source_page=Path("index.md"),
            source_url="",
            line_number=99,
        ),
    ]

    for note in notes:
        plugin.note_manager.add(note)

    assert plugin.note_manager.build_aggregator_markdown(plugin.get_emoji) == snick.dedent(
        """
        # Editor Notes

        This page aggregates all editor notes found throughout the documentation.


        ## 🐻 ewok

        <div class="editor-note-entry">
            <span id="agg-ewok-forest-bear"></span>
            <h4>
                forest-bear (<a href="../reference/#ref-ewok-forest-bear">reference.md:71</a>)
            </h4>
            <p>Yub nub!</p>
        </div>


        ## 🥷 jawa

        <div class="editor-note-entry">
            <span id="agg-jawa-desert-rat"></span>
            <h4>
                desert-rat (<a href="../#ref-jawa-desert-rat">index.md:13</a>)
            </h4>
            <p>Utinni!</p>
        </div>


        ## ⏳ ponder

        <div class="editor-note-entry">
            <span id="agg-ponder-question"></span>
            <h4>
                question (<a href="../features/#ref-ponder-question">features.md:21</a>)
            </h4>
            <p>Think about this</p>
        </div>


        ## ✅ todo

        <div class="editor-note-entry">
            <span id="agg-todo-improve"></span>
            <h4>
                improve (<a href="../#ref-todo-improve">index.md:34</a>)
            </h4>
            <p>Make it better</p>
        </div>

        <div class="editor-note-entry">
            <span id="agg-todo-chill"></span>
            <h4>
                chill (<a href="../#ref-todo-chill">index.md:99</a>)
            </h4>
            <p>Now, rest</p>
        </div>
        """
    )


def test_marker_links__use_agg_id():
    """Verify that marker links point to aggregator anchors using agg_id."""
    plugin = EditorNotesPlugin()
    plugin.load_config(dict(show_markers=True, aggregator_page="notes.md"))

    note = EditorNote(
        note_type="todo",
        label="test-label",
        text="Test text",
        source_page=Path("index.md"),
        source_url="",
        line_number=10,
    )
    plugin.note_manager.add(note)

    from unittest.mock import Mock

    mock_page = Mock()
    mock_page.url = ""

    replacer = plugin.get_ref_replacer(mock_page)
    assert callable(replacer), "replacer should be callable when show_markers=True"

    test_text = "Some text[^todo:test-label] more text"
    match = NOTE_REF_PATTERN.search(test_text)
    assert match

    result = replacer(match)

    # Verify the link uses agg_id (agg-todo-test-label) not ref_id (ref-todo-test-label)
    assert 'href="notes#agg-todo-test-label"' in result
    assert "ref-todo-test-label" not in result
    assert f'title="{note.hover_text}"' in result


def test_plugin_config__custom_highlight_durations():
    """Verify that custom highlight durations can be configured."""
    plugin = EditorNotesPlugin()
    plugin.load_config(
        dict(
            highlight_duration=5000,
            highlight_fade_duration=1000,
        )
    )

    assert plugin.config.highlight_duration == 5000
    assert plugin.config.highlight_fade_duration == 1000


def test_plugin_config__default_highlight_durations():
    """Verify default highlight duration values."""
    plugin = EditorNotesPlugin()
    plugin.load_config(dict())

    assert plugin.config.highlight_duration == 3000
    assert plugin.config.highlight_fade_duration == 2000


def test_undefined_note_reference__logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that undefined note references generate warnings."""
    import logging
    from unittest.mock import Mock

    caplog.set_level(logging.WARNING)

    plugin = EditorNotesPlugin()
    plugin.load_config(dict())

    mock_page = Mock()
    mock_page.file.src_uri = "test.md"

    mock_config = Mock()
    mock_files = Mock()

    markdown = snick.dedent(
        """
        This is some text with a reference[^todo:undefined-note] to a note that doesn't exist.
        """
    )

    plugin.on_page_markdown(markdown, mock_page, mock_config, mock_files)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "Undefined note reference" in caplog.records[0].message
    assert "[^todo:undefined-note]" in caplog.records[0].message
    assert "test.md" in caplog.records[0].message


def test_note_refs_in_headings():
    """Verify that note refs in headings don't break heading rendering."""
    from unittest.mock import Mock

    plugin = EditorNotesPlugin()
    plugin.load_config(dict(show_markers=True))

    markdown = snick.dedent("""
        # Test Heading[^todo:heading-fix]

        Some content.

        ## Subheading[^ponder:subheading]

        More content.

        [^todo:heading-fix]: Fix this heading
        [^ponder:subheading]: Consider this subheading
    """)

    mock_page = Mock()
    mock_page.url = "test/"
    mock_page.file.src_uri = "test.md"

    result = plugin.on_page_markdown(markdown, mock_page, Mock(), Mock())
    assert result is not None, "on_page_markdown should return processed markdown"

    # Verify anchors are placed after heading markers, not before
    assert '#<span id="ref-todo-heading-fix"></span>' in result
    assert '##<span id="ref-ponder-subheading"></span>' in result

    # Verify they're not at the start of the line (which would break headings)
    assert not result.strip().startswith('<span id="ref-todo-heading-fix"></span>#')
    assert '<span id="ref-ponder-subheading"></span>##' not in result


def test_note_refs_in_lists():
    from unittest.mock import Mock

    plugin = EditorNotesPlugin()
    plugin.load_config(dict(show_markers=True))

    for note in [
        EditorNote(
            note_type="todo",
            label="fixit",
            text="Fix this list item",
            source_page=Path("test.md"),
            source_url="",
            line_number=1,
        ),
        EditorNote(
            note_type="bug",
            label="issue",
            text="This is broken",
            source_page=Path("test.md"),
            source_url="",
            line_number=2,
        ),
    ]:
        plugin.note_manager.add(note)

    markdown = snick.dedent(
        """
        # Test Lists

        Unordered list:

        - Item one
        - Item two[^todo:fixit]
        - Item three

        Ordered list:

        1. First
        2. Second[^bug:issue]
        3. Third
        """
    )

    mock_page = Mock()
    mock_page.file = Mock()
    mock_page.file.src_uri = "test.md"
    mock_page.url = ""

    mock_config = Mock()
    mock_files = Mock()

    result = plugin.on_page_markdown(markdown, mock_page, mock_config, mock_files)

    # Check that anchor spans are placed after list markers
    assert result is not None
    assert '- <span id="ref-todo-fixit"></span>Item two' in result
    assert '2. <span id="ref-bug-issue"></span>Second' in result
