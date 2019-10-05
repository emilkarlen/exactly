from typing import Sequence, Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver, \
    FilesMatcherModel, FilesMatcherValue, FilesMatcher, FilesMatcherConstructor
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation as validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.test_case_utils.files_matcher.impl.validator_for_file_matcher import \
    resolver_validator_for_file_matcher
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


def sub_set_selection_matcher(selector: FileMatcherResolver,
                              matcher_on_selection: FilesMatcherResolver) -> FilesMatcherResolver:
    return _SubSetSelectorMatcherResolver(selector,
                                          matcher_on_selection)


class _SubSetSelectorMatcher(FilesMatcher):
    NAME = 'on ' + instruction_arguments.SELECTION_OPTION.name.long

    def __init__(self,
                 selector: FileMatcher,
                 matcher_on_selection: FilesMatcher):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def negation(self) -> FilesMatcher:
        return _SubSetSelectorMatcher(
            self._selector,
            self._matcher_on_selection.negation,
        )

    def matches_emr(self,
                    files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._matcher_on_selection.matches_emr(
            files_source.sub_set(self._selector),
        )

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        result = self._matcher_on_selection.matches_w_trace(
            model.sub_set(self._selector),
        )

        return self._new_tb() \
            .append_details(_SelectionDetailsRenderer(self._selector)) \
            .append_child(result.trace) \
            .build_result(result.value)


class _SelectionDetailsRenderer(DetailsRenderer):
    def __init__(self, selector: FileMatcher):
        self._selector = selector

    def render(self) -> Sequence[Detail]:
        return [tree.StringDetail(self._selector.option_description)]


class _SubSetSelectorMatcherValue(FilesMatcherValue):
    def __init__(self,
                 selector: FileMatcherValue,
                 matcher_on_selection: FilesMatcherValue,
                 ):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FilesMatcherConstructor:
        selector = self._selector.value_of_any_dependency(tcds)
        matcher_on_selection = self._matcher_on_selection.value_of_any_dependency(tcds)

        def mk_matcher(tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
            return _SubSetSelectorMatcher(
                selector,
                matcher_on_selection.construct(tmp_files_space),
            )

        return files_matchers.ConstructorFromFunction(mk_matcher)


class _SubSetSelectorMatcherResolver(FilesMatcherResolver):
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
