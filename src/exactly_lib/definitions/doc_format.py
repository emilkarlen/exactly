from exactly_lib.common.exit_value import ExitValue
from exactly_lib.definitions import formatting
from exactly_lib.help import std_tags as std_tags
from exactly_lib.util.textformat.structure.core import StringText


def syntax_text(text: str) -> StringText:
    return StringText(text,
                      tags={std_tags.SYNTAX_TEXT})


def text_as_header(text: str) -> StringText:
    return StringText(text,
                      tags={std_tags.TEXT_AS_HEADER})


def enum_name_text(name: str) -> StringText:
    return StringText(name,
                      tags={std_tags.SYNTAX_TEXT,
                            std_tags.ENUM_CONSTANT})


def directory_variable_name_text(name: str) -> StringText:
    return syntax_text(name)


def file_name_text(name: str) -> StringText:
    return syntax_text(name)


def dir_name_text(name: str) -> StringText:
    return file_name_text(name + '/')


def literal_source_text(source: str) -> StringText:
    return syntax_text(source)


def instruction_name_text(name: str) -> StringText:
    return syntax_text(name)


def section_name_text(name: formatting.SectionName) -> StringText:
    return syntax_text(name.syntax)


def exit_value_text(ev: ExitValue) -> StringText:
    return syntax_text(ev.exit_identifier)
