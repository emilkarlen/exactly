"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.sections.anonymous import ConfigurationBuilder
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    AnonymousPhaseInstructionThatReturns
from shellcheck_lib_test.instructions.configuration.test_resources import instruction_check
from shellcheck_lib_test.instructions.configuration.test_resources import configuration_check
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.test_resources.test_of_test_framework_utils import ParserThatGives
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(
            instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION)),
            single_line_source())

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_result=test_misc.ShRaisesTestError()),
                single_line_source())

    def test_fail_due_to_fail_of_side_effects_on_configuration(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_configuration=ConfigurationCheckRaisesTestError()),
                single_line_source())


class ConfigurationCheckRaisesTestError(configuration_check.Assertion):
    def apply(self, put: unittest.TestCase, initial: ConfigurationBuilder, actual_result: ConfigurationBuilder):
        raise test_misc.TestError()


def single_line_source() -> SingleInstructionParserSource:
    return utils.new_source('instruction name', 'instruction arguments')


SUCCESSFUL_INSTRUCTION = AnonymousPhaseInstructionThatReturns(sh.new_sh_success())
