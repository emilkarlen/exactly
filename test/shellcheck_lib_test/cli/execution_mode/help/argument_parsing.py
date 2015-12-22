import unittest

from shellcheck_lib.cli.execution_mode.help import argument_parsing as sut
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.test_case.help.instruction_description import Description
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


def setup() -> InstructionsSetup:
    config_instruction_set = {}
    setup_instruction_set = {}
    assert_instruction_set = {}
    cleanup_instruction_set = {}
    return InstructionsSetup(config_instruction_set,
                             setup_instruction_set,
                             assert_instruction_set,
                             cleanup_instruction_set)


def instruction(description: Description) -> SingleInstructionSetup:
    return SingleInstructionSetup(ParserThatFailsUnconditionally(),
                                  description)


class ParserThatFailsUnconditionally(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        raise NotImplementedError('This method should never be used')


if __name__ == '__main__':
    unittest.main()
