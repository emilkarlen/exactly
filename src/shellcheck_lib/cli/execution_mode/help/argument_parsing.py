from shellcheck_lib.test_case.instruction_setup import InstructionsSetup

from .settings import HelpSettings, ProgramHelpSettings, TestCaseHelpSettings, TestCaseHelpItem

INSTRUCTIONS = 'instructions'


class HelpError(Exception):
    def __init__(self,
                 msg: str):
        self.msg = msg


def parse(instruction_set: InstructionsSetup,
          help_command_arguments: list) -> HelpSettings:
    """
    :raises HelpError Invalid usage
    """
    if not help_command_arguments:
        return ProgramHelpSettings()
    if len(help_command_arguments) != 1:
        raise HelpError('Invalid number of arguments.')
    argument = help_command_arguments[0]
    if argument != INSTRUCTIONS:
        raise HelpError('Invalid argument: ' + argument)
    return TestCaseHelpSettings(TestCaseHelpItem.INSTRUCTION_SET, None, None)
