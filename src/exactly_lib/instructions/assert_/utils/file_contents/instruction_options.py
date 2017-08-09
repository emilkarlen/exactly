from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(WITH_REPLACED_ENV_VARS_OPTION_NAME.long)
NOT_ARGUMENT = NEGATION_ARGUMENT_STR
EMPTY_ARGUMENT = EMPTINESS_CHECK_ARGUMENT
EQUALS_ARGUMENT = 'equals'
CONTAINS_ARGUMENT = 'contains'
