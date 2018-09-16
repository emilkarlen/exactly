from exactly_lib.definitions import instruction_arguments
from exactly_lib.util.cli_syntax import short_and_long_option_syntax

HELP_COMMAND = 'help'
SUITE_COMMAND = 'suite'

COMMAND_DESCRIPTIONS = {
    HELP_COMMAND: 'Help system (use "help help" for help on help.)',
    SUITE_COMMAND: 'Runs a test suite (use "help suite" for help.)'
}

SHELL_COMMAND = instruction_arguments.COMMAND_ARGUMENT.name

OPTION_FOR_ACTOR__LONG = 'actor'
OPTION_FOR_ACTOR = short_and_long_option_syntax.long_syntax(OPTION_FOR_ACTOR__LONG)

ACTOR_OPTION_ARGUMENT = SHELL_COMMAND
