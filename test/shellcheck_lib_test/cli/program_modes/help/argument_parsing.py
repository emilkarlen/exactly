import unittest

from shellcheck_lib.cli.program_modes.help import argument_parsing as sut
from shellcheck_lib.cli.program_modes.help.argument_parsing import HelpError
from shellcheck_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest, ConceptHelpItem
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.help_request import *
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.help_request import *
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.help_request import *
from shellcheck_lib.help.concepts.concept_structure import PlainConceptDocumentation, Name, ConceptDocumentation
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseDocumentation, TestCaseHelp, \
    ConceptsHelp
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from shellcheck_lib.help.program_modes.test_suite.contents_structure import TestSuiteSectionHelp, \
    TestSuiteHelp
from shellcheck_lib.help.utils import formatting
from shellcheck_lib.help.utils.description import Description, single_line_description
from shellcheck_lib_test.cli.program_modes.help.test_resources import arguments_for
from shellcheck_lib_test.help.test_resources import test_case_phase_help, \
    single_line_description_that_identifies_instruction_and_phase


class TestProgramHelp(unittest.TestCase):
    def test_program_help(self):
        actual = sut.parse(_app_help_for([]),
                           [])
        self.assertIsInstance(actual,
                              MainProgramHelpRequest,
                              'Expecting settings for MainProgram')
        assert isinstance(actual, MainProgramHelpRequest)
        self.assertIs(MainProgramHelpItem.PROGRAM,
                      actual.item,
                      'Expects program help')

    def test_help_help(self):
        actual = sut.parse(_app_help_for([]),
                           [sut.HELP])
        self.assertIsInstance(actual,
                              MainProgramHelpRequest,
                              'Expecting settings for MainProgram')
        assert isinstance(actual, MainProgramHelpRequest)
        self.assertIs(MainProgramHelpItem.HELP,
                      actual.item,
                      'Expects MainProgram help for help')


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
        arguments = arguments_for.phase_for_name('non existing phase')
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help, arguments)

    def _assert_successful_parsing_of_existing_phase(self,
                                                     application_help: ApplicationHelp,
                                                     phase_name: str):
        arguments = arguments_for.phase_for_name(phase_name)
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
                              TestCasePhaseDocumentation)

        self.assertEqual(expected_phase_name,
                         actual.data.name)

    def _application_help_with_phases(self, all_phases):
        return ApplicationHelp(MainProgramHelp(),
                               TestCaseHelp(map(lambda ph_name: test_case_phase_help(ph_name, []),
                                                all_phases)),
                               TestSuiteHelp({}))


class TestTestCaseSingleInstructionInPhase(unittest.TestCase):
    def test_unknown_phase(self):
        application_help = _app_help_for([
            test_case_phase_help('phase', ['instruction-name'])
        ])
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      arguments_for.instruction_in_phase('non-existing-phase', 'instruction-name'))

    def test_unknown_instruction(self):
        application_help = _app_help_for([
            test_case_phase_help('phase-1', ['instruction']),
            test_case_phase_help('empty-phase', []),
        ])
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      arguments_for.instruction_in_phase('empty-phase', 'instruction'))

    def test_single_instruction_for_phases_with_instructions(self):
        phase_name = 'the phase name'
        instructions = [phase_name, 'name-that-is-not-the-name-of-a-phase']
        application_help = _app_help_for([
            test_case_phase_help(phase_name, instructions),
            test_case_phase_help('other phase than ' + phase_name, instructions)
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
                           arguments_for.instruction_in_phase(phase_name,
                                                              instruction_name))
        actual = self._check_is_test_case_settings_for_single_instruction(actual)
        self.assertEqual(actual.name,
                         instruction_name,
                         'Name of instruction')
        self.assertEqual(single_line_description_that_identifies_instruction_and_phase(phase_name,
                                                                                       instruction_name),
                         actual.data.single_line_description(),
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
        application_help = _app_help_for([test_case_phase_help('phase-a', ['a-instruction']),
                                          test_case_phase_help('phase-with-target', ['target-instruction'])])
        actual = sut.parse(application_help, arguments_for.instruction_search('target-instruction'))
        actual = self._assert_is_valid_instruction_list_settings('target-instruction',
                                                                 actual)
        self.assertEqual(1,
                         len(actual.data),
                         'One instruction is expected to be found')
        self.assertEqual('phase-with-target',
                         actual.data[0][0].plain,
                         'The instruction is expected to be found in the %s phase.' % 'phase-with-target')

    def test_instruction_in_multiple_phase(self):
        application_help = _app_help_for([
            test_case_phase_help('phase-a', ['a-instr']),
            test_case_phase_help('phase-b', ['the-instr']),
            test_case_phase_help('phase-c', ['c-instr']),
            test_case_phase_help('phase-d', ['the-instr']),
        ])
        actual = sut.parse(application_help,
                           arguments_for.instruction_search('the-instr'))
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
        application_help = _app_help_for([test_case_phase_help('phase', instructions)])
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      arguments_for.instruction_search('unknown-instruction'))

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
            self.assertEquals(2,
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
        actual = sut.parse(_app_help_for([]),
                           arguments_for.instructions())
        self.assertIsInstance(actual, TestCaseHelpRequest,
                              'Expecting settings for Test Case')
        assert isinstance(actual, TestCaseHelpRequest)
        self.assertIs(
            TestCaseHelpItem.INSTRUCTION_SET,
            actual.item,
            'Item should denote help for Instruction Set')


class TestTestCaseHelp(unittest.TestCase):
    def test_overview(self):
        actual = sut.parse(_app_help_for([]),
                           arguments_for.test_case())
        self.assertIsInstance(actual,
                              TestCaseHelpRequest,
                              'Expecting settings for test-case')
        assert isinstance(actual,
                          TestCaseHelpRequest)
        self.assertIs(TestCaseHelpItem.OVERVIEW,
                      actual.item,
                      'Item should denote help for test-case overview')


class TestTestSuiteHelp(unittest.TestCase):
    def test_overview(self):
        actual = sut.parse(_app_help_for([]),
                           arguments_for.suite())
        self.assertIsInstance(actual,
                              TestSuiteHelpRequest,
                              'Expecting settings for test-suite')
        assert isinstance(actual,
                          TestSuiteHelpRequest)
        self.assertIs(TestSuiteHelpItem.OVERVIEW,
                      actual.item,
                      'Item should denote help for test-suite overview')

    def test_known_section(self):
        actual = sut.parse(_app_help_for([],
                                         suite_sections=[TestSuiteSectionHelp('section A'),
                                                         TestSuiteSectionHelp('section B')]),
                           arguments_for.suite_section('section A'))
        self.assertIsInstance(actual,
                              TestSuiteHelpRequest,
                              'Expecting help for Suite Section')
        assert isinstance(actual,
                          TestSuiteHelpRequest)
        self.assertIs(TestSuiteHelpItem.SECTION,
                      actual.item,
                      'Item should denote help for a Section')
        self.assertIsInstance(actual.data,
                              TestSuiteSectionHelp)

    def test_unknown_section(self):
        application_help = _app_help_for([],
                                         suite_sections=[TestSuiteSectionHelp('section A')])
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      arguments_for.suite_section('unknown section'))


def _app_help_for(test_case_phase_helps: list,
                  suite_sections=(),
                  concepts=()) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           ConceptsHelp(concepts),
                           TestCaseHelp(test_case_phase_helps),
                           TestSuiteHelp(suite_sections))


