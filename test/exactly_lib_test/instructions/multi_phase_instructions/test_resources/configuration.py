import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementBase
from exactly_lib_test.instructions.test_resources.check_description import suite_for_documentation_instance
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.execution.sds_check import sds_populator
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class ConfigurationBase:
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
                    sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    environ: dict = None,
                    os_services: OsServices = new_default()):
        raise NotImplementedError()

    def empty_arrangement(self) -> ArrangementBase:
        return self.arrangement(sds_contents_before_main=sds_populator.empty())

    def arrangement_with_timeout(self, timeout_in_seconds: int) -> ArrangementBase:
        raise NotImplementedError()

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: va.ValueAssertion):
        """
        :param main_side_effects_on_files: An assertion on the SDS
        """
        raise NotImplementedError()

    def expect_success(self):
        raise NotImplementedError()

    def expect_failure_of_main(self,
                               assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        raise NotImplementedError()

    def expect_failing_validation_pre_sds(self,
                                          assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        raise NotImplementedError()


def suite_for_cases(configuration: ConfigurationBase,
                    test_case_classes: list) -> unittest.TestSuite:
    return unittest.TestSuite(
        [suite_for_documentation_instance(configuration.documentation())] +
        list(tcc(configuration) for tcc in test_case_classes))
