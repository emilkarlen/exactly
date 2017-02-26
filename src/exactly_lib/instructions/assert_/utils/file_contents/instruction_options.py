from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(WITH_REPLACED_ENV_VARS_OPTION_NAME.long)
NOT_ARGUMENT = '!'
EMPTY_ARGUMENT = 'empty'
EQUALS_ARGUMENT = 'equals'
CONTAINS_ARGUMENT = 'contains'
