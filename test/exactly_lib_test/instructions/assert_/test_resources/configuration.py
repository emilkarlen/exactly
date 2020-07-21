import unittest

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.util.process_execution.execution_elements import with_environ, ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import check, Expectation
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators, tcds_populators, \
    sds_populator
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
        return ArrangementPostAct(
            process_execution_settings=ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds))

    def expect_success(self,
                       main_side_effects_on_sds: ValueAssertion = asrt.anything_goes(),
                       symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        return Expectation(
            main_side_effects_on_sds=main_side_effects_on_sds,
            symbol_usages=symbol_usages)

    def expect_failure_of_main(self,
                               assertion_on_error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                               ):
        return Expectation(
            main_result=pfh_assertions.is_fail(assertion_on_error_message)
        )

    def expect_hard_error_of_main(self,
                                  assertion_on_error_message: ValueAssertion[str] = asrt.anything_goes()):
        return Expectation(main_result=pfh_assertions.is_hard_error(
            asrt_text_doc.is_string_for_test(assertion_on_error_message)
        ))

    def expect_hard_error_of_main__any(self):
        return Expectation(main_result=pfh_assertions.is_hard_error(
            asrt_text_doc.is_any_text()
        ))

    def expect_failing_validation_pre_sds(self,
                                          error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()):
        return Expectation(
            validation_pre_sds=svh_assertions.is_validation_error(error_message)
        )

    def expect_failing_validation_post_setup(self,
                                             error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()):
        return Expectation(
            validation_post_sds=svh_assertions.is_validation_error(error_message)
        )

    def arrangement(self,
                    pre_contents_population_action: TcdsAction = TcdsAction(),
                    hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default(),
                    symbols: SymbolTable = None):
        return ArrangementPostAct(
            pre_contents_population_action=pre_contents_population_action,
            hds_contents=hds_contents,
            sds_contents=sds_contents_before_main,
            tcds_contents=tcds_contents,
            process_execution_settings=with_environ(environ),
            os_services=os_services,
            symbols=symbols)
