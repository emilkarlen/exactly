from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import str_matcher, matcher
from exactly_lib.definitions.primitives.file_or_dir_contents import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.util.cli_syntax.elements import argument as a

NOT_ARGUMENT = logic.NOT_OPERATOR_NAME
EMPTY_ARGUMENT = EMPTINESS_CHECK_ARGUMENT
EQUALS_ARGUMENT = 'equals'
EQUALS_ARGUMENT__ALTERNATIVE = '=='
MATCHES_ARGUMENT = str_matcher.MATCH_REGEX_ARGUMENT
MATCHES_ARGUMENT__ALTERNATIVE = str_matcher.MATCH_REGEX_ARGUMENT__SHORT
RUN_PROGRAM_ARGUMENT = matcher.RUN_PROGRAM

FULL_MATCH_ARGUMENT_OPTION = a.OptionName(long_name='full')

NUM_LINES_ARGUMENT = 'num-lines'

LINE_ARGUMENT = 'line'

NUM_LINES_DESCRIPTION = 'number of lines'
