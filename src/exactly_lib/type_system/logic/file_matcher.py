import pathlib
from abc import ABC, abstractmethod
from typing import Set, Optional

from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator, \
    ConstantPreOrPostSdsValueValidator, constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver, \
    FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.matcher_base_class import Matcher
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileMatcherModel(ABC):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: pathlib.Path):
        self._tmp_file_space = tmp_file_space
        self._path = path

    @property
    def tmp_file_space(self) -> TmpDirFileSpace:
        return self._tmp_file_space

    @property
    def path(self) -> pathlib.Path:
        """Path of the file to match. May or may not exist."""
        return self._path

    @property
    @abstractmethod
    def file_descriptor(self) -> FilePropertyDescriptorConstructor:
        pass


class FileMatcher(Matcher[FileMatcherModel]):
    """Matches a path of an existing file."""

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        """"Want this variant to replace the bool variant."""
        if self.matches(model):
            return None
        else:
            return ConstantErrorMessageResolver('Failure of ' + self.option_description)

    def matches(self, model: FileMatcherModel) -> bool:
        raise NotImplementedError('abstract method')


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
