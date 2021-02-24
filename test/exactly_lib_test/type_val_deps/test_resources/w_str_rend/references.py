from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import ArbitraryValueWStrRenderingRestriction


def reference_to__w_str_rendering(symbol_name: str) -> SymbolReference:
    return SymbolReference(symbol_name,
                           reference_restrictions.is_any_type_w_str_rendering())


def reference_to__on_direct_and_indirect(
        name: str,
        value_restriction: ValueRestriction = ArbitraryValueWStrRenderingRestriction.of_any(),
) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))
