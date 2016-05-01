import unittest

from exactly_lib.instructions.assert_ import change_dir as sut
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.instructions.test_resources import pfh_check
from exactly_lib_test.instructions.test_resources.assertion_utils.side_effects import AdaptVa
from exactly_lib_test.test_resources.value_assertion import ValueAssertion


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: ValueAssertion):
        return Expectation(side_effects_check=AdaptVa(side_effects_check))

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=pfh_check.is_hard_error())


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
