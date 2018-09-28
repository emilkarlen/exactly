from abc import ABC, abstractmethod
from typing import Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.matcher_base_class import Matcher

StringMatcherModel = str


class StringMatcher(Matcher[StringMatcherModel], ABC):
    @abstractmethod
    def matches(self, model: StringMatcherModel) -> bool:
        raise NotImplementedError('abstract method')


class StringMatcherValue(MultiDirDependentValue[StringMatcher]):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> StringMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise NotImplementedError()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()
