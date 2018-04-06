from typing import Sequence, Iterable, List

from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data import concrete_string_values as csv
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class Element:
    """
    An element of a list resolver.
    """

    @property
    def symbol_reference_if_is_symbol_reference(self) -> SymbolReference:
        """
        :returns: None if this element is not a single-symbol-reference element ,
        else the reference.
        """
        raise NotImplementedError()

    @property
    def references(self) -> Sequence[SymbolReference]:
        """
        Values in the symbol table used by this object.
        """
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable) -> List[str]:
        """Gives the list of string values that this element represents"""
        raise NotImplementedError()


class StringResolverElement(Element):
    """ An element that is a string. """

    def __init__(self, string_resolver: StringResolver):
        self._string_resolver = string_resolver

    @property
    def symbol_reference_if_is_symbol_reference(self) -> SymbolReference:
        """
        :returns: None if this element is not a single-symbol-reference element ,
        else the reference.
        """
        return None

    @property
    def references(self) -> Sequence[SymbolReference]:
        return tuple(self._string_resolver.references)

    def resolve(self, symbols: SymbolTable) -> List[str]:
        return [self._string_resolver.resolve(symbols)]


class SymbolReferenceElement(Element):
    """ An element that is a reference to a symbol. """

    def __init__(self, symbol_reference: SymbolReference):
        self._symbol_reference = symbol_reference

    @property
    def symbol_reference_if_is_symbol_reference(self) -> SymbolReference:
        return self._symbol_reference

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_reference,

    def resolve(self, symbols: SymbolTable) -> list:
        container = symbols.lookup(self._symbol_reference.name)
        value = container.resolver.resolve(symbols)
        if isinstance(value, StringValue):
            return [value]
        if isinstance(value, FileRef):
            return [csv.string_value_of_single_file_ref(value)]
        if isinstance(value, ListValue):
            return list(value.string_value_elements)
        raise TypeError('Unknown Symbol Value: ' + str(value))


class ListResolver(DataValueResolver):
    """
    Resolver who's resolved value is of type `ValueType.LIST` / :class:`ListValue`
    """

    def __init__(self, elements: Iterable[Element]):
        self._elements = tuple(elements)

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.LIST

    @property
    def value_type(self) -> ValueType:
        return ValueType.LIST

    @property
    def elements(self) -> Sequence[Element]:
        return self._elements

    @property
    def references(self) -> Sequence[SymbolReference]:
        ret_val = []
        for string_resolver in self._elements:
            ret_val.extend(string_resolver.references)
        return ret_val

    def resolve(self, symbols: SymbolTable) -> ListValue:
        value_elements = []
        for resolver_element in self._elements:
            value_elements.extend(resolver_element.resolve(symbols))
        return ListValue(value_elements)
