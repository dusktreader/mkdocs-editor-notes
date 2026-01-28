from dataclasses import dataclass
from pathlib import Path


@dataclass
class EditorNote:
    note_type: str
    label: str
    text: str
    source_page: Path
    source_url: str = ""
    line_number: int = 0

    def __post_init__(self):
        """Ensure source_url always ends with a slash if non-empty."""
        if self.source_url and not self.source_url.endswith("/"):
            self.source_url = f"{self.source_url}/"

    @property
    def ref_id(self) -> str:
        return f"ref-{self.note_type}-{self.label}"

    @property
    def ref_url(self) -> str:
        if self.source_url:
            return f"../{self.source_url}#{self.ref_id}"
        # For root index page (empty URL), use relative path
        return f"../#{self.ref_id}"

    @property
    def agg_id(self) -> str:
        return f"agg-{self.note_type}-{self.label}"

    @property
    def hover_text(self) -> str:
        return f"{self.note_type}: {self.label}"
