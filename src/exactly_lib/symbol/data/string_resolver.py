from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data import string_value as sv
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringFragmentResolver(DataValueResolver):
    """
    A part of the value of a StringResolver.
    """

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.STRING

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING

    @property
    def is_string_constant(self) -> bool:
        return False

    @property
    def string_constant(self) -> str:
        """
        :raises ValueError: This object does not represent a string constant
        :rtype str
        """
        raise ValueError('The object is not a string constant')

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        raise NotImplementedError()


class StringResolver(DataValueResolver):
    """
    Resolver who's resolved value is of type `ValueType.STRING` / :class:`StringValue`
    """

    def __init__(self, fragment_resolvers: Sequence[StringFragmentResolver]):
        self._fragment_resolvers = fragment_resolvers

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.STRING

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING

    def resolve(self, symbols: SymbolTable) -> sv.StringValue:
        fragments = [fr.resolve(symbols)
                     for fr in self._fragment_resolvers]
        return sv.StringValue(tuple(fragments))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references(self._fragment_resolvers)

    @property
    def has_fragments(self) -> bool:
        """
        Whether there are any fragments or not.
        :return:
        """
        return len(self._fragment_resolvers) != 0

    @property
    def fragments(self) -> Sequence[StringFragmentResolver]:
        """
        The sequence of fragments that makes up the value.

        The resolved value is the concatenation of all fragments.
        """
        return self._fragment_resolvers

    @property
    def is_string_constant(self) -> bool:
        """
        Tells if the object does not depend on any symbols
        """
        return all(map(lambda x: x.is_string_constant, self._fragment_resolvers))

    @property
    def string_constant(self) -> str:
        """
        Precondition: is_string_constant

        :return: The constant string that this object represents
        """
        fragments = [fragment_resolver.string_constant
                     for fragment_resolver in self._fragment_resolvers]
        return ''.join(fragments)

    def __str__(self):
        return str(type(self))
