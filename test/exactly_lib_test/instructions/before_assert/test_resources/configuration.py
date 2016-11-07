import unittest

from exactly_lib.instructions.utils.sub_process_execution import ProcessExecutionSettings
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib_test.instructions.before_assert.test_resources import instruction_check as ic
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class BeforeAssertConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: SingleInstructionParser,
                             source: SingleInstructionParserSource,
                             arrangement,
                             expectation):
        ic.check(put, parser, source, arrangement, expectation)

    def expect_success(self):
        return ic.is_success()

    def expect_failure_of_main(self,
                               assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return ic.Expectation(main_result=sh_check.is_hard_error(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return ic.Expectation(validation_pre_sds=svh_check.is_validation_error(assertion_on_error_message))

    def arrangement(self,
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    os_services: OsServices = new_default()):
        return ic.arrangement(sds_contents_before_main=sds_contents_before_main,
                              os_services=os_services)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return ic.arrangement(
            process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: ValueAssertion):
        return ic.Expectation(main_side_effects_on_files=main_side_effects_on_files)
