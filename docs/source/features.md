# Features

## Overview

mkdocs-editor-notes allows you to embed editorial notes directly in your markdown documentation.[^todo:feature-comparison] These notes are collected and displayed on a dedicated aggregator page while being optionally visible or hidden in the source pages themselves.

[^todo:feature-comparison]: Add comparison with other documentation note-taking approaches

## Note Types

The plugin supports multiple note types out of the box:

- **todo**: Tasks that need to be completed
- **ponder**: Questions or considerations
- **improve**: Improvement suggestions  
- **research**: Research tasks

Custom note types can be configured in your `mkdocs.yml`.[^improve:custom-types]

[^improve:custom-types]: Add example of how to configure custom note types

## Labeled Notes

Notes can have optional labels for better organization:[^ponder:label-format]

[^ponder:label-format]: Should labels support different formats or special characters?

```markdown
This paragraph has a labeled note.[^todo:fix-typo]

[^todo:fix-typo]: Correct the spelling error here
```

Labels make it easier to identify specific notes in the aggregator page and provide better context.

## Aggregator Page

All notes are automatically collected into a single aggregator page:

- Notes are grouped by type
- Each note shows its label (if provided)
- Links back to the source location  
- Source paragraph is highlighted when navigating from aggregator[^research:highlight-methods]

[^research:highlight-methods]: Research best practices for scroll-to-highlight UX

## Paragraph Highlighting

When clicking a link from the aggregator page to a source paragraph, the paragraph is automatically highlighted using CSS `:target` pseudo-class.[^improve:highlight-style]

[^improve:highlight-style]: Make highlighting style configurable via CSS variables

The highlight fades out after a few seconds for a better user experience.

## Configuration Options

### show_markers

Control whether editor note markers are visible in the rendered pages:

```yaml
plugins:
  - editor-notes:
      show_markers: false  # default
```

When `false`, notes are invisible in source pages. When `true`, notes appear as superscript markers.

### note_types

Define which note types are recognized:

```yaml
plugins:
  - editor-notes:
      note_types:
        - todo
        - ponder  
        - improve
        - research
        - custom
```

### aggregator_page

Customize the location of the aggregator page:[^todo:nav-integration]

[^todo:nav-integration]: Auto-add aggregator page to navigation

```yaml
plugins:
  - editor-notes:
      aggregator_page: "notes/editor-notes.md"
```

### enable_highlighting

Enable or disable paragraph highlighting:

```yaml
plugins:
  - editor-notes:
      enable_highlighting: true  # default
```
