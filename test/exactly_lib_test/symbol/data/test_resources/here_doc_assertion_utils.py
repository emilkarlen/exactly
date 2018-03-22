from typing import List

from exactly_lib.test_case_utils.parse.parse_here_document import DOCUMENT_MARKER_PREFIX
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.symbol.data.test_resources import string_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def contents_str_from_lines(lines_of_here_doc: list) -> str:
    return lines_content(lines_of_here_doc)


def here_doc_lines(marker: str,
                   contents_lines: List[str],
                   first_line_start: str = '') -> List[str]:
    return ([first_line_start + DOCUMENT_MARKER_PREFIX + marker] +
            contents_lines +
            [marker]
            )


def matches_resolved_value(expected_resolved_primitive_lines: list,
                           symbol_references: list = None,
                           symbols: SymbolTable = None) -> asrt.ValueAssertion:
    symbols = empty_symbol_table() if symbols is None else symbols
    symbol_references = [] if symbol_references is None else symbol_references
    return string_assertions.matches_primitive_string(
        asrt.equals(contents_str_from_lines(expected_resolved_primitive_lines)),
        symbol_references,
        symbols)