class TestConceptHelp(unittest.TestCase):
    def test_concept_list(self):
        actual = sut.parse(_app_help_for([]),
                           arguments_for.concept_list())
        self.assertIsInstance(actual,
                              ConceptHelpRequest,
                              'Expecting settings for concepts')
        assert isinstance(actual,
                          ConceptHelpRequest)
        self.assertIs(ConceptHelpItem.ALL_CONCEPTS_LIST,
                      actual.item,
                      'Item should denote help for ' + ConceptHelpItem.ALL_CONCEPTS_LIST.name)

    def test_individual_concept_with_single_word_name(self):
        # ARRANGE #
        concepts = [
            ConceptTestImpl('first'),
            ConceptTestImpl('second'),
        ]
        application_help = _app_help_for([], concepts=concepts)
        # ACT #
        actual = sut.parse(application_help,
                           arguments_for.individual_concept('second'))
        # ASSERT #
        self._assert_result_is_individual_concept(actual, 'second')

    def test_individual_concept_with_multiple_words_name(self):
        # ARRANGE #
        concepts = [
            ConceptTestImpl('first'),
            ConceptTestImpl('a b c'),
            ConceptTestImpl('last'),
        ]
        application_help = _app_help_for([], concepts=concepts)
        # ACT #
        actual = sut.parse(application_help,
                           arguments_for.individual_concept('a b c'))
        # ASSERT #
        self._assert_result_is_individual_concept(actual, 'a b c')

    def test_individual_concept_with_multiple_words_and_different_case_name(self):
        # ARRANGE #
        concepts = [
            ConceptTestImpl('first'),
            ConceptTestImpl('a b c'),
            ConceptTestImpl('last'),
        ]
        application_help = _app_help_for([], concepts=concepts)
        # ACT #
        actual = sut.parse(application_help,
                           arguments_for.individual_concept('a B C'))
        # ASSERT #
        self._assert_result_is_individual_concept(actual, 'a b c')

    def test_search_for_non_existing_concept_SHOULD_raise_HelpError(self):
        # ARRANGE #
        concepts = [
            ConceptTestImpl('first'),
            ConceptTestImpl('second'),
        ]
        application_help = _app_help_for([], concepts=concepts)
        # ACT & ASSERT #
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      arguments_for.individual_concept('non-existing concept'))

    def _assert_result_is_individual_concept(self,
                                             actual: HelpRequest,
                                             concept_name: str):
        self.assertIsInstance(actual,
                              ConceptHelpRequest,
                              'Expecting settings for concepts')
        assert isinstance(actual,
                          ConceptHelpRequest)
        self.assertIs(ConceptHelpItem.INDIVIDUAL_CONCEPT,
                      actual.item,
                      'Item should denote help for ' + ConceptHelpItem.INDIVIDUAL_CONCEPT.name)

        self.assertIsInstance(actual.individual_concept,
                              ConceptDocumentation,
                              'Individual concept is expected to an instance of ' + str(ConceptDocumentation))

        self.assertEqual(concept_name,
                         actual.individual_concept.name().singular)


class ConceptTestImpl(PlainConceptDocumentation):
    def __init__(self, singular_name: str):
        super().__init__(Name(singular_name))

    def purpose(self) -> Description:
        return single_line_description('single line description')


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestProgramHelp))
    ret_val.addTest(unittest.makeSuite(TestConceptHelp))
    ret_val.addTest(unittest.makeSuite(TestTestCaseHelp))
    ret_val.addTest(unittest.makeSuite(TestTestCaseInstructionSet))
    ret_val.addTest(unittest.makeSuite(TestTestCaseSingleInstructionInPhase))
    ret_val.addTest(unittest.makeSuite(TestTestCaseInstructionList))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteHelp))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
