from typing import Sequence

from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherValue
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources import resolver_assertions
from exactly_lib_test.test_case_utils.file_matcher.test_resources.value_assertions import value_equals_file_matcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def resolved_value_equals_file_matcher(expected: FileMatcher,
                                       references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                       symbols: symbol_table.SymbolTable = None
                                       ) -> ValueAssertion[SymbolValueResolver]:
    return resolver_assertions.matches_resolver_of_file_matcher(
        references,
        value_equals_file_matcher(expected),
        symbols=symbols)


def resolved_value_matches_file_matcher(value: ValueAssertion[FileMatcherValue],
                                        references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                        symbols: symbol_table.SymbolTable = None
                                        ) -> ValueAssertion[SymbolValueResolver]:
    return resolver_assertions.matches_resolver_of_file_matcher(
        references,
        value,
        symbols=symbols)
