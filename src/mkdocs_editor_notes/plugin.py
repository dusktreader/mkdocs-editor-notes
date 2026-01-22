"""MkDocs plugin for aggregating editor notes."""

import hashlib
import re
from pathlib import Path
from typing import Any, override

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.config_options import Type
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page

from mkdocs_editor_notes.constants import (
    FIXED_NOTE_TYPES,
    DEFAULT_CUSTOM_EMOJI,
    NOTE_DEF_PATTERN,
    NOTE_REF_PATTERN,
    CODE_BLOCK_PATTERN,
)
from mkdocs_editor_notes.models import EditorNote


class EditorNotesPluginConfig(Config):
    """Configuration for the EditorNotes plugin."""

    show_markers: Type[bool] = config_options.Type(bool, default=False)
    note_type_emojis: Type[dict[str, str]] = config_options.Type(dict, default={})
    aggregator_page: Type[str] = config_options.Type(str, default="editor-notes.md")


class EditorNotesPlugin(BasePlugin[EditorNotesPluginConfig]):
    """MkDocs plugin to aggregate editor notes from documentation."""

    config: EditorNotesPluginConfig
    notes: list[EditorNote]
    note_type_emojis: dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self.notes = []
        self.note_type_emojis = {}

    @override
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Setup configuration and emoji mappings."""
        self.note_type_emojis = {
            **FIXED_NOTE_TYPES,
            **self.config.note_type_emojis,
        }

        docs_dir = Path(config["docs_dir"])
        aggregator_file = docs_dir / self.config.aggregator_page
        if not aggregator_file.exists():
            aggregator_file.write_text("# Editor Notes\n\nThis page will be generated during the build.\n")

        return config

    def is_fixed_type(self, note_type: str) -> bool:
        return note_type in FIXED_NOTE_TYPES

    def get_emoji(self, note_type: str) -> str:
        return self.note_type_emojis.get(note_type, DEFAULT_CUSTOM_EMOJI)

    @override
    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str | None:
        note_to_paragraph = {}
        ref_counter = 0

        # Protect code blocks by temporarily replacing them
        code_blocks: list[str] = []

        def save_code_block(match: re.Match[str]) -> str:
            code_blocks.append(match.group(0))
            return f"<<<CODE_BLOCK_{len(code_blocks) - 1}>>>"

        markdown_protected = CODE_BLOCK_PATTERN.sub(save_code_block, markdown)

        # Find all note definitions and extract them
        for match in NOTE_DEF_PATTERN.finditer(markdown_protected):
            note_type = match.group("type")
            note_label = match.group("label")
            note_text = match.group("text").strip()

            # Create EditorNote object (we'll set paragraph_id later)
            note = EditorNote(
                note_type=note_type,
                label=note_label,
                text=note_text,
                source_page=page.file.src_uri,
            )

            note_to_paragraph[note.note_key] = note

        # Process line by line to find note references and add anchors
        lines = markdown_protected.split("\n")
        processed_lines = []

        for line in lines:
            ref_match = NOTE_REF_PATTERN.search(line)
            if ref_match:
                note_type = ref_match.group("type")
                note_label = ref_match.group("label")
                note_key = f"{note_type}:{note_label}"

                # Generate paragraph ID for this note
                ref_counter += 1
                ref_id = f"editor-note-para-{ref_counter}"

                # Set the paragraph ID and line number for the note
                if note_key in note_to_paragraph:
                    note_to_paragraph[note_key].paragraph_id = ref_id
                    # Store line number (approximate, based on position in file)
                    note_to_paragraph[note_key].line_number = len(processed_lines) + 1

                # Add anchor span at the start of the line
                if "<span id=" not in line:
                    line = f'<span id="{ref_id}"></span>{line}'

            processed_lines.append(line)

        markdown = "\n".join(processed_lines)

        # Add notes to collection
        for note in note_to_paragraph.values():
            if note.paragraph_id:  # Only add if we found a reference
                self.notes.append(note)

        # Remove note definitions from markdown (they can span multiple lines)
        markdown = NOTE_DEF_PATTERN.sub("", markdown)
        # Clean up any extra newlines left behind
        markdown = re.sub(r"\n\n\n+", "\n\n", markdown)

        # Remove note references if show_markers is False
        if not self.config["show_markers"]:
            markdown = NOTE_REF_PATTERN.sub("", markdown)
        else:
            # Replace with clickable markers linking to aggregator
            def replace_ref(match):
                note_type = match.group("type")
                note_label = match.group("label")
                note_key = f"{note_type}:{note_label}"

                # Generate a unique ID for this note for linking to aggregator
                if note_key in note_to_paragraph and note_to_paragraph[note_key].paragraph_id:
                    note_id = f"note-{note_to_paragraph[note_key].paragraph_id}"
                    paragraph_id = note_to_paragraph[note_key].paragraph_id
                    # Use matching emoji for this note type
                    marker_symbol = self.get_emoji(note_type)
                    # Create hover text with type and label
                    hover_text = f"{note_type}: {note_label}"
                    # Link to aggregator page using markdown format
                    aggregator_path = self.config.get("aggregator_page", "editor-notes.md")
                    # Use markdown link format which MkDocs will handle correctly
                    return f'<sup class="editor-note-marker"><a href="{aggregator_path}#{note_id}" title="{hover_text}">{marker_symbol}</a></sup>'
                return ""

            markdown = NOTE_REF_PATTERN.sub(replace_ref, markdown)

        # Restore code blocks
        for i, code_block in enumerate(code_blocks):
            markdown = markdown.replace(f"<<<CODE_BLOCK_{i}>>>", code_block)

        return markdown

    @override
    def on_env(self, env, config: MkDocsConfig, files: Files):
        """Write aggregator markdown file after pages are processed but before rendering."""
        # This runs after on_page_markdown for all pages, so we have all notes
        if self.notes:
            # Generate the aggregator page as markdown
            aggregator_md = self._generate_aggregator_markdown()

            # Write markdown file to docs directory
            docs_dir = Path(config["docs_dir"])
            aggregator_file = docs_dir / self.config["aggregator_page"]
            aggregator_file.write_text(aggregator_md)

        return env

    @override
    def on_post_page(self, output: str, page, config: MkDocsConfig) -> str:
        """Inject CSS and fix marker links."""
        # Fix marker links to point to proper URLs (remove .md extension)
        aggregator_page = self.config.get("aggregator_page", "editor-notes.md")
        aggregator_url = aggregator_page.replace(".md", "/")
        output = output.replace(f'href="{aggregator_page}#', f'href="{aggregator_url}#')

        # Load CSS and JS from static files
        static_dir = Path(__file__).parent / "static"
        css_file = static_dir / "editor-notes.css"
        js_file = static_dir / "editor-notes.js"

        css_content = css_file.read_text()
        js_content = js_file.read_text()

        inject_content = f"""
