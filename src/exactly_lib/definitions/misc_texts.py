from exactly_lib.util import name

SYNTAX_ERROR_NAME = name.a_name(name.name_with_plural_s('syntax error'))

FILE_ACCESS_ERROR_NAME = name.a_name(name.name_with_plural_s('file access error'))

EXIT_IDENTIFIER = name.an_name(name.name_with_plural_s('exit identifier'))

EXIT_CODE = name.an_name(name.name_with_plural_s('exit code'))

EXIT_IDENTIFIER_TITLE = EXIT_IDENTIFIER.singular.capitalize()

EXIT_CODE_TITLE = EXIT_CODE.singular.capitalize()

IS_A_SHELL_CMD = """is a shell command (with optional arguments), using Unix shell syntax."""
