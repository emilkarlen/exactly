from exactly_lib.symbol import string_resolver
from exactly_lib.symbol import symbol_usage
from exactly_lib.symbol.concrete_restrictions import no_restrictions
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.string_resolver import StringResolver


def string_resolver_of_single_symbol_reference(
        symbol_name: str,
        restrictions: ReferenceRestrictions = no_restrictions()) -> StringResolver:
    symbol_reference = symbol_usage.SymbolReference(symbol_name,
                                                    restrictions)
    fragments = [
        string_resolver.SymbolStringFragmentResolver(symbol_reference)
    ]
    return StringResolver(tuple(fragments))
