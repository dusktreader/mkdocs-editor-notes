"""MkDocs plugin for aggregating editor notes."""

import re
from pathlib import Path
from typing import Any, Callable, cast, override

import snick
from jinja2 import Environment
from mkdocs.plugins import get_plugin_logger

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
)
from mkdocs_editor_notes.note import EditorNote
from mkdocs_editor_notes.manager import EditorNotesManager

log = get_plugin_logger(__name__)

MdxConfigs = dict[str, dict[str, Any]]


class EditorNotesPluginConfig(Config):
    show_markers: Type[bool] = config_options.Type(bool, default=False)
    note_type_emojis: Type[dict[str, str]] = config_options.Type(dict, default={})
    aggregator_page: Type[str] = config_options.Type(str, default="editor-notes.md")
    highlight_duration: Type[int] = config_options.Type(int, default=3000)
    highlight_fade_duration: Type[int] = config_options.Type(int, default=2000)


class EditorNotesPlugin(BasePlugin[EditorNotesPluginConfig]):
    config: EditorNotesPluginConfig
    note_manager: EditorNotesManager

    def __init__(self) -> None:
        super().__init__()
        self.note_manager = EditorNotesManager()

    def is_fixed_type(self, note_type: str) -> bool:
        return note_type in FIXED_NOTE_TYPES

    def get_emoji(self, note_type: str) -> str:
        return self.config.note_type_emojis.get(note_type, FIXED_NOTE_TYPES.get(note_type, DEFAULT_CUSTOM_EMOJI))

    def get_ref_replacer(self, current_page: Page) -> Callable[[re.Match[str]], str] | str:
        if not self.config.show_markers:
            return ""

        aggregator_url = EditorNotesManager.get_aggregator_url(current_page, self.config.aggregator_page)

        def replacer(match: re.Match[str]):
            note_type = match.group("type")
            note_label = match.group("label")

            note: EditorNote | None = self.note_manager.get(note_type, note_label)
            if note:
                # Use single-line HTML to avoid breaking headings and other inline contexts
                # (unwrap removes newlines but preserves readability in source)
                return snick.unwrap(
                    f"""
                    <sup class="editor-note-marker">
                        <a href="{aggregator_url}#{note.agg_id}" title="{note.hover_text}">
                            {self.get_emoji(note_type)}
                        </a>
                    </sup>
                    """
                )

            return ""

        return replacer

    @override
    def on_files(  # pyright: ignore[reportIncompatibleMethodOverride] - MkDocs uses dynamic hook discovery
        self, files: Files, config: MkDocsConfig
    ) -> Files:
        """Add aggregator page to the files collection."""
        EditorNotesManager.ensure_aggregator_file(config.docs_dir, self.config.aggregator_page)
        EditorNotesManager.add_aggregator_to_files(
            files,
            self.config.aggregator_page,
            config.docs_dir,
            config.site_dir,
            config.use_directory_urls,
        )

        return files

    @override
    def on_page_markdown(  # pyright: ignore[reportIncompatibleMethodOverride] - MkDocs uses dynamic hook discovery
        self, markdown: str, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        if self.note_manager.is_aggregator_page(page, self.config.aggregator_page):
            return self.note_manager.handle_aggregator_page(page)

        return self.note_manager.process_page_markdown(markdown, page, self.get_ref_replacer(page))

    @override
    def on_env(  # pyright: ignore[reportIncompatibleMethodOverride] - MkDocs uses dynamic hook discovery
        self, env: Environment, config: MkDocsConfig, files: Files
    ) -> Environment:
        """After all pages are processed, regenerate aggregator page."""
        self.note_manager.regenerate_aggregator_content(
            self.get_emoji,
            config.markdown_extensions,
            cast(MdxConfigs, config.mdx_configs),
        )
        return env

    @override
    def on_post_page(  # pyright: ignore[reportIncompatibleMethodOverride] - MkDocs uses dynamic hook discovery
        self, output: str, page: Page, config: MkDocsConfig
    ) -> str:
        """Inject CSS and JavaScript."""

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
            // Editor Notes Configuration
            window.EDITOR_NOTES_CONFIG = {{
                highlightDuration: {self.config.highlight_duration},
                highlightFadeDuration: {self.config.highlight_fade_duration}
            }};
            </script>

            <script>
            {js_content}
            </script>
            """
        )

        if "</head>" in output:
            output = output.replace("</head>", f"{inject_content}</head>")

        return output
