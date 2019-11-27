from abc import ABC, abstractmethod

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.type_system.logic.files_matcher import FilesMatcherDdv
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FilesMatcherSdv(LogicTypeSdv, ABC):
    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_MATCHER

    @abstractmethod
    def validator(self) -> SdvValidator:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        pass
