import pathlib
from abc import ABC
from typing import Optional

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencyError
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, specific_relative_relativity, \
    RelOptionType, RESOLVING_DEPENDENCY_OF, DirectoryStructurePartition
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.impl.path import described_w_handler
from exactly_lib.type_system.data.impl.path import describer_handlers
from exactly_lib.type_system.data.impl.path.described_w_handler import PathDescriberHandlerForDdv
from exactly_lib.type_system.data.path_ddv import PathDdv, DescribedPath
from exactly_lib.type_system.data.path_describer import PathDescriberForDdv
from exactly_lib.type_system.data.path_part import PathPartDdv


class PathDdvWithDescriptionBase(PathDdv, ABC):
    def describer(self) -> PathDescriberForDdv:
        return self._describer_handler().describer

    def value_when_no_dir_dependencies__d(self) -> DescribedPath:
        primitive = self.value_when_no_dir_dependencies()
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_when_no_dir_dependencies(primitive),
        )

    def value_pre_sds__d(self, hds: HomeDirectoryStructure) -> DescribedPath:
        primitive = self.value_pre_sds(hds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_pre_sds(primitive, hds),
        )

    def value_post_sds__d(self, sds: SandboxDirectoryStructure) -> DescribedPath:
        primitive = self.value_post_sds(sds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_post_sds__wo_hds(primitive, sds),
        )

    def value_of_any_dependency__d(self, tcds: Tcds) -> DescribedPath:
        primitive = self.value_of_any_dependency(tcds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_of_any_dependency(primitive, tcds),
        )

    def _describer_handler(self) -> PathDescriberHandlerForDdv:
        return describer_handlers.PathDescriberHandlerForDdvWithDdv(self)


class PathDdvWithPathSuffixBase(PathDdvWithDescriptionBase, ABC):
    def __init__(self, path_part: PathPartDdv):
        self._path_suffix = path_part

    def path_suffix(self) -> PathPartDdv:
        return self._path_suffix

    def path_suffix_str(self) -> str:
        return self._path_suffix.value()

    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str())


class PathDdvWithPathSuffixAndIsNotAbsoluteBase(PathDdvWithPathSuffixBase, ABC):
    def __init__(self, path_part: PathPartDdv):
        super().__init__(path_part)

    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return RESOLVING_DEPENDENCY_OF[self._relativity()]

    def has_dir_dependency(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise DirDependencyError({self.resolving_dependency()})

    def relativity(self) -> SpecificPathRelativity:
        rel_option_type = self._relativity()
        return specific_relative_relativity(rel_option_type)

    def _relativity(self) -> RelOptionType:
        raise NotImplementedError()
