import pathlib
from abc import ABC
from typing import Optional

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencyError
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, specific_relative_relativity, \
    RelOptionType, RESOLVING_DEPENDENCY_OF, DirectoryStructurePartition
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data.file_ref import FileRef, DescribedPathPrimitive
from exactly_lib.type_system.data.impl.path import described_path_ddv
from exactly_lib.type_system.data.path_describer import PathDescriberForValue
from exactly_lib.type_system.data.path_part import PathPart


class FileRefWithDescriptionBase(FileRef, ABC):
    def describer(self) -> PathDescriberForValue:
        return described_path_ddv.of(self).describer

    def value_when_no_dir_dependencies__d(self) -> DescribedPathPrimitive:
        return described_path_ddv.of(self).value_when_no_dir_dependencies()

    def value_pre_sds__d(self, hds: HomeDirectoryStructure) -> DescribedPathPrimitive:
        return described_path_ddv.of(self).value_pre_sds(hds)

    def value_post_sds__d(self, sds: SandboxDirectoryStructure) -> DescribedPathPrimitive:
        return described_path_ddv.of(self).value_post_sds__wo_hds(sds)

    def value_of_any_dependency__d(self, tcds: HomeAndSds) -> DescribedPathPrimitive:
        return described_path_ddv.of(self).value_of_any_dependency(tcds)


class FileRefWithPathSuffixBase(FileRefWithDescriptionBase, ABC):
    def __init__(self, path_part: PathPart):
        self._path_suffix = path_part

    def path_suffix(self) -> PathPart:
        return self._path_suffix

    def path_suffix_str(self) -> str:
        return self._path_suffix.value()

    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str())


class FileRefWithPathSuffixAndIsNotAbsoluteBase(FileRefWithPathSuffixBase, ABC):
    def __init__(self, path_part: PathPart):
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
