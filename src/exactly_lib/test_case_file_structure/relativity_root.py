import pathlib
from typing import Callable

from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import \
    RelOptionType, RelSdsOptionType, RelNonHdsOptionType, RelHdsOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds


class RelRootResolver:
    def __init__(self, relativity_type: RelOptionType):
        self._relativity = relativity_type

    @property
    def relativity_type(self) -> RelOptionType:
        return self._relativity

    def from_tcds(self, tcds: Tcds) -> pathlib.Path:
        raise NotImplementedError()

    def from_hds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        raise ValueError('Root is not relative HDS: ' + str(self._relativity))

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('Root is not relative SDS: ' + str(self._relativity))

    def from_non_hds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('Root is not relative non-HDS: ' + str(self._relativity))

    @property
    def is_rel_hds(self) -> bool:
        raise NotImplementedError()

    @property
    def is_rel_sds(self) -> bool:
        raise NotImplementedError()

    @property
    def is_rel_cwd(self) -> bool:
        raise NotImplementedError()

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()


class RelHdsRootResolver(RelRootResolver):
    def __init__(self,
                 relativity_type: RelHdsOptionType,
                 hds_2_root_fun: Callable[[HomeDirectoryStructure], pathlib.Path]):
        super().__init__(path_relativity.rel_any_from_rel_hds(relativity_type))
        self._relativity_type_hds = relativity_type
        self._hds_2_root_fun = hds_2_root_fun

    @property
    def hds_relativity_type(self) -> RelHdsOptionType:
        return self._relativity_type_hds

    def from_hds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self._hds_2_root_fun(hds)

    def from_tcds(self, tcds: Tcds) -> pathlib.Path:
        return self.from_hds(tcds.hds)

    @property
    def is_rel_hds(self) -> bool:
        return True

    @property
    def is_rel_sds(self) -> bool:
        return False

    @property
    def is_rel_cwd(self) -> bool:
        return False

    @property
    def exists_pre_sds(self) -> bool:
        return True


class RelNonHdsRootResolver(RelRootResolver):
    def __init__(self, relativity_type: RelNonHdsOptionType):
        super().__init__(path_relativity.rel_any_from_rel_non_hds(relativity_type))
        self._relativity_type_non_hds = relativity_type

    @property
    def non_hds_relativity_type(self) -> RelNonHdsOptionType:
        return self._relativity_type_non_hds

    def from_non_hds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def from_tcds(self, tcds: Tcds) -> pathlib.Path:
        return self.from_non_hds(tcds.sds)

    @property
    def is_rel_hds(self) -> bool:
        return False

    @property
    def exists_pre_sds(self) -> bool:
        return False


class RelNonHdsRootResolverForCwd(RelNonHdsRootResolver):
    def __init__(self):
        super().__init__(RelNonHdsOptionType.REL_CWD)

    def from_cwd(self) -> pathlib.Path:
        return pathlib.Path().cwd()

    def from_non_hds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.from_cwd()

    @property
    def is_rel_cwd(self) -> bool:
        return True

    @property
    def is_rel_sds(self) -> bool:
        return False


class RelSdsRootResolver(RelNonHdsRootResolver):
    def __init__(self,
                 relativity_type: RelSdsOptionType,
                 sds_2_root_fun: Callable[[SandboxDirectoryStructure], pathlib.Path]):
        super().__init__(path_relativity.rel_non_hds_from_rel_sds(relativity_type))
        self._relativity_type_sds = relativity_type
        self._sds_2_root_fun = sds_2_root_fun

    @property
    def sds_relativity_type(self) -> RelSdsOptionType:
        return self._relativity_type_sds

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._sds_2_root_fun(sds)

    def from_non_hds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.from_sds(sds)

    @property
    def is_rel_cwd(self) -> bool:
        return False

    @property
    def is_rel_sds(self) -> bool:
        return True


resolver_for_act = RelSdsRootResolver(RelSdsOptionType.REL_ACT,
                                      SandboxDirectoryStructure.act_dir.fget)

resolver_for_result = RelSdsRootResolver(RelSdsOptionType.REL_RESULT,
                                         SandboxDirectoryStructure.result_dir.fget)

resolver_for_tmp_user = RelSdsRootResolver(RelSdsOptionType.REL_TMP,
                                           SandboxDirectoryStructure.user_tmp_dir.fget)

resolver_for_cwd = RelNonHdsRootResolverForCwd()

resolver_for_hds_case = RelHdsRootResolver(RelHdsOptionType.REL_HDS_CASE,
                                           HomeDirectoryStructure.case_dir.fget)

resolver_for_hds_act = RelHdsRootResolver(RelHdsOptionType.REL_HDS_ACT,
                                          HomeDirectoryStructure.act_dir.fget)
