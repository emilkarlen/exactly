from typing import Sequence, Set

from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelSdsOptionType, RelOptionType
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

RELATIVITY_DESCRIPTION_ABSOLUTE = 'absolute'
RELATIVITY_DESCRIPTION_HDS_CASE = 'home directory'
RELATIVITY_DESCRIPTION_HDS_ACT = 'act-home directory'
RELATIVITY_DESCRIPTION_CWD = 'current directory'
RELATIVITY_DESCRIPTION_ACT = 'act directory'
RELATIVITY_DESCRIPTION_TMP = 'tmp directory'
RELATIVITY_DESCRIPTION_RESULT = 'result directory'

RELATIVITY_DESCRIPTION_SYMBOL = 'value of path symbol'
RELATIVITY_DESCRIPTION_SOURCE_FILE = 'location of the current source file'

EXACTLY_DIR__REL_HDS_CASE = 'EXACTLY_HOME'
EXACTLY_DIR__REL_HDS_ACT = 'EXACTLY_ACT_HOME'
EXACTLY_DIR__REL_ACT = 'EXACTLY_ACT'
EXACTLY_DIR__REL_TMP = 'EXACTLY_TMP'
EXACTLY_DIR__REL_RESULT = 'EXACTLY_RESULT'

REL_TMP_OPTION_NAME = argument.OptionName(long_name='rel-tmp')
REL_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act')
REL_RESULT_OPTION_NAME = argument.OptionName(long_name='rel-result')
REL_CWD_OPTION_NAME = argument.OptionName(long_name='rel-cd')
REL_HDS_CASE_OPTION_NAME = argument.OptionName(long_name='rel-home')
REL_HDS_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act-home')
REL_SYMBOL_OPTION_NAME = argument.OptionName(long_name='rel')
REL_SOURCE_FILE_DIR_OPTION_NAME = argument.OptionName('rel-here')

REL_TMP_OPTION = long_option_syntax(REL_TMP_OPTION_NAME.long)
REL_ACT_OPTION = long_option_syntax(REL_ACT_OPTION_NAME.long)
REL_RESULT_OPTION = long_option_syntax(REL_RESULT_OPTION_NAME.long)
REL_CWD_OPTION = long_option_syntax(REL_CWD_OPTION_NAME.long)
REL_HDS_CASE_OPTION = long_option_syntax(REL_HDS_CASE_OPTION_NAME.long)
REL_HDS_ACT_OPTION = long_option_syntax(REL_HDS_ACT_OPTION_NAME.long)
REL_symbol_OPTION = long_option_syntax(REL_SYMBOL_OPTION_NAME.long)
REL_source_file_dir_OPTION = long_option_syntax(REL_SOURCE_FILE_DIR_OPTION_NAME.long)

HDS_DIR_DISPLAY_ORDER = (
    RelHdsOptionType.REL_HDS_CASE,
    RelHdsOptionType.REL_HDS_ACT,
)

SDS_DIR_DISPLAY_ORDER = (
    RelSdsOptionType.REL_ACT,
    RelSdsOptionType.REL_TMP,
    RelSdsOptionType.REL_RESULT,
)

DIR_DISPLAY_ORDER = (
    RelOptionType.REL_HDS_CASE,
    RelOptionType.REL_HDS_ACT,
    RelOptionType.REL_ACT,
    RelOptionType.REL_TMP,
    RelOptionType.REL_RESULT,
    RelOptionType.REL_CWD,
)


def sort_rel_options(options: Set[RelOptionType]) -> Sequence[RelOptionType]:
    ret_val = []

    for any_opt in DIR_DISPLAY_ORDER:
        if any_opt in options:
            ret_val.append(any_opt)

    return ret_val
