from typing import Sequence

from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import resolver_assertions
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_PROGRAM_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.PROGRAM)


def is_program_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_PROGRAM_REFERENCE_RESTRICTION)


def matches_program_resolver(references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                             resolved_value: ValueAssertion = asrt.anything_goes(),
                             symbols: SymbolTable = None) -> ValueAssertion[SymbolValueResolver]:
    return resolver_assertions.matches_resolver_of_program(references=references,
                                                           resolved_program_value=resolved_value,
                                                           symbols=symbols)
