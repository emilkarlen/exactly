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

    def __init__(self,
                 direct: ValueRestriction,
                 indirect: ValueRestriction = None):
        self._direct = direct
        self._indirect = indirect

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
        result = self._direct.is_satisfied_by(symbol_table, symbol_name, value)
        if result is not None:
            return result
        if self._indirect is None:
            return None
        return self._check_indirect(symbol_table, value.value.references)

    @property
    def direct(self) -> ValueRestriction:
        """
        Restriction on the symbol that is the direct target of the reference.
        """
        return self._direct

    @property
    def indirect(self) -> ValueRestriction:
        """
        Restriction that must be satisfied by the symbols references indirectly referenced.
        :rtype: None or ValueRestriction
        """
        return self._indirect

    def _check_indirect(self,
                        symbol_table: SymbolTable,
                        references: list) -> str:
        for reference in references:
            symbol_value = symbol_table.lookup(reference.name)
            result = self._indirect.is_satisfied_by(symbol_table, reference.name, symbol_value)
            if result is not None:
                return result
            result = self._check_indirect(symbol_table, symbol_value.value.references)
            if result is not None:
                return result
        return None

    def _check_every_node(self,
                          symbol_table: SymbolTable,
                          symbol_name: str,
                          value: ValueContainer) -> str:
        result = self._indirect.is_satisfied_by(symbol_table, symbol_name, value)
        if result is not None:
            return result
        for reference in value.value.references:
            symbol = symbol_table.lookup(reference.name)
            result = self._check_every_node(symbol_table, reference.name, symbol)
            if result is not None:
                return result
        return None
