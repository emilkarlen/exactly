from typing import Sequence

from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_case_utils.test_resources import resolver_assertions as asrt_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

IS_PROGRAM_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.PROGRAM)


def is_program_reference_to(symbol_name: str) -> asrt.ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_PROGRAM_REFERENCE_RESTRICTION)


def matches_program_resolver(references: asrt.ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                             resolved_value: asrt.ValueAssertion = asrt.anything_goes(),
                             symbols: SymbolTable = None) -> asrt.ValueAssertion[SymbolValueResolver]:
    return asrt_resolver.matches_resolver_of_logic_type2(ProgramResolver,
                                                         LogicValueType.PROGRAM,
                                                         ValueType.PROGRAM,
                                                         references=references,
                                                         resolved_value=resolved_value,
                                                         symbols=symbols)
