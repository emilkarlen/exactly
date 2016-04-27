import unittest

from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.test_case.os_services import new_default, OsServices
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import arrangement, check, is_pass, \
    Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.test_resources.execution import eds_populator
from shellcheck_lib_test.test_resources.execution.eds_contents_check import AdaptVa
from shellcheck_lib_test.test_resources.value_assertion import ValueAssertion


class AssertConfigurationBase(ConfigurationBase):
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        check(put, self.parser(), source, arrangement, expectation)

    def expect_success(self):
        return is_pass()

    def expect_failure_of_main(self):
        return Expectation(main_result=pfh_check.is_fail())

    def expect_failing_validation_pre_eds(self):
        return Expectation(validation_pre_eds=svh_check.is_validation_error())

    def arrangement(self,
                    eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                    os_services: OsServices = new_default()):
        return arrangement(eds_contents_before_main=eds_contents_before_main,
                           os_services=os_services)

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: ValueAssertion):
        return Expectation(main_side_effects_on_files=AdaptVa(main_side_effects_on_files))
