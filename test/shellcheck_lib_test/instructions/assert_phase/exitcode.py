import unittest

from shellcheck_lib.instructions.assert_phase import exitcode
from shellcheck_lib.instruction_parsing.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction
from shellcheck_lib_test.instructions import utils


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


class TestParseAndExecute(unittest.TestCase):
    def test_that__when__actual_value_is_as_expected__then__pass_is_returned(self):
        parser = exitcode.Parser()
        instruction = parser.apply('72')
        with utils.act_phase_result(exitcode=72) as post_eds_environment:
            validation_result = instruction.validate(post_eds_environment)
            self.assertTrue(validation_result.is_success,
                            'The assertion/validation is expected to succeed')
            main_actual = instruction.main(post_eds_environment,
                                           i.PhaseEnvironmentForInternalCommands())
            self.assertEqual(i.PassOrFailOrHardErrorEnum.PASS,
                             main_actual.status,
                             'The assertion is expected to PASS')

    def test_that__when__actual_value_is_as_not_expected__then__fail_is_returned(self):
        parser = exitcode.Parser()
        instruction = parser.apply('72')
        with utils.act_phase_result(exitcode=0) as post_eds_environment:
            validation_result = instruction.validate(post_eds_environment)
            self.assertTrue(validation_result.is_success,
                            'The assertion/validation is expected to succeed')
            main_actual = instruction.main(post_eds_environment,
                                           i.PhaseEnvironmentForInternalCommands())
            self.assertEqual(i.PassOrFailOrHardErrorEnum.FAIL,
                             main_actual.status,
                             'The assertion is expected to FAIL')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecute))
    return ret_val


if __name__ == '__main__':
    unittest.main()
