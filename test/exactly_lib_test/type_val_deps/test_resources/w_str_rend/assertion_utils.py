from typing import Sequence, Tuple

from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.symbol.value_type import ValueType, WithStrRenderingType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.tcfs.relativity_root import RelOptionType
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import value_restrictions as vr
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.value_restrictions_visitor import \
    ProdValueRestrictionVariantsVisitor
from exactly_lib_test.type_val_deps.types.path.test_resources.simple_path import path_test_impl


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


class _ValueCorrespondingToValueRestriction(ProdValueRestrictionVariantsVisitor[Tuple[ValueType, DataTypeSdv]]):
    def visit_any(self, x: vr.ArbitraryValueWStrRenderingRestriction) -> Tuple[ValueType, DataTypeSdv]:
        if WithStrRenderingType.STRING in x.accepted:
            return _arbitrary_sdv__string()
        elif WithStrRenderingType.PATH in x.accepted:
            return _arbitrary_sdv__path(PathRelativityVariants(set(RelOptionType), True))
        elif WithStrRenderingType.LIST in x.accepted:
            return _arbitrary_sdv__list()
        else:
            raise TypeError('Unknown or empty list of {}: {}'.format(WithStrRenderingType, x.accepted))

    def visit_path_relativity(self, x: vr.PathAndRelativityRestriction) -> Tuple[ValueType, DataTypeSdv]:
        return _arbitrary_sdv__path(x.accepted)


def _arbitrary_sdv__path(accepted: PathRelativityVariants) -> Tuple[ValueType, DataTypeSdv]:
    return ValueType.PATH, path_sdv_test_impl(accepted)


def _arbitrary_sdv__string() -> Tuple[ValueType, DataTypeSdv]:
    return ValueType.STRING, string_sdvs.str_constant('a string (from <string value restriction>)')


def _arbitrary_sdv__list() -> Tuple[ValueType, DataTypeSdv]:
    return ValueType.LIST, list_sdvs.empty()
