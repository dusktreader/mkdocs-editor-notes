# Quickstart

## Requirements

* Python 3.12 to 3.14


## Installation

### Install from pypi:

This will install the latest release from pypi via pip:

```bash
pip install mkdocs-editor-notes
```


## Using

### Basic Setup

Add the plugin to your `mkdocs.yml` configuration:[^todo:verify-config]

[^todo:verify-config]: Make sure the configuration example is complete

```yaml
plugins:
  - editor-notes
```

### Adding Editor Notes

Editor notes use a syntax similar to footnotes.[^ponder:syntax-alternative] You can add different types of notes:

[^ponder:syntax-alternative]: Should we support alternative syntax formats?

#### Todo Notes

Use todo notes to mark tasks that need to be completed:[^improve:better-examples]

[^improve:better-examples]: Add more diverse examples

```markdown
This feature needs more documentation.[^todo:expand-docs]

[^todo:expand-docs]: Add examples and API reference
```

#### Ponder Notes

Use ponder notes for questions or things to think about:[^ponder]

[^ponder]: Is this the best name for this type of note?

```markdown
This approach might not scale well.[^ponder:scalability]

[^ponder:scalability]: Should we benchmark this with larger datasets?
```

#### Improve Notes

Mark areas for improvement:

```markdown
The error handling here is basic.[^improve:error-handling]

[^improve:error-handling]: Add specific error types and better messages
```

#### Research Notes

Mark items that need research:[^research:alternatives]

[^research:alternatives]: Look into other mkdocs plugins for similar functionality

```markdown
We could use a different markdown parser.[^research:parser-options]

[^research:parser-options]: Research python-markdown alternatives
```

#### Custom Note Types

You can use any note type you want - they're automatically discovered:[^question:custom-examples]

[^question:custom-examples]: Should we add more custom type examples?

```markdown
This might be a bug.[^bug:rendering-issue]

[^bug:rendering-issue]: Investigate why this renders incorrectly in Safari

I have a question about this.[^question:performance]

[^question:performance]: Will this approach scale?
```

Custom types like `bug` and `question` automatically appear in a "Custom Notes" section with ❗ emoji by default.

### Viewing Editor Notes

All editor notes are automatically collected and aggregated into a single page. After building your site, navigate to `/editor-notes/` to view all notes grouped by type with links back to their source locations.
