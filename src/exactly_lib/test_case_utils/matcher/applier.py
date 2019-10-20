from typing import Generic, TypeVar, Optional, Sequence

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.matcher.element_getter import ElementGetter, ElementGetterValue, ElementGetterResolver
from exactly_lib.test_case_utils.matcher.matcher import T, MatcherValue, MatcherResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace, Failure
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class MatcherApplier(Generic[MODEL, T]):
    def __init__(self,
                 matcher: MatcherWTrace[T],
                 model_adapter: ElementGetter[MODEL, T],
                 ):
        self._matcher = matcher
        self._model_adapter = model_adapter

    def matches_w_failure(self, model: MODEL) -> Optional[Failure[T]]:
        """
        :raises HardErrorException
        """
        return self._matcher.matches_w_failure(
            self._model_adapter.get_from(model),
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        """
        :raises HardErrorException
        """
        return self._matcher.matches_w_trace(
            self._model_adapter.get_from(model),
        )


class MatcherApplierValue(Generic[MODEL, T]):
    def __init__(self,
                 matcher: MatcherValue[T],
                 model_adapter: ElementGetterValue[MODEL, T],
                 ):
        self._matcher = matcher
        self._model_adapter = model_adapter

    def value_of_any_dependency(self, tcds: HomeAndSds) -> MatcherApplier[MODEL, T]:
        return MatcherApplier(
            self._matcher.value_of_any_dependency(tcds),
            self._model_adapter.value_of_any_dependency(tcds),
        )


class MatcherApplierResolver(Generic[MODEL, T]):
    def __init__(self,
                 matcher: MatcherResolver[T],
                 model_adapter: ElementGetterResolver[MODEL, T],
                 ):
        self._matcher = matcher
        self._model_adapter = model_adapter
        self._references = list(matcher.references) + list(model_adapter.references)
        self._validator = pre_or_post_validation.all_of([
            self._matcher.validator,
            self._model_adapter.validator,
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> MatcherApplierValue[MODEL, T]:
        return MatcherApplierValue(
            self._matcher.resolve(symbols),
            self._model_adapter.resolve(symbols),
        )
