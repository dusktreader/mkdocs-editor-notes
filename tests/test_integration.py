"""Integration tests that build actual MkDocs sites."""

import tempfile
from pathlib import Path

import pytest
import snick
from mkdocs import config
from mkdocs.commands import build


@pytest.fixture
def temp_site():
    """Create a temporary MkDocs site for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir)
        docs_dir = site_dir / "docs"
        docs_dir.mkdir()

        # Create mkdocs.yml
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


def test_build_site_with_notes(temp_site):
    """Test building a site with editor notes."""
    site_dir, docs_dir = temp_site

    # Create index.md with notes
    (docs_dir / "index.md").write_text(
        snick.dedent(
            """
            # Home

            This is a test page[^todo:fixthis].

            [^todo:fixthis]: Fix this section
            """
        )
    )

    # Create features.md with notes
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

    # Create guide/advanced.md (nested page)
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

    # Build the site
    cfg = config.load_config(str(site_dir / "mkdocs.yml"))
    build.build(cfg)

    # Verify the build succeeded
    site_output = site_dir / "site"
    assert site_output.exists()

    # Verify aggregator page was created
    aggregator_page = site_output / "editor-notes" / "index.html"
    assert aggregator_page.exists()

    # Verify aggregator contains notes
    aggregator_html = aggregator_page.read_text()
    assert "agg-todo-fixthis" in aggregator_html
    assert "agg-bug-issue" in aggregator_html
    assert "agg-improve-enhance" in aggregator_html
    assert "agg-todo-document" in aggregator_html

    # Verify aggregator contains links back to source pages
    assert 'href="../' in aggregator_html  # Links should use relative paths

    # Verify source pages contain markers
    index_html = (site_output / "index.html").read_text()
    assert "ref-todo-fixthis" in index_html

    features_html = (site_output / "features" / "index.html").read_text()
    assert "ref-bug-issue" in features_html
    assert "ref-improve-enhance" in features_html

    advanced_html = (site_output / "guide" / "advanced" / "index.html").read_text()
    assert "ref-todo-document" in advanced_html


def test_build_site_with_notes_in_headings(temp_site):
    """Test building a site with notes in headings."""
    site_dir, docs_dir = temp_site

    # Create page with notes in headings
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

    # Build the site
    cfg = config.load_config(str(site_dir / "mkdocs.yml"))
    build.build(cfg)

    # Verify the build succeeded
    site_output = site_dir / "site"
    index_html = (site_output / "index.html").read_text()

    # Verify headings are properly rendered with anchors
    # The anchor should be after the heading marker but before text
    assert "<h1" in index_html
    assert "ref-todo-update" in index_html
    assert "<h2" in index_html
    assert "ref-bug-fix" in index_html


def test_build_site_with_custom_note_types(temp_site):
    """Test building a site with custom note types."""
    site_dir, docs_dir = temp_site

    # Update mkdocs.yml with custom note types
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

    # Create page with custom notes
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

    # Build the site
    cfg = config.load_config(str(site_dir / "mkdocs.yml"))
    build.build(cfg)

    # Verify custom notes are in aggregator
    site_output = site_dir / "site"
    aggregator_html = (site_output / "editor-notes" / "index.html").read_text()
    assert "agg-custom-test" in aggregator_html
    assert "agg-urgent-priority" in aggregator_html


def test_build_site_with_multiline_notes(temp_site):
    """Test building a site with multi-line note definitions."""
    site_dir, docs_dir = temp_site

    # Create page with multi-line notes
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

    # Build the site
    cfg = config.load_config(str(site_dir / "mkdocs.yml"))
    build.build(cfg)

    # Verify notes are properly captured
    site_output = site_dir / "site"
    aggregator_html = (site_output / "editor-notes" / "index.html").read_text()
    assert "agg-todo-inline" in aggregator_html
    assert "agg-todo-multiline" in aggregator_html
    assert "agg-bug-test" in aggregator_html

    # Verify note definitions don't appear in source page
    index_html = (site_output / "index.html").read_text()
    assert "[^todo:inline]:" not in index_html
    assert "[^todo:multiline]:" not in index_html


def test_build_site_link_depths(temp_site):
    """Test that links work correctly at different page depths."""
    site_dir, docs_dir = temp_site

    # Update mkdocs.yml to enable markers
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

    # Create deeply nested structure
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

    # Build the site
    cfg = config.load_config(str(site_dir / "mkdocs.yml"))
    build.build(cfg)

    site_output = site_dir / "site"

    # Check root page links to aggregator (no ../ prefix)
    index_html = (site_output / "index.html").read_text()
    assert 'href="editor-notes#agg-' in index_html

    # Check one-level deep page links to aggregator (one ../ prefix)
    features_html = (site_output / "features" / "index.html").read_text()
    assert 'href="../editor-notes#agg-' in features_html

    # Check two-levels deep page links to aggregator (two ../ prefixes)
    advanced_html = (site_output / "guide" / "advanced" / "index.html").read_text()
    assert 'href="../../editor-notes#agg-' in advanced_html

    # Check aggregator links back to source pages
    aggregator_html = (site_output / "editor-notes" / "index.html").read_text()
    assert 'href="../#ref-todo-root' in aggregator_html
    assert 'href="../features/#ref-todo-one' in aggregator_html
    assert 'href="../guide/advanced/#ref-todo-two' in aggregator_html
