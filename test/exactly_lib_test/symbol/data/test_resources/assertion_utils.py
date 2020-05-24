from typing import Sequence, Tuple

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.restrictions import value_restrictions as vr
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.string_sdvs import str_constant
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.simple_path import path_test_impl


def symbol_table_with_values_matching_references(references: Sequence[SymbolReference]) -> SymbolTable:
    value_constructor = _ValueCorrespondingToValueRestriction()
    elements = {}
    for ref in references:
        restrictions = ref.restrictions
        assert isinstance(restrictions,
                          ReferenceRestrictionsOnDirectAndIndirect), 'Only handled/needed case for the moment'
        value_restriction = restrictions.direct
        assert isinstance(value_restriction, ValueRestriction)
        value_type, value = value_constructor.visit(value_restriction)
        elements[ref.name] = SymbolContainer(value, value_type, None)
    return SymbolTable(elements)


def path_sdv_test_impl(valid_relativities: PathRelativityVariants) -> PathSdv:
    relativity = list(valid_relativities.rel_option_types)[0]
    assert isinstance(relativity, RelOptionType)
    return path_sdvs.constant(path_test_impl('path_test_impl', relativity))


class _ValueCorrespondingToValueRestriction(vr.ValueRestrictionVisitor[Tuple[ValueType, DataTypeSdv]]):
    def visit_none(self, x: vr.AnyDataTypeRestriction) -> Tuple[ValueType, DataTypeSdv]:
        return ValueType.STRING, str_constant('a string (from <no restriction>)')

    def visit_string(self, x: vr.StringRestriction) -> Tuple[ValueType, DataTypeSdv]:
        return ValueType.STRING, str_constant('a string (from <string value restriction>)')

    def visit_path_relativity(self, x: vr.PathRelativityRestriction) -> Tuple[ValueType, DataTypeSdv]:
        return ValueType.PATH, path_sdv_test_impl(x.accepted)
