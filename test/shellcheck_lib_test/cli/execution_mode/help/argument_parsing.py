import unittest

import shellcheck_lib.cli.execution_mode.help.mode.help_request
import shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request
import shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request
from shellcheck_lib.cli.execution_mode.help import argument_parsing as sut
from shellcheck_lib.cli.execution_mode.help.contents_structure import ApplicationHelp
from shellcheck_lib.cli.execution_mode.help.mode.main_program.contents_structure import MainProgramHelp
from shellcheck_lib.cli.execution_mode.help.mode.test_case.contents_structure import TestCasePhaseInstructionSet, \
    TestCasePhaseHelp, TestCaseHelp
from shellcheck_lib.cli.execution_mode.help.mode.test_suite.contents_structure import TestSuiteSectionHelp, \
    TestSuiteHelp
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.cli.execution_mode.help.test_resources import arguments_for
from shellcheck_lib_test.test_resources.instruction_description import DescriptionWithConstantValues


class TestProgramHelp(unittest.TestCase):
    def test_program_help(self):
        actual = sut.parse(_app_help_for([]),
                           [])
        self.assertIsInstance(actual,
                              shellcheck_lib.cli.execution_mode.help.mode.help_request.ProgramHelpRequest,
                              'Expecting settings for Program')
        assert isinstance(actual, shellcheck_lib.cli.execution_mode.help.mode.help_request.ProgramHelpRequest)
        self.assertIs(shellcheck_lib.cli.execution_mode.help.mode.help_request.ProgramHelpItem.PROGRAM,
                      actual.item,
                      'Expects program help')

    def test_help_help(self):
        actual = sut.parse(_app_help_for([sut.HELP]),
                           [])
        self.assertIsInstance(actual,
                              shellcheck_lib.cli.execution_mode.help.mode.help_request.ProgramHelpRequest,
                              'Expecting settings for Program')
        assert isinstance(actual, shellcheck_lib.cli.execution_mode.help.mode.help_request.ProgramHelpRequest)
        self.assertIs(shellcheck_lib.cli.execution_mode.help.mode.help_request.ProgramHelpItem.PROGRAM,
                      actual.item,
                      'Expects program help')


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
                              shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest,
                              'Parse result should be a ' + str(
                                      shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest))
        assert isinstance(actual,
                          shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest)
        self.assertIs(shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpItem.PHASE,
                      actual.item)
        self.assertIsInstance(actual.data,
                              TestCasePhaseHelp)

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
        phase_name = 'phase name'
        instructions = [phase_name, 'name-that-is-not-the-name-of-a-phase']
        application_help = _app_help_for([
            test_case_phase_help(phase_name, instructions),
            test_case_phase_help('other phase ' + phase_name, instructions)
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
        self.assertEqual(_single_line_description_that_identifies_instruction_and_phase(phase_name,
                                                                                        instruction_name),
                         actual.data.single_line_description(),
                         'The single-line-description in this test is expected to identify (phase,instruction-name)')

    def _check_is_test_case_settings_for_single_instruction(
            self,
            value) -> shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest:
        self.assertIsInstance(value,
                              shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest,
                              'Should be help for Test Case')
        assert isinstance(value,
                          shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest)
        self.assertIs(shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpItem.INSTRUCTION,
                      value.item)
        self.assertIsInstance(value.data,
                              Description,
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
                         actual.data[0][0],
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
                         actual.data[0][0],
                         'The first instruction is expected to be found in the %s phase.' % 'phase-b')
        self.assertEqual('phase-d',
                         actual.data[1][0],
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
            value) -> shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest:
        self.assertIsInstance(value,
                              shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest,
                              'Should be help for Test Case')
        assert isinstance(value,
                          shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest)
        self.assertEqual(expected_instruction_name,
                         value.name,
                         'Name of instruction')
        self.assertIs(
                shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpItem.INSTRUCTION_LIST,
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
                                  str,
                                  'Each item in the list is expected to have a %s as first element' % str(str))
            self.assertIsInstance(list_item[1],
                                  Description,
                                  'Each item in the list is expected to have a Description as second element')
            description = list_item[1]
            assert isinstance(description, Description)
            self.assertEqual(expected_instruction_name,
                             list_item[1].instruction_name(),
                             'The name of each instruction is expected to be "%s"' % expected_instruction_name)

        return value


class TestTestCaseInstructionSet(unittest.TestCase):
    def test_instruction_set(self):
        actual = sut.parse(_app_help_for([]),
                           arguments_for.instructions())
        self.assertIsInstance(actual,
                              shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest,
                              'Expecting settings for Test Case')
        assert isinstance(actual,
                          shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpRequest)
        self.assertIs(
                shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request.TestCaseHelpItem.INSTRUCTION_SET,
                actual.item,
                'Item should denote help for Instruction Set')


class TestTestSuiteHelp(unittest.TestCase):
    def test_overview(self):
        actual = sut.parse(_app_help_for([]),
                           arguments_for.suite())
        self.assertIsInstance(actual,
                              shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request.TestSuiteHelpRequest,
                              'Expecting settings for Program')
        assert isinstance(actual,
                          shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request.TestSuiteHelpRequest)
        self.assertIs(shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request.TestSuiteHelpItem.OVERVIEW,
                      actual.item,
                      'Item should denote help for Overview')

    def test_known_section(self):
        actual = sut.parse(_app_help_for([],
                                         suite_sections=[TestSuiteSectionHelp('section A'),
                                                         TestSuiteSectionHelp('section B')]),
                           arguments_for.suite_section('section A'))
        self.assertIsInstance(actual,
                              shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request.TestSuiteHelpRequest,
                              'Expecting help for Suite Section')
        assert isinstance(actual,
                          shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request.TestSuiteHelpRequest)
        self.assertIs(shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request.TestSuiteHelpItem.SECTION,
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


def instr_descr(phase_name: str, name: str) -> Description:
    return DescriptionWithConstantValues(
            name,
            _single_line_description_that_identifies_instruction_and_phase(phase_name,
                                                                           name),
            '',
            [])


def _single_line_description_that_identifies_instruction_and_phase(phase_name: str,
                                                                   instruction_name: str) -> str:
    return phase_name + '/' + instruction_name


def _app_help_for(test_case_phase_helps: list,
                  suite_sections=()) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp(test_case_phase_helps),
                           TestSuiteHelp(suite_sections))


def test_case_phase_help(phase_name: str,
                         instruction_names: list) -> TestCasePhaseHelp:
    instruction_descriptions = map(lambda name: instr_descr(phase_name, name),
                                   instruction_names)
    return TestCasePhaseHelp(phase_name,
                             TestCasePhaseInstructionSet(instruction_descriptions))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestProgramHelp))
    ret_val.addTest(unittest.makeSuite(TestTestCaseInstructionSet))
    ret_val.addTest(unittest.makeSuite(TestTestCaseSingleInstructionInPhase))
    ret_val.addTest(unittest.makeSuite(TestTestCaseInstructionList))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteHelp))
    return ret_val


if __name__ == '__main__':
    unittest.main()
