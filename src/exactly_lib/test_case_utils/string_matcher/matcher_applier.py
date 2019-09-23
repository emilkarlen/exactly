from typing import Optional, Generic, Set, List, Callable

from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.matcher.applier import MatcherApplier, MatcherApplierValue, MatcherApplierResolver
from exactly_lib.test_case_utils.matcher.matcher import T, Failure
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck, StringMatcherValue
from exactly_lib.util.symbol_table import SymbolTable


class MaStringMatcher(Generic[T], StringMatcher):
    def __init__(self,
                 applier: MatcherApplier[FileToCheck, T],
                 err_msg_constructor: Callable[[FileToCheck, Failure[T]], ErrorMessageResolver],
                 ):
        self._applier = applier
        self._err_msg_constructor = err_msg_constructor

    @property
    def option_description(self) -> str:
        return 'todo'

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        failure = self._applier.apply(model)
        if failure is None:
            return None

        return self._err_msg_constructor(model, failure)


class MaStringMatcherValue(Generic[T], StringMatcherValue):
    def __init__(self,
                 applier: MatcherApplierValue[FileToCheck, T],
                 err_msg_constructor: Callable[[FileToCheck, Failure[T]], ErrorMessageResolver],
                 ):
        self._applier = applier
        self._err_msg_constructor = err_msg_constructor

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set(DirectoryStructurePartition)

    def value_when_no_dir_dependencies(self) -> StringMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return MaStringMatcher(
            self._applier.value_of_any_dependency(home_and_sds),
            self._err_msg_constructor,
        )


class MaStringMatcherResolver(Generic[T], StringMatcherResolver):
    def __init__(self,
                 applier: MatcherApplierResolver[FileToCheck, T],
                 err_msg_constructor: Callable[[FileToCheck, Failure[T]], ErrorMessageResolver],
                 ):
        self._applier = applier
        self._err_msg_constructor = err_msg_constructor

    @property
    def references(self) -> List[SymbolReference]:
        return list(self._applier.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._applier.validator

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        return MaStringMatcherValue(
            self._applier.resolve(symbols),
            self._err_msg_constructor
        )
