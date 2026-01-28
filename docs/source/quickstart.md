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

Add the plugin to your `mkdocs.yml` configuration:

```yaml
plugins:
  - editor-notes
```


### Adding Editor Notes

Editor notes use a syntax similar to footnotes. You can add different types of notes.

**Note:** Labels (like `:expand-docs` or `:scalability`) are optional. You can use unlabeled notes or add specific
labels for better organization.


#### Todo Notes

Use todo notes to mark tasks that need to be completed:


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

Mark items that need research:


```markdown
We could use a different markdown parser.[^research:parser-options]

[^research:parser-options]: Research python-markdown alternatives
```


#### Custom Note Types

You can use any note type you want - they're automatically discovered:


```markdown
This might be a bug.[^bug:rendering-issue]

[^bug:rendering-issue]: Investigate why this renders incorrectly in Safari

I have a question about this.[^question:performance]

[^question:performance]: Will this approach scale?
```

Custom types like `bug` and `question` automatically appear in a "Custom Notes" section with ❗ emoji by default.


### Unlabeled Notes

Labels are optional. You can create notes without specific labels:

```markdown
This needs some thought.[^ponder]

[^ponder]: Should we consider a different approach here?
```

Without a label, the note is still tracked and displayed in the aggregator, but won't have a specific identifier
beyond its type.


### Viewing Editor Notes

All editor notes are automatically collected and aggregated into a single page. After building your site, navigate to
`/editor-notes/` to view all notes grouped by type with links back to their source locations.


## Running the Example

This repository includes a complete example MkDocs site that demonstrates the plugin's features in action. The example
site is a fictional "SpiceFlow API" documentation that showcases various types of editor notes throughout its pages.

### Prerequisites

Make sure you have the development dependencies installed:

```bash
uv sync
```

### Building the Example

To build the example site:

```bash
make example/build
```

This will generate the static site in the `example/site/` directory.

### Serving the Example

To serve the example site locally with live reload:

```bash
make example/serve
```

The example site will be available at `http://localhost:10001`. Navigate through the documentation to see inline editor
notes, then visit the `/editor-notes/` page to see all collected notes organized by type.

### What to Look For

The example demonstrates:

- Different note types (todo, ponder, improve, research, and custom types like urgent and idea)
- Labeled and unlabeled notes
- Custom emoji configuration
- The aggregator page with source links
- Marker visibility in rendered pages
