from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.value_structure import ValueRestriction, Value


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        return None
