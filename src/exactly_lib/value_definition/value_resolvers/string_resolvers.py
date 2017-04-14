from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_values import StringResolver


class StringConstant(StringResolver):
    def __init__(self, string: str):
        self._string = string

    def resolve(self, symbols: SymbolTable) -> str:
        return self._string

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + self._string + '\''
