import unittest

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.test_resources.data.assertion_utils import \
    symbol_table_with_values_matching_references
from exactly_lib_test.type_val_deps.test_resources.data.symbol_reference_assertions import \
    equals_symbol_references__convertible_to_string
from exactly_lib_test.type_val_deps.types.path.test_resources.path_assertions import equals_path


def equals_path_sdv(expected: PathSdv) -> Assertion[SymbolDependentValue]:
    symbols = symbol_table_with_values_matching_references(expected.references)
    expected_path = expected.resolve(symbols)
    return type_sdv_assertions.matches_sdv_of_path(
        equals_symbol_references__convertible_to_string(expected.references),
        equals_path(expected_path),
        symbols=symbols)


def equals_path_sdv_2(expected: PathSdv) -> Assertion[PathSdv]:
    return asrt.is_instance_with(PathSdv,
                                 equals_path_sdv(expected))


def matches_path_sdv(expected_resolved_value: PathDdv,
                     expected_symbol_references: Assertion,
                     symbol_table: SymbolTable = None) -> Assertion[SymbolDependentValue]:
    return type_sdv_assertions.matches_sdv_of_path(expected_symbol_references,
                                                   equals_path(
                                                       expected_resolved_value),
                                                   symbols=symbol_table)


class NameMatches(AssertionBase[PathSdv]):
    def __init__(self,
                 symbols: SymbolTable,
                 name: Assertion[str],
                 ):
        self._symbols = symbols
        self._name = name

    def _apply(self,
               put: unittest.TestCase,
               value: PathSdv,
               message_builder: MessageBuilder,
               ):
        put.assertIsInstance(value, PathSdv)
        path = value.resolve(self._symbols).value_of_any_dependency(fake_tcds())
        self._name.apply(put, path.name, message_builder.for_sub_component('name'))
