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
NOTE_DEF_PATTERN = re.compile(
    r"""
    ^                                   # Start of line
    \[\^                                # Literal [^
    (?P<type>[a-z]+)                    # Note type (letters only)
    (?::(?P<label>[a-z0-9\-_]+))?       # Optional :label (alphanumeric, hyphens, underscores)
    \]:                                 # Literal ]:
    (?P<text>.*?)                       # Note text (non-greedy, can span multiple lines)
    (?=                                 # Lookahead (don't consume):
        \n\s*\n                         #   Blank line (newline, optional whitespace, newline)
        |\n\[\^                         #   OR next note definition
        |\Z                             #   OR end of string
    )
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)

# Pattern for note references: [^type:label] or [^type]
NOTE_REF_PATTERN = re.compile(
    r"""
    \[\^                                # Literal [^
    (?P<type>[a-z]+)                    # Note type (letters only)
    (?::(?P<label>[a-z0-9\-_]+))?       # Optional :label (alphanumeric, hyphens, underscores)
    \]                                  # Literal ]
    """,
    re.VERBOSE,
)

# Pattern for code blocks (to protect from processing)
CODE_BLOCK_PATTERN = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~)", re.MULTILINE)
