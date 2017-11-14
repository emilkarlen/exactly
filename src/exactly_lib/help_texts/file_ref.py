from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelSdsOptionType
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

RELATIVITY_DESCRIPTION_ABSOLUTE = 'absolute'
RELATIVITY_DESCRIPTION_HOME_CASE = 'home directory'
RELATIVITY_DESCRIPTION_HOME_ACT = 'act-home directory'
RELATIVITY_DESCRIPTION_CWD = 'current directory'
RELATIVITY_DESCRIPTION_ACT = 'act directory'
RELATIVITY_DESCRIPTION_TMP = 'tmp directory'
RELATIVITY_DESCRIPTION_RESULT = 'result directory'

EXACTLY_DIR__REL_HOME_CASE = 'EXACTLY_HOME'
EXACTLY_DIR__REL_HOME_ACT = 'EXACTLY_ACT_HOME'
EXACTLY_DIR__REL_ACT = 'EXACTLY_ACT'
EXACTLY_DIR__REL_TMP = 'EXACTLY_TMP'
EXACTLY_DIR__REL_RESULT = 'EXACTLY_RESULT'

REL_TMP_OPTION_NAME = argument.OptionName(long_name='rel-tmp')
REL_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act')
REL_RESULT_OPTION_NAME = argument.OptionName(long_name='rel-result')
REL_CWD_OPTION_NAME = argument.OptionName(long_name='rel-cd')
REL_HOME_CASE_OPTION_NAME = argument.OptionName(long_name='rel-home')
REL_HOME_ACT_OPTION_NAME = argument.OptionName(long_name='rel-act-home')
REL_SYMBOL_OPTION_NAME = argument.OptionName(long_name='rel')

REL_TMP_OPTION = long_option_syntax(REL_TMP_OPTION_NAME.long)
REL_ACT_OPTION = long_option_syntax(REL_ACT_OPTION_NAME.long)
REL_RESULT_OPTION = long_option_syntax(REL_RESULT_OPTION_NAME.long)
REL_CWD_OPTION = long_option_syntax(REL_CWD_OPTION_NAME.long)
REL_HOME_CASE_OPTION = long_option_syntax(REL_HOME_CASE_OPTION_NAME.long)
REL_HOME_ACT_OPTION = long_option_syntax(REL_HOME_ACT_OPTION_NAME.long)
REL_symbol_OPTION = long_option_syntax(REL_SYMBOL_OPTION_NAME.long)

HDS_DIR_DISPLAY_ORDER = (
    RelHomeOptionType.REL_HOME_CASE,
    RelHomeOptionType.REL_HOME_ACT,
)

SDS_DIR_DISPLAY_ORDER = (
    RelSdsOptionType.REL_ACT,
    RelSdsOptionType.REL_TMP,
    RelSdsOptionType.REL_RESULT,
)
