import pathlib
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import Max1DependencyDdv
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, RESOLVING_DEPENDENCY_OF, \
    DirectoryStructurePartition
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.path_describer import PathDescriberForDdv, PathDescriberForPrimitive
from exactly_lib.type_system.data.path_part import PathPartDdv


class DescribedPath(ABC):
    @property
    @abstractmethod
    def primitive(self) -> Path:
        pass

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForPrimitive:
        pass

    @abstractmethod
    def child(self, child_path_component: str) -> 'DescribedPath':
        pass

    @abstractmethod
    def parent(self) -> 'DescribedPath':
        """Gives a path with the last component removed"""
        pass


class PathDdv(Max1DependencyDdv[pathlib.Path], ABC):
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    @abstractmethod
    def describer(self) -> PathDescriberForDdv:
        pass

    def path_suffix(self) -> PathPartDdv:
        raise NotImplementedError()

    def path_suffix_str(self) -> str:
        raise NotImplementedError()

    def path_suffix_path(self) -> pathlib.Path:
        raise NotImplementedError()

    def exists_pre_sds(self) -> bool:
        return self.resolving_dependency() is not DirectoryStructurePartition.NON_HDS

    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        relativity = self.relativity()
        if relativity.is_absolute:
            return None
        else:
            return RESOLVING_DEPENDENCY_OF[relativity.relativity_type]

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        relativity = self.relativity()
        if relativity.is_absolute:
            return set()
        else:
            return {RESOLVING_DEPENDENCY_OF[relativity.relativity_type]}

    def relativity(self) -> SpecificPathRelativity:
        raise NotImplementedError()

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise NotImplementedError()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    @abstractmethod
    def value_when_no_dir_dependencies__d(self) -> DescribedPath:
        pass

    @abstractmethod
    def value_pre_sds__d(self, hds: HomeDirectoryStructure) -> DescribedPath:
        pass

    @abstractmethod
    def value_post_sds__d(self, sds: SandboxDirectoryStructure) -> DescribedPath:
        pass

    @abstractmethod
    def value_of_any_dependency__d(self, tcds: Tcds) -> DescribedPath:
        pass
