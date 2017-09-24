from exactly_lib.symbol.data.restrictions import reference_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference


def reference_to_any_data_type_value(symbol_name: str) -> SymbolReference:
    return SymbolReference(symbol_name,
                           reference_restrictions.is_any_data_type())
