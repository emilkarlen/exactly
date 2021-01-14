from exactly_lib.definitions.primitives import program, string_transformer
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.impls.types.path import path_relativities
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

SHELL_COMMAND_TOKEN = program.SHELL_COMMAND_TOKEN
SYSTEM_PROGRAM_TOKEN = program.SYSTEM_PROGRAM_TOKEN

SYMBOL_REF_PROGRAM_TOKEN = instruction_names.SYMBOL_REF_PROGRAM_INSTRUCTION_NAME

EXE_FILE_REL_OPTION_ARG_CONF = path_relativities.ALL_REL_OPTIONS_ARG_CONFIG

PYTHON_EXECUTABLE_OPTION_NAME = argument.OptionName(long_name='python')
PYTHON_EXECUTABLE_OPTION_STRING = long_option_syntax(PYTHON_EXECUTABLE_OPTION_NAME.long)

REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER = ':>'
EXISTING_FILE_OPTION_NAME = a.OptionName(long_name='existing-file')
EXISTING_DIR_OPTION_NAME = a.OptionName(long_name='existing-dir')
EXISTING_PATH_OPTION_NAME = a.OptionName(long_name='existing-path')

ARGUMENT_SYNTAX_ELEMENT_NAME = a.Named('ARGUMENT')

WITH_TRANSFORMED_CONTENTS_OPTION_NAME = string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME

STDIN_OPTION_NAME = a.OptionName(long_name='stdin')
