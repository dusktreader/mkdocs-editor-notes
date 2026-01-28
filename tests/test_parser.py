"""Tests for markdown parsing utilities."""

import pytest

from mkdocs_editor_notes.manager import LineType, EditorNotesManager


class TestLineType:
    """Tests for LineType enum."""

    def test_enum_values(self):
        """Verify enum has expected values."""
        assert LineType.HEADING.value == "heading"
        assert LineType.UNORDERED_LIST.value == "unordered_list"
        assert LineType.ORDERED_LIST.value == "ordered_list"
        assert LineType.REGULAR.value == "regular"

    def test_enum_members(self):
        """Verify all expected enum members exist."""
        expected = {"HEADING", "UNORDERED_LIST", "ORDERED_LIST", "REGULAR"}
        actual = {member.name for member in LineType}
        assert actual == expected


class TestClassifyLine:
    """Tests for classify_line function."""

    def test_classify_heading_h1(self):
        assert EditorNotesManager.classify_line("# Heading") == LineType.HEADING

    def test_classify_heading_h2(self):
        assert EditorNotesManager.classify_line("## Heading") == LineType.HEADING

    def test_classify_heading_h3(self):
        assert EditorNotesManager.classify_line("### Heading") == LineType.HEADING

    def test_classify_heading_h4(self):
        assert EditorNotesManager.classify_line("#### Heading") == LineType.HEADING

    def test_classify_heading_h5(self):
        assert EditorNotesManager.classify_line("##### Heading") == LineType.HEADING

    def test_classify_heading_h6(self):
        assert EditorNotesManager.classify_line("###### Heading") == LineType.HEADING

    def test_classify_heading_with_leading_space(self):
        assert EditorNotesManager.classify_line("  # Indented heading") == LineType.HEADING

    def test_classify_heading_with_tab(self):
        assert EditorNotesManager.classify_line("\t## Tabbed heading") == LineType.HEADING

    def test_classify_unordered_list_dash(self):
        assert EditorNotesManager.classify_line("- Item") == LineType.UNORDERED_LIST

    def test_classify_unordered_list_asterisk(self):
        assert EditorNotesManager.classify_line("* Item") == LineType.UNORDERED_LIST

    def test_classify_unordered_list_plus(self):
        assert EditorNotesManager.classify_line("+ Item") == LineType.UNORDERED_LIST

    def test_classify_unordered_list_indented(self):
        assert EditorNotesManager.classify_line("  - Indented item") == LineType.UNORDERED_LIST

    def test_classify_ordered_list_single_digit(self):
        assert EditorNotesManager.classify_line("1. Item") == LineType.ORDERED_LIST

    def test_classify_ordered_list_double_digit(self):
        assert EditorNotesManager.classify_line("10. Item") == LineType.ORDERED_LIST

    def test_classify_ordered_list_triple_digit(self):
        assert EditorNotesManager.classify_line("999. Item") == LineType.ORDERED_LIST

    def test_classify_ordered_list_indented(self):
        assert EditorNotesManager.classify_line("  1. Indented item") == LineType.ORDERED_LIST

    def test_classify_regular_text(self):
        assert EditorNotesManager.classify_line("Regular text") == LineType.REGULAR

    def test_classify_regular_with_indent(self):
        assert EditorNotesManager.classify_line("  Regular text with indent") == LineType.REGULAR

    def test_classify_empty_line(self):
        assert EditorNotesManager.classify_line("") == LineType.REGULAR

    def test_classify_whitespace_only(self):
        assert EditorNotesManager.classify_line("   ") == LineType.REGULAR

    def test_classify_text_with_dash(self):
        """Text containing dash but not starting with list marker."""
        assert EditorNotesManager.classify_line("Not a list - just text") == LineType.REGULAR

    def test_classify_text_with_number(self):
        """Text starting with number but no period nearby."""
        assert EditorNotesManager.classify_line("2024 is the year") == LineType.REGULAR

    def test_classify_hashtag_in_text(self):
        """Text containing # but not as heading marker."""
        assert EditorNotesManager.classify_line("Use #hashtag in text") == LineType.REGULAR


