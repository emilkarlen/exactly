import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_environ
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.setup.test_resources import instruction_check as ic
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class SetupConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        ic.check(put, parser, source, arrangement, expectation)

    def phase_is_after_act(self) -> bool:
        return False

    def expect_success(self,
                       main_side_effects_on_files: asrt.ValueAssertion = asrt.anything_goes(),
                       symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return ic.Expectation(main_side_effects_on_files=main_side_effects_on_files,
                              symbol_usages=symbol_usages)

    def expect_failure_of_main(self,
                               assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return ic.Expectation(main_result=sh_assertions.is_hard_error(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return ic.Expectation(pre_validation_result=svh_assertions.is_validation_error())

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return ic.Expectation(post_validation_result=svh_assertions.is_validation_error())

    def arrangement(self,
                    pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default(),
                    symbols: SymbolTable = None):
        return ic.Arrangement(pre_contents_population_action=pre_contents_population_action,
                              sds_contents_before_main=sds_contents_before_main,
                              home_or_sds_contents=home_or_sds_contents,
                              process_execution_settings=with_environ(environ),
                              os_services=os_services,
                              symbols=symbols)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return ic.Arrangement(
            process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))
