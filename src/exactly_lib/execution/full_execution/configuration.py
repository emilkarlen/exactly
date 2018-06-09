from exactly_lib.util.symbol_table import SymbolTable


class PredefinedProperties:
    """Properties that are forwarded to the right place in the execution."""

    def __init__(self,
                 predefined_symbols: SymbolTable = None):
        self.__predefined_symbols = predefined_symbols

    @property
    def predefined_symbols(self) -> SymbolTable:
        return self.__predefined_symbols
