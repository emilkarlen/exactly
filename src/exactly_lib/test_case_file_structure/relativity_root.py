import pathlib
import types

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType, RelNonHomeOptionType, \
    rel_non_home_from_rel_sds, rel_any_from_rel_non_home
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class RelSdsRootResolver:
    def __init__(self,
                 relativity_type: RelSdsOptionType,
                 sds_2_root_fun: types.FunctionType):
        self._relativity_type = relativity_type
        self._sds_2_root_fun = sds_2_root_fun

    @property
    def sds_relativity_type(self) -> RelSdsOptionType:
        return self._relativity_type

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._sds_2_root_fun(sds)
        #
        # def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        #     return self.from_sds(home_and_sds.sds)


class RelNonHomeRootResolver:
    @property
    def non_home_relativity_type(self) -> RelNonHomeOptionType:
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
        raise ValueError('Root does not exist pre SDS')

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        """
        Precondition: `is_rel_sds`
        """
        raise ValueError('Root is not relative the SDS')

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        if self.is_rel_cwd:
            return self.from_cwd()
        else:
            return self.from_sds(sds)

    @property
    def is_rel_cwd(self) -> bool:
        raise NotImplementedError()

    @property
    def is_rel_sds(self) -> bool:
        raise NotImplementedError()

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()


class RelRootResolver:
    @property
    def relativity_type(self) -> RelOptionType:
        raise NotImplementedError()

    def from_cwd(self) -> pathlib.Path:
        """
        Precondition: `is_rel_cwd`
        """
        raise ValueError('Root is not relative the cwd: ' + str(self.relativity_type))

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Precondition: `is_rel_home`
        """
        raise ValueError('Root does not exist pre SDS: ' + str(self.relativity_type))

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        """
        Precondition: `is_rel_sds`
        """
        raise ValueError('Root is not relative the SDS: ' + str(self.relativity_type))

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    @property
    def is_rel_cwd(self) -> bool:
        raise NotImplementedError()

    @property
    def is_rel_home(self) -> bool:
        raise NotImplementedError()

    @property
    def is_rel_sds(self) -> bool:
        raise NotImplementedError()

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()


class _RelPathResolverRelHome(RelRootResolver):
    @property
    def relativity_type(self) -> RelOptionType:
        return RelOptionType.REL_HOME

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

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('Root is not relative HOME: ' + str(self.relativity_type))

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_home(home_and_sds.home_dir_path)


class _RelNonHomeRootResolverFromSdsResolver(RelNonHomeRootResolver):
    def __init__(self,
                 rel_sds_resolver: RelSdsRootResolver,
                 ):
        self._rel_sds_resolver = rel_sds_resolver

    @property
    def non_home_relativity_type(self) -> RelNonHomeOptionType:
        return rel_non_home_from_rel_sds(self._rel_sds_resolver.sds_relativity_type)

    def from_cwd(self) -> pathlib.Path:
        """
        Precondition: `is_rel_cwd`
        """
        raise ValueError('Root is not relative the cwd: ' + str(self.non_home_relativity_type))

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Precondition: `is_rel_home`
        """
        raise ValueError('Root does not exist pre SDS: ' + str(self.non_home_relativity_type))

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._rel_sds_resolver.from_sds(sds)

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.from_sds(sds)

    @property
    def is_rel_cwd(self) -> bool:
        return False

    @property
    def is_rel_sds(self) -> bool:
        return True

    @property
    def exists_pre_sds(self) -> bool:
        return False


class _RelNonHomeRootResolverForCwd(RelNonHomeRootResolver):
    @property
    def non_home_relativity_type(self) -> RelNonHomeOptionType:
        return RelNonHomeOptionType.REL_CWD

    def from_cwd(self) -> pathlib.Path:
        return pathlib.Path().cwd()

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('Root is not relative the SDS: ' + str(self.non_home_relativity_type))

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.from_cwd()

    @property
    def is_rel_cwd(self) -> bool:
        return True

    @property
    def is_rel_sds(self) -> bool:
        return False

    @property
    def exists_pre_sds(self) -> bool:
        return False


class _RelRootResolverFromRelNonHome(RelRootResolver):
    def __init__(self,
                 rel_non_home_resolver: RelNonHomeRootResolver,
                 ):
        self._rel_non_home_resolver = rel_non_home_resolver

    @property
    def relativity_type(self) -> RelOptionType:
        return rel_any_from_rel_non_home(self._rel_non_home_resolver.non_home_relativity_type)

    @property
    def is_rel_sds(self) -> bool:
        return self._rel_non_home_resolver.is_rel_sds

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._rel_non_home_resolver.from_sds(sds)

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self._rel_non_home_resolver.from_non_home(home_and_sds.sds)

    @property
    def is_rel_cwd(self) -> bool:
        return self._rel_non_home_resolver.is_rel_cwd

    @property
    def exists_pre_sds(self) -> bool:
        return self._rel_non_home_resolver.exists_pre_sds

    @property
    def is_rel_home(self) -> bool:
        return False

    def from_non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._rel_non_home_resolver.from_non_home(sds)

    def from_cwd(self) -> pathlib.Path:
        return self._rel_non_home_resolver.from_cwd()


resolver_rel_sds__for_act = RelSdsRootResolver(RelSdsOptionType.REL_ACT,
                                               lambda sds: sds.act_dir)

resolver_rel_sds__for_result = RelSdsRootResolver(RelSdsOptionType.REL_RESULT,
                                                  lambda sds: sds.result.root_dir)

resolver_rel_sds__for_tmp_user = RelSdsRootResolver(RelSdsOptionType.REL_TMP,
                                                    lambda sds: sds.tmp.user_dir)

resolver_rel_non_home__for_act = _RelNonHomeRootResolverFromSdsResolver(resolver_rel_sds__for_act)
resolver_rel_non_home__for_result = _RelNonHomeRootResolverFromSdsResolver(resolver_rel_sds__for_result)
resolver_rel_non_home__for_tmp_user = _RelNonHomeRootResolverFromSdsResolver(resolver_rel_sds__for_tmp_user)
resolver_rel_non_home__for_cwd = _RelNonHomeRootResolverForCwd()

resolver_for_act = _RelRootResolverFromRelNonHome(resolver_rel_non_home__for_act)
resolver_for_result = _RelRootResolverFromRelNonHome(resolver_rel_non_home__for_result)
resolver_for_tmp_user = _RelRootResolverFromRelNonHome(resolver_rel_non_home__for_tmp_user)
resolver_for_cwd = _RelRootResolverFromRelNonHome(resolver_rel_non_home__for_cwd)

resolver_for_home = _RelPathResolverRelHome()
