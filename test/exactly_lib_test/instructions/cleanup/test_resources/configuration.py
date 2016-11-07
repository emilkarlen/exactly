import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib_test.instructions.cleanup.test_resources.instruction_check import Arrangement, check, is_success, \
    Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
        return Expectation(main_result=sh_check.is_hard_error())

    def expect_failing_validation_pre_eds(self):
        return Expectation(validate_pre_eds_result=svh_check.is_validation_error())

    def arrangement(self,
                    eds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    os_services: OsServices = new_default()):
        return Arrangement(eds_contents_before_main=eds_contents_before_main,
                           os_services=os_services)

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: ValueAssertion):
        return Expectation(main_side_effects_on_files=main_side_effects_on_files)
