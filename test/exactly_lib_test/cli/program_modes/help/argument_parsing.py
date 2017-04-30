import unittest

from exactly_lib.cli.cli_environment.program_modes.help import arguments_for
from exactly_lib.cli.cli_environment.program_modes.help import command_line_options as clo
from exactly_lib.cli.program_modes.help import argument_parsing as sut
from exactly_lib.cli.program_modes.help.error import HelpError
from exactly_lib.cli.program_modes.help.html_doc.help_request import HtmlDocHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import *
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import *
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.actors.contents_structure import actors_help
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation, \
    concepts_help
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME, SUITE_REPORTER_ENTITY_TYPE_NAME, \
    ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.utils.names import formatting
from exactly_lib_test.cli.program_modes.help.test_resources import entity_lookup_test_cases
from exactly_lib_test.help.actors.test_resources import documentation as actor_doc
from exactly_lib_test.help.concepts.test_resources.documentation import ConceptTestImpl
from exactly_lib_test.help.suite_reporters.test_resources.documentation import SuiteReporterDocTestImpl
from exactly_lib_test.help.test_resources import application_help_for
from exactly_lib_test.help.test_resources import section_documentation, \
    single_line_description_that_identifies_instruction_and_section, \
    SectionDocumentationForSectionWithoutInstructionsTestImpl, application_help_for_suite_sections


class TestProgramHelp(unittest.TestCase):
    def test_program_help(self):
        actual = sut.parse(application_help_for([]),
                           [])
        self.assertIsInstance(actual,
                              MainProgramHelpRequest,
                              'Expecting settings for MainProgram')
        assert isinstance(actual, MainProgramHelpRequest)
        self.assertIs(MainProgramHelpItem.PROGRAM,
                      actual.item,
                      'Expects program help')

    def test_help_help(self):
        actual = sut.parse(application_help_for([]),
                           [clo.HELP])
        self.assertIsInstance(actual,
                              MainProgramHelpRequest,
                              'Expecting settings for MainProgram')
        assert isinstance(actual, MainProgramHelpRequest)
        self.assertIs(MainProgramHelpItem.HELP,
                      actual.item,
                      'Expects MainProgram help for help')


class TestHtmlDocHelp(unittest.TestCase):
    def test_valid_usage(self):
        actual = sut.parse(application_help_for([]),
                           [clo.HTML_DOCUMENTATION])
        self.assertIsInstance(actual,
                              HtmlDocHelpRequest,
                              'Expecting settings for XHTML')

    def test_invalid_usage(self):
        with self.assertRaises(HelpError):
            sut.parse(application_help_for([]),
                      [clo.HTML_DOCUMENTATION, 'superfluous argument'])


class TestTestCasePhase(unittest.TestCase):
    def test_existing_phases(self):
        all_phases = ['phase 1',
                      'phase 2']
        application_help = self._application_help_with_phases(all_phases)
        for phase_name in all_phases:
            self._assert_successful_parsing_of_existing_phase(application_help, phase_name)

    def test_non_existing_phases(self):
        application_help = self._application_help_with_phases(['phase 1',
                                                               'phase 2'])
        arguments = arguments_for.case_phase_for_name('non existing phase')
        with self.assertRaises(HelpError):
            sut.parse(application_help, arguments)

    def _assert_successful_parsing_of_existing_phase(self,
                                                     application_help: ApplicationHelp,
                                                     phase_name: str):
        arguments = arguments_for.case_phase_for_name(phase_name)
        actual = sut.parse(application_help, arguments)
        self._assert_is_single_phase_help(phase_name, actual)

    def _assert_is_single_phase_help(self,
                                     expected_phase_name: str,
                                     actual):
        self.assertIsInstance(actual,
                              TestCaseHelpRequest,
                              'Parse result should be a ' + str(
                                  TestCaseHelpRequest))
        assert isinstance(actual, TestCaseHelpRequest)
        self.assertIs(TestCaseHelpItem.PHASE,
                      actual.item)
        self.assertIsInstance(actual.data,
                              SectionDocumentation)

        self.assertEqual(expected_phase_name,
                         actual.data.name.plain)

    def _application_help_with_phases(self, all_phases):
        return ApplicationHelp(MainProgramHelp(),
                               concepts_help(()),
                               actors_help(()),
                               TestCaseHelp(map(lambda ph_name: section_documentation(ph_name, []),
                                                all_phases)),
                               TestSuiteHelp({}))


