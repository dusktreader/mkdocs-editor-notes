"""Data models for editor notes."""

from dataclasses import dataclass


@dataclass
class EditorNote:
    """Represents an editor note extracted from markdown."""

    note_type: str
    label: str
    text: str
    source_page: str
    paragraph_id: str
    line_number: int | None = None

    @property
    def note_id(self) -> str:
        return f"{self.note_type}-{self.label}"
