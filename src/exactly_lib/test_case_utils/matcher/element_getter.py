from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.matcher.matcher import T
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class ElementGetter(Generic[MODEL, T], ABC):
    @abstractmethod
    def get_from(self, model: MODEL) -> T:
        """
        :raises HardErrorException
        """
        pass


class ElementGetterValue(Generic[MODEL, T], ABC):
    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> ElementGetter[MODEL, T]:
        pass


class ElementGetterResolver(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ElementGetterValue[MODEL, T]:
        pass

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.ConstantSuccessValidator()
