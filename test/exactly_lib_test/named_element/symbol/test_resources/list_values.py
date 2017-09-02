from exactly_lib.named_element.symbol.list_resolver import ListResolver
from exactly_lib.type_system.list_value import ListValue
from exactly_lib.util.symbol_table import SymbolTable


class ListResolverTestImplForConstantListValue(ListResolver):
    def __init__(self, list_value: ListValue):
        super().__init__([])
        self._list_value = list_value

    @property
    def elements(self) -> tuple:
        raise ValueError('this method is not supported')

    @property
    def references(self) -> list:
        return []

    def resolve(self, symbols: SymbolTable) -> ListValue:
        return self._list_value
