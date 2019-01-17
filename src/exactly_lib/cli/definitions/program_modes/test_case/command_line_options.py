from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.util.cli_syntax import short_and_long_option_syntax

OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG = 'keep'
OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT = 'k'
OPTION_FOR_KEEPING_SANDBOX_DIRECTORY = short_and_long_option_syntax.long_syntax(
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG)

OPTION_FOR_EXECUTING_ACT_PHASE__LONG = 'act'
OPTION_FOR_EXECUTING_ACT_PHASE = short_and_long_option_syntax.long_syntax(OPTION_FOR_EXECUTING_ACT_PHASE__LONG)

OPTION_FOR_PREPROCESSOR__LONG = 'preprocessor'
OPTION_FOR_PREPROCESSOR = short_and_long_option_syntax.long_syntax(OPTION_FOR_PREPROCESSOR__LONG)

PREPROCESSOR_OPTION_ARGUMENT = common_cli_options.SHELL_COMMAND

OPTION_FOR_SUITE__LONG = 'suite'
OPTION_FOR_SUITE = short_and_long_option_syntax.long_syntax(OPTION_FOR_SUITE__LONG)

SUITE_OPTION_METAVAR = 'FILE'

TEST_CASE_FILE_ARGUMENT = 'FILE'
