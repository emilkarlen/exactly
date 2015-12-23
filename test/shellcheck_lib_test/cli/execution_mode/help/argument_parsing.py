import unittest

from shellcheck_lib.cli.execution_mode.help import argument_parsing as sut
from shellcheck_lib.cli.execution_mode.help.contents import ApplicationHelp, HelpInstructionsSetup, MainProgramHelp, \
    TestCaseHelp, TestSuiteHelp
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.help.instruction_description import DescriptionWithConstantValues, Description
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup, SingleInstructionSetup


def _arguments_for_help_for_phase(phase: phases.Phase) -> list:
    return [phase.identifier]


def _arguments_for_help_for_instruction_in_phase(phase_identifier: str,
                                                 instruction_name: str) -> list:
    return [phase_identifier, instruction_name]


def _arguments_for_help_for_instruction_search(instruction_name: str) -> list:
    return [instruction_name]


class TestProgramHelp(unittest.TestCase):
    def test_program(self):
        actual = sut.parse(_app_help_for(empty_instruction_set()),
                           [])
        self.assertIsInstance(actual,
                              sut.settings.ProgramHelpSettings,
                              'Expecting settings for Program')


class TestTestCaseSingleInstructionInPhase(unittest.TestCase):
    def test_single_instruction_for_phases_with_instructions(self):
        for phase in phases.ALL_WITH_INSTRUCTIONS:
            self._check_instruction_in_phase(phase)

    def test_unknown_phase(self):
        instructions = ['instruction-name']
        instr_set = instruction_set(instructions,
                                    instructions,
                                    instructions,
                                    instructions)
        application_help = _app_help_for(instr_set)
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      _arguments_for_help_for_instruction_in_phase('non-existing-phase', 'instruction-name'))

    def test_unknown_instruction(self):
        instructions = ['instruction-name']
        instr_set = instruction_set(instructions,
                                    instructions,
                                    [],
                                    instructions)
        application_help = _app_help_for(instr_set)
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      _arguments_for_help_for_instruction_in_phase(phases.ASSERT.identifier, 'instruction-name'))

    def _check_instruction_in_phase(self, phase: phases.Phase):
        instructions = [phase.identifier, 'name-that-is-not-the-name-of-a-phase']
        instr_set = instruction_set(instructions,
                                    instructions,
                                    instructions,
                                    instructions)
        application_help = _app_help_for(instr_set)
        self._assert_is_existing_instruction_in_phase(application_help,
                                                      phase,
                                                      'name-that-is-not-the-name-of-a-phase')
        self._assert_is_existing_instruction_in_phase(application_help,
                                                      phase,
                                                      phase.identifier)

    def _assert_is_existing_instruction_in_phase(self,
                                                 application_help: ApplicationHelp,
                                                 phase: phases.Phase,
                                                 instruction_name: str):
        actual = sut.parse(application_help,
                           _arguments_for_help_for_instruction_in_phase(phase.identifier,
                                                                        instruction_name))
        actual = self._check_is_test_case_settings_for_single_instruction(actual)
        self.assertEqual(actual.name,
                         instruction_name,
                         'Name of instruction')
        self.assertEqual(_single_line_description_that_identifies_instruction_and_phase(phase,
                                                                                        instruction_name),
                         actual.value.single_line_description(),
                         'The single-line-description in this test is expected to identify (phase,instruction-name)')

    def _check_is_test_case_settings_for_single_instruction(
            self,
            value) -> sut.settings.TestCaseHelpSettings:
        self.assertIsInstance(value,
                              sut.settings.TestCaseHelpSettings,
                              'Should be help for Test Case')
        assert isinstance(value, sut.settings.TestCaseHelpSettings)
        self.assertIs(sut.settings.TestCaseHelpItem.INSTRUCTION,
                      value.item)
        self.assertIsInstance(value.value,
                              Description,
                              'The value is expected to be the description of the instruction')
        return value