class TestInsertAnchorInHeading:
    """Tests for insert_anchor_in_heading function."""

    def test_h1_heading(self):
        result = EditorNotesManager.insert_anchor_in_heading("# My Heading[^note]", '<span id="ref-note"></span>')
        assert result == '#<span id="ref-note"></span> My Heading[^note]'

    def test_h2_heading(self):
        result = EditorNotesManager.insert_anchor_in_heading(
            "## Subheading[^todo:fix]", '<span id="ref-todo-fix"></span>'
        )
        assert result == '##<span id="ref-todo-fix"></span> Subheading[^todo:fix]'

    def test_h3_heading(self):
        result = EditorNotesManager.insert_anchor_in_heading("### Section[^note]", '<span id="ref-note"></span>')
        assert result == '###<span id="ref-note"></span> Section[^note]'

    def test_heading_with_leading_whitespace(self):
        result = EditorNotesManager.insert_anchor_in_heading("  ### Indented[^note]", '<span id="ref-note"></span>')
        assert result == '  ###<span id="ref-note"></span> Indented[^note]'

    def test_heading_with_multiple_spaces(self):
        result = EditorNotesManager.insert_anchor_in_heading(
            "    # Multiple spaces[^note]", '<span id="ref-note"></span>'
        )
        assert result == '    #<span id="ref-note"></span> Multiple spaces[^note]'

    def test_heading_with_tab(self):
        result = EditorNotesManager.insert_anchor_in_heading("\t## Tabbed[^note]", '<span id="ref-note"></span>')
        assert result == '\t##<span id="ref-note"></span> Tabbed[^note]'


class TestInsertAnchorInUnorderedList:
    """Tests for insert_anchor_in_unordered_list function."""

    def test_dash_list(self):
        result = EditorNotesManager.insert_anchor_in_unordered_list("- Item text[^note]", '<span id="ref-note"></span>')
        assert result == '- <span id="ref-note"></span>Item text[^note]'

    def test_asterisk_list(self):
        result = EditorNotesManager.insert_anchor_in_unordered_list("* Item text[^note]", '<span id="ref-note"></span>')
        assert result == '* <span id="ref-note"></span>Item text[^note]'

    def test_plus_list(self):
        result = EditorNotesManager.insert_anchor_in_unordered_list("+ Item text[^note]", '<span id="ref-note"></span>')
        assert result == '+ <span id="ref-note"></span>Item text[^note]'

    def test_list_with_leading_whitespace(self):
        result = EditorNotesManager.insert_anchor_in_unordered_list(
            "  - Indented item[^note]", '<span id="ref-note"></span>'
        )
        assert result == '  - <span id="ref-note"></span>Indented item[^note]'

    def test_list_with_extra_spacing(self):
        """List item with extra spaces after marker."""
        result = EditorNotesManager.insert_anchor_in_unordered_list(
            "-   Item with spaces[^note]", '<span id="ref-note"></span>'
        )
        assert result == '- <span id="ref-note"></span>Item with spaces[^note]'

    def test_list_with_tab(self):
        result = EditorNotesManager.insert_anchor_in_unordered_list(
            "\t* Tabbed item[^note]", '<span id="ref-note"></span>'
        )
        assert result == '\t* <span id="ref-note"></span>Tabbed item[^note]'


class TestInsertAnchorInOrderedList:
    """Tests for insert_anchor_in_ordered_list function."""

    def test_single_digit(self):
        result = EditorNotesManager.insert_anchor_in_ordered_list("1. Item text[^note]", '<span id="ref-note"></span>')
        assert result == '1. <span id="ref-note"></span>Item text[^note]'

    def test_double_digit(self):
        result = EditorNotesManager.insert_anchor_in_ordered_list("42. Item text[^note]", '<span id="ref-note"></span>')
        assert result == '42. <span id="ref-note"></span>Item text[^note]'

    def test_triple_digit(self):
        result = EditorNotesManager.insert_anchor_in_ordered_list(
            "999. Item text[^note]", '<span id="ref-note"></span>'
        )
        assert result == '999. <span id="ref-note"></span>Item text[^note]'

    def test_list_with_leading_whitespace(self):
        result = EditorNotesManager.insert_anchor_in_ordered_list(
            "  10. Indented item[^note]", '<span id="ref-note"></span>'
        )
        assert result == '  10. <span id="ref-note"></span>Indented item[^note]'

    def test_list_with_extra_spacing(self):
        """List item with extra spaces after number."""
        result = EditorNotesManager.insert_anchor_in_ordered_list(
            "1.   Item with spaces[^note]", '<span id="ref-note"></span>'
        )
        assert result == '1. <span id="ref-note"></span>Item with spaces[^note]'

    def test_fallback_no_period(self):
        """Edge case: number without period (fallback)."""
        result = EditorNotesManager.insert_anchor_in_ordered_list(
            "1 Item without period", '<span id="ref-note"></span>'
        )
        assert result == '<span id="ref-note"></span>1 Item without period'

    def test_fallback_empty_stripped(self):
        """Edge case: empty line after stripping."""
        result = EditorNotesManager.insert_anchor_in_ordered_list("   ", '<span id="ref-note"></span>')
        assert result == '<span id="ref-note"></span>   '

    def test_period_far_from_start(self):
        """Period appears after 4 characters - should fallback."""
        result = EditorNotesManager.insert_anchor_in_ordered_list("12345. Item", '<span id="ref-note"></span>')
        # Period at position 5, which is beyond the [:4] check in classify_line
        # But if it gets here, we should still handle it
        assert result == '12345. <span id="ref-note"></span>Item'


