import pathlib
from typing import Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.matcher_base_class import Matcher


class FileMatcher(Matcher[pathlib.Path]):
    """Matches a path of an existing file."""

    def matches(self, path: pathlib.Path) -> bool:
        """
        :param path: The path of an existing file (but may be a broken symbolic link).
        """
        raise NotImplementedError('abstract method')


class FileMatcherValue(MultiDirDependentValue[FileMatcher]):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> FileMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise NotImplementedError()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> FileMatcher:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()
