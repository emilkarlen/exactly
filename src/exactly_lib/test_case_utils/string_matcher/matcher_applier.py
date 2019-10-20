from typing import Optional, Generic, Set, List, Callable

from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher.applier import MatcherApplier, MatcherApplierValue, MatcherApplierResolver
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.matcher_base_class import T, Failure
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck, StringMatcherValue
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable


class MaStringMatcher(Generic[T], StringMatcher):
    def __init__(self,
                 name: str,
                 applier: MatcherApplier[FileToCheck, T],
                 err_msg_constructor: Callable[[FileToCheck, Failure[T]], ErrorMessageResolver],
                 ):
        super().__init__()
        self._name = name
        self._applier = applier
        self._err_msg_constructor = err_msg_constructor

    @staticmethod
    def new_structure_tree(name: str,
                           matcher: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            name,
            None,
            (),
            (matcher,),
        )

    @property
    def name(self) -> str:
        return self._name

    def _structure(self) -> StructureRenderer:
        return MaStringMatcher.new_structure_tree(self._name,
                                                  self._applier.structure())

    @property
    def option_description(self) -> str:
        return 'todo'

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        failure = self._applier.matches_w_failure(model)
        if failure is None:
            return None

        return self._err_msg_constructor(model, failure)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        result = self._applier.matches_w_trace(model)
        return (
            self._new_tb()
                .append_child(result.trace)
                .build_result(result.value)
        )


class MaStringMatcherValue(Generic[T],
                           WithCachedTreeStructureDescriptionBase,
                           StringMatcherValue):
    def __init__(self,
                 name: str,
                 applier: MatcherApplierValue[FileToCheck, T],
                 err_msg_constructor: Callable[[FileToCheck, Failure[T]], ErrorMessageResolver],
                 ):
        WithCachedTreeStructureDescriptionBase.__init__(self)
        self._name = name
        self._applier = applier
        self._err_msg_constructor = err_msg_constructor

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set(DirectoryStructurePartition)

    def _structure(self) -> StructureRenderer:
        return MaStringMatcher.new_structure_tree(self._name,
                                                  self._applier.structure())

    def value_when_no_dir_dependencies(self) -> StringMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return MaStringMatcher(
            self._name,
            self._applier.value_of_any_dependency(home_and_sds),
            self._err_msg_constructor,
        )


class MaStringMatcherResolver(Generic[T], StringMatcherResolver):
    def __init__(self,
                 name: str,
                 applier: MatcherApplierResolver[FileToCheck, T],
                 err_msg_constructor: Callable[[FileToCheck, Failure[T]], ErrorMessageResolver],
                 ):
        self._name = name
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
            self._name,
            self._applier.resolve(symbols),
            self._err_msg_constructor
        )
