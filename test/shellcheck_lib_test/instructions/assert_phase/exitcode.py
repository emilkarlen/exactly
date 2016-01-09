import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.instructions.assert_phase import exitcode as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import ActResultProducer, \
    arrangement, Expectation, is_pass
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.instructions.test_resources.utils import new_source2


class TestParse(unittest.TestCase):
    def test_that_when_operator_is_invalid_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2(' <> 1'))

    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2(''))

    def test_that_when_too_many_arguments_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2('a b c'))

    def test_that_when_argument_does_not_contain_integer_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2('a'))

    def test_that__when__argument_contains_too_small_integer__then__exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2('-1'))

    def test_that__when__argument_contains_too_large_integer__then__exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2('256'))

    def test_that_when_valid_argument_is_given_than_instruction_is_returned(self):
        parser = sut.Parser()
        actual_instruction = parser.apply(new_source2('1'))
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


class TestCaseBaseForParser(instruction_check.TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestParseAndExecute(TestCaseBaseForParser):
    def test_that__when__actual_value_is_as_expected__then__pass_is_returned(self):
        self._run(
                new_source2(' 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_that__when__actual_value_is_as_not_expected__then__fail_is_returned(self):
        self._run(
                new_source2('72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=0))),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsEq(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
                new_source2(' = 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(),
        )

    def test_fail(self):
        self._run(
                new_source2(' = 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=0))),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsNe(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
                new_source2(' ! 73'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_fail(self):
        self._run(
                new_source2(' ! 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail())
        )


class TestParseAndExecuteTwoArgumentsLt(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
                new_source2(' < 87'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_fail_equal(self):
        self._run(
                new_source2(' < 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail_unequal(self):
        self._run(
                new_source2(' < 28'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsLe(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
                new_source2(' <= 87'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_pass_equal(self):
        self._run(
                new_source2(' <= 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_fail_unequal(self):
        self._run(
                new_source2(' <= 28'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsGt(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
                new_source2(' > 28'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_fail_equal(self):
        self._run(
                new_source2(' > 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail_unequal(self):
        self._run(
                new_source2(' > 87'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsGe(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
                new_source2(' >= 28'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_pass_equal(self):
        self._run(
                new_source2(' >= 72'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                is_pass(),
        )

    def test_fail_unequal(self):
        self._run(
                new_source2(' >= 87'),
                arrangement(act_result_producer=ActResultProducer(utils.ActResult(exitcode=72))),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.TheDescription('instruction name')


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
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
