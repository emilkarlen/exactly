from exactly_lib.definitions import instruction_arguments, misc_texts
from exactly_lib.util.cli_syntax import short_and_long_option_syntax

HELP_COMMAND = 'help'
SUITE_COMMAND = 'suite'
SYMBOL_COMMAND = 'symbol'

COMMAND_DESCRIPTIONS = {
    HELP_COMMAND: 'Help system (use "{} {}" for help on help.)'.format(HELP_COMMAND, HELP_COMMAND),
    SUITE_COMMAND: '{} (use "{} {}" for help.)'.format(misc_texts.SUITE_COMMAND_SINGLE_LINE_DESCRIPTION,
                                                       HELP_COMMAND, SUITE_COMMAND),
    SYMBOL_COMMAND: '{} (use "{} {}" for help.)'.format(misc_texts.SYMBOL_COMMAND_SINGLE_LINE_DESCRIPTION,
                                                        HELP_COMMAND,
                                                        SYMBOL_COMMAND),
}

SHELL_COMMAND = instruction_arguments.COMMAND_ARGUMENT.name

OPTION_FOR_ACTOR__LONG = 'actor'
OPTION_FOR_ACTOR = short_and_long_option_syntax.long_syntax(OPTION_FOR_ACTOR__LONG)

ACTOR_OPTION_ARGUMENT = SHELL_COMMAND
