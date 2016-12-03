from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.cli.program_modes.help.html_documentation.help_request import HtmlDocHelpRequest
from exactly_lib.cli.program_modes.help.program_modes import help_request
from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import *
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME, ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.test_case import phase_identifier

HELP = 'help'
INSTRUCTIONS = 'instructions'
TEST_CASE = 'case'
TEST_SUITE = 'suite'
SPECIFICATION = 'spec'
CONCEPT = CONCEPT_ENTITY_TYPE_NAME
ACTOR = ACTOR_ENTITY_TYPE_NAME
HTML_DOCUMENTATION = 'htmldoc'


class HelpError(Exception):
    def __init__(self,
                 msg: str):
        self.msg = msg


def parse(application_help: ApplicationHelp,
          help_command_arguments: list) -> help_request.HelpRequest:
    """
    :raises HelpError Invalid usage
    """
    return Parser(application_help).apply(help_command_arguments)


class Parser:
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help

    def apply(self, help_command_arguments: list) -> help_request.HelpRequest:
        """
        :raises HelpError Invalid usage
        """
        if not help_command_arguments:
            return MainProgramHelpRequest(MainProgramHelpItem.PROGRAM)
        command_argument = help_command_arguments[0].lower()
        if command_argument == HELP:
            return MainProgramHelpRequest(MainProgramHelpItem.HELP)
        if command_argument in _ENTITY_TYPE_NAME_2_ENTITY_HELP:
            return self._parse_entity_help(command_argument, help_command_arguments[1:])
        if command_argument == HTML_DOCUMENTATION:
            return self._parse_xhtml_help(help_command_arguments[1:])
        if command_argument == TEST_CASE:
            if len(help_command_arguments) == 1:
                return TestCaseHelpRequest(TestCaseHelpItem.CLI_SYNTAX, None, None)
            elif help_command_arguments[1:] == [SPECIFICATION]:
                return TestCaseHelpRequest(TestCaseHelpItem.SPECIFICATION, None, None)
            else:
                raise HelpError('Invalid number of arguments for help command. Use help help, for help.')
        if command_argument == TEST_SUITE:
            return self._parse_suite_help(help_command_arguments[1:])
        if len(help_command_arguments) == 2:
            return self._parse_instruction_in_phase(command_argument,
                                                    help_command_arguments[1])
        if len(help_command_arguments) != 1:
            raise HelpError('Invalid number of arguments for help command. Use help help, for help.')
        argument = command_argument
        if argument == INSTRUCTIONS:
            return TestCaseHelpRequest(TestCaseHelpItem.INSTRUCTION_SET, None, None)
        case_help = self.application_help.test_case_help
        if argument in case_help.phase_name_2_phase_help:
            return TestCaseHelpRequest(TestCaseHelpItem.PHASE,
                                       argument,
                                       case_help.phase_name_2_phase_help[argument])
        return self._parse_instruction_search_when_not_a_phase(argument)

    def _parse_suite_help(self,
                          arguments: list) -> TestSuiteHelpRequest:
        if not arguments:
            return TestSuiteHelpRequest(TestSuiteHelpItem.CLI_SYNTAX,
                                        None, None)
        if arguments[0] == SPECIFICATION and len(arguments) == 1:
            return TestSuiteHelpRequest(TestSuiteHelpItem.SPECIFICATION, None, None)
        section_name = arguments.pop(0)
        test_suite_section_help = self._lookup_suite_section(section_name)
        if not arguments:
            return TestSuiteHelpRequest(TestSuiteHelpItem.SECTION,
                                        section_name,
                                        test_suite_section_help)
        if len(arguments) != 1:
            raise HelpError('Invalid help request: too many arguments.')
        if not test_suite_section_help.has_instructions:
            raise HelpError('Section "%s" does not have instructions.')
        instruction_name = arguments[0]
        try:
            description = test_suite_section_help.instruction_set.name_2_description[instruction_name]
            return TestSuiteHelpRequest(
                TestSuiteHelpItem.INSTRUCTION,
                instruction_name,
                description)
        except KeyError:
            msg = 'The section %s does not contain the instruction: %s' % (section_name, instruction_name)
            raise HelpError(msg)

    def _lookup_suite_section(self, section_name: str) -> SectionDocumentation:
        for test_suite_section_help in self.application_help.test_suite_help.section_helps:
            if test_suite_section_help.name.plain == section_name:
                return test_suite_section_help
        raise HelpError('Not a test-suite section: "%s"' % section_name)

    def _parse_instruction_in_phase(self,
                                    phase_name: str,
                                    instruction_name: str) -> TestCaseHelpRequest:
        try:
            test_case_phase_help = self.application_help.test_case_help.phase_name_2_phase_help[phase_name]
            if not test_case_phase_help.has_instructions:
                msg = 'The phase %s does not use instructions.' % instruction_name
                raise HelpError(msg)
            if instruction_name == INSTRUCTIONS:
                return TestCaseHelpRequest(
                    TestCaseHelpItem.PHASE_INSTRUCTION_LIST,
                    phase_name,
                    test_case_phase_help)
            try:
                description = test_case_phase_help.instruction_set.name_2_description[instruction_name]
                return TestCaseHelpRequest(
                    TestCaseHelpItem.INSTRUCTION,
                    instruction_name,
                    description)
            except KeyError:
                msg = 'The phase %s does not contain the instruction: %s' % (phase_name, instruction_name)
                raise HelpError(msg)
        except KeyError:
            raise HelpError('There is no phase with the name "%s"' % phase_name)

    def _parse_instruction_search_when_not_a_phase(self, instruction_name) -> TestCaseHelpRequest:
        phase_and_instr_descr_list = []
        test_case_phase_helps = self.application_help.test_case_help.phase_helps_in_order_of_execution
        for test_case_phase_help in test_case_phase_helps:
            if test_case_phase_help.has_instructions:
                name_2_description = test_case_phase_help.instruction_set.name_2_description
                if instruction_name in name_2_description:
                    phase_and_instr_descr_list.append((test_case_phase_help.name,
                                                       name_2_description[instruction_name]))
        if not phase_and_instr_descr_list:
            msg = 'Neither the name of a phase nor of an instruction: "%s"' % instruction_name
            raise HelpError(msg)
        return TestCaseHelpRequest(
            TestCaseHelpItem.INSTRUCTION_SEARCH,
            instruction_name,
            phase_and_instr_descr_list)

    def _parse_entity_help(self, entity_type_name: str, arguments: list) -> EntityHelpRequest:
        if not arguments:
            return EntityHelpRequest(entity_type_name, EntityHelpItem.ALL_ENTITIES_LIST)
        name_to_lookup = ' '.join(arguments).lower()
        entities_help = _ENTITY_TYPE_NAME_2_ENTITY_HELP[entity_type_name](self.application_help)
        try:
            entity = entities_help.lookup_by_name_in_singular(name_to_lookup)
            return EntityHelpRequest(entity_type_name, EntityHelpItem.INDIVIDUAL_ENTITY, entity)
        except KeyError:
            raise HelpError('%s does not exist: "%s"' % (entity_type_name.capitalize(), name_to_lookup))

    def _parse_xhtml_help(self, arguments: list) -> HtmlDocHelpRequest:
        if arguments:
            raise HelpError('The %s command expects no arguments.' % HTML_DOCUMENTATION)
        return HtmlDocHelpRequest()


def _is_name_of_phase(name: str):
    return name in map(lambda x: x.identifier, phase_identifier.ALL)


_ENTITY_TYPE_NAME_2_ENTITY_HELP = {
    ACTOR_ENTITY_TYPE_NAME: ApplicationHelp.actors_help.fget,
    CONCEPT_ENTITY_TYPE_NAME: ApplicationHelp.concepts_help.fget,
}
