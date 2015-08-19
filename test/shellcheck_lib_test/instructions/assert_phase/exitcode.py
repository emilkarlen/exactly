import unittest

from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
from shellcheck_lib.instructions.assert_phase import exitcode
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.assert_phase.utils import AssertInstructionTest


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name '),
                          '')

    def test_that_when_too_many_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name a b c'),
                          'a b c')

    def test_that_when_argument_does_not_contain_integer_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name a'),
                          'a')

    def test_that__when__argument_contains_too_small_integer__then__exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name -1'),
                          '-1')

    def test_that__when__argument_contains_too_large_integer__then__exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name 256'),
                          '256')

    def test_that_when_valid_argument_is_given_than_instruction_is_returned(self):
        parser = exitcode.Parser()
        actual_instruction = parser.apply(new_source('instruction-name 1'), '1')
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


class TestParseAndExecute(unittest.TestCase):
    def test_that__when__actual_value_is_as_expected__then__pass_is_returned(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.PASS,
                                     utils.ActResult(exitcode=72))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name 72'),
                   ' 72')

    def test_that__when__actual_value_is_as_not_expected__then__fail_is_returned(self):
        test = AssertInstructionTest(i.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     i.PassOrFailOrHardErrorEnum.FAIL,
                                     utils.ActResult(exitcode=0))
        test.apply(self,
                   exitcode.Parser(),
                   new_source('instruction-name 72'),
                   ' 72')


def new_source(text: str) -> line_source.LineSequenceBuilder:
    return line_source.LineSequenceBuilder(
        parse.LineSequenceSourceFromListOfLines(
            parse.ListOfLines([])),
        1,
        text)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestParseAndExecute))
    return ret_val


if __name__ == '__main__':
    unittest.main()
