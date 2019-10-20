from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class MatcherValue(Generic[T], ABC):
    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> MatcherWTraceAndNegation[T]:
        pass


class MatcherResolver(Generic[T], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherValue[T]:
        pass

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.ConstantSuccessValidator()
