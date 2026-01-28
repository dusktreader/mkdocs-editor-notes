# AGENTS.md - AI Assistant Guide

> **Important**: This is a living document that should be updated as the project evolves. When making significant
> changes to the codebase, architecture, or development workflow, please update this file accordingly to keep it
> accurate and useful for both human developers and AI assistants.

## Project Overview

This is **mkdocs-editor-notes**, a MkDocs plugin that allows documentation authors to add inline editor
notes (TODOs, questions, improvements, research tasks) that are automatically collected and displayed on an
aggregated notes page.

### Key Features
- Footnote-like syntax: `[^type:label]` with definition `[^type:label]: note text`
- Four note types: `todo`, `ponder`, `improve`, `research`
- Automatic aggregator page at `/editor-notes/`
- Bidirectional linking with visual highlighting
- Configurable marker visibility

### Tech Stack
- Python 3.12+
- MkDocs plugin API
- uv for dependency management
- Pytest for testing
- Regex-based markdown parsing

## Project Structure

```
mkdocs-editor-notes/
├── mkdocs_editor_notes/
│   ├── __init__.py       # Package exports
│   ├── models.py         # EditorNote data class
│   ├── plugin.py         # Main plugin implementation
│   └── highlight.js      # JavaScript for paragraph highlighting
├── tests/
│   └── test_plugin.py    # Unit tests
├── docs/                 # Documentation site (uses the plugin itself)
│   ├── mkdocs.yaml       # MkDocs configuration
│   └── source/           # Documentation markdown files
├── pyproject.toml        # uv dependencies and project metadata
└── README.md             # User-facing documentation
```

## Architecture

### Plugin Flow
1. **on_config**: Create placeholder aggregator file in docs_dir
2. **on_page_markdown**: Parse each markdown file for notes
   - Extract note references: `[^type:label]` or `[^type]`
   - Extract note definitions: `[^type:label]: text`
   - Match references to definitions
   - Add anchor IDs to paragraphs with references
   - Remove definitions from output
   - Optionally show/hide reference markers
3. **on_env**: Generate aggregator page markdown after all pages processed
4. **on_post_page**: Convert marker links from `.md` to proper URLs

### Note Syntax
```markdown
This paragraph has a note.[^todo:fix-typo]

[^todo:fix-typo]: Fix the typo in this paragraph
```

Without label:
```markdown
This paragraph has a note.[^ponder]

[^ponder]: Should we reconsider this approach?
```

### Paragraph Anchors
Each paragraph with a note gets an anchor ID:
```markdown
This paragraph has a note.[^todo:example]
```

Becomes:
```html
<p id="editor-note-para-1">
  This paragraph has a note.
  <a href="editor-notes/#todo-example">📝</a>
</p>
```

### Highlighting System
- JavaScript in `highlight.js` detects URL hash fragments
- Highlights target element on navigation
- Soft yellow background (50% opacity) for 3s, then 2s fade out
- Works bidirectionally (source ↔ aggregator)

## Configuration

In `mkdocs.yaml`:
```yaml
plugins:
  - editor-notes:
      show_markers: true    # Show/hide note markers in source pages
      aggregator_page: editor-notes  # URL path for aggregator page
      note_types:
        - todo      # 📝 Tasks to complete
        - ponder    # ⏳ Questions/considerations
        - improve   # 🛠️ Improvement suggestions
        - research  # 🔬 Research tasks
```

## Development Guidelines

### Running Tests
```bash
# Run tests
make qa/test

# Run full QA suite (tests, linting, type checking)
make qa/full

# Or use uv directly for specific test options
uv run pytest
uv run pytest --cov=mkdocs_editor_notes
```

Current coverage target: 90% (see `pyproject.toml`)

### Building Documentation
```bash
# Serve documentation with live reload
make docs/serve
# Visit http://127.0.0.1:10000

# Or build without serving
make docs/build
```

The docs site uses the plugin itself, providing live examples.

### Code Style
- Type hints on public functions
- Docstrings for classes and complex functions
- Regex patterns documented with comments
- Keep functions focused and testable

### Adding New Note Types
1. Add type to `DEFAULT_NOTE_TYPES` in `plugin.py`
2. Add emoji mapping in `_get_note_emoji()`
3. Update tests in `test_plugin.py`
4. Update documentation examples

### Key Patterns

#### Regex Patterns
```python
# Reference: [^type:label] or [^type]
REFERENCE_PATTERN = r'\[\^([a-zA-Z0-9_-]+)(?::([a-zA-Z0-9_-]+))?\]'

# Definition: [^type:label]: text
DEFINITION_PATTERN = r'^\[\^([a-zA-Z0-9_-]+)(?::([a-zA-Z0-9_-]+))?\]:\s*(.+)$'
```

#### Code Block Protection
Notes inside code blocks should not be processed. Use placeholder replacement:
```python
# Extract code blocks
code_blocks = re.findall(r'```.*?```', markdown, flags=re.DOTALL)
# Replace with placeholders
# Process markdown
# Restore code blocks
```

## Common Tasks

### Adding a Configuration Option
1. Add to `EditorNotesPluginConfig` in `plugin.py`
2. Use `self.config['option_name']` in plugin methods
3. Document in README.md and example `mkdocs.yaml`
4. Add test coverage

### Testing Highlighting
1. Build docs: `make docs/serve`
2. Navigate to aggregator: `http://127.0.0.1:10000/editor-notes/`
3. Click note link, verify highlight on source page
4. Click marker in source, verify highlight on aggregator entry

## Known Limitations

1. **Code block notes**: Notes in code blocks are ignored (by design)
2. **Custom themes**: Highlighting CSS may need adjustment for some themes
3. **Note threading**: No support for nested or threaded notes

## Testing Strategy

### Unit Tests
- Note pattern matching (references and definitions)
- Note collection and deduplication
- Anchor ID generation
- Marker HTML generation
- Aggregator markdown generation

### Integration Testing
Use the example site for comprehensive integration testing:
- Build example site: `make example/build` or `make example/serve`
- 443+ note annotations across multiple pages and types
- Real mkdocs build with plugin active in strict mode
- Examples of all note types and edge cases
- Bidirectional linking verification
- Visual regression testing for highlighting
- Visit http://127.0.0.1:10001 when serving

The docs site (`make docs/serve`) can also be used but has fewer annotations (48).

## Troubleshooting

### Notes not appearing
- Check regex patterns match your syntax exactly
- Verify definitions are on their own line
- Check indentation (no leading spaces on definitions)

### Links 404ing
- Ensure placeholder file created in `on_config`
- Check URL conversion in `on_post_page`
- Verify `aggregator_page` config matches links

### Highlighting not working
- Check JavaScript loaded: view page source for `highlight.js`
- Verify anchor IDs in HTML: inspect element
- Check browser console for JavaScript errors
- Ensure `extra_javascript` in `mkdocs.yaml`

### Live reload not picking up changes
- Plugin code changes require mkdocs restart
- Template changes require restart
- Markdown changes should hot-reload
- Watch paths configured in `mkdocs.yaml`

## Resources

- [MkDocs Plugin API](https://www.mkdocs.org/dev-guide/plugins/)
- [Python Markdown Extensions](https://python-markdown.github.io/extensions/)
- [uv Documentation](https://docs.astral.sh/uv/)
- Project README: `README.md`
- User docs: `docs/source/`

## Contact & Contributions

For issues, questions, or contributions, please refer to the project's GitHub repository (if available) or
contact the maintainer listed in `pyproject.toml`.

---

**Last Updated**: 2026-01-27
**Plugin Version**: 0.2.0
**MkDocs Compatibility**: 1.4+

