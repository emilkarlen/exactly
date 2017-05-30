import pathlib
import types

from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType, RelNonHomeOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class RelRootResolver:
    def __init__(self, relativity_type: RelOptionType):
        self._relativity = relativity_type

    @property
    def relativity_type(self) -> RelOptionType:
        return self._relativity

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        raise ValueError('Root is not relative home: ' + str(self._relativity))

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('Root is not relative non-home: ' + str(self._relativity))

    @property
    def is_rel_home(self) -> bool:
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


class RelPathResolverRelHome(RelRootResolver):
    def __init__(self):
        super().__init__(RelOptionType.REL_HOME)

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_home(home_and_sds.home_dir_path)

    @property
    def is_rel_home(self) -> bool:
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


class RelNonHomeRootResolver(RelRootResolver):
    def __init__(self, relativity_type: RelNonHomeOptionType):
        super().__init__(path_relativity.rel_any_from_rel_non_home(relativity_type))
        self._relativity_type_non_home = relativity_type

    @property
    def non_home_relativity_type(self) -> RelNonHomeOptionType:
        return self._relativity_type_non_home

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_non_home(home_and_sds.sds)

    @property
    def is_rel_home(self) -> bool:
        return False

    @property
    def exists_pre_sds(self) -> bool:
        return False


class RelNonHomeRootResolverForCwd(RelNonHomeRootResolver):
    def __init__(self):
        super().__init__(RelNonHomeOptionType.REL_CWD)

    def from_cwd(self) -> pathlib.Path:
        return pathlib.Path().cwd()

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.from_cwd()

    @property
    def is_rel_cwd(self) -> bool:
        return True

    @property
    def is_rel_sds(self) -> bool:
        return False


class RelSdsRootResolver(RelNonHomeRootResolver):
    def __init__(self,
                 relativity_type: RelSdsOptionType,
                 sds_2_root_fun: types.FunctionType):
        super().__init__(path_relativity.rel_non_home_from_rel_sds(relativity_type))
        self._relativity_type_sds = relativity_type
        self._sds_2_root_fun = sds_2_root_fun

    @property
    def sds_relativity_type(self) -> RelSdsOptionType:
        return self._relativity_type_sds

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._sds_2_root_fun(sds)

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.from_sds(sds)

    @property
    def is_rel_cwd(self) -> bool:
        return False

    @property
    def is_rel_sds(self) -> bool:
        return True


resolver_for_act = RelSdsRootResolver(RelSdsOptionType.REL_ACT,
                                      lambda sds: sds.act_dir)

resolver_for_result = RelSdsRootResolver(RelSdsOptionType.REL_RESULT,
                                         lambda sds: sds.result.root_dir)

resolver_for_tmp_user = RelSdsRootResolver(RelSdsOptionType.REL_TMP,
                                           lambda sds: sds.tmp.user_dir)

resolver_for_cwd = RelNonHomeRootResolverForCwd()

resolver_for_home = RelPathResolverRelHome()