class TestTestCaseSingleInstructionInPhase(unittest.TestCase):
    def test_unknown_phase(self):
        application_help = application_help_for([
            section_documentation('phase', ['instruction-name'])
        ])
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.case_instruction_in_phase('non-existing-phase', 'instruction-name'))

    def test_unknown_instruction(self):
        application_help = application_help_for([
            section_documentation('phase-1', ['instruction']),
            section_documentation('empty-phase', []),
        ])
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.case_instruction_in_phase('empty-phase', 'instruction'))

    def test_single_instruction_for_phases_with_instructions(self):
        phase_name = 'the phase name'
        instructions = [phase_name, 'name-that-is-not-the-name-of-a-phase']
        application_help = application_help_for([
            section_documentation(phase_name, instructions),
            section_documentation('other phase than ' + phase_name, instructions)
        ])
        self._assert_is_existing_instruction_in_phase(application_help,
                                                      phase_name,
                                                      'name-that-is-not-the-name-of-a-phase')
        self._assert_is_existing_instruction_in_phase(application_help,
                                                      phase_name,
                                                      phase_name)

    def _assert_is_existing_instruction_in_phase(self,
                                                 application_help: ApplicationHelp,
                                                 phase_name: str,
                                                 instruction_name: str):
        actual = sut.parse(application_help,
                           arguments_for.case_instruction_in_phase(phase_name,
                                                                   instruction_name))
        actual = self._check_is_test_case_settings_for_single_instruction(actual)
        self.assertEqual(actual.name,
                         instruction_name,
                         'Name of instruction')
        single_line_desc_str = actual.data.single_line_description()
        self.assertEqual(single_line_description_that_identifies_instruction_and_section(phase_name,
                                                                                         instruction_name),
                         single_line_desc_str,
                         'The single-line-description in this test is expected to identify (phase,instruction-name)')

    def _check_is_test_case_settings_for_single_instruction(
            self,
            value) -> TestCaseHelpRequest:
        self.assertIsInstance(value, TestCaseHelpRequest,
                              'Should be help for Test Case')
        assert isinstance(value, TestCaseHelpRequest)
        self.assertIs(TestCaseHelpItem.INSTRUCTION,
                      value.item)
        self.assertIsInstance(value.data,
                              InstructionDocumentation,
                              'The value is expected to be the description of the instruction')
        return value


class TestTestCaseInstructionList(unittest.TestCase):
    def test_instruction_in_single_phase(self):
        application_help = application_help_for([section_documentation('phase-a', ['a-instruction']),
                                                 section_documentation('phase-with-target', ['target-instruction'])])
        actual = sut.parse(application_help, arguments_for.case_instruction_search('target-instruction'))
        actual = self._assert_is_valid_instruction_list_settings('target-instruction',
                                                                 actual)
        self.assertEqual(1,
                         len(actual.data),
                         'One instruction is expected to be found')
        self.assertEqual('phase-with-target',
                         actual.data[0][0].plain,
                         'The instruction is expected to be found in the %s phase.' % 'phase-with-target')

    def test_instruction_in_multiple_phase(self):
        application_help = application_help_for([
            section_documentation('phase-a', ['a-instr']),
            section_documentation('phase-b', ['the-instr']),
            section_documentation('phase-c', ['c-instr']),
            section_documentation('phase-d', ['the-instr']),
        ])
        actual = sut.parse(application_help,
                           arguments_for.case_instruction_search('the-instr'))
        actual = self._assert_is_valid_instruction_list_settings('the-instr',
                                                                 actual)
        self.assertEqual(2,
                         len(actual.data),
                         'Two instructions are expected to be found')
        self.assertEqual('phase-b',
                         actual.data[0][0].plain,
                         'The first instruction is expected to be found in the %s phase.' % 'phase-b')
        self.assertEqual('phase-d',
                         actual.data[1][0].plain,
                         'The second instruction is expected to be found in the %s phase.' % 'phase-d')

    def test_unknown_instruction(self):
        instructions = ['known-instruction']
        application_help = application_help_for([section_documentation('phase', instructions)])
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.case_instruction_search('unknown-instruction'))

    def _assert_is_valid_instruction_list_settings(
            self,
            expected_instruction_name: str,
            value) -> TestCaseHelpRequest:
        self.assertIsInstance(value, TestCaseHelpRequest,
                              'Should be help for Test Case')
        assert isinstance(value, TestCaseHelpRequest)
        self.assertEqual(expected_instruction_name,
                         value.name,
                         'Name of instruction')
        self.assertIs(TestCaseHelpItem.INSTRUCTION_SEARCH,
                      value.item)
        self.assertIsInstance(value.data,
                              list,
                              'The value is expected to be a list')
        for list_item in value.data:
            self.assertIsInstance(list_item,
                                  tuple,
                                  'Each item in the list is expected to be a tuple')
            self.assertEqual(2,
                             len(list_item),
                             'Each item in the list is expected to be a pair.')
            self.assertIsInstance(list_item[0],
                                  formatting.SectionName,
                                  'Each item in the list is expected to have a %s as first element' %
                                  str(formatting.SectionName))
            self.assertIsInstance(list_item[1],
                                  InstructionDocumentation,
                                  'Each item in the list is expected to have a Description as second element')
            description = list_item[1]
            assert isinstance(description, InstructionDocumentation)
            self.assertEqual(expected_instruction_name,
                             list_item[1].instruction_name(),
                             'The name of each instruction is expected to be "%s"' % expected_instruction_name)

        return value


