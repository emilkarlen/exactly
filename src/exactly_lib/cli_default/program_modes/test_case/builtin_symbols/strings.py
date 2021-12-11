import os
from typing import Tuple

from exactly_lib import program_info
from exactly_lib.cli.builtin_symbol import BuiltinSymbol
from exactly_lib.cli.custom_symbol import CustomSymbolDocumentation
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import types, concepts
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser

TAB = 'TAB'
NEW_LINE = 'NEW_LINE'
OS_LINE_SEP = 'OS_LINE_SEP'
OS_PATH_SEP = 'OS_PATH_SEP'


def all_strings() -> Tuple[BuiltinSymbol, ...]:
    return (
        BuiltinSymbol(
            TAB,
            ValueType.STRING,
            string_sdvs.str_constant('\t'),
            CustomSymbolDocumentation(
                _TAB_SL_DESCR,
                SectionContents.empty(),
            ),
        ),
        BuiltinSymbol(
            NEW_LINE,
            ValueType.STRING,
            string_sdvs.str_constant('\n'),
            CustomSymbolDocumentation(
                _TP.format(_NEW_LINE__SL_DESCR),
                _TP.section_contents(_NEW_LINE_DESCRIPTION),
            ),
        ),
        BuiltinSymbol(
            OS_LINE_SEP,
            ValueType.STRING,
            string_sdvs.str_constant(os.linesep),
            CustomSymbolDocumentation(
                _TP.format(_OS_LINE_SEP__SL_DESCR),
                SectionContents.empty(),
            ),
        ),
        BuiltinSymbol(
            OS_PATH_SEP,
            ValueType.STRING,
            string_sdvs.str_constant(os.pathsep),
            CustomSymbolDocumentation(
                _TP.format(_OS_PATH_SEP__SL_DESCR),
                _TP.section_contents(_OS_PATH_SEP__DESCRIPTION),
            ),
        ),
    )


_TP = TextParser({
    'NL': misc_texts.NEW_LINE_STRING_CONSTANT,
    'current_os': misc_texts.CURRENT_OS,
    'program_name': program_info.PROGRAM_NAME.capitalize(),
    'LINE_SEP__WIN': formatting.string_constant('\\r\\n'),
    'plain_string': misc_texts.PLAIN_STRING,
    'string': types.STRING_TYPE_INFO.name,
    'PATH_SEP__UNIX': formatting.string_constant(':'),
    'PATH_SEP__WIN': formatting.string_constant(';'),
    'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
})

_TAB_SL_DESCR = 'The tab character.'

_NEW_LINE__SL_DESCR = """\
The new-line character ({NL}), the line separator of {string:s} handled by {program_name}.
"""

_NEW_LINE_DESCRIPTION = """\
{program_name} separates lines by {NL}, regardless of the {current_os}. 
"""

_OS_LINE_SEP__SL_DESCR = """\
The {plain_string} that separates text lines on the {current_os} ({NL}, {LINE_SEP__WIN}, e.g.).
"""

_OS_PATH_SEP__SL_DESCR = """\
The {plain_string} that separates file paths on the {current_os}.
"""

_OS_PATH_SEP__DESCRIPTION = """\
This {plain_string} separates file paths in the PATH {env_var}.


This is {PATH_SEP__UNIX} on Unix,
and {PATH_SEP__WIN} on Windows, e.g.
"""
