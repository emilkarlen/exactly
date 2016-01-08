import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib_test.instructions.cleanup.test_resources.instruction_check import arrangement, check, is_success, \
    Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import svh_check


class CleanupConfigurationBase(ConfigurationBase):
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        check(put, self.parser(), source, arrangement, expectation)

    def expect_success(self):
        return is_success()

    def expect_failure_of_main(self):
        return Expectation(main_result=sh_check.IsHardError())

    def expect_failing_validation_pre_eds(self):
        return Expectation(validate_pre_eds_result=svh_check.is_validation_error())

    def arrangement(self, eds_contents_before_main: eds_populator.EdsPopulator):
        return arrangement(eds_contents_before_main=eds_contents_before_main)
