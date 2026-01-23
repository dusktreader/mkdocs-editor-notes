"""MkDocs plugin for aggregating editor notes."""

import re
from pathlib import Path
from typing import Callable, override

import snick

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.config_options import Type
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
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
    show_markers: Type[bool] = config_options.Type(bool, default=False)
    note_type_emojis: Type[dict[str, str]] = config_options.Type(dict, default={})
    aggregator_page: Type[str] = config_options.Type(str, default="editor-notes.md")


class EditorNotesPlugin(BasePlugin[EditorNotesPluginConfig]):
    config: EditorNotesPluginConfig
    note_map: dict[str, EditorNote]
    note_type_emojis: dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self.note_map = {}
        self.note_type_emojis = {}

    @property
    def notes(self) -> list[EditorNote]:
        """Get all notes as a list."""
        return list(self.note_map.values())

    @notes.setter
    def notes(self, value: list[EditorNote]) -> None:
        """Set notes from a list."""
        self.note_map = {note.note_key: note for note in value}

    @override
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        self.note_type_emojis = {
            **FIXED_NOTE_TYPES,
            **self.config.note_type_emojis,
        }

        docs_dir = Path(config["docs_dir"])
        aggregator_file = docs_dir / self.config.aggregator_page
        if not aggregator_file.exists():
            aggregator_file.write_text(
                snick.dedent(
                    """
                    # Editor Notes

                    This page will be generated during the build.
                    """
                )
            )

        return config

    def is_fixed_type(self, note_type: str) -> bool:
        return note_type in FIXED_NOTE_TYPES

    def get_emoji(self, note_type: str) -> str:
        return self.note_type_emojis.get(note_type, DEFAULT_CUSTOM_EMOJI)

    @staticmethod
    def _protect_code_blocks(markdown: str, code_blocks: list[str]) -> str:
        """Protect code blocks by replacing them with placeholders."""

        def save_code_block(match: re.Match[str]) -> str:
            code_blocks.append(match.group(0))
            return f"<<<CODE_BLOCK_{len(code_blocks) - 1}>>>"

        return CODE_BLOCK_PATTERN.sub(save_code_block, markdown)

    @staticmethod
    def _restore_code_blocks(markdown: str, code_blocks: list[str]) -> str:
        for i, code_block in enumerate(code_blocks):
            markdown = markdown.replace(f"<<<CODE_BLOCK_{i}>>>", code_block)

        return markdown

    def _find_note_defs(self, markdown: str, page: Page):
        for match in NOTE_DEF_PATTERN.finditer(markdown):
            note_type = match.group("type")
            note_label = match.group("label")
            note_text = match.group("text").strip()

            note = EditorNote(
                note_type=note_type,
                label=note_label,
                text=note_text,
                source_page=Path(page.file.src_uri),
            )

            self.note_map[note.note_key] = note

    def _find_note_refs(self, markdown: str) -> str:
        ref_counter = 0
        lines = markdown.split("\n")
        for line_number, line in enumerate(lines):
            ref_match = NOTE_REF_PATTERN.search(line)
            if not ref_match:
                continue

            note_type = ref_match.group("type")
            note_label = ref_match.group("label")
            note_key = f"{note_type}:{note_label}"

            ref_counter += 1
            ref_id = f"editor-note-para-{ref_counter}"

            note: EditorNote | None = self.note_map.get(note_key)
            if note:
                note.ref_id = ref_id
                # WARN: this might be approximate based on the position in the file
                note.line_number = line_number + 1
            # TODO: log a warning if note isn't found? Throw an exception?

            lines[line_number] = f'<span id="{ref_id}"></span>{line}'

        return "\n".join(lines)

    def get_ref_replacer(self) -> Callable[[re.Match[str]], str] | str:
        if not self.config.show_markers:
            return ""

        def replacer(match: re.Match[str]):
            note_type = match.group("type")
            note_label = match.group("label")
            note_key = f"{note_type}:{note_label}"

            note: EditorNote | None = self.note_map.get(note_key)
            if not note or not note.ref_id:
                # TODO: should we throw an error or log one here?
                return ""

            # TODO: should this be using the note's node_id property?
            return snick.dedent(
                f"""
                <sup class="editor-note-marker">
                    <a href="{self.config.aggregator_page}#note-{note.ref_id}" title="{note.hover_text}">
                    {self.get_emoji(note_type)},
                    </a>
                </sup>
                """
            )

        return replacer

    @override
    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str | None:
        code_blocks: list[str] = []
        markdown = self._protect_code_blocks(markdown, code_blocks)
        self._find_note_defs(markdown, page)
        markdown = self._find_note_refs(markdown)
        markdown = NOTE_DEF_PATTERN.sub("", markdown)
        markdown = re.sub(r"\n\n\n+", "\n\n", markdown)
        markdown = NOTE_REF_PATTERN.sub(self.get_ref_replacer(), markdown)
        markdown = self._restore_code_blocks(markdown, code_blocks)
        return markdown

    @override
    def on_env(self, env, config: MkDocsConfig, files: Files):
        """Write aggregator markdown file after pages are processed but before rendering."""
        self.build_aggregator_markdown(Path(config.docs_dir))
        return env

    @override
    def on_post_page(self, output: str, page, config: MkDocsConfig) -> str:
        """Inject CSS and fix marker links."""
        # Fix marker links to point to proper URLs (remove .md extension)
        aggregator_page = self.config.aggregator_page
        aggregator_url = aggregator_page.stem
        output = output.replace(f'href="{aggregator_page}#', f'href="{aggregator_url}#')

        static_dir = Path(__file__).parent / "static"
        css_file = static_dir / "editor-notes.css"
        js_file = static_dir / "editor-notes.js"

        css_content = css_file.read_text()
        js_content = js_file.read_text()

        inject_content = snick.dedent(
            f"""
            <style>
            {css_content}
            </style>
            <script>
            {js_content}
            </script>
            """
        )

        # Inject before </head>
        if "</head>" in output:
            output = output.replace("</head>", f"{inject_content}</head>")
        return output

    def build_aggregator_markdown(self, docs_dir: Path) -> None:
        if not self.note_map:
            # TODO: warn?
            return

        type_map: dict[str, list[EditorNote]] = {}
        fixed_types: set[str] = set()
        custom_types: set[str] = set()
        for note in self.note_map.values():
            type_map.setdefault(note.note_type, []).append(note)
            if self.is_fixed_type(note.note_type):
                fixed_types.add(note.note_type)
            else:
                custom_types.add(note.note_type)

        md_parts = snick.Conjoiner()
        md_parts.add(
            """
            ---
            toc_depth: 2
            ---

            # Editor Notes

            This page aggregates all editor notes found throughout the documentation.
            """,
            blanks_after=2,
        )

        for note_type in fixed_types:
            notes = type_map[note_type]
            emoji = self.get_emoji(note_type)
            md_parts.add(f"## {emoji} {note_type.capitalize()}", blanks_after=1)

            for note in notes:
                note_id = f"note-{note.ref_id}"
                md_parts.add(
                    """
                    <div class="editor-note-entry">
                        <span id="{note_id}"></span>
                        <h4>
                            {note.label} (
                            <a href="{note.source_page.stem}#{note.ref_id}">
                                {note.source_page}:{note.line_number}
                            </a>
                            )
                        </h4>
                        <p>{note.text}</p>
                    </div>
                    """,
                    blanks_before=1,
                )

        if custom_types:
            md_parts.add("## Custom Notes", blanks_before=1, blanks_after=1)

            for note_type in custom_types:
                notes = type_map[note_type]
                emoji = self.get_emoji(note_type)
                md_parts.add(f"### {emoji} {note_type}", blanks_before=1, blanks_after=1)

                for note in notes:
                    note_id = f"note-{note.ref_id}"
                    link_path = f"{note.source_page.stem}#{note.ref_id}"

                    md_parts.add(
                        f"""
                        <div class="editor-note-entry">
                            <span id="{note_id}"></span>
                            <h4>{note.label} (<a href="{link_path}">{note.source_page}:{note.line_number}</a>)</h4>
                            <p>{note.text}</p>
                        </div>
                        """,
                        blanks_before=1,
                    )

        aggregator_file = docs_dir / self.config.aggregator_page
        aggregator_file.write_text(str(md_parts))

    def _get_inline_css(self) -> str:
        """Get inline CSS for the aggregator page."""
        return snick.dedent(
            """
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
        )

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
