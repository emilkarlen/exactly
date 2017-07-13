from exactly_lib.symbol.value_structure import SymbolValueResolver
from exactly_lib.type_system_values.list_value import ListValue
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class ListResolver(SymbolValueResolver):
    """
    Resolver who's resolved value is of type `ValueType.LIST` / :class:`ListValue`
    """

    def __init__(self, string_resolver_elements: list):
        """

        :param string_resolver_elements: List of :class:`StringResolver`
        """
        self._string_resolver_elements = tuple(string_resolver_elements)

    @property
    def value_type(self) -> ValueType:
        return ValueType.LIST

    @property
    def references(self) -> list:
        ret_val = []
        for string_resolver in self._string_resolver_elements:
            ret_val.extend(string_resolver.references)
        return ret_val

    def resolve(self, symbols: SymbolTable) -> ListValue:
        elements = [string_resolver.resolve(symbols)
                    for string_resolver in self._string_resolver_elements]
        return ListValue(elements)
