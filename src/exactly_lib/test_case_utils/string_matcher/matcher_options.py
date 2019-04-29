from exactly_lib.definitions.instruction_arguments import NEGATION_ARGUMENT_STR
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.util.cli_syntax.elements import argument as a

NOT_ARGUMENT = NEGATION_ARGUMENT_STR
EMPTY_ARGUMENT = EMPTINESS_CHECK_ARGUMENT
EQUALS_ARGUMENT = 'equals'
MATCHES_ARGUMENT = 'matches'

FULL_MATCH_ARGUMENT_OPTION = a.OptionName(long_name='full')

NUM_LINES_ARGUMENT = 'num-lines'

LINE_ARGUMENT = 'line'

NUM_LINES_DESCRIPTION = 'number of lines'
