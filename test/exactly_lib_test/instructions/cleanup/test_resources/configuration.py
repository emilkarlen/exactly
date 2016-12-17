import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_environ
from exactly_lib_test.instructions.cleanup.test_resources.instruction_check import Arrangement, check, is_success, \
    Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class CleanupConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: SingleInstructionParser,
                             source: SingleInstructionParserSource,
                             arrangement,
                             expectation):
        check(put, parser, source, arrangement, expectation)

    def expect_success(self):
        return is_success()

    def expect_failure_of_main(self,
                               assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return Expectation(main_result=sh_check.is_hard_error(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return Expectation(validate_pre_sds_result=svh_check.is_validation_error(assertion_on_error_message))

    def arrangement(self,
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default()):
        return Arrangement(sds_contents_before_main=sds_contents_before_main,
                           process_execution_settings=with_environ(environ),
                           os_services=os_services)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return Arrangement(process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: ValueAssertion):
        return Expectation(main_side_effects_on_files=main_side_effects_on_files)
