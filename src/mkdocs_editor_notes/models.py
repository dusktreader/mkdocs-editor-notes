"""Data models for editor notes."""

from dataclasses import dataclass


@dataclass
class EditorNote:
    """Represents an editor note extracted from markdown."""

    note_type: str
    label: str
    text: str
    source_page: str
    ref_id: str | None = None
    line_number: int = 0

    @property
    def note_id(self) -> str:
        return f"{self.note_type}-{self.label}"

    @property
    def note_key(self) -> str:
        return f"{self.note_type}:{self.label}"

    @property
    def hover_text(self) -> str:
        return f"{self.note_type}: {self.label}"
