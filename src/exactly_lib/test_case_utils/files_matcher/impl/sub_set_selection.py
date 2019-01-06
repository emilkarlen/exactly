from typing import Sequence, Optional

from exactly_lib.symbol.files_matcher import FilesMatcherResolver, \
    Environment, FilesMatcherModel
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.error_message import ErrorMessageResolver


def sub_set_selection_matcher(selector: FileMatcherResolver,
                              matcher_on_selection: FilesMatcherResolver) -> FilesMatcherResolver:
    return _SubSetSelectorMatcher(selector,
                                  matcher_on_selection)


class _SubSetSelectorMatcher(FilesMatcherResolver):
    def __init__(self,
                 selector: FileMatcherResolver,
                 matcher_on_selection: FilesMatcherResolver):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection
        self._references = references_from_objects_with_symbol_references([
            selector, matcher_on_selection
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def validator(self) -> PreOrPostSdsValidator:
        return self._matcher_on_selection.validator()

    @property
    def negation(self) -> FilesMatcherResolver:
        return _SubSetSelectorMatcher(
            self._selector,
            self._matcher_on_selection.negation
        )

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._matcher_on_selection.matches(environment,
                                                  files_source.sub_set(self._selector))
