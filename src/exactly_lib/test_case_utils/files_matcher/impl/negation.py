from typing import Sequence, Optional

from exactly_lib.symbol.files_matcher import FilesMatcherResolver, \
    Environment, FilesMatcherModel, FilesMatcherValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util.symbol_table import SymbolTable


def negation_matcher(matcher_to_negate: FilesMatcherResolver) -> FilesMatcherResolver:
    return _NegationMatcher(matcher_to_negate)


class _NegationMatcherValue(FilesMatcherValue):
    def __init__(self, matcher_to_negate: FilesMatcherValue):
        self._matcher_to_negate = matcher_to_negate

    @property
    def negation(self) -> FilesMatcherValue:
        return self._matcher_to_negate

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._matcher_to_negate.negation.matches(environment,
                                                        files_source)


class _NegationMatcher(FilesMatcherResolver):
    def __init__(self, matcher_to_negate: FilesMatcherResolver):
        self._matcher_to_negate = matcher_to_negate

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher_to_negate.references

    def validator(self) -> PreOrPostSdsValidator:
        return self._matcher_to_negate.validator()

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _NegationMatcherValue(self._matcher_to_negate.resolve(symbols))