class TestTestCaseInstructionSet(unittest.TestCase):
    def test_instruction_set(self):
        actual = sut.parse(application_help_for([]),
                           arguments_for.case_instructions())
        self.assertIsInstance(actual, TestCaseHelpRequest,
                              'Expecting settings for Test Case')
        assert isinstance(actual, TestCaseHelpRequest)
        self.assertIs(
            TestCaseHelpItem.INSTRUCTION_SET,
            actual.item,
            'Item should denote help for Instruction Set')


class TestTestCaseCliAndOverviewHelp(unittest.TestCase):
    def test_overview(self):
        actual = sut.parse(application_help_for([]),
                           arguments_for.case_specification())
        self.assertIsInstance(actual,
                              TestCaseHelpRequest,
                              'Expecting settings for test-case')
        assert isinstance(actual,
                          TestCaseHelpRequest)
        self.assertIs(TestCaseHelpItem.SPECIFICATION,
                      actual.item,
                      'Item should denote help for test-case overview')

    def test_cli_syntax(self):
        actual = sut.parse(application_help_for([]),
                           arguments_for.case_cli_syntax())
        self.assertIsInstance(actual,
                              TestCaseHelpRequest,
                              'Expecting settings for test-case')
        assert isinstance(actual,
                          TestCaseHelpRequest)
        self.assertIs(TestCaseHelpItem.CLI_SYNTAX,
                      actual.item,
                      'Item should denote help for test-case CLI syntax')


class TestTestSuiteHelp(unittest.TestCase):
    def test_cli_syntax(self):
        actual = sut.parse(application_help_for([]),
                           arguments_for.suite_cli_syntax())
        self.assertIsInstance(actual,
                              TestSuiteHelpRequest,
                              'Expecting settings for test-suite')
        assert isinstance(actual,
                          TestSuiteHelpRequest)
        self.assertIs(TestSuiteHelpItem.CLI_SYNTAX,
                      actual.item,
                      'Item should denote help for test-suite overview')

    def test_overview(self):
        actual = sut.parse(application_help_for([]),
                           arguments_for.suite_specification())
        self.assertIsInstance(actual,
                              TestSuiteHelpRequest,
                              'Expecting settings for test-suite')
        assert isinstance(actual,
                          TestSuiteHelpRequest)
        self.assertIs(TestSuiteHelpItem.SPECIFICATION,
                      actual.item,
                      'Item should denote help for test-suite overview')

    def test_known_section(self):
        actual = sut.parse(application_help_for(
            [],
            suite_sections=[SectionDocumentationForSectionWithoutInstructionsTestImpl('section A'),
                            SectionDocumentationForSectionWithoutInstructionsTestImpl('section B')]),
            arguments_for.suite_section_for_name('section A'))
        self.assertIsInstance(actual,
                              TestSuiteHelpRequest,
                              'Expecting help for Suite Section')
        assert isinstance(actual,
                          TestSuiteHelpRequest)
        self.assertIs(TestSuiteHelpItem.SECTION,
                      actual.item,
                      'Item should denote help for a Section')
        self.assertIsInstance(actual.data,
                              SectionDocumentation)

    def test_unknown_section(self):
        application_help = application_help_for(
            [],
            suite_sections=[SectionDocumentationForSectionWithoutInstructionsTestImpl('section A')])
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.suite_section_for_name('unknown section'))


