from typing import Sequence

from exactly_lib.symbol import symbol_usage as su, resolver_structure as struct
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data import string_value as sv, concrete_string_values as csv
from exactly_lib.type_system.data.concrete_string_values import StrValueTransformer, TransformedStringFragment, \
    StringValueFragment
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


class FileRefAsStringFragmentResolver(StringFragmentResolver):
    def __init__(self, file_ref: FileRefResolver):
        self._file_ref = file_ref

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._file_ref.references

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        return csv.FileRefFragment(self._file_ref.resolve(symbols))


class ListAsStringFragmentResolver(StringFragmentResolver):
    def __init__(self, list_resolver: ListResolver):
        self._list_resolver = list_resolver

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._list_resolver.references

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        return csv.ListValueFragment(self._list_resolver.resolve(symbols))


class TransformedStringFragmentResolver(StringFragmentResolver):
    """
    A fragment who's string is transformed by a function.
    """

    def __init__(self,
                 string_resolver: StringFragmentResolver,
                 transformer: StrValueTransformer):
        self._string_resolver = string_resolver
        self._transformer = transformer

    @property
    def is_string_constant(self) -> bool:
        return self._string_resolver.is_string_constant

    @property
    def string_constant(self) -> str:
        return self._transformer(self._string_resolver.string_constant)

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        return TransformedStringFragment(StringValueFragment(self._string_resolver.resolve(symbols)),
                                         self._transformer)

    @property
    def references(self) -> list:
        return self._string_resolver.references

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return self.resolve(environment.symbols).value_of_any_dependency(environment)
