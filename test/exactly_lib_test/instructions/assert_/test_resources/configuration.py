import unittest

from exactly_lib.instructions.utils.sub_process_execution import ProcessExecutionSettings
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.util.process_execution.os_process_execution import with_environ
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, check, is_pass, \
    Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class AssertConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        check(put, parser, source, arrangement, expectation)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return arrangement(process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))

    def expect_success(self):
        return is_pass()

    def expect_failure_of_main(self,
                               assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return Expectation(main_result=pfh_check.is_fail(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return Expectation(validation_pre_sds=svh_check.is_validation_error(assertion_on_error_message))

    def arrangement(self,
                    pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default()):
        return arrangement(pre_contents_population_action=pre_contents_population_action,
                           sds_contents_before_main=sds_contents_before_main,
                           process_execution_settings=with_environ(environ),
                           os_services=os_services)

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: ValueAssertion):
        return Expectation(main_side_effects_on_files=main_side_effects_on_files)
