# Plan for mkdocs-editor-notes Plugin

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Syntax Design](#syntax-design)
4. [Implementation Steps](#implementation-steps)
5. [Documentation Plan](#documentation-plan)

## Overview

Create a mkdocs plugin that:
- Allows adding "editor notes" in markdown files with footnote-like syntax
- Aggregates all notes into a dedicated page
- Supports different note types (todo, ponder, improve, research, etc.)
- Allows labeled notes with `<name>:<text>` syntax
- Links back to source paragraphs with highlighting
- Optionally shows/hides markers in the source pages

## Architecture

### Components
1. **Markdown Extension**: Parse editor notes from markdown
2. **Plugin**: MkDocs plugin to coordinate processing
3. **Note Collector**: Gather notes from all pages
4. **Aggregator Page Generator**: Create the editor notes index page
5. **HTML Post-processor**: Add anchor links and highlighting support

### Data Structure
```python
EditorNote:
  - type: str (todo, ponder, improve, research, etc.)
  - label: Optional[str]
  - text: str
  - source_page: str
  - source_paragraph_id: str
  - visible_marker: bool
```

## Syntax Design

### Proposed Syntax
Extending footnote syntax: `[^type:label]` or `[^type]`

Examples:
```markdown
This is a paragraph with an editor note.[^todo:fix-grammar]

[^todo:fix-grammar]: Need to review grammar here

Another paragraph with a ponder.[^ponder]

[^ponder]: Should we consider a different approach?

Research needed here.[^research:alternatives]

[^research:alternatives]: Look into alternative libraries
```

### Note Types
- `todo` - Tasks to complete
- `ponder` - Questions or considerations
- `improve` - Improvement suggestions
- `research` - Research tasks

## Implementation Steps

### Phase 1: Core Parsing
1. Create markdown extension to parse editor note syntax
2. Extract notes with type, label, and text
3. Store notes with source location information

### Phase 2: Note Collection
1. Implement plugin hooks to collect notes during build
2. Store notes with page context
3. Generate unique paragraph IDs for linking

### Phase 3: Aggregator Page
1. Create "Editor Notes" page automatically
2. Group notes by type
3. Add back-links to source paragraphs

### Phase 4: Highlighting & Navigation
1. Add paragraph ID anchors in HTML
2. Implement CSS for highlighting on navigation
3. Use :target pseudo-class or JavaScript

### Phase 5: Configuration
1. Add plugin config options:
   - Show/hide markers in source pages
   - Custom note types
   - Aggregator page location
   - Enable/disable highlighting

### Phase 6: Documentation
1. Add examples to docs site
2. Show each note type in action
3. Document configuration options

## Documentation Plan

### Files to Create/Update
1. `docs/source/quickstart.md` - Basic usage examples
2. `docs/source/features.md` - Detailed feature documentation
3. `docs/source/reference.md` - API reference
4. Add editor notes to docs themselves as examples

### Example Content
Include working examples of:
- Each note type (todo, ponder, improve, research)
- Labeled and unlabeled notes
- Multiple notes on one page
- Notes with different visibility settings
