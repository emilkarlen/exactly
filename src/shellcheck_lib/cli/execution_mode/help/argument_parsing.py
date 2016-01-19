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
        if help_command_arguments[0] == SUITE:
            return self._parse_suite_help(help_command_arguments[1:])
        if len(help_command_arguments) == 2:
            return self._parse_instruction_in_phase(help_command_arguments[0],
                                                    help_command_arguments[1])
        if len(help_command_arguments) != 1:
            raise HelpError('Invalid number of arguments. Use help help, for help!')
        argument = help_command_arguments[0]
        if argument == INSTRUCTIONS:
            return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.INSTRUCTION_SET, None, None)
        case_help = self.application_help.test_case_help
        if argument in case_help.phase_name_2_phase_help:
            return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.PHASE,
                                                 argument,
                                                 case_help.phase_name_2_phase_help[argument])
        return self._parse_instruction_search(argument)

    def _parse_suite_help(self, arguments: list) -> settings.TestSuiteHelpSettings:
        if not arguments:
            return settings.TestSuiteHelpSettings(settings.TestSuiteHelpItem.OVERVIEW, None, None)
        if len(arguments) != 1:
            raise HelpError('Invalid help syntax.')
        section_name = arguments[0]
        for test_suite_section_help in self.application_help.test_suite_help.section_helps:
            if test_suite_section_help.name == section_name:
                return settings.TestSuiteHelpSettings(settings.TestSuiteHelpItem.SECTION,
                                                      section_name,
                                                      test_suite_section_help)
        raise HelpError('Unknown section: "%s"' % section_name)

    def _parse_instruction_in_phase(self,
                                    phase_name: str,
                                    instruction_name: str) -> settings.TestCaseHelpSettings:
        try:
            test_case_phase_help = self.application_help.test_case_help.phase_name_2_phase_help[phase_name]
            if not test_case_phase_help.is_phase_with_instructions:
                msg = 'The phase %s does not contain instructions.' % instruction_name
                raise HelpError(msg)
            try:
                description = test_case_phase_help.instruction_set.name_2_description[instruction_name]
                return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.INSTRUCTION,
                                                     instruction_name,
                                                     description)
            except KeyError:
                msg = 'The phase %s does not contain the instruction: %s' % (phase_name, instruction_name)
                raise HelpError(msg)
        except KeyError:
            if phase_name == phases.ACT.identifier:
                msg = 'The %s phase does not have instructions' % phases.ACT.identifier
            else:
                msg = 'Unknown phase: ' + phase_name
            raise HelpError(msg)

    def _parse_instruction_search(self, instruction_name) -> settings.TestCaseHelpSettings:
        phase_and_instr_descr_list = []
        test_case_phase_helps = self.application_help.test_case_help.phase_helps
        for test_case_phase_help in test_case_phase_helps:
            if test_case_phase_help.is_phase_with_instructions:
                name_2_description = test_case_phase_help.instruction_set.name_2_description
                if instruction_name in name_2_description:
                    phase_and_instr_descr_list.append((test_case_phase_help.name,
                                                       name_2_description[instruction_name]))
        if not phase_and_instr_descr_list:
            msg = 'There is no instruction "%s"' % instruction_name
            raise HelpError(msg)
        return settings.TestCaseHelpSettings(settings.TestCaseHelpItem.INSTRUCTION_LIST,
                                             instruction_name,
                                             phase_and_instr_descr_list)


def _is_name_of_phase(name: str):
    return name in map(lambda x: x.identifier, phases.ALL)
