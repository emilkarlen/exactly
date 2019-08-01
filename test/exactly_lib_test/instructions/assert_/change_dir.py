import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_ import change_dir as sut
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: ValueAssertion,
                                                     symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        return Expectation(main_side_effects_on_home_and_sds=side_effects_check,
                           symbol_usages=symbol_usages)

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=pfh_assertions.is_hard_error__with_arbitrary_message())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
