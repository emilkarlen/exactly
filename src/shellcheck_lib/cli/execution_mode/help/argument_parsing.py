from shellcheck_lib.cli import argument_parsing_utils

from .settings import HelpSettings


INSTRUCTIONS = 'instructions'


def parse(help_command_arguments: list) -> HelpSettings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    if len(help_command_arguments) != 1:
        raise argument_parsing_utils.ArgumentParsingError(None,
                                                          'Invalid number of arguments.')
    argument = help_command_arguments[0]
    if argument != INSTRUCTIONS:
        raise argument_parsing_utils.ArgumentParsingError(None,
                                                          'Invalid argument: ' + argument)
    return HelpSettings()
