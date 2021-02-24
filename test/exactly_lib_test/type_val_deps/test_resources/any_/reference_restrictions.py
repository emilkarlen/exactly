from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import \
    ArbitraryValueWStrRenderingRestriction
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import value_restrictions
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.value_restrictions import \
    ValueRestrictionWithConstantResult


def reference_restrictions__unconditionally_satisfied() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(ArbitraryValueWStrRenderingRestriction.of_any())


def reference_restrictions__unconditionally_unsatisfied() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(ValueRestrictionWithConstantResult.of_err_msg_for_test())


def reference_restrictions__string__w_all_indirect_refs_are_strings() -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(
        value_restrictions.is_string(),
        value_restrictions.is_string(),
    )
