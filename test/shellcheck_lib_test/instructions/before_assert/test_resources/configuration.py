import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib_test.instructions.before_assert.test_resources.instruction_check import arrangement, check, \
    is_success, Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check__va
from shellcheck_lib_test.instructions.test_resources import svh_check__va


class BeforeAssertConfigurationBase(ConfigurationBase):
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        check(put, self.parser(), source, arrangement, expectation)

    def expectation_of_success(self):
        return is_success()

    def expectation_of_failure_of_main(self):
        return Expectation(main_result=sh_check__va.is_hard_error())

    def expectation_of_failing_validation_pre_eds(self):
        return Expectation(validation_pre_eds=svh_check__va.is_validation_error())

    def arrangement(self, eds_contents_before_main: eds_populator.EdsPopulator):
        return arrangement(eds_contents_before_main=eds_contents_before_main)
