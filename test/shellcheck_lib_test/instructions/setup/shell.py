import unittest

from shellcheck_lib.instructions.setup import shell as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.shell_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_check.IsHardError())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
