import unittest

from shellcheck_lib.instructions.before_assert import change_dir as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import sh_check__va
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects__va import SideEffectsCheckAsVa


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: SideEffectsCheck):
        return Expectation(home_and_eds=SideEffectsCheckAsVa(side_effects_check))

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=sh_check__va.is_hard_error())


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
