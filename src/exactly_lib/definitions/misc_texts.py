from exactly_lib.definitions.formatting import misc_name_with_formatting
from exactly_lib.util import name

SYNTAX_ERROR_NAME = name.a_name(name.name_with_plural_s('syntax error'))

FILE_ACCESS_ERROR_NAME = name.a_name(name.name_with_plural_s('file access error'))

OS_PROCESS_NAME = misc_name_with_formatting(
    name.an_name(name.Name('OS process',
                           'OS processes')))

EXIT_IDENTIFIER = misc_name_with_formatting(
    name.an_name(name.name_with_plural_s('exit identifier')))

EXIT_CODE = name.an_name(name.name_with_plural_s('exit code'))

EXIT_IDENTIFIER_TITLE = EXIT_IDENTIFIER.singular.capitalize()

IS_A_SHELL_CMD = """is a shell command (with optional arguments), using Unix shell syntax."""

RELATIVITY = misc_name_with_formatting(
    name.a_name(name.Name('relativity', 'relativities')))

EXIT_CODE_TITLE = EXIT_CODE.singular.capitalize()

TEST_CASE_SPEC_TITLE = 'Specification of test case functionality'

TEST_SUITE_SPEC_TITLE = 'Specification of test suite functionality'

SYMBOL_COMMAND_SINGLE_LINE_DESCRIPTION = 'Reports the usage of symbols in a test case'

SUITE_COMMAND_SINGLE_LINE_DESCRIPTION = 'Runs a test suite'
