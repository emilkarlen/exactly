import unittest

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, with_environ
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.cleanup.test_resources.instruction_check import Arrangement, check, Expectation
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import home_populators, home_and_sds_populators, \
    sds_populator
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class CleanupConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        check(put, parser, source, arrangement, expectation)

    def phase_is_after_act(self) -> bool:
        return True

    def expect_success(self,
                       main_side_effects_on_sds: asrt.ValueAssertion = asrt.anything_goes(),
                       symbol_usages: asrt.ValueAssertion = asrt.is_empty_sequence):
        return Expectation(main_side_effects_on_sds=main_side_effects_on_sds,
                           symbol_usages=symbol_usages)

    def expect_failure_of_main(self,
                               assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(main_result=sh_assertions.is_hard_error(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return Expectation(validate_pre_sds_result=svh_assertions.is_validation_error(assertion_on_error_message))

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return self.expect_failure_of_main(assertion_on_error_message=assertion_on_error_message)

    def arrangement(self,
                    pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                    hds_contents: home_populators.HomePopulator = home_populators.empty(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default(),
                    symbols: SymbolTable = None):
        return Arrangement(pre_contents_population_action=pre_contents_population_action,
                           hds_contents=hds_contents,
                           sds_contents_before_main=sds_contents_before_main,
                           home_or_sds_contents=home_or_sds_contents,
                           process_execution_settings=with_environ(environ),
                           os_services=os_services,
                           symbols=symbols)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return Arrangement(process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))
