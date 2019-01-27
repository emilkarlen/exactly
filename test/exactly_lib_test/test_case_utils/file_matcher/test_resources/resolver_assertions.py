from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources import resolver_assertions
from exactly_lib_test.test_case_utils.file_matcher.test_resources.value_assertions import value_equals_file_matcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def resolved_value_equals_file_matcher(expected: FileMatcher,
                                       expected_references: ValueAssertion = asrt.is_empty_sequence,
                                       symbols: symbol_table.SymbolTable = None
                                       ) -> ValueAssertion[SymbolValueResolver]:
    return resolver_assertions.matches_resolver_of_file_matcher(expected_references,
                                                                value_equals_file_matcher(expected),
                                                                symbols=symbols)
