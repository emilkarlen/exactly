import unittest

from shellcheck_lib.instructions.assert_phase import exitcode
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.assert_phase.utils import AssertInstructionTest, new_source, new_line_sequence


class TestParse(unittest.TestCase):
    def test_that_when_operator_is_invalid_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name <> 1'),
                          ' <> 1')

    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name '),
                          '')

    def test_that_when_too_many_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name a b c'),
                          'a b c')

    def test_that_when_argument_does_not_contain_integer_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name a'),
                          'a')

    def test_that__when__argument_contains_too_small_integer__then__exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name -1'),
                          '-1')

    def test_that__when__argument_contains_too_large_integer__then__exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_line_sequence('instruction-name 256'),
                          '256')

    def test_that_when_valid_argument_is_given_than_instruction_is_returned(self):
        parser = exitcode.Parser()
        actual_instruction = parser.apply(new_line_sequence('instruction-name 1'), '1')
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


class TestParseAndExecute(unittest.TestCase):
    def test_that__when__actual_value_is_as_expected__then__pass_is_returned(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' 72'))

    def test_that__when__actual_value_is_as_not_expected__then__fail_is_returned(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=0))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' 72'))


class TestParseAndExecuteTwoArgumentsEq(unittest.TestCase):
    def test_pass(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' = 72'))

    def test_fail(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=0))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' = 72'))


class TestParseAndExecuteTwoArgumentsNe(unittest.TestCase):
    def test_pass(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' ! 73'))

    def test_fail(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' ! 72'))


class TestParseAndExecuteTwoArgumentsLt(unittest.TestCase):
    def test_pass(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' < 73'))

    def test_fail_equal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' < 72'))

    def test_fail_unequal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' < 28'))


class TestParseAndExecuteTwoArgumentsLe(unittest.TestCase):
    def test_pass(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' <= 73'))

    def test_pass_equal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' <= 72'))

    def test_fail_unequal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' <= 28'))


class TestParseAndExecuteTwoArgumentsGt(unittest.TestCase):
    def test_pass(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' > 28'))

    def test_fail_equal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' > 72'))

    def test_fail_unequal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' > 87'))


class TestParseAndExecuteTwoArgumentsGe(unittest.TestCase):
    def test_pass(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' >= 28'))

    def test_pass_equal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' >= 72'))

    def test_fail_unequal(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name', ' >= 87'))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecute))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecuteTwoArgumentsEq))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecuteTwoArgumentsNe))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecuteTwoArgumentsLt))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecuteTwoArgumentsLe))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecuteTwoArgumentsGt))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecuteTwoArgumentsGe))
    return ret_val


if __name__ == '__main__':
    unittest.main()
