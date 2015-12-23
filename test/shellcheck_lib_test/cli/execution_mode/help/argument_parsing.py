import unittest

from shellcheck_lib.cli.execution_mode.help import argument_parsing as sut
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.help.instruction_description import DescriptionWithConstantValues
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup, SingleInstructionSetup


class TestProgramHelp(unittest.TestCase):
    def test_program(self):
        actual = sut.parse(empty_instruction_set(), [])
        self.assertIsInstance(actual,
                              sut.settings.ProgramHelpSettings,
                              'Expecting settings for Program')


class TestTestCaseHelp(unittest.TestCase):
    def test_instruction_set(self):
        actual = sut.parse(empty_instruction_set(), [sut.INSTRUCTIONS])
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
        instr_with_same_name_as_phase = instr(phase.identifier)
        instr_set = instruction_set([instr_with_same_name_as_phase], [instr_with_same_name_as_phase],
                                    [instr_with_same_name_as_phase], [instr_with_same_name_as_phase])
        actual = sut.parse(instr_set, [phase.identifier])
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
        actual = sut.parse(empty_instruction_set(), [sut.SUITE])
        self.assertIsInstance(actual,
                              sut.settings.TestSuiteHelpSettings,
                              'Expecting settings for Program')
        assert isinstance(actual, sut.settings.TestSuiteHelpSettings)
        self.assertIs(sut.settings.TestSuiteHelpItem.OVERVIEW,
                      actual.item,
                      'Item should denote help for Overview')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestProgramHelp))
    ret_val.addTest(unittest.makeSuite(TestTestCaseHelp))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteHelp))
    return ret_val


def empty_instruction_set() -> InstructionsSetup:
    return InstructionsSetup({}, {}, {}, {})


def instruction_set(config_set: iter = (),
                    setup_set: iter = (),
                    assert_set: iter = (),
                    cleanup_set: iter = ()) -> InstructionsSetup:
    return InstructionsSetup(dict(config_set),
                             dict(setup_set),
                             dict(assert_set),
                             dict(cleanup_set))


def instr(name: str) -> (str, SingleInstructionSetup):
    return (name,
            SingleInstructionSetup(ParserThatFailsUnconditionally(),
                                   DescriptionWithConstantValues(name,
                                                                 name,
                                                                 '',
                                                                 [])))


class ParserThatFailsUnconditionally(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        raise NotImplementedError('This method should never be used')


if __name__ == '__main__':
    unittest.main()
