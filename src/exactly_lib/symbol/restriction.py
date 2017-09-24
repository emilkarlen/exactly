from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.type_system import value_type
from exactly_lib.type_system.value_type import TypeCategory, ValueType
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
                        container: SymbolContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError('abstract method')


class InvalidTypeCategoryFailure(FailureInfo):
    def __init__(self,
                 expected: TypeCategory,
                 actual: TypeCategory):
        self.actual = actual
        self.expected = expected


class InvalidValueTypeFailure(FailureInfo):
    def __init__(self,
                 expected: ValueType,
                 actual: ValueType):
        self.actual = actual
        self.expected = expected


class TypeCategoryRestriction(ReferenceRestrictions):
    def __init__(self, type_category: TypeCategory):
        self._type_category = type_category

    @property
    def type_category(self) -> TypeCategory:
        return self._type_category

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        if container.resolver.type_category is self._type_category:
            return None
        else:
            return InvalidTypeCategoryFailure(self._type_category,
                                              container.resolver.type_category)


class ValueTypeRestriction(ReferenceRestrictions):
    def __init__(self, expected: ValueType):
        self._expected = expected

    @property
    def type_category(self) -> TypeCategory:
        return value_type.VALUE_TYPE_2_TYPE_CATEGORY[self._expected]

    @property
    def value_type(self) -> ValueType:
        return self._expected

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        if container.resolver.value_type is self._expected:
            return None
        else:
            return InvalidValueTypeFailure(self._expected,
                                           container.resolver.value_type)


class DataTypeReferenceRestrictions(ReferenceRestrictions):
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError('abstract method')
