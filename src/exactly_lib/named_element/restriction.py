from exactly_lib.named_element.resolver_structure import NamedValueContainer
from exactly_lib.util.symbol_table import SymbolTable


class FailureInfo:
    pass


class ReferenceRestrictions:
    """
    Restrictions on a referenced named element
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedValueContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError('abstract method')


class InvalidElementTypeFailure(FailureInfo):
    pass


class FileSelectorReferenceRestrictions(ReferenceRestrictions):
    """
    Restrictions on a reference file selector
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedValueContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        container.resolver
        raise NotImplementedError('abstract method')


class SymbolReferenceRestrictions(ReferenceRestrictions):
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedValueContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError()
