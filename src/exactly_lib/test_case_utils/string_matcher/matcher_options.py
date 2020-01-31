from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives.file_or_dir_contents import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.definitions.primitives.str_matcher import MATCH_REGEX_OR_GLOB_PATTERN_CHECK_ARGUMENT
from exactly_lib.util.cli_syntax.elements import argument as a

NOT_ARGUMENT = logic.NOT_OPERATOR_NAME
EMPTY_ARGUMENT = EMPTINESS_CHECK_ARGUMENT
EQUALS_ARGUMENT = 'equals'
MATCHES_ARGUMENT = MATCH_REGEX_OR_GLOB_PATTERN_CHECK_ARGUMENT

FULL_MATCH_ARGUMENT_OPTION = a.OptionName(long_name='full')

NUM_LINES_ARGUMENT = 'num-lines'

LINE_ARGUMENT = 'line'

NUM_LINES_DESCRIPTION = 'number of lines'
