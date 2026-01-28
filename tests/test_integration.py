"""Integration tests that build actual MkDocs sites."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
import snick
from mkdocs import config
from mkdocs.commands import build


@pytest.fixture
def temp_site() -> Generator[tuple[Path, Path], None, None]:
    """Create a temporary MkDocs site for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir)
        docs_dir = site_dir / "docs"
        docs_dir.mkdir()

        mkdocs_yml = site_dir / "mkdocs.yml"
        mkdocs_yml.write_text(
            snick.dedent(
                """
                site_name: Test Site
                plugins:
                  - search
                  - editor-notes

                nav:
                  - Home: index.md
                  - Features: features.md
                  - Guide:
                      - Advanced: guide/advanced.md
                """
            )
        )

        yield site_dir, docs_dir


def test_build_site_with_notes(temp_site: tuple[Path, Path]) -> None:
    """Test building a site with editor notes."""
    site_dir: Path
    docs_dir: Path
    site_dir, docs_dir = temp_site

    (docs_dir / "index.md").write_text(
        snick.dedent(
            """
            # Home

            This is a test page[^todo:fixthis].

            [^todo:fixthis]: Fix this section
            """
        )
    )

    (docs_dir / "features.md").write_text(
        snick.dedent(
            """
            # Features

            ## Feature 1[^bug:issue]

            This feature needs work[^improve:enhance].

            [^bug:issue]: There's a bug here

            [^improve:enhance]: Could be better
            """
        )
    )

    guide_dir = docs_dir / "guide"
    guide_dir.mkdir()
    (guide_dir / "advanced.md").write_text(
        snick.dedent(
            """
            # Advanced Guide

            Advanced content[^todo:document].

            [^todo:document]: Add more docs
            """
        )
    )

    cfg = config.load_config(str(site_dir / "mkdocs.yml"))  # pyright: ignore[reportUnknownMemberType]
    build.build(cfg)

    site_output = site_dir / "site"
    assert site_output.exists()

    aggregator_page = site_output / "editor-notes" / "index.html"
    assert aggregator_page.exists()

    aggregator_html = aggregator_page.read_text()
    assert "agg-todo-fixthis" in aggregator_html
    assert "agg-bug-issue" in aggregator_html
    assert "agg-improve-enhance" in aggregator_html
    assert "agg-todo-document" in aggregator_html

    assert 'href="../' in aggregator_html

    index_html = (site_output / "index.html").read_text()
    assert "ref-todo-fixthis" in index_html

    features_html = (site_output / "features" / "index.html").read_text()
    assert "ref-bug-issue" in features_html
    assert "ref-improve-enhance" in features_html

    advanced_html = (site_output / "guide" / "advanced" / "index.html").read_text()
    assert "ref-todo-document" in advanced_html


def test_build_site_with_notes_in_headings(temp_site: tuple[Path, Path]) -> None:
    """Test building a site with notes in headings."""
    site_dir: Path
    docs_dir: Path
    site_dir, docs_dir = temp_site

    (docs_dir / "index.md").write_text(
        snick.dedent(
            """
            # Home Page[^todo:update]

            ## Section[^bug:fix]

            Content here.

            [^todo:update]: Update this heading
            [^bug:fix]: Fix this section
            """
        )
    )

    (docs_dir / "features.md").write_text("# Features\n\nNo notes here.")

    cfg = config.load_config(str(site_dir / "mkdocs.yml"))  # pyright: ignore[reportUnknownMemberType]
    build.build(cfg)

    site_output = site_dir / "site"
    index_html = (site_output / "index.html").read_text()

    # Verify headings are properly rendered with anchors
    # The anchor should be after the heading marker but before text
    assert "<h1" in index_html
    assert "ref-todo-update" in index_html
    assert "<h2" in index_html
    assert "ref-bug-fix" in index_html


