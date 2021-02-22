from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction


def reference_to__convertible_to_string(symbol_name: str) -> SymbolReference:
    return SymbolReference(symbol_name,
                           reference_restrictions.is_type_convertible_to_string())


def reference_to__on_direct_and_indirect(name: str,
                                         value_restriction: ValueRestriction = AnyDataTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))
