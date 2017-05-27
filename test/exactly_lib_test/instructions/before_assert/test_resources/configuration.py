import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_environ
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.before_assert.test_resources import instruction_check as ic
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class BeforeAssertConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        ic.check(put, parser, source, arrangement, expectation)

    def phase_is_after_act(self) -> bool:
        return True

    def expect_success(self,
                       main_side_effects_on_files: asrt.ValueAssertion = asrt.anything_goes(),
                       symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return ic.Expectation(main_side_effects_on_files=main_side_effects_on_files,
                              symbol_usages=symbol_usages)

    def expect_failure_of_main(self,
                               assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return ic.Expectation(main_result=sh_check.is_hard_error(assertion_on_error_message))

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return ic.Expectation(validation_pre_sds=svh_check.is_validation_error(assertion_on_error_message))

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: asrt.ValueAssertion = asrt.anything_goes()):
        return ic.Expectation(validation_post_setup=svh_check.is_validation_error(assertion_on_error_message))

    def arrangement(self,
                    pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default(),
                    symbols: SymbolTable = None):
        return ic.arrangement(pre_contents_population_action=pre_contents_population_action,
                              sds_contents_before_main=sds_contents_before_main,
                              process_execution_settings=with_environ(environ),
                              os_services=os_services,
                              symbols=symbols)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return ic.arrangement(
            process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))
