import unittest

from exactly_lib.instructions.cleanup import new_dir as sut
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.instructions.cleanup.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.new_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.instructions.test_resources import sh_check


class TheConfiguration(CleanupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self):
        return Expectation(main_result=sh_check.IsHardError())


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())
