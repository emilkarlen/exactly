import pathlib
from abc import abstractmethod, ABC
from typing import Optional, Set

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import SpecificPathRelativity, RESOLVING_DEPENDENCY_OF, \
    DirectoryStructurePartition
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import Max1DependencyDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.path_describer import PathDescriberForDdv


class PathDdv(Max1DependencyDdv[pathlib.Path], ABC):
    """
    A reference to a file (any kind of file), with functionality to resolve its path,
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

    def value_pre_sds(self, hds: HomeDs) -> pathlib.Path:
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDs) -> pathlib.Path:
        raise NotImplementedError()

    @abstractmethod
    def value_when_no_dir_dependencies__d(self) -> DescribedPath:
        pass

    @abstractmethod
    def value_pre_sds__d(self, hds: HomeDs) -> DescribedPath:
        pass

    @abstractmethod
    def value_post_sds__d(self, sds: SandboxDs) -> DescribedPath:
        pass

    @abstractmethod
    def value_of_any_dependency__d(self, tcds: TestCaseDs) -> DescribedPath:
        pass
