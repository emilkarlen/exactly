import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.setup import shell as sut
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.shell_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case_utils.test_resources import sh_assertions


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_assertions.is_hard_error())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
