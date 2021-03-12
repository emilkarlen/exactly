import unittest
from abc import ABC, abstractmethod
from typing import Sequence, Dict, Optional

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.os_services.os_services_access import new_for_current_os
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.test_resources.instruction_checker import InstructionChecker
from exactly_lib_test.impls.test_resources.validation.validation import ValidationActual
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.tcfs.test_resources import hds_populators, tcds_populators, \
    sds_populator
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementBase
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class ConfigurationBase(ABC):
    def phase_is_after_act(self) -> bool:
        raise NotImplementedError()

    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        raise NotImplementedError()

    @property
    @abstractmethod
    def instruction_checker(self) -> InstructionChecker:
        pass

    def run_test(self,
                 put: unittest.TestCase,
                 source: ParseSource,
                 arrangement,
                 expectation):
        self.run_test_with_parser(put, self.parser(), source, arrangement, expectation)

    def run_single_line_test_with_source_variants_and_source_check(self,
                                                                   put: unittest.TestCase,
                                                                   instruction_argument: str,
                                                                   arrangement,
                                                                   expectation):
        for source in equivalent_source_variants__with_source_check__consume_last_line(put, instruction_argument):
            self.run_test(put, source, arrangement, expectation)

    def instruction_setup(self) -> SingleInstructionSetup:
        raise NotImplementedError()

    def parser(self) -> InstructionParser:
        return self.instruction_setup()

    @property
    def parse_checker(self) -> parse_checker.Checker[Instruction]:
        return parse_checker.Checker(self.parser())

    def documentation(self) -> InstructionDocumentation:
        return self.instruction_setup().documentation

    def arrangement(self,
                    pre_contents_population_action: TcdsAction = TcdsAction(),
                    hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                    environ: Optional[Dict[str, str]] = None,
                    default_environ_getter: DefaultEnvironGetter = get_empty_environ,
                    os_services: OsServices = new_for_current_os(),
                    symbols: SymbolTable = None):
        raise NotImplementedError()

    def arrangement_with_timeout(self, timeout_in_seconds: int) -> ArrangementBase:
        raise NotImplementedError()

    def expect_success(self,
                       main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                       symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                       source: Assertion[ParseSource] = asrt.anything_goes(),
                       proc_exe_settings: Assertion[ProcessExecutionSettings]
                       = asrt.is_instance(ProcessExecutionSettings),
                       instruction_settings: Assertion[InstructionSettings]
                       = asrt.is_instance(InstructionSettings),
                       ):
        raise NotImplementedError()

    def expect_failure_of_main(self,
                               assertion_on_error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
                               symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                               ):
        """
        Expectation that the result should be HARD_ERROR for non-assertions and FAIL for assertions.
        """
        raise NotImplementedError()

    def expect_hard_error_of_main(self,
                                  assertion_on_error_message: Assertion[str] = asrt.anything_goes(),
                                  symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                  ):
        """
        Expectation that the result should be HARD_ERROR,
        both for assert- and non-assert phase instructions.
        """
        return self.expect_failure_of_main(
            asrt_text_doc.is_string_for_test(assertion_on_error_message)
        )

    def expect_hard_error_of_main__any(self,
                                       symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                       ):
        """
        Expectation that the result should be HARD_ERROR,
        both for assert- and non-assert phase instructions.
        """
        return self.expect_failure_of_main(symbol_usages=symbol_usages)

    def expect_failing_validation_pre_sds(self,
                                          error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
                                          symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                          ):
        raise NotImplementedError()

    def expect_failing_validation_post_setup(self,
                                             error_message: Assertion[TextRenderer] = asrt.anything_goes(),
                                             symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                             ):
        raise NotImplementedError()

    def expect_failing_validation(self,
                                  actual: ValidationActual,
                                  symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                                  ):
        if actual.pre_sds is not None:
            return self.expect_failing_validation_pre_sds(
                asrt_text_doc.is_string_for_test_that_equals(actual.pre_sds),
                symbol_usages=symbol_usages,
            )
        else:
            return self.expect_failing_validation_post_setup(
                asrt_text_doc.is_string_for_test_that_equals(actual.post_sds),
                symbol_usages=symbol_usages,
            )


class TestCaseWithConfiguration(unittest.TestCase, ABC):
    def __init__(self, conf: ConfigurationBase):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return '\n / '.join([str(type(self)),
                             str(type(self.conf))])


def suite_for_cases(configuration: ConfigurationBase,
                    test_case_classes: list) -> unittest.TestSuite:
    return unittest.TestSuite(
        [suite_for_documentation_instance(configuration.documentation())] +
        list(tcc(configuration) for tcc in test_case_classes))