<style>
{css_content}
</style>
<script>
{js_content}
</script>
"""
        # Inject before </head>
        if "</head>" in output:
            output = output.replace("</head>", f"{inject_content}</head>")
        return output

    @override
    def on_post_build(self, config: MkDocsConfig) -> None:
        """Cleanup after build."""
        pass

    def _generate_aggregator_markdown(self) -> str:
        """Generate markdown content for the aggregator page."""
        # Group notes by type
        notes_by_type: dict[str, list[EditorNote]] = {}
        for note in self.notes:
            notes_by_type.setdefault(note.note_type, []).append(note)

        # Separate fixed and custom types
        fixed_types = [t for t in sorted(notes_by_type.keys()) if self.is_fixed_type(t)]
        custom_types = [t for t in sorted(notes_by_type.keys()) if not self.is_fixed_type(t)]

        # Build markdown content with front matter to configure TOC
        md_parts = [
            "---",
            "toc_depth: 2",
            "---",
            "",
            "# Editor Notes",
            "",
            "This page aggregates all editor notes found throughout the documentation.",
            "",
        ]

        # Add fixed note types first
        for note_type in fixed_types:
            notes = notes_by_type[note_type]
            emoji = self.get_emoji(note_type)
            md_parts.append(f"## {emoji} {note_type.capitalize()}")
            md_parts.append("")

            for note in notes:
                # Add anchor for linking from markers
                note_id = f"note-{note.paragraph_id}"

                # Format identifier as H4 with source link
                identifier = note.label
                source_file = note.source_page
                line_num = note.line_number or 0

                # Convert source file path to relative URL
                # Both aggregator and source pages are in the same directory
                source_url = source_file.replace(".md", "/")
                link_path = f"{source_url}#{note.paragraph_id}"

                # Use pure HTML for the entry
                md_parts.append(f'<div class="editor-note-entry">')
                md_parts.append(f'<span id="{note_id}"></span>')
                md_parts.append(f'<h4>{identifier} (<a href="{link_path}">{source_file}:{line_num}</a>)</h4>')
                md_parts.append(f"<p>{note.text}</p>")
                md_parts.append("</div>")
                md_parts.append("")

            md_parts.append("")

        # Add custom note types at the bottom
        if custom_types:
            md_parts.append("## Custom Notes")
            md_parts.append("")

            for note_type in custom_types:
                notes = notes_by_type[note_type]
                emoji = self.get_emoji(note_type)
                md_parts.append(f"### {emoji} {note_type}")
                md_parts.append("")

                for note in notes:
                    # Add anchor for linking from markers
                    note_id = f"note-{note.paragraph_id}"

                    # Format identifier as H4 with source link
                    identifier = note.label
                    source_file = note.source_page
                    line_num = note.line_number or 0

                    # Convert source file path to relative URL
                    # Both aggregator and source pages are in the same directory
                    source_url = source_file.replace(".md", "/")
                    link_path = f"{source_url}#{note.paragraph_id}"

                    # Use pure HTML for the entry
                    md_parts.append(f'<div class="editor-note-entry">')
                    md_parts.append(f'<span id="{note_id}"></span>')
                    md_parts.append(f'<h4>{identifier} (<a href="{link_path}">{source_file}:{line_num}</a>)</h4>')
                    md_parts.append(f"<p>{note.text}</p>")
                    md_parts.append("</div>")
                    md_parts.append("")

                md_parts.append("")

        return "\n".join(md_parts)

    def _get_inline_css(self) -> str:
        """Get inline CSS for the aggregator page."""
        return """
