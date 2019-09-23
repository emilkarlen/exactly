from typing import Sequence, Optional

from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver, \
    Environment, FilesMatcherModel, FilesMatcherValue
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparison_structures
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.impl.files_matchers import FilesMatcherResolverBase
from exactly_lib.test_case_utils.matcher.applier import MatcherApplier
from exactly_lib.test_case_utils.matcher.element_getter import ElementGetter
from exactly_lib.test_case_utils.matcher.impls.err_msg import ErrorMessageResolverForFailure
from exactly_lib.test_case_utils.matcher.matcher import MatcherResolver, MatcherValue
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.util import logic_types
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def resolver(matcher: MatcherResolver[int]) -> FilesMatcherResolver:
    return _NumFilesMatcherResolver(ExpectationType.POSITIVE, matcher)


class _NumFilesMatcherValue(FilesMatcherValue):
    def __init__(self,
                 expectation_type: ExpectationType,
                 matcher: MatcherValue[int]):
        self._expectation_type = expectation_type
        self._matcher = matcher

    @property
    def negation(self) -> FilesMatcherValue:
        return _NumFilesMatcherValue(
            logic_types.negation(self._expectation_type),
            self._matcher,
        )

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        matcher_applier = self._matcher_applier(environment)

        failure = matcher_applier.apply(files_source)

        return (
            ErrorMessageResolverForFailure(
                files_source.error_message_info.property_descriptor(config.NUM_FILES_PROPERTY_NAME),
                failure,
            )
            if failure
            else
            None
        )

    def _matcher_applier(self, environment: Environment) -> MatcherApplier[FilesMatcherModel, int]:
        matcher = self._matcher.value_of_any_dependency(environment.path_resolving_environment.home_and_sds)
        if self._expectation_type is ExpectationType.NEGATIVE:
            matcher = matcher.negation

        return MatcherApplier(matcher, _ElementGetter())


class _NumFilesMatcherResolver(FilesMatcherResolverBase):
    def __init__(self,
                 expectation_type: ExpectationType,
                 matcher: MatcherResolver[int]):
        self._matcher = matcher

        super().__init__(expectation_type,
                         matcher.validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher.references

    @property
    def negation(self) -> FilesMatcherResolver:
        return _NumFilesMatcherResolver(
            logic_types.negation(self._expectation_type),
            self._matcher,
        )

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _NumFilesMatcherValue(
            self._expectation_type,
            self._matcher.resolve(symbols),
        )


class _ElementGetter(ElementGetter[FilesMatcherModel, int]):
    def get_from(self, model: FilesMatcherModel) -> int:
        return len(list(model.files()))


class NumFilesResolver(comparison_structures.OperandResolver[int]):
    def __init__(self,
                 path_to_check: FilesMatcherModel):
        self.path_to_check = path_to_check

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        return len(list(self.path_to_check.files()))
