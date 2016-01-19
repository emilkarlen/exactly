import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.assert_phase import execute as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.assert_phase.test_resources.configuration import AssertConfigurationBase
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.execute_instruction_test import \
    suite_for, Configuration
from shellcheck_lib_test.instructions.test_resources import svh_check


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def parser(self) -> SingleInstructionParser:
        return self.instruction_setup()

    def description(self) -> Description:
        return self.instruction_setup().description

    def expect_failure_because_specified_file_under_eds_is_missing(self):
        return Expectation(validation_post_eds=svh_check.is_validation_error())



def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
