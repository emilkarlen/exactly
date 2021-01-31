from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.data.test_resources.assertion_utils import \
    symbol_table_with_values_matching_references
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    equals_data_type_symbol_references
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.types.path.test_resources.path_assertions import equals_path


def equals_path_sdv(expected: PathSdv) -> Assertion[SymbolDependentValue]:
    symbols = symbol_table_with_values_matching_references(expected.references)
    expected_path = expected.resolve(symbols)
    return type_sdv_assertions.matches_sdv_of_path(
        equals_data_type_symbol_references(expected.references),
        equals_path(expected_path),
        symbols=symbols)


def matches_path_sdv(expected_resolved_value: PathDdv,
                     expected_symbol_references: Assertion,
                     symbol_table: SymbolTable = None) -> Assertion[SymbolDependentValue]:
    return type_sdv_assertions.matches_sdv_of_path(expected_symbol_references,
                                                   equals_path(
                                                       expected_resolved_value),
                                                   symbols=symbol_table)
