from typing import Iterable, List, Sequence, Optional

from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolReference
from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.types.list_ import list_sdv, list_sdvs
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.assertion_utils import \
    symbol_table_with_values_matching_references
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    equals_symbol_references__w_str_rendering, \
    equals_data_type_symbol_reference
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ddv_assertions import equals_list_ddv
from exactly_lib_test.type_val_deps.types.string_.test_resources.ddv_assertions import equals_string_ddv


def equals_list_sdv_element(expected: list_sdv.ElementSdv,
                            symbols: SymbolTable = None) -> Assertion[list_sdv.ElementSdv]:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(list(expected.references))
    expected_resolved_value_list = expected.resolve(symbols)
    assertion_on_resolved_value = asrt.matches_sequence(
        [equals_string_ddv(sv) for sv in expected_resolved_value_list])
    component_assertions = [
        asrt.sub_component('references',
                           lambda x: list(x.references),
                           equals_symbol_references__w_str_rendering(list(expected.references))),
        asrt.sub_component('resolved value',
                           lambda x: x.resolve(symbols),
                           assertion_on_resolved_value),

    ]
    symbol_reference_assertion = asrt.is_none
    reference = expected.symbol_reference_if_is_symbol_reference
    if reference is not None:
        reference_restrictions = reference.restrictions
        if not isinstance(reference_restrictions, WithStrRenderingTypeRestrictions):
            raise ValueError('A list element must reference a data type value')
        assert isinstance(reference_restrictions, WithStrRenderingTypeRestrictions)  # Type info for IDE

        symbol_reference_assertion = equals_data_type_symbol_reference(reference)

        asrt_sym_ref.matches_reference_2(
            reference.name,
            data_restrictions_assertions.equals__w_str_rendering(
                reference_restrictions)
        )

    symbol_reference_component_assertion = asrt.sub_component('symbol_reference_if_is_symbol_reference',
                                                              lambda x: x.symbol_reference_if_is_symbol_reference,
                                                              symbol_reference_assertion)
    component_assertions.append(symbol_reference_component_assertion)
    return asrt.is_instance_with(
        list_sdv.ElementSdv,
        asrt.and_(component_assertions))


def equals_list_sdv_elements(elements: List[list_sdv.ElementSdv],
                             symbols: SymbolTable = None) -> Assertion[Sequence[list_sdv.ElementSdv]]:
    element_assertions = [equals_list_sdv_element(element, symbols)
                          for element in elements]
    return asrt.matches_sequence(element_assertions)


def equals_list_sdv(expected: ListSdv,
                    symbols: Optional[SymbolTable] = None) -> Assertion[SymbolDependentValue]:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(expected.references)

    expected_resolved_value = expected.resolve(symbols)

    def get_element_sdvs(x: ListSdv) -> Sequence[list_sdv.ElementSdv]:
        return x.elements

    return type_sdv_assertions.matches_sdv_of_list(
        equals_symbol_references__w_str_rendering(expected.references),
        equals_list_ddv(expected_resolved_value),
        asrt.sub_component('element SDVs',
                           get_element_sdvs,
                           equals_list_sdv_elements(
                               list(expected.elements))),

        symbols)


def matches_list_sdv(expected_resolved_value: ListDdv,
                     expected_symbol_references: Assertion[Sequence[SymbolReference]],
                     symbols: Optional[SymbolTable] = None) -> Assertion[SymbolDependentValue]:
    return type_sdv_assertions.matches_sdv_of_list(expected_symbol_references,
                                                   equals_list_ddv(
                                                       expected_resolved_value),
                                                   symbols=symbols)


def equals_constant_list(expected_str_list: Iterable[str]) -> Assertion[SymbolDependentValue]:
    return equals_list_sdv(list_sdvs.from_str_constants(expected_str_list))
