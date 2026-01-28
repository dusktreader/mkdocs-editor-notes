import re

FIXED_NOTE_TYPES = {
    "todo": "✅",
    "ponder": "⏳",
    "improve": "🛠️",
    "research": "🔍",
}

DEFAULT_CUSTOM_EMOJI = "❗"


# Matches: [^type:label]: note text (can span multiple lines)
NOTE_DEF_PATTERN = re.compile(
    r"""
    ^                                   # Start of line
    \[\^                                # Literal [^
    (?P<type>[a-z]+)                    # Note type (letters only)
    :(?P<label>[a-z0-9\-_]+)            # Label (alphanumeric, hyphens, underscores)
    \]:                                 # Literal ]:
    \s*                                 # Optional whitespace (including newlines)
    (?P<text>.*?)                       # Note text (non-greedy, can span multiple lines)
    (?=                                 # Lookahead (don't consume):
        \n\s*\n                         #   Blank line (newline, optional whitespace, newline)
        |\n\[\^                         #   OR next note definition
        |\Z                             #   OR end of string
    )
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


# Matches: [^type:label]
NOTE_REF_PATTERN = re.compile(
    r"""
    \[\^                                # Literal [^
    (?P<type>[a-z]+)                    # Note type (letters only)
    :(?P<label>[a-z0-9\-_]+)            # Label (alphanumeric, hyphens, underscores)
    \]                                  # Literal ]
    """,
    re.VERBOSE,
)


CODE_BLOCK_PATTERN = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~)", re.MULTILINE)
