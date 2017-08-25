from exactly_lib.named_element.resolver_structure import NamedElementContainer, ElementType
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
                        container: NamedElementContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError('abstract method')


class InvalidElementTypeFailure(FailureInfo):
    def __init__(self,
                 expected: ElementType,
                 actual: ElementType):
        self.actual = actual
        self.expected = expected


class ElementTypeRestriction(ReferenceRestrictions):
    def __init__(self, element_type: ElementType):
        self._element_type = element_type

    @property
    def element_type(self) -> ElementType:
        return self._element_type

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedElementContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        if container.resolver.element_type is self._element_type:
            return None
        else:
            return InvalidElementTypeFailure(self._element_type,
                                             container.resolver.element_type)


class SymbolReferenceRestrictions(ReferenceRestrictions):
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedElementContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError('abstract method')
