import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.test_case_utils.sub_process_execution import ProcessExecutionSettings
from exactly_lib.util.process_execution.os_process_execution import with_environ
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, check, Expectation
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class AssertConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        check(put, parser, source, arrangement, expectation)

    def phase_is_after_act(self) -> bool:
        return True

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return arrangement(process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))

    def expect_success(self,
                       main_side_effects_on_files: asrt.ValueAssertion = asrt.anything_goes(),
                       symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return Expectation(main_side_effects_on_files=main_side_effects_on_files,
                           symbol_usages=symbol_usages)

    def expect_failure_of_main(self,
                               assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(main_result=pfh_check.is_fail(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(validation_pre_sds=svh_assertions.is_validation_error(assertion_on_error_message))

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(validation_post_sds=svh_assertions.is_validation_error(assertion_on_error_message))

    def arrangement(self,
                    pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default(),
                    symbols: SymbolTable = None):
        return arrangement(pre_contents_population_action=pre_contents_population_action,
                           sds_contents_before_main=sds_contents_before_main,
                           home_or_sds_contents_before_main=home_or_sds_contents,
                           process_execution_settings=with_environ(environ),
                           os_services=os_services,
                           symbols=symbols)
