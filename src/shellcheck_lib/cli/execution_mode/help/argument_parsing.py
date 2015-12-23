from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup

from . import settings

INSTRUCTIONS = 'instructions'
SUITE = 'suite'


class HelpError(Exception):
    def __init__(self,
                 msg: str):
        self.msg = msg


def parse(instruction_set: InstructionsSetup,
          help_command_arguments: list) -> settings.HelpSettings:
    """
    :raises HelpError Invalid usage
    """
    if not help_command_arguments:
        return settings.ProgramHelpSettings()
    if len(help_command_arguments) != 1:
        raise HelpError('Invalid number of arguments.')
    argument = help_command_arguments[0]
    if argument == INSTRUCTIONS:
        return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.INSTRUCTION_SET, None, None)
    if argument == SUITE:
        return settings.TestSuiteHelpSettings(settings.TestSuiteHelpItem.OVERVIEW, None)
    if _is_name_of_phase(argument):
        return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.PHASE,
                                             argument,
                                             None)
    raise HelpError('Invalid argument: ' + argument)


def _is_name_of_phase(x: str):
    return x in map(lambda x: x.identifier, phases.ALL)
