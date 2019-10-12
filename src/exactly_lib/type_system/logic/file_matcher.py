from abc import ABC, abstractmethod
from typing import Set, Optional

from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.type_system.data.file_ref import DescribedPathPrimitive
from exactly_lib.type_system.description import trace_renderers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileMatcherModel(ABC):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: DescribedPathPrimitive):
        self._tmp_file_space = tmp_file_space
        self._path = path

    @property
    def tmp_file_space(self) -> TmpDirFileSpace:
        return self._tmp_file_space

    @property
    def path(self) -> DescribedPathPrimitive:
        """Path of the file to match. May or may not exist."""
        return self._path

    @property
    @abstractmethod
    def file_descriptor(self) -> FilePropertyDescriptorConstructor:
        pass


class FileMatcher(MatcherWTraceAndNegation[FileMatcherModel], ABC):
    """Matches a path of an existing file."""

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        """"Want this variant to replace the bool variant."""
        if self.matches(model):
            return None
        else:
            return err_msg_resolvers.constant('Failure of: ' + self.option_description)

    def matches(self, model: FileMatcherModel) -> bool:
        raise NotImplementedError('abstract method')

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        mb_emr = self.matches_emr(model)

        tb = self._new_tb()

        if mb_emr is None:
            return tb.build_result(True)
        else:
            tb.details.append(
                trace_renderers.DetailsRendererOfErrorMessageResolver(mb_emr))
            return tb.build_result(False)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


class FileMatcherValue(MultiDirDependentValue[FileMatcher]):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> FileMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise NotImplementedError()

    def validator(self) -> PreOrPostSdsValueValidator:
        return constant_success_validator()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> FileMatcher:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()