class TestTestCaseInstructionList(unittest.TestCase):
    def test_instruction_in_single_phase(self):
        instr_set = instruction_set(['config-instruction'],
                                    ['setup-instruction'],
                                    ['assert-instruction'],
                                    ['cleanup-instruction'])
        application_help = _app_help_for(instr_set)
        actual = sut.parse(application_help, _arguments_for_help_for_instruction_search('setup-instruction'))
        actual = self._assert_is_valid_instruction_list_settings('setup-instruction',
                                                                 actual)
        self.assertEqual(1,
                         len(actual.value),
                         'One instruction is expected to be found')
        self.assertEqual(phases.SETUP,
                         actual.value[0][0],
                         'The instruction is expected to be found in the %s phase.' % phases.SETUP.identifier)

    def test_instruction_in_multiple_phase(self):
        instr_set = instruction_set(['config-instruction'],
                                    ['the-instruction'],
                                    ['assert-instruction'],
                                    ['the-instruction'])
        application_help = _app_help_for(instr_set)
        actual = sut.parse(application_help,
                           _arguments_for_help_for_instruction_search('the-instruction'))
        actual = self._assert_is_valid_instruction_list_settings('the-instruction',
                                                                 actual)
        self.assertEqual(2,
                         len(actual.value),
                         'Two instructions are expected to be found')
        self.assertEqual(phases.SETUP,
                         actual.value[0][0],
                         'The first instruction is expected to be found in the %s phase.' % phases.SETUP.identifier)
        self.assertEqual(phases.CLEANUP,
                         actual.value[1][0],
                         'The second instruction is expected to be found in the %s phase.' % phases.CLEANUP.identifier)

    def test_unknown_instruction(self):
        instructions = ['known-instruction']
        instr_set = instruction_set(instructions,
                                    instructions,
                                    instructions,
                                    instructions)
        application_help = _app_help_for(instr_set)
        with self.assertRaises(sut.HelpError):
            sut.parse(application_help,
                      _arguments_for_help_for_instruction_search('unknown-instruction'))

    def _assert_is_valid_instruction_list_settings(
            self,
            expected_instruction_name: str,
            value) -> sut.settings.TestCaseHelpSettings:
        self.assertIsInstance(value,
                              sut.settings.TestCaseHelpSettings,
                              'Should be help for Test Case')
        assert isinstance(value, sut.settings.TestCaseHelpSettings)
        self.assertEqual(expected_instruction_name,
                         value.name,
                         'Name of instruction')
        self.assertIs(sut.settings.TestCaseHelpItem.INSTRUCTION_LIST,
                      value.item)
        self.assertIsInstance(value.value,
                              list,
                              'The value is expected to be a list')
        for list_item in value.value:
            self.assertIsInstance(list_item,
                                  tuple,
                                  'Each item in the list is expected to be a tuple')
            self.assertEquals(2,
                              len(list_item),
                              'Each item in the list is expected to be a pair.')
            self.assertIsInstance(list_item[0],
                                  phases.Phase,
                                  'Each item in the list is expected to have a %s as first element' % str(phases.Phase))
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
        actual = sut.parse(_app_help_for(empty_instruction_set()),
                           [sut.INSTRUCTIONS])
        self.assertIsInstance(actual,
                              sut.settings.TestCaseHelpSettings,
                              'Expecting settings for Test Case')
        assert isinstance(actual, sut.settings.TestCaseHelpSettings)
        self.assertIs(sut.settings.TestCaseHelpItem.INSTRUCTION_SET,
                      actual.item,
                      'Item should denote help for Instruction Set')

    def test_phase(self):
        for phase in phases.ALL:
            self._check_phase(phase)

    def _check_phase(self, phase: phases.Phase):
        instr_set = instruction_set([phase.identifier],
                                    [phase.identifier],
                                    [phase.identifier],
                                    [phase.identifier])
        actual = sut.parse(_app_help_for(instr_set),
                           _arguments_for_help_for_phase(phase))
        self.assertIsInstance(actual,
                              sut.settings.TestCaseHelpSettings,
                              'Should be help for Test Case')
        assert isinstance(actual, sut.settings.TestCaseHelpSettings)
        self.assertIs(sut.settings.TestCaseHelpItem.PHASE,
                      actual.item)
        self.assertEqual(phase.identifier,
                         actual.name,
                         'Name of phase')


class TestTestSuiteHelp(unittest.TestCase):
    def test_overview(self):
        actual = sut.parse(_app_help_for(empty_instruction_set()),
                           [sut.SUITE])
        self.assertIsInstance(actual,
                              sut.settings.TestSuiteHelpSettings,
                              'Expecting settings for Program')
        assert isinstance(actual, sut.settings.TestSuiteHelpSettings)
        self.assertIs(sut.settings.TestSuiteHelpItem.OVERVIEW,
                      actual.item,
                      'Item should denote help for Overview')


def empty_instruction_set() -> InstructionsSetup:
    return InstructionsSetup({}, {}, {}, {})


def instruction_set(config_set_instruction_names: iter = (),
                    setup_set_instruction_names: iter = (),
                    assert_set_instruction_names: iter = (),
                    cleanup_set_instruction_names: iter = ()) -> InstructionsSetup:
    return InstructionsSetup(dict(map(lambda name: instr(phases.ANONYMOUS, name), config_set_instruction_names)),
                             dict(map(lambda name: instr(phases.SETUP, name), setup_set_instruction_names)),
                             dict(map(lambda name: instr(phases.ASSERT, name), assert_set_instruction_names)),
                             dict(map(lambda name: instr(phases.CLEANUP, name), cleanup_set_instruction_names)))


def instr(phase: phases.Phase, name: str) -> (str, SingleInstructionSetup):
    return (name,
            SingleInstructionSetup(
                    ParserThatFailsUnconditionally(),
                    DescriptionWithConstantValues(name,
                                                  _single_line_description_that_identifies_instruction_and_phase(phase,
                                                                                                                 name),
                                                  '',
                                                  [])))


def _single_line_description_that_identifies_instruction_and_phase(phase: phases.Phase,
                                                                   instruction_name: str):
    return phase.identifier + '/' + instruction_name


class ParserThatFailsUnconditionally(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        raise NotImplementedError('This method should never be used')


def _app_help_for(instructions_setup: InstructionsSetup) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp(HelpInstructionsSetup(instructions_setup)),
                           TestSuiteHelp())


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
