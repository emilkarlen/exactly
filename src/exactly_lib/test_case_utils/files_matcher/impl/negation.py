from typing import Sequence, Optional

from exactly_lib.definitions import expression
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherConstructor, \
    FilesMatcherDdv
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


def negation_matcher(matcher_to_negate: FilesMatcherSdv) -> FilesMatcherSdv:
    return _NegationMatcherSdv(matcher_to_negate)


class _NegationMatcher(FilesMatcher):
    def __init__(self, matcher_to_negate: FilesMatcher):
        self._matcher_to_negate = matcher_to_negate

    @property
    def name(self) -> str:
        return expression.NOT_OPERATOR_NAME

    @property
    def negation(self) -> FilesMatcher:
        return self._matcher_to_negate

    def matches_emr(self,
                    files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._matcher_to_negate.negation.matches_emr(files_source)

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        un_negated = self._matcher_to_negate.matches_w_trace(model)

        return self._new_tb().append_child(un_negated.trace).build_result(not un_negated.value)


class _NegationMatcherDdv(FilesMatcherDdv):
    def __init__(self, matcher_to_negate: FilesMatcherDdv):
        self._matcher_to_negate = matcher_to_negate

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherConstructor:
        matcher_to_negate = self._matcher_to_negate.value_of_any_dependency(tcds)

        def mk_matcher(tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
            return _NegationMatcher(
                matcher_to_negate.construct(tmp_files_space),
            )

        return files_matchers.ConstructorFromFunction(mk_matcher)


class _NegationMatcherSdv(FilesMatcherSdv):
    def __init__(self, matcher_to_negate: FilesMatcherSdv):
        self._matcher_to_negate = matcher_to_negate

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher_to_negate.references

    def validator(self) -> SdvValidator:
        return self._matcher_to_negate.validator()

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return _NegationMatcherDdv(self._matcher_to_negate.resolve(symbols))
