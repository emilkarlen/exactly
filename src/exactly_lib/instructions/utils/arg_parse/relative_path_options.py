import enum
import pathlib
import types

from exactly_lib.test_case.home_and_sds import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax


class RelOptionType(enum.Enum):
    REL_ACT = 0
    REL_RESULT = 1
    REL_TMP = 2
    REL_HOME = 3
    REL_CWD = 4


class RelRootResolver:
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


class RelOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                root_resolver: RelRootResolver):
        return tuple.__new__(cls, (option_name, root_resolver))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def root_resolver(self) -> RelRootResolver:
        return self[1]


class _RelPathResolverRelHome(RelRootResolver):
    @property
    def is_rel_home(self) -> bool:
        return True

    def from_home(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_home(home_and_sds.home_dir_path)


class _RelPathResolverRelCwd(RelRootResolver):
    @property
    def is_rel_cwd(self) -> bool:
        return True

    def from_cwd(self) -> pathlib.Path:
        return pathlib.Path().cwd()

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_cwd()


class _RelRootResolverForRelSds(RelRootResolver):
    def __init__(self, sds_2_root_fun: types.FunctionType):
        self._sds_2_root_fun = sds_2_root_fun

    @property
    def is_rel_sds(self) -> bool:
        return True

    def from_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._sds_2_root_fun(sds)

    def from_home_and_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self.from_sds(home_and_sds.sds)


resolver_for_act = _RelRootResolverForRelSds(lambda sds: sds.act_dir)

resolver_for_result = _RelRootResolverForRelSds(lambda sds: sds.result.root_dir)

resolver_for_tmp_user = _RelRootResolverForRelSds(lambda sds: sds.tmp.user_dir)

resolver_for_cwd = _RelPathResolverRelCwd()

resolver_for_home = _RelPathResolverRelHome()

REL_TMP_OPTION_NAME = argument.OptionName(long_name='rel-tmp')
REL_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act')
REL_RESULT_OPTION_NAME = argument.OptionName(long_name='rel-result')
REL_CWD_OPTION_NAME = argument.OptionName(long_name='rel-cd')
REL_HOME_OPTION_NAME = argument.OptionName(long_name='rel-home')

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME: RelOptionInfo(REL_HOME_OPTION_NAME, resolver_for_home),
    RelOptionType.REL_CWD: RelOptionInfo(REL_CWD_OPTION_NAME, resolver_for_cwd),
    RelOptionType.REL_ACT: RelOptionInfo(REL_ACT_OPTION_NAME, resolver_for_act),
    RelOptionType.REL_TMP: RelOptionInfo(REL_TMP_OPTION_NAME, resolver_for_tmp_user),
    RelOptionType.REL_RESULT: RelOptionInfo(REL_RESULT_OPTION_NAME, resolver_for_result),
}

REL_TMP_OPTION = long_option_syntax(REL_TMP_OPTION_NAME.long)
REL_ACT_OPTION = long_option_syntax(REL_ACT_OPTION_NAME.long)
REL_RESULT_OPTION = long_option_syntax(REL_RESULT_OPTION_NAME.long)
REL_CWD_OPTION = long_option_syntax(REL_CWD_OPTION_NAME.long)
REL_HOME_OPTION = long_option_syntax(REL_HOME_OPTION_NAME.long)


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
