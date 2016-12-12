import unittest

from exactly_lib.instructions.assert_ import exitcode as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution import utils
from exactly_lib_test.test_resources.parse import new_source2


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
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_that__when__actual_value_is_as_not_expected__then__fail_is_returned(self):
        self._run(
            new_source2('72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=0))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsEq(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
            new_source2(' = 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(),
        )

    def test_fail(self):
        self._run(
            new_source2(' = 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=0))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsNe(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
            new_source2(' ! 73'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_fail(self):
        self._run(
            new_source2(' ! 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail())
        )


class TestParseAndExecuteTwoArgumentsLt(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
            new_source2(' < 87'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_fail_equal(self):
        self._run(
            new_source2(' < 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail_unequal(self):
        self._run(
            new_source2(' < 28'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsLe(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
            new_source2(' <= 87'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_pass_equal(self):
        self._run(
            new_source2(' <= 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_fail_unequal(self):
        self._run(
            new_source2(' <= 28'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsGt(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
            new_source2(' > 28'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_fail_equal(self):
        self._run(
            new_source2(' > 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail_unequal(self):
        self._run(
            new_source2(' > 87'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestParseAndExecuteTwoArgumentsGe(TestCaseBaseForParser):
    def test_pass(self):
        self._run(
            new_source2(' >= 28'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_pass_equal(self):
        self._run(
            new_source2(' >= 72'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            is_pass(),
        )

    def test_fail_unequal(self):
        self._run(
            new_source2(' >= 87'),
            arrangement(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=72))),
            Expectation(main_result=pfh_check.is_fail()),
        )


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestParseAndExecute),
        unittest.makeSuite(TestParseAndExecuteTwoArgumentsEq),
        unittest.makeSuite(TestParseAndExecuteTwoArgumentsNe),
        unittest.makeSuite(TestParseAndExecuteTwoArgumentsLt),
        unittest.makeSuite(TestParseAndExecuteTwoArgumentsLe),
        unittest.makeSuite(TestParseAndExecuteTwoArgumentsGt),
        unittest.makeSuite(TestParseAndExecuteTwoArgumentsGe),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
