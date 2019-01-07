from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, FilesMatcherValue
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironment
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import ValidatorOfReferredResolverBase, PreOrPostSdsValidator
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


def symbol_reference_matcher(name_of_referenced_resolver: str) -> FilesMatcherResolver:
    return _ReferenceResolver(name_of_referenced_resolver)


class _ReferenceResolver(FilesMatcherResolver):
    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.FILES_MATCHER))]
        self._validator = _ValidatorOfReferredResolver(name_of_referenced_resolver)

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        resolver = lookups.lookup_files_matcher(symbols, self._name_of_referenced_resolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class _ValidatorOfReferredResolver(ValidatorOfReferredResolverBase):
    def _referred_validator(self, environment: PathResolvingEnvironment) -> PreOrPostSdsValidator:
        referred_matcher_resolver = lookups.lookup_files_matcher(environment.symbols, self.symbol_name)
        return referred_matcher_resolver.validator()