class TestInsertAnchorAtBeginning:
    """Tests for insert_anchor_at_beginning function."""

    def test_regular_text(self):
        result = EditorNotesManager.insert_anchor_at_beginning("Regular text[^note]", '<span id="ref-note"></span>')
        assert result == '<span id="ref-note"></span>Regular text[^note]'

    def test_empty_line(self):
        result = EditorNotesManager.insert_anchor_at_beginning("", '<span id="ref-note"></span>')
        assert result == '<span id="ref-note"></span>'

    def test_whitespace_line(self):
        result = EditorNotesManager.insert_anchor_at_beginning("   ", '<span id="ref-note"></span>')
        assert result == '<span id="ref-note"></span>   '

    def test_text_with_special_chars(self):
        result = EditorNotesManager.insert_anchor_at_beginning(
            "Text with **bold** and `code`[^note]", '<span id="ref-note"></span>'
        )
        assert result == '<span id="ref-note"></span>Text with **bold** and `code`[^note]'


class TestInsertAnchorInLine:
    """Tests for insert_anchor_in_line function (integration)."""

    def test_integrates_heading(self):
        result = EditorNotesManager.insert_anchor_in_line("## Test Heading[^note]", '<span id="ref-note"></span>')
        assert result == '##<span id="ref-note"></span> Test Heading[^note]'

    def test_integrates_unordered_list(self):
        result = EditorNotesManager.insert_anchor_in_line("- List item[^note]", '<span id="ref-note"></span>')
        assert result == '- <span id="ref-note"></span>List item[^note]'

    def test_integrates_ordered_list(self):
        result = EditorNotesManager.insert_anchor_in_line("1. List item[^note]", '<span id="ref-note"></span>')
        assert result == '1. <span id="ref-note"></span>List item[^note]'

    def test_integrates_regular(self):
        result = EditorNotesManager.insert_anchor_in_line("Regular text[^note]", '<span id="ref-note"></span>')
        assert result == '<span id="ref-note"></span>Regular text[^note]'

    def test_integrates_empty_line(self):
        result = EditorNotesManager.insert_anchor_in_line("", '<span id="ref-note"></span>')
        assert result == '<span id="ref-note"></span>'

    def test_all_heading_levels(self):
        """Test all heading levels work correctly."""
        for level in range(1, 7):
            heading = "#" * level + " Heading"
            result = EditorNotesManager.insert_anchor_in_line(heading, '<span id="x"></span>')
            expected = "#" * level + '<span id="x"></span> Heading'
            assert result == expected

    def test_all_unordered_markers(self):
        """Test all unordered list markers work correctly."""
        for marker in ["-", "*", "+"]:
            line = f"{marker} Item"
            result = EditorNotesManager.insert_anchor_in_line(line, '<span id="x"></span>')
            expected = f'{marker} <span id="x"></span>Item'
            assert result == expected

    def test_preserves_indentation_in_all_types(self):
        """Test that indentation is preserved for all line types."""
        test_cases = [
            ("  # Heading", '  #<span id="x"></span> Heading'),
            ("  - Item", '  - <span id="x"></span>Item'),
            ("  1. Item", '  1. <span id="x"></span>Item'),
            ("  Regular", '<span id="x"></span>  Regular'),
        ]
        for line, expected in test_cases:
            result = EditorNotesManager.insert_anchor_in_line(line, '<span id="x"></span>')
            assert result == expected


class TestEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_heading_with_no_space_after_markers(self):
        """Heading without space after # markers."""
        result = EditorNotesManager.insert_anchor_in_line("#Heading", '<span id="x"></span>')
        assert result == '#<span id="x"></span>Heading'

    def test_list_with_no_space_after_marker(self):
        """List without space after marker."""
        result = EditorNotesManager.insert_anchor_in_line("-Item", '<span id="x"></span>')
        assert result == '- <span id="x"></span>Item'

    def test_very_long_line(self):
        """Very long line should still work."""
        long_line = "Regular text " * 100
        result = EditorNotesManager.insert_anchor_in_line(long_line, '<span id="x"></span>')
        assert result == f'<span id="x"></span>{long_line}'

    def test_unicode_content(self):
        """Lines with unicode characters."""
        result = EditorNotesManager.insert_anchor_in_line("- 日本語 text[^note]", '<span id="x"></span>')
        assert result == '- <span id="x"></span>日本語 text[^note]'

    def test_multiple_anchors_same_line(self):
        """What happens if we try to insert multiple anchors (shouldn't normally happen)."""
        line = "# Heading"
        result1 = EditorNotesManager.insert_anchor_in_line(line, '<span id="1"></span>')
        result2 = EditorNotesManager.insert_anchor_in_line(result1, '<span id="2"></span>')
        # Second insertion still classifies as heading after lstrip(), so anchor goes after #
        assert result2 == '#<span id="2"></span><span id="1"></span> Heading'
