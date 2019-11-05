from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_value_validation
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')
T = TypeVar('T')


class PropertyGetter(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_from(self, model: MODEL) -> T:
        """
        :raises HardErrorException
        """
        pass


class PropertyGetterValue(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> PropertyGetter[MODEL, T]:
        pass

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return pre_or_post_value_validation.constant_success_validator()


class PropertyGetterResolver(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> PropertyGetterValue[MODEL, T]:
        pass
