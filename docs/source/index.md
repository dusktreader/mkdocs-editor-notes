# mkdocs-editor-notes

_Provides a page of editor's notes gathered from annotated document files._


## Overview

mkdocs-editor-notes is a plugin that allows you to embed editorial notes directly in your markdown documentation
files. These notes can be used to track todos, questions, improvements, and research items without cluttering
the main documentation.

All notes are automatically collected and displayed on a dedicated aggregator page, making it easy to see all
editorial work at a glance.


## Key Features

- **Multiple Note Types**: Support for todo, ponder, improve, and research notes
- **Labeled Notes**: Optional labels for better organization
- **Aggregator Page**: Automatic collection of all notes in one place
- **Source Linking**: Click to navigate back to note locations
- **Highlighting**: Paragraphs highlight when navigated from aggregator
- **Configurable**: Show/hide markers, custom note types, and more


## Quick Example

```markdown
This feature needs more work.[^todo:polish]

[^todo:polish]: Add error handling and tests

The current approach might not scale.[^ponder:performance]

[^ponder:performance]: Should we benchmark with larger datasets?
```


## Installation

Install from PyPI:

```bash
pip install mkdocs-editor-notes
```

Add to your `mkdocs.yml`:

```yaml
plugins:
  - editor-notes
```


## Documentation

- [Quickstart](quickstart.md): Get started quickly
- [Features](features.md): Detailed feature documentation
- [Reference](reference.md): API reference
