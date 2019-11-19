from typing import Sequence

from exactly_lib.definitions.type_system import DATA_TYPE_2_VALUE_TYPE
from exactly_lib.symbol import symbol_usage
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import DependenciesAwareDdv
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


def string_sdv_of_single_symbol_reference(
        symbol_name: str,
        restrictions: ReferenceRestrictions = is_any_data_type()) -> StringSdv:
    symbol_reference = symbol_usage.SymbolReference(symbol_name,
                                                    restrictions)
    fragments = [
        string_sdvs.symbol_fragment(symbol_reference)
    ]
    return StringSdv(tuple(fragments))


class ConstantSdv(DataTypeSdv):
    def __init__(self,
                 value_type: DataValueType,
                 value: DependenciesAwareDdv):
        self._value_type = value_type
        self._value = value

    @property
    def data_value_type(self) -> DataValueType:
        return self._value_type

    @property
    def value_type(self) -> ValueType:
        return DATA_TYPE_2_VALUE_TYPE[self._value_type]

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> DependenciesAwareDdv:
        return self._value
