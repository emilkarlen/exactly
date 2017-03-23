from exactly_lib.util.symbol_table import SymbolTable


class PathPart:
    """
    The relative path that follows the root path of the `FileRef`.
    """

    def resolve(self, symbols: SymbolTable) -> str:
        raise NotImplementedError()

    @property
    def value_references(self) -> list:
        """
        :rtype: [ValueReference]
        """
        raise NotImplementedError()
