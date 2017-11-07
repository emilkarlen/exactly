from exactly_lib.symbol import resolver_structure as struct, symbol_usage as su
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.type_system.data import concrete_string_values as csv
from exactly_lib.type_system.data import string_value as sv
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
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

    @property
    def is_symbol(self) -> bool:
        return False

    @property
    def references(self) -> tuple:
        """
        Values in the symbol table used by this object.

        :type: (SymbolReference)
        """
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        raise NotImplementedError()


class ConstantStringFragmentResolver(StringFragmentResolver):
    """
    A fragment that is a string constant.
    """

    def __init__(self, string_constant: str):
        self._string_constant = string_constant

    @property
    def is_string_constant(self) -> bool:
        return True

    @property
    def string_constant(self) -> str:
        return self._string_constant

    @property
    def references(self) -> tuple:
        return ()

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        return csv.ConstantFragment(self._string_constant)


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
    def references(self) -> tuple:
        return self._symbol_reference,

    def resolve(self, symbols: SymbolTable) -> sv.StringFragment:
        container = symbols.lookup(self._symbol_reference.name)
        assert isinstance(container, struct.SymbolContainer), 'Value in SymTbl must be SymbolContainer'
        value_resolver = container.resolver
        assert isinstance(value_resolver, DataValueResolver), 'Value must be a SymbolValueResolver'
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


class StringResolver(DataValueResolver):
    """
    Resolver who's resolved value is of type `ValueType.STRING` / :class:`StringValue`
    """

    def __init__(self, fragment_resolvers: tuple):
        """
        :param fragment_resolvers: Tuple of `StringFragmentResolver`
        """
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
    def references(self) -> list:
        ret_val = []
        for fragment in self._fragment_resolvers:
            ret_val.extend(fragment.references)
        return ret_val

    @property
    def fragments(self) -> tuple:
        """
        The sequence of fragments that makes up the value.

        The resolved value is the concatenation of all fragments.

        :rtype: (`StringFragmentResolver`)
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


def string_constant(string: str) -> StringResolver:
    return StringResolver((ConstantStringFragmentResolver(string),))


def symbol_reference(symbol_ref: su.SymbolReference) -> StringResolver:
    return StringResolver((SymbolStringFragmentResolver(symbol_ref),))


def resolver_from_fragments(fragments: list) -> StringResolver:
    return StringResolver(tuple(fragments))
