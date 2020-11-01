from abc import ABC
from enum import Enum
from typing import TypeVar, Generic, Set, Optional

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs


class DirDependencies(Enum):
    """Specifies a set of test case directories that a value may depend on."""
    NONE = 0
    HDS = 1
    SDS = 2
    TCDS = 3


def dir_dependency_of_resolving_dependencies(
        resolving_dependencies: Set[DirectoryStructurePartition]) -> DirDependencies:
    if DirectoryStructurePartition.HDS in resolving_dependencies:
        if DirectoryStructurePartition.NON_HDS in resolving_dependencies:
            return DirDependencies.TCDS
        else:
            return DirDependencies.HDS
    if DirectoryStructurePartition.NON_HDS in resolving_dependencies:
        return DirDependencies.SDS
    else:
        return DirDependencies.NONE


def resolving_dependencies_from_dir_dependencies(dir_dependencies: DirDependencies) -> Set[DirectoryStructurePartition]:
    if dir_dependencies == DirDependencies.NONE:
        return set()
    elif dir_dependencies == DirDependencies.HDS:
        return {DirectoryStructurePartition.HDS}
    elif dir_dependencies == DirDependencies.SDS:
        return {DirectoryStructurePartition.NON_HDS}
    elif dir_dependencies == DirDependencies.TCDS:
        return {DirectoryStructurePartition.HDS, DirectoryStructurePartition.NON_HDS}
    else:
        raise ValueError('Unknown {}: {}'.format(DirDependencies,
                                                 dir_dependencies))


RESOLVED_TYPE = TypeVar('RESOLVED_TYPE')


class DirDependentValue(Generic[RESOLVED_TYPE]):
    """A value that may refer to the test case directories."""

    def value_of_any_dependency(self, tcds: TestCaseDs) -> RESOLVED_TYPE:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()


class WithDirDependenciesReporting:
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        raise NotImplementedError()

    def has_dir_dependency(self) -> bool:
        """
        Tells whether or not the evaluation of this object uses any of the test case directories.
        """
        return bool(self.resolving_dependencies())

    def exists_pre_sds(self) -> bool:
        return DirectoryStructurePartition.NON_HDS not in self.resolving_dependencies()


class DirDependencyError(ValueError):
    def __init__(self, unexpected_dependency: Set[DirectoryStructurePartition],
                 msg: str = ''):
        super().__init__(msg)
        self.unexpected_dependency = unexpected_dependency

    def __str__(self) -> str:
        return '{}(unexpected={}: {})'.format(type(self),
                                              self.unexpected_dependency,
                                              super().__str__())


class DependenciesAwareDdv(Generic[RESOLVED_TYPE],
                           DirDependentValue[RESOLVED_TYPE],
                           WithDirDependenciesReporting,
                           ABC):
    """A DDV that know and can report its dependencies."""

    def value_when_no_dir_dependencies(self) -> RESOLVED_TYPE:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise DirDependencyError(self.resolving_dependencies())


class Max1DependencyDdv(Generic[RESOLVED_TYPE],
                        DependenciesAwareDdv[RESOLVED_TYPE]):
    """A :class:`DirDependentValue` that depends at most on one :class:`ResolvingDependency`."""

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        resolving_dep = self.resolving_dependency()
        if resolving_dep is None:
            return set()
        else:
            return {resolving_dep}

    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        """
        :rtype: None iff the value has no dependency
        """
        raise NotImplementedError()

    def value_pre_sds(self, hds: HomeDs) -> RESOLVED_TYPE:
        """
        :raises DirDependencyError: This file exists only post-SDS.
        """
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDs):
        """
        :raises DirDependencyError: This file exists pre-SDS.
        """
        raise NotImplementedError()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> RESOLVED_TYPE:
        if self.exists_pre_sds():
            return self.value_pre_sds(tcds.hds)
        else:
            return self.value_post_sds(tcds.sds)


class MultiDependenciesDdv(Generic[RESOLVED_TYPE],
                           DependenciesAwareDdv[RESOLVED_TYPE],
                           ABC):
    """A :class:`DirDependentValue` that may depend on a multiple :class:`ResolvingDependency`."""

    def dir_dependencies(self) -> DirDependencies:
        return dir_dependency_of_resolving_dependencies(self.resolving_dependencies())

    def has_dir_dependency(self) -> bool:
        return bool(self.resolving_dependencies())
