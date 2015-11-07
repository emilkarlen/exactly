import unittest

from shellcheck_lib.instructions.assert_phase import exitcode
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, ActResultProducer
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources.utils import new_source


class TestParse(unittest.TestCase):
    def test_that_when_operator_is_invalid_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name',
                                     ' <> 1'))

    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name', ''))

    def test_that_when_too_many_arguments_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name',
                                     'a b c'))

    def test_that_when_argument_does_not_contain_integer_then_exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name', 'a'))

    def test_that__when__argument_contains_too_small_integer__then__exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name', '-1'))

    def test_that__when__argument_contains_too_large_integer__then__exception_is_raised(self):
        parser = exitcode.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name', '256'))

    def test_that_when_valid_argument_is_given_than_instruction_is_returned(self):
        parser = exitcode.Parser()
        actual_instruction = parser.apply(new_source('instruction-name', '1'))
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


class TestParseAndExecute(instruction_check.TestCaseBase):
    def test_that__when__actual_value_is_as_expected__then__pass_is_returned(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' 72'))

    def test_that__when__actual_value_is_as_not_expected__then__fail_is_returned(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=0)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       '72'))


class TestParseAndExecuteTwoArgumentsEq(instruction_check.TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' = 72'))

    def test_fail(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=0)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' = 72'))


class TestParseAndExecuteTwoArgumentsNe(instruction_check.TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name', ' ! 73'))

    def test_fail(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name',
                       ' ! 72'))


class TestParseAndExecuteTwoArgumentsLt(instruction_check.TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' < 87'))

    def test_fail_equal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' < 72'))

    def test_fail_unequal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' < 28'))


class TestParseAndExecuteTwoArgumentsLe(instruction_check.TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' <= 87'))

    def test_pass_equal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' <= 72'))

    def test_fail_unequal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' <= 28'))


class TestParseAndExecuteTwoArgumentsGt(instruction_check.TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' > 28'))

    def test_fail_equal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' > 72'))

    def test_fail_unequal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' > 87'))


class TestParseAndExecuteTwoArgumentsGe(instruction_check.TestCaseBase):
    def test_pass(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' >= 28'))

    def test_pass_equal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 ),
            new_source('instruction-name',
                       ' >= 72'))

    def test_fail_unequal(self):
        self._check(
            Flow(exitcode.Parser(),
                 act_result_producer=ActResultProducer(utils.ActResult(exitcode=72)),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       ' >= 87'))


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
