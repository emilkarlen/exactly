import os
from typing import Tuple

from exactly_lib import program_info
from exactly_lib.cli.builtin_symbol import BuiltinSymbol
from exactly_lib.cli.custom_symbol import CustomSymbolDocumentation
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import types
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser

OS_LINE_SEP = 'OS_LINE_SEP'
NEW_LINE = 'NEW_LINE'
TAB = 'TAB'


def all_strings() -> Tuple[BuiltinSymbol, ...]:
    return (
        BuiltinSymbol(
            OS_LINE_SEP,
            ValueType.STRING,
            string_sdvs.str_constant(os.linesep),
            CustomSymbolDocumentation(
                "The {plain_string} that separates text lines on the {current_os} ({NL}, {WIN_LINE_SEP}, e.g.).".format(
                    NL=misc_texts.NEW_LINE_STRING_CONSTANT,
                    WIN_LINE_SEP=formatting.string_constant('\\r\\n'),
                    current_os=misc_texts.CURRENT_OS,
                    plain_string=misc_texts.PLAIN_STRING,
                ),
                SectionContents.empty(),
            ),
        ),
        BuiltinSymbol(
            NEW_LINE,
            ValueType.STRING,
            string_sdvs.str_constant('\n'),
            CustomSymbolDocumentation(
                "The new-line character ({NL}), the line separator of {string:s} handled by {program_name}".format(
                    NL=misc_texts.NEW_LINE_STRING_CONSTANT,
                    string=types.STRING_TYPE_INFO.name,
                    program_name=program_info.PROGRAM_NAME.capitalize(),
                ),
                _TP.section_contents(_NEW_LINE_DESCRIPTION),
            ),
        ),
        BuiltinSymbol(
            TAB,
            ValueType.STRING,
            string_sdvs.str_constant('\t'),
            CustomSymbolDocumentation(
                'The tab character.',
                SectionContents.empty(),
            ),
        ),
    )


_TP = TextParser({
    'NL': misc_texts.NEW_LINE_STRING_CONSTANT,
    'current_os': misc_texts.CURRENT_OS,
    'program_name': program_info.PROGRAM_NAME.capitalize(),

})

_NEW_LINE_DESCRIPTION = """\
{program_name} separates lines by {NL}, regardless of the {current_os}. 
"""
