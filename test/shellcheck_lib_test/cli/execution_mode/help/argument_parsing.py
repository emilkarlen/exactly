import unittest

from shellcheck_lib.cli.execution_mode.help import argument_parsing as sut
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup


class TestTestCaseHelp(unittest.TestCase):
    def test_program(self):
        actual = sut.parse(empty_instruction_set(), [])
        self.assertIsInstance(actual,
                              sut.ProgramHelpSettings,
                              'Expecting settings for Program')

    def test_instruction_set(self):
        actual = sut.parse(empty_instruction_set(), [sut.INSTRUCTIONS])
        self.assertIsInstance(actual,
                              sut.TestCaseHelpSettings,
                              'Expecting settings for Test Case')
        assert isinstance(actual, sut.TestCaseHelpSettings)
        self.assertIs(sut.TestCaseHelpItem.INSTRUCTION_SET,
                      actual.item,
                      'Item should denote help for Instruction Set')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestCaseHelp))
    return ret_val


def empty_instruction_set() -> InstructionsSetup:
    return InstructionsSetup({}, {}, {}, {})


if __name__ == '__main__':
    unittest.main()
