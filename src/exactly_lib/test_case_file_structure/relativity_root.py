import pathlib
import types

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class RelRootResolver:
    @property
    def relativity_type(self) -> RelOptionType:
        raise NotImplementedError()

    def from_cwd(self) -> pathlib.Path:
        """
        Precondition: `is_rel_cwd`
        """
        raise ValueError('Root is not relative the cwd')

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Precondition: `is_rel_home`
        """
        raise ValueError('Root is not relative the home directory')

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        """
        Precondition: `is_rel_sds`
        """
        raise ValueError('Root is not relative the SDS')

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        if self.is_rel_cwd:
            return self.from_cwd()
        else:
            return self.from_sds(sds)

    @property
    def is_rel_cwd(self) -> bool:
        return False

    @property
    def is_rel_home(self) -> bool:
        return False

    @property
    def is_rel_sds(self) -> bool:
        return False

    @property
    def exists_pre_sds(self) -> bool:
        return not (self.is_rel_cwd or self.is_rel_sds)


class _RelPathResolverRelHome(RelRootResolver):
    @property
    def relativity_type(self) -> RelOptionType:
        return RelOptionType.REL_HOME

    @property
    def is_rel_home(self) -> bool:
        return True

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_home(home_and_sds.home_dir_path)


class _RelPathResolverRelCwd(RelRootResolver):
    @property
    def relativity_type(self) -> RelOptionType:
        return RelOptionType.REL_CWD

    @property
    def is_rel_cwd(self) -> bool:
        return True

    def from_cwd(self) -> pathlib.Path:
        return pathlib.Path().cwd()

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        """
        Precondition: `is_rel_sds`
        """
        raise ValueError('Root is not relative the SDS')

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_cwd()


class _RelRootResolverForRelSds(RelRootResolver):
    def __init__(self,
                 relativity_type: RelOptionType,
                 sds_2_root_fun: types.FunctionType):
        self._relativity_type = relativity_type
        self._sds_2_root_fun = sds_2_root_fun

    @property
    def relativity_type(self) -> RelOptionType:
        return self._relativity_type

    @property
    def is_rel_sds(self) -> bool:
        return True

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._sds_2_root_fun(sds)

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_sds(home_and_sds.sds)


resolver_for_cwd = _RelPathResolverRelCwd()
resolver_for_home = _RelPathResolverRelHome()
resolver_for_act = _RelRootResolverForRelSds(RelOptionType.REL_ACT,
                                             lambda sds: sds.act_dir)
resolver_for_result = _RelRootResolverForRelSds(RelOptionType.REL_RESULT,
                                                lambda sds: sds.result.root_dir)
resolver_for_tmp_user = _RelRootResolverForRelSds(RelOptionType.REL_TMP,
                                                  lambda sds: sds.tmp.user_dir)
