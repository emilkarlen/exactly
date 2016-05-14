import enum

from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax


class RelOptionType(enum.Enum):
    REL_ACT = 0
    REL_TMP = 1
    REL_PWD = 2
    REL_HOME = 3


REL_TMP_OPTION_NAME = argument.OptionName(long_name='rel-tmp')
REL_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act')
REL_CWD_OPTION_NAME = argument.OptionName(long_name='rel-cwd')
REL_HOME_OPTION_NAME = argument.OptionName(long_name='rel-home')

REL_OPTIONS_MAP = {
    RelOptionType.REL_HOME: REL_HOME_OPTION_NAME,
    RelOptionType.REL_PWD: REL_CWD_OPTION_NAME,
    RelOptionType.REL_ACT: REL_ACT_OPTION_NAME,
    RelOptionType.REL_TMP: REL_TMP_OPTION_NAME,
}

REL_TMP_OPTION = long_option_syntax(REL_TMP_OPTION_NAME.long)
REL_ACT_OPTION = long_option_syntax(REL_ACT_OPTION_NAME.long)
REL_CWD_OPTION = long_option_syntax(REL_CWD_OPTION_NAME.long)
REL_HOME_OPTION = long_option_syntax(REL_HOME_OPTION_NAME.long)


def option_for(option_name: argument.OptionName, argument_name: str = None) -> argument.Option:
    return argument.Option(option_name, argument_name)
