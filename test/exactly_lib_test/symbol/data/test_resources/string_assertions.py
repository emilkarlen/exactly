import unittest
from typing import Sequence

from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_data_type_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def matches_primitive_string(resolved_str: ValueAssertion[str],
                             symbol_references: Sequence[SymbolReference],
                             symbols: SymbolTable) -> ValueAssertion[StringSdv]:
    return MatchesPrimitiveValueResolvedOfAnyDependency(resolved_str,
                                                        symbol_references,
                                                        symbols)


class MatchesPrimitiveValueResolvedOfAnyDependency(ValueAssertionBase[StringSdv]):
    def __init__(self,
                 expected_resolved_primitive_value: ValueAssertion[str],
                 symbol_references: Sequence[SymbolReference],
                 symbols: SymbolTable):
        self.symbol_references = symbol_references
        self.symbols = symbols
        self.expected_resolved_primitive_value = expected_resolved_primitive_value

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, StringSdv)
        assert isinstance(value, StringSdv)  # Type info for IDE
        equals_data_type_symbol_references(self.symbol_references).apply_with_message(put,
                                                                                      value.references,
                                                                                      'symbol references')
        environment = PathResolvingEnvironmentPreOrPostSds(fake_tcds(),
                                                           self.symbols)
        actual_resolved_prim_val = value.resolve_value_of_any_dependency(environment)
        self.expected_resolved_primitive_value.apply_with_message(put, actual_resolved_prim_val,
                                                                  'resolved primitive value')
