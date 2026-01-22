"""Constants for the mkdocs-editor-notes plugin."""

import re

# Fixed note types with default emojis
FIXED_NOTE_TYPES = {
    "todo": "✅",
    "ponder": "⏳",
    "improve": "🛠️",
    "research": "🔍",
}

# Default emoji for custom note types
DEFAULT_CUSTOM_EMOJI = "❗"

# Pattern for note definitions: [^type:label]: note text (can span multiple lines)
# Text continues until: blank line (\n\s*\n) OR another definition (\n\[^) OR end of string
NOTE_DEF_PATTERN = re.compile(
    r"^\[\^(?P<type>[a-z]+)(?::(?P<label>[a-z0-9\-_]+))?\]:(?P<text>.*?)(?=\n\s*\n|\n\[\^|\Z)",
    re.MULTILINE | re.DOTALL,
)

# Pattern for note references: [^type:label] or [^type]
NOTE_REF_PATTERN = re.compile(r"\[\^(?P<type>[a-z]+)(?::(?P<label>[a-z0-9\-_]+))?\]")

# Pattern for code blocks (to protect from processing)
CODE_BLOCK_PATTERN = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~)", re.MULTILINE)
