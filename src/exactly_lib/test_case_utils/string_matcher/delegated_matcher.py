from typing import Optional, Set, List

from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.matcher.resolver import MatcherResolver
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace, MatcherValue
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck, StringMatcherValue
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherDelegatedToMatcher(StringMatcher):
    def __init__(self, delegated: MatcherWTrace[FileToCheck]):
        super().__init__()
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    def _structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    def matches(self, model: FileToCheck) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        return self._delegated.matches_w_trace(model)


class StringMatcherValueDelegatedToMatcher(StringMatcherValue):
    def __init__(self, delegated: MatcherValue[FileToCheck]):
        super().__init__()
        self._delegated = delegated

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set(DirectoryStructurePartition)

    def structure(self) -> StructureRenderer:
        return self._delegated.structure()

    def value_when_no_dir_dependencies(self) -> StringMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return StringMatcherDelegatedToMatcher(self._delegated.value_of_any_dependency(home_and_sds))


class StringMatcherResolverDelegatedToMatcher(StringMatcherResolver):
    def __init__(self, delegated: MatcherResolver[FileToCheck]):
        super().__init__()
        self._delegated = delegated

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._delegated.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._delegated.validator

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        return StringMatcherValueDelegatedToMatcher(self._delegated.resolve(symbols))
