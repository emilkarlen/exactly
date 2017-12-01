from exactly_lib.help import std_tags as std_tags
from exactly_lib.util.textformat.structure.core import Text, StringText


def syntax_text(text: str) -> Text:
    return StringText(text,
                      tags={std_tags.SYNTAX_TEXT})
