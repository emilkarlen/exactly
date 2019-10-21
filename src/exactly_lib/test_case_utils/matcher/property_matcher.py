from typing import Generic, TypeVar, Optional, Sequence

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.matcher.matcher import T, MatcherValue, MatcherResolver
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterValue, \
    PropertyGetterResolver
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace, Failure
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class PropertyMatcher(Generic[MODEL, T], MatcherWTrace[MODEL]):
    """Matches a property of a model"""

    def __init__(self,
                 matcher: MatcherWTrace[T],
                 property_getter: PropertyGetter[MODEL, T],
                 ):
        self._matcher = matcher
        self._property_getter = property_getter

    @property
    def name(self) -> str:
        """TODO Temp helper that should be removed after usages removed"""
        return self._property_getter.name

    def structure(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._property_getter.name,
            None,
            (),
            (self._matcher.structure(),)
        )

    def matches_w_failure(self, model: MODEL) -> Optional[Failure[T]]:
        """
        :raises HardErrorException
        """
        return self._matcher.matches_w_failure(
            self._property_getter.get_from(model),
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        """
        :raises HardErrorException
        """
        matcher_result = self._matcher.matches_w_trace(self._property_getter.get_from(model))
        return MatchingResult(
            matcher_result.value,
            renderers.NodeRendererFromParts(
                self._property_getter.name,
                matcher_result.value,
                (),
                (matcher_result.trace,)
            )
        )


class PropertyMatcherValue(Generic[MODEL, T], MatcherValue[MODEL]):
    def __init__(self,
                 matcher: MatcherValue[T],
                 model_adapter: PropertyGetterValue[MODEL, T],
                 ):
        self._matcher = matcher
        self._model_adapter = model_adapter

    @property
    def name(self) -> str:
        """TODO Temp helper that should be removed after usages removed"""
        return self._model_adapter.name

    def structure(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._model_adapter.name,
            None,
            (),
            (self._matcher.structure(),)
        )

    def value_of_any_dependency(self, tcds: HomeAndSds) -> PropertyMatcher[MODEL, T]:
        return PropertyMatcher(
            self._matcher.value_of_any_dependency(tcds),
            self._model_adapter.value_of_any_dependency(tcds),
        )


class PropertyMatcherResolver(Generic[MODEL, T], MatcherResolver[MODEL]):
    def __init__(self,
                 matcher: MatcherResolver[T],
                 model_adapter: PropertyGetterResolver[MODEL, T],
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

    def resolve(self, symbols: SymbolTable) -> PropertyMatcherValue[MODEL, T]:
        return PropertyMatcherValue(
            self._matcher.resolve(symbols),
            self._model_adapter.resolve(symbols),
        )
