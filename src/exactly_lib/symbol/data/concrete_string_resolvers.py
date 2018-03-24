from typing import Sequence

from exactly_lib.symbol import symbol_usage as su, resolver_structure as struct
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver, StringResolver
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data import string_value as sv, concrete_string_values as csv
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.util.symbol_table import SymbolTable


class ConstantStringFragmentResolver(StringFragmentResolver):
    """
    A fragment that is a string constant.
    """

    def __init__(self, constant: str):
        self._constant = constant

    @property
    def is_string_constant(self) -> bool:
        return True

    @property
    def string_constant(self) -> str:
        return self._constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        return csv.ConstantFragment(self._constant)


class SymbolStringFragmentResolver(StringFragmentResolver):
    """
    A fragment that represents a reference to a symbol.
    """

    def __init__(self, symbol_reference: su.SymbolReference):
        self._symbol_reference = symbol_reference

    @property
    def is_symbol(self) -> bool:
        return True

    @property
    def symbol_name(self) -> str:
        return self._symbol_reference.name

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_reference,

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        container = symbols.lookup(self._symbol_reference.name)
        assert isinstance(container, struct.SymbolContainer), 'Value in SymTbl must be SymbolContainer'
        value_resolver = container.resolver
        assert isinstance(value_resolver, DataValueResolver), 'Value must be a DataValueResolver'
        value = value_resolver.resolve(symbols)
        if isinstance(value, sv.StringValue):
            return csv.StringValueFragment(value)
        elif isinstance(value, FileRef):
            return csv.FileRefFragment(value)
        elif isinstance(value, ListValue):
            return csv.ListValueFragment(value)
        else:
            raise TypeError('Not a {}: {}'.format(str(DataValueResolver),
                                                  value))


def string_constant(string: str) -> StringResolver:
    return StringResolver((ConstantStringFragmentResolver(string),))


def symbol_reference(symbol_ref: su.SymbolReference) -> StringResolver:
    return StringResolver((SymbolStringFragmentResolver(symbol_ref),))


def resolver_from_fragments(fragments: Sequence[StringFragmentResolver]) -> StringResolver:
    return StringResolver(tuple(fragments))
