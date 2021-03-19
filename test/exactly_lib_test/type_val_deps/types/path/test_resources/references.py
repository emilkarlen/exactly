import enum

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import WithStrRenderingType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, OrReferenceRestrictions, OrRestrictionPart
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.any_.reference_restrictions import \
    reference_restrictions__string__w_all_indirect_refs_are_strings
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import \
    data_restrictions_assertions as asrt_data_ref_restriction


def path_reference_restrictions(accepted_relativities: PathRelativityVariants
                                ) -> WithStrRenderingTypeRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(PathAndRelativityRestriction(accepted_relativities))


def path_or_string_reference_restrictions(accepted_relativities: PathRelativityVariants
                                          ) -> WithStrRenderingTypeRestrictions:
    return OrReferenceRestrictions([
        OrRestrictionPart(
            WithStrRenderingType.PATH,
            ReferenceRestrictionsOnDirectAndIndirect(PathAndRelativityRestriction(accepted_relativities))),
        OrRestrictionPart(
            WithStrRenderingType.STRING,
            reference_restrictions__string__w_all_indirect_refs_are_strings()),
    ])


def is_reference_to__path_or_string(symbol_name: str,
                                    accepted_relativities: PathRelativityVariants,
                                    ) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(
        symbol_name,
        asrt_data_ref_restriction.equals__w_str_rendering(
            path_or_string_reference_restrictions(accepted_relativities))
    )


class PathReferenceVariant(enum.IntEnum):
    PATH = 1
    PATH_OR_STRING = 2
