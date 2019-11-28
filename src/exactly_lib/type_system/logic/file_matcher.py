from abc import ABC, abstractmethod

from exactly_lib.test_case.validation.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileMatcherModel(ABC):
    @property
    @abstractmethod
    def tmp_file_space(self) -> TmpDirFileSpace:
        pass

    @property
    @abstractmethod
    def path(self) -> DescribedPathPrimitive:
        """Path of the file to match. May or may not exist."""
        pass

    @property
    @abstractmethod
    def file_descriptor(self) -> FilePropertyDescriptorConstructor:
        pass


FileMatcher = MatcherWTraceAndNegation[FileMatcherModel]


class FileMatcherDdv(DirDependentValue[FileMatcher], ABC):
    def validator(self) -> DdvValidator:
        return constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcher:
        pass
