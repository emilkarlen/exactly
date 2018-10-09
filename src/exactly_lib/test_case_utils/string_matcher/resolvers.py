from typing import Sequence, Callable, Set

from exactly_lib.symbol import lookups
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic import string_matcher_values
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherConstantResolver(StringMatcherResolver):
    """
    A :class:`StringMatcherResolver` that is a constant :class:`StringMatcher`
    """

    def __init__(self, value: StringMatcher):
        self._value = string_matcher_values.StringMatcherConstantValue(value)

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class StringMatcherConstantOfValueResolver(StringMatcherResolver):
    """
    A :class:`StringMatcherResolver` that is a constant :class:`StringMatcherValue`
    """

    def __init__(self, value: StringMatcherValue):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class StringMatcherResolverFromParts(StringMatcherResolver):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 validator: PreOrPostSdsValidator,
                 resolving_dependencies: Callable[[SymbolTable], Set[DirectoryStructurePartition]],
                 matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], StringMatcher]):
        self._matcher = matcher
        self._resolving_dependencies = resolving_dependencies
        self._validator = validator
        self._references = references

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        def get_matcher(tcds: HomeAndSds) -> StringMatcher:
            environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            return self._matcher(environment)

        return StringMatcherValueFromParts(self._resolving_dependencies(symbols),
                                           get_matcher)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def __str__(self):
        return str(type(self))


class StringMatcherValueFromParts(StringMatcherValue):
    def __init__(self,
                 resolving_dependencies: Set[DirectoryStructurePartition],
                 matcher: Callable[[HomeAndSds], StringMatcher]):
        self._matcher = matcher
        self._resolving_dependencies = resolving_dependencies

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return self._matcher(home_and_sds)


class StringMatcherReferenceResolver(StringMatcherResolver):
    """
    A :class:`StringMatcherResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.STRING_MATCHER))]

    def resolve(self, symbols: SymbolTable) -> StringMatcher:
        resolver = lookups.lookup_string_matcher(symbols,
                                                 self._name_of_referenced_resolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''
