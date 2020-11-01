from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions


def reference_to_any_data_type_value(symbol_name: str) -> SymbolReference:
    return SymbolReference(symbol_name,
                           reference_restrictions.is_any_data_type())
