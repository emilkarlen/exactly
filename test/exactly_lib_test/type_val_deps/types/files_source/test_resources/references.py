from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type__single
from exactly_lib_test.type_val_deps.types.string_.test_resources.reference_assertions import \
    IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS

IS_FILES_SOURCE_REFERENCE_RESTRICTION = is_reference_restrictions__value_type__single(
    ValueType.FILES_SOURCE
)


def is_reference_to__files_source(symbol_name: str) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(
        symbol_name,
        IS_FILES_SOURCE_REFERENCE_RESTRICTION,
    )


def is_reference_restrictions_of_file_name_part() -> Assertion[ReferenceRestrictions]:
    return IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS


def is_reference_to__file_name_part(symbol_name: str) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(
        symbol_name,
        IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS,
    )