def test_build_site_with_custom_note_types(temp_site: tuple[Path, Path]) -> None:
    """Test building a site with custom note types."""
    site_dir: Path
    docs_dir: Path
    site_dir, docs_dir = temp_site

    mkdocs_yml = site_dir / "mkdocs.yml"
    mkdocs_yml.write_text(
        snick.dedent(
            """
            site_name: Test Site
            plugins:
              - search
              - editor-notes:
                  note_type_emojis:
                    custom: "🎯"
                    urgent: "🚨"

            nav:
              - Home: index.md
            """
        )
    )

    (docs_dir / "index.md").write_text(
        snick.dedent(
            """
            # Home

            Custom note[^custom:test].
            Urgent note[^urgent:priority].

            [^custom:test]: Custom type
            [^urgent:priority]: High priority
            """
        )
    )

    cfg = config.load_config(str(site_dir / "mkdocs.yml"))  # pyright: ignore[reportUnknownMemberType]
    build.build(cfg)

    site_output = site_dir / "site"
    aggregator_html = (site_output / "editor-notes" / "index.html").read_text()
    assert "agg-custom-test" in aggregator_html
    assert "agg-urgent-priority" in aggregator_html


def test_build_site_with_multiline_notes(temp_site: tuple[Path, Path]) -> None:
    """Test building a site with multi-line note definitions."""
    site_dir: Path
    docs_dir: Path
    site_dir, docs_dir = temp_site

    (docs_dir / "index.md").write_text(
        snick.dedent(
            """
            # Home

            Inline note[^todo:inline].

            Multi-line note[^todo:multiline].

            Another note[^bug:test].

            [^todo:inline]: This is inline.

            [^todo:multiline]:
            This is on the next line.

            [^bug:test]:
                This has indentation.
            """
        )
    )

    (docs_dir / "features.md").write_text("# Features\n\nNo notes.")

    cfg = config.load_config(str(site_dir / "mkdocs.yml"))  # pyright: ignore[reportUnknownMemberType]
    build.build(cfg)

    site_output = site_dir / "site"
    aggregator_html = (site_output / "editor-notes" / "index.html").read_text()
    assert "agg-todo-inline" in aggregator_html
    assert "agg-todo-multiline" in aggregator_html
    assert "agg-bug-test" in aggregator_html

    index_html = (site_output / "index.html").read_text()
    assert "[^todo:inline]:" not in index_html
    assert "[^todo:multiline]:" not in index_html


def test_build_site_link_depths(temp_site: tuple[Path, Path]) -> None:
    """Test that links work correctly at different page depths."""
    site_dir: Path
    docs_dir: Path
    site_dir, docs_dir = temp_site

    mkdocs_yml = site_dir / "mkdocs.yml"
    mkdocs_yml.write_text(
        snick.dedent(
            """
            site_name: Test Site
            plugins:
              - search
              - editor-notes:
                  show_markers: true

            nav:
              - Home: index.md
              - Features: features.md
              - Guide:
                  - Advanced: guide/advanced.md
            """
        )
    )

    (docs_dir / "index.md").write_text(
        snick.dedent(
            """
            # Home

            Root note[^todo:root].

            [^todo:root]: Root level note
            """
        )
    )

    (docs_dir / "features.md").write_text(
        snick.dedent(
            """
            # Features

            One level[^todo:one].

            [^todo:one]: One level deep
            """
        )
    )

    guide_dir = docs_dir / "guide"
    guide_dir.mkdir()
    (guide_dir / "advanced.md").write_text(
        snick.dedent(
            """
            # Advanced

            Two levels[^todo:two].

            [^todo:two]: Two levels deep
            """
        )
    )

    cfg = config.load_config(str(site_dir / "mkdocs.yml"))  # pyright: ignore[reportUnknownMemberType]
    build.build(cfg)

    site_output = site_dir / "site"

    index_html = (site_output / "index.html").read_text()
    assert 'href="editor-notes#agg-' in index_html

    features_html = (site_output / "features" / "index.html").read_text()
    assert 'href="../editor-notes#agg-' in features_html

    advanced_html = (site_output / "guide" / "advanced" / "index.html").read_text()
    assert 'href="../../editor-notes#agg-' in advanced_html

    aggregator_html = (site_output / "editor-notes" / "index.html").read_text()
    assert 'href="../#ref-todo-root' in aggregator_html
    assert 'href="../features/#ref-todo-one' in aggregator_html
    assert 'href="../guide/advanced/#ref-todo-two' in aggregator_html
