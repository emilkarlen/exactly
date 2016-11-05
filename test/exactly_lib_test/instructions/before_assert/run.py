import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert import run as sut
from exactly_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.run_instruction_test import \
    suite_for, Configuration
from exactly_lib_test.instructions.test_resources import svh_check__va


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_eds_is_missing(self):
        return Expectation(validation_post_setup=svh_check__va.is_validation_error())


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
