from exactly_lib.symbol.resolver_structure import ResolverContainer
from exactly_lib.symbol.restriction import ValueRestriction
from exactly_lib.util.symbol_table import SymbolTable


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: ResolverContainer) -> str:
        return None
