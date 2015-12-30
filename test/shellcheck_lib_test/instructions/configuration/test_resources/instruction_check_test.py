"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.test_case.sections.anonymous import ConfigurationBuilder
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources.instruction_test_resources import \
    AnonymousPhaseInstructionThatReturns
from shellcheck_lib_test.instructions.configuration.test_resources import configuration_check
from shellcheck_lib_test.instructions.configuration.test_resources import instruction_check
from shellcheck_lib_test.instructions.configuration.test_resources.instruction_check import Arrangement, Expectation
from shellcheck_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.test_of_test_framework_utils import ParserThatGives


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(
                ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                single_line_source(),
                Arrangement(),
                Expectation())

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    ParserThatGives(_SUCCESSFUL_INSTRUCTION),

                    single_line_source(),
                    Arrangement(),
                    Expectation(main_result=test_misc.ShRaisesTestError()))

    def test_fail_due_to_fail_of_side_effects_on_configuration(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    Arrangement(),
                    Expectation(configuration=ConfigurationCheckRaisesTestError()))


class ConfigurationCheckRaisesTestError(configuration_check.Assertion):
    def apply(self, put: unittest.TestCase, initial: ConfigurationBuilder, actual_result: ConfigurationBuilder):
        raise test_misc.TestError()


def single_line_source() -> SingleInstructionParserSource:
    return utils.new_source('instruction name', 'instruction arguments')


_SUCCESSFUL_INSTRUCTION = AnonymousPhaseInstructionThatReturns(sh.new_sh_success())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
