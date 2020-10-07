from exactly_lib.definitions.primitives import program
from exactly_lib.util.cli_syntax.elements import argument as a

IDENTITY_TRANSFORMER_NAME = 'identity'
REPLACE_TRANSFORMER_NAME = 'replace'
FILTER_TRANSFORMER_NAME = 'filter'
TO_UPPER_CASE = 'to-upper-case'
TO_LOWER_CASE = 'to-lower-case'
STRIP_TRAILING_NEW_LINES = 'strip-trailing-new-lines'
STRIP_TRAILING_SPACE = 'strip-trailing-space'
STRIP_SPACE = 'strip-space'
TCDS_PATH_REPLACEMENT = 'replace-test-case-dirs'
SEQUENCE_OPERATOR_NAME = '|'
RUN_PROGRAM_TRANSFORMER_NAME = program.RUN_PROGRAM_PRIMITIVE
RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME = program.WITH_IGNORED_EXIT_CODE_OPTION_NAME

PRESERVE_NEW_LINES_OPTION_NAME = a.OptionName(long_name='preserve-new-lines')
PRESERVE_NEW_LINES_OPTION = a.Option(PRESERVE_NEW_LINES_OPTION_NAME)