class TestTestSuiteSingleInstructionInSection(unittest.TestCase):
    def test_unknown_section(self):
        application_help = application_help_for_suite_sections([
            section_documentation('section', ['instruction-name'])
        ])
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.suite_instruction_in_section('non-existing-section', 'instruction-name'))

    def test_unknown_instruction(self):
        application_help = application_help_for_suite_sections([
            section_documentation('section-1', ['instruction']),
            section_documentation('empty-section', []),
        ])
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.suite_instruction_in_section('empty-section', 'instruction'))

    def test_single_instruction_for_section_with_instructions(self):
        section_name = 'the section name'
        instructions = [section_name, 'name-that-is-not-the-name-of-a-section']
        application_help = application_help_for_suite_sections([
            section_documentation(section_name, instructions),
            section_documentation('other section than ' + section_name, instructions)
        ])
        self._assert_is_existing_instruction_in_section(application_help,
                                                        section_name,
                                                        'name-that-is-not-the-name-of-a-section')
        self._assert_is_existing_instruction_in_section(application_help,
                                                        section_name,
                                                        section_name)

    def _assert_is_existing_instruction_in_section(self,
                                                   application_help: ApplicationHelp,
                                                   section_name: str,
                                                   instruction_name: str):
        actual = sut.parse(application_help,
                           arguments_for.suite_instruction_in_section(section_name,
                                                                      instruction_name))
        actual = self._check_is_test_suite_settings_for_single_instruction(actual)
        self.assertEqual(actual.name,
                         instruction_name,
                         'Name of instruction')
        single_line_desc_str = actual.data.single_line_description()
        self.assertEqual(single_line_description_that_identifies_instruction_and_section(section_name,
                                                                                         instruction_name),
                         single_line_desc_str,
                         'The single-line-description in this test is expected to identify (section,instruction-name)')

    def _check_is_test_suite_settings_for_single_instruction(self, value) -> TestSuiteHelpRequest:
        self.assertIsInstance(value, TestSuiteHelpRequest,
                              'Should be help for Test Case')
        assert isinstance(value, TestSuiteHelpRequest)
        self.assertIs(TestSuiteHelpItem.INSTRUCTION,
                      value.item)
        self.assertIsInstance(value.data,
                              InstructionDocumentation,
                              'The value is expected to be the description of the instruction')
        return value


class TestSetupForActor(entity_lookup_test_cases.EntityTestSetup):
    def __init__(self):
        super().__init__(actor_doc.ActorDocumentation, ACTOR_ENTITY_TYPE_NAME)

    def entity_with_name(self, entity_name: str):
        return actor_doc.ActorTestImpl(entity_name)

    def arguments_for_list(self) -> list:
        return arguments_for.actor_list()

    def arguments_for_single_entity(self, entity_name_pattern: str) -> list:
        return arguments_for.actor_single(entity_name_pattern)

    def application_help_for_list_of_entities(self, entities: list) -> ApplicationHelp:
        return application_help_for([], actors=entities)


class TestSetupForConcept(entity_lookup_test_cases.EntityTestSetup):
    def __init__(self):
        super().__init__(ConceptDocumentation, CONCEPT_ENTITY_TYPE_NAME)

    def entity_with_name(self, entity_name: str):
        return ConceptTestImpl(entity_name)

    def arguments_for_list(self) -> list:
        return arguments_for.concept_list()

    def arguments_for_single_entity(self, entity_name_pattern: str) -> list:
        return arguments_for.concept_single(entity_name_pattern)

    def application_help_for_list_of_entities(self, entities: list) -> ApplicationHelp:
        return application_help_for([], concepts=entities)


class TestSetupForSuiteReporter(entity_lookup_test_cases.EntityTestSetup):
    def __init__(self):
        super().__init__(SuiteReporterDocumentation, SUITE_REPORTER_ENTITY_TYPE_NAME)

    def entity_with_name(self, entity_name: str):
        return SuiteReporterDocTestImpl(entity_name)

    def arguments_for_list(self) -> list:
        return arguments_for.suite_reporter_list()

    def arguments_for_single_entity(self, entity_name_pattern: str) -> list:
        return arguments_for.suite_reporter_single(entity_name_pattern)

    def application_help_for_list_of_entities(self, entities: list) -> ApplicationHelp:
        return application_help_for([], suite_reporters=entities)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestProgramHelp))
    ret_val.addTest(unittest.makeSuite(TestHtmlDocHelp))
    ret_val.addTest(entity_lookup_test_cases.suite_for(TestSetupForActor()))
    ret_val.addTest(entity_lookup_test_cases.suite_for(TestSetupForConcept()))
    ret_val.addTest(entity_lookup_test_cases.suite_for(TestSetupForSuiteReporter()))
    ret_val.addTest(unittest.makeSuite(TestTestCaseCliAndOverviewHelp))
    ret_val.addTest(unittest.makeSuite(TestTestCaseInstructionSet))
    ret_val.addTest(unittest.makeSuite(TestTestCaseSingleInstructionInPhase))
    ret_val.addTest(unittest.makeSuite(TestTestCaseInstructionList))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteHelp))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteSingleInstructionInSection))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
