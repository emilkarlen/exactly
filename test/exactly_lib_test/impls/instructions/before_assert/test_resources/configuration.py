import unittest
from typing import Optional, Dict, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.os_services.os_services_access import new_for_current_os
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.before_assert.test_resources import instruction_check
from exactly_lib_test.impls.instructions.before_assert.test_resources import instruction_check as ic
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.impls.instructions.test_resources.instruction_checker import InstructionChecker
from exactly_lib_test.tcfs.test_resources import hds_populators, tcds_populators, \
    sds_populator
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class BeforeAssertConfigurationBase(ConfigurationBase):
    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        ic.check(put, parser, source, arrangement, expectation)

    @property
    def instruction_checker(self) -> InstructionChecker:
        return instruction_check.BeforeAssertInstructionChecker()

    def phase_is_after_act(self) -> bool:
        return True

    def expect_success(self,
                       main_side_effects_on_sds: Assertion = asrt.anything_goes(),
                       symbol_usages: Assertion = asrt.is_empty_sequence,
                       source: Assertion[ParseSource] = asrt.anything_goes(),
                       proc_exe_settings: Assertion[ProcessExecutionSettings]
                       = asrt.is_instance(ProcessExecutionSettings),
                       instruction_settings: Assertion[InstructionSettings]
                       = asrt.is_instance(InstructionSettings),
                       ):
        return ic.Expectation(
            source=source,
            symbol_usages=symbol_usages,
            main_side_effects_on_sds=main_side_effects_on_sds,
            proc_exe_settings=proc_exe_settings,
            instruction_settings=instruction_settings,
        )

    def expect_failure_of_main(self,
                               assertion_on_error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
                               symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                               ):
        return ic.Expectation(
            symbol_usages=symbol_usages,
            main_result=asrt_sh.is_hard_error(assertion_on_error_message)
        )

    def expect_failing_validation_pre_sds(self,
                                          error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
                                          symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                          ):
        return ic.Expectation(
            symbol_usages=symbol_usages,
            validation_pre_sds=svh_assertions.is_validation_error(error_message)
        )

    def expect_failing_validation_post_setup(self,
                                             error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
                                             symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                             ):
        return ic.Expectation(
            main_result=asrt_sh.is_hard_error(error_message),
            symbol_usages=symbol_usages,
        )

    def arrangement(self,
                    pre_contents_population_action: TcdsAction = TcdsAction(),
                    hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                    environ: Optional[Dict[str, str]] = None,
                    default_environ_getter: DefaultEnvironGetter = get_empty_environ,
                    os_services: OsServices = new_for_current_os(),
                    symbols: SymbolTable = None):
        return ic.arrangement(pre_contents_population_action=pre_contents_population_action,
                              hds_contents=hds_contents,
                              sds_contents_before_main=sds_contents_before_main,
                              tcds_contents=tcds_contents,
                              process_execution_settings=ProcessExecutionSettings.from_non_immutable(environ=environ),
                              default_environ_getter=default_environ_getter,
                              os_services=os_services,
                              symbols=symbols)

    def arrangement_with_timeout(self, timeout_in_seconds: int):
        return ic.arrangement(
            process_execution_settings=proc_exe_env_for_test(timeout_in_seconds=timeout_in_seconds))
