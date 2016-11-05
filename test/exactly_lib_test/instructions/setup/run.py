import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.setup import run as sut
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.run_instruction_test import suite_for, \
    Configuration
from exactly_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources import sh_check


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_eds_is_missing(self):
        return Expectation(main_result=sh_check.IsHardError())


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
