from typing import Sequence, Optional

from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver, \
    Environment, FilesMatcherModel, FilesMatcherValue
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation as validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.files_matcher.impl.validator_for_file_matcher import \
    resolver_validator_for_file_matcher
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue
from exactly_lib.util.symbol_table import SymbolTable


def sub_set_selection_matcher(selector: FileMatcherResolver,
                              matcher_on_selection: FilesMatcherResolver) -> FilesMatcherResolver:
    return _SubSetSelectorMatcher(selector,
                                  matcher_on_selection)


class _SubSetSelectorMatcherValue(FilesMatcherValue):
    def __init__(self,
                 selector: FileMatcherValue,
                 matcher_on_selection: FilesMatcherValue):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection

    @property
    def negation(self) -> FilesMatcherValue:
        return _SubSetSelectorMatcherValue(
            self._selector,
            self._matcher_on_selection.negation,
        )

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._matcher_on_selection.matches(environment,
                                                  files_source.sub_set(self._selector))


class _SubSetSelectorMatcher(FilesMatcherResolver):
    def __init__(self,
                 selector: FileMatcherResolver,
                 matcher_on_selection: FilesMatcherResolver):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection
        self._references = references_from_objects_with_symbol_references([
            selector, matcher_on_selection
        ])

        self._validator = validation.AndValidator([
            resolver_validator_for_file_matcher(selector),
            self._matcher_on_selection.validator(),
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _SubSetSelectorMatcherValue(
            self._selector.resolve(symbols),
            self._matcher_on_selection.resolve(symbols)
        )

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        selector = self._selector.resolve(environment.symbols)
        matcher_on_selection = self.resolve(environment.symbols)
        return matcher_on_selection.matches(environment,
                                            files_source.sub_set(selector))
