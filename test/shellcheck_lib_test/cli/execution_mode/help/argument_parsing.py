import unittest

from shellcheck_lib.cli.execution_mode.help import argument_parsing as sut
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup


class TestCase(unittest.TestCase):
    def test_program(self):
        actual = sut.parse(empty_instruction_set(), [])
        self.assertIsInstance(actual,
                              sut.HelpSettings)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


def empty_instruction_set() -> InstructionsSetup:
    return InstructionsSetup({}, {}, {}, {})


if __name__ == '__main__':
    unittest.main()
