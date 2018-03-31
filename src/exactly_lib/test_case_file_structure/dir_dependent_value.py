import pathlib
from enum import Enum
from typing import TypeVar, Generic, Set, Optional

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class DirDependencies(Enum):
    """Specifies a set of test case directories that a value may depend on."""
    NONE = 0
    HOME = 1
    SDS = 2
    HOME_AND_SDS = 3


def dir_dependency_of_resolving_dependencies(resolving_dependencies: set) -> DirDependencies:
    if ResolvingDependency.HOME in resolving_dependencies:
        if ResolvingDependency.NON_HOME in resolving_dependencies:
            return DirDependencies.HOME_AND_SDS
        else:
            return DirDependencies.HOME
    if ResolvingDependency.NON_HOME in resolving_dependencies:
        return DirDependencies.SDS
    else:
        return DirDependencies.NONE


class DirDependencyError(ValueError):
    def __init__(self, unexpected_dependency: Set[ResolvingDependency],
                 msg: str = ''):
        super().__init__(msg)
        self.unexpected_dependency = unexpected_dependency

    def __str__(self) -> str:
        return '{}(unexpected={}: {})'.format(type(self),
                                              self.unexpected_dependency,
                                              super().__str__())


RESOLVED_TYPE = TypeVar('RESOLVED_TYPE')


class WithDirDependencies:
    def resolving_dependencies(self) -> Set[ResolvingDependency]:
        raise NotImplementedError()

    def has_dir_dependency(self) -> bool:
        """
        Tells whether or not the evaluation of this object uses any of the test case directories.
        """
        return bool(self.resolving_dependencies())

    def exists_pre_sds(self) -> bool:
        return ResolvingDependency.NON_HOME not in self.resolving_dependencies()


class DirDependentValue(Generic[RESOLVED_TYPE], WithDirDependencies):
    """A value that may refer to the test case directories."""

    def value_when_no_dir_dependencies(self) -> RESOLVED_TYPE:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise DirDependencyError(self.resolving_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> RESOLVED_TYPE:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()


class SingleDirDependentValue(DirDependentValue[pathlib.Path]):
    """A :class:`DirDependentValue` that depends at most on a single :class:`ResolvingDependency`."""

    def resolving_dependency(self) -> Optional[ResolvingDependency]:
        """
        :rtype: None iff the value has no dependency
        """
        raise NotImplementedError()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        """
        :raises DirDependencyError: This file exists only post-SDS.
        """
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        """
        :raises DirDependencyError: This file exists pre-SDS.
        """
        raise NotImplementedError()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        if self.exists_pre_sds():
            return self.value_pre_sds(home_and_sds.hds)
        else:
            return self.value_post_sds(home_and_sds.sds)


class MultiDirDependentValue(Generic[RESOLVED_TYPE], DirDependentValue[RESOLVED_TYPE]):
    """A :class:`DirDependentValue` that may depend on a multiple :class:`ResolvingDependency`."""

    def dir_dependency(self) -> DirDependencies:
        return dir_dependency_of_resolving_dependencies(self.resolving_dependencies())

    def has_dir_dependency(self) -> bool:
        return self.dir_dependency() is not DirDependencies.NONE
