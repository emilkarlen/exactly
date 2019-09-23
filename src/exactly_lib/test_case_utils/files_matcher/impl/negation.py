from typing import Sequence, Optional

from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver, \
    FilesMatcherModel, FilesMatcherValue, FilesMatcher, FilesMatcherConstructor
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


def negation_matcher(matcher_to_negate: FilesMatcherResolver) -> FilesMatcherResolver:
    return _NegationMatcherResolver(matcher_to_negate)


class _NegationMatcher(FilesMatcher):
    def __init__(self, matcher_to_negate: FilesMatcher):
        self._matcher_to_negate = matcher_to_negate

    @property
    def negation(self) -> FilesMatcher:
        return self._matcher_to_negate

    def matches(self,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self._matcher_to_negate.negation.matches(files_source)


class _NegationMatcherValue(FilesMatcherValue):
    def __init__(self, matcher_to_negate: FilesMatcherValue):
        self._matcher_to_negate = matcher_to_negate

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FilesMatcherConstructor:
        matcher_to_negate = self._matcher_to_negate.value_of_any_dependency(tcds)

        def mk_matcher(tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
            return _NegationMatcher(
                matcher_to_negate.construct(tmp_files_space),
            )

        return files_matchers.ConstructorFromFunction(mk_matcher)


class _NegationMatcherResolver(FilesMatcherResolver):
    def __init__(self, matcher_to_negate: FilesMatcherResolver):
        self._matcher_to_negate = matcher_to_negate

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher_to_negate.references

    def validator(self) -> PreOrPostSdsValidator:
        return self._matcher_to_negate.validator()

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _NegationMatcherValue(self._matcher_to_negate.resolve(symbols))
