"""Data models for editor notes."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EditorNote:
    """Represents an editor note extracted from markdown."""

    note_type: str  # todo, ponder, improve, research, etc.
    label: Optional[str]  # optional label for the note
    text: str  # the note content
    source_page: str  # path to source page
    paragraph_id: str  # unique ID for the paragraph containing the note
    line_number: Optional[int] = None  # line number in source file

    @property
    def note_id(self) -> str:
        """Generate a unique ID for this note."""
        if self.label:
            return f"{self.note_type}-{self.label}"
        return f"{self.note_type}-{self.paragraph_id}"

    @property
    def display_label(self) -> str:
        """Get display label for the note."""
        return self.label if self.label else self.note_type
