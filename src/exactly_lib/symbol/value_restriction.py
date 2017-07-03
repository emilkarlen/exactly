from exactly_lib.symbol.value_structure import ValueContainer
from exactly_lib.util.symbol_table import SymbolTable


class ValueRestrictionFailure(tuple):
    def __new__(cls,
                message: str,
                how_to_fix: str = ''):
        return tuple.__new__(cls, (message, how_to_fix))

    @property
    def message(self) -> str:
        return self[0]

    @property
    def how_to_fix(self) -> str:
        return self[1]


class ValueRestriction:
    """
    A restriction on a value in the symbol table, that is applied by the frame work -
    i.e. not by specific instructions.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str, value: ValueContainer) -> ValueRestrictionFailure:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :rtype ValueRestrictionFailure
        :return: None if satisfied
        """
        raise NotImplementedError()


class FailureInfo:
    pass


class ReferenceRestrictions:
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError()
