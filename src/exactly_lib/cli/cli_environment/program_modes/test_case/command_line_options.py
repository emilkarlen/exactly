from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG = 'keep'
OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT = 'k'
OPTION_FOR_KEEPING_SANDBOX_DIRECTORY = long_option_syntax(OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG)

OPTION_FOR_EXECUTING_ACT_PHASE__LONG = 'act'
OPTION_FOR_EXECUTING_ACT_PHASE = long_option_syntax(OPTION_FOR_EXECUTING_ACT_PHASE__LONG)

OPTION_FOR_PREPROCESSOR__LONG = 'preprocessor'
OPTION_FOR_PREPROCESSOR = long_option_syntax(OPTION_FOR_PREPROCESSOR__LONG)

PREPROCESSOR_OPTION_ARGUMENT = 'PROGRAM'

OPTION_FOR_ACTOR__LONG = 'actor'
OPTION_FOR_ACTOR = long_option_syntax(OPTION_FOR_ACTOR__LONG)

OPTION_FOR_SUITE__LONG = 'suite'
OPTION_FOR_SUITE = long_option_syntax(OPTION_FOR_SUITE__LONG)

SUITE_OPTION_METAVAR = 'SUITE'

ACTOR_OPTION_ARGUMENT = 'PROGRAM'

TEST_CASE_FILE_ARGUMENT = 'FILE'
