import unittest

from shellcheck_lib.instructions.assert_phase import exitcode
from shellcheck_lib.instruction_parsing.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          '')

    def test_that_when_too_many_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          'a b c')

    def test_that_when_argument_does_not_contain_integer_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          'a')

    def test_that_when_argument_contains_integer_out_of_range_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          '-1')

    def test_that_when_valid_argument_is_given_than_instruction_is_returned(self):
        parser = exitcode.Parser()
        actual_instruction = parser.apply('1')
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


if __name__ == '__main__':
    unittest.main()
