from enum import Enum

from exactly_lib.symbol.string_value import StringValue
from exactly_lib.symbol.value_structure import Value
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


class ValueType(Enum):
    STRING = 0
    PATH = 1


class SymbolValueResolver(Value):
    """
    Base class for values in the symbol table used by Exactly.
    """

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        """Values in the symbol table used by this object."""
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable):
        """
        Resolves the value given a symbol table.
        :rtype: Depends on the concrete value.
        """
        raise NotImplementedError()


class StringFragment:
    """
    A part of the value of a StringResolver.
    """

    @property
    def is_string_constant(self) -> bool:
        return False

    @property
    def is_symbol(self) -> bool:
        return False


class StringConstantFragment(StringFragment):
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


class StringSymbolFragment(StringFragment):
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

        :rtype: (`StringFragment`)
        """
        return ()

    def __str__(self):
        return str(type(self))


class FileRefResolver(SymbolValueResolver):
    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        raise NotImplementedError()

    def __str__(self):
        return str(type(self))


class ValueVisitor:
    """
    Visitor of `Value`
    """

    def visit(self, value: Value):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileRefResolver):
            return self._visit_file_ref(value)
        if isinstance(value, StringResolver):
            return self._visit_string(value)
        raise TypeError('Unknown {}: {}'.format(Value, str(value)))

    def _visit_string(self, value: StringResolver):
        raise NotImplementedError()

    def _visit_file_ref(self, value: FileRefResolver):
        raise NotImplementedError()
