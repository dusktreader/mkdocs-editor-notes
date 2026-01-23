"""Data models for editor notes."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class EditorNote:
    """Represents an editor note extracted from markdown."""

    note_type: str
    label: str
    text: str
    source_page: str | Path
    ref_id: str | None = None
    line_number: int = 0

    def __post_init__(self) -> None:
        """Convert source_page to Path if it's a string."""
        if isinstance(self.source_page, str):
            self.source_page = Path(self.source_page)

    @property
    def note_id(self) -> str:
        return f"{self.note_type}-{self.label}"

    @property
    def note_key(self) -> str:
        return f"{self.note_type}:{self.label}"

    @property
    def hover_text(self) -> str:
        return f"{self.note_type}: {self.label}"
