[![Latest Version](https://img.shields.io/pypi/v/mkdocs-editor-notes?label=pypi-version&logo=python&style=plastic)](https://pypi.org/project/mkdocs-editor-notes/)
[![Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdusktreader%2Fmkdocs-editor-notes%2Fmain%2Fpyproject.toml&style=plastic&logo=python&label=python-versions)](https://www.python.org/)
[![Build Status](https://github.com/dusktreader/mkdocs-editor-notes/actions/workflows/main.yml/badge.svg)](https://github.com/dusktreader/mkdocs-editor-notes/actions/workflows/main.yml)
[![Documentation Status](https://github.com/dusktreader/mkdocs-editor-notes/actions/workflows/docs.yml/badge.svg)](https://dusktreader.github.io/mkdocs-editor-notes/)

# mkdocs-editor-notes

_Provides a page of editor's notes gathered from annotated document files._


## Overview

mkdocs-editor-notes is a MkDocs plugin that allows you to embed editorial notes directly in your markdown documentation files. These notes can be used to track todos, questions, improvements, and research items without cluttering the main documentation.

All notes are automatically collected and displayed on a dedicated aggregator page, making it easy to see all editorial work at a glance.

## Key Features

- **Multiple Note Types**: Support for `todo`, `ponder`, `improve`, and `research` notes
- **Labeled Notes**: Optional labels for better organization (e.g., `[^todo:fix-grammar]`)
- **Aggregator Page**: Automatic collection of all notes in one place
- **Source Linking**: Click to navigate back to note locations with paragraph highlighting
- **Configurable Visibility**: Show or hide note markers in rendered pages
- **Footnote-like Syntax**: Familiar syntax similar to markdown footnotes

## Quick Example

```markdown
This feature needs more work.[^todo:polish]

[^todo:polish]: Add error handling and tests

The current approach might not scale.[^ponder:performance]

[^ponder:performance]: Should we benchmark with larger datasets?

Research needed here.[^research:alternatives]

[^research:alternatives]: Look into alternative libraries
```

All these notes will appear on the `/editor-notes/` page, grouped by type, with links back to their source paragraphs.

## Super-quick Start

Requires: Python 3.12 to 3.14

Install through pip:

```bash
pip install mkdocs-editor-notes
```

Add to your `mkdocs.yml`:

```yaml
plugins:
  - editor-notes
```

## Configuration Options

```yaml
plugins:
  - editor-notes:
      show_markers: false          # Show/hide markers in source pages (default: false)
      enable_highlighting: true    # Enable paragraph highlighting (default: true)
      aggregator_page: "editor-notes.md"  # Location of aggregator page
      note_types:                  # Supported note types
        - todo
        - ponder
        - improve
        - research
```

## Note Types

- **todo**: Tasks that need to be completed
- **ponder**: Questions or considerations  
- **improve**: Improvement suggestions
- **research**: Research tasks

## Syntax

### With Label
```markdown
This paragraph has a note.[^todo:fix-typo]

[^todo:fix-typo]: Correct the spelling error here
```

### Without Label
```markdown
Another paragraph.[^ponder]

[^ponder]: Should we consider a different approach?
```


## Documentation

The complete documentation can be found at the
[mkdocs-editor-notes home page](https://dusktreader.github.io/mkdocs-editor-notes)
