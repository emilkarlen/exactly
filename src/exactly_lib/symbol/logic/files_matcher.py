from abc import ABC, abstractmethod

from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.files_matcher import FilesMatcherDdv
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FilesMatcherResolver(LogicValueResolver, ABC):
    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_MATCHER

    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        pass
