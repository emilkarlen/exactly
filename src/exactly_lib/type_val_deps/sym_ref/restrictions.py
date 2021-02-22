from typing import Optional, Sequence

from exactly_lib.symbol.err_msg import error_messages
from exactly_lib.symbol.sdv_structure import SymbolContainer, Failure, ReferenceRestrictions
from exactly_lib.symbol.value_type import TypeCategory, ValueType, TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.symbol_table import SymbolTable


class InvalidTypeCategoryFailure(Failure):
    def __init__(self,
                 expected: TypeCategory,
                 actual: TypeCategory,
                 ):
        self.actual = actual
        self.expected = expected

    def render(self,
               failing_symbol: str,
               symbols: SymbolTable,
               ) -> Sequence[MajorBlock]:
        value_restriction_failure = error_messages.invalid_type_msg(
            TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE[self.expected],
            failing_symbol,
            symbol_lookup.lookup_container(symbols, failing_symbol),
        )

        return value_restriction_failure.render_sequence()


class InvalidValueTypeFailure(Failure):
    def __init__(self, expected: Sequence[ValueType]):
        self._expected = expected

    def render(self,
               failing_symbol: str,
               symbols: SymbolTable,
               ) -> Sequence[MajorBlock]:
        value_restriction_failure = error_messages.invalid_type_msg(
            self._expected,
            failing_symbol,
            symbol_lookup.lookup_container(symbols, failing_symbol),
        )

        return value_restriction_failure.render_sequence()


class TypeCategoryRestriction(ReferenceRestrictions):
    def __init__(self, type_category: TypeCategory):
        self._type_category = type_category

    @property
    def type_category(self) -> TypeCategory:
        return self._type_category

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[Failure]:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        if container.type_category is self._type_category:
            return None
        else:
            return InvalidTypeCategoryFailure(self._type_category,
                                              container.type_category)


class ValueTypeRestriction(ReferenceRestrictions):
    def __init__(self, expected: Sequence[ValueType]):
        self._expected = expected

    @staticmethod
    def of_single(expected: ValueType) -> 'ValueTypeRestriction':
        return ValueTypeRestriction((expected,))

    @property
    def value_types(self) -> Sequence[ValueType]:
        return self._expected

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[Failure]:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        if container.value_type in self._expected:
            return None
        else:
            return InvalidValueTypeFailure(self._expected)


class DataTypeReferenceRestrictions(ReferenceRestrictions):
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[Failure]:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        raise NotImplementedError('abstract method')
