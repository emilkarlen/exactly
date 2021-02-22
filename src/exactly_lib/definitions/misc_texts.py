from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import all_entity_types
from exactly_lib.definitions.formatting import misc_name_with_formatting
from exactly_lib.util.str_ import name

WHITESPACE = 'whitespace'

RESERVED_WORD_NAME = name.a_name(name.name_with_plural_s('reserved word'))

SYNTAX_ERROR_NAME = name.a_name(name.name_with_plural_s('syntax error'))

FILE_ACCESS_ERROR_NAME = name.a_name(name.name_with_plural_s('file access error'))

EXIT_IDENTIFIER = misc_name_with_formatting(
    name.an_name(name.name_with_plural_s('exit identifier')))

EXIT_CODE = misc_name_with_formatting(
    name.an_name(name.name_with_plural_s('exit code'))
)
EXIT_CODE_TITLE = EXIT_CODE.singular.capitalize()

STDOUT = 'stdout'
STDERR = 'stderr'
STDIN = 'stdin'

OS_PROCESS_NAME = misc_name_with_formatting(
    name.an_name(name.Name('OS process',
                           'OS processes')))

CURRENT_OS = 'current OS'

NEW_LINE_STRING_CONSTANT = formatting.string_constant('\\n')

LINES_ARE_SEPARATED_BY_NEW_LINE = 'Lines are separated by {}, regardless of the {}.'.format(
    NEW_LINE_STRING_CONSTANT,
    CURRENT_OS,
)

EXECUTABLE_FILE = name.an_name(name.name_with_plural_s('executable file'))
EXTERNAL_PROGRAM = misc_name_with_formatting(name.an_name(name.name_with_plural_s('external program')))
SHELL_COMMAND = name.a_name(name.name_with_plural_s('shell command'))
SHELL_COMMAND_LINE = name.a_name(name.name_with_plural_s('shell command line'))
SYSTEM_COMMAND_LINE = name.a_name(name.name_with_plural_s('COMMAND-LINE'))
IS_A_SHELL_CMD = ' '.join(('is a', SHELL_COMMAND.singular,
                           '(with optional arguments), using Unix shell syntax.'))
IS_A_SYSTEM_CMD = ' '.join(('is a command line',
                            '(with optional arguments), using Unix shell syntax.'))
PLAIN_STRING = name.a_name(name.name_with_plural_s('string'))
# ^ The concept of a string - independent of the string type or the matcher/transformer model.

EXIT_IDENTIFIER_TITLE = EXIT_IDENTIFIER.singular.capitalize()

RELATIVITY = misc_name_with_formatting(
    name.a_name(name.Name('relativity', 'relativities')))

TEST_CASE_SPEC_TITLE = 'Specification of test case functionality'

OS_PROCESS_ENVIRONMENT_SECTION_HEADER = OS_PROCESS_NAME.singular + ' environment'

TEST_SUITE_SPEC_TITLE = 'Specification of test suite functionality'

SYMBOL_COMMAND_SINGLE_LINE_DESCRIPTION = (
    'Reports the usage of {symbols} in a test case or test suite'.format(
        symbols=all_entity_types.SYMBOL_CONCEPT_NAME.plural
    )
)

SUITE_COMMAND_SINGLE_LINE_DESCRIPTION = 'Runs a test suite'

SYSTEM_PROGRAM_DESCRIPTION = 'A program installed on the {current_os} - a program in the OS PATH.'.format(
    current_os=CURRENT_OS
)
SYSTEM_CMD_SINGLE_LINE_DESCRIPTION = 'Runs a program installed on the current system (in the OS PATH)'

SYMBOLIC_LINKS_ARE_FOLLOWED = 'Symbolic links are followed'
