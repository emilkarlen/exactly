import unittest

from shellcheck_lib.instructions.before_assert import execute as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.execute_instruction_test import \
    suite_for, Configuration
from shellcheck_lib_test.instructions.test_resources import svh_check__va


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_eds_is_missing(self):
        return Expectation(validation_post_setup=svh_check__va.is_validation_error())


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
