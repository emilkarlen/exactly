import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_ import new_dir as sut
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.new_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self,
                                     symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return Expectation(main_result=pfh_check.is_hard_error(),
                           symbol_usages=symbol_usages)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
