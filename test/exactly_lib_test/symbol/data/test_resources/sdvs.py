from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions


def string_sdv_of_single_symbol_reference(
        symbol_name: str,
        restrictions: ReferenceRestrictions = is_any_data_type()) -> StringSdv:
    symbol_reference = SymbolReference(symbol_name,
                                       restrictions)
    fragments = [
        string_sdvs.symbol_fragment(symbol_reference)
    ]
    return StringSdv(tuple(fragments))
