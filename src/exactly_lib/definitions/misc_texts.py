from exactly_lib.definitions.entity import all_entity_types
from exactly_lib.definitions.formatting import misc_name_with_formatting
from exactly_lib.util import name

NOTE_LINE_HEADER = 'Note:'

SYNTAX_ERROR_NAME = name.a_name(name.name_with_plural_s('syntax error'))

FILE_ACCESS_ERROR_NAME = name.a_name(name.name_with_plural_s('file access error'))

OS_PROCESS_NAME = misc_name_with_formatting(
    name.an_name(name.Name('OS process',
                           'OS processes')))

EXIT_IDENTIFIER = misc_name_with_formatting(
    name.an_name(name.name_with_plural_s('exit identifier')))

EXIT_CODE = name.an_name(name.name_with_plural_s('exit code'))

EXECUTABLE_FILE = name.an_name(name.name_with_plural_s('executable file'))
SHELL_COMMAND = name.a_name(name.name_with_plural_s('shell command'))
SHELL_COMMAND_LINE = name.a_name(name.name_with_plural_s('shell command line'))
IS_A_SHELL_CMD = ''.join(('is a ', SHELL_COMMAND.singular,
                          ' (with optional arguments), using Unix shell syntax.'))

EXIT_IDENTIFIER_TITLE = EXIT_IDENTIFIER.singular.capitalize()

RELATIVITY = misc_name_with_formatting(
    name.a_name(name.Name('relativity', 'relativities')))

EXIT_CODE_TITLE = EXIT_CODE.singular.capitalize()

TEST_CASE_SPEC_TITLE = 'Specification of test case functionality'

OS_PROCESS_ENVIRONMENT_SECTION_HEADER = OS_PROCESS_NAME.singular + ' environment'

TEST_SUITE_SPEC_TITLE = 'Specification of test suite functionality'

SYMBOL_COMMAND_SINGLE_LINE_DESCRIPTION = (
    'Reports the usage of user defined {symbols} in a test case or test suite'.format(
        symbols=all_entity_types.SYMBOL_CONCEPT_NAME.plural
    )
)

SUITE_COMMAND_SINGLE_LINE_DESCRIPTION = 'Runs a test suite'

SYSTEM_PROGRAM_DESCRIPTION = 'A program installed on the current system - a program in the OS PATH.'

SYMBOLIC_LINKS_ARE_FOLLOWED = 'Symbolic links are followed'
