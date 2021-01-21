from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a

SHELL_COMMAND_TOKEN = '$'
SYSTEM_PROGRAM_TOKEN = '%'
SYMBOL_PROGRAM_TOKEN = '@'

RUN_PROGRAM_PRIMITIVE = 'run'

STDIN_OPTION_NAME = a.OptionName(long_name='stdin')
STDIN_OPTION_STR = option_syntax.option_syntax(STDIN_OPTION_NAME)

WITH_IGNORED_EXIT_CODE_OPTION_NAME = a.OptionName(long_name='ignore-exit-code')
