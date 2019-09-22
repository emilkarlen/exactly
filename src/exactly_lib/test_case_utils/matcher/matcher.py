from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence, Optional

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class Failure(Generic[T]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected: str,
                 actual: T):
        self.expectation_type = expectation_type
        self.expected = expected
        self.actual = actual


class Matcher(Generic[T], ABC):
    @abstractmethod
    def matches(self, model: T) -> Optional[Failure[T]]:
        """
        :raises HardErrorException
        """
        pass

    @property
    @abstractmethod
    def negation(self) -> 'Matcher':
        pass


class MatcherValue(Generic[T], ABC):
    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> Matcher[T]:
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
