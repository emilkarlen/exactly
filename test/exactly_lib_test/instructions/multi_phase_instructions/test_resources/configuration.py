import unittest

from exactly_lib.common.instruction_documentation import InstructionDocumentation
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementBase
from exactly_lib_test.instructions.test_resources.check_description import suite_for_description_instance
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class ConfigurationBase:
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        raise NotImplementedError()

    def instruction_setup(self) -> SingleInstructionSetup:
        raise NotImplementedError()

    def parser(self) -> SingleInstructionParser:
        return self.instruction_setup()

    def description(self) -> InstructionDocumentation:
        return self.instruction_setup().description

    def arrangement(self,
                    eds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                    os_services: OsServices = new_default()):
        raise NotImplementedError()

    def empty_arrangement(self) -> ArrangementBase:
        return self.arrangement(eds_contents_before_main=sds_populator.empty())

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: va.ValueAssertion):
        """
        :param main_side_effects_on_files: An assertion on the EDS
        """
        raise NotImplementedError()

    def expect_success(self):
        raise NotImplementedError()

    def expect_failure_of_main(self,
                               assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        raise NotImplementedError()

    def expect_failing_validation_pre_eds(self,
                                          assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        raise NotImplementedError()


def suite_for_cases(configuration: ConfigurationBase,
                    test_case_classes: list) -> unittest.TestSuite:
    return unittest.TestSuite(
        [suite_for_description_instance(configuration.description())] +
        list(tcc(configuration) for tcc in test_case_classes))
