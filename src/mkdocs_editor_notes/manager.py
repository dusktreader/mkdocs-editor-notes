from collections.abc import Callable, Generator
from enum import StrEnum, auto
from pathlib import Path
import re

from markdown import Markdown
import snick
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from mkdocs_editor_notes.constants import NOTE_DEF_PATTERN, NOTE_REF_PATTERN, CODE_BLOCK_PATTERN
from mkdocs_editor_notes.note import EditorNote

log = get_plugin_logger(__name__)


class LineType(StrEnum):
    """Types of markdown lines for anchor placement."""

    HEADING = auto()
    UNORDERED_LIST = auto()
    ORDERED_LIST = auto()
    REGULAR = auto()


class EditorNotesManager:
    """Manager for collecting, parsing, and aggregating editor notes."""

    notes_map: dict[str, EditorNote]
    type_map: dict[str, set[str]]
    aggregator_page: Page | None

    def __init__(self):
        self.notes_map = {}
        self.type_map = {}
        self.aggregator_page = None

    def __iter__(self) -> Generator[EditorNote, None, None]:
        yield from self.notes_map.values()

    @staticmethod
    def key(note_type: str, note_label: str) -> str:
        return f"{note_type}:{note_label}"

    @staticmethod
    def classify_line(line: str) -> LineType:
        """Classify a markdown line by its type for anchor placement.

        Args:
            line: The markdown line to classify

        Returns:
            LineType enum indicating the line type
        """
        stripped = line.lstrip()

        match stripped:
            case "":
                return LineType.REGULAR
            case str() if stripped.startswith("#"):
                return LineType.HEADING
            case str() if stripped.startswith(("-", "*", "+")):
                return LineType.UNORDERED_LIST
            case str() if stripped[0].isdigit() and "." in stripped[:4]:
                return LineType.ORDERED_LIST
            case _:
                return LineType.REGULAR

    @staticmethod
    def insert_anchor_in_heading(line: str, anchor_span: str) -> str:
        """Insert anchor span after heading markers in a markdown heading.

        Args:
            line: The markdown line (e.g., "## My Heading[^note]")
            anchor_span: The HTML span to insert (e.g., '<span id="ref-note-id"></span>')

        Returns:
            Modified line with anchor placed after heading markers
        """
        stripped = line.lstrip()
        heading_markers = ""
        remaining = stripped
        while remaining.startswith("#"):
            heading_markers += "#"
            remaining = remaining[1:]
        leading_space = line[: len(line) - len(stripped)]
        return f"{leading_space}{heading_markers}{anchor_span}{remaining}"

    @staticmethod
    def insert_anchor_in_unordered_list(line: str, anchor_span: str) -> str:
        """Insert anchor span after list marker in an unordered list item.

        Args:
            line: The markdown line (e.g., "- Item text[^note]")
            anchor_span: The HTML span to insert

        Returns:
            Modified line with anchor placed after list marker
        """
        stripped = line.lstrip()
        list_marker = stripped[0]
        remaining = stripped[1:].lstrip()
        leading_space = line[: len(line) - len(stripped)]
        return f"{leading_space}{list_marker} {anchor_span}{remaining}"

    @staticmethod
    def insert_anchor_in_ordered_list(line: str, anchor_span: str) -> str:
        """Insert anchor span after number and period in an ordered list item.

        Args:
            line: The markdown line (e.g., "1. Item text[^note]")
            anchor_span: The HTML span to insert

        Returns:
            Modified line with anchor placed after number and period, or fallback to beginning
        """
        stripped = line.lstrip()
        dot_pos = stripped.find(".")
        if dot_pos > 0:
            list_marker = stripped[: dot_pos + 1]
            remaining = stripped[dot_pos + 1 :].lstrip()
            leading_space = line[: len(line) - len(stripped)]
            return f"{leading_space}{list_marker} {anchor_span}{remaining}"
        else:
            # Fallback if no period found
            return f"{anchor_span}{line}"

    @staticmethod
    def insert_anchor_at_beginning(line: str, anchor_span: str) -> str:
        """Insert anchor span at the beginning of a regular line.

        Args:
            line: The markdown line
            anchor_span: The HTML span to insert

        Returns:
            Modified line with anchor at beginning
        """
        return f"{anchor_span}{line}"

    @staticmethod
    def insert_anchor_in_line(line: str, anchor_span: str) -> str:
        """Insert anchor span in a line based on its markdown type.

        Uses structural pattern matching to handle different line types appropriately.

        Args:
            line: The markdown line
            anchor_span: The HTML span to insert

        Returns:
            Modified line with anchor placed appropriately for the line type
        """
        line_type = EditorNotesManager.classify_line(line)

        match line_type:
            case LineType.HEADING:
                return EditorNotesManager.insert_anchor_in_heading(line, anchor_span)
            case LineType.UNORDERED_LIST:
                return EditorNotesManager.insert_anchor_in_unordered_list(line, anchor_span)
            case LineType.ORDERED_LIST:
                return EditorNotesManager.insert_anchor_in_ordered_list(line, anchor_span)
            case LineType.REGULAR:
                return EditorNotesManager.insert_anchor_at_beginning(line, anchor_span)
            case _:
                # Fallback (should never reach here)
                return EditorNotesManager.insert_anchor_at_beginning(line, anchor_span)

    @property
    def empty(self) -> bool:
        return len(self.notes_map) == 0

    @property
    def types(self) -> Generator[str, None, None]:
        yield from self.type_map.keys()

    def add(self, note: EditorNote):
        note_key = self.key(note.note_type, note.label)
        if note_key in self.notes_map:
            raise ValueError(
                snick.conjoin(
                    f"Note with key '{note_key}' already exists. ",
                    "Each note must have a unique combination of type and label.",
                )
            )
        self.notes_map[note_key] = note
        self.type_map.setdefault(note.note_type, set()).add(note_key)

    def get(self, note_type: str, note_label: str) -> EditorNote | None:
        note_key = self.key(note_type, note_label)
        return self.notes_map.get(note_key)

    def parse_note_definitions(self, markdown: str, page: Page) -> None:
        """
        Parse note definitions from markdown and add them to the manager.

        Note definitions follow the pattern: [^type:label]: Note text

        Args:
            markdown: The markdown content to parse
            page: The MkDocs page being processed
        """
        for match in NOTE_DEF_PATTERN.finditer(markdown):
            note_type = match.group("type")
            note_label = match.group("label")
            note_text = match.group("text").strip()

            note = EditorNote(
                note_type=note_type,
                label=note_label,
                text=note_text,
                source_page=Path(page.file.src_uri),
                source_url=page.url or "",
            )

            self.add(note)

    def parse_note_references(self, markdown: str, page: Page) -> str:
        """
        Parse note references from markdown and insert anchor spans.

        Note references follow the pattern: [^type:label]

        This method:
        1. Finds all note references in the markdown
        2. Updates the line_number for each referenced note
        3. Inserts anchor spans at the reference locations
        4. Logs warnings for undefined references

        Args:
            markdown: The markdown content to parse
            page: The MkDocs page being processed

        Returns:
            Updated markdown with anchor spans inserted
        """
        lines = markdown.split("\n")
        for line_number, line in enumerate(lines):
            ref_match = NOTE_REF_PATTERN.search(line)
            if not ref_match:
                continue

            note_type = ref_match.group("type")
            note_label = ref_match.group("label")
            note: EditorNote | None = self.get(note_type, note_label)

            if note:
                # WARN: this might be approximate based on the position in the file
                note.line_number = line_number + 1

                anchor_span = f'<span id="{note.ref_id}"></span>'
                lines[line_number] = self.insert_anchor_in_line(line, anchor_span)
            else:
                log.warning(
                    f"Undefined note reference '[^{note_type}:{note_label}]' in {page.file.src_uri}:{line_number + 1}"
                )

        return "\n".join(lines)

    def process_page_markdown(
        self, markdown: str, page: Page, ref_replacer: Callable[[re.Match[str]], str] | str
    ) -> str:
        """
        Process a page's markdown to extract and replace editor notes.

        This method orchestrates the complete note processing workflow:
        1. Protects code blocks from being processed
        2. Parses note definitions and adds them to the manager
        3. Removes note definitions from the markdown
        4. Parses note references and inserts anchor spans
        5. Replaces note references with formatted links (if ref_replacer is a function)
        6. Restores protected code blocks

        Args:
            markdown: The markdown content to process
            page: The MkDocs page being processed
            ref_replacer: Function to replace note references with formatted links,
                         or empty string to remove references without replacement

        Returns:
            Processed markdown with notes extracted and references replaced
        """
        code_blocks: list[str] = []
        markdown = self.protect_code_blocks(markdown, code_blocks)
        self.parse_note_definitions(markdown, page)
        markdown = NOTE_DEF_PATTERN.sub("", markdown)
        markdown = re.sub(r"\n\n\n+", "\n\n", markdown)
        markdown = self.parse_note_references(markdown, page)
        markdown = NOTE_REF_PATTERN.sub(ref_replacer, markdown)
        markdown = self.restore_code_blocks(markdown, code_blocks)
        return markdown

    def is_aggregator_page(self, page: Page, aggregator_page_path: str) -> bool:
        """
        Check if the given page is the aggregator page.

        Args:
            page: The MkDocs page to check
            aggregator_page_path: The configured aggregator page path

        Returns:
            True if this is the aggregator page, False otherwise
        """
        return page.file.src_uri == aggregator_page_path

    def handle_aggregator_page(self, page: Page) -> str:
        """
        Handle processing of the aggregator page itself.

        Stores a reference to the aggregator page for later regeneration
        and returns placeholder content.

        Args:
            page: The aggregator page being processed

        Returns:
            Placeholder markdown content for the aggregator page
        """
        self.aggregator_page = page
        return "# Editor Notes\n\nGenerating..."

    @staticmethod
    def ensure_aggregator_file(docs_dir: str, aggregator_page: str) -> None:
        """
        Ensure the aggregator file exists with placeholder content.

        Creates the aggregator markdown file if it doesn't exist yet.
        This is needed so MkDocs can discover and process the file.

        Args:
            docs_dir: The MkDocs docs directory path
            aggregator_page: The aggregator page path relative to docs_dir
        """
        file_path = Path(docs_dir) / aggregator_page
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("# Editor Notes\n\nLoading...\n")

    @staticmethod
    def add_aggregator_to_files(
        files: Files, aggregator_page: str, docs_dir: str, site_dir: str, use_directory_urls: bool
    ) -> None:
        """
        Add the aggregator file to MkDocs files collection if not already present.

        Mkdocs may auto-discover the file, but this ensures it's included.

        Args:
            files: MkDocs Files collection to add to
            aggregator_page: The aggregator page path relative to docs_dir
            docs_dir: The MkDocs docs directory path
            site_dir: The MkDocs site directory path
            use_directory_urls: Whether MkDocs uses directory URLs
        """
        if not any(f.src_uri == aggregator_page for f in files):
            aggregator_file = File(
                path=aggregator_page,
                src_dir=docs_dir,
                dest_dir=site_dir,
                use_directory_urls=use_directory_urls,
            )
            files.append(aggregator_file)

    def build_aggregator_markdown(self, emoji_getter: Callable[[str], str]) -> str:
        """
        Build the markdown content for the aggregator page.

        Args:
            emoji_getter: Function to get emoji for a note type (note_type: str) -> str

        Returns:
            Complete markdown for the aggregator page
        """
        if self.empty:
            return ""

        md_parts = snick.Conjoiner()
        md_parts.add(
            """
            # Editor Notes

            This page aggregates all editor notes found throughout the documentation.
            """,
        )

        for note_type in sorted(self.types):
            emoji = emoji_getter(note_type)
            md_parts.add(f"## {emoji} {note_type}", blanks_before=2)

            for note in self:
                if note.note_type != note_type:
                    continue
                md_parts.add(
                    f"""
                    <div class="editor-note-entry">
                        <span id="{note.agg_id}"></span>
                        <h4>
                            {note.label} (<a href="{note.ref_url}">{note.source_page}:{note.line_number}</a>)
                        </h4>
                        <p>{note.text}</p>
                    </div>
                    """,
                    blanks_before=1,
                )

        return str(md_parts)

    def regenerate_aggregator_content(
        self, emoji_getter: Callable[[str], str], markdown_extensions: list[str], mdx_configs: dict | None
    ) -> None:
        """
        Regenerate the aggregator page content after all pages are processed.

        This method should be called after all pages have been processed to
        generate the final aggregator page content with all collected notes.

        Args:
            emoji_getter: Function to get emoji for a note type (note_type: str) -> str
            markdown_extensions: List of MkDocs markdown extensions
            mdx_configs: MkDocs extension configurations
        """
        if self.aggregator_page is None:
            return

        markdown = self.build_aggregator_markdown(emoji_getter)
        md = Markdown(extensions=markdown_extensions, extension_configs=mdx_configs)
        self.aggregator_page.content = md.convert(markdown)  # type: ignore

    @staticmethod
    def get_aggregator_url(current_page: Page, aggregator_page: str) -> str:
        """
        Calculate the relative URL from current page to the aggregator page.

        Args:
            current_page: The current MkDocs page being processed
            aggregator_page: The aggregator page path (e.g., "editor-notes.md")

        Returns:
            The relative URL to reach the aggregator from the current page
            (e.g., "editor-notes", "../editor-notes", "../../editor-notes")
        """
        aggregator_path = Path(aggregator_page)
        aggregator_url = aggregator_path.stem  # e.g., "editor-notes"

        if current_page.url and current_page.url != "":
            # Pages like "features/" need "../" to get back to root
            # Pages like "guide/advanced/" need "../../"
            # Count directory levels (non-root pages need at least one "../")
            url_parts = current_page.url.rstrip("/").split("/")
            url_parts = [p for p in url_parts if p]
            depth = len(url_parts)
            rel_prefix = "../" * depth if depth > 0 else ""
        else:
            # Root page (index) - no prefix needed
            rel_prefix = ""

        return f"{rel_prefix}{aggregator_url}"

    @staticmethod
    def protect_code_blocks(markdown: str, code_blocks: list[str]) -> str:
        """
        Protect code blocks by replacing them with placeholders.

        This prevents note patterns from being detected inside code blocks.

        Args:
            markdown: The markdown content to process
            code_blocks: List to store protected code blocks (modified in place)

        Returns:
            Markdown with code blocks replaced by placeholders
        """

        def save_code_block(match: re.Match[str]) -> str:
            code_blocks.append(match.group(0))
            return f"<<<CODE_BLOCK_{len(code_blocks) - 1}>>>"

        return CODE_BLOCK_PATTERN.sub(save_code_block, markdown)

    @staticmethod
    def restore_code_blocks(markdown: str, code_blocks: list[str]) -> str:
        """
        Restore code blocks from placeholders.

        Args:
            markdown: The markdown content with placeholders
            code_blocks: List of protected code blocks to restore

        Returns:
            Markdown with code blocks restored
        """
        for i, code_block in enumerate(code_blocks):
            markdown = markdown.replace(f"<<<CODE_BLOCK_{i}>>>", code_block)

        return markdown
