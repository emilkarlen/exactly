from exactly_lib.symbol.string_value import StringValue
from exactly_lib.symbol.value_structure import SymbolValueResolver, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringFragmentResolver:
    """
    A part of the value of a StringResolver.
    """

    @property
    def is_string_constant(self) -> bool:
        return False

    @property
    def is_symbol(self) -> bool:
        return False


class StringConstantFragmentResolver(StringFragmentResolver):
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


class StringSymbolFragmentResolver(StringFragmentResolver):
    """
    A fragment that represents a reference to a symbol.
    """

    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    @property
    def is_symbol(self) -> bool:
        return True

    @property
    def symbol_name(self) -> str:
        return self._symbol_name


class StringResolver(SymbolValueResolver):
    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING

    def resolve(self, symbols: SymbolTable) -> str:
        raise NotImplementedError()

    def resolve_string_value(self, symbols: SymbolTable) -> StringValue:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        raise NotImplementedError()

    @property
    def fragments(self) -> tuple:
        """
        The sequence of fragments that makes up the value.

        The resolved value is the concatenation of all fragments.

        :rtype: (`StringFragmentResolver`)
        """
        return ()

    def __str__(self):
        return str(type(self))
