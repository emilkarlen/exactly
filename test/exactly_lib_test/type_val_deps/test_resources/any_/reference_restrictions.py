from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction, StringRestriction
from exactly_lib_test.type_val_deps.test_resources.data.value_restriction import ValueRestrictionWithConstantResult


def reference_restrictions__unconditionally_satisfied() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction())


def reference_restrictions__unconditionally_unsatisfied() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(ValueRestrictionWithConstantResult.of_err_msg_for_test())


def reference_restrictions__string_made_up_of_just_strings() -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(StringRestriction(),
                                                    StringRestriction())
