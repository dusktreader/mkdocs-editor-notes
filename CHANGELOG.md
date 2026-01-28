# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased


## v0.2.0 - 2026-01-27

Initial feature release of the MkDocs Editor Notes plugin featuring:

- **Editor-style notes**: Add inline editorial notes using `[^note-id]: Note text` syntax that are removed from rendered pages
- **Note references**: Reference notes anywhere in your docs with `[^note-id]` - rendered as clickable markers
- **Aggregator page**: Automatically generated page at `/editor-notes/` that collects all notes across your documentation
- **Smart anchor placement**: Note references work correctly in headings, list items, and regular paragraphs
- **Multi-line support**: Note definitions can span multiple lines for longer editorial comments
- **Relative linking**: All links between notes, references, and source pages work correctly regardless of page depth
- **Comprehensive type safety**: Full type annotations with zero type warnings for maintainability


## v0.1.0 - 2026-01-21
- Generated project from template
