# Features


## Overview

mkdocs-editor-notes allows you to embed editorial notes directly in your markdown
documentation.[^todo:feature-comparison] These notes are collected and displayed on a dedicated aggregator page while
being optionally visible or hidden in the source pages themselves.

[^todo:feature-comparison]: Add comparison with other documentation note-taking approaches


## Note Types

The plugin supports four fixed note types with default emojis:[^bug:emoji-rendering]

[^bug:emoji-rendering]: Test emoji rendering across different browsers

- **✅ todo**: Tasks that need to be completed
- **💭 ponder**: Questions or considerations
- **⚡ improve**: Improvement suggestions
- **🔍 research**: Research tasks


### Custom Note Types

Any note type that is not one of the fixed types above is automatically treated as a custom type. Custom note types:

- Can be any lowercase text with hyphens (kebab-case)
- Are discovered automatically during aggregation (no need to configure)
- Appear in a "Custom Notes" section at the bottom of the aggregator page
- Use ❗ as the default emoji

You can specify emojis for any note type (fixed or custom) in your `mkdocs.yml`:

```yaml
plugins:
  - editor-notes:
      note_type_emojis:
        question: "❓"      # Custom type with custom emoji
        bug: "🐛"           # Custom type with custom emoji
        improve: "💡"       # Override default ⚡ for built-in type
```

**Example custom note usage:**

```markdown
Is this a bug?[^bug:rendering]

[^bug:rendering]: Check rendering in Safari

What about this?[^question:scaling]

[^question:scaling]: Will this scale to 1000 users?
```

Both `bug` and `question` are automatically recognized as custom types and will appear in the aggregator.


## Labeled Notes

Notes can have optional labels for better organization:[^ponder:label-format]

[^ponder:label-format]: Should labels support different formats or special characters?

```markdown
This paragraph has a labeled note.[^todo:fix-typo]

[^todo:fix-typo]: Correct the spelling error here
```

Labels make it easier to identify specific notes in the aggregator page and provide better context.


## Aggregator Page

All notes are automatically collected into a single aggregator page at `/editor-notes/`:

- Notes are grouped by type
- Each note shows its label (if provided)
- Links back to the source location
- Source paragraph is highlighted when navigating from aggregator

The aggregator page is generated during the build and can be accessed by navigating directly to `/editor-notes/` in
your browser.


## Paragraph Highlighting

When clicking a link from the aggregator page to a source paragraph, the paragraph is automatically highlighted using
CSS `:target` pseudo-class.[^improve:highlight-style]

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


### highlight_duration

Duration in milliseconds for the highlight to remain at full intensity before fading:

```yaml
plugins:
  - editor-notes:
      highlight_duration: 3000  # default (3 seconds)
```


### highlight_fade_duration

Duration in milliseconds for the highlight fade-out transition:

```yaml
plugins:
  - editor-notes:
      highlight_fade_duration: 2000  # default (2 seconds)
```

These options allow you to customize the paragraph highlighting behavior when navigating from the aggregator page to
source locations.


## Theme Integration

The plugin uses CSS custom properties that integrate with your MkDocs theme, especially the Material theme. The
following CSS variables can be customized:


### CSS Custom Properties

You can override these in your own CSS to customize the appearance:

```css
:root {
    /* Tooltip styling */
    --editor-note-tooltip-bg: var(--md-default-fg-color--light, #333);
    --editor-note-tooltip-fg: var(--md-default-bg-color, white);

    /* Highlight colors */
    --editor-note-highlight-bg: var(--md-accent-fg-color--transparent, rgba(255, 253, 231, 0.5));
    --editor-note-highlight-intense: var(--md-accent-fg-color, #ffeb3b);
}
```

The plugin automatically adapts to your theme's color scheme, including dark mode support when using the Material
theme.
