from typing import Sequence, Optional

from exactly_lib.definitions.primitives import files_matcher
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver, \
    FilesMatcherModel, FilesMatcherValue, FilesMatcher, FilesMatcherConstructor
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.test_case_utils.files_matcher.impl.files_matchers import FilesMatcherResolverBase
from exactly_lib.test_case_utils.matcher.applier import MatcherApplier
from exactly_lib.test_case_utils.matcher.element_getter import ElementGetter
from exactly_lib.test_case_utils.matcher.impls.err_msg import ErrorMessageResolverForFailure
from exactly_lib.test_case_utils.matcher.matcher import MatcherResolver, MatcherValue
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace
from exactly_lib.util import logic_types
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def resolver(matcher: MatcherResolver[int]) -> FilesMatcherResolver:
    return _NumFilesMatcherResolver(matcher)


class _FilesMatcher(FilesMatcher):
    def __init__(self,
                 expectation_type: ExpectationType,
                 matcher: MatcherWTrace[int]):
        self._expectation_type = expectation_type
        self._matcher = matcher

    @property
    def name(self) -> str:
        return files_matcher.NUM_FILES_CHECK_ARGUMENT

    @property
    def negation(self) -> FilesMatcher:
        return _FilesMatcher(
            logic_types.negation(self._expectation_type),
            self._matcher,
        )

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        matcher_applier = self._matcher_applier()

        failure = matcher_applier.matches_w_failure(files_source)

        return (
            ErrorMessageResolverForFailure(
                files_source.error_message_info.property_descriptor(config.NUM_FILES_PROPERTY_NAME),
                failure,
            )
            if failure
            else
            None
        )

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return self._matcher_applier().matches_w_trace(model)

    def _matcher_applier(self, ) -> MatcherApplier[FilesMatcherModel, int]:
        matcher = self._matcher
        if self._expectation_type is ExpectationType.NEGATIVE:
            matcher = matcher.negation

        return MatcherApplier(matcher, _ElementGetter())


class _NumFilesMatcherValue(FilesMatcherValue):
    def __init__(self,
                 matcher: MatcherValue[int]):
        self._matcher = matcher

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FilesMatcherConstructor:
        return files_matchers.ConstantConstructor(
            _FilesMatcher(
                ExpectationType.POSITIVE,
                self._matcher.value_of_any_dependency(tcds),
            ),
        )


class _NumFilesMatcherResolver(FilesMatcherResolverBase):
    def __init__(self,
                 matcher: MatcherResolver[int],
                 ):
        self._matcher = matcher

        super().__init__(matcher.validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher.references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _NumFilesMatcherValue(
            self._matcher.resolve(symbols),
        )


class _ElementGetter(ElementGetter[FilesMatcherModel, int]):
    @property
    def name(self) -> str:
        return files_matcher.NUM_FILES_CHECK_ARGUMENT

    def get_from(self, model: FilesMatcherModel) -> int:
        return len(list(model.files()))
