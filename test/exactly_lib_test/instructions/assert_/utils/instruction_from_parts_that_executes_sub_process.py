import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.utils.instruction_parts import InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_from_parts_that_executes_sub_process as test_impl
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class ConfigurationForTheAssertPhase(AssertConfigurationBase, test_impl.Configuration):
    def phase(self) -> phase_identifier.Phase:
        return phase_identifier.ASSERT

    def instruction_setup(self) -> SingleInstructionSetup:
        raise ValueError('this method is not used by these tests')

    def instruction_info_for(self, instruction_name: str) -> InstructionInfoForConstructingAnInstructionFromParts:
        return instruction_from_parts.instruction_info_for(instruction_name)

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_pass())

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        return Expectation(validation_post_eds=svh_check.is_validation_error(assertion_on_error_message))


def suite() -> unittest.TestSuite:
    return test_impl.suite_for(ConfigurationForTheAssertPhase())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
