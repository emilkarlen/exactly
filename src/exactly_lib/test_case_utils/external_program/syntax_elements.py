from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

SHELL_COMMAND_TOKEN = instruction_names.SHELL_INSTRUCTION_NAME

REL_OPTION_ARG_CONF = parse_file_ref.ALL_REL_OPTIONS_CONFIG

INTERPRET_OPTION_NAME = a.OptionName(long_name='interpret')
INTERPRET_OPTION = long_option_syntax(INTERPRET_OPTION_NAME.long)

SOURCE_OPTION_NAME = a.OptionName(long_name='source')
SOURCE_OPTION = long_option_syntax(SOURCE_OPTION_NAME.long)

OPTIONS_SEPARATOR_ARGUMENT = '--'

SOURCE_SYNTAX_ELEMENT_NAME = 'SOURCE'

LIST_DELIMITER_START = '('
LIST_DELIMITER_END = ')'

PYTHON_EXECUTABLE_OPTION_NAME = argument.OptionName(long_name='python')
PYTHON_EXECUTABLE_OPTION_STRING = long_option_syntax(PYTHON_EXECUTABLE_OPTION_NAME.long)