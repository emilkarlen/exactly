from exactly_lib.definitions.instruction_arguments import NEGATION_ARGUMENT_STR, EXISTS_QUANTIFIER_ARGUMENT, \
    ALL_QUANTIFIER_ARGUMENT
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.util.cli_syntax.elements import argument as a

NOT_ARGUMENT = NEGATION_ARGUMENT_STR
EMPTY_ARGUMENT = EMPTINESS_CHECK_ARGUMENT
EQUALS_ARGUMENT = 'equals'
MATCHES_ARGUMENT = 'matches'

FULL_MATCH_ARGUMENT_OPTION = a.OptionName(long_name='full')

NUM_LINES_ARGUMENT = 'num-lines'

LINE_ARGUMENT = 'line'

ALL_CHECKS = (
    EQUALS_ARGUMENT,
    EMPTY_ARGUMENT,
    MATCHES_ARGUMENT,
    ' '.join([EXISTS_QUANTIFIER_ARGUMENT, LINE_ARGUMENT]),
    ' '.join([ALL_QUANTIFIER_ARGUMENT, LINE_ARGUMENT]),
    NUM_LINES_ARGUMENT,
)

NUM_LINES_DESCRIPTION = 'number of lines'
