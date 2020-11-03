import pathlib
from abc import ABC
from typing import Optional

from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import SpecificPathRelativity, specific_relative_relativity, \
    RelOptionType, RESOLVING_DEPENDENCY_OF, DirectoryStructurePartition
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependencyError
from exactly_lib.type_val_deps.types.path.impl import describer_handlers, described_w_handler
from exactly_lib.type_val_deps.types.path.impl.described_w_handler import PathDescriberHandlerForDdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv, DescribedPath
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_prims.path_describer import PathDescriberForDdv


class PathDdvWithDescriptionBase(PathDdv, ABC):
    def describer(self) -> PathDescriberForDdv:
        return self._describer_handler().describer

    def value_when_no_dir_dependencies__d(self) -> DescribedPath:
        primitive = self.value_when_no_dir_dependencies()
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_when_no_dir_dependencies(primitive),
        )

    def value_pre_sds__d(self, hds: HomeDs) -> DescribedPath:
        primitive = self.value_pre_sds(hds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_pre_sds(primitive, hds),
        )

    def value_post_sds__d(self, sds: SandboxDs) -> DescribedPath:
        primitive = self.value_post_sds(sds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_post_sds__wo_hds(primitive, sds),
        )

    def value_of_any_dependency__d(self, tcds: TestCaseDs) -> DescribedPath:
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
