import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementBase
from exactly_lib_test.test_case_file_structure.test_resources import home_populators, home_and_sds_populators, \
    sds_populator
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class ConfigurationBase:
    def phase_is_after_act(self) -> bool:
        raise NotImplementedError()

    def run_test_with_parser(self,
                             put: unittest.TestCase,
                             parser: InstructionParser,
                             source: ParseSource,
                             arrangement,
                             expectation):
        raise NotImplementedError()

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
        for source in equivalent_source_variants__with_source_check(put, instruction_argument):
            self.run_test(put, source, arrangement, expectation)

    def instruction_setup(self) -> SingleInstructionSetup:
        raise NotImplementedError()

    def parser(self) -> InstructionParser:
        return self.instruction_setup()

    def documentation(self) -> InstructionDocumentation:
        return self.instruction_setup().documentation

    def arrangement(self,
                    pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                    hds_contents: home_populators.HomePopulator = home_populators.empty(),
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default(),
                    symbols: SymbolTable = None):
        raise NotImplementedError()

    def arrangement_with_timeout(self, timeout_in_seconds: int) -> ArrangementBase:
        raise NotImplementedError()

    def expect_success(self,
                       main_side_effects_on_sds: ValueAssertion = asrt.anything_goes(),
                       symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        raise NotImplementedError()

    def expect_failure_of_main(self,
                               assertion_on_error_message: ValueAssertion = asrt.anything_goes()):
        """
        Expectation that the result should be HARD_ERROR for non-assertions and FAIL for assertions.
        """
        raise NotImplementedError()

    def expect_hard_error_of_main(self,
                                  assertion_on_error_message: ValueAssertion = asrt.anything_goes()):
        """
        Expectation that the result should be HARD_ERROR,
        both for assert- and non-assert phase instructions.
        """
        return self.expect_failure_of_main(assertion_on_error_message)

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: ValueAssertion = asrt.anything_goes()):
        raise NotImplementedError()

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: ValueAssertion = asrt.anything_goes()):
        raise NotImplementedError()


def suite_for_cases(configuration: ConfigurationBase,
                    test_case_classes: list) -> unittest.TestSuite:
    return unittest.TestSuite(
        [suite_for_documentation_instance(configuration.documentation())] +
        list(tcc(configuration) for tcc in test_case_classes))