.editor-note-item {
    margin: 15px 0;
    padding: 12px;
    border-left: 4px solid #2196F3;
    background: #f5f9ff;
    border-radius: 4px;
}
.editor-note-label {
    font-weight: 600;
    color: #1976D2;
    margin-bottom: 4px;
    font-size: 1.1em;
}
.editor-note-text {
    margin: 8px 0;
    line-height: 1.6;
}
.editor-note-source {
    font-size: 0.9em;
    color: #666;
    margin-top: 8px;
}
.editor-note-source a {
    color: #1976D2;
    text-decoration: none;
}
.editor-note-source a:hover {
    text-decoration: underline;
}
:target {
    background-color: #ffffcc !important;
    animation: highlight-fade 3s ease-out;
    padding: 8px;
    margin: -8px;
    border-radius: 4px;
}
@keyframes highlight-fade {
    from { background-color: #ffff99; }
    50% { background-color: #ffffcc; }
    to { background-color: transparent; }
}
.editor-note-marker {
    font-size: 0.75em;
    color: #1976D2;
    margin-left: 2px;
    padding: 2px 4px;
    background: #e3f2fd;
    border-radius: 3px;
}
"""

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML (simple implementation)."""
        import re

        html = markdown_text

        # Convert headers
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Convert paragraphs (simple)
        lines = html.split("\n")
        result = []
        in_div = False

        for line in lines:
            if '<div class="editor-note-item">' in line:
                in_div = True
                result.append(line)
            elif "</div>" in line and in_div:
                result.append(line)
                # Check if this closes the note item
                if line.strip() == "</div>":
                    in_div = False
            elif line.startswith("<"):
                result.append(line)
            elif line.strip() and not in_div:
                result.append(f"<p>{line}</p>")
            else:
                result.append(line)

        return "\n".join(result)
