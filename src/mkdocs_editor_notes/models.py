"""Data models for editor notes."""

from dataclasses import dataclass


@dataclass
class EditorNote:
    """Represents an editor note extracted from markdown."""

    note_type: str
    label: str | None
    text: str
    source_page: str # TODO: should this be a Path?
    paragraph_id: str # TODO: was this only used for notes taht didn't have a label?
    line_number: int | None = None  # TODO: why is this optional?

    @property
    def note_id(self) -> str:
        if self.label:
            return f"{self.note_type}-{self.label}"
        return f"{self.note_type}-{self.paragraph_id}"

    @property
    def display_label(self) -> str:
        """Get display label for the note."""
        return self.label if self.label else self.note_type
