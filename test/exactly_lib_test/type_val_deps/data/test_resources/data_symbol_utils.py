from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction


def symbol_reference(name: str,
                     value_restriction: ValueRestriction = AnyDataTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))
