from typing import Generic, TypeVar, Optional, Sequence

from exactly_lib.symbol.logic.resolver import T, MatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_value_validators
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterValue, \
    PropertyGetterResolver
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace, Failure, MatcherValue
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

    @property
    def option_description(self) -> str:
        return self._property_getter.name

    def structure(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._property_getter.name,
            None,
            (),
            (self._matcher.structure(),)
        )

    def matches_emr(self, model: T) -> Optional[ErrorMessageResolver]:
        return (
            None
            if self.matches_w_trace(model).value
            else
            err_msg_resolvers.constant('False')
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
                 property_getter: PropertyGetterValue[MODEL, T],
                 ):
        self._matcher = matcher
        self._property_getter = property_getter
        self._validator = pre_or_post_value_validators.all_of([
            self._matcher.validator,
            self._property_getter.validator,
        ])

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

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> PropertyMatcher[MODEL, T]:
        return PropertyMatcher(
            self._matcher.value_of_any_dependency(tcds),
            self._property_getter.value_of_any_dependency(tcds),
        )


class PropertyMatcherResolver(Generic[MODEL, T], MatcherResolver[MODEL]):
    def __init__(self,
                 matcher: MatcherResolver[T],
                 property_getter: PropertyGetterResolver[MODEL, T],
                 ):
        self._matcher = matcher
        self._property_getter = property_getter
        self._references = list(matcher.references) + list(property_getter.references)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> PropertyMatcherValue[MODEL, T]:
        return PropertyMatcherValue(
            self._matcher.resolve(symbols),
            self._property_getter.resolve(symbols),
        )
