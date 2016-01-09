import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.os_services import new_default, OsServices
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources.arrangements import ArrangementBase
from shellcheck_lib_test.instructions.test_resources.check_description import suite_for_description_instance
from shellcheck_lib_test.test_resources.value_assertion import ValueAssertion


class ConfigurationBase:
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        raise NotImplementedError()

    def parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def description(self) -> Description:
        raise NotImplementedError()

    def arrangement(self,
                    eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                    os_services: OsServices = new_default()):
        raise NotImplementedError()

    def empty_arrangement(self) -> ArrangementBase:
        return self.arrangement(eds_contents_before_main=eds_populator.empty())

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: ValueAssertion):
        """
        :param main_side_effects_on_files: An assertion on the EDS
        """
        raise NotImplementedError()

    def expect_success(self):
        raise NotImplementedError()

    def expect_failure_of_main(self):
        raise NotImplementedError()

    def expect_failing_validation_pre_eds(self):
        raise NotImplementedError()


def suite_for_cases(configuration: ConfigurationBase,
                    test_case_classes: list) -> unittest.TestSuite:
    return unittest.TestSuite(
            [suite_for_description_instance(configuration.description())] +
            list(tcc(configuration) for tcc in test_case_classes))
