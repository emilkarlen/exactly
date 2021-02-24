from typing import List, Optional, Sequence

import exactly_lib_test.type_val_deps.types.string_.test_resources.sdv_assertions
from exactly_lib.definitions.primitives.string import HERE_DOCUMENT_MARKER_PREFIX
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def contents_str_from_lines(lines_of_here_doc: Sequence[str]) -> str:
    return lines_content(lines_of_here_doc)


def here_doc_lines(marker: str,
                   contents_lines: List[str],
                   first_line_start: str = '') -> List[str]:
    return ([first_line_start + HERE_DOCUMENT_MARKER_PREFIX + marker] +
            contents_lines +
            [marker]
            )


def matches_resolved_value(expected_resolved_primitive_lines: Sequence[str],
                           symbol_references: Optional[Sequence[SymbolReference]] = None,
                           symbols: SymbolTable = None) -> Assertion[StringSdv]:
    symbols = empty_symbol_table() if symbols is None else symbols
    symbol_references = [] if symbol_references is None else symbol_references
    return exactly_lib_test.type_val_deps.types.string_.test_resources.sdv_assertions.matches_primitive_string(
        asrt.equals(contents_str_from_lines(expected_resolved_primitive_lines)),
        symbol_references,
        symbols)
