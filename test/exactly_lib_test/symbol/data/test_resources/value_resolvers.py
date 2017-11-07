from exactly_lib.help_texts.type_system import DATA_TYPE_2_VALUE_TYPE
from exactly_lib.symbol import symbol_usage
from exactly_lib.symbol.data import string_resolver
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


def string_resolver_of_single_symbol_reference(
        symbol_name: str,
        restrictions: ReferenceRestrictions = is_any_data_type()) -> StringResolver:
    symbol_reference = symbol_usage.SymbolReference(symbol_name,
                                                    restrictions)
    fragments = [
        string_resolver.SymbolStringFragmentResolver(symbol_reference)
    ]
    return StringResolver(tuple(fragments))


class ConstantValueResolver(DataValueResolver):
    def __init__(self,
                 value_type: DataValueType,
                 value: DirDependentValue):
        self._value_type = value_type
        self._value = value

    @property
    def data_value_type(self) -> DataValueType:
        return self._value_type

    @property
    def value_type(self) -> ValueType:
        return DATA_TYPE_2_VALUE_TYPE[self._value_type]

    @property
    def references(self) -> list:
        return []

    def resolve(self, symbols: SymbolTable) -> DirDependentValue:
        return self._value
