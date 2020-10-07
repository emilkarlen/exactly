import os
from typing import Tuple

from exactly_lib.cli.builtin_symbol import BuiltinSymbol
from exactly_lib.cli.custom_symbol import CustomSymbolDocumentation
from exactly_lib.definitions import misc_texts
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.textformat.structure.document import SectionContents

LINE_SEP = 'LINE_SEP'
TAB = 'TAB'


def all_strings() -> Tuple[BuiltinSymbol, ...]:
    return (
        BuiltinSymbol(
            LINE_SEP,
            ValueType.STRING,
            string_sdvs.str_constant(os.linesep),
            CustomSymbolDocumentation(
                "The string that separates text lines on the {} ('\\n', '\\r\\n', e.g.)".format(
                    misc_texts.CURRENT_OS
                ),
                SectionContents.empty(),
            ),
        ),
        BuiltinSymbol(
            TAB,
            ValueType.STRING,
            string_sdvs.str_constant('\t'),
            CustomSymbolDocumentation(
                'The tab character',
                SectionContents.empty(),
            ),
        ),
    )
