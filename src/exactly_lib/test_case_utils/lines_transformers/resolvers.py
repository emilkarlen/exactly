from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.type_system_values.lines_transformer import LinesTransformer
from exactly_lib.util.symbol_table import SymbolTable


class LinesTransformerConstant(LinesTransformerResolver):
    """
    A :class:`FileSelectorResolver` that is a constant :class:`FileSelector`
    """

    def __init__(self, value: LinesTransformer):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> LinesTransformer:
        return self._value

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''
