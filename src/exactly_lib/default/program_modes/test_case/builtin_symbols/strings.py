import os
from typing import Tuple

from exactly_lib.cli.main_program import builtin_symbol_of_custom_symbol, BuiltinSymbol
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_utils.symbol.custom_symbol import CustomSymbolDocumentation
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.textformat.structure.document import SectionContents

LINE_SEP = 'LINE_SEP'
TAB = 'TAB'


def all_strings() -> Tuple[BuiltinSymbol, ...]:
    return (
        builtin_symbol_of_custom_symbol(
            LINE_SEP,
            ValueType.STRING,
            string_sdvs.str_constant(os.linesep),
            CustomSymbolDocumentation(
                "The string that separates text lines on the current OS ('\\n', '\\r\\n', e.g.)",
                SectionContents.empty(),
            ),
        ),
        builtin_symbol_of_custom_symbol(
            TAB,
            ValueType.STRING,
            string_sdvs.str_constant('\t'),
            CustomSymbolDocumentation(
                'The tab character',
                SectionContents.empty(),
            ),
        ),
    )
