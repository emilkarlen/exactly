from shellcheck_lib.cli.execution_mode.help.contents import ApplicationHelp
from shellcheck_lib.execution import phases

from . import settings

INSTRUCTIONS = 'instructions'
SUITE = 'suite'


class HelpError(Exception):
    def __init__(self,
                 msg: str):
        self.msg = msg


def parse(application_help: ApplicationHelp,
          help_command_arguments: list) -> settings.HelpSettings:
    """
    :raises HelpError Invalid usage
    """
    return Parser(application_help).apply(help_command_arguments)


class Parser:
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help

    def apply(self,
              help_command_arguments: list) -> settings.HelpSettings:
        """
        :raises HelpError Invalid usage
        """
        if not help_command_arguments:
            return settings.ProgramHelpSettings()
        if len(help_command_arguments) == 2:
            return self._parse_instruction_in_phase(help_command_arguments[0],
                                                    help_command_arguments[1])
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

    def _parse_instruction_in_phase(self,
                                    phase_name: str,
                                    instruction_name: str) -> settings.TestCaseHelpSettings:
        try:
            instruction_set = self.application_help.instructions_setup.phase_2_instruction_set[phase_name]
            try:
                sing_instr_setup = instruction_set[instruction_name]
                return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.INSTRUCTION,
                                                     instruction_name,
                                                     sing_instr_setup.description)
            except KeyError:
                msg = 'The phase %s does not contain the instruction: %s' % (phase_name, instruction_name)
                raise HelpError(msg)
        except KeyError:
            if phase_name == phases.ACT.identifier:
                msg = 'The %s phase does not have instructions' % phases.ACT.identifier
            else:
                msg = 'Unknown phase: ' + phase_name
            raise HelpError(msg)


def _is_name_of_phase(name: str):
    return name in map(lambda x: x.identifier, phases.ALL)
