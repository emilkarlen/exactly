from typing import List

from exactly_lib.cli.definitions.program_modes.help import command_line_options as cl_opts
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.cli.program_modes.help.error import HelpError
from exactly_lib.cli.program_modes.help.html_doc.help_request import HtmlDocHelpRequest
from exactly_lib.cli.program_modes.help.program_modes import help_request
from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.symbol.help_request import SymbolHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import *
from exactly_lib.cli.program_modes.help.util import argument_value_lookup
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.contents_structure.entity import EntityTypeHelp
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation


def parse(application_help: ApplicationHelp,
          help_command_arguments: List[str]) -> help_request.HelpRequest:
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
        :raises HelpError: Invalid usage
        """
        if not help_command_arguments:
            return MainProgramHelpRequest(MainProgramHelpItem.PROGRAM)
        command_argument = help_command_arguments[0].lower()
        if command_argument == cl_opts.HELP:
            return MainProgramHelpRequest(MainProgramHelpItem.HELP)
        if command_argument in self.application_help.entity_type_id_2_entity_type_conf:
            return self._parse_entity_help(command_argument, help_command_arguments[1:])
        if command_argument == cl_opts.HTML_DOCUMENTATION:
            return self._parse_html_doc_help(help_command_arguments[1:])
        if command_argument == cl_opts.TEST_CASE:
            if len(help_command_arguments) == 1:
                return TestCaseHelpRequest(TestCaseHelpItem.CLI_SYNTAX, None, None)
            elif help_command_arguments[1:] == [cl_opts.SPECIFICATION]:
                return TestCaseHelpRequest(TestCaseHelpItem.SPECIFICATION, None, None)
            else:
                raise HelpError('Invalid number of arguments for help command. Use help help, for help.')
        if command_argument == cl_opts.TEST_SUITE:
            return self._parse_suite_help(help_command_arguments[1:])
        if command_argument == cl_opts.SYMBOL:
            return self._parse_symbol_help(help_command_arguments[1:])
        if len(help_command_arguments) == 2:
            return self._parse_instruction_in_phase(command_argument,
                                                    help_command_arguments[1])
        if len(help_command_arguments) != 1:
            raise HelpError('Invalid number of arguments for help command. Use help help, for help.')
        argument = command_argument
        if argument == cl_opts.INSTRUCTIONS:
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
        if arguments[0] == cl_opts.SPECIFICATION and len(arguments) == 1:
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
        match = argument_value_lookup.lookup_argument__dict('instruction',
                                                            instruction_name,
                                                            test_suite_section_help.instruction_set.name_2_description)
        return TestSuiteHelpRequest(TestSuiteHelpItem.INSTRUCTION,
                                    match.key,
                                    match.value)

    def _parse_symbol_help(self,
                           arguments: List[str]) -> SymbolHelpRequest:
        if not arguments:
            return SymbolHelpRequest()
        raise HelpError('Invalid help request: too many arguments.')

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
        except KeyError:
            raise HelpError('There is no phase with the name "%s"' % phase_name)
        if not test_case_phase_help.has_instructions:
            msg = 'The phase %s does not use instructions.' % instruction_name
            raise HelpError(msg)
        if instruction_name == cl_opts.INSTRUCTIONS:
            return TestCaseHelpRequest(TestCaseHelpItem.PHASE_INSTRUCTION_LIST,
                                       phase_name,
                                       test_case_phase_help)
        match = argument_value_lookup.lookup_argument__dict('instruction',
                                                            instruction_name,
                                                            test_case_phase_help.instruction_set.name_2_description)
        return TestCaseHelpRequest(TestCaseHelpItem.INSTRUCTION,
                                   match.key,
                                   match.value,
                                   not match.is_exact_match)

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
        return TestCaseHelpRequest(TestCaseHelpItem.INSTRUCTION_SEARCH,
                                   instruction_name,
                                   phase_and_instr_descr_list)

    def _parse_entity_help(self, entity_type_name: str, arguments: List[str]) -> EntityHelpRequest:
        if not arguments:
            return EntityHelpRequest(entity_type_name, EntityHelpItem.ALL_ENTITIES_LIST)
        entities_help = self.application_help.entity_type_id_2_entity_type_conf[entity_type_name].entities_help
        match = lookup_entity(entities_help, arguments)
        return EntityHelpRequest(entity_type_name,
                                 EntityHelpItem.INDIVIDUAL_ENTITY,
                                 match.value,
                                 not match.is_exact_match)

    @staticmethod
    def _parse_html_doc_help(arguments: List[str]) -> HtmlDocHelpRequest:
        if arguments:
            raise HelpError('The %s command expects no arguments.' % cl_opts.HTML_DOCUMENTATION)
        return HtmlDocHelpRequest()


def lookup_entity(entities: EntityTypeHelp, arguments: List[str]) -> argument_value_lookup.Match:
    return argument_value_lookup.lookup_argument(entities.names.name.singular,
                                                 ' '.join(arguments),
                                                 argument_value_lookup.entities_key_value_iter(entities))
