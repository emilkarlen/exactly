from exactly_lib.symbol.value_structure import ValueContainer
from exactly_lib.util.symbol_table import SymbolTable


class ValueRestriction:
    """
    A restriction on a value in the symbol table, that is applied by the frame work -
    i.e. not by specific instructions.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, symbol_name: str, value: ValueContainer) -> str:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError()


class ReferenceRestrictions:
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: ValueContainer) -> str:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError()
