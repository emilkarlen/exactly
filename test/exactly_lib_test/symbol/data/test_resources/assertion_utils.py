from typing import Sequence

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.restrictions import value_restrictions as vr
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.string_sdvs import str_constant
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_utils import single_line_sequence
from exactly_lib_test.test_case_file_structure.test_resources.simple_path import path_test_impl


def symbol_table_with_values_matching_references(references: Sequence[SymbolReference]) -> SymbolTable:
    value_constructor = _ValueCorrespondingToValueRestriction()
    elements = {}
    for ref in references:
        assert isinstance(ref, SymbolReference), "Type info for IDE"
        restrictions = ref.restrictions
        assert isinstance(restrictions,
                          ReferenceRestrictionsOnDirectAndIndirect), 'Only handled/needed case for the moment'
        value_restriction = restrictions.direct
        assert isinstance(value_restriction, ValueRestriction)
        value = value_constructor.visit(value_restriction)
        elements[ref.name] = _symbol_container(value)
    return SymbolTable(elements)


def path_sdv_test_impl(valid_relativities: PathRelativityVariants) -> PathSdv:
    relativity = list(valid_relativities.rel_option_types)[0]
    assert isinstance(relativity, RelOptionType)
    return path_sdvs.constant(path_test_impl('path_test_impl', relativity))


class _ValueCorrespondingToValueRestriction(vr.ValueRestrictionVisitor):
    def visit_none(self, x: vr.AnyDataTypeRestriction) -> DataTypeSdv:
        return str_constant('a string (from <no restriction>)')

    def visit_string(self, x: vr.StringRestriction) -> DataTypeSdv:
        return str_constant('a string (from <string value restriction>)')

    def visit_path_relativity(self, x: vr.PathRelativityRestriction) -> DataTypeSdv:
        return path_sdv_test_impl(x.accepted)


def _symbol_container(value: PathSdv) -> SymbolContainer:
    return SymbolContainer(value,
                           single_line_sequence(1, 'source line'))
