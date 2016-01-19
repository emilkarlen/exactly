from shellcheck_lib.instructions.assert_phase import change_dir as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.assert_phase.test_resources.configuration import AssertConfigurationBase
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import AdaptVa
from shellcheck_lib_test.test_resources.value_assertion import ValueAssertion


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: ValueAssertion):
        return Expectation(side_effects_check=AdaptVa(side_effects_check))

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=pfh_check.is_hard_error())


def suite():
    return suite_for(TheConfiguration())
