import unittest
from typing import Optional, Dict

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.os_services.os_services_access import new_for_current_os
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import check, Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.impls.instructions.test_resources.instruction_checker import InstructionChecker
from exactly_lib_test.tcfs.test_resources import hds_populators, tcds_populators, \
    sds_populator
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class AssertConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        check(put, parser, source, arrangement, expectation)

    @property
    def instruction_checker(self) -> InstructionChecker:
        return instruction_check.AssertInstructionChecker()

    def phase_is_after_act(self) -> bool:
        return True

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return ArrangementPostAct(
            process_execution_settings=proc_exe_env_for_test(timeout_in_seconds=timeout_in_seconds))

    def expect_success(self,
                       main_side_effects_on_sds: Assertion = asrt.anything_goes(),
                       symbol_usages: Assertion = asrt.is_empty_sequence,
                       source: Assertion[ParseSource] = asrt.anything_goes(),
                       proc_exe_settings: Assertion[ProcessExecutionSettings]
                       = asrt.is_instance(ProcessExecutionSettings),
                       instruction_settings: Assertion[InstructionSettings]
                       = asrt.is_instance(InstructionSettings),
                       ):
        return Expectation(
            source=source,
            symbol_usages=symbol_usages,
            main_side_effects_on_sds=main_side_effects_on_sds,
            proc_exe_settings=proc_exe_settings,
            instruction_settings=instruction_settings,
        )

    def expect_failure_of_main(self,
                               assertion_on_error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()
                               ):
        return Expectation(
            main_result=pfh_assertions.is_fail(assertion_on_error_message)
        )

    def expect_hard_error_of_main(self,
                                  assertion_on_error_message: Assertion[str] = asrt.anything_goes()):
        return Expectation(main_result=pfh_assertions.is_hard_error(
            asrt_text_doc.is_string_for_test(assertion_on_error_message)
        ))

    def expect_hard_error_of_main__any(self):
        return Expectation(main_result=pfh_assertions.is_hard_error(
            asrt_text_doc.is_any_text()
        ))

    def expect_failing_validation_pre_sds(self,
                                          error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()):
        return Expectation(
            validation_pre_sds=svh_assertions.is_validation_error(error_message)
        )

    def expect_failing_validation_post_setup(self,
                                             error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()):
        return Expectation(
            validation_post_sds=svh_assertions.is_validation_error(error_message)
        )

    def arrangement(self,
                    pre_contents_population_action: TcdsAction = TcdsAction(),
                    hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                    environ: Optional[Dict[str, str]] = None,
                    os_services: OsServices = new_for_current_os(),
                    symbols: SymbolTable = None):
        return ArrangementPostAct(
            pre_contents_population_action=pre_contents_population_action,
            hds_contents=hds_contents,
            sds_contents=sds_contents_before_main,
            tcds_contents=tcds_contents,
            process_execution_settings=ProcessExecutionSettings.from_non_immutable(environ=environ),
            os_services=os_services,
            symbols=symbols)
