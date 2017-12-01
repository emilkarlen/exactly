from exactly_lib.help import std_tags as std_tags
from exactly_lib.help_texts import formatting
from exactly_lib.util.textformat.structure.core import StringText


def syntax_text(text: str) -> StringText:
    return StringText(text,
                      tags={std_tags.SYNTAX_TEXT})


def directory_variable_name_text(name: str) -> StringText:
    return syntax_text(name)


def file_name_text(name: str) -> StringText:
    return syntax_text(name)


def instruction_name_text(name: str) -> StringText:
    return syntax_text(name)


def section_name_text(name: formatting.SectionName) -> StringText:
    return syntax_text(name.syntax)
