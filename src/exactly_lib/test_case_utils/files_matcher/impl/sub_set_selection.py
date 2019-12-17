from typing import Sequence, Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherConstructor, \
    FilesMatcherDdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


def sub_set_selection_matcher(selector: FileMatcherSdv,
                              matcher_on_selection: FilesMatcherSdv) -> FilesMatcherSdv:
    return _SubSetSelectorMatcherSdv(selector,
                                     matcher_on_selection)


class _SubSetSelectorMatcher(WithCachedNameAndTreeStructureDescriptionBase, FilesMatcher):
    NAME = ' '.join([
        option_syntax.option_syntax(instruction_arguments.SELECTION_OPTION.name),
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    ])

    def __init__(self,
                 selector: FileMatcher,
                 matcher_on_selection: FilesMatcher):
        WithCachedNameAndTreeStructureDescriptionBase.__init__(self)
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

        return (
            self._new_tb()
                .append_details(self._details_renderer_of(self._selector))
                .append_child(result.trace)
                .build_result(result.value)
        )

    def _structure(self) -> StructureRenderer:
        return (
            self._new_structure_builder()
                .append_details(self._details_renderer_of(self._selector))
                .append_child(self._node_renderer_of(self._matcher_on_selection))
                .build()
        )


class _SubSetSelectorMatcherDdv(FilesMatcherDdv):
    def __init__(self,
                 selector: FileMatcherDdv,
                 matcher_on_selection: FilesMatcherDdv,
                 ):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection
        self._validator = ddv_validators.AndValidator([
            selector.validator,
            matcher_on_selection.validator,
        ])

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherConstructor:
        selector_adv = self._selector.value_of_any_dependency(tcds)
        matcher_on_selection = self._matcher_on_selection.value_of_any_dependency(tcds)

        def mk_matcher(tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
            return _SubSetSelectorMatcher(
                selector_adv.applier(ApplicationEnvironment(tmp_files_space)),
                matcher_on_selection.construct(tmp_files_space),
            )

        return files_matchers.ConstructorFromFunction(mk_matcher)


class _SubSetSelectorMatcherSdv(FilesMatcherSdv):
    def __init__(self,
                 selector: FileMatcherSdv,
                 matcher_on_selection: FilesMatcherSdv):
        self._selector = selector
        self._matcher_on_selection = matcher_on_selection
        self._references = references_from_objects_with_symbol_references([
            selector, matcher_on_selection
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return _SubSetSelectorMatcherDdv(
            self._selector.resolve(symbols),
            self._matcher_on_selection.resolve(symbols)
        )
