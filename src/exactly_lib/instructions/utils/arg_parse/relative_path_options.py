import enum
import pathlib
import types

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax


class RelOptionType(enum.Enum):
    REL_ACT = 0
    REL_TMP = 1
    REL_CWD = 2
    REL_HOME = 3


class RelOptionInfo(tuple):
    def __new__(cls,
                option_name: argument.OptionName,
                home_and_sds_2_path: types.FunctionType):
        return tuple.__new__(cls, (option_name, home_and_sds_2_path))

    @property
    def option_name(self) -> argument.OptionName:
        return self[0]

    @property
    def home_and_sds_2_path(self) -> types.FunctionType:
        return self[1]


def home_and_sds_2_act(home_and_sds: HomeAndSds) -> pathlib.Path:
    return home_and_sds.sds.act_dir


def home_and_sds_2_tmp_user(home_and_sds: HomeAndSds) -> pathlib.Path:
    return home_and_sds.sds.tmp.user_dir


def home_and_sds_2_cwd(home_and_sds: HomeAndSds) -> pathlib.Path:
    return pathlib.Path().cwd()


def home_and_sds_2_home(home_and_sds: HomeAndSds) -> pathlib.Path:
    return home_and_sds.home_dir_path


REL_TMP_OPTION_NAME = argument.OptionName(long_name='rel-tmp')
REL_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act')
REL_CWD_OPTION_NAME = argument.OptionName(long_name='rel-cd')
REL_HOME_OPTION_NAME = argument.OptionName(long_name='rel-home')

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME: RelOptionInfo(REL_HOME_OPTION_NAME, home_and_sds_2_home),
    RelOptionType.REL_CWD: RelOptionInfo(REL_CWD_OPTION_NAME, home_and_sds_2_cwd),
    RelOptionType.REL_ACT: RelOptionInfo(REL_ACT_OPTION_NAME, home_and_sds_2_act),
    RelOptionType.REL_TMP: RelOptionInfo(REL_TMP_OPTION_NAME, home_and_sds_2_tmp_user),
}

REL_TMP_OPTION = long_option_syntax(REL_TMP_OPTION_NAME.long)
REL_ACT_OPTION = long_option_syntax(REL_ACT_OPTION_NAME.long)
REL_CWD_OPTION = long_option_syntax(REL_CWD_OPTION_NAME.long)
REL_HOME_OPTION = long_option_syntax(REL_HOME_OPTION_NAME.long)


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
